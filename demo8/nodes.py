from __future__ import annotations

from dataclasses import dataclass

from demo6.framework import ask_llm_json, ask_llm_text
from demo8.example_context import CodeWorkflowContext
from demo8.framework import BaseWorkflowNode
from demo8.tools import list_files, read_text_file, replace_text_in_file, search_text, write_text_file


@dataclass
class ClassifyNode(BaseWorkflowNode):
    """
    把用户目标分类为 summary / edit。

    这是 workflow 的第一步：
    先把任务分成“只读观察”还是“需要修改”两类，
    后面的节点再走不同路径。
    """

    def run(self, ctx: CodeWorkflowContext) -> str:
        system_prompt = (
            "你是一个 workflow 分类器。"
            "请根据用户目标输出 JSON，字段如下："
            "intent (summary 或 edit), target_file, search_query, reason。"
            "如果用户明显要求修改代码或文件，intent 选择 edit。"
            "如果用户只是想了解、总结或检查，intent 选择 summary。"
        )
        data = ask_llm_json(system_prompt, f"用户目标：{ctx.goal}")

        ctx.intent = str(data.get("intent") or "edit")
        ctx.target_file = data.get("target_file") or None
        ctx.search_query = data.get("search_query") or None
        ctx.logs.append(f"classify={data}")
        return "inspect"


@dataclass
class InspectNode(BaseWorkflowNode):
    """
    先观察工作区。

    workflow 的第二步先看：
    - 当前目录有什么
    - 目标文件长什么样
    - 搜索关键词命中了哪些地方
    """

    def run(self, ctx: CodeWorkflowContext) -> str:
        listing = list_files(str(ctx.workspace_dir), ".")
        ctx.logs.append(f"workspace_list_count={len(listing.get('items', []))}")

        if ctx.search_query:
            hits = search_text(str(ctx.workspace_dir), ctx.search_query, ".")
            ctx.search_hits = hits.get("matches", [])
            ctx.logs.append(f"search_hits={len(ctx.search_hits)}")

        if ctx.target_file:
            ctx.file_snapshot = read_text_file(str(ctx.workspace_dir), ctx.target_file)
            ctx.logs.append(f"snapshot_path={ctx.file_snapshot.get('path')}")

        if ctx.intent == "summary":
            return "report"
        return "plan"


@dataclass
class PlanNode(BaseWorkflowNode):
    """
    让模型根据观察结果生成一个具体修改计划。

    这一步的目标不是让模型直接修改，而是先把修改意图收敛成
    可执行的 patch plan。
    """

    def run(self, ctx: CodeWorkflowContext) -> str:
        system_prompt = (
            "你是一个 workflow 规划器。"
            "根据用户目标、文件快照和搜索结果，输出 JSON。"
            "字段如下：relative_path, old_text, new_text, expected_occurrences, rationale。"
            "只做一个小而精确的改动。"
        )
        user_content = (
            f"用户目标：{ctx.goal}\n"
            f"目标文件：{ctx.target_file}\n"
            f"文件快照：{ctx.file_snapshot}\n"
            f"搜索结果：{ctx.search_hits}\n"
        )
        plan = ask_llm_json(system_prompt, user_content)
        ctx.patch_plan = plan
        ctx.logs.append(f"plan={plan}")
        return "apply"


@dataclass
class ApplyNode(BaseWorkflowNode):
    """执行修改计划。"""

    def run(self, ctx: CodeWorkflowContext) -> str:
        relative_path = str(ctx.patch_plan.get("relative_path") or ctx.target_file or "")
        old_text = str(ctx.patch_plan.get("old_text") or "")
        new_text = str(ctx.patch_plan.get("new_text") or "")
        expected_occurrences = int(ctx.patch_plan.get("expected_occurrences") or 1)

        if old_text and new_text:
            result = replace_text_in_file(
                str(ctx.workspace_dir),
                relative_path,
                old_text,
                new_text,
                expected_occurrences,
            )
        else:
            result = write_text_file(
                str(ctx.workspace_dir),
                relative_path,
                str(ctx.patch_plan.get("content") or ""),
                overwrite=True,
            )

        ctx.apply_result = result
        ctx.logs.append(f"apply_result={result}")
        return "verify"


@dataclass
class VerifyNode(BaseWorkflowNode):
    """读取文件并确认修改结果。"""

    def run(self, ctx: CodeWorkflowContext) -> str:
        if not ctx.apply_result.get("ok"):
            ctx.verification_result = {"ok": False, "error": "apply failed"}
            return "report"

        path = str(ctx.apply_result.get("path") or ctx.target_file or "")
        snapshot = read_text_file(str(ctx.workspace_dir), path)
        ctx.verification_result = snapshot
        ctx.logs.append(f"verification={snapshot.get('ok')}")
        return "report"


@dataclass
class ReportNode(BaseWorkflowNode):
    """
    把 workflow 过程总结成最终答案。

    最终输出不是工具日志，而是对用户可读的简短结果。
    """

    def run(self, ctx: CodeWorkflowContext) -> str:
        system_prompt = (
            "你是一个 workflow 报告生成器。"
            "基于执行日志、修改结果和验证结果，输出一段简洁中文总结。"
        )
        user_content = (
            f"用户目标：{ctx.goal}\n"
            f"意图：{ctx.intent}\n"
            f"修改计划：{ctx.patch_plan}\n"
            f"执行结果：{ctx.apply_result}\n"
            f"验证结果：{ctx.verification_result}\n"
            f"日志：{ctx.logs}\n"
        )
        ctx.report = ask_llm_text(system_prompt, user_content)
        return "done"

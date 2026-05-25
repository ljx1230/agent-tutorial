from __future__ import annotations

from dataclasses import dataclass

from demo8.framework import BaseWorkflowNode
from demo8.nodes import ClassifyNode, InspectNode, PlanNode, VerifyNode
from demo8.tools import read_text_file, replace_text_in_file, write_text_file
from demo6.framework import ask_llm_text

from demo9.hitl_context import HitlWorkflowContext


def _preview_text(value: str, max_length: int = 500) -> str:
    """让终端确认信息更短一点，避免一大段代码直接糊满屏幕。"""
    if len(value) <= max_length:
        return value
    return value[:max_length] + "\n...省略..."


@dataclass
class ApprovalNode(BaseWorkflowNode):
    """
    人工确认节点。

    这个节点是第九课的核心：
    - 模型可以给出修改计划
    - 但真正写文件之前，必须先给人看
    - 人工同意后，workflow 才能进入 apply 节点
    """

    def run(self, ctx: HitlWorkflowContext) -> str:
        if not ctx.approval_required:
            ctx.approved = True
            ctx.logs.append("approval skipped")
            return "approved"

        if ctx.intent == "summary":
            ctx.logs.append("approval skipped for summary task")
            return "approved"

        relative_path = str(ctx.patch_plan.get("relative_path") or ctx.target_file or "")
        old_text = str(ctx.patch_plan.get("old_text") or "")
        new_text = str(ctx.patch_plan.get("new_text") or "")
        rationale = str(ctx.patch_plan.get("rationale") or "模型没有提供修改理由。")

        print("\n--- 待确认的修改计划 ---")
        print(f"目标文件：{relative_path}")
        print(f"修改理由：{rationale}")

        if old_text:
            print("\n将被替换的旧内容：")
            print(_preview_text(old_text))

        if new_text:
            print("\n准备写入的新内容：")
            print(_preview_text(new_text))

        answer = input("\n是否允许执行这个修改？输入 yes 执行，其他内容取消：").strip().lower()

        if answer in {"yes", "y"}:
            ctx.approved = True
            ctx.approval_note = "human approved"
            ctx.logs.append("approval=approved")
            return "approved"

        ctx.rejected = True
        ctx.approval_note = "human rejected"
        ctx.human_feedback = input("可以输入取消原因，直接回车跳过：").strip()
        ctx.logs.append(f"approval=rejected, feedback={ctx.human_feedback!r}")
        return "rejected"


@dataclass
class SafeApplyNode(BaseWorkflowNode):
    """
    带确认保护的执行节点。

    第八课的 ApplyNode 会直接执行修改；第九课这里多了一道硬约束：
    没有人工确认，就不允许写文件。
    """

    def run(self, ctx: HitlWorkflowContext) -> str:
        if ctx.approval_required and not ctx.approved:
            ctx.apply_result = {"ok": False, "error": "human approval is required before applying changes"}
            ctx.logs.append("apply blocked: approval missing")
            return "report"

        relative_path = str(ctx.patch_plan.get("relative_path") or ctx.target_file or "")
        old_text = str(ctx.patch_plan.get("old_text") or "")
        new_text = str(ctx.patch_plan.get("new_text") or "")
        expected_occurrences = int(ctx.patch_plan.get("expected_occurrences") or 1)

        if relative_path:
            ctx.before_snapshot = read_text_file(str(ctx.workspace_dir), relative_path)
            ctx.logs.append(f"backup_before_apply={ctx.before_snapshot.get('ok')}")

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
class HitlReportNode(BaseWorkflowNode):
    """生成包含确认结果的最终报告。"""

    def run(self, ctx: HitlWorkflowContext) -> str:
        if ctx.rejected:
            ctx.report = (
                "任务已取消：修改计划没有通过人工确认，所以没有写入任何文件。"
                f"\n取消原因：{ctx.human_feedback or '未填写'}"
            )
            return "done"

        system_prompt = (
            "你是一个 workflow 报告生成器。"
            "请基于执行日志、审批结果、修改结果和验证结果，输出一段简洁中文总结。"
        )
        user_content = (
            f"用户目标：{ctx.goal}\n"
            f"意图：{ctx.intent}\n"
            f"审批结果：approved={ctx.approved}, rejected={ctx.rejected}, note={ctx.approval_note}\n"
            f"修改计划：{ctx.patch_plan}\n"
            f"执行结果：{ctx.apply_result}\n"
            f"验证结果：{ctx.verification_result}\n"
            f"日志：{ctx.logs}\n"
        )
        ctx.report = ask_llm_text(system_prompt, user_content)
        return "done"


__all__ = [
    "ApprovalNode",
    "ClassifyNode",
    "HitlReportNode",
    "InspectNode",
    "PlanNode",
    "SafeApplyNode",
    "VerifyNode",
]

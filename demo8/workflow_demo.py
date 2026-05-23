from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from demo6.framework import get_api_key

from demo8.config import MAX_WORKFLOW_STEPS, WORKSPACE_DIR
from demo8.example_context import CodeWorkflowContext
from demo8.framework import Workflow
from demo8.nodes import ApplyNode, ClassifyNode, InspectNode, PlanNode, ReportNode, VerifyNode


def build_workflow() -> Workflow:
    """
    构造一条固定的 workflow。

    这就是第八课要展示的核心：
    - framework 层只负责 workflow 能力
    - example 层负责把节点和业务任务拼起来
    """
    classify = ClassifyNode(name="classify")
    inspect = InspectNode(name="inspect")
    plan = PlanNode(name="plan")
    apply_node = ApplyNode(name="apply")
    verify = VerifyNode(name="verify")
    report = ReportNode(name="report")

    classify.connect("inspect", inspect)
    inspect.connect("plan", plan)
    inspect.connect("report", report)
    plan.connect("apply", apply_node)
    apply_node.connect("verify", verify)
    verify.connect("report", report)

    return Workflow(start_node=classify, max_steps=MAX_WORKFLOW_STEPS)


def main() -> None:
    """程序入口。"""
    # 这里只做一次环境检查，确保后面的节点调用 LLM 时不会因为缺 key 才报错。
    _ = get_api_key()
    print("Workflow Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我找到 utils.py 里的 greet_user，并把空名字处理改得更友好。")
    print(f"工作区目录：{WORKSPACE_DIR}")

    workflow = build_workflow()

    while True:
        goal = input("\n你：").strip()

        if not goal:
            print("请输入任务目标。")
            continue

        if goal.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        ctx = CodeWorkflowContext(goal=goal, workspace_dir=WORKSPACE_DIR)
        try:
            result = workflow.run(ctx)
        except Exception as exc:
            print(f"\n执行失败：{exc}")
            continue

        print("\n--- Workflow Logs ---")
        for line in result.logs:
            print(line)
        print("\n--- Result ---")
        print(result.report or "任务完成。")


if __name__ == "__main__":
    main()

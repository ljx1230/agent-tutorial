from __future__ import annotations

from .context import WorkflowContext
from .node import BaseWorkflowNode


class Workflow:
    """
    最小 workflow 执行器。

    它只负责三件事：
    - 执行当前节点
    - 读取节点返回的 action
    - 根据 action 跳到下一节点
    """

    def __init__(self, start_node: BaseWorkflowNode, max_steps: int = 6) -> None:
        self.start_node = start_node
        self.max_steps = max_steps

    def run(self, ctx: WorkflowContext) -> WorkflowContext:
        """执行 workflow，直到没有下一跳或达到上限。"""
        current: BaseWorkflowNode | None = self.start_node
        for step_index in range(1, self.max_steps + 1):
            if current is None:
                break

            ctx.logs.append(f"step={step_index}, node={current.name}")
            action = current.run(ctx)
            ctx.logs.append(f"node={current.name} -> action={action}")

            if action == "done":
                break

            next_node = current.route(action)
            if next_node is None:
                ctx.logs.append(f"no route for action={action}, stop workflow")
                break

            current = next_node

        return ctx

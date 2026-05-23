from __future__ import annotations

from .context import WorkflowContext
from .node import WorkflowNode


class Workflow:
    """
    一个最小的工作流执行器。

    它只负责：
    - 持续执行节点
    - 根据节点返回的 action 路由到下一跳
    - 限制最大步数，避免循环失控
    """

    def __init__(self, start_node: WorkflowNode, max_steps: int = 6) -> None:
        self.start_node = start_node
        self.max_steps = max_steps

    def run(self, ctx: WorkflowContext) -> WorkflowContext:
        """执行 workflow，直到没有后续节点或达到上限。"""
        current: WorkflowNode | None = self.start_node
        for step_index in range(1, self.max_steps + 1):
            if current is None:
                break

            ctx.logs.append(f"step={step_index}, node={current.name}")
            action = current.run(ctx)
            ctx.logs.append(f"node={current.name} -> action={action}")

            if action == "done":
                break

            next_node = getattr(current, "route", lambda _action: None)(action)
            if next_node is None:
                ctx.logs.append(f"没有找到 action={action} 的下一跳，工作流结束。")
                break
            current = next_node

        return ctx

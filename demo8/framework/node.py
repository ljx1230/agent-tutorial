from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .context import WorkflowContext


class WorkflowNode(Protocol):
    """工作流节点协议。"""

    name: str

    def run(self, ctx: WorkflowContext) -> str:
        ...


@dataclass
class BaseWorkflowNode:
    """工作流节点基类。"""

    name: str
    next_nodes: dict[str, WorkflowNode] = field(default_factory=dict)

    def connect(self, action: str, node: WorkflowNode) -> WorkflowNode:
        """连接到下一个节点。"""
        self.next_nodes[action] = node
        return node

    def route(self, action: str) -> WorkflowNode | None:
        """根据 action 选择下一跳节点。"""
        return self.next_nodes.get(action)

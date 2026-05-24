from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .context import WorkflowContext


@dataclass
class BaseWorkflowNode(ABC):
    """
    工作流节点基类。

    这一层只保留两类能力：
    - run: 当前节点做什么
    - connect / route: 节点怎么把流程交给下一跳
    """

    name: str
    next_nodes: dict[str, "BaseWorkflowNode"] = field(default_factory=dict)

    @abstractmethod
    def run(self, ctx: WorkflowContext) -> str:
        """执行当前节点，并返回下一步 action。"""

    def connect(self, action: str, node: "BaseWorkflowNode") -> "BaseWorkflowNode":
        """连接到下一跳节点。"""
        self.next_nodes[action] = node
        return node

    def route(self, action: str) -> "BaseWorkflowNode | None":
        """根据 action 选择下一跳节点。"""
        return self.next_nodes.get(action)

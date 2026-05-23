from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowContext:
    """
    工作流上下文。

    这是框架层的最小共享状态对象：
    - goal: 当前任务目标
    - shared: 节点之间共享的通用字典
    - logs: 工作流日志
    """

    goal: str
    shared: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)

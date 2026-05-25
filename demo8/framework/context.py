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


@dataclass
class HitlContext(WorkflowContext):
    """
    带人工打断能力的通用 workflow 上下文。

    - approval_required: 当前 workflow 是否需要人工确认
    - approved: 人工是否批准
    - rejected: 人工是否拒绝
    - approval_note: 框架或节点写入的确认备注
    - human_feedback: 人工拒绝或补充时留下的反馈
    """

    approval_required: bool = True
    approved: bool = False
    rejected: bool = False
    approval_note: str = ""
    human_feedback: str = ""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from demo8.example_context import CodeWorkflowContext
from demo8.framework import HitlContext


@dataclass
class HitlWorkflowContext(HitlContext, CodeWorkflowContext):
    """
    这里是代码修改workflow才需要的文件快照。
    """

    before_snapshot: dict[str, Any] = field(default_factory=dict) # 保存文件之前的内容

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorkflowContext:
    """
    工作流上下文。

    这是 workflow 里的“共享状态对象”：
    节点之间不通过全局变量传值，而是统一通过 context 读写。
    """

    goal: str
    workspace_dir: Path
    intent: str = "edit"
    target_file: str | None = None
    search_query: str | None = None
    search_hits: list[dict[str, Any]] = field(default_factory=list)
    file_snapshot: dict[str, Any] = field(default_factory=dict)
    patch_plan: dict[str, Any] = field(default_factory=dict)
    apply_result: dict[str, Any] = field(default_factory=dict)
    verification_result: dict[str, Any] = field(default_factory=dict)
    report: str = ""
    logs: list[str] = field(default_factory=list)

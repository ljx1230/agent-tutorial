from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from demo8.framework import WorkflowContext


@dataclass
class CodeWorkflowContext(WorkflowContext):
    """
    第八课示例自己的业务上下文。

    这里放的是“本地代码修改工作流”专用字段，
    不再污染 framework 层。
    """

    workspace_dir: Path = Path(".")
    intent: str = "edit"
    target_file: str | None = None
    search_query: str | None = None
    search_hits: list[dict[str, Any]] = field(default_factory=list)
    file_snapshot: dict[str, Any] = field(default_factory=dict)
    patch_plan: dict[str, Any] = field(default_factory=dict)
    apply_result: dict[str, Any] = field(default_factory=dict)
    verification_result: dict[str, Any] = field(default_factory=dict)
    report: str = ""

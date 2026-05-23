from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolHandler = Callable[..., dict[str, Any]]


@dataclass
class ToolDefinition:
    """描述一个可注册到运行时中的工具。"""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler

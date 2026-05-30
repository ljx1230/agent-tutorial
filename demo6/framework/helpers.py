from __future__ import annotations

from collections.abc import Callable
from types import ModuleType
from typing import Any

from .mcp_adapter import McpServerConfig, load_mcp_tools
from .message_store import MessageStore
from .runtime import AgentRuntime
from .tool_registry import ToolRegistry


def create_runtime(
    api_key: str,
    tools: list[Callable[..., dict[str, Any]]] | None = None,
    tool_modules: list[ModuleType] | None = None,
    mcp_servers: list[McpServerConfig] | None = None,
    *,
    max_loops: int = 8,
    max_turns: int = 6,
    system_message: dict[str, str] | None = None,
) -> tuple[AgentRuntime, MessageStore]:
    """
    创建一个可直接使用的 runtime 和 message store。

    """
    registry = ToolRegistry()

    for tool in tools or []:
        registry.register(tool)

    for module in tool_modules or []:
        registry.register_tools_from_module(module)

    for server_config in mcp_servers or []:
        for mcp_tool in load_mcp_tools(server_config):
            registry.register(mcp_tool)

    runtime = AgentRuntime(
        api_key=api_key,
        tool_registry=registry,
        max_loops=max_loops,
        system_message=system_message,
    )
    message_store = MessageStore(max_turns=max_turns)
    return runtime, message_store

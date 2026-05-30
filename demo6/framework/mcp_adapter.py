from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .agent_types import ToolDefinition


@dataclass
class McpServerConfig:
    """
    描述一个通过 stdio 启动的 MCP Server。

    MCP 支持多种 transport。这里只演示最简单的 stdio 模式。
    """

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] | None = None


def _extract_mcp_result_content(result: Any) -> dict[str, Any]:
    """
    把 MCP call_tool 的结果转换成普通 dict。

    demo6 的 ToolRegistry 约定工具返回 dict[str, Any]，
    但 MCP SDK 返回的是结构化对象，所以这里做一层格式适配。
    """
    content_items = getattr(result, "content", [])
    texts: list[str] = []

    for item in content_items:
        text = getattr(item, "text", None)
        if text is not None:
            texts.append(text)
        else:
            texts.append(str(item))

    return {
        "ok": not getattr(result, "isError", False),
        "content": "\n".join(texts),
    }


async def _list_mcp_tools(server_config: McpServerConfig) -> list[Any]:
    """连接 MCP Server 并读取它暴露的工具列表。"""
    server_params = StdioServerParameters(
        command=server_config.command,
        args=server_config.args,
        env=server_config.env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            return list(result.tools)


async def _call_mcp_tool(
    server_config: McpServerConfig,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """连接 MCP Server 并调用指定工具。"""
    server_params = StdioServerParameters(
        command=server_config.command,
        args=server_config.args,
        env=server_config.env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return _extract_mcp_result_content(result)


def load_mcp_tools(server_config: McpServerConfig) -> list[ToolDefinition]:
    """
    把一个 MCP Server 暴露的 tools 转换成 demo6 框架里的 ToolDefinition。

    - MCP Server 负责按标准协议暴露工具
    - demo6 Agent Runtime 仍然只认识 ToolDefinition
    - adapter 把两边接起来
    """
    mcp_tools = asyncio.run(_list_mcp_tools(server_config))
    tool_definitions: list[ToolDefinition] = []

    for mcp_tool in mcp_tools:
        original_name = mcp_tool.name
        exposed_name = f"{server_config.name}_{original_name}"

        def handler(
            _tool_name: str = original_name,
            _server_config: McpServerConfig = server_config,
            **arguments: Any,
        ) -> dict[str, Any]:
            return asyncio.run(_call_mcp_tool(_server_config, _tool_name, arguments))

        tool_definitions.append(
            ToolDefinition(
                name=exposed_name,
                description=f"[MCP:{server_config.name}] {mcp_tool.description or original_name}",
                parameters=mcp_tool.inputSchema,
                handler=handler,
            )
        )

    return tool_definitions

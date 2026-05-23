from __future__ import annotations

import json
import inspect
from types import ModuleType
from typing import Any, Callable

from .agent_types import ToolDefinition


class ToolRegistry:
    """
    管理工具注册、schema 暴露和工具执行。

    这是第六课里非常核心的一层抽象：
    - 上层 runtime 不直接关心每个工具怎么实现
    - 下层工具函数也不需要知道 runtime 的细节
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def _normalize_tool(self, tool: ToolDefinition | Callable[..., dict[str, Any]]) -> ToolDefinition:
        """
        把 ToolDefinition 或 @tool 装饰过的函数统一转换成 ToolDefinition。

        这样框架同时支持两种定义方式：
        - 显式 ToolDefinition
        - 更轻量的 @tool
        """
        if isinstance(tool, ToolDefinition):
            return tool

        tool_definition = getattr(tool, "__tool_definition__", None)
        if isinstance(tool_definition, ToolDefinition):
            return tool_definition

        raise TypeError(
            "register(...) 只接受 ToolDefinition 或使用 @tool 装饰过的函数。"
        )

    def register(self, tool: ToolDefinition | Callable[..., dict[str, Any]]) -> None:
        """注册一个工具。"""
        tool_definition = self._normalize_tool(tool)
        self._tools[tool_definition.name] = tool_definition

    def register_many(self, *tools: ToolDefinition | Callable[..., dict[str, Any]]) -> None:
        """一次注册多个工具。"""
        for tool in tools:
            self.register(tool)

    def register_tools_from_module(self, module: ModuleType) -> None:
        """
        从一个模块中批量注册所有带 @tool 的函数。

        这样工具模块可以只负责定义函数，注册阶段只需要传模块本身。
        """
        for _, value in inspect.getmembers(module):
            tool_definition = getattr(value, "__tool_definition__", None)
            if isinstance(tool_definition, ToolDefinition):
                self.register(value)

    def build_tools_payload(self) -> list[dict[str, Any]]:
        """
        生成发送给模型的 tools payload。

        这一步相当于把 Python 世界里的工具定义，
        翻译成 LLM 能理解的 OpenAI/DeepSeek tools 格式。
        """
        payload: list[dict[str, Any]] = []

        for tool in self._tools.values():
            payload.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )

        return payload

    def execute_tool_call(self, tool_call: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        执行模型返回的单个 tool_call。

        这里做了两件事：
        1. 把 arguments 从 JSON 字符串解析成 Python 字典
        2. 找到对应 handler 并执行
        """
        function_info = tool_call.get("function", {})
        tool_name = function_info.get("name", "unknown_tool")
        raw_arguments = function_info.get("arguments", "{}")

        # 模型返回的参数是字符串，不是现成 dict，所以这里必须先 parse。
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError as exc:
            return tool_name, {
                "ok": False,
                "error": f"工具参数不是合法 JSON：{exc}",
                "raw_arguments": raw_arguments,
            }

        tool = self._tools.get(tool_name)
        if tool is None:
            return tool_name, {
                "ok": False,
                "error": f"未知工具：{tool_name}",
                "arguments": arguments,
            }

        # 这里直接按关键字参数调用工具函数。
        # 这也是为什么 @tool 的函数签名要和 schema 一致。
        try:
            return tool_name, tool.handler(**arguments)
        except KeyError as exc:
            return tool_name, {
                "ok": False,
                "error": f"缺少必要参数：{exc}",
                "arguments": arguments,
            }
        except TypeError as exc:
            return tool_name, {
                "ok": False,
                "error": f"工具参数不匹配：{exc}",
                "arguments": arguments,
            }

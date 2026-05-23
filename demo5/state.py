from __future__ import annotations

from typing import Any


def create_agent_state() -> dict[str, Any]:
    """
    创建当前任务的状态对象。

    第五课里，真实一点的 Agent 会同时维护：
    - messages: 给模型看的会话上下文
    - state: 给程序判断的结构化事实
    """
    return {
        "current_goal": None,
        "last_tool_name": None,
        "last_tool_result": None,
        "last_created_path": None,
        "last_read_content": None,
        "completed": False,
        "loop_count": 0,
    }


def update_state_from_tool_result(
    state: dict[str, Any],
    tool_name: str,
    tool_result: dict[str, Any],
) -> None:
    """把最近一次工具调用结果同步进 state。"""
    state["last_tool_name"] = tool_name
    state["last_tool_result"] = tool_result

    if tool_name == "create_text_file" and tool_result.get("ok"):
        state["last_created_path"] = tool_result.get("path")

    if tool_name == "read_text_file" and tool_result.get("ok"):
        state["last_read_content"] = tool_result.get("content")

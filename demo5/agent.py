from __future__ import annotations

import json
from typing import Any

from config import MAX_AGENT_LOOPS, MAX_HISTORY_TURNS
from llm import call_llm, create_system_message
from state import create_agent_state, update_state_from_tool_result
from tools import build_tools, execute_tool_call


def trim_messages(messages: list[dict[str, Any]], max_turns: int) -> list[dict[str, Any]]:
    """
    裁剪最近若干轮对话历史。

    这里只裁 user / assistant / tool 这类上下文消息，不包含 system。
    """
    max_message_count = max_turns * 4
    if len(messages) > max_message_count:
        return messages[-max_message_count:]
    return messages


def build_runtime_messages(
    user_messages: list[dict[str, Any]],
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    组装本轮请求发送给模型的消息。

    第五课里既保留 messages，也保留 state：
    - messages 负责会话记忆和工具历史
    - state 负责结构化任务状态
    """
    state_message = {
        "role": "system",
        "content": (
            "当前任务状态摘要："
            f" current_goal={state.get('current_goal')!r};"
            f" last_tool_name={state.get('last_tool_name')!r};"
            f" last_created_path={state.get('last_created_path')!r};"
            f" completed={state.get('completed')!r};"
            f" loop_count={state.get('loop_count')!r}."
        ),
    }

    return [
        create_system_message(),
        state_message,
        *trim_messages(user_messages, MAX_HISTORY_TURNS),
    ]


def run_react_agent(
    api_key: str,
    user_goal: str,
    messages: list[dict[str, Any]],
) -> str:
    """
    执行第五课的 ReAct Agent 主循环。

    相比第四课，这里不是程序先写死下一步 action，
    而是模型自己根据上下文和工具结果决定是否继续调用工具。
    """
    tools = build_tools()
    state = create_agent_state()
    state["current_goal"] = user_goal

    for loop_index in range(1, MAX_AGENT_LOOPS + 1):
        state["loop_count"] = loop_index
        request_messages = build_runtime_messages(messages, state)
        assistant_message = call_llm(api_key=api_key, messages=request_messages, tools=tools)
        tool_calls = assistant_message.get("tool_calls") or []

        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call.get("function", {}).get("name", "unknown_tool")
                raw_arguments = tool_call.get("function", {}).get("arguments", "{}")

                print(f"\n[循环 {loop_index}] 模型选择工具：{tool_name}")
                print(f"[工具参数] {raw_arguments}")

                executed_tool_name, tool_result = execute_tool_call(tool_call)
                update_state_from_tool_result(
                    state=state,
                    tool_name=executed_tool_name,
                    tool_result=tool_result,
                )

                print(f"[工具结果] {json.dumps(tool_result, ensure_ascii=False)}")

                # 工具结果既写回 messages，也同步到 state。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

            continue

        final_answer = assistant_message.get("content") or "任务已处理完成。"
        state["completed"] = True
        messages.append({"role": "assistant", "content": final_answer})
        return final_answer

    raise RuntimeError("超过最大循环次数，任务仍未完成。可以把任务描述得更具体一点再重试。")

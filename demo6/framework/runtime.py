from __future__ import annotations

import json
from typing import Any

from .llm import call_llm, create_system_message
from .message_store import MessageStore
from .tool_registry import ToolRegistry


class AgentRuntime:
    """
    一个最小可扩展的 Agent Runtime。

    第六课的核心，不是增加新能力，而是把前 1 到 5 课里已经验证过的能力
    抽成一个更通用的运行时。
    """

    def __init__(
        self,
        api_key: str,
        tool_registry: ToolRegistry,
        max_loops: int = 8,
        system_message: dict[str, str] | None = None,
    ) -> None:
        self.api_key = api_key
        self.tool_registry = tool_registry
        self.max_loops = max_loops
        self.system_message = system_message

    def create_state(self, goal: str) -> dict[str, Any]:
        """
        创建通用任务状态。

        这里有意不写死“文件路径”“文件内容”这类具体业务字段，
        而是通过 shared_context 给不同任务自己扩展。
        """
        return {
            "goal": goal,
            "shared_context": {},
            "last_tool_name": None,
            "last_tool_result": None,
            "completed": False,
            "loop_count": 0,
        }

    def get_system_message(self) -> dict[str, str]:
        """返回当前运行时使用的 system message。"""
        return self.system_message or create_system_message()

    def build_runtime_message(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        组装单条运行时调度消息。

        动态状态不伪装成固定规则，而是单独作为本轮调度消息交给模型。
        """
        # 这一条消息是“运行时调度消息”。
        # 它不是固定系统规则，也不是用户原始输入，
        # 而是程序在每轮循环里主动告诉模型当前任务状态。
        return {
            "role": "user",
            "content": (
                "当前运行时状态如下，请基于这些信息决定下一步：\n"
                f"- goal: {state.get('goal')!r}\n"
                f"- shared_context: {json.dumps(state.get('shared_context', {}), ensure_ascii=False)}\n"
                f"- last_tool_name: {state.get('last_tool_name')!r}\n"
                f"- last_tool_result: {json.dumps(state.get('last_tool_result'), ensure_ascii=False)}\n"
                f"- completed: {state.get('completed')!r}\n"
                f"- loop_count: {state.get('loop_count')!r}\n"
                "如果任务还没完成，就继续调用合适工具；如果任务已完成，就直接自然语言回答。"
            ),
        }

    def build_runtime_messages(
        self,
        message_store: MessageStore,
        state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        组装本轮请求的 messages。

        这里的顺序很重要：
        1. system message
        2. 历史消息
        3. 当前这轮的运行时状态
        """
        return [
            self.get_system_message(),
            *message_store.snapshot(),
            self.build_runtime_message(state),
        ]

    def update_state_from_tool_result(
        self,
        state: dict[str, Any],
        tool_name: str,
        tool_result: dict[str, Any],
    ) -> None:
        """
        根据工具结果更新通用状态。

        工具如果返回了 context_updates，
        runtime 会把这些信息统一合并到 shared_context。
        这样工具和任务状态之间就有了一个通用通信面。
        """
        state["last_tool_name"] = tool_name
        state["last_tool_result"] = tool_result

        context_updates = tool_result.get("context_updates")
        if isinstance(context_updates, dict):
            state["shared_context"].update(context_updates)

    def on_tool_result(
        self,
        state: dict[str, Any],
        tool_name: str,
        tool_result: dict[str, Any],
        message_store: MessageStore,
    ) -> None:
        """工具执行后的扩展钩子，默认不做额外处理。"""
        return None

    def run(self, goal: str, message_store: MessageStore) -> str:
        """
        执行一轮完整的 Agent 任务。

        这是第六课最重要的主循环：
        - 组装消息
        - 调模型
        - 如果模型要调工具，就执行工具
        - 把工具结果写回 messages 和 state
        - 如果模型不再调工具，就把自然语言答复作为最终结果返回
        """
        state = self.create_state(goal)
        tools_payload = self.tool_registry.build_tools_payload()

        for loop_index in range(1, self.max_loops + 1):
            state["loop_count"] = loop_index
            request_messages = self.build_runtime_messages(message_store, state)
            assistant_message = call_llm(
                api_key=self.api_key,
                messages=request_messages,
                tools=tools_payload,
            )
            tool_calls = assistant_message.get("tool_calls") or []

            if tool_calls:
                # 先把 assistant 的“工具调用意图”写进消息历史。
                # 这样下一轮模型能看到自己上一步是如何决策的。
                message_store.append(
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

                    executed_tool_name, tool_result = self.tool_registry.execute_tool_call(tool_call)
                    self.update_state_from_tool_result(
                        state=state,
                        tool_name=executed_tool_name,
                        tool_result=tool_result,
                    )
                    self.on_tool_result(
                        state=state,
                        tool_name=executed_tool_name,
                        tool_result=tool_result,
                        message_store=message_store,
                    )

                    print(f"[工具结果] {json.dumps(tool_result, ensure_ascii=False)}")

                    # 再把工具真实执行结果回写成 role=tool 的消息。
                    # 这是 ReAct / tool-calling 闭环里非常关键的一步。
                    message_store.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(tool_result, ensure_ascii=False),
                        }
                    )

                continue

            # 如果本轮没有 tool_calls，就把 assistant 的自然语言输出
            # 当作“任务完成后的最终答复”。
            final_answer = assistant_message.get("content") or "任务已处理完成。"
            state["completed"] = True
            message_store.append({"role": "assistant", "content": final_answer})
            return final_answer

        raise RuntimeError("超过最大循环次数，任务仍未完成。可以把任务描述得更具体一点再重试。")

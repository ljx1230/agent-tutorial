from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from demo6.framework import MessageStore, ToolRegistry, get_api_key

from demo7.coding_runtime import CodingAgentRuntime
from demo7.config import MAX_HISTORY_TURNS, WORKSPACE_DIR
from demo7.coding_tools import register_coding_tools


def main() -> None:
    api_key = get_api_key()
    registry = ToolRegistry()
    register_coding_tools(registry)

    # 这里直接复用 demo6.framework 里的 ToolRegistry 和 MessageStore。
    runtime = CodingAgentRuntime(api_key=api_key, tool_registry=registry)
    message_store = MessageStore(max_turns=MAX_HISTORY_TURNS)

    print("Coding Agent Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我找到 greet_user 的实现，并给空名字加一个更友好的处理。")
    print(f"工作区目录：{WORKSPACE_DIR}")
    print(f"当前会保留最近 {MAX_HISTORY_TURNS} 轮会话记忆。")

    while True:
        user_goal = input("\n你：").strip()

        if not user_goal:
            print("请输入任务目标。")
            continue

        if user_goal.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        # coding agent 同样使用 message history。
        # 这意味着多轮任务约束、上文要求、前一次修改结论都能被保留下来。
        message_store.append({"role": "user", "content": user_goal})

        try:
            final_answer = runtime.run(goal=user_goal, message_store=message_store)
        except Exception as exc:
            print(f"\n执行失败：{exc}")
            if message_store.messages and message_store.messages[-1]["role"] == "user":
                message_store.messages.pop()
            continue

        print(f"\n助手：{final_answer}")


if __name__ == "__main__":
    main()

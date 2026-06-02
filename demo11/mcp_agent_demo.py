from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo6.framework import McpServerConfig, create_runtime, get_api_key


def create_mcp_system_message() -> dict[str, str]:
    return {
        "role": "system",
        "content": (
            "你是一个支持 MCP 工具调用的 Agent。"
            "当用户询问天气、城市天气、出行建议时，优先调用天气 MCP 工具获取真实工具结果。"
            "如果工具返回不支持某个城市，请如实告诉用户当前支持哪些城市。"
            "不要伪造天气数据。回答使用简洁中文。"
        ),
    }


def main() -> None:
    api_key = get_api_key()
    server_path = Path(__file__).resolve().parent / "weather_server.py"

    runtime, message_store = create_runtime(
        api_key=api_key,
        mcp_servers=[
            McpServerConfig(
                name="weather",
                command=sys.executable,
                args=[str(server_path)],
            )
        ],
        max_loops=5,
        max_turns=6,
        system_message=create_mcp_system_message(),
    )

    print("MCP Agent Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我查一下杭州今天的天气，并给我一个出行建议。")
    print("本节课的天气数据来自 demo11/weather_server.py 里的 MCP Server。")

    while True:
        user_goal = input("\n你：").strip()

        if not user_goal:
            print("请输入任务目标。")
            continue

        if user_goal.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

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

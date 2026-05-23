from __future__ import annotations

from agent import run_react_agent, trim_messages
from config import GENERATED_FILES_DIR, MAX_HISTORY_TURNS
from llm import get_api_key


def main() -> None:
    """程序入口。"""
    api_key = get_api_key()

    print("ReAct Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我生成一份 Python 学习计划，保存成 markdown 文件，然后再读出来帮我检查一下格式。")
    print(f"工具操作目录：{GENERATED_FILES_DIR}")
    print(f"当前会保留最近 {MAX_HISTORY_TURNS} 轮会话记忆。")

    messages: list[dict[str, object]] = []

    while True:
        user_goal = input("\n你：").strip()

        if not user_goal:
            print("请输入任务目标。")
            continue

        if user_goal.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        messages.append({"role": "user", "content": user_goal})
        messages = trim_messages(messages, MAX_HISTORY_TURNS)

        try:
            final_answer = run_react_agent(
                api_key=api_key,
                user_goal=user_goal,
                messages=messages,
            )
        except Exception as exc:
            print(f"\n执行失败：{exc}")
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            continue

        messages = trim_messages(messages, MAX_HISTORY_TURNS)
        print(f"\n助手：{final_answer}")


if __name__ == "__main__":
    main()

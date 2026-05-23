from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from demo6.framework import create_runtime, get_api_key

import demo6.builtin_tools as builtin_tools
from demo6.config import GENERATED_FILES_DIR, MAX_HISTORY_TURNS


def main() -> None:
    """
    程序入口。

    - 读取 API Key
    - 创建 runtime 和 message_store
    - 进入交互循环

    真正的框架逻辑都已经被放到 demo6.framework 子包里了。
    """
    api_key = get_api_key()
    # 这里展示的是第六课推荐的“最小使用方式”：
    # 只给 create_runtime(...) 一个工具模块，它会自动帮我们注册带 @tool 的函数。
    runtime, message_store = create_runtime(
        api_key=api_key,
        tool_modules=[builtin_tools],
        max_turns=MAX_HISTORY_TURNS,
    )

    print("Framework Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我生成一份 Python 学习计划，保存成 markdown 文件，然后再读出来帮我检查一下格式。")
    print(f"工具操作目录：{GENERATED_FILES_DIR}")
    print(f"当前会保留最近 {MAX_HISTORY_TURNS} 轮会话记忆。")

    while True:
        user_goal = input("\n你：").strip()

        if not user_goal:
            print("请输入任务目标。")
            continue

        if user_goal.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        # 会话消息由 MessageStore 托管
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

"""
多轮对话 + Memory 示例

这个示例演示一个最基础的“带记忆的 Agent”：
1. 使用 system prompt 约束助手身份
2. 通过 user / assistant 消息维护多轮对话历史
3. 使用 requests 调用一次 DeepSeek Chat API
4. 通过“保留最近若干轮对话”的方式模拟短期记忆

运行前请先安装依赖：
    pip install requests

并设置环境变量：
    PowerShell:
        $env:DEEPSEEK_API_KEY="你的 API Key"
"""

from __future__ import annotations

import os

import requests


API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-v4-flash"

# 保留最近多少轮用户/助手对话。
# 一轮对话通常由两条消息组成：
# - 一条 user
# - 一条 assistant
# 这里保留最近 4 轮，足够演示“短期记忆”的概念。
MAX_TURNS = 4


def create_system_message() -> dict[str, str]:
    """创建 system prompt。"""
    return {
        "role": "system",
        "content": (
            "你是一个面向初学者的 Python 和 agent 助手。"
            "请使用简洁、友好、清晰的中文回答。"
            "如果用户的问题依赖上文，请结合对话历史继续回答。"
        ),
    }


def trim_messages(messages: list[dict[str, str]], max_turns: int) -> list[dict[str, str]]:
    """
    裁剪对话历史，只保留 system prompt 和最近若干轮对话。

    为什么要裁剪：
    - 多轮对话越长，发送给模型的 token 就越多
    - token 越多，请求成本和响应时间通常也会增加

    这里采用最容易理解的策略：
    - 永远保留第 1 条 system 消息
    - 其余消息里，只保留最近 max_turns 轮

    一轮对话约等于 2 条消息（user + assistant），
    所以需要保留的非 system 消息数量约为 max_turns * 2。
    """
    if not messages:
        return messages

    system_message = messages[0]
    recent_messages = messages[1:]
    max_message_count = max_turns * 2

    if len(recent_messages) > max_message_count:
        recent_messages = recent_messages[-max_message_count:]

    return [system_message, *recent_messages]


def call_llm(api_key: str, messages: list[dict[str, str]]) -> str:
    """
    调用 DeepSeek Chat API，并返回模型回复文本。

    这里把 messages 整体发送给模型，
    这样模型才能“看到”前面的对话历史。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "thinking": {"type": "disabled"},
        "max_tokens": 300,
        "temperature": 0.7,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"]


def main() -> None:
    """程序入口。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )

    # messages 就是这个示例里的“短期记忆”。
    # 每次用户发言和助手回复，都会被追加到这里。
    messages: list[dict[str, str]] = [create_system_message()]

    print("Memory Demo 已启动。输入 exit 或 quit 结束。")
    print(f"当前会保留最近 {MAX_TURNS} 轮对话作为短期记忆。")

    while True:
        user_input = input("\n你：").strip()

        if not user_input:
            print("请输入内容。")
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        # 先把用户输入加入记忆中。
        messages.append({"role": "user", "content": user_input})

        # 为了避免历史越来越长，发送前先裁剪一次。
        messages = trim_messages(messages, MAX_TURNS)

        try:
            answer = call_llm(api_key=api_key, messages=messages)
        except requests.RequestException as exc:
            print(f"\n请求失败：{exc}")
            # 这次请求失败时，把刚刚加入的 user 消息回滚掉，
            # 避免一次失败请求污染后续对话历史。
            if len(messages) > 1 and messages[-1]["role"] == "user":
                messages.pop()
            continue

        print(f"\n助手：{answer}")

        # 模型回复也必须写回记忆。
        # 否则下一轮用户如果说“展开讲讲”或“换个例子”，
        # 模型可能无法准确理解它是在接着哪一句往下说。
        messages.append({"role": "assistant", "content": answer})

        # 回写 assistant 后再裁剪一次，保证记忆长度稳定。
        messages = trim_messages(messages, MAX_TURNS)


if __name__ == "__main__":
    main()

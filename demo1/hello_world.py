"""
DeepSeek Agent Hello World

这是一个最小可运行的教程示例，演示：
1. 如何组织 system prompt（系统提示词）
2. 如何组织 user prompt（用户提示词）
3. 如何使用 requests 调用一次 DeepSeek Chat API
4. 如何读取并打印模型返回结果

运行前请先安装依赖：
    pip install requests

并设置环境变量：
    PowerShell:
        $env:DEEPSEEK_API_KEY="你的 API Key"
"""

from __future__ import annotations

import json
import os

import requests


# DeepSeek模型API地址： https://api.deepseek.com/chat/completions
API_URL = "https://api.deepseek.com/chat/completions"

# 选用deepseek-v4-flash模型
MODEL_NAME = "deepseek-v4-flash"


def build_messages() -> list[dict[str, str]]:
    """构造一次最基础的对话消息列表。"""
    return [
        {
            "role": "system", # 系统提示词，你给你的AI设定的角色和行为准则
            "content": (
                "你是一个面向初学者的 Python 和 agent 助手。"
                "回答时尽量简洁、友好，并在必要时给出清晰步骤。"
            ),
        },
        {
            "role": "user",
            "content": "请用一句话介绍什么是 Agent，并给一个生活中的类比。", # 用户提示词，用户向AI提出的问题或请求
        },
    ]


def call_llm(api_key: str, messages: list[dict[str, str]]) -> dict:
    """
    调用 DeepSeek Chat Completions 接口。

    参数：
    - api_key: 从环境变量中读取到的 DeepSeek API Key
    - messages: 按 chat 格式组织好的消息列表

    返回：
    - 接口返回的 JSON 字典
    """
    headers = {
        "Content-Type": "application/json",
        # DeepSeek 使用 Bearer Token 鉴权
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        # 模型名称
        "model": MODEL_NAME,
        # 对话消息，包含 system / user / assistant 等角色
        "messages": messages,
        # 非流式输出，方便 hello world 初学者先看完整响应
        "stream": False,
        # 将 thinking 关闭，让返回更接近普通聊天模型，示例也更简单
        "thinking": {"type": "disabled"},
        # 限制一下输出长度，避免教程示例返回太长
        "max_tokens": 200,
        # 适度降低随机性，让教程输出更稳定
        "temperature": 0.7,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    # 如果 HTTP 状态码不是 2xx，这里会直接抛出异常，
    # 便于我们快速定位鉴权失败、配额不足、参数错误等问题。
    response.raise_for_status()

    return response.json()


def main() -> None:
    """程序入口。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )

    messages = build_messages()

    print("=== 发送给模型的消息 ===")
    print(json.dumps(messages, ensure_ascii=False, indent=2))

    result = call_llm(api_key=api_key, messages=messages)

    # OpenAI 兼容格式下，模型的正文通常在：
    # result["choices"][0]["message"]["content"]
    answer = result["choices"][0]["message"]["content"]

    print("\n=== 模型回复 ===")
    print(answer)

    # usage 中通常会带上 token 用量，适合教程里顺手观察成本信息。
    usage = result.get("usage")
    if usage:
        print("\n=== Token 用量 ===")
        print(json.dumps(usage, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

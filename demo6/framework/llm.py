from __future__ import annotations

import os
from typing import Any

import requests
import json

DEFAULT_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL_NAME = "deepseek-v4-flash"
DEFAULT_MAX_COMPLETION_TOKENS = 3000


def get_api_key() -> str:
    """读取 API Key。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )
    return api_key


def create_system_message() -> dict[str, str]:
    """
    定义小型 Agent 框架默认使用的系统提示词。

    这里故意保持得比较通用：
    - 不绑定某个具体业务
    - 只强调 runtime、工具调用、结果真实性
    这样第七课的 coding agent 才能在上面继续定制。
    """

    return {
        "role": "system",
        "content": (
            "你是一个基于小型 Agent Runtime 运行的 ReAct 风格 Agent。"
            "你需要结合用户目标、会话消息、工具结果和运行时状态，自主决定下一步。"
            "如果任务需要外部动作，请调用合适工具。"
            "如果任务已经完成，请直接输出最终自然语言答复。"
            "不要声称工具已执行成功，除非你已经看到了真实的 tool 结果。"
            "回答使用简洁清晰的中文。"
        ),
    }


def call_llm(
    api_key: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    api_url: str = DEFAULT_API_URL,
    model_name: str = DEFAULT_MODEL_NAME,
    max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS,
) -> dict[str, Any]:
    """
    调用 DeepSeek Chat API，返回 assistant message。

    这一层只做“模型通信”，不做业务判断。
    这样 runtime、tool registry、tool handlers 都能保持边界清楚。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model_name,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "stream": False,
        "thinking": {"type": "disabled"},
        "max_tokens": max_completion_tokens,
        "temperature": 0.2,
    }

    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]

def build_messages(system_prompt: str, user_content: str) -> list[dict[str, str]]:
    """
    构造最简单的单轮提示消息。
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

def ask_llm_text(
    system_prompt: str,
    user_content: str,
    *,
    api_key: str | None = None,
) -> str:
    """
    请求模型返回普通文本。

    适合 demo8 这种 workflow 节点内部的“一次性调用”场景。
    """
    resolved_api_key = api_key or get_api_key()
    result = call_llm(
        api_key=resolved_api_key,
        messages=build_messages(system_prompt, user_content),
        tools=[],
    )
    return result.get("content", "")


def ask_llm_json(
    system_prompt: str,
    user_content: str,
    *,
    api_key: str | None = None,
) -> dict[str, Any]:
    """
    请求模型返回 JSON 文本并解析。

    这层封装的意义是：
    - workflow 节点只关心“我要一个 JSON 结果”
    - 不需要每个节点都重复写 parse 逻辑
    """
    text = ask_llm_text(
        system_prompt,
        user_content,
        api_key=api_key,
    ).strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"模型没有返回合法 JSON：{exc}\n原始内容：{text}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"模型返回的 JSON 不是对象：{text}")

    return data

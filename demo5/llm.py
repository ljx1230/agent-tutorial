from __future__ import annotations

import os
from typing import Any

import requests

from config import API_URL, MAX_COMPLETION_TOKENS, MODEL_NAME


def create_system_message() -> dict[str, str]:
    """定义第五课 ReAct Agent 的系统提示词。"""
    return {
        "role": "system",
        "content": (
            "你是一个更真实的 ReAct 风格 Agent。"
            "你需要结合会话记忆、当前用户目标、工具结果，决定下一步是否调用工具。"
            "如果任务还没完成，请继续调用合适工具。"
            "如果任务已经完成，请直接给出最终自然语言答复。"
            "不要假装工具已经执行成功，除非你已经看到了真实的 tool 结果。"
            "你拥有多个工具，需要根据任务自动选择最合适的工具。"
            "如果用户要求保存文件，优先使用 create_text_file。"
            "如果用户要求检查、核对、读取文件内容，优先使用 read_text_file。"
            "如果用户问当前有哪些文件，优先使用 list_files。"
            "所有文件都只能位于 demo5/generated_files 中。"
            "回答使用简洁清晰的中文。"
        ),
    }


def get_api_key() -> str:
    """读取 API Key。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )
    return api_key


def call_llm(
    api_key: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> dict[str, Any]:
    """调用 DeepSeek Chat API，返回 assistant message。"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "stream": False,
        "thinking": {"type": "disabled"},
        "max_tokens": MAX_COMPLETION_TOKENS,
        "temperature": 0.2,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]

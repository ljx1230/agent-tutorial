"""
第三课：Tool Calling Agent 示例

这个示例演示一个“会使用工具的 Agent”：
1. 使用 system prompt 约束助手身份
2. 使用多轮 messages 维护上下文
3. 使用 DeepSeek 的 tools / tool_calls 机制让模型决定是否调用工具
4. 在本地真正执行一个更有用的工具：创建文件
5. 将工具执行结果再发回模型，让模型生成最终答复

运行前请先安装依赖：
    pip install requests

并设置环境变量：
    PowerShell:
        $env:DEEPSEEK_API_KEY="你的 API Key"
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests


API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-v4-flash"
MAX_TOOL_ROUNDS = 5
MAX_COMPLETION_TOKENS = 4000

# 所有由工具创建的文件都限制在这个目录里。
# 这样既方便演示，也能避免模型把文件写到任意路径。
GENERATED_FILES_DIR = Path(__file__).resolve().parent / "generated_files"


def create_system_message() -> dict[str, Any]:
    """定义助手的系统提示词。"""
    return {
        "role": "system",
        "content": (
            "你是一个会使用工具的 Python 和 agent 助手。"
            "当用户明确要求创建文件、生成文档、输出代码文件、保存内容时，"
            "你应该优先调用工具，而不是只在聊天中口头描述结果。"
            "如果需要调用工具，请基于用户需求生成合理的文件路径和完整内容。"
            "工具调用参数必须是完整、合法的 JSON。"
            "如果内容里有换行、引号或代码块，也必须正确转义，不能输出截断的 JSON。"
            "如果用户没有要求非常详细的长文档，优先生成简洁但完整的文件内容。"
            "不要声称文件已经创建，除非工具实际返回成功。"
            "所有工具创建的文件都必须位于 demo3/generated_files 目录之下。"
            "在拿到工具结果后，再用简洁清晰的中文告诉用户执行情况。"
        ),
    }


def build_tools() -> list[dict[str, Any]]:
    """
    定义可供模型调用的工具。
    演示一个更接近真实工作的工具：创建文件。
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_text_file",
                "description": (
                    "Create a text-based file under demo3/generated_files. "
                    "Use this when the user asks to create a note, markdown file, "
                    "JSON file, Python file, config file, or any other text file."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": (
                                "Relative file path under demo3/generated_files, "
                                "for example notes/todo.md or scripts/hello.py."
                            ),
                        },
                        "content": {
                            "type": "string",
                            "description": (
                                "The complete file content to write. "
                                "Keep it complete and valid, but concise unless the user asks for a long document."
                            ),
                        },
                        "overwrite": {
                            "type": "boolean",
                            "description": (
                                "Whether to overwrite the file if it already exists."
                            ),
                        },
                    },
                    "required": ["relative_path", "content", "overwrite"],
                },
            },
        }
    ]


def resolve_safe_path(relative_path: str) -> Path:
    """
    将模型给出的相对路径解析成安全的绝对路径。

    这里做两层保护：
    1. 不允许绝对路径
    2. 不允许跳出 GENERATED_FILES_DIR
    """
    cleaned_path = relative_path.strip().replace("\\", "/")
    if not cleaned_path:
        raise ValueError("relative_path 不能为空。")

    relative = Path(cleaned_path)
    if relative.is_absolute():
        raise ValueError("relative_path 不能是绝对路径。")

    target = (GENERATED_FILES_DIR / relative).resolve()
    base_dir = GENERATED_FILES_DIR.resolve()

    if target != base_dir and base_dir not in target.parents:
        raise ValueError("不允许写入 demo3/generated_files 目录之外的路径。")

    return target


def create_text_file(relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
    """真正执行“创建文件”工具。"""
    try:
        target_path = resolve_safe_path(relative_path)
    except ValueError as exc:
        return {
            "ok": False,
            "error": str(exc),
            "relative_path": relative_path,
        }

    GENERATED_FILES_DIR.mkdir(parents=True, exist_ok=True)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    existed_before = target_path.exists()
    if existed_before and not overwrite:
        return {
            "ok": False,
            "error": "文件已存在，且 overwrite 为 False。",
            "path": str(target_path),
        }

    target_path.write_text(content, encoding="utf-8")

    return {
        "ok": True,
        "path": str(target_path),
        "created": not existed_before,
        "overwritten": existed_before,
        "characters_written": len(content),
    }


def call_llm(
    api_key: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    调用 DeepSeek Chat API，返回 assistant message。

    当模型决定调用工具时，返回结果里会包含 tool_calls。
    当模型不需要调用工具时，返回结果里通常会直接包含 content。
    """
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


def execute_tool_call(tool_call: dict[str, Any]) -> dict[str, Any]:
    """
    根据模型给出的 tool_call，在本地执行对应工具。

    DeepSeek / OpenAI 兼容格式里，函数参数通常以 JSON 字符串形式
    放在 tool_call["function"]["arguments"] 中。
    """
    function_info = tool_call.get("function", {})
    function_name = function_info.get("name")
    raw_arguments = function_info.get("arguments", "{}")

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": (
                f"工具参数不是合法 JSON：{exc}。"
                "请重新发起同一个工具调用，并返回完整、未截断的合法 JSON 参数。"
            ),
            "tool_name": function_name,
            "raw_arguments": raw_arguments,
        }

    if function_name == "create_text_file":
        try:
            return create_text_file(
                relative_path=arguments["relative_path"],
                content=arguments["content"],
                overwrite=arguments["overwrite"],
            )
        except KeyError as exc:
            return {
                "ok": False,
                "error": f"缺少必要参数：{exc}",
                "tool_name": function_name,
                "arguments": arguments,
            }

    return {
        "ok": False,
        "error": f"未知工具：{function_name}",
        "tool_name": function_name,
        "arguments": arguments,
    }


def run_agent_turn(api_key: str, messages: list[dict[str, Any]]) -> str:
    """
    执行一轮完整的 Agent 交互。

    一轮里可能发生两种情况：
    1. 模型直接返回自然语言答案
    2. 模型先请求调用工具，我们执行工具后，再把结果发回模型拿最终答案

    为了避免异常情况下无限循环，这里限制最多进行 MAX_TOOL_ROUNDS 轮工具交互。
    """
    tools = build_tools()

    for _ in range(MAX_TOOL_ROUNDS):
        assistant_message = call_llm(api_key=api_key, messages=messages, tools=tools)
        tool_calls = assistant_message.get("tool_calls") or []

        if tool_calls:
            # 先把“模型想调用什么工具”记录到对话历史里，
            # 这样下一次请求时，模型能看到自己上一步做了什么决策。
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

                print(f"\n[工具调用] {tool_name}")
                print(f"[工具参数] {raw_arguments}")

                tool_result = execute_tool_call(tool_call)
                print(f"[工具结果] {json.dumps(tool_result, ensure_ascii=False)}")

                # 以 role=tool 的消息把工具执行结果返回给模型。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

            # 有工具调用时，不立即返回，而是继续下一轮，
            # 让模型基于工具结果输出最终自然语言答复。
            continue

        final_answer = assistant_message.get("content") or "我已经完成处理，但没有生成额外文本。"
        messages.append({"role": "assistant", "content": final_answer})
        return final_answer

    raise RuntimeError(
        "工具调用轮数过多，已停止，避免无限循环。"
        "这通常说明模型连续返回了损坏或截断的工具参数。"
        "可以重试一次，或者让它生成更短一点的文件内容。"
    )


def main() -> None:
    """程序入口。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )

    messages: list[dict[str, Any]] = [create_system_message()]

    print("Tool Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我创建一个 markdown 文件，内容是一个 Agent 教程大纲。")
    print(f"工具创建的文件会保存在：{GENERATED_FILES_DIR}")

    while True:
        user_input = input("\n你：").strip()

        if not user_input:
            print("请输入内容。")
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            answer = run_agent_turn(api_key=api_key, messages=messages)
        except requests.RequestException as exc:
            print(f"\n请求失败：{exc}")
            if len(messages) > 1 and messages[-1]["role"] == "user":
                messages.pop()
            continue
        except RuntimeError as exc:
            print(f"\n执行失败：{exc}")
            continue

        print(f"\n助手：{answer}")


if __name__ == "__main__":
    # print(GENERATED_FILES_DIR)
    main()

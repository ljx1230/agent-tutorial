import json
import os
from pathlib import Path
from typing import Any

import requests


API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-v4-flash"
MAX_AGENT_STEPS = 6
MAX_COMPLETION_TOKENS = 2500
MAX_HISTORY_TURNS = 6
GENERATED_FILES_DIR = Path(__file__).resolve().parent / "generated_files"


def create_system_message() -> dict[str, str]:
    """定义系统提示词，让模型按固定动作集合分步推进。"""
    return {
        "role": "system",
        "content": (
            "你是一个分步执行任务的 Agent。"
            "你不能一次性跳过所有步骤，而是要根据当前状态决定下一步动作。"
            "你必须结合已有的会话历史理解用户偏好、默认约定和上文提到的内容。"
            "你只允许返回 JSON，不要输出 markdown，不要输出额外解释。"
            "可选动作只有四种：decide_path、draft_content、create_file、finish。"
            "动作规则如下："
            "1. 如果还没有文件路径，优先 decide_path。"
            "2. 如果还没有文件内容，优先 draft_content。"
            "3. 如果路径和内容都准备好了，但文件还没创建，使用 create_file。"
            "4. 只有在任务已经完成，或者不需要再执行动作时，才能 finish。"
            "返回 JSON 时请使用以下字段："
            "step_summary、action、relative_path、content、final_response。"
            "其中 step_summary 是简短的人类可读步骤说明，不要暴露冗长推理。"
            "relative_path 和 content 可以为 null，但在需要时必须提供完整值。"
            "如果用户没有要求超长文档，请生成简洁但完整的内容。"
            "所有待创建文件都必须位于 demo4/generated_files 目录之下。"
        ),
    }


def trim_messages(
    messages: list[dict[str, str]],
    max_turns: int,
) -> list[dict[str, str]]:
    """
    只保留最近若干轮 user / assistant 历史消息。
    """
    max_message_count = max_turns * 2
    if len(messages) > max_message_count:
        return messages[-max_message_count:]
    return messages


def create_text_file(relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
    """在安全目录中创建文本文件。"""
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


def resolve_safe_path(relative_path: str) -> Path:
    """将相对路径解析为安全的绝对路径，禁止跳出 demo4/generated_files。"""
    cleaned_path = relative_path.strip().replace("\\", "/")
    if not cleaned_path:
        raise ValueError("relative_path 不能为空。")

    relative = Path(cleaned_path)
    if relative.is_absolute():
        raise ValueError("relative_path 不能是绝对路径。")

    target = (GENERATED_FILES_DIR / relative).resolve()
    base_dir = GENERATED_FILES_DIR.resolve()

    if target != base_dir and base_dir not in target.parents:
        raise ValueError("不允许写入 demo4/generated_files 目录之外的路径。")

    return target


def build_state_message(user_goal: str, state: dict[str, Any], step_logs: list[str]) -> dict[str, str]:
    """将当前任务状态整理成一条消息，发给模型决定下一步动作。"""
    step_log_text = "\n".join(f"- {item}" for item in step_logs) if step_logs else "- 暂无"
    tool_result = state.get("tool_result")
    tool_result_text = (
        json.dumps(tool_result, ensure_ascii=False, indent=2)
        if tool_result is not None
        else "null"
    )

    content = f"""
用户目标：
{user_goal}

当前状态：
- relative_path: {state.get("relative_path")}
- has_content: {"yes" if state.get("content") else "no"}
- file_created: {state.get("file_created")}
- overwrite: {state.get("overwrite")}
- tool_result:
{tool_result_text}

之前已经执行的步骤：
{step_log_text}

请只返回一个 JSON 对象，字段如下：
{{
  "step_summary": "简短说明下一步要做什么",
  "action": "decide_path | draft_content | create_file | finish",
  "relative_path": "字符串或 null",
  "content": "字符串或 null",
  "final_response": "字符串或 null"
}}
""".strip()

    return {"role": "user", "content": content}


def call_planner(
    api_key: str,
    user_goal: str,
    messages: list[dict[str, str]],
    state: dict[str, Any],
    step_logs: list[str],
) -> dict[str, Any]:
    """调用模型，让它根据当前状态决定下一步动作。"""
    request_messages = [
        create_system_message(),
        *trim_messages(messages, MAX_HISTORY_TURNS),
        build_state_message(user_goal=user_goal, state=state, step_logs=step_logs),
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": request_messages,
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
    raw_content = result["choices"][0]["message"]["content"]
    return parse_json_response(raw_content)


def parse_json_response(raw_content: str) -> dict[str, Any]:
    """把模型返回的 JSON 文本解析成 Python 字典。"""
    text = raw_content.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"模型没有返回合法 JSON：{exc}\n原始内容：{raw_content}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"模型返回的 JSON 不是对象：{raw_content}")

    return data


def apply_model_updates(state: dict[str, Any], decision: dict[str, Any]) -> None:
    """
    把模型返回里的可选字段写回状态。

    例如模型在 draft_content 阶段，可能顺便也给出一个更合适的 relative_path。
    """
    relative_path = decision.get("relative_path")
    if isinstance(relative_path, str) and relative_path.strip():
        state["relative_path"] = relative_path.strip()

    content = decision.get("content")
    if isinstance(content, str) and content.strip():
        state["content"] = content


def run_task_agent(
    api_key: str,
    user_goal: str,
    messages: list[dict[str, str]],
) -> str:
    """执行一轮完整的多步任务。"""
    state: dict[str, Any] = {
        "relative_path": None,
        "content": None,
        "file_created": False,
        "overwrite": True,
        "tool_result": None,
    }
    step_logs: list[str] = []

    for step_number in range(1, MAX_AGENT_STEPS + 1):
        decision = call_planner(
            api_key=api_key,
            user_goal=user_goal,
            messages=messages,
            state=state,
            step_logs=step_logs,
        )

        action = decision.get("action")
        step_summary = decision.get("step_summary") or "模型没有提供步骤说明。"

        print(f"\n[步骤 {step_number}] {action}")
        print(f"[步骤说明] {step_summary}")

        apply_model_updates(state, decision)

        if action == "decide_path":
            relative_path = state.get("relative_path")
            if not relative_path:
                raise RuntimeError("模型选择了 decide_path，但没有提供 relative_path。")
            step_logs.append(f"已确定文件路径：{relative_path}")
            continue

        if action == "draft_content":
            content = state.get("content")
            if not content:
                raise RuntimeError("模型选择了 draft_content，但没有提供 content。")
            step_logs.append(f"已生成文件内容草稿，长度约 {len(content)} 个字符。")
            continue

        if action == "create_file":
            relative_path = state.get("relative_path")
            content = state.get("content")
            if not relative_path:
                raise RuntimeError("模型选择了 create_file，但还没有 relative_path。")
            if not content:
                raise RuntimeError("模型选择了 create_file，但还没有 content。")

            tool_result = create_text_file(
                relative_path=relative_path,
                content=content,
                overwrite=state["overwrite"],
            )
            state["tool_result"] = tool_result
            state["file_created"] = bool(tool_result.get("ok"))

            print(f"[工具结果] {json.dumps(tool_result, ensure_ascii=False)}")

            if tool_result.get("ok"):
                step_logs.append(f"已创建文件：{tool_result['path']}")
            else:
                step_logs.append(f"创建文件失败：{tool_result.get('error')}")
            continue

        if action == "finish":
            final_response = decision.get("final_response")
            if not isinstance(final_response, str) or not final_response.strip():
                if state.get("file_created") and state.get("tool_result"):
                    final_response = f"任务已完成，文件已创建：{state['tool_result']['path']}"
                else:
                    final_response = "任务已结束。"
            return final_response

        raise RuntimeError(f"模型返回了未知动作：{action}")

    raise RuntimeError("超过最大步骤数，任务仍未完成。可以让任务描述更具体一些再重试。")


def main() -> None:
    """程序入口。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )

    print("Planning Demo 已启动。输入 exit 或 quit 结束。")
    print("你可以试试：帮我生成一份 Python 学习计划，并保存成 markdown 文件。")
    print(f"生成的文件会保存在：{GENERATED_FILES_DIR}")
    print(f"当前会保留最近 {MAX_HISTORY_TURNS} 轮会话记忆。")

    # messages 继承第二课的思路：
    # - user / assistant 消息会被持续保存
    # - 后续任务会带着这些上下文一起交给模型
    messages: list[dict[str, str]] = []

    while True:
        user_goal = input("\n你：").strip()

        if not user_goal:
            print("请输入任务目标。")
            continue

        if user_goal.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        messages.append({"role": "user", "content": user_goal})
        messages = trim_messages(
            messages,
            MAX_HISTORY_TURNS,
        )

        try:
            final_answer = run_task_agent(
                api_key=api_key,
                user_goal=user_goal,
                messages=messages,
            )
        except requests.RequestException as exc:
            print(f"\n请求失败：{exc}")
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            continue
        except (RuntimeError, ValueError) as exc:
            print(f"\n执行失败：{exc}")
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            continue

        messages.append({"role": "assistant", "content": final_answer})
        messages = trim_messages(
            messages,
            MAX_HISTORY_TURNS,
        )

        print(f"\n助手：{final_answer}")


if __name__ == "__main__":
    main()

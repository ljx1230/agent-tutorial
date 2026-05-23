from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import GENERATED_FILES_DIR


def build_tools() -> list[dict[str, Any]]:
    """定义本节课可供模型自动选择的工具集合。"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_text_file",
                "description": (
                    "Create a text file under demo5/generated_files. "
                    "Use this when the user wants to save notes, outlines, plans, markdown, or code."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "Relative file path under demo5/generated_files.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Complete file content to write.",
                        },
                        "overwrite": {
                            "type": "boolean",
                            "description": "Whether to overwrite the file if it already exists.",
                        },
                    },
                    "required": ["relative_path", "content", "overwrite"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_text_file",
                "description": (
                    "Read a text file under demo5/generated_files. "
                    "Use this when the user asks to inspect, verify, or review file content."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "Relative file path under demo5/generated_files.",
                        }
                    },
                    "required": ["relative_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": (
                    "List files under demo5/generated_files. "
                    "Use this when the user asks what files exist or wants to inspect the directory."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_dir": {
                            "type": "string",
                            "description": "Relative directory under demo5/generated_files. Use '.' for the root.",
                        }
                    },
                    "required": ["relative_dir"],
                },
            },
        },
    ]


def resolve_safe_path(relative_path: str) -> Path:
    """把模型给出的相对路径解析成 demo5/generated_files 里的安全路径。"""
    cleaned_path = relative_path.strip().replace("\\", "/")
    if not cleaned_path:
        raise ValueError("relative_path 不能为空。")

    relative = Path(cleaned_path)
    if relative.is_absolute():
        raise ValueError("relative_path 不能是绝对路径。")

    target = (GENERATED_FILES_DIR / relative).resolve()
    base_dir = GENERATED_FILES_DIR.resolve()

    if target != base_dir and base_dir not in target.parents:
        raise ValueError("不允许访问 demo5/generated_files 目录之外的路径。")

    return target


def create_text_file(relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
    """创建文本文件。"""
    try:
        target_path = resolve_safe_path(relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_path": relative_path}

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


def read_text_file(relative_path: str) -> dict[str, Any]:
    """读取文本文件。"""
    try:
        target_path = resolve_safe_path(relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_path": relative_path}

    if not target_path.exists():
        return {
            "ok": False,
            "error": "文件不存在。",
            "path": str(target_path),
        }

    content = target_path.read_text(encoding="utf-8")
    return {
        "ok": True,
        "path": str(target_path),
        "content": content,
        "characters_read": len(content),
    }


def list_files(relative_dir: str) -> dict[str, Any]:
    """列出目录中的文件。"""
    try:
        target_dir = resolve_safe_path(relative_dir if relative_dir != "." else "")
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_dir": relative_dir}

    if not target_dir.exists():
        return {
            "ok": False,
            "error": "目录不存在。",
            "path": str(target_dir),
        }

    if not target_dir.is_dir():
        return {
            "ok": False,
            "error": "目标路径不是目录。",
            "path": str(target_dir),
        }

    items = []
    for item in sorted(target_dir.iterdir(), key=lambda p: p.name.lower()):
        items.append(
            {
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
            }
        )

    return {
        "ok": True,
        "path": str(target_dir),
        "items": items,
    }


def execute_tool_call(tool_call: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    执行模型返回的单个 tool_call。

    返回：
    - tool_name
    - tool_result
    """
    function_info = tool_call.get("function", {})
    tool_name = function_info.get("name", "unknown_tool")
    raw_arguments = function_info.get("arguments", "{}")

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        return tool_name, {
            "ok": False,
            "error": f"工具参数不是合法 JSON：{exc}",
            "raw_arguments": raw_arguments,
        }

    if tool_name == "create_text_file":
        return tool_name, create_text_file(
            relative_path=arguments["relative_path"],
            content=arguments["content"],
            overwrite=arguments["overwrite"],
        )

    if tool_name == "read_text_file":
        return tool_name, read_text_file(relative_path=arguments["relative_path"])

    if tool_name == "list_files":
        return tool_name, list_files(relative_dir=arguments["relative_dir"])

    return tool_name, {
        "ok": False,
        "error": f"未知工具：{tool_name}",
        "arguments": arguments,
    }

from __future__ import annotations

from pathlib import Path
from typing import Any

from demo6.framework import ToolRegistry, tool

from demo6.config import GENERATED_FILES_DIR


def resolve_safe_path(relative_path: str) -> Path:
    """
    将相对路径解析为 demo6/generated_files 里的安全路径。

    这里统一把工具的写入范围限制在 demo6/generated_files，
    这样示例更安全，也更容易讲清楚“工具权限边界”。
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
        raise ValueError("不允许访问 demo6/generated_files 目录之外的路径。")

    return target


def resolve_safe_dir(relative_dir: str) -> Path:
    """解析目录路径，'.' 表示生成文件根目录。"""
    if relative_dir.strip() in {"", "."}:
        return GENERATED_FILES_DIR.resolve()
    return resolve_safe_path(relative_dir)


@tool(
    description=(
        "Create a text file under demo6/generated_files. "
        "Use this when the user wants to save notes, outlines, plans, markdown, or code."
    ),
    parameter_descriptions={
        "relative_path": "Relative file path under demo6/generated_files, such as notes/plan.md.",
        "content": "Complete file content to write.",
        "overwrite": "Whether to overwrite the file if it already exists.",
    },
)
def create_text_file(relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
    """
    创建文本文件。

    这个工具除了返回成功与否，还会返回 context_updates。
    runtime 看到这些字段后，会自动把它们写进 shared_context。
    """
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
        "context_updates": {
            "last_created_relative_path": relative_path,
        },
    }


@tool(
    description=(
        "Read a text file under demo6/generated_files. "
        "Use this when the user asks to inspect, verify, or review file content."
    ),
    parameter_descriptions={
        "relative_path": "Relative file path under demo6/generated_files.",
    },
)
def read_text_file(relative_path: str) -> dict[str, Any]:
    """
    读取文本文件。

    这个工具会把最近读取的相对路径回写给 runtime，
    方便模型在后续步骤里继续引用。
    """
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
        "context_updates": {
            "last_read_relative_path": relative_path,
        },
    }


@tool(
    description=(
        "List files under demo6/generated_files. "
        "Use this when the user asks what files exist or wants to inspect the directory."
    ),
    parameter_descriptions={
        "relative_dir": "Relative directory under demo6/generated_files. Use '.' for the root.",
    },
)
def list_files(relative_dir: str) -> dict[str, Any]:
    """列出目录中的文件。"""
    try:
        target_dir = resolve_safe_dir(relative_dir)
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


def register_builtin_file_tools(registry: ToolRegistry) -> None:
    """
    注册第六课示例中用到的内置文件工具。

    这里使用 register_many(...)，
    表达的是“这一组工具一起构成了 demo6 的默认工具集”。
    """
    registry.register_many(
        create_text_file,
        read_text_file,
        list_files,
    )

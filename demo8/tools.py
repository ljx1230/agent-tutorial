from __future__ import annotations

from pathlib import Path
from typing import Any

from demo6.framework import ToolRegistry, tool


def _normalize_workspace_path(workspace_dir: Path, candidate_path: str) -> Path:
    """
    把路径统一归一化到工作区内部。

    兼容两种输入：
    - 相对路径：utils.py
    - 绝对路径：D:/.../project_workspace/utils.py

    如果是工作区内的绝对路径，会自动转成相对路径再继续处理。
    """
    cleaned_path = candidate_path.strip().replace("\\", "/")
    if not cleaned_path:
        raise ValueError("relative_path 不能为空。")

    base_dir = workspace_dir.resolve()
    candidate = Path(cleaned_path)

    if candidate.is_absolute():
        resolved = candidate.resolve()
        if resolved == base_dir:
            return resolved
        if base_dir in resolved.parents:
            return resolved
        raise ValueError("不允许访问工作区之外的路径。")

    target = (base_dir / candidate).resolve()
    if target != base_dir and base_dir not in target.parents:
        raise ValueError("不允许访问工作区之外的路径。")
    return target


def resolve_safe_path(workspace_dir: Path, relative_path: str) -> Path:
    """
    将相对路径解析到 workspace_dir 下，并禁止跳出工作区。

    第八课的工具仍然强调一个原则：
    workflow 可以编排很多步骤，但每个工具的作用边界必须清晰。
    """
    return _normalize_workspace_path(workspace_dir, relative_path)


@tool(
    description="List files under the workspace.",
    parameter_descriptions={
        "workspace_dir": "Absolute workspace directory path.",
        "relative_dir": "Relative directory under the workspace, use '.' for the root.",
    },
)
def list_files(workspace_dir: str, relative_dir: str = ".") -> dict[str, Any]:
    """列出工作区中的文件。"""
    base_dir = Path(workspace_dir)
    target_dir = (
        base_dir.resolve()
        if relative_dir.strip() in {"", "."}
        else _normalize_workspace_path(base_dir, relative_dir)
    )

    if not target_dir.exists():
        return {"ok": False, "error": "目录不存在。", "path": str(target_dir)}
    if not target_dir.is_dir():
        return {"ok": False, "error": "目标路径不是目录。", "path": str(target_dir)}

    items = []
    for item in sorted(target_dir.iterdir(), key=lambda p: p.name.lower()):
        items.append(
            {
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "relative_path": str(item.relative_to(base_dir)).replace("\\", "/"),
            }
        )

    return {"ok": True, "path": str(target_dir), "items": items}


@tool(
    description="Search text in files under the workspace.",
    parameter_descriptions={
        "workspace_dir": "Absolute workspace directory path.",
        "query": "Text to search for.",
        "relative_dir": "Relative directory under the workspace, use '.' for the root.",
    },
)
def search_text(workspace_dir: str, query: str, relative_dir: str = ".") -> dict[str, Any]:
    """在工作区中搜索文本。"""
    base_dir = Path(workspace_dir)
    target_dir = (
        base_dir.resolve()
        if relative_dir.strip() in {"", "."}
        else _normalize_workspace_path(base_dir, relative_dir)
    )

    if not target_dir.exists() or not target_dir.is_dir():
        return {"ok": False, "error": "搜索目录不存在或不是目录。", "path": str(target_dir)}

    matches: list[dict[str, Any]] = []
    for path in sorted(target_dir.rglob("*"), key=lambda p: str(p).lower()):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            if query in line:
                matches.append(
                    {
                        "relative_path": str(path.relative_to(base_dir)).replace("\\", "/"),
                        "line_number": line_number,
                        "line": line,
                    }
                )

    return {"ok": True, "query": query, "match_count": len(matches), "matches": matches}


@tool(
    description="Read a text file under the workspace.",
    parameter_descriptions={
        "workspace_dir": "Absolute workspace directory path.",
        "relative_path": "Relative file path under the workspace.",
    },
)
def read_text_file(workspace_dir: str, relative_path: str) -> dict[str, Any]:
    """读取工作区中的文本文件。"""
    base_dir = Path(workspace_dir)
    target_path = _normalize_workspace_path(base_dir, relative_path)
    if not target_path.exists():
        return {"ok": False, "error": "文件不存在。", "path": str(target_path)}

    content = target_path.read_text(encoding="utf-8")
    return {
        "ok": True,
        "path": str(target_path),
        "content": content,
        "characters_read": len(content),
    }


@tool(
    description="Replace exact text in a file under the workspace.",
    parameter_descriptions={
        "workspace_dir": "Absolute workspace directory path.",
        "relative_path": "Relative file path under the workspace.",
        "old_text": "Exact old text to replace.",
        "new_text": "Exact new text to write.",
        "expected_occurrences": "Expected number of occurrences for safety.",
    },
)
def replace_text_in_file(
    workspace_dir: str,
    relative_path: str,
    old_text: str,
    new_text: str,
    expected_occurrences: int,
) -> dict[str, Any]:
    """精确替换文件中的文本。"""
    base_dir = Path(workspace_dir)
    target_path = _normalize_workspace_path(base_dir, relative_path)
    if not target_path.exists():
        return {"ok": False, "error": "文件不存在。", "path": str(target_path)}

    original = target_path.read_text(encoding="utf-8")
    occurrences = original.count(old_text)
    if occurrences != expected_occurrences:
        return {
            "ok": False,
            "error": (
                f"目标文本出现次数不符合预期：expected_occurrences={expected_occurrences}, "
                f"actual_occurrences={occurrences}"
            ),
            "path": str(target_path),
        }

    updated = original.replace(old_text, new_text)
    target_path.write_text(updated, encoding="utf-8")

    return {"ok": True, "path": str(target_path), "replaced_occurrences": occurrences}


@tool(
    description="Write a complete file under the workspace.",
    parameter_descriptions={
        "workspace_dir": "Absolute workspace directory path.",
        "relative_path": "Relative file path under the workspace.",
        "content": "Complete file content to write.",
        "overwrite": "Whether to overwrite an existing file.",
    },
)
def write_text_file(
    workspace_dir: str,
    relative_path: str,
    content: str,
    overwrite: bool,
) -> dict[str, Any]:
    """写入完整文件内容。"""
    base_dir = Path(workspace_dir)
    target_path = _normalize_workspace_path(base_dir, relative_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    existed_before = target_path.exists()
    if existed_before and not overwrite:
        return {"ok": False, "error": "文件已存在，且 overwrite 为 False。", "path": str(target_path)}

    target_path.write_text(content, encoding="utf-8")
    return {
        "ok": True,
        "path": str(target_path),
        "created": not existed_before,
        "overwritten": existed_before,
        "characters_written": len(content),
    }


def register_workflow_tools(registry: ToolRegistry) -> None:
    """把 workflow 这组工具一次性注册进去。"""
    registry.register_many(
        list_files,
        search_text,
        read_text_file,
        replace_text_in_file,
        write_text_file,
    )

from __future__ import annotations

from pathlib import Path
from typing import Any

from demo6.framework import ToolRegistry, tool

from demo7.config import WORKSPACE_DIR


def resolve_safe_path(relative_path: str) -> Path:
    """
    将相对路径解析为 demo7/project_workspace 下的安全路径。

    第七课把 coding agent 的作用范围严格限制在 project_workspace，
    这样既安全，也方便我们控制演示样例。
    """
    cleaned_path = relative_path.strip().replace("\\", "/")
    if not cleaned_path:
        raise ValueError("relative_path 不能为空。")

    relative = Path(cleaned_path)
    if relative.is_absolute():
        raise ValueError("relative_path 不能是绝对路径。")

    target = (WORKSPACE_DIR / relative).resolve()
    base_dir = WORKSPACE_DIR.resolve()

    if target != base_dir and base_dir not in target.parents:
        raise ValueError("不允许访问 project_workspace 目录之外的路径。")

    return target


def resolve_safe_dir(relative_dir: str) -> Path:
    """解析目录路径，'.' 表示工作区根目录。"""
    if relative_dir.strip() in {"", "."}:
        return WORKSPACE_DIR.resolve()
    return resolve_safe_path(relative_dir)


@tool(
    description="List files under demo7/project_workspace. Use '.' for the workspace root.",
    parameter_descriptions={
        "relative_dir": "Relative directory under the workspace.",
    },
)
def list_files(relative_dir: str) -> dict[str, Any]:
    """列出工作区目录中的文件。"""
    try:
        target_dir = resolve_safe_dir(relative_dir)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_dir": relative_dir}

    if not target_dir.exists():
        return {"ok": False, "error": "目录不存在。", "path": str(target_dir)}
    if not target_dir.is_dir():
        return {"ok": False, "error": "目标路径不是目录。", "path": str(target_dir)}

    items = []
    for item in sorted(target_dir.iterdir(), key=lambda p: p.name.lower()):
        items.append({"name": item.name, "type": "dir" if item.is_dir() else "file"})

    return {
        "ok": True,
        "path": str(target_dir),
        "items": items,
    }


@tool(
    description="Read a text file under demo7/project_workspace.",
    parameter_descriptions={
        "relative_path": "Relative file path under the workspace.",
    },
)
def read_text_file(relative_path: str) -> dict[str, Any]:
    """
    读取工作区中的文本文件。

    coding agent 做代码修改前，通常先要读文件。
    所以这是第七课里最常用的观察型工具之一。
    """
    try:
        target_path = resolve_safe_path(relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_path": relative_path}

    if not target_path.exists():
        return {"ok": False, "error": "文件不存在。", "path": str(target_path)}

    content = target_path.read_text(encoding="utf-8")
    return {
        "ok": True,
        "path": str(target_path),
        "content": content,
        "characters_read": len(content),
        "context_updates": {"last_read_relative_path": relative_path},
    }


@tool(
    description="Search text in files under demo7/project_workspace.",
    parameter_descriptions={
        "query": "Text to search for.",
        "relative_dir": "Relative directory under the workspace.",
    },
)
def search_text(query: str, relative_dir: str) -> dict[str, Any]:
    """
    在工作区中搜索文本。

    这个工具对应的是最常见的 coding agent 行为之一：
    先缩小范围，再去读具体文件。
    """
    try:
        target_dir = resolve_safe_dir(relative_dir)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_dir": relative_dir}

    if not target_dir.exists() or not target_dir.is_dir():
        return {"ok": False, "error": "搜索目录不存在或不是目录。", "path": str(target_dir)}

    matches = []
    for path in sorted(target_dir.rglob("*"), key=lambda p: str(p).lower()):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if query in line:
                matches.append(
                    {
                        "relative_path": str(path.relative_to(WORKSPACE_DIR)).replace("\\", "/"),
                        "line_number": line_number,
                        "line": line,
                    }
                )

    return {
        "ok": True,
        "query": query,
        "matches": matches,
        "match_count": len(matches),
        "context_updates": {"last_search_query": query},
    }


@tool(
    description="Search files by name under demo7/project_workspace.",
    parameter_descriptions={
        "name_query": "Filename or partial filename to search.",
        "relative_dir": "Relative directory under the workspace.",
    },
)
def search_files_by_name(name_query: str, relative_dir: str) -> dict[str, Any]:
    """按文件名搜索工作区中的文件。"""
    try:
        target_dir = resolve_safe_dir(relative_dir)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_dir": relative_dir}

    if not target_dir.exists() or not target_dir.is_dir():
        return {"ok": False, "error": "搜索目录不存在或不是目录。", "path": str(target_dir)}

    normalized_query = name_query.lower()
    matches = []
    for path in sorted(target_dir.rglob("*"), key=lambda p: str(p).lower()):
        if path.is_file() and normalized_query in path.name.lower():
            matches.append(str(path.relative_to(WORKSPACE_DIR)).replace("\\", "/"))

    return {
        "ok": True,
        "name_query": name_query,
        "matches": matches,
        "match_count": len(matches),
        "context_updates": {"last_file_search_query": name_query},
    }


@tool(
    description=(
        "Replace exact text inside a file under demo7/project_workspace. "
        "Use this for small, precise code edits after reading the file."
    ),
    parameter_descriptions={
        "relative_path": "Relative file path under the workspace.",
        "old_text": "Exact old text to replace.",
        "new_text": "Exact new text to write.",
        "expected_occurrences": "Expected number of occurrences for safety.",
    },
)
def replace_text_in_file(
    relative_path: str,
    old_text: str,
    new_text: str,
    expected_occurrences: int,
) -> dict[str, Any]:
    """
    对文件做精确字符串替换。

    这是第七课里最重要的“修改型工具”。
    它要求模型给出：
    - 要改哪个文件
    - 旧文本是什么
    - 新文本是什么
    - 预期替换次数是多少

    `expected_occurrences` 的作用是做最基础的安全保护，
    避免模型误替换了太多地方。
    """
    try:
        target_path = resolve_safe_path(relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_path": relative_path}

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

    return {
        "ok": True,
        "path": str(target_path),
        "replaced_occurrences": occurrences,
        "context_updates": {"last_modified_relative_path": relative_path},
    }


@tool(
    description="Write a complete file under demo7/project_workspace.",
    parameter_descriptions={
        "relative_path": "Relative file path under the workspace.",
        "content": "Complete file content to write.",
        "overwrite": "Whether to overwrite an existing file.",
    },
)
def write_text_file(relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
    """
    在工作区写入完整文件内容。

    这个工具比 replace_text_in_file 更重，
    一般留给“需要重写完整文件”或“创建新文件”的情况。
    """
    try:
        target_path = resolve_safe_path(relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc), "relative_path": relative_path}

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
        "context_updates": {"last_modified_relative_path": relative_path},
    }


def register_coding_tools(registry: ToolRegistry) -> None:
    """
    注册 coding agent 使用的工具。

    这里故意把工具分成两类：
    - 观察型工具：list / search / read
    - 修改型工具：replace / write

    这样第七课在讲“coding agent 的工作流”时会更清楚：
    先观察，再修改。
    """
    registry.register_many(
        list_files,
        read_text_file,
        search_text,
        search_files_by_name,
        replace_text_in_file,
        write_text_file,
    )

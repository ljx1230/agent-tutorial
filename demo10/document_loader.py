from __future__ import annotations

import hashlib
from dataclasses import dataclass

from demo10.config import CHUNK_OVERLAP, CHUNK_SIZE, KNOWLEDGE_BASE_DIR


@dataclass
class DocumentChunk:
    """写入向量数据库的最小文档单元。"""

    chunk_id: str
    source: str
    chunk_index: int
    content: str


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    把长文档切成多个 chunk。

    chunk 太大：检索不精准，模型上下文也浪费。
    chunk 太小：语义容易断裂，答案缺少上下文。
    overlap 的作用是让相邻 chunk 之间保留一点上下文衔接。
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end].strip())

        if end == len(cleaned):
            break

        start = max(0, end - overlap)

    return [chunk for chunk in chunks if chunk]


def load_knowledge_base() -> list[DocumentChunk]:
    """读取 knowledge_base 目录下的 Markdown 文件并切分成 chunks。"""
    chunks: list[DocumentChunk] = []

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        for index, content in enumerate(split_text(text)):
            digest = hashlib.md5(f"{path.name}:{index}:{content}".encode("utf-8")).hexdigest()
            chunks.append(
                DocumentChunk(
                    chunk_id=digest,
                    source=path.name,
                    chunk_index=index,
                    content=content,
                )
            )

    return chunks

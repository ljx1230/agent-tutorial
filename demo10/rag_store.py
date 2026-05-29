from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg import sql

from demo10.config import (
    EMBEDDING_DIMENSION,
    PGVECTOR_DATABASE,
    PGVECTOR_HOST,
    PGVECTOR_PASSWORD,
    PGVECTOR_PORT,
    PGVECTOR_USER,
    TABLE_NAME,
    TOP_K,
)
from demo10.document_loader import load_knowledge_base
from demo10.embeddings import embed_query, embed_texts


@dataclass
class RetrievedChunk:
    """从 pgvector 检索回来的上下文片段。"""

    source: str
    chunk_index: int
    content: str
    distance: float


def require_database_password() -> str:
    if not PGVECTOR_PASSWORD:
        raise RuntimeError(
            "缺少环境变量 PGVECTOR_PASSWORD。请先在 PowerShell 中执行："
            ' $env:PGVECTOR_PASSWORD="你的数据库密码"'
        )
    return PGVECTOR_PASSWORD


def connect() -> psycopg.Connection[Any]:
    """连接阿里云 PostgreSQL。"""
    return psycopg.connect(
        host=PGVECTOR_HOST,
        port=PGVECTOR_PORT,
        dbname=PGVECTOR_DATABASE,
        user=PGVECTOR_USER,
        password=require_database_password(),
        connect_timeout=10,
    )


def vector_literal(embedding: list[float]) -> str:
    """
    把 Python list 转成 pgvector 可识别的文本格式。

    pgvector 的向量字面量长这样：[0.1,0.2,0.3]
    这里不拼 SQL 结构，只把它作为参数传给 psycopg，再在 SQL 里显式转换为 vector。
    """
    return "[" + ",".join(str(value) for value in embedding) + "]"


def setup_database() -> None:
    """
    初始化 pgvector 扩展和数据表。

    注意：CREATE EXTENSION vector 需要数据库已经安装 pgvector 扩展。
    阿里云 RDS PostgreSQL 如果没有开启 pgvector，需要先在控制台或数据库侧启用。
    """
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id TEXT PRIMARY KEY,
                        source TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        embedding vector({dimension}) NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT now()
                    )
                    """
                ).format(
                    table_name=sql.Identifier(TABLE_NAME),
                    dimension=sql.SQL(str(EMBEDDING_DIMENSION)),
                )
            )

    # 向量索引是性能优化，不是 RAG 流程成立的前提。
    # 部分云数据库 pgvector 版本可能不支持 hnsw，因此这里失败只提示，不中断 demo。
    with connect() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    sql.SQL(
                        "CREATE INDEX IF NOT EXISTS {index_name} "
                        "ON {table_name} USING hnsw (embedding vector_cosine_ops)"
                    ).format(
                        index_name=sql.Identifier(f"{TABLE_NAME}_embedding_hnsw_idx"),
                        table_name=sql.Identifier(TABLE_NAME),
                    )
                )
            except Exception as exc:
                conn.rollback()
                print(f"提示：向量索引创建失败，将使用顺序扫描完成 demo。原因：{exc}", flush=True)


def rebuild_index() -> dict[str, int]:
    """
    重建 RAG 索引。

    教学 demo 为了让流程清晰，每次启动都清空并重新写入知识库。
    真实项目一般会做增量更新，而不是每次重建。
    """
    print("[1/5] 初始化 pgvector 数据表...", flush=True)
    setup_database()

    print("[2/5] 读取并切分 knowledge_base 文档...", flush=True)
    chunks = load_knowledge_base()
    if not chunks:
        raise RuntimeError("knowledge_base 目录下没有可索引的 Markdown 文档。")

    print(f"[3/5] 调用智谱 embedding-3：chunks={len(chunks)}...", flush=True)
    embeddings = embed_texts([chunk.content for chunk in chunks])

    print("[4/5] 清空旧索引...", flush=True)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("TRUNCATE TABLE {table_name}").format(table_name=sql.Identifier(TABLE_NAME)))

    print("[5/5] 写入 pgvector...", flush=True)
    with connect() as conn:
        with conn.cursor() as cur:
            for chunk, embedding in zip(chunks, embeddings):
                cur.execute(
                    sql.SQL(
                        """
                        INSERT INTO {table_name} (id, source, chunk_index, content, embedding)
                        VALUES (%s, %s, %s, %s, %s::vector)
                        ON CONFLICT (id) DO UPDATE SET
                            source = EXCLUDED.source,
                            chunk_index = EXCLUDED.chunk_index,
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding
                        """
                    ).format(table_name=sql.Identifier(TABLE_NAME)),
                    [
                        chunk.chunk_id,
                        chunk.source,
                        chunk.chunk_index,
                        chunk.content,
                        vector_literal(embedding),
                    ],
                )

    return {"documents": len({chunk.source for chunk in chunks}), "chunks": len(chunks)}


def retrieve(query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    """把用户问题转成向量，然后用 pgvector 做相似度检索。"""
    query_embedding = embed_query(query)

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    """
                    SELECT
                        source,
                        chunk_index,
                        content,
                        embedding <=> %s::vector AS distance
                    FROM {table_name}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """
                ).format(table_name=sql.Identifier(TABLE_NAME)),
                [vector_literal(query_embedding), vector_literal(query_embedding), top_k],
            )

            rows = cur.fetchall()

    return [
        RetrievedChunk(
            source=row[0],
            chunk_index=row[1],
            content=row[2],
            distance=float(row[3]),
        )
        for row in rows
    ]

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

PGVECTOR_PORT = 5432
PGVECTOR_DATABASE = "agent_demo"
PGVECTOR_USER = "ljx"
PGVECTOR_HOST = os.getenv("PGVECTOR_HOST") # 公网访问地址
PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD") # 用户密码

EMBEDDING_MODEL = "embedding-3"
EMBEDDING_DIMENSION = 2048

TABLE_NAME = "rag_chunks"
TOP_K = 4
CHUNK_SIZE = 700
CHUNK_OVERLAP = 120

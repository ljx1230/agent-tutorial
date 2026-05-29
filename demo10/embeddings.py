from __future__ import annotations

import os

from zai import ZhipuAiClient

from demo10.config import EMBEDDING_MODEL


def get_zhipu_api_key() -> str:
    """读取智谱 API Key。"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 ZHIPU_API_KEY。请先在 PowerShell 中执行："
            ' $env:ZHIPU_API_KEY="你的智谱 API Key"'
        )
    return api_key


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    使用智谱 embedding-3 把文本转成向量。

    RAG 里最关键的一步就是把人类可读的文本转换成机器可检索的向量。
    """
    if not texts:
        return []

    client = ZhipuAiClient(api_key=get_zhipu_api_key())
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    # SDK 返回的 data 顺序和 input 顺序一致，因此可以直接按 index 排序取出。
    items = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in items]


def embed_query(query: str) -> list[float]:
    """查询文本也要使用同一个 embedding 模型，否则向量空间不一致。"""
    return embed_texts([query])[0]

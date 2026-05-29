from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from demo6.framework import ask_llm_text, get_api_key

from demo10.rag_store import rebuild_index, retrieve


def build_context_text(chunks: list) -> str:
    """把检索结果整理成适合塞进 prompt 的上下文文本。"""
    if not chunks:
        return "没有检索到相关资料。"

    parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        parts.append(
            "\n".join(
                [
                    f"[资料 {index}]",
                    f"来源：{chunk.source}，chunk_index={chunk.chunk_index}，distance={chunk.distance:.4f}",
                    chunk.content,
                ]
            )
        )

    return "\n\n".join(parts)


def answer_with_rag(question: str) -> str:
    """先检索，再把检索结果交给大模型生成答案。"""
    chunks = retrieve(question)
    context_text = build_context_text(chunks)

    system_prompt = (
        "你是一个 RAG 教程助手。"
        "回答问题时必须优先依据提供的资料。"
        "如果资料里没有答案，要明确说资料不足，不要编造。"
        "回答使用简洁清晰的中文。"
    )
    user_content = f"用户问题：{question}\n\n可参考资料：\n{context_text}"

    return ask_llm_text(system_prompt, user_content)


def main() -> None:
    print("RAG Demo 已启动。正在使用 智谱 embedding-3 + 阿里云 PostgreSQL pgvector 构建索引...")

    # 提前检查 DeepSeek Key，让错误尽早暴露。
    _ = get_api_key()

    try:
        result = rebuild_index()
    except Exception as exc:
        print(f"索引构建失败：{exc}")
        return

    print(f"索引构建完成：documents={result['documents']}，chunks={result['chunks']}")
    print("输入 exit 或 quit 结束。")
    print("你可以试试：ReAct Agent 和普通聊天机器人有什么区别？")

    while True:
        question = input("\n你：").strip()
        if question.lower() in {"exit", "quit"}:
            print("已结束。")
            break

        if not question:
            continue

        try:
            answer = answer_with_rag(question)
        except Exception as exc:
            print(f"回答失败：{exc}")
            continue

        print(f"\n助手：{answer}")


if __name__ == "__main__":
    main()

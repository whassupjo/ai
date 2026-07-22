from collections.abc import Iterator

from app.services.llm_client import LLMClient
from app.services.vector_store import VectorStore


SYSTEM_PROMPT = """你是企业内部知识库问答助手。
只能基于给定知识片段回答问题；如果片段不足，请明确说明无法确认。
回答要清晰、简洁，并尽量按步骤输出。"""


class RAGAgent:
    def __init__(self) -> None:
        self.store = VectorStore()
        self.llm = LLMClient()

    def answer(self, question: str, role: str, top_k: int = 4) -> dict[str, object]:
        hits = self.retrieve(question=question, role=role, top_k=top_k)
        prompt = self.build_prompt(question=question, role=role, hits=hits)
        answer = self.llm.complete(SYSTEM_PROMPT, prompt)
        return {
            "question": question,
            "role": role,
            "answer": answer,
            "sources": self.format_sources(hits),
        }

    def stream_answer(self, question: str, role: str, top_k: int = 4) -> Iterator[str]:
        hits = self.retrieve(question=question, role=role, top_k=top_k)
        prompt = self.build_prompt(question=question, role=role, hits=hits)
        yield from self.llm.stream_complete(SYSTEM_PROMPT, prompt)

    def retrieve(self, question: str, role: str, top_k: int = 4) -> list[dict[str, object]]:
        return self.store.search(query=question, role=role, top_k=top_k)

    def build_prompt(self, question: str, role: str, hits: list[dict[str, object]]) -> str:
        context = "\n\n".join(
            f"[来源: {hit['filename']}#{hit['chunk_index']} score={hit['score']}]\n{hit['text']}"
            for hit in hits
        )
        return f"""
用户角色：{role}
用户问题：{question}

检索到的企业知识片段：
{context or "无"}

请输出：
1. 直接答案
2. 依据来源
3. 如果信息不足，说明还需要补充哪类文档
"""

    @staticmethod
    def format_sources(hits: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {
                "filename": hit["filename"],
                "chunk_index": hit["chunk_index"],
                "score": hit["score"],
                "access_role": hit["access_role"],
                "preview": str(hit["text"])[:160],
            }
            for hit in hits
        ]

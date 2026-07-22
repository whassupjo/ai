from collections.abc import Iterator

from openai import OpenAI

from app.core.config import settings


class LLMClient:
    def __init__(self) -> None:
        self._client: OpenAI | None = None
        if settings.dashscope_api_key:
            self._client = OpenAI(
                api_key=settings.dashscope_api_key,
                base_url=settings.qwen_base_url,
            )

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            if settings.enable_mock_llm:
                return self._mock_response(user_prompt)
            raise RuntimeError("DASHSCOPE_API_KEY is not configured.")

        response = self._client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""

    def stream_complete(self, system_prompt: str, user_prompt: str) -> Iterator[str]:
        if self._client is None:
            if settings.enable_mock_llm:
                yield from self._chunk_text(self._mock_response(user_prompt))
                return
            raise RuntimeError("DASHSCOPE_API_KEY is not configured.")

        stream = self._client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            stream=True,
        )
        for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                yield delta

    @staticmethod
    def _mock_response(user_prompt: str) -> str:
        return """根据已召回的知识片段，可以先按制度文档中的流程处理。若召回内容不足，应提示用户补充相关文档或联系管理员确认。

回答策略：
1. 优先引用检索到的企业知识片段。
2. 不确定的内容不要编造。
3. 对流程类问题给出步骤化答案。"""

    @staticmethod
    def _chunk_text(text: str, size: int = 8) -> Iterator[str]:
        for index in range(0, len(text), size):
            yield text[index : index + size]

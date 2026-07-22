import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.permissions import normalize_role
from app.services.rag_agent import RAGAgent, SYSTEM_PROMPT


router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2)
    role: str = "employee"
    top_k: int = Field(default=4, ge=1, le=8)


@router.post("/")
def chat(request: ChatRequest) -> dict[str, object]:
    agent = RAGAgent()
    try:
        return agent.answer(
            question=request.question,
            role=normalize_role(request.role),
            top_k=request.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM call failed: {exc}",
        ) from exc


@router.post("/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    agent = RAGAgent()
    role = normalize_role(request.role)

    def event_stream():
        try:
            hits = agent.retrieve(question=request.question, role=role, top_k=request.top_k)
            yield _sse("sources", agent.format_sources(hits))

            prompt = agent.build_prompt(question=request.question, role=role, hits=hits)
            for chunk in agent.llm.stream_complete(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
            ):
                yield _sse("delta", chunk)
            yield _sse("done", {"ok": True})
        except Exception as exc:
            yield _sse("error", f"LLM call failed: {exc}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

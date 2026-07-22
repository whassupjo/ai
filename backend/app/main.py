from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as document_router


app = FastAPI(
    title="Enterprise RAG Knowledge Agent",
    description="Document upload, retrieval and role-aware enterprise Q&A.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router, prefix="/documents", tags=["documents"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])


@app.get("/")
def index() -> FileResponse:
    frontend = Path(__file__).resolve().parents[2] / "frontend" / "index.html"
    return FileResponse(frontend)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"message": "Enterprise RAG Knowledge Agent is running"}

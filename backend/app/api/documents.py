import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.chunker import split_text
from app.services.document_parser import parse_document
from app.services.permissions import normalize_role
from app.services.vector_store import VectorStore


router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    access_role: str = Form("employee"),
) -> dict[str, object]:
    role = normalize_role(access_role)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Supported files: pdf, docx, txt, md.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        text = parse_document(tmp_path, original_name=file.filename or "document")
        chunks = split_text(text)
        if not chunks:
            raise HTTPException(status_code=422, detail="No readable text found.")

        store = VectorStore()
        stored = store.add_document(
            filename=file.filename or "document",
            access_role=role,
            chunks=chunks,
        )
        return {
            "filename": file.filename,
            "access_role": role,
            "chunks": stored,
        }
    finally:
        tmp_path.unlink(missing_ok=True)


@router.delete("/")
def clear_documents() -> dict[str, object]:
    VectorStore().clear()
    return {"ok": True, "message": "Knowledge base cleared."}

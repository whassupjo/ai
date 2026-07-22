import hashlib
import json
import math
import re
import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.permissions import can_access


LATIN_PATTERN = re.compile(r"[A-Za-z0-9_+#.-]+")
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]+")
VECTOR_DIM = 256
TOKEN_VERSION = 2


def _tokens(text: str) -> list[str]:
    tokens = [token.lower() for token in LATIN_PATTERN.findall(text)]
    for segment in CJK_PATTERN.findall(text):
        if len(segment) <= 4:
            tokens.append(segment)
        for size in (2, 3, 4):
            tokens.extend(segment[index : index + size] for index in range(0, len(segment) - size + 1))
    return tokens


def _hash_vector(text: str) -> list[float]:
    vector = [0.0] * VECTOR_DIM
    for token in _tokens(text):
        digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % VECTOR_DIM
        vector[index] += 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def _cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


class VectorStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or settings.vector_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, records: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self._save([])

    def add_document(self, filename: str, access_role: str, chunks: list[str]) -> int:
        records = self._load()
        document_id = str(uuid.uuid4())
        for index, chunk in enumerate(chunks):
            records.append(
                {
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": index,
                    "access_role": access_role,
                    "text": chunk,
                    "vector": _hash_vector(chunk),
                    "token_version": TOKEN_VERSION,
                }
            )
        self._save(records)
        return len(chunks)

    def search(self, query: str, role: str, top_k: int = 4) -> list[dict[str, Any]]:
        query_vector = _hash_vector(query)
        scored = []
        for record in self._load():
            if not can_access(role, record["access_role"]):
                continue
            vector = record["vector"]
            if record.get("token_version") != TOKEN_VERSION:
                vector = _hash_vector(record["text"])
            score = _cosine(query_vector, vector)
            scored.append({**record, "score": round(score, 4)})
        scored.sort(key=lambda item: item["score"], reverse=True)
        positive = [item for item in scored if item["score"] > 0]
        return (positive or scored)[:top_k]

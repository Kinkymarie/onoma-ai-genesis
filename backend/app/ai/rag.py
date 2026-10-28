from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document
from . import embeddings


def retrieve(db: Session, user_id: int, query: str, limit: int = 5) -> list[dict]:
    q = embeddings.hash_embed(query)
    scored = []
    for d in db.scalars(select(Document).where(Document.user_id == user_id)):
        vec = embeddings.loads(d.embedding) if d.embedding else embeddings.hash_embed(d.content)
        scored.append({"document_id": d.id, "name": d.name, "score": embeddings.cosine(q, vec),
                       "snippet": d.content[:300]})
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:limit]


def build_context(hits: list[dict]) -> tuple[str, list[dict]]:
    citations = [{"ref": i + 1, "document_id": h["document_id"], "name": h["name"]} for i, h in enumerate(hits)]
    text = "\n\n".join(f"[{i + 1}] {h['name']}: {h['snippet']}" for i, h in enumerate(hits))
    return text, citations

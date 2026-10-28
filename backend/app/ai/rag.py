"""Retrieval-augmented generation over workspace documents."""
from dataclasses import dataclass

from ..models.schemas import Document
from .config import get_ai_settings
from .embeddings import cosine_similarity, embed_texts
from .providers import get_provider


@dataclass
class Chunk:
    document_id: str
    title: str
    text: str
    score: float = 0.0


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    if size <= overlap:
        raise ValueError("size must exceed overlap")
    text = text.strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks


async def retrieve(query: str, documents: list[Document], k: int = 4) -> list[Chunk]:
    chunks = [Chunk(d.id, d.title, c) for d in documents for c in chunk_text(f"{d.title}\n{d.content}")]
    if not chunks:
        return []
    vectors = await embed_texts([query] + [c.text for c in chunks])
    qvec = vectors[0]
    for chunk, vec in zip(chunks, vectors[1:]):
        chunk.score = cosine_similarity(qvec, vec)
    return sorted((c for c in chunks if c.score > 0), key=lambda c: c.score, reverse=True)[:k]


def build_context(chunks: list[Chunk]) -> str:
    limit = get_ai_settings().max_context_chars
    parts, used = [], 0
    for c in chunks:
        piece = f"[{c.title}] {c.text}"
        if used + len(piece) > limit:
            break
        parts.append(piece)
        used += len(piece)
    return "\n\n".join(parts)


async def answer(query: str, documents: list[Document], provider: str | None = None, k: int = 4):
    chunks = await retrieve(query, documents, k)
    context = build_context(chunks)
    system = "Answer using the provided context. If it is insufficient, say so."
    if context:
        system += f"\n\nContext:\n{context}"
    reply = await get_provider(provider).chat(
        [{"role": "system", "content": system}, {"role": "user", "content": query}])
    return reply, chunks

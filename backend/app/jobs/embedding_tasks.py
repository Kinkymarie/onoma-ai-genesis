"""Embedding generation jobs."""
import asyncio

from ..ai.embeddings import embed_texts
from ..db.repositories import Repositories


def embed_missing_memories(repos: Repositories) -> int:
    """Generate embeddings for memories that lack one. Returns number updated."""
    pending = [m for m in repos.memories.list() if not m.embedding]
    if not pending:
        return 0
    vectors = asyncio.run(embed_texts([m.content for m in pending]))
    for mem, vec in zip(pending, vectors):
        repos.memories.update(mem.id, embedding=vec)
    return len(pending)

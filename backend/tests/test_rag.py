import asyncio

from app.ai.embeddings import cosine_similarity, hash_embed
from app.ai.rag import answer, chunk_text, retrieve
from app.models.schemas import Document
import pytest


def test_chunking():
    assert chunk_text("") == []
    chunks = chunk_text("a" * 1200, size=500, overlap=50)
    assert len(chunks) == 3 and all(len(c) <= 500 for c in chunks)
    with pytest.raises(ValueError):
        chunk_text("abc", size=10, overlap=10)


def test_embeddings_similarity():
    a, b, c = hash_embed("cats and dogs"), hash_embed("cats and dogs"), hash_embed("quantum chromodynamics")
    assert cosine_similarity(a, b) == pytest.approx(1.0)
    assert cosine_similarity(a, c) < 0.5
    assert cosine_similarity([], a) == 0.0


def docs():
    return [Document(workspace_id="w", title="Pets", content="cats and dogs are pets", created_by="u"),
            Document(workspace_id="w", title="Physics", content="quantum chromodynamics and quarks", created_by="u")]


def test_retrieve_ranks_relevant_first():
    chunks = asyncio.run(retrieve("quarks", docs(), k=2))
    assert chunks[0].title == "Physics"


def test_answer_uses_provider():
    reply, chunks = asyncio.run(answer("cats", docs(), provider="echo"))
    assert reply == "Echo: cats" and chunks

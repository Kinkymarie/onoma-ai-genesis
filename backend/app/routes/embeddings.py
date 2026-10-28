"""Embedding API."""
from fastapi import APIRouter, Depends

from ..ai.embeddings import embed_texts
from ..dependencies import get_current_user
from ..models.schemas import EmbeddingRequest, User

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


@router.post("")
async def embed(data: EmbeddingRequest, _: User = Depends(get_current_user)):
    vectors = await embed_texts(data.texts)
    return {"embeddings": vectors, "dimensions": len(vectors[0]) if vectors else 0}

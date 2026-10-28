"""Text embeddings: provider-backed with a deterministic offline fallback."""
import hashlib
import math
import re

from ..utils.logger import get_logger
from .config import get_ai_settings

log = get_logger(__name__)
_TOKEN_RE = re.compile(r"\w+")


def hash_embed(text: str, dims: int | None = None) -> list[float]:
    """Deterministic bag-of-words hashing embedding (L2 normalised)."""
    dims = dims or get_ai_settings().embedding_dimensions
    vec = [0.0] * dims
    for tok in _TOKEN_RE.findall(text.lower()):
        h = int.from_bytes(hashlib.sha256(tok.encode()).digest()[:8], "big")
        vec[h % dims] += 1.0 if (h >> 63) & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm else vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed using OpenAI when configured, else the offline hash embedder."""
    if not texts:
        return []
    if get_ai_settings().openai_api_key:
        from .providers.openai import OpenAIProvider
        try:
            return await OpenAIProvider().embed(texts)
        except Exception:  # noqa: BLE001 - fall back so search keeps working
            log.warning("embedding provider failed; using offline embeddings")
    return [hash_embed(t) for t in texts]

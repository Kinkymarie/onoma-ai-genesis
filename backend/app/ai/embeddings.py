"""Embedding service with a deterministic hashing fallback; vectors stored as JSON (pgvector-ready)."""
from __future__ import annotations

import hashlib
import json
import math

from .providers import ProviderError, get_provider

DIM = 256


def hash_embed(text: str, dim: int = DIM) -> list[float]:
    vec = [0.0] * dim
    for tok in text.lower().split():
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0 if (h >> 8) & 1 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed_texts(texts: list[str], provider: str | None = None) -> list[list[float]]:
    if provider in (None, "hash"):
        return [hash_embed(t) for t in texts]
    try:
        return get_provider(provider).embed(texts)
    except ProviderError:
        return [hash_embed(t) for t in texts]


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def dumps(v: list[float]) -> str:
    return json.dumps(v)


def loads(s: str) -> list[float]:
    return json.loads(s)

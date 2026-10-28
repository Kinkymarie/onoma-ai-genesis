from __future__ import annotations

import httpx

from ...config import get_settings
from .base import LLMProvider, ProviderError


class LocalProvider(LLMProvider):
    """Ollama-compatible local model server; falls back to a deterministic echo if unreachable."""

    name = "local"

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or get_settings().local_llm_url).rstrip("/")

    def complete(self, messages, model=None, **kw):
        try:
            r = httpx.post(
                f"{self.base_url}/api/chat",
                json={"model": model or "llama3", "messages": messages, "stream": False},
                timeout=120,
            )
            r.raise_for_status()
            return r.json()["message"]["content"]
        except (httpx.HTTPError, KeyError, ValueError):
            last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            return f"[local provider unavailable] Received: {last[:500]}"

    def embed(self, texts, model=None):
        out = []
        for t in texts:
            try:
                r = httpx.post(f"{self.base_url}/api/embeddings",
                               json={"model": model or "nomic-embed-text", "prompt": t}, timeout=60)
                r.raise_for_status()
                out.append(r.json()["embedding"])
            except (httpx.HTTPError, KeyError, ValueError) as e:
                raise ProviderError("local embedding server unavailable") from e
        return out

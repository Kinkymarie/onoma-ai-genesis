"""Offline provider used for development and tests (no external calls)."""
from typing import AsyncIterator

from ..embeddings import hash_embed
from .base import ChatMessages, LLMProvider


class EchoProvider(LLMProvider):
    name = "echo"

    async def chat(self, messages: ChatMessages, *, model=None, temperature=0.7, max_tokens=None) -> str:
        last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return f"Echo: {last}"

    async def stream(self, messages: ChatMessages, *, model=None, temperature=0.7,
                     max_tokens=None) -> AsyncIterator[str]:
        reply = await self.chat(messages)
        for word in reply.split(" "):
            yield word + " "

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [hash_embed(t) for t in texts]

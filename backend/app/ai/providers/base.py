"""Abstract LLM provider."""
from abc import ABC, abstractmethod
from typing import AsyncIterator

ChatMessages = list[dict[str, str]]


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def chat(self, messages: ChatMessages, *, model: str | None = None,
                   temperature: float = 0.7, max_tokens: int | None = None) -> str:
        """Return the full assistant reply."""

    @abstractmethod
    def stream(self, messages: ChatMessages, *, model: str | None = None,
               temperature: float = 0.7, max_tokens: int | None = None) -> AsyncIterator[str]:
        """Yield reply text chunks."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError(f"{self.name} does not support embeddings")

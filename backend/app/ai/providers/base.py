from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator


class ProviderError(Exception):
    pass


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def complete(self, messages: list[dict], model: str | None = None, **kw) -> str: ...

    def stream(self, messages: list[dict], model: str | None = None, **kw) -> Iterator[str]:
        yield self.complete(messages, model, **kw)

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        raise ProviderError(f"{self.name} does not support embeddings")

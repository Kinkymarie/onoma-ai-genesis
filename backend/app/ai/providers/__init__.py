from __future__ import annotations

from .base import LLMProvider, ProviderError


def get_provider(name: str | None = None) -> LLMProvider:
    from ...config import get_settings

    name = (name or get_settings().default_provider).lower()
    if name == "openai":
        from .openai import OpenAIProvider
        return OpenAIProvider()
    if name == "anthropic":
        from .anthropic import AnthropicProvider
        return AnthropicProvider()
    if name == "local":
        from .local import LocalProvider
        return LocalProvider()
    raise ProviderError(f"unknown provider: {name}")


__all__ = ["LLMProvider", "ProviderError", "get_provider"]

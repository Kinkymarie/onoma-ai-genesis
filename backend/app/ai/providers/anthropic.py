from __future__ import annotations

from ...config import get_settings
from .base import LLMProvider, ProviderError


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().anthropic_api_key
        if not self.api_key:
            raise ProviderError("ANTHROPIC_API_KEY is not configured")
        import anthropic

        self.client = anthropic.Anthropic(api_key=self.api_key)

    @staticmethod
    def _split(messages):
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        return system, [m for m in messages if m["role"] != "system"]

    def complete(self, messages, model=None, **kw):
        system, msgs = self._split(messages)
        r = self.client.messages.create(
            model=model or "claude-3-5-sonnet-latest", max_tokens=kw.pop("max_tokens", 1024),
            system=system or None, messages=msgs, **kw)
        return "".join(b.text for b in r.content if getattr(b, "text", None))

from __future__ import annotations

from ...config import get_settings
from .base import LLMProvider, ProviderError


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().openai_api_key
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is not configured")
        from openai import OpenAI

        self.client = OpenAI(api_key=self.api_key)

    def complete(self, messages, model=None, **kw):
        r = self.client.chat.completions.create(model=model or "gpt-4o-mini", messages=messages, **kw)
        return r.choices[0].message.content or ""

    def stream(self, messages, model=None, **kw):
        for chunk in self.client.chat.completions.create(
            model=model or "gpt-4o-mini", messages=messages, stream=True, **kw
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def embed(self, texts, model=None):
        r = self.client.embeddings.create(model=model or "text-embedding-3-small", input=texts)
        return [d.embedding for d in r.data]

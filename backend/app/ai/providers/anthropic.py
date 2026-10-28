"""Anthropic Claude provider."""
import json
from typing import AsyncIterator

import httpx

from ...utils.exceptions import ProviderError
from ..config import get_ai_settings
from .base import ChatMessages, LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        s = get_ai_settings()
        self.api_key = s.anthropic_api_key if api_key is None else api_key
        self.base_url = s.anthropic_base_url.rstrip("/")
        self.model = model or s.anthropic_model
        self.timeout = s.request_timeout

    def _headers(self) -> dict[str, str]:
        return {"x-api-key": self.api_key, "anthropic-version": "2023-06-01",
                "content-type": "application/json"}

    def _body(self, messages, model, temperature, max_tokens, stream=False) -> dict:
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        chat = [{"role": "assistant" if m["role"] == "assistant" else "user", "content": m["content"]}
                for m in messages if m["role"] != "system"]
        body = {"model": model or self.model, "messages": chat, "temperature": min(temperature, 1.0),
                "max_tokens": max_tokens or 1024, "stream": stream}
        if system:
            body["system"] = system
        return body

    async def chat(self, messages: ChatMessages, *, model=None, temperature=0.7, max_tokens=None) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(f"{self.base_url}/messages", headers=self._headers(),
                                      json=self._body(messages, model, temperature, max_tokens))
                r.raise_for_status()
                return "".join(b.get("text", "") for b in r.json()["content"])
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError("anthropic request failed") from exc

    async def stream(self, messages: ChatMessages, *, model=None, temperature=0.7,
                     max_tokens=None) -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/messages", headers=self._headers(),
                                         json=self._body(messages, model, temperature, max_tokens, True)) as r:
                    r.raise_for_status()
                    async for line in r.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        event = json.loads(line[5:].strip())
                        if event.get("type") == "content_block_delta":
                            text = event.get("delta", {}).get("text")
                            if text:
                                yield text
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError("anthropic stream failed") from exc

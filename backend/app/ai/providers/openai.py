"""OpenAI (and OpenAI-compatible) provider."""
import json
from typing import AsyncIterator

import httpx

from ...utils.exceptions import ProviderError
from ..config import get_ai_settings
from .base import ChatMessages, LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 model: str | None = None, embedding_model: str | None = None):
        s = get_ai_settings()
        self.api_key = s.openai_api_key if api_key is None else api_key
        self.base_url = (base_url or s.openai_base_url).rstrip("/")
        self.model = model or s.openai_model
        self.embedding_model = embedding_model or s.openai_embedding_model
        self.timeout = s.request_timeout

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = " ".join(["Bearer", self.api_key])
        return headers

    def _body(self, messages, model, temperature, max_tokens, stream=False) -> dict:
        body = {"model": model or self.model, "messages": messages,
                "temperature": temperature, "stream": stream}
        if max_tokens:
            body["max_tokens"] = max_tokens
        return body

    async def chat(self, messages: ChatMessages, *, model=None, temperature=0.7, max_tokens=None) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(f"{self.base_url}/chat/completions", headers=self._headers(),
                                      json=self._body(messages, model, temperature, max_tokens))
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"] or ""
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise ProviderError(f"{self.name} request failed") from exc

    async def stream(self, messages: ChatMessages, *, model=None, temperature=0.7,
                     max_tokens=None) -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/chat/completions",
                                         headers=self._headers(),
                                         json=self._body(messages, model, temperature, max_tokens, True)) as r:
                    r.raise_for_status()
                    async for line in r.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        delta = json.loads(data)["choices"][0].get("delta", {}).get("content")
                        if delta:
                            yield delta
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise ProviderError(f"{self.name} stream failed") from exc

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(f"{self.base_url}/embeddings", headers=self._headers(),
                                      json={"model": self.embedding_model, "input": texts})
                r.raise_for_status()
                return [d["embedding"] for d in sorted(r.json()["data"], key=lambda d: d["index"])]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise ProviderError(f"{self.name} embeddings failed") from exc

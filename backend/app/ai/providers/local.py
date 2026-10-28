"""Local LLM (Ollama / llama.cpp / vLLM via OpenAI-compatible API)."""
from ..config import get_ai_settings
from .openai import OpenAIProvider


class LocalProvider(OpenAIProvider):
    name = "local"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        s = get_ai_settings()
        super().__init__(api_key="", base_url=base_url or s.local_llm_url, model=model or s.local_llm_model)

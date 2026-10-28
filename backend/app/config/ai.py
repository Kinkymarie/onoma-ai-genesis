"""AI provider configuration."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4-turbo"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com/v1"
    anthropic_model: str = "claude-3-5-sonnet-latest"
    local_llm_url: str = "http://localhost:11434/v1"
    local_llm_model: str = "llama3"
    default_provider: str = "openai"
    embedding_dimensions: int = 256
    request_timeout: float = 60.0
    max_context_chars: int = 8000


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()

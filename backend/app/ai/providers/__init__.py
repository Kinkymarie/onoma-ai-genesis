"""Provider factory."""
from ...utils.exceptions import BadRequest
from ...utils.logger import get_logger
from ..config import SUPPORTED_PROVIDERS, get_ai_settings
from .anthropic import AnthropicProvider
from .base import LLMProvider
from .echo import EchoProvider
from .local import LocalProvider
from .openai import OpenAIProvider

log = get_logger(__name__)


def get_provider(name: str | None = None) -> LLMProvider:
    s = get_ai_settings()
    name = (name or s.default_provider).lower()
    if name not in SUPPORTED_PROVIDERS:
        raise BadRequest(f"Unsupported provider: {name}")
    if name == "openai":
        if s.openai_api_key:
            return OpenAIProvider()
        log.warning("OPENAI_API_KEY not set; using offline echo provider")
        return EchoProvider()
    if name == "anthropic":
        if s.anthropic_api_key:
            return AnthropicProvider()
        log.warning("ANTHROPIC_API_KEY not set; using offline echo provider")
        return EchoProvider()
    if name == "local":
        return LocalProvider()
    return EchoProvider()


__all__ = ["LLMProvider", "OpenAIProvider", "AnthropicProvider", "LocalProvider", "EchoProvider", "get_provider"]

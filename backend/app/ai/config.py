"""AI configuration facade."""
from ..config.ai import AISettings, get_ai_settings

SUPPORTED_PROVIDERS = ("openai", "anthropic", "local", "echo")

__all__ = ["AISettings", "get_ai_settings", "SUPPORTED_PROVIDERS"]

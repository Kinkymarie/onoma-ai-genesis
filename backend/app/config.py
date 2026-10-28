from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./onoma.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    redis_url: str = ""
    jwt_secret: str = "dev-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 120
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    local_llm_url: str = "http://localhost:11434"
    default_provider: str = "local"
    google_client_id: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    sendgrid_api_key: str = ""
    sentry_dsn: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.app_env == "production" and s.jwt_secret.startswith("dev-insecure"):
        raise RuntimeError("JWT_SECRET must be set in production")
    return s

"""Database configuration."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://localhost:5432/onoma"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    redis_url: str = "redis://localhost:6379/0"
    # "memory" keeps data in-process (dev/tests); other backends plug in via repositories.
    db_backend: str = "memory"


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()

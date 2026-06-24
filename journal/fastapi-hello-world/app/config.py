from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    port: int = 8000
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://postgres:dev@localhost:5432/day08_api"
    database_echo: bool = True
    jwt_secret: str = "dev-only-change-me-32-bytes-minimum"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

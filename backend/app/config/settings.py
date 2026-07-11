"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration; values are supplied by environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DecisionLens"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    supermemory_base_url: str | None = None
    supermemory_api_key: str | None = None
    github_token: str | None = None
    slack_signing_secret: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the singleton settings object for dependency injection."""
    return Settings()

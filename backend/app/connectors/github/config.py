"""Configuration and dependency providers for the GitHub connector."""

from collections.abc import AsyncIterator
from functools import lru_cache

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GitHubConnectorSettings(BaseSettings):
    """GitHub API settings loaded exclusively from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    token: SecretStr = Field(validation_alias="GITHUB_TOKEN")
    api_base_url: AnyHttpUrl = Field(
        default="https://api.github.com", validation_alias="GITHUB_API_BASE_URL"
    )
    timeout_seconds: float = Field(default=30.0, gt=0, validation_alias="GITHUB_TIMEOUT_SECONDS")


@lru_cache
def get_github_settings() -> GitHubConnectorSettings:
    """Return immutable connector settings for dependency injection."""
    return GitHubConnectorSettings()


async def get_github_settings_dependency() -> AsyncIterator[GitHubConnectorSettings]:
    """Expose settings as an async dependency provider when needed by an API layer."""
    yield get_github_settings()

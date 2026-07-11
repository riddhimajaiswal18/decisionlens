"""Configuration and dependency providers for the Slack connector."""

from functools import lru_cache

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SlackConnectorSettings(BaseSettings):
    """Slack API settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: SecretStr = Field(validation_alias="SLACK_BOT_TOKEN")
    api_base_url: AnyHttpUrl = Field(
        default="https://slack.com/api", validation_alias="SLACK_API_BASE_URL"
    )
    timeout_seconds: float = Field(default=30.0, gt=0, validation_alias="SLACK_TIMEOUT_SECONDS")


@lru_cache
def get_slack_settings() -> SlackConnectorSettings:
    """Return cached connector settings for dependency injection."""
    return SlackConnectorSettings()

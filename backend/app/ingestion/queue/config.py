"""Environment-backed Artifact Queue settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.app.ingestion.queue.models import QueueConfig


class QueueSettings(BaseSettings):
    """Loads queue delivery settings independently from queue implementation."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    max_attempts: int = Field(default=3, ge=1, validation_alias="ARTIFACT_QUEUE_MAX_ATTEMPTS")

    def to_config(self) -> QueueConfig:
        return QueueConfig(max_attempts=self.max_attempts)


@lru_cache
def get_queue_config() -> QueueConfig:
    """Return the default queue configuration for dependency injection."""
    return QueueSettings().to_config()

"""Environment-backed defaults for the ingestion buffer."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.app.ingestion.buffer.models import BufferConfig


class BufferSettings(BaseSettings):
    """Loads buffer limits while keeping BufferConfig independent for unit tests."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    inactivity_seconds: int = Field(default=300, ge=1, validation_alias="INGESTION_BUFFER_INACTIVITY_SECONDS")
    max_messages: int = Field(default=50, ge=1, validation_alias="INGESTION_BUFFER_MAX_MESSAGES")

    def to_config(self) -> BufferConfig:
        """Convert environment settings into the pure buffer configuration contract."""
        return BufferConfig(inactivity_seconds=self.inactivity_seconds, max_messages=self.max_messages)


@lru_cache
def get_buffer_config() -> BufferConfig:
    """Return cached runtime buffer limits for dependency injection."""
    return BufferSettings().to_config()

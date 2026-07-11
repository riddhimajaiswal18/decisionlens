"""Environment-backed Supermemory Local configuration."""

from functools import lru_cache

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SupermemorySettings(BaseSettings):
    """Loads host, authentication, batching, timeout, and retry settings from the environment."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: AnyHttpUrl = Field(validation_alias="SUPERMEMORY_BASE_URL")
    api_key: SecretStr | None = Field(default=None, validation_alias="SUPERMEMORY_API_KEY")
    container_tag: str = Field(default="decisionlens", min_length=1, validation_alias="SUPERMEMORY_CONTAINER_TAG")
    timeout_seconds: float = Field(default=30.0, gt=0, validation_alias="SUPERMEMORY_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, ge=0, validation_alias="SUPERMEMORY_MAX_RETRIES")
    retry_base_seconds: float = Field(default=0.25, gt=0, validation_alias="SUPERMEMORY_RETRY_BASE_SECONDS")
    batch_size: int = Field(default=100, ge=1, le=600, validation_alias="SUPERMEMORY_BATCH_SIZE")
    document_batch_path: str = Field(default="/v3/documents/batch", validation_alias="SUPERMEMORY_DOCUMENT_BATCH_PATH")
    search_path: str = Field(default="/v4/search", validation_alias="SUPERMEMORY_SEARCH_PATH")
    health_path: str = Field(default="/health", validation_alias="SUPERMEMORY_HEALTH_PATH")


@lru_cache
def get_supermemory_settings() -> SupermemorySettings:
    """Return singleton runtime settings for dependency injection."""
    return SupermemorySettings()

"""Environment-backed configuration for local structured-extraction providers."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExtractionSettings(BaseSettings):
    """Selects an extraction provider without leaking that choice into EKPP."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    provider: Literal["demo", "ollama"] = Field(default="ollama", validation_alias="EXTRACTION_PROVIDER")
    ollama_base_url: AnyHttpUrl = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3:8b", min_length=1, validation_alias="OLLAMA_MODEL")
    ollama_timeout: float = Field(default=120.0, gt=0, validation_alias="OLLAMA_TIMEOUT")
    prompt_directory: str | None = Field(default=None, validation_alias="EXTRACTION_PROMPT_DIRECTORY")


@lru_cache
def get_extraction_settings() -> ExtractionSettings:
    """Return the process-wide extraction settings instance."""
    return ExtractionSettings()

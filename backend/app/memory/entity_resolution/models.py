"""Contracts for two-stage entity canonicalization."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResolvedEntity(BaseModel):
    """An entity normalized by canonicalization and optional code lookup stages."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    original_name: str = Field(min_length=1)
    canonical_name: str = Field(min_length=1)
    entity_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EntityResolutionConfig(BaseModel):
    """Configurable code-lookup aliases owned by the entity-resolution layer."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    lookup_map: dict[str, str] = Field(default_factory=dict)

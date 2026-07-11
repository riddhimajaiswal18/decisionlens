"""Typed request-independent models returned by the Supermemory client."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StorageResult(BaseModel):
    """Result of persisting one DecisionLens object into Supermemory."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    custom_id: str
    remote_id: str | None = None
    status: str | None = None
    error: str | None = None


class MemorySearchResult(BaseModel):
    """Opaque Supermemory search result exposed as a typed client response."""

    model_config = ConfigDict(extra="allow", frozen=True)

    id: str | None = None
    content: str | None = None
    similarity: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemorySearchResponse(BaseModel):
    """Transport-neutral response from the client-level search operation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    results: tuple[MemorySearchResult, ...] = ()
    total: int = 0
    timing_ms: float | None = None

"""Domain schemas not owned by the Artifact contract module."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from backend.app.models.artifact import Artifact, SourceRecord


class Entity(BaseModel):
    name: str
    entity_type: str | None = None
    canonical_name: str | None = None


class KnowledgeObject(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_id: UUID
    decisions: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    status: str | None = None
    architecture_changes: list[str] = Field(default_factory=list)
    entities: list[Entity] = Field(default_factory=list)
    custom_id: str | None = None


class IntelligenceResult(BaseModel):
    result_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime | None = None

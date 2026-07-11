"""Structured, source-grounded extraction contracts."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExtractionType(str, Enum):
    """Engineering fact categories extracted independently from an Artifact."""

    DECISION = "decision"
    TRADEOFF = "tradeoff"
    ALTERNATIVE = "alternative"
    TOPIC = "topic"
    STATUS = "status"
    ARCHITECTURE_CHANGE = "architecture_change"
    ENTITY = "entity"
    OPEN_QUESTION = "open_question"


class ExtractedEvidence(BaseModel):
    """A verbatim source reference returned by an extractor before object building."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    excerpt: str = Field(min_length=1)
    location: str | None = None
    supporting_text: str | None = None


class ExtractedFact(BaseModel):
    """One structured extraction; a null value explicitly represents unknown information."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    type: ExtractionType
    entity: str = Field(min_length=1)
    value: str | None = None
    status: str | None = None
    participants: tuple[str, ...] = ()
    reason: str | None = None
    evidence: tuple[ExtractedEvidence, ...] = ()
    confidence: float = Field(default=0.0, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

"""Immutable, evidence-bound models produced by the Intelligence Engine."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRequest(BaseModel):
    """Caller-supplied query scope shared by independently registered analyzers."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    query: str | None = None
    limit: int = Field(default=100, ge=1, le=500)


class InsightEvidence(BaseModel):
    """Persisted source evidence reconstructed from a stored Knowledge Object."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    content: str = Field(min_length=1)
    memory_id: str | None = None
    artifact_reference: str | None = None
    original_snippet: str = Field(min_length=1)
    source_location: str | None = None
    supporting_text: str = Field(min_length=1)
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    retrieval_similarity: float | None = Field(default=None, ge=0, le=1)


class Insight(BaseModel):
    """Base reusable intelligence result consumed by future API and dashboard layers."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    evidence: tuple[InsightEvidence, ...] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    related_artifacts: tuple[str, ...] = ()
    related_entities: tuple[str, ...] = ()
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TimelineEvent(BaseModel):
    """One source-timestamped architectural event in chronological analysis."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    timestamp: datetime
    decision: str = Field(min_length=1)
    reason: str | None = None
    evidence: tuple[InsightEvidence, ...] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class ArchitectureTimeline(Insight):
    """Chronological architecture history built only from timestamped stored memories."""

    events: tuple[TimelineEvent, ...] = Field(min_length=1)


class RecurringDiscussion(Insight):
    """A repeatedly discussed engineering topic with traceable supporting memories."""

    topic: str = Field(min_length=1)
    discussion_count: int = Field(ge=2)
    status: str | None = None
    last_discussed: datetime | None = None


class TechnologyTrend(Insight):
    """Frequency and explicit acceptance/rejection signals for one technology."""

    technology: str = Field(min_length=1)
    discussion_count: int = Field(ge=1)
    accepted_count: int = Field(default=0, ge=0)
    rejected_count: int = Field(default=0, ge=0)
    is_new: bool = False
    is_deprecated: bool = False


class DecisionHistory(Insight):
    """Evidence-backed sequence of stored decision events for a topic or technology."""

    decision: str = Field(min_length=1)
    history: tuple[TimelineEvent, ...] = Field(min_length=1)
    reasons: tuple[str, ...] = ()
    participants: tuple[str, ...] = ()
    timestamps: tuple[datetime, ...] = Field(min_length=1)


class HistoricalContext(Insight):
    """Prior source-grounded context for a requested engineering topic."""

    topic: str = Field(min_length=1)
    previous_decisions: tuple[str, ...] = ()
    related_discussions: tuple[str, ...] = ()
    tradeoffs: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    architecture_changes: tuple[str, ...] = ()

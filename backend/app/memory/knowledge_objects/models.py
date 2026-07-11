"""Immutable, evidence-backed engineering knowledge object models."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class KnowledgeObjectType(str):
    """String constants used to classify engineering knowledge without source coupling."""

    DECISION = "decision"
    TRADEOFF = "tradeoff"
    ALTERNATIVE = "alternative"
    TOPIC = "topic"
    ARCHITECTURE_CHANGE = "architecture_change"
    ENTITY = "entity"
    STATUS = "status"
    OPEN_QUESTION = "open_question"


class Evidence(BaseModel):
    """Persistable, source-grounded support for one Knowledge Object."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_artifact: UUID = Field(validation_alias=AliasChoices("source_artifact", "artifact_reference"))
    original_snippet: str = Field(min_length=1, validation_alias=AliasChoices("original_snippet", "excerpt"))
    source_location: str | None = Field(default=None, validation_alias=AliasChoices("source_location", "location"))
    supporting_text: str = Field(min_length=1)

    @property
    def artifact_reference(self) -> UUID:
        return self.source_artifact

    @property
    def excerpt(self) -> str:
        return self.original_snippet

    @property
    def location(self) -> str | None:
        return self.source_location


class Confidence(BaseModel):
    """EKPP extraction confidence; it is never a retrieval-similarity score."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    extraction_score: float = Field(ge=0, le=1, validation_alias=AliasChoices("extraction_score", "score"))
    rationale: str | None = None

    @property
    def score(self) -> float:
        """Compatibility accessor for callers of the previous contract."""
        return self.extraction_score


class KnowledgeObject(BaseModel):
    """Evidence-backed engineering fact awaiting deterministic identity assignment."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    knowledge_id: UUID = Field(default_factory=uuid4)
    type: str
    entity: str = Field(min_length=1)
    value: str = Field(min_length=1)
    status: str | None = None
    timestamp: datetime
    participants: tuple[str, ...] = ()
    reason: str | None = None
    artifact_reference: UUID
    evidence: tuple[Evidence, ...] = Field(min_length=1)
    confidence: Confidence
    metadata: dict[str, Any] = Field(default_factory=dict)
    custom_id: str | None = Field(default=None, validation_alias=AliasChoices("custom_id", "customId"), serialization_alias="customId")


class PersistedKnowledgeObject(KnowledgeObject):
    """A Knowledge Object whose deduplication stage has assigned its required custom ID."""

    custom_id: str = Field(validation_alias=AliasChoices("custom_id", "customId"), serialization_alias="customId")


class Decision(KnowledgeObject):
    """A documented engineering choice consumed by historical decision retrieval."""

    type: Literal["decision"] = KnowledgeObjectType.DECISION


class Tradeoff(KnowledgeObject):
    """A stated engineering compromise consumed by decision-context analysis."""

    type: Literal["tradeoff"] = KnowledgeObjectType.TRADEOFF


class Alternative(KnowledgeObject):
    """A considered option consumed by future decision and comparison workflows."""

    type: Literal["alternative"] = KnowledgeObjectType.ALTERNATIVE


class Topic(KnowledgeObject):
    """An engineering discussion subject consumed by topical retrieval."""

    type: Literal["topic"] = KnowledgeObjectType.TOPIC


class ArchitectureChange(KnowledgeObject):
    """A recorded structural system change consumed by architecture timelines."""

    type: Literal["architecture_change"] = KnowledgeObjectType.ARCHITECTURE_CHANGE


class Entity(KnowledgeObject):
    """A canonical engineering entity consumed by relationship and graph features."""

    type: Literal["entity"] = KnowledgeObjectType.ENTITY


class Status(KnowledgeObject):
    """A source-grounded engineering state consumed by project-status retrieval."""

    type: Literal["status"] = KnowledgeObjectType.STATUS


class OpenQuestion(KnowledgeObject):
    """An unresolved source-grounded question consumed by follow-up workflows."""

    type: Literal["open_question"] = KnowledgeObjectType.OPEN_QUESTION

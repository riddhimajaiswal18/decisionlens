"""Source-agnostic artifact contracts shared across DecisionLens layers."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArtifactSource(str, Enum):
    """Identifies the connector layer that normalized the source material."""

    GITHUB = "github"
    SLACK = "slack"
    MARKDOWN = "markdown"


class ArtifactEventType(str, Enum):
    """Classifies raw engineering material before any knowledge processing occurs."""

    README = "readme"
    MARKDOWN = "markdown"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_COMMENT = "pull_request_comment"
    COMMIT = "commit"
    THREAD = "thread"
    DOCUMENT = "document"
    ADR = "adr"
    RFC = "rfc"


class ProcessingStatus(str, Enum):
    """Represents the Artifact lifecycle state owned by the ingestion workflow."""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class _RawSourceContract(BaseModel):
    """Shared immutable fields for source-normalized and canonical raw data."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source: ArtifactSource
    source_id: str = Field(min_length=1)
    event_type: ArtifactEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    author: str = Field(min_length=1)
    title: str | None = None
    raw_content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Reject timestamps that cannot be placed accurately on a shared timeline."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value


class SourceRecord(_RawSourceContract):
    """Connector-owned normalized source data awaiting the ingestion engine.

    Connectors produce this bridge contract; the ingestion engine consumes it to create
    an Artifact. Queue and knowledge-processing layers do not consume SourceRecord.
    """


class Artifact(_RawSourceContract):
    """The canonical, source-agnostic raw-data contract in DecisionLens.

    The ingestion engine owns Artifact creation. The queue and EKPP consume it as raw
    material, without needing connector-specific schemas or performing AI work here.
    """

    artifact_id: UUID = Field(default_factory=uuid4)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING

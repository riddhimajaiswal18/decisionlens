"""Immutable Artifact Queue state models."""

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models import Artifact


class QueueItemStatus(str, Enum):
    """Lifecycle states owned by the Artifact Queue, not by an Artifact itself."""

    QUEUED = "queued"
    PROCESSING = "processing"
    RETRY = "retry"
    COMPLETED = "completed"
    DEAD_LETTER = "dead_letter"


class QueueItem(BaseModel):
    """One queued Artifact plus delivery state consumed by the EKPP worker."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    item_id: UUID = Field(default_factory=uuid4)
    artifact: Artifact
    status: QueueItemStatus = QueueItemStatus.QUEUED
    attempts: int = Field(default=0, ge=0)
    last_error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QueueConfig(BaseModel):
    """Testable queue delivery limits owned by the queue layer."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    max_attempts: int = Field(default=3, ge=1)

"""Immutable contracts emitted and managed by the ingestion buffer."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TranscriptMessage(BaseModel):
    """One raw message retained in a transcript for the ingestion engine to consume."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: str = Field(min_length=1)
    message_ts: str = Field(min_length=1)
    author: str = Field(min_length=1)
    text: str
    timestamp: datetime
    attachments: tuple[dict[str, Any], ...] = ()


class AggregatedTranscript(BaseModel):
    """A ready-to-ingest conversation session owned and emitted by the buffer layer.

    The future ingestion engine consumes this raw transcript to create an Artifact.
    It intentionally contains no Artifact, extraction, or storage fields.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    transcript_id: UUID = Field(default_factory=uuid4)
    session_key: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    thread_ts: str | None = None
    started_at: datetime
    ended_at: datetime
    messages: tuple[TranscriptMessage, ...] = Field(min_length=1)


class BufferState(BaseModel):
    """The persisted, incomplete conversation state owned by a buffer store.

    Buffer managers read and replace this immutable state; Redis or another store can
    implement the same lifecycle without changing the grouping algorithm.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_key: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    thread_ts: str | None = None
    started_at: datetime
    last_activity_at: datetime
    messages: tuple[TranscriptMessage, ...] = Field(min_length=1)


class BufferConfig(BaseModel):
    """Testable buffering limits owned by the ingestion-buffer layer."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    inactivity_seconds: int = Field(default=300, ge=1)
    max_messages: int = Field(default=50, ge=1)

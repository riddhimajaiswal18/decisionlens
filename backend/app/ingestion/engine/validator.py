"""Boundary validation for normalized ingestion inputs and produced Artifacts."""

from datetime import datetime
from uuid import UUID

from backend.app.ingestion.buffer.models import AggregatedTranscript
from backend.app.ingestion.engine.exceptions import (
    MetadataValidationError,
    RequiredFieldError,
    TimestampValidationError,
    UnsupportedInputError,
)
from backend.app.ingestion.engine.interfaces import ArtifactInput, IngestionValidator
from backend.app.models import Artifact, ArtifactEventType, SourceRecord


class DefaultIngestionValidator(IngestionValidator):
    """Validates the common raw-data invariants owned by the ingestion engine."""

    def validate_input(self, value: ArtifactInput) -> None:
        if isinstance(value, SourceRecord):
            self._validate_source_record(value)
            return
        if isinstance(value, AggregatedTranscript):
            self._validate_transcript(value)
            return
        raise UnsupportedInputError(f"Unsupported ingestion input: {type(value).__name__}.")

    def validate_artifact(self, artifact: Artifact) -> None:
        if not isinstance(artifact.artifact_id, UUID):
            raise RequiredFieldError("artifact_id")
        if not isinstance(artifact.event_type, ArtifactEventType):
            raise UnsupportedInputError("Artifact has an unknown event type.")
        self._validate_timestamp(artifact.timestamp, "artifact.timestamp")
        if not isinstance(artifact.metadata, dict):
            raise MetadataValidationError()

    def _validate_source_record(self, record: SourceRecord) -> None:
        for field_name, value in (("source_id", record.source_id), ("author", record.author), ("raw_content", record.raw_content)):
            if not isinstance(value, str) or not value.strip():
                raise RequiredFieldError(field_name)
        if not isinstance(record.event_type, ArtifactEventType):
            raise UnsupportedInputError("SourceRecord has an unknown event type.")
        self._validate_timestamp(record.timestamp, "source_record.timestamp")
        if not isinstance(record.metadata, dict):
            raise MetadataValidationError()

    def _validate_transcript(self, transcript: AggregatedTranscript) -> None:
        if not transcript.messages:
            raise RequiredFieldError("messages")
        self._validate_timestamp(transcript.started_at, "transcript.started_at")
        self._validate_timestamp(transcript.ended_at, "transcript.ended_at")
        if transcript.ended_at < transcript.started_at:
            raise TimestampValidationError("Transcript end time must not precede its start time.")
        for message in transcript.messages:
            self._validate_timestamp(message.timestamp, "transcript.message.timestamp")

    @staticmethod
    def _validate_timestamp(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise TimestampValidationError(f"{field_name} must be timezone-aware.")

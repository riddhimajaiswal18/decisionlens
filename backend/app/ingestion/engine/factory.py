"""Source-specific Artifact builders and the factory that selects them."""

from abc import ABC, abstractmethod

from backend.app.ingestion.buffer.models import AggregatedTranscript
from backend.app.ingestion.engine.exceptions import UnsupportedInputError
from backend.app.ingestion.engine.interfaces import ArtifactBuilder, ArtifactBuilderFactory, ArtifactInput
from backend.app.models import Artifact, ArtifactEventType, ArtifactSource, ProcessingStatus, SourceRecord


class SourceRecordArtifactBuilder(ArtifactBuilder, ABC):
    """Common Artifact construction for connectors that already emit SourceRecords."""

    source: ArtifactSource

    def supports(self, value: ArtifactInput) -> bool:
        return isinstance(value, SourceRecord) and value.source is self.source

    async def build(self, value: ArtifactInput) -> Artifact:
        if not isinstance(value, SourceRecord):
            raise UnsupportedInputError("SourceRecord builder received an unsupported input.")
        return Artifact(
            source=value.source,
            source_id=value.source_id,
            event_type=value.event_type,
            timestamp=value.timestamp,
            author=value.author,
            title=value.title,
            raw_content=value.raw_content,
            metadata={**value.metadata, "ingestion": {"input_type": "source_record"}},
            processing_status=ProcessingStatus.PENDING,
        )


class GitHubArtifactBuilder(SourceRecordArtifactBuilder):
    """Builds Artifacts from normalized GitHub records."""

    source = ArtifactSource.GITHUB


class MarkdownArtifactBuilder(SourceRecordArtifactBuilder):
    """Builds Artifacts from normalized Markdown documentation records."""

    source = ArtifactSource.MARKDOWN


class SlackTranscriptArtifactBuilder(ArtifactBuilder):
    """Builds one Slack Artifact from a buffer-emitted conversation transcript."""

    def supports(self, value: ArtifactInput) -> bool:
        return isinstance(value, AggregatedTranscript)

    async def build(self, value: ArtifactInput) -> Artifact:
        if not isinstance(value, AggregatedTranscript):
            raise UnsupportedInputError("Slack transcript builder received an unsupported input.")
        return Artifact(
            source=ArtifactSource.SLACK,
            source_id=str(value.transcript_id),
            event_type=ArtifactEventType.THREAD,
            timestamp=value.ended_at,
            author="multiple",
            title=f"Slack conversation {value.thread_ts or value.channel_id}",
            raw_content="\n\n".join(f"{message.author}: {message.text}" for message in value.messages),
            metadata={
                "channel_id": value.channel_id,
                "thread_ts": value.thread_ts,
                "session_key": value.session_key,
                "message_count": len(value.messages),
                "message_source_ids": [message.source_id for message in value.messages],
                "ingestion": {"input_type": "aggregated_transcript"},
            },
            processing_status=ProcessingStatus.PENDING,
        )


class DefaultArtifactBuilderFactory(ArtifactBuilderFactory):
    """Selects registered builders, making new connector types additive."""

    def __init__(self, builders: tuple[ArtifactBuilder, ...] | None = None) -> None:
        self._builders = builders or (
            GitHubArtifactBuilder(),
            MarkdownArtifactBuilder(),
            SlackTranscriptArtifactBuilder(),
        )

    def for_input(self, value: ArtifactInput) -> ArtifactBuilder:
        for builder in self._builders:
            if builder.supports(value):
                return builder
        raise UnsupportedInputError(f"No Artifact builder is registered for {type(value).__name__}.")

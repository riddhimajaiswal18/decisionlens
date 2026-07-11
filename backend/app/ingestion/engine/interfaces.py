"""Testable abstractions for source-specific Artifact construction."""

from abc import ABC, abstractmethod
from typing import TypeAlias

from backend.app.ingestion.buffer.models import AggregatedTranscript
from backend.app.models import Artifact, SourceRecord

ArtifactInput: TypeAlias = SourceRecord | AggregatedTranscript


class ArtifactBuilder(ABC):
    """Builds one canonical Artifact from one supported normalized input type."""

    @abstractmethod
    def supports(self, value: ArtifactInput) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def build(self, value: ArtifactInput) -> Artifact:
        raise NotImplementedError


class ArtifactBuilderFactory(ABC):
    """Selects a source-specific builder without exposing source logic to the engine."""

    @abstractmethod
    def for_input(self, value: ArtifactInput) -> ArtifactBuilder:
        raise NotImplementedError


class IngestionValidator(ABC):
    """Validates normalized inputs and constructed Artifacts at the engine boundary."""

    @abstractmethod
    def validate_input(self, value: ArtifactInput) -> None:
        raise NotImplementedError

    @abstractmethod
    def validate_artifact(self, artifact: Artifact) -> None:
        raise NotImplementedError


class IngestionEngine(ABC):
    """Transforms normalized inputs into immutable Artifacts and nothing else."""

    @abstractmethod
    async def ingest(self, value: ArtifactInput) -> Artifact:
        raise NotImplementedError

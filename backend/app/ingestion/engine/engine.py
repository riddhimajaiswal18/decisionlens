"""Orchestration boundary that creates canonical Artifacts from normalized inputs."""

from collections.abc import AsyncIterator

from backend.app.ingestion.engine.factory import DefaultArtifactBuilderFactory
from backend.app.ingestion.engine.interfaces import ArtifactBuilderFactory, ArtifactInput, IngestionEngine, IngestionValidator
from backend.app.ingestion.engine.validator import DefaultIngestionValidator
from backend.app.models import Artifact


class DefaultIngestionEngine(IngestionEngine):
    """Coordinates validation and source builders without downstream side effects."""

    def __init__(
        self,
        *,
        factory: ArtifactBuilderFactory | None = None,
        validator: IngestionValidator | None = None,
    ) -> None:
        self._factory = factory or DefaultArtifactBuilderFactory()
        self._validator = validator or DefaultIngestionValidator()

    async def ingest(self, value: ArtifactInput) -> Artifact:
        """Validate one normalized input and return its immutable canonical Artifact."""
        self._validator.validate_input(value)
        artifact = await self._factory.for_input(value).build(value)
        self._validator.validate_artifact(artifact)
        return artifact


async def get_ingestion_engine() -> AsyncIterator[IngestionEngine]:
    """Yield the default engine for dependency-injected application consumers."""
    yield DefaultIngestionEngine()

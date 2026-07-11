"""FastAPI dependency-injection skeleton."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from backend.app.config.settings import Settings, get_settings
from backend.app.ingestion.engine.engine import get_ingestion_engine
from backend.app.ingestion.engine.interfaces import IngestionEngine
from backend.app.ingestion.queue.interfaces import ArtifactQueue
from backend.app.ingestion.queue.manager import InMemoryArtifactQueue
from backend.app.intelligence.engine import create_default_intelligence_engine
from backend.app.intelligence.interfaces import EngineeringIntelligenceEngine
from backend.app.memory.supermemory.client import get_supermemory_client
from backend.app.memory.supermemory.contracts import SupermemoryClient

SettingsDependency = Annotated[Settings, Depends(get_settings)]
SupermemoryDependency = Annotated[SupermemoryClient, Depends(get_supermemory_client)]
IngestionEngineDependency = Annotated[IngestionEngine, Depends(get_ingestion_engine)]


def get_intelligence_engine(supermemory: SupermemoryDependency) -> EngineeringIntelligenceEngine:
    """Compose the existing Supermemory-backed Intelligence Engine for one request."""
    return create_default_intelligence_engine(supermemory)


@lru_cache
def get_artifact_queue() -> ArtifactQueue:
    """Return the process-local implementation of the existing Artifact Queue contract."""
    return InMemoryArtifactQueue()


IntelligenceEngineDependency = Annotated[EngineeringIntelligenceEngine, Depends(get_intelligence_engine)]
ArtifactQueueDependency = Annotated[ArtifactQueue, Depends(get_artifact_queue)]

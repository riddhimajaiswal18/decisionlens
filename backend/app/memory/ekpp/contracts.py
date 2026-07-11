"""EKPP orchestration contract."""

from abc import ABC, abstractmethod

from backend.app.memory.knowledge_objects.models import PersistedKnowledgeObject
from backend.app.models import Artifact


class EngineeringKnowledgeProcessingPipeline(ABC):
    """Transforms one Artifact into evidence-backed Knowledge Objects."""

    @abstractmethod
    async def process(self, artifact: Artifact) -> list[PersistedKnowledgeObject]:
        raise NotImplementedError

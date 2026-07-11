"""Knowledge-object construction interface."""

from abc import ABC, abstractmethod

from backend.app.memory.extractors.models import ExtractedFact
from backend.app.memory.knowledge_objects.models import KnowledgeObject
from backend.app.models import Artifact


class KnowledgeObjectBuilder(ABC):
    """Converts evidence-backed extracted facts into immutable Knowledge Objects."""

    @abstractmethod
    async def build(self, artifact: Artifact, facts: list[ExtractedFact]) -> list[KnowledgeObject]:
        raise NotImplementedError

"""Serializer and retry abstractions for independently testable memory persistence."""

from abc import ABC, abstractmethod
from typing import Any

from backend.app.memory.knowledge_objects.models import PersistedKnowledgeObject
from backend.app.models import Artifact


class SupermemorySerializer(ABC):
    """Converts DecisionLens contracts into the stable Supermemory document shape."""

    @abstractmethod
    def artifact_document(self, artifact: Artifact, *, container_tag: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def knowledge_document(self, knowledge_object: PersistedKnowledgeObject, *, container_tag: str) -> dict[str, Any]:
        raise NotImplementedError

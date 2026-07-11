"""High-level Supermemory persistence interface."""

from abc import ABC, abstractmethod

from backend.app.memory.knowledge_objects.models import PersistedKnowledgeObject
from backend.app.memory.supermemory.models import MemorySearchResponse, StorageResult
from backend.app.models import Artifact


class SupermemoryClient(ABC):
    """Persists DecisionLens objects without exposing Supermemory HTTP transport."""

    @abstractmethod
    async def store_artifact(self, artifact: Artifact) -> StorageResult:
        raise NotImplementedError

    @abstractmethod
    async def store_knowledge_object(self, knowledge_object: PersistedKnowledgeObject) -> StorageResult:
        raise NotImplementedError

    @abstractmethod
    async def batch_store(self, knowledge_objects: list[PersistedKnowledgeObject]) -> list[StorageResult]:
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str, *, limit: int = 10) -> MemorySearchResponse:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

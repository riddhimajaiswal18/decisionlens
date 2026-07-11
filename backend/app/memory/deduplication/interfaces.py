"""Deterministic identifier generation interfaces."""

from abc import ABC, abstractmethod

from backend.app.memory.knowledge_objects.models import KnowledgeObject, PersistedKnowledgeObject


class HashStrategy(ABC):
    """Hashes normalized identity strings using a replaceable deterministic strategy."""

    @abstractmethod
    def digest(self, value: str) -> str:
        raise NotImplementedError


class CustomIdGenerator(ABC):
    """Creates deterministic custom IDs for future Supermemory versioning."""

    @abstractmethod
    def generate(self, knowledge_object: KnowledgeObject) -> str:
        raise NotImplementedError


class DeduplicationService(ABC):
    """Assigns deterministic custom IDs without communicating with any memory store."""

    @abstractmethod
    async def assign(self, knowledge_objects: list[KnowledgeObject]) -> list[PersistedKnowledgeObject]:
        raise NotImplementedError

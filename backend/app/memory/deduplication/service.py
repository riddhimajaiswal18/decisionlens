"""SHA-256 custom ID generation and immutable knowledge-object assignment."""

import hashlib
import re

from backend.app.memory.deduplication.interfaces import CustomIdGenerator, DeduplicationService, HashStrategy
from backend.app.memory.knowledge_objects.models import KnowledgeObject, PersistedKnowledgeObject


class SHA256HashStrategy(HashStrategy):
    """Produces a stable SHA-256 digest for normalized engineering fact identity."""

    def digest(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


class DefaultCustomIdGenerator(CustomIdGenerator):
    """Normalizes type and value before deriving a deterministic custom ID."""

    def __init__(self, hash_strategy: HashStrategy | None = None) -> None:
        self._hash_strategy = hash_strategy or SHA256HashStrategy()

    def generate(self, knowledge_object: KnowledgeObject) -> str:
        normalized_value = re.sub(r"[^a-z0-9]+", ":", knowledge_object.value.casefold()).strip(":")
        return self._hash_strategy.digest(f"{knowledge_object.type}:{normalized_value}")


class DefaultDeduplicationService(DeduplicationService):
    """Adds IDs to immutable objects; persistence and comparison remain out of scope."""

    def __init__(self, generator: CustomIdGenerator | None = None) -> None:
        self._generator = generator or DefaultCustomIdGenerator()

    async def assign(self, knowledge_objects: list[KnowledgeObject]) -> list[PersistedKnowledgeObject]:
        return [
            PersistedKnowledgeObject.model_validate(
                {**item.model_dump(), "custom_id": self._generator.generate(item)}
            )
            for item in knowledge_objects
        ]

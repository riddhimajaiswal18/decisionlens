"""Replaceable interfaces for entity canonicalization and lookup normalization."""

from abc import ABC, abstractmethod

from backend.app.memory.entity_resolution.models import ResolvedEntity


class EntityCanonicalizer(ABC):
    """LLM-backed stage that proposes a source-grounded canonical entity name."""

    @abstractmethod
    async def canonicalize(self, name: str) -> str | None:
        raise NotImplementedError


class EntityResolver(ABC):
    """Combines LLM canonicalization with deterministic code lookup normalization."""

    @abstractmethod
    async def resolve(self, names: list[str]) -> list[ResolvedEntity]:
        raise NotImplementedError

    @abstractmethod
    async def canonicalize(self, name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, name: str) -> str:
        raise NotImplementedError

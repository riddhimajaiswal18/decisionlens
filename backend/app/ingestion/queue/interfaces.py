"""Interfaces that allow an in-memory queue to be replaced by Redis later."""

from abc import ABC, abstractmethod
from uuid import UUID

from backend.app.ingestion.queue.models import QueueItem
from backend.app.models import Artifact


class ArtifactQueue(ABC):
    """Buffers Artifacts before EKPP processing without knowing EKPP implementation details."""

    @abstractmethod
    async def enqueue(self, artifact: Artifact) -> QueueItem:
        raise NotImplementedError

    @abstractmethod
    async def dequeue(self, *, timeout_seconds: float | None = None) -> QueueItem | None:
        raise NotImplementedError

    @abstractmethod
    async def acknowledge(self, item_id: UUID) -> QueueItem:
        raise NotImplementedError

    @abstractmethod
    async def retry(self, item_id: UUID, error: str) -> QueueItem:
        raise NotImplementedError

    @abstractmethod
    async def dead_letters(self) -> list[QueueItem]:
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        raise NotImplementedError

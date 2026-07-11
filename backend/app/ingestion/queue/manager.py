"""In-memory asynchronous Artifact Queue with retry and graceful shutdown."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from backend.app.ingestion.queue.config import get_queue_config
from backend.app.ingestion.queue.interfaces import ArtifactQueue
from backend.app.ingestion.queue.models import QueueConfig, QueueItem, QueueItemStatus
from backend.app.ingestion.queue.queue import InMemoryQueueStore
from backend.app.models import Artifact


class InMemoryArtifactQueue(ArtifactQueue):
    """Schedules Artifacts in memory while preserving replaceable queue-state semantics."""

    def __init__(self, *, store: InMemoryQueueStore | None = None, config: QueueConfig | None = None) -> None:
        self._store = store or InMemoryQueueStore()
        self._config = config or get_queue_config()
        self._ready: asyncio.Queue[UUID] = asyncio.Queue()
        self._closed = False

    async def enqueue(self, artifact: Artifact) -> QueueItem:
        if self._closed:
            raise RuntimeError("Artifact Queue is shut down.")
        item = QueueItem(artifact=artifact)
        await self._store.put(item)
        await self._ready.put(item.item_id)
        return item

    async def dequeue(self, *, timeout_seconds: float | None = None) -> QueueItem | None:
        if self._closed and self._ready.empty():
            return None
        try:
            item_id = await asyncio.wait_for(self._ready.get(), timeout=timeout_seconds) if timeout_seconds is not None else await self._ready.get()
        except TimeoutError:
            return None
        item = await self._store.get(item_id)
        if item is None or item.status not in {QueueItemStatus.QUEUED, QueueItemStatus.RETRY}:
            return None
        processing = item.model_copy(update={"status": QueueItemStatus.PROCESSING, "updated_at": datetime.now(UTC)})
        await self._store.put(processing)
        return processing

    async def acknowledge(self, item_id: UUID) -> QueueItem:
        item = await self._require_item(item_id)
        completed = item.model_copy(update={"status": QueueItemStatus.COMPLETED, "updated_at": datetime.now(UTC)})
        await self._store.put(completed)
        return completed

    async def retry(self, item_id: UUID, error: str) -> QueueItem:
        item = await self._require_item(item_id)
        attempts = item.attempts + 1
        status = QueueItemStatus.DEAD_LETTER if attempts >= self._config.max_attempts else QueueItemStatus.RETRY
        updated = item.model_copy(update={"attempts": attempts, "status": status, "last_error": error, "updated_at": datetime.now(UTC)})
        await self._store.put(updated)
        if status is QueueItemStatus.RETRY and not self._closed:
            await self._ready.put(updated.item_id)
        return updated

    async def dead_letters(self) -> list[QueueItem]:
        return await self._store.dead_letters()

    async def shutdown(self) -> None:
        """Stop accepting work while allowing already dequeued work to finish."""
        self._closed = True

    async def _require_item(self, item_id: UUID) -> QueueItem:
        item = await self._store.get(item_id)
        if item is None:
            raise KeyError(f"Queue item not found: {item_id}")
        return item

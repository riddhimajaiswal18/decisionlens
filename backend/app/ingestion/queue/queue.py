"""Small asynchronous storage primitive used by the in-memory queue manager."""

import asyncio
from uuid import UUID

from backend.app.ingestion.queue.models import QueueItem


class InMemoryQueueStore:
    """Stores immutable queue state separately from delivery scheduling mechanics."""

    def __init__(self) -> None:
        self._items: dict[UUID, QueueItem] = {}
        self._dead_letters: set[UUID] = set()
        self._lock = asyncio.Lock()

    async def get(self, item_id: UUID) -> QueueItem | None:
        async with self._lock:
            return self._items.get(item_id)

    async def put(self, item: QueueItem) -> None:
        async with self._lock:
            self._items[item.item_id] = item
            if item.status.value == "dead_letter":
                self._dead_letters.add(item.item_id)

    async def dead_letters(self) -> list[QueueItem]:
        async with self._lock:
            return [self._items[item_id] for item_id in self._dead_letters]

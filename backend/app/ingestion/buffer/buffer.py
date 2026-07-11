"""In-memory buffer store and metadata-based conversation grouping."""

import asyncio

from backend.app.ingestion.buffer.interfaces import BufferStore, ConversationKeyResolver
from backend.app.ingestion.buffer.models import BufferState
from backend.app.models import SourceRecord


class InMemoryBufferStore(BufferStore):
    """Async-safe state store suitable for local use and deterministic unit tests."""

    def __init__(self) -> None:
        self._states: dict[str, BufferState] = {}
        self._lock = asyncio.Lock()

    async def get(self, session_key: str) -> BufferState | None:
        async with self._lock:
            return self._states.get(session_key)

    async def put(self, state: BufferState) -> None:
        async with self._lock:
            self._states[state.session_key] = state

    async def delete(self, session_key: str) -> None:
        async with self._lock:
            self._states.pop(session_key, None)

    async def list_states(self) -> list[BufferState]:
        async with self._lock:
            return list(self._states.values())


class MetadataConversationKeyResolver(ConversationKeyResolver):
    """Groups threaded records by thread timestamp and other records by conversation."""

    def resolve(self, record: SourceRecord) -> tuple[str, str, str | None]:
        metadata = record.metadata
        channel_id = metadata.get("channel_id") or metadata.get("conversation_id")
        if not isinstance(channel_id, str) or not channel_id:
            raise ValueError("SourceRecord metadata requires channel_id or conversation_id for buffering")
        thread_ts = metadata.get("thread_ts")
        if thread_ts is not None and not isinstance(thread_ts, str):
            raise ValueError("SourceRecord metadata thread_ts must be a string when present")
        session_key = f"thread:{channel_id}:{thread_ts}" if thread_ts else f"channel:{channel_id}"
        return session_key, channel_id, thread_ts

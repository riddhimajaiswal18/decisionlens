"""Async sliding-window orchestration for independent conversation buffers."""

import asyncio
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from backend.app.ingestion.buffer.buffer import InMemoryBufferStore, MetadataConversationKeyResolver
from backend.app.ingestion.buffer.config import get_buffer_config
from backend.app.ingestion.buffer.interfaces import BufferStore, ConversationKeyResolver, IngestionBuffer
from backend.app.ingestion.buffer.models import AggregatedTranscript, BufferConfig, BufferState, TranscriptMessage
from backend.app.models import SourceRecord


class IngestionBufferManager(IngestionBuffer):
    """Buffers independent conversations until inactivity or capacity closes a session.

    It owns grouping only: emitted transcripts are left for the future ingestion engine.
    """

    def __init__(
        self,
        *,
        store: BufferStore | None = None,
        config: BufferConfig | None = None,
        key_resolver: ConversationKeyResolver | None = None,
    ) -> None:
        self._store = store or InMemoryBufferStore()
        self._config = config or get_buffer_config()
        self._key_resolver = key_resolver or MetadataConversationKeyResolver()
        self._key_locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def add(self, record: SourceRecord) -> list[AggregatedTranscript]:
        """Add one record and emit a completed session when a boundary is reached."""
        session_key, channel_id, thread_ts = self._key_resolver.resolve(record)
        async with self._key_locks[session_key]:
            state = await self._store.get(session_key)
            emitted: list[AggregatedTranscript] = []
            if state is not None and self._has_inactivity_gap(state, record.timestamp):
                emitted.append(await self._emit(state))
                state = None

            message = self._to_transcript_message(record)
            next_state = self._append_or_start(state, session_key, channel_id, thread_ts, message)
            if len(next_state.messages) >= self._config.max_messages:
                emitted.append(await self._emit(next_state))
            else:
                await self._store.put(next_state)
            return emitted

    async def flush_inactive(self, now: datetime) -> list[AggregatedTranscript]:
        """Emit all sessions whose most recent message is outside the inactivity window."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        emitted: list[AggregatedTranscript] = []
        for candidate in await self._store.list_states():
            async with self._key_locks[candidate.session_key]:
                state = await self._store.get(candidate.session_key)
                if state is not None and self._has_inactivity_gap(state, now):
                    emitted.append(await self._emit(state))
        return emitted

    async def flush_all(self) -> list[AggregatedTranscript]:
        """Emit all active sessions, for controlled shutdown or deterministic tests."""
        emitted: list[AggregatedTranscript] = []
        for candidate in await self._store.list_states():
            async with self._key_locks[candidate.session_key]:
                state = await self._store.get(candidate.session_key)
                if state is not None:
                    emitted.append(await self._emit(state))
        return emitted

    def _has_inactivity_gap(self, state: BufferState, later: datetime) -> bool:
        return later - state.last_activity_at >= timedelta(seconds=self._config.inactivity_seconds)

    @staticmethod
    def _to_transcript_message(record: SourceRecord) -> TranscriptMessage:
        attachments = record.metadata.get("attachments", [])
        normalized_attachments = tuple(attachment for attachment in attachments if isinstance(attachment, dict))
        return TranscriptMessage(
            source_id=record.source_id,
            message_ts=str(record.metadata.get("message_ts") or record.source_id),
            author=record.author,
            text=record.raw_content,
            timestamp=record.timestamp,
            attachments=normalized_attachments,
        )

    @staticmethod
    def _append_or_start(
        state: BufferState | None,
        session_key: str,
        channel_id: str,
        thread_ts: str | None,
        message: TranscriptMessage,
    ) -> BufferState:
        if state is None:
            return BufferState(
                session_key=session_key,
                channel_id=channel_id,
                thread_ts=thread_ts,
                started_at=message.timestamp,
                last_activity_at=message.timestamp,
                messages=(message,),
            )
        return state.model_copy(
            update={
                "last_activity_at": max(state.last_activity_at, message.timestamp),
                "messages": (*state.messages, message),
            }
        )

    async def _emit(self, state: BufferState) -> AggregatedTranscript:
        await self._store.delete(state.session_key)
        messages = tuple(sorted(state.messages, key=lambda message: message.timestamp))
        return AggregatedTranscript(
            session_key=state.session_key,
            channel_id=state.channel_id,
            thread_ts=state.thread_ts,
            started_at=messages[0].timestamp,
            ended_at=messages[-1].timestamp,
            messages=messages,
        )

"""Store, grouping, and buffer interfaces isolated from implementation details."""

from abc import ABC, abstractmethod
from datetime import datetime

from backend.app.ingestion.buffer.models import AggregatedTranscript, BufferState
from backend.app.models import SourceRecord


class BufferStore(ABC):
    """Persists active conversation state; in-memory and Redis stores share this contract."""

    @abstractmethod
    async def get(self, session_key: str) -> BufferState | None:
        raise NotImplementedError

    @abstractmethod
    async def put(self, state: BufferState) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_states(self) -> list[BufferState]:
        raise NotImplementedError


class ConversationKeyResolver(ABC):
    """Maps connector-neutral metadata to a conversation session identity."""

    @abstractmethod
    def resolve(self, record: SourceRecord) -> tuple[str, str, str | None]:
        """Return session key, channel/conversation ID, and optional thread timestamp."""
        raise NotImplementedError


class IngestionBuffer(ABC):
    """Accepts raw source records and emits only ready AggregatedTranscript values."""

    @abstractmethod
    async def add(self, record: SourceRecord) -> list[AggregatedTranscript]:
        raise NotImplementedError

    @abstractmethod
    async def flush_inactive(self, now: datetime) -> list[AggregatedTranscript]:
        raise NotImplementedError

    @abstractmethod
    async def flush_all(self) -> list[AggregatedTranscript]:
        raise NotImplementedError

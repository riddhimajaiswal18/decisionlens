"""Base contract for source connectors."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from backend.app.models import SourceRecord


class SourceConnector(ABC):
    """Fetches and normalizes source data without processing it."""

    @abstractmethod
    async def fetch_records(self) -> AsyncIterator[SourceRecord]:
        """Yield normalized source records."""
        raise NotImplementedError

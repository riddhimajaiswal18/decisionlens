"""Public Slack connector facade."""

from collections.abc import AsyncIterator
from datetime import datetime

from backend.app.connectors.slack.service import SlackService, get_slack_service
from backend.app.models import SourceRecord


class SlackConnector:
    """Fetch one normalized SourceRecord for each Slack source item."""

    def __init__(self, service: SlackService) -> None:
        self._service = service

    async def fetch_channels(self) -> list[SourceRecord]:
        return await self._service.fetch_channels()

    async def fetch_messages(self, channel_id: str, *, limit: int = 100) -> list[SourceRecord]:
        return await self._service.fetch_messages(channel_id, limit=limit)

    async def fetch_thread(self, channel_id: str, thread_ts: str) -> list[SourceRecord]:
        return await self._service.fetch_thread(channel_id, thread_ts)

    async def fetch_recent_messages(self, channel_id: str, *, limit: int = 100) -> list[SourceRecord]:
        return await self._service.fetch_recent_messages(channel_id, limit=limit)

    async def fetch_messages_since(
        self, channel_id: str, timestamp: datetime | str, *, limit: int = 100
    ) -> list[SourceRecord]:
        return await self._service.fetch_messages_since(channel_id, timestamp, limit=limit)


async def get_slack_connector() -> AsyncIterator[SlackConnector]:
    """Yield a request-scoped Slack connector through dependency injection."""
    async for service in get_slack_service():
        yield SlackConnector(service)

"""Slack retrieval and normalization into one SourceRecord per source item."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from backend.app.connectors.slack.client import SlackApiClient
from backend.app.connectors.slack.config import get_slack_settings
from backend.app.connectors.slack.models import SlackAttachment
from backend.app.models import ArtifactEventType, ArtifactSource, SourceRecord


class SlackService:
    """Retrieves public Slack data without aggregation or downstream processing."""

    def __init__(self, client: SlackApiClient) -> None:
        self._client = client

    async def fetch_channels(self) -> list[SourceRecord]:
        """Fetch public-channel descriptors as source records."""
        channels = await self._fetch_pages("conversations.list", item_key="channels", params={"types": "public_channel", "exclude_archived": "true"})
        return [self._channel_record(channel) for channel in channels]

    async def fetch_messages(self, channel_id: str, *, limit: int = 100) -> list[SourceRecord]:
        """Fetch individual channel-history messages without thread aggregation."""
        messages = await self._fetch_pages("conversations.history", item_key="messages", params={"channel": channel_id}, limit=limit)
        return [self._message_record(channel_id, message) for message in messages]

    async def fetch_thread(self, channel_id: str, thread_ts: str) -> list[SourceRecord]:
        """Fetch a thread root and replies as separate SourceRecords."""
        messages = await self._fetch_pages("conversations.replies", item_key="messages", params={"channel": channel_id, "ts": thread_ts})
        return [self._message_record(channel_id, message) for message in messages]

    async def fetch_recent_messages(self, channel_id: str, *, limit: int = 100) -> list[SourceRecord]:
        """Fetch the latest individual messages available in a public channel."""
        return await self.fetch_messages(channel_id, limit=limit)

    async def fetch_messages_since(
        self, channel_id: str, timestamp: datetime | str, *, limit: int = 100
    ) -> list[SourceRecord]:
        """Fetch messages newer than a Slack timestamp for incremental synchronization."""
        oldest = self._as_slack_timestamp(timestamp)
        messages = await self._fetch_pages(
            "conversations.history",
            item_key="messages",
            params={"channel": channel_id, "oldest": oldest, "inclusive": "false"},
            limit=limit,
        )
        return [self._message_record(channel_id, message) for message in messages]

    async def _fetch_pages(
        self,
        method: str,
        *,
        item_key: str,
        params: dict[str, str],
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor: str | None = None
        while limit is None or len(items) < limit:
            page_size = min(200, limit - len(items)) if limit is not None else 200
            page_params = {**params, "limit": str(page_size)}
            if cursor:
                page_params["cursor"] = cursor
            payload = await self._client.get_json(method, params=page_params)
            page_items = payload.get(item_key, [])
            items.extend(page_items)
            cursor = payload.get("response_metadata", {}).get("next_cursor") or None
            if not cursor or not page_items:
                break
        return items[:limit] if limit is not None else items

    @staticmethod
    def _channel_record(channel: dict[str, Any]) -> SourceRecord:
        created = datetime.fromtimestamp(int(channel["created"]), tz=UTC)
        purpose = channel.get("purpose", {}).get("value") or channel.get("topic", {}).get("value") or channel["name"]
        return SourceRecord(
            source=ArtifactSource.SLACK,
            source_id=str(channel["id"]),
            event_type=ArtifactEventType.THREAD,
            timestamp=created,
            author="unknown",
            title=str(channel["name"]),
            raw_content=str(purpose),
            metadata={"channel_id": str(channel["id"]), "message_type": "channel"},
        )

    @classmethod
    def _message_record(cls, channel_id: str, message: dict[str, Any]) -> SourceRecord:
        message_ts = str(message["ts"])
        metadata: dict[str, Any] = {
            "channel_id": channel_id,
            "thread_ts": message.get("thread_ts"),
            "message_ts": message_ts,
            "message_type": message.get("subtype") or "message",
        }
        attachments = cls._attachments(message.get("attachments"))
        if attachments:
            metadata["attachments"] = attachments
        return SourceRecord(
            source=ArtifactSource.SLACK,
            source_id=f"{channel_id}:{message_ts}",
            event_type=ArtifactEventType.THREAD,
            timestamp=cls._datetime_from_slack_timestamp(message_ts),
            author=str(message.get("user") or message.get("bot_id") or "unknown"),
            raw_content=str(message.get("text") or ""),
            metadata=metadata,
        )

    @staticmethod
    def _attachments(raw_attachments: Any) -> list[dict[str, str]]:
        if not isinstance(raw_attachments, list):
            return []
        attachments: list[dict[str, str]] = []
        for attachment in raw_attachments:
            if not isinstance(attachment, dict):
                continue
            normalized = SlackAttachment(
                title=attachment.get("title"),
                text=attachment.get("text"),
                title_link=attachment.get("title_link"),
                image_url=attachment.get("image_url"),
            ).model_dump(exclude_none=True)
            if normalized:
                attachments.append(normalized)
        return attachments

    @staticmethod
    def _datetime_from_slack_timestamp(timestamp: str) -> datetime:
        return datetime.fromtimestamp(float(Decimal(timestamp)), tz=UTC)

    @classmethod
    def _as_slack_timestamp(cls, timestamp: datetime | str) -> str:
        if isinstance(timestamp, str):
            cls._datetime_from_slack_timestamp(timestamp)
            return timestamp
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return format(timestamp.timestamp(), ".6f")


async def get_slack_service() -> AsyncIterator[SlackService]:
    """Yield a request-scoped Slack service and close its HTTP client afterwards."""
    client = SlackApiClient(get_slack_settings())
    try:
        yield SlackService(client)
    finally:
        await client.aclose()

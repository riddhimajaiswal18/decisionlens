"""Markdown source connector placeholder."""

from backend.app.connectors.base import SourceConnector


class MarkdownConnector(SourceConnector):
    """Reserved implementation point for Markdown normalization."""

    async def fetch_records(self):
        raise NotImplementedError("Markdown ingestion is not implemented.")

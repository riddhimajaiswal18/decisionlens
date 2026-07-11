"""Transport contracts for source-upload endpoints."""

from uuid import UUID

from pydantic import BaseModel


class MarkdownUploadResponse(BaseModel):
    """Identifiers for an uploaded Markdown artifact accepted by the queue."""

    artifact_id: UUID
    queue_item_id: UUID
    status: str

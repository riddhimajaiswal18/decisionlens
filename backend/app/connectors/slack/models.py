"""Small normalized Slack value objects used while producing SourceRecords."""

from pydantic import BaseModel, ConfigDict


class SlackAttachment(BaseModel):
    """The limited attachment data useful to downstream raw-content processing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str | None = None
    text: str | None = None
    title_link: str | None = None
    image_url: str | None = None

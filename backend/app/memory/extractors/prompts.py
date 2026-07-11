"""Replaceable placeholder prompt templates and registry."""

from backend.app.memory.extractors.interfaces import PromptProvider
from backend.app.memory.extractors.models import ExtractionType

PromptTemplates: dict[ExtractionType, str] = {
    extraction_type: "" for extraction_type in ExtractionType
}


class PromptRegistry(PromptProvider):
    """Stores caller-supplied prompt templates without embedding them in extractors."""

    def __init__(self, templates: dict[ExtractionType, str] | None = None) -> None:
        self._templates = {**PromptTemplates, **(templates or {})}

    def get(self, extraction_type: ExtractionType) -> str:
        return self._templates[extraction_type]

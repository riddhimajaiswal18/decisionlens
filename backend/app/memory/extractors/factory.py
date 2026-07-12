"""Extraction-layer dependency injection for provider selection."""

from backend.app.memory.extractors.config import ExtractionSettings, get_extraction_settings
from backend.app.memory.extractors.interfaces import StructuredExtractionClient
from backend.app.memory.extractors.providers import DemoExtractionClient, OllamaProvider


def create_structured_extraction_client(settings: ExtractionSettings | None = None) -> StructuredExtractionClient:
    """Create the selected provider while keeping callers independent of its implementation."""
    selected = settings or get_extraction_settings()
    if selected.provider == "ollama":
        return OllamaProvider(selected)
    return DemoExtractionClient()

"""Replaceable extractor and prompt abstractions."""

from abc import ABC, abstractmethod

from backend.app.memory.extractors.models import ExtractedFact, ExtractionType
from backend.app.models import Artifact


class PromptProvider(ABC):
    """Provides replaceable prompts without coupling extraction logic to templates."""

    @abstractmethod
    def get(self, extraction_type: ExtractionType) -> str:
        raise NotImplementedError


class StructuredExtractionClient(ABC):
    """LLM transport boundary that returns validated structured extraction data."""

    @abstractmethod
    async def extract(self, *, prompt: str, artifact: Artifact, extraction_type: ExtractionType) -> list[ExtractedFact]:
        raise NotImplementedError


class InformationExtractor(ABC):
    """Extracts one category of evidence-backed facts from an Artifact."""

    extraction_type: ExtractionType

    @abstractmethod
    async def extract(self, artifact: Artifact) -> list[ExtractedFact]:
        raise NotImplementedError

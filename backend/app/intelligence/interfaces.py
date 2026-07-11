"""Plugin-style analyzer and engine contracts."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from backend.app.intelligence.models import AnalysisRequest, Insight, InsightEvidence
from backend.app.memory.supermemory.contracts import SupermemoryClient
from backend.app.memory.supermemory.models import MemorySearchResult


class IntelligenceAnalyzer(ABC):
    """A modular Supermemory-only analyzer that returns strongly typed insights."""

    name: str

    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> list[Insight]:
        raise NotImplementedError


class BaseSupermemoryAnalyzer(IntelligenceAnalyzer):
    """Shared evidence and metadata handling for analyzers that query Supermemory."""

    def __init__(self, supermemory: SupermemoryClient) -> None:
        self._supermemory = supermemory

    async def _search(self, query: str, limit: int) -> tuple[MemorySearchResult, ...]:
        return (await self._supermemory.search(query, limit=limit)).results

    @staticmethod
    def metadata(result: MemorySearchResult) -> dict[str, Any]:
        metadata = dict(result.metadata)
        encoded = metadata.get("metadata_json")
        if isinstance(encoded, str):
            try:
                decoded = json.loads(encoded)
            except json.JSONDecodeError:
                decoded = None
            if isinstance(decoded, dict):
                for key, value in decoded.items():
                    metadata.setdefault(key, value)
        return metadata

    @classmethod
    def evidence(cls, result: MemorySearchResult) -> tuple[InsightEvidence, ...]:
        metadata = cls.metadata(result)
        encoded = metadata.get("evidence_json")
        if not isinstance(encoded, str):
            return ()
        try:
            evidence = json.loads(encoded)
        except json.JSONDecodeError:
            return ()
        if not isinstance(evidence, list):
            return ()
        reconstructed: list[InsightEvidence] = []
        for source in evidence:
            if not isinstance(source, dict):
                continue
            original_snippet = cls.string_value(source.get("original_snippet")) or cls.string_value(source.get("excerpt"))
            supporting_text = cls.string_value(source.get("supporting_text")) or original_snippet
            if original_snippet is None or supporting_text is None:
                continue
            reconstructed.append(
                InsightEvidence(
                    content=supporting_text,
                    memory_id=result.id,
                    artifact_reference=cls.string_value(source.get("source_artifact")) or cls.string_value(source.get("artifact_reference")),
                    original_snippet=original_snippet,
                    source_location=cls.string_value(source.get("source_location")) or cls.string_value(source.get("location")),
                    supporting_text=supporting_text,
                    extraction_confidence=cls.extraction_confidence(result),
                    retrieval_similarity=result.similarity,
                )
            )
        return tuple(reconstructed)

    @staticmethod
    def timestamp(result: MemorySearchResult) -> datetime | None:
        metadata = BaseSupermemoryAnalyzer.metadata(result)
        raw = metadata.get("timestamp") or metadata.get("created_at") or metadata.get("updated_at")
        if not isinstance(raw, str):
            return None
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None

    @staticmethod
    def confidence(results: list[MemorySearchResult]) -> float:
        scores = [score for result in results if (score := BaseSupermemoryAnalyzer.extraction_confidence(result)) is not None]
        return sum(scores) / len(scores) if scores else 0.0

    @staticmethod
    def extraction_confidence(result: MemorySearchResult) -> float | None:
        value = BaseSupermemoryAnalyzer.metadata(result).get("confidence")
        return value if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1 else None

    @staticmethod
    def participants(result: MemorySearchResult) -> tuple[str, ...]:
        encoded = BaseSupermemoryAnalyzer.metadata(result).get("participants_json")
        if not isinstance(encoded, str):
            return ()
        try:
            participants = json.loads(encoded)
        except json.JSONDecodeError:
            return ()
        if not isinstance(participants, list):
            return ()
        return tuple(item for item in participants if isinstance(item, str) and item)

    @staticmethod
    def string_value(value: Any) -> str | None:
        return value if isinstance(value, str) and value else None


class EngineeringIntelligenceEngine(ABC):
    """Dispatches registered analyzers without coupling to source or pipeline layers."""

    @abstractmethod
    def register(self, analyzer: IntelligenceAnalyzer) -> None:
        raise NotImplementedError

    @abstractmethod
    async def analyze(self, analyzer_name: str, request: AnalysisRequest) -> list[Insight]:
        raise NotImplementedError

    @abstractmethod
    async def analyze_all(self, request: AnalysisRequest) -> dict[str, list[Insight]]:
        raise NotImplementedError

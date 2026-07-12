"""Provider implementations behind the stable StructuredExtractionClient contract."""

import json
import logging
from collections.abc import Mapping
from typing import Any

import httpx
from pydantic import ValidationError

from backend.app.memory.extractors.config import ExtractionSettings
from backend.app.memory.extractors.interfaces import StructuredExtractionClient
from backend.app.memory.extractors.models import ExtractedEvidence, ExtractedFact, ExtractionType
from backend.app.memory.extractors.prompts import ExtractionPromptBuilder
from backend.app.models import Artifact

logger = logging.getLogger(__name__)


class OllamaProvider(StructuredExtractionClient):
    """Fail-soft asynchronous Ollama implementation for structured extraction."""

    def __init__(
        self,
        settings: ExtractionSettings,
        *,
        prompt_builder: ExtractionPromptBuilder | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._prompt_builder = prompt_builder or ExtractionPromptBuilder()
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            base_url=str(settings.ollama_base_url).rstrip("/"), timeout=settings.ollama_timeout
        )

    async def extract(self, *, prompt: str, artifact: Artifact, extraction_type: ExtractionType) -> list[ExtractedFact]:
        request = self._prompt_builder.build(instruction=prompt, artifact=artifact, extraction_type=extraction_type)
        raw = await self._generate(request.system, request.user)
        facts = self._parse(raw, artifact=artifact, extraction_type=extraction_type)
        if facts is not None:
            return facts

        # A single repair request handles JSON-mode edge cases without propagating failure into EKPP.
        repair = self._prompt_builder.build_repair(original_prompt=request, invalid_output=raw)
        repaired = await self._generate(repair.system, repair.user)
        return self._parse(repaired, artifact=artifact, extraction_type=extraction_type) or []

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _generate(self, system: str, prompt: str) -> str:
        try:
            response = await self._client.post(
                "/api/generate",
                json={"model": self._settings.ollama_model, "system": system, "prompt": prompt, "format": "json", "stream": False},
            )
            if response.status_code == 429 or response.status_code >= 500:
                logger.warning("Ollama extraction unavailable: HTTP %s", response.status_code)
                return ""
            response.raise_for_status()
            payload = response.json()
            content = payload.get("response") if isinstance(payload, Mapping) else None
            if not isinstance(content, str):
                logger.warning("Ollama extraction response did not contain a string response field")
                return ""
            return content
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Ollama extraction request failed: %s", exc)
            return ""

    @staticmethod
    def _parse(raw: str, *, artifact: Artifact, extraction_type: ExtractionType) -> list[ExtractedFact] | None:
        try:
            decoded = json.loads(raw)
            rows = decoded.get("facts") if isinstance(decoded, Mapping) else None
            if not isinstance(rows, list):
                return None
            facts: list[ExtractedFact] = []
            for row in rows:
                fact = OllamaProvider._validate_fact(row, artifact=artifact, extraction_type=extraction_type)
                if fact is not None:
                    facts.append(fact)
            return facts
        except (TypeError, ValueError, ValidationError):
            return None

    @staticmethod
    def _validate_fact(row: Any, *, artifact: Artifact, extraction_type: ExtractionType) -> ExtractedFact | None:
        if not isinstance(row, Mapping) or row.get("type") != extraction_type.value:
            return None
        allowed_fact_fields = {"type", "entity", "value", "status", "participants", "reason", "evidence", "confidence", "metadata"}
        if set(row) - allowed_fact_fields:
            return None
        evidence_rows = row.get("evidence")
        if not isinstance(evidence_rows, list) or not evidence_rows:
            return None
        evidence: list[ExtractedEvidence] = []
        for item in evidence_rows:
            if not isinstance(item, Mapping) or not isinstance(item.get("excerpt"), str):
                return None
            if set(item) - {"excerpt", "location", "supporting_text"}:
                return None
            # Grounding check: no evidence is accepted unless it occurs verbatim in the artifact.
            if item["excerpt"] not in artifact.raw_content:
                return None
            evidence.append(
                ExtractedEvidence(
                    excerpt=item["excerpt"],
                    location=item.get("location") if isinstance(item.get("location"), str) else None,
                    supporting_text=item.get("supporting_text") if isinstance(item.get("supporting_text"), str) else None,
                )
            )
        participants = row.get("participants", [])
        if not isinstance(participants, list) or not all(isinstance(value, str) for value in participants):
            return None
        confidence = row.get("confidence", 0.0)
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            return None
        try:
            return ExtractedFact(
                type=extraction_type,
                entity=row.get("entity"),
                value=row.get("value") if isinstance(row.get("value"), str) or row.get("value") is None else None,
                status=row.get("status") if isinstance(row.get("status"), str) or row.get("status") is None else None,
                participants=tuple(participants),
                reason=row.get("reason") if isinstance(row.get("reason"), str) or row.get("reason") is None else None,
                evidence=tuple(evidence),
                confidence=float(confidence),
                metadata=dict(row.get("metadata", {})) if isinstance(row.get("metadata", {}), Mapping) else {},
            )
        except ValidationError:
            return None


class DemoExtractionClient(StructuredExtractionClient):
    """Deterministic fixture provider retained for tests and offline demos."""

    _prefixes = {
        "Decision:": ExtractionType.DECISION,
        "Tradeoff:": ExtractionType.TRADEOFF,
        "Alternative:": ExtractionType.ALTERNATIVE,
        "Architecture Change:": ExtractionType.ARCHITECTURE_CHANGE,
        "Open Question:": ExtractionType.OPEN_QUESTION,
        "Status:": ExtractionType.STATUS,
    }
    _known_entities = ("Supabase", "Redis", "Stripe", "PostgreSQL", "Kafka", "background jobs", "RLS", "Markdown", "ADRs", "RFCs", "session")

    async def extract(self, *, prompt: str, artifact: Artifact, extraction_type: ExtractionType) -> list[ExtractedFact]:
        facts: list[ExtractedFact] = []
        for line_number, line in enumerate((item.strip(" -\t") for item in artifact.raw_content.splitlines()), start=1):
            if not line:
                continue
            detected = next(((prefix, kind) for prefix, kind in self._prefixes.items() if prefix in line), None)
            if detected and detected[1] is extraction_type:
                prefix, _ = detected
                facts.append(self._fact(extraction_type, self._entity_for(line), line.split(prefix, 1)[1].strip(), line, line_number, artifact.author))
            if extraction_type in {ExtractionType.ENTITY, ExtractionType.TOPIC}:
                for entity in self._known_entities:
                    if entity.casefold() in line.casefold():
                        value = entity if extraction_type is ExtractionType.ENTITY else f"Discussion involving {entity}"
                        facts.append(self._fact(extraction_type, entity, value, line, line_number, artifact.author))
        return facts

    @classmethod
    def _entity_for(cls, line: str) -> str:
        return next((entity for entity in cls._known_entities if entity.casefold() in line.casefold()), "engineering platform")

    @staticmethod
    def _fact(kind: ExtractionType, entity: str, value: str, line: str, line_number: int, author: str) -> ExtractedFact:
        return ExtractedFact(
            type=kind,
            entity=entity,
            value=value,
            participants=(author,),
            evidence=(ExtractedEvidence(excerpt=line, location=f"line {line_number}", supporting_text=line),),
            confidence=0.9,
        )

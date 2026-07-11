"""Construction of strongly typed Knowledge Objects from extracted facts."""

from collections.abc import Callable

from backend.app.memory.extractors.models import ExtractedFact, ExtractionType
from backend.app.memory.knowledge_objects.interfaces import KnowledgeObjectBuilder
from backend.app.memory.knowledge_objects.models import (
    Alternative,
    ArchitectureChange,
    Confidence,
    Decision,
    Entity,
    Evidence,
    KnowledgeObject,
    OpenQuestion,
    Status,
    Topic,
    Tradeoff,
)
from backend.app.models import Artifact

_MODEL_BY_TYPE: dict[ExtractionType, type[KnowledgeObject]] = {
    ExtractionType.DECISION: Decision,
    ExtractionType.TRADEOFF: Tradeoff,
    ExtractionType.ALTERNATIVE: Alternative,
    ExtractionType.TOPIC: Topic,
    ExtractionType.ARCHITECTURE_CHANGE: ArchitectureChange,
    ExtractionType.ENTITY: Entity,
    ExtractionType.STATUS: Status,
    ExtractionType.OPEN_QUESTION: OpenQuestion,
}


class DefaultKnowledgeObjectBuilder(KnowledgeObjectBuilder):
    """Builds only facts with source evidence; null extractions produce no objects."""

    async def build(self, artifact: Artifact, facts: list[ExtractedFact]) -> list[KnowledgeObject]:
        knowledge: list[KnowledgeObject] = []
        for fact in facts:
            if fact.value is None or not fact.evidence:
                continue
            model = _MODEL_BY_TYPE[fact.type]
            knowledge.append(
                model(
                    entity=fact.entity,
                    value=fact.value,
                    evidence=tuple(
                        Evidence(
                            source_artifact=artifact.artifact_id,
                            original_snippet=item.excerpt,
                            source_location=item.location,
                            supporting_text=item.supporting_text or item.excerpt,
                        )
                        for item in fact.evidence
                    ),
                    confidence=Confidence(extraction_score=fact.confidence),
                    artifact_reference=artifact.artifact_id,
                    timestamp=artifact.timestamp,
                    participants=fact.participants or (artifact.author,),
                    status=fact.status,
                    reason=fact.reason,
                    metadata=fact.metadata,
                )
            )
        return knowledge

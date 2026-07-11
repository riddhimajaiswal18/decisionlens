"""Dependency-injected Engineering Knowledge Processing Pipeline orchestration."""

from backend.app.memory.deduplication.interfaces import DeduplicationService
from backend.app.memory.ekpp.contracts import EngineeringKnowledgeProcessingPipeline
from backend.app.memory.entity_resolution.interfaces import EntityResolver
from backend.app.memory.extractors.models import ExtractionType
from backend.app.memory.extractors.service import CompositeInformationExtractor
from backend.app.memory.knowledge_objects.interfaces import KnowledgeObjectBuilder
from backend.app.memory.knowledge_objects.models import PersistedKnowledgeObject
from backend.app.models import Artifact


class DefaultEngineeringKnowledgeProcessingPipeline(EngineeringKnowledgeProcessingPipeline):
    """Coordinates extraction, entity resolution, object building, and ID assignment."""

    def __init__(
        self,
        *,
        extractor: CompositeInformationExtractor,
        entity_resolver: EntityResolver,
        builder: KnowledgeObjectBuilder,
        deduplication: DeduplicationService,
    ) -> None:
        self._extractor = extractor
        self._entity_resolver = entity_resolver
        self._builder = builder
        self._deduplication = deduplication

    async def process(self, artifact: Artifact) -> list[PersistedKnowledgeObject]:
        facts = await self._extractor.extract(artifact)
        entity_names = list(dict.fromkeys(fact.entity for fact in facts))
        resolved = await self._entity_resolver.resolve(entity_names)
        canonical_by_entity = {item.original_name: item.canonical_name for item in resolved}
        normalized_facts = [
            fact.model_copy(
                update={
                    "entity": canonical_by_entity[fact.entity],
                    "value": canonical_by_entity[fact.entity] if fact.type is ExtractionType.ENTITY else fact.value,
                }
            )
            for fact in facts
        ]
        knowledge_objects = await self._builder.build(artifact, normalized_facts)
        return await self._deduplication.assign(knowledge_objects)

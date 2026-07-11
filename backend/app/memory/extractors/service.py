"""Category extractors and an orchestrator over the structured extraction client."""

from backend.app.memory.extractors.interfaces import InformationExtractor, PromptProvider, StructuredExtractionClient
from backend.app.memory.extractors.models import ExtractedFact, ExtractionType
from backend.app.models import Artifact


class LLMInformationExtractor(InformationExtractor):
    """Delegates one structured category extraction to an injected LLM client."""

    def __init__(self, extraction_type: ExtractionType, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        self.extraction_type = extraction_type
        self._client = client
        self._prompts = prompts

    async def extract(self, artifact: Artifact) -> list[ExtractedFact]:
        facts = await self._client.extract(
            prompt=self._prompts.get(self.extraction_type), artifact=artifact, extraction_type=self.extraction_type
        )
        return [fact for fact in facts if fact.type is self.extraction_type]


class DecisionExtractor(LLMInformationExtractor):
    """Extracts source-grounded engineering decisions."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.DECISION, client, prompts)


class TradeoffExtractor(LLMInformationExtractor):
    """Extracts source-grounded engineering tradeoffs."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.TRADEOFF, client, prompts)


class AlternativeExtractor(LLMInformationExtractor):
    """Extracts source-grounded considered alternatives."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.ALTERNATIVE, client, prompts)


class TopicExtractor(LLMInformationExtractor):
    """Extracts source-grounded engineering topics."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.TOPIC, client, prompts)


class StatusExtractor(LLMInformationExtractor):
    """Extracts source-grounded engineering status statements."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.STATUS, client, prompts)


class ArchitectureChangeExtractor(LLMInformationExtractor):
    """Extracts source-grounded architecture changes."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.ARCHITECTURE_CHANGE, client, prompts)


class EntityExtractor(LLMInformationExtractor):
    """Extracts source-grounded engineering entities."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.ENTITY, client, prompts)


class OpenQuestionExtractor(LLMInformationExtractor):
    """Extracts source-grounded unresolved engineering questions."""

    def __init__(self, client: StructuredExtractionClient, prompts: PromptProvider) -> None:
        super().__init__(ExtractionType.OPEN_QUESTION, client, prompts)


class CompositeInformationExtractor:
    """Runs independently replaceable category extractors and combines their facts."""

    def __init__(self, extractors: tuple[InformationExtractor, ...]) -> None:
        self._extractors = extractors

    async def extract(self, artifact: Artifact) -> list[ExtractedFact]:
        facts: list[ExtractedFact] = []
        for extractor in self._extractors:
            facts.extend(await extractor.extract(artifact))
        return facts

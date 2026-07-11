"""Historical-context analysis over a caller-provided Supermemory topic query."""

from collections import defaultdict

from backend.app.intelligence.interfaces import BaseSupermemoryAnalyzer
from backend.app.intelligence.models import AnalysisRequest, HistoricalContext, Insight


class HistoricalContextAnalyzer(BaseSupermemoryAnalyzer):
    """Collects prior decisions and related fact types without adding new interpretation."""

    name = "historical_context"

    async def analyze(self, request: AnalysisRequest) -> list[Insight]:
        if not request.query:
            return []
        results = list(await self._search(request.query, request.limit))
        grouped: dict[str, list[str]] = defaultdict(list)
        evidence = tuple(item for result in results for item in self.evidence(result))
        if not evidence:
            return []
        for result in results:
            fact_type = self.string_value(self.metadata(result).get("type"))
            if fact_type and result.content:
                grouped[fact_type].append(result.content)
        artifacts = tuple(sorted({item.artifact_reference for item in evidence if item.artifact_reference}))
        entities = tuple(sorted({entity for result in results if (entity := self.string_value(self.metadata(result).get("entity")))}))
        return [
            HistoricalContext(
                title=f"Historical context: {request.query}",
                summary=f"{len(evidence)} supporting memories were found for {request.query}.",
                evidence=evidence,
                confidence=self.confidence(results),
                related_artifacts=artifacts,
                related_entities=entities or (request.query,),
                topic=request.query,
                previous_decisions=tuple(grouped["decision"]),
                related_discussions=tuple(grouped["topic"]),
                tradeoffs=tuple(grouped["tradeoff"]),
                alternatives=tuple(grouped["alternative"]),
                architecture_changes=tuple(grouped["architecture_change"]),
            )
        ]

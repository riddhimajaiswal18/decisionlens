"""Deterministic technology discussion trend analysis."""

from collections import defaultdict

from backend.app.intelligence.interfaces import BaseSupermemoryAnalyzer
from backend.app.intelligence.models import AnalysisRequest, Insight, TechnologyTrend
from backend.app.memory.supermemory.models import MemorySearchResult


class TechnologyTrendAnalyzer(BaseSupermemoryAnalyzer):
    """Counts explicit technology mentions and explicit acceptance/rejection wording."""

    name = "technology_trends"

    async def analyze(self, request: AnalysisRequest) -> list[Insight]:
        results = list(await self._search(request.query or "engineering technologies", request.limit))
        grouped: dict[str, list[MemorySearchResult]] = defaultdict(list)
        for result in results:
            metadata = self.metadata(result)
            technology = self.string_value(metadata.get("entity")) or self.string_value(metadata.get("technology"))
            if technology:
                grouped[technology].append(result)
        insights: list[Insight] = []
        for technology, mentions in grouped.items():
            evidence = tuple(item for result in mentions for item in self.evidence(result))
            if not evidence:
                continue
            contents = " ".join(result.content or "" for result in mentions).casefold()
            accepted = contents.count("accepted")
            rejected = contents.count("rejected")
            deprecated = "deprecated" in contents
            artifacts = tuple(sorted({item.artifact_reference for item in evidence if item.artifact_reference}))
            insights.append(
                TechnologyTrend(
                    title=f"Technology trend: {technology}",
                    summary=f"{technology} is mentioned in {len(mentions)} stored engineering memories.",
                    evidence=evidence,
                    confidence=self.confidence(mentions),
                    related_artifacts=artifacts,
                    related_entities=(technology,),
                    technology=technology,
                    discussion_count=len(mentions),
                    accepted_count=accepted,
                    rejected_count=rejected,
                    is_new=len(mentions) == 1,
                    is_deprecated=deprecated,
                )
            )
        return insights

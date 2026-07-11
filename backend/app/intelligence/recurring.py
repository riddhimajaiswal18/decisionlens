"""Recurring engineering discussion analysis over Supermemory search results."""

from collections import defaultdict
from datetime import datetime

from backend.app.intelligence.interfaces import BaseSupermemoryAnalyzer
from backend.app.intelligence.models import AnalysisRequest, Insight, RecurringDiscussion
from backend.app.memory.supermemory.models import MemorySearchResult


class RecurringDiscussionAnalyzer(BaseSupermemoryAnalyzer):
    """Detects entities or topics represented by two or more supporting memories."""

    name = "recurring_discussions"

    async def analyze(self, request: AnalysisRequest) -> list[Insight]:
        results = list(await self._search(request.query or "engineering discussions", request.limit))
        groups: dict[str, list[MemorySearchResult]] = defaultdict(list)
        for result in results:
            topic = self._topic_for(result)
            if topic:
                groups[topic].append(result)
        insights: list[Insight] = []
        for topic, discussions in groups.items():
            if len(discussions) < 2:
                continue
            evidence = tuple(item for result in discussions for item in self.evidence(result))
            if not evidence:
                continue
            timestamps = [timestamp for result in discussions if (timestamp := self.timestamp(result)) is not None]
            metadata = self.metadata(discussions[-1])
            insights.append(
                RecurringDiscussion(
                    title=f"Recurring discussion: {topic}",
                    summary=f"{topic} appears in {len(discussions)} stored engineering discussions.",
                    evidence=evidence,
                    confidence=self.confidence(discussions),
                    related_artifacts=tuple(sorted({item.artifact_reference for item in evidence if item.artifact_reference})),
                    related_entities=(topic,),
                    topic=topic,
                    discussion_count=len(discussions),
                    status=self.string_value(metadata.get("status")),
                    last_discussed=max(timestamps) if timestamps else None,
                )
            )
        return insights

    def _topic_for(self, result: MemorySearchResult) -> str | None:
        metadata = self.metadata(result)
        return self.string_value(metadata.get("entity")) or self.string_value(metadata.get("topic")) or result.content

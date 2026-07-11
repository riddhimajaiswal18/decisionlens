"""Architecture timeline analysis over timestamped Supermemory memories."""

from backend.app.intelligence.interfaces import BaseSupermemoryAnalyzer
from backend.app.intelligence.models import AnalysisRequest, ArchitectureTimeline, Insight, TimelineEvent


class ArchitectureTimelineAnalyzer(BaseSupermemoryAnalyzer):
    """Builds chronological events only when Supermemory supplies source timestamps."""

    name = "architecture_timeline"

    async def analyze(self, request: AnalysisRequest) -> list[Insight]:
        results = list(await self._search(request.query or "architecture decisions", request.limit))
        events: list[TimelineEvent] = []
        artifacts: set[str] = set()
        entities: set[str] = set()
        for result in results:
            metadata = self.metadata(result)
            event_type = self.string_value(metadata.get("type"))
            timestamp = self.timestamp(result)
            evidence = self.evidence(result)
            if event_type not in {"decision", "architecture_change"} or timestamp is None or not evidence:
                continue
            artifacts.update(item.artifact_reference for item in evidence if item.artifact_reference)
            entity = self.string_value(metadata.get("entity"))
            if entity:
                entities.add(entity)
            events.append(
                TimelineEvent(
                    timestamp=timestamp,
                    decision=result.content,
                    reason=self.string_value(metadata.get("reason")),
                    evidence=evidence,
                    confidence=self.extraction_confidence(result) or 0.0,
                )
            )
        if not events:
            return []
        ordered = tuple(sorted(events, key=lambda event: event.timestamp))
        return [
            ArchitectureTimeline(
                title="Architecture timeline",
                summary=f"{len(ordered)} timestamped architecture events were found in Supermemory.",
                evidence=tuple(item for event in ordered for item in event.evidence),
                confidence=sum(event.confidence for event in ordered) / len(ordered),
                related_artifacts=tuple(sorted(artifacts)),
                related_entities=tuple(sorted(entities)),
                timestamp=ordered[-1].timestamp,
                events=ordered,
            )
        ]

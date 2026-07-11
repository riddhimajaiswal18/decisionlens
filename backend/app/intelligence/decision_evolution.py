"""Decision evolution analysis over stored decision and status memories."""

from backend.app.intelligence.interfaces import BaseSupermemoryAnalyzer
from backend.app.intelligence.models import AnalysisRequest, DecisionHistory, Insight, TimelineEvent


class DecisionEvolutionAnalyzer(BaseSupermemoryAnalyzer):
    """Tracks explicit, timestamped decision statements without inferring missing states."""

    name = "decision_evolution"

    async def analyze(self, request: AnalysisRequest) -> list[Insight]:
        if not request.query:
            return []
        results = list(await self._search(request.query, request.limit))
        events: list[TimelineEvent] = []
        participants: set[str] = set()
        reasons: set[str] = set()
        artifacts: set[str] = set()
        for result in results:
            metadata = self.metadata(result)
            if self.string_value(metadata.get("type")) not in {"decision", "status"}:
                continue
            timestamp = self.timestamp(result)
            evidence = self.evidence(result)
            if timestamp is None or not evidence:
                continue
            reason = self.string_value(metadata.get("reason"))
            participants.update(self.participants(result))
            if reason:
                reasons.add(reason)
            artifacts.update(item.artifact_reference for item in evidence if item.artifact_reference)
            events.append(TimelineEvent(timestamp=timestamp, decision=result.content, reason=reason, evidence=evidence, confidence=self.extraction_confidence(result) or 0.0))
        if not events:
            return []
        history = tuple(sorted(events, key=lambda event: event.timestamp))
        return [
            DecisionHistory(
                title=f"Decision evolution: {request.query}",
                summary=f"{len(history)} timestamped decision or status events relate to {request.query}.",
                evidence=tuple(item for event in history for item in event.evidence),
                confidence=sum(event.confidence for event in history) / len(history),
                related_artifacts=tuple(sorted(artifacts)),
                related_entities=(request.query,),
                timestamp=history[-1].timestamp,
                decision=request.query,
                history=history,
                reasons=tuple(sorted(reasons)),
                participants=tuple(sorted(participants)),
                timestamps=tuple(event.timestamp for event in history),
            )
        ]

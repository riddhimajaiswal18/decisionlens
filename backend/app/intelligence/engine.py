"""Plugin-style orchestration for Supermemory-backed intelligence analyzers."""

from backend.app.intelligence.decision_evolution import DecisionEvolutionAnalyzer
from backend.app.intelligence.exceptions import AnalyzerNotFoundError, AnalyzerRegistrationError
from backend.app.intelligence.historical_context import HistoricalContextAnalyzer
from backend.app.intelligence.interfaces import EngineeringIntelligenceEngine, IntelligenceAnalyzer
from backend.app.intelligence.models import AnalysisRequest, Insight
from backend.app.intelligence.recurring import RecurringDiscussionAnalyzer
from backend.app.intelligence.technology_trends import TechnologyTrendAnalyzer
from backend.app.intelligence.timeline import ArchitectureTimelineAnalyzer
from backend.app.memory.supermemory.contracts import SupermemoryClient


class DefaultEngineeringIntelligenceEngine(EngineeringIntelligenceEngine):
    """Dispatches registered independent analyzers; it has no source or EKPP dependencies."""

    def __init__(self, analyzers: tuple[IntelligenceAnalyzer, ...] = ()) -> None:
        self._analyzers: dict[str, IntelligenceAnalyzer] = {}
        for analyzer in analyzers:
            self.register(analyzer)

    def register(self, analyzer: IntelligenceAnalyzer) -> None:
        if not analyzer.name:
            raise AnalyzerRegistrationError("Analyzer name is required.")
        if analyzer.name in self._analyzers:
            raise AnalyzerRegistrationError(f"Analyzer is already registered: {analyzer.name}")
        self._analyzers[analyzer.name] = analyzer

    async def analyze(self, analyzer_name: str, request: AnalysisRequest) -> list[Insight]:
        analyzer = self._analyzers.get(analyzer_name)
        if analyzer is None:
            raise AnalyzerNotFoundError(f"Analyzer is not registered: {analyzer_name}")
        return await analyzer.analyze(request)

    async def analyze_all(self, request: AnalysisRequest) -> dict[str, list[Insight]]:
        return {name: await analyzer.analyze(request) for name, analyzer in self._analyzers.items()}


def create_default_intelligence_engine(supermemory: SupermemoryClient) -> DefaultEngineeringIntelligenceEngine:
    """Compose the default analyzer plugin set from the only permitted dependency."""
    return DefaultEngineeringIntelligenceEngine(
        analyzers=(
            RecurringDiscussionAnalyzer(supermemory),
            ArchitectureTimelineAnalyzer(supermemory),
            DecisionEvolutionAnalyzer(supermemory),
            TechnologyTrendAnalyzer(supermemory),
            HistoricalContextAnalyzer(supermemory),
        )
    )

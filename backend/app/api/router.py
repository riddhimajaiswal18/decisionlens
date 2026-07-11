"""Thin HTTP adapters over the existing ingestion and intelligence services."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.intelligence.models import (
    AnalysisRequest,
    ArchitectureTimeline,
    DecisionHistory,
    RecurringDiscussion,
    TechnologyTrend,
)
from backend.app.models import ArtifactEventType, ArtifactSource, SourceRecord
from backend.app.schemas import HealthResponse, MarkdownUploadResponse, QueryRequest, QueryResponse
from backend.app.services.dependencies import (
    ArtifactQueueDependency,
    IngestionEngineDependency,
    IntelligenceEngineDependency,
)

api_router = APIRouter()


@api_router.get("/health", response_model=HealthResponse, tags=["system"], summary="Liveness check")
async def health_check() -> HealthResponse:
    """Expose application liveness without invoking downstream services."""
    return HealthResponse(status="ok")


@api_router.post("/query", response_model=QueryResponse, tags=["intelligence"], summary="Query engineering intelligence")
async def query_engineering_intelligence(
    request: QueryRequest,
    intelligence: IntelligenceEngineDependency,
) -> QueryResponse:
    """Dispatch a caller query to the registered Supermemory-backed analyzers."""
    results = await intelligence.analyze_all(AnalysisRequest(query=request.query, limit=request.filters.limit))
    return QueryResponse(results=results)


@api_router.get("/timeline", response_model=list[ArchitectureTimeline], tags=["intelligence"], summary="Architecture timeline")
async def architecture_timeline(intelligence: IntelligenceEngineDependency) -> list[ArchitectureTimeline]:
    """Return the existing architecture-timeline analyzer output."""
    return await intelligence.analyze("architecture_timeline", AnalysisRequest())


@api_router.get(
    "/recurring-discussions",
    response_model=list[RecurringDiscussion],
    tags=["intelligence"],
    summary="Recurring engineering discussions",
)
async def recurring_discussions(intelligence: IntelligenceEngineDependency) -> list[RecurringDiscussion]:
    """Return the existing recurring-discussion analyzer output."""
    return await intelligence.analyze("recurring_discussions", AnalysisRequest())


@api_router.get(
    "/technology-trends",
    response_model=list[TechnologyTrend],
    tags=["intelligence"],
    summary="Technology trends",
)
async def technology_trends(intelligence: IntelligenceEngineDependency) -> list[TechnologyTrend]:
    """Return the existing technology-trend analyzer output."""
    return await intelligence.analyze("technology_trends", AnalysisRequest())


@api_router.get(
    "/decision-history/{entity}",
    response_model=list[DecisionHistory],
    tags=["intelligence"],
    summary="Decision history for an entity",
)
async def decision_history(entity: str, intelligence: IntelligenceEngineDependency) -> list[DecisionHistory]:
    """Return the existing decision-evolution analyzer output for an entity."""
    return await intelligence.analyze("decision_evolution", AnalysisRequest(query=entity))


@api_router.post(
    "/upload/markdown",
    response_model=MarkdownUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["ingestion"],
    summary="Upload a Markdown artifact",
)
async def upload_markdown(
    file: Annotated[UploadFile, File(description="A UTF-8 .md or .mdx file")],
    ingestion: IngestionEngineDependency,
    queue: ArtifactQueueDependency,
) -> MarkdownUploadResponse:
    """Adapt an uploaded Markdown file into the existing ingestion-engine and queue contracts."""
    filename = file.filename or ""
    if Path(filename).suffix.lower() not in {".md", ".mdx"}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="A .md or .mdx file is required.")
    try:
        content = (await file.read()).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Markdown must be UTF-8 encoded.") from exc

    artifact = await ingestion.ingest(
        SourceRecord(
            source=ArtifactSource.MARKDOWN,
            source_id=filename,
            event_type=ArtifactEventType.MARKDOWN,
            timestamp=datetime.now(UTC),
            author="upload",
            title=filename,
            raw_content=content,
            metadata={"filename": filename, "content_type": file.content_type or ""},
        )
    )
    item = await queue.enqueue(artifact)
    return MarkdownUploadResponse(
        artifact_id=artifact.artifact_id,
        queue_item_id=item.item_id,
        status=item.status.value,
    )

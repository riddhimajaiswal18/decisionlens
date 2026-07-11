"""Transport contracts for Intelligence Engine query endpoints."""

from pydantic import BaseModel, ConfigDict, Field

from backend.app.intelligence.models import Insight


class QueryFilters(BaseModel):
    """The existing Intelligence Engine retrieval scope exposed to callers."""

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=100, ge=1, le=500)


class QueryRequest(BaseModel):
    """Caller query and retrieval scope accepted by the API boundary."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    filters: QueryFilters = Field(default_factory=QueryFilters)


class QueryResponse(BaseModel):
    """Insights grouped by their registered analyzer name."""

    results: dict[str, list[Insight]]

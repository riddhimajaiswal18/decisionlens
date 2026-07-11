"""Health endpoint response schema placeholder."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str

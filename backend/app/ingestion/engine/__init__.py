"""Artifact creation engine and its dependency-injection boundary."""

from backend.app.ingestion.engine.engine import DefaultIngestionEngine, get_ingestion_engine
from backend.app.ingestion.engine.interfaces import IngestionEngine

__all__ = ["DefaultIngestionEngine", "IngestionEngine", "get_ingestion_engine"]

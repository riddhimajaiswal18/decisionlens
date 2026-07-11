"""Backward-compatible import for the ingestion-buffer interface."""

from backend.app.ingestion.buffer.interfaces import IngestionBuffer

SlackIngestionBuffer = IngestionBuffer

__all__ = ["SlackIngestionBuffer"]

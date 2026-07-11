"""Backward-compatible import for the Artifact Queue interface."""

from backend.app.ingestion.queue.interfaces import ArtifactQueue

__all__ = ["ArtifactQueue"]

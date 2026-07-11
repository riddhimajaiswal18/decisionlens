"""Backward-compatible deterministic custom-ID contract."""

from backend.app.memory.deduplication.interfaces import CustomIdGenerator

KnowledgeObjectDeduplicator = CustomIdGenerator

__all__ = ["KnowledgeObjectDeduplicator"]

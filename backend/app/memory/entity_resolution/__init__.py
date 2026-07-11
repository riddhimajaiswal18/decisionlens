"""Two-stage entity resolution components."""

from backend.app.memory.entity_resolution.interfaces import EntityResolver
from backend.app.memory.entity_resolution.service import DefaultEntityResolver

__all__ = ["DefaultEntityResolver", "EntityResolver"]

"""Mapping from DecisionLens contracts to Supermemory document payloads."""

import json
from typing import Any

from backend.app.memory.knowledge_objects.models import PersistedKnowledgeObject
from backend.app.memory.supermemory.exceptions import SupermemorySerializationError
from backend.app.memory.supermemory.interfaces import SupermemorySerializer
from backend.app.models import Artifact


class DefaultSupermemorySerializer(SupermemorySerializer):
    """Maps explicit Knowledge Object fields to a persistence-safe document contract."""

    def artifact_document(self, artifact: Artifact, *, container_tag: str) -> dict[str, Any]:
        return {
            "content": artifact.raw_content,
            "containerTag": container_tag,
            "customId": f"artifact:{artifact.artifact_id}",
            "taskType": "memory",
            "metadata": {
                "source": artifact.source.value,
                "source_id": artifact.source_id,
                "event_type": artifact.event_type.value,
                "timestamp": artifact.timestamp.isoformat(),
                "author": artifact.author,
                "title": artifact.title or "",
                "processing_status": artifact.processing_status.value,
                "metadata_json": self._json(artifact.metadata),
            },
        }

    def knowledge_document(self, knowledge_object: PersistedKnowledgeObject, *, container_tag: str) -> dict[str, Any]:
        if not knowledge_object.custom_id:
            raise SupermemorySerializationError("Persisted Knowledge Object requires a deterministic custom_id.")
        return {
            "content": knowledge_object.value,
            "containerTag": container_tag,
            "customId": knowledge_object.custom_id,
            "taskType": "memory",
            "metadata": {
                "knowledge_id": str(knowledge_object.knowledge_id),
                "type": knowledge_object.type,
                "entity": knowledge_object.entity,
                "status": knowledge_object.status or "",
                "timestamp": knowledge_object.timestamp.isoformat(),
                "participants_json": self._json(knowledge_object.participants),
                "reason": knowledge_object.reason or "",
                "artifact_reference": str(knowledge_object.artifact_reference),
                "confidence": knowledge_object.confidence.extraction_score,
                "evidence_json": self._json([item.model_dump(mode="json") for item in knowledge_object.evidence]),
                "metadata_json": self._json(knowledge_object.metadata),
            },
        }

    @staticmethod
    def _json(value: Any) -> str:
        try:
            return json.dumps(value, separators=(",", ":"), sort_keys=True, default=str)
        except (TypeError, ValueError) as exc:
            raise SupermemorySerializationError("Metadata is not JSON-serializable.") from exc

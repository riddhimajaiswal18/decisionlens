"""Retrying asynchronous Supermemory Local client with a high-level persistence API."""

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from backend.app.memory.knowledge_objects.models import PersistedKnowledgeObject
from backend.app.memory.supermemory.config import SupermemorySettings, get_supermemory_settings
from backend.app.memory.supermemory.contracts import SupermemoryClient
from backend.app.memory.supermemory.exceptions import (
    SupermemoryAuthenticationError,
    SupermemoryError,
    SupermemoryRequestError,
    SupermemoryUnavailableError,
)
from backend.app.memory.supermemory.interfaces import SupermemorySerializer
from backend.app.memory.supermemory.models import MemorySearchResponse, MemorySearchResult, StorageResult
from backend.app.memory.supermemory.serializer import DefaultSupermemorySerializer
from backend.app.models import Artifact

logger = logging.getLogger(__name__)


class HttpSupermemoryClient(SupermemoryClient):
    """Stores DecisionLens contracts with retry, timeout, backoff, and typed errors."""

    def __init__(
        self,
        settings: SupermemorySettings,
        *,
        serializer: SupermemorySerializer | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._serializer = serializer or DefaultSupermemorySerializer()
        self._owns_client = http_client is None
        headers = {"Content-Type": "application/json"}
        if settings.api_key is not None:
            headers["Authorization"] = f"Bearer {settings.api_key.get_secret_value()}"
        self._client = http_client or httpx.AsyncClient(
            base_url=str(settings.base_url).rstrip("/"), timeout=settings.timeout_seconds, headers=headers
        )

    async def store_artifact(self, artifact: Artifact) -> StorageResult:
        document = self._serializer.artifact_document(artifact, container_tag=self._settings.container_tag)
        return (await self._store_documents([document]))[0]

    async def store_knowledge_object(self, knowledge_object: PersistedKnowledgeObject) -> StorageResult:
        document = self._serializer.knowledge_document(knowledge_object, container_tag=self._settings.container_tag)
        return (await self._store_documents([document]))[0]

    async def batch_store(self, knowledge_objects: list[PersistedKnowledgeObject]) -> list[StorageResult]:
        documents = [self._serializer.knowledge_document(item, container_tag=self._settings.container_tag) for item in knowledge_objects]
        results: list[StorageResult] = []
        for start in range(0, len(documents), self._settings.batch_size):
            results.extend(await self._store_documents(documents[start : start + self._settings.batch_size]))
        return results

    async def search(self, query: str, *, limit: int = 10) -> MemorySearchResponse:
        payload = await self._request("POST", self._settings.search_path, json={"q": query, "containerTag": self._settings.container_tag, "limit": limit})
        results = tuple(
            MemorySearchResult(
                id=item.get("id") or item.get("documentId"),
                content=item.get("memory") or item.get("chunk") or item.get("content"),
                similarity=item.get("similarity") or item.get("score"),
                metadata=item.get("metadata") or {},
            )
            for item in payload.get("results", [])
        )
        return MemorySearchResponse(results=results, total=int(payload.get("total", len(results))), timing_ms=payload.get("timing"))

    async def health_check(self) -> bool:
        try:
            await self._request("GET", self._settings.health_path)
            return True
        except SupermemoryError:
            return False

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _store_documents(self, documents: list[dict[str, Any]]) -> list[StorageResult]:
        payload = await self._request("POST", self._settings.document_batch_path, json={"documents": documents})
        response_results = payload.get("results", [])
        results: list[StorageResult] = []
        for index, document in enumerate(documents):
            response = response_results[index] if index < len(response_results) else {}
            results.append(
                StorageResult(
                    custom_id=document["customId"],
                    remote_id=response.get("id"),
                    status=response.get("status"),
                    error=response.get("error"),
                )
            )
        return results

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        for attempt in range(self._settings.max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
            except httpx.HTTPError as exc:
                if attempt == self._settings.max_retries:
                    raise SupermemoryUnavailableError("Supermemory connection failed after retries.") from exc
                await self._backoff(attempt, "transport")
                continue
            if response.status_code in {401, 403}:
                raise SupermemoryAuthenticationError("Supermemory authentication was rejected.")
            if response.status_code == 429 or response.status_code >= 500:
                if attempt == self._settings.max_retries:
                    raise SupermemoryUnavailableError(f"Supermemory unavailable: HTTP {response.status_code}.")
                await self._backoff(attempt, f"HTTP {response.status_code}")
                continue
            if response.is_error:
                raise SupermemoryRequestError(f"Supermemory rejected request: HTTP {response.status_code}.")
            try:
                return response.json()
            except ValueError as exc:
                raise SupermemoryRequestError("Supermemory returned invalid JSON.") from exc
        raise SupermemoryUnavailableError("Supermemory retry loop exited unexpectedly.")

    async def _backoff(self, attempt: int, reason: str) -> None:
        delay = self._settings.retry_base_seconds * (2**attempt)
        logger.warning("Retrying Supermemory request after %s in %.2fs", reason, delay)
        await asyncio.sleep(delay)


async def get_supermemory_client() -> AsyncIterator[SupermemoryClient]:
    """Yield a request-scoped client through dependency injection."""
    client = HttpSupermemoryClient(get_supermemory_settings())
    try:
        yield client
    finally:
        await client.aclose()

"""Thin asynchronous HTTP client for the GitHub REST API."""

from typing import Any

import httpx

from backend.app.connectors.github.config import GitHubConnectorSettings
from backend.app.connectors.github.exceptions import (
    GitHubApiError,
    GitHubAuthenticationError,
    GitHubResourceNotFoundError,
)


class GitHubApiClient:
    """Owns authenticated requests; it intentionally exposes no domain behavior."""

    def __init__(self, settings: GitHubConnectorSettings, client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=str(settings.api_base_url).rstrip("/"),
            timeout=settings.timeout_seconds,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {settings.token.get_secret_value()}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    async def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Fetch and decode a JSON response, mapping HTTP failures to connector errors."""
        try:
            response = await self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 403}:
                raise GitHubAuthenticationError("GitHub authentication was rejected.") from exc
            if exc.response.status_code == 404:
                raise GitHubResourceNotFoundError(f"GitHub resource not found: {path}") from exc
            raise GitHubApiError(f"GitHub request failed with status {exc.response.status_code}.") from exc
        except httpx.HTTPError as exc:
            raise GitHubApiError("GitHub request could not be completed.") from exc
        return response.json()

    async def aclose(self) -> None:
        """Close the internally-created HTTP client."""
        if self._owns_client:
            await self._client.aclose()

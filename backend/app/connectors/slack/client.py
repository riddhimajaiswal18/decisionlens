"""Thin asynchronous HTTP client for Slack's Web API."""

from typing import Any

import httpx

from backend.app.connectors.slack.config import SlackConnectorSettings
from backend.app.connectors.slack.exceptions import (
    SlackApiError,
    SlackAuthenticationError,
    SlackRateLimitError,
)

_AUTHENTICATION_ERRORS = frozenset({"invalid_auth", "not_authed", "token_revoked", "account_inactive"})


class SlackApiClient:
    """Owns authenticated Slack HTTP calls and maps transport errors."""

    def __init__(self, settings: SlackConnectorSettings, client: httpx.AsyncClient | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=str(settings.api_base_url).rstrip("/"),
            timeout=settings.timeout_seconds,
            headers={"Authorization": f"Bearer {settings.bot_token.get_secret_value()}"},
        )

    async def get_json(self, method: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call a Slack API method and return its successful JSON payload."""
        try:
            response = await self._client.get(method, params=params)
        except httpx.HTTPError as exc:
            raise SlackApiError("Slack request could not be completed.") from exc

        if response.status_code == 429:
            retry_after = self._retry_after(response)
            raise SlackRateLimitError(retry_after)
        if response.status_code in {401, 403}:
            raise SlackAuthenticationError("Slack authentication was rejected.")
        if response.is_error:
            raise SlackApiError(f"Slack request failed with status {response.status_code}.", status_code=response.status_code)

        try:
            payload = response.json()
        except ValueError as exc:
            raise SlackApiError("Slack returned an invalid JSON response.", status_code=response.status_code) from exc

        if not payload.get("ok", False):
            error = str(payload.get("error", "unknown_error"))
            if error in _AUTHENTICATION_ERRORS:
                raise SlackAuthenticationError(f"Slack authentication failed: {error}.")
            retry_after = self._retry_after(response) if error == "ratelimited" else None
            if error == "ratelimited":
                raise SlackRateLimitError(retry_after)
            raise SlackApiError(f"Slack API error: {error}.", status_code=response.status_code)
        return payload

    async def aclose(self) -> None:
        """Close an internally-created HTTP client."""
        if self._owns_client:
            await self._client.aclose()

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        value = response.headers.get("Retry-After")
        try:
            return float(value) if value is not None else None
        except ValueError:
            return None

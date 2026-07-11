"""Retry-aware errors raised by the Slack connector."""


class SlackConnectorError(RuntimeError):
    """Base error for failures communicating with Slack."""


class SlackApiError(SlackConnectorError):
    """A Slack request failure with information suitable for retry policies."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after
        self.retryable = status_code is None or status_code == 429 or status_code >= 500


class SlackAuthenticationError(SlackApiError):
    """Slack rejected the configured bot token; retrying will not resolve it."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=401)
        self.retryable = False


class SlackRateLimitError(SlackApiError):
    """Slack rate-limited the request and supplied an optional retry delay."""

    def __init__(self, retry_after: float | None) -> None:
        super().__init__("Slack rate limit exceeded.", status_code=429, retry_after=retry_after)

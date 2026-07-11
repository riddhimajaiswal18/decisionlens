"""Typed Supermemory persistence errors."""


class SupermemoryError(RuntimeError):
    """Base error for Supermemory persistence failures."""


class SupermemoryAuthenticationError(SupermemoryError):
    """Authentication is invalid and retrying will not resolve the failure."""


class SupermemoryUnavailableError(SupermemoryError):
    """Service or transport is temporarily unavailable and may be retried."""


class SupermemoryRequestError(SupermemoryError):
    """The service rejected a non-retryable request."""


class SupermemorySerializationError(SupermemoryError):
    """A DecisionLens object could not be represented by the memory contract."""

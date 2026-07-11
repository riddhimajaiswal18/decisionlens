"""Typed errors for analyzer registration and execution."""


class IntelligenceError(RuntimeError):
    """Base error raised by the Engineering Intelligence Engine."""


class AnalyzerRegistrationError(IntelligenceError):
    """Raised when an analyzer name is missing or registered more than once."""


class AnalyzerNotFoundError(IntelligenceError):
    """Raised when a caller requests an analyzer that has not been registered."""

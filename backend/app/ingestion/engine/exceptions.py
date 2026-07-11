"""Structured errors raised while constructing canonical Artifacts."""


class IngestionEngineError(ValueError):
    """Base structured error for invalid ingestion inputs."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


class UnsupportedInputError(IngestionEngineError):
    """Raised when no registered builder accepts an ingestion input."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="unsupported_input")


class RequiredFieldError(IngestionEngineError):
    """Raised when a required normalized value is missing or empty."""

    def __init__(self, field_name: str) -> None:
        super().__init__(f"Required field is missing or empty: {field_name}.", code="required_field")
        self.field_name = field_name


class TimestampValidationError(IngestionEngineError):
    """Raised when an input timestamp is not timezone-aware or is inconsistent."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="invalid_timestamp")


class MetadataValidationError(IngestionEngineError):
    """Raised when input metadata is not a dictionary suitable for an Artifact."""

    def __init__(self) -> None:
        super().__init__("Metadata must be a dictionary.", code="invalid_metadata")

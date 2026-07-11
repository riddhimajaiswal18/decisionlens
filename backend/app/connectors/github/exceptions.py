"""Connector-specific GitHub API errors."""


class GitHubConnectorError(RuntimeError):
    """Base exception raised for GitHub connector failures."""


class GitHubAuthenticationError(GitHubConnectorError):
    """Raised when GitHub rejects the configured personal access token."""


class GitHubResourceNotFoundError(GitHubConnectorError):
    """Raised when a requested GitHub repository resource does not exist."""


class GitHubApiError(GitHubConnectorError):
    """Raised when GitHub returns an unexpected API response."""

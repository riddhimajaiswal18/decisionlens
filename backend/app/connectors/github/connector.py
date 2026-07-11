"""Public GitHub connector facade."""

from collections.abc import AsyncIterator

from backend.app.connectors.github.models import (
    GitHubCommit,
    GitHubMarkdownDocument,
    GitHubPullRequest,
    GitHubPullRequestComment,
    GitHubReadme,
)
from backend.app.connectors.github.service import GitHubService, get_github_service


class GitHubConnector:
    """Fetch normalized engineering data from a GitHub repository.

    This facade deliberately has no knowledge of artifacts, queues, LLMs, or storage.
    """

    def __init__(self, service: GitHubService) -> None:
        self._service = service

    async def fetch_readme(self, repository: str) -> GitHubReadme:
        return await self._service.fetch_readme(repository)

    async def fetch_pull_requests(
        self, repository: str, *, state: str = "open"
    ) -> list[GitHubPullRequest]:
        return await self._service.fetch_pull_requests(repository, state=state)

    async def fetch_pull_request_comments(
        self, repository: str, pull_number: int
    ) -> list[GitHubPullRequestComment]:
        return await self._service.fetch_pull_request_comments(repository, pull_number)

    async def fetch_commits(self, repository: str, *, ref: str | None = None) -> list[GitHubCommit]:
        return await self._service.fetch_commits(repository, ref=ref)

    async def fetch_markdown_documents(self, repository: str, *, ref: str | None = None) -> list[GitHubMarkdownDocument]:
        return await self._service.fetch_markdown_documents(repository, ref=ref)


async def get_github_connector() -> AsyncIterator[GitHubConnector]:
    """Yield a connector with a request-scoped GitHub HTTP client."""
    async for service in get_github_service():
        yield GitHubConnector(service)

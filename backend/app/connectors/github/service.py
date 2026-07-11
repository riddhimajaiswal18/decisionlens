"""GitHub API operations and normalization into connector source models."""

import base64
from collections.abc import AsyncIterator
from typing import Any

from backend.app.connectors.github.client import GitHubApiClient
from backend.app.connectors.github.config import get_github_settings
from backend.app.connectors.github.models import (
    GitHubCommit,
    GitHubMarkdownDocument,
    GitHubPullRequest,
    GitHubPullRequestComment,
    GitHubReadme,
)


class GitHubService:
    """Retrieves GitHub engineering data without creating downstream objects."""

    def __init__(self, client: GitHubApiClient) -> None:
        self._client = client

    async def fetch_readme(self, repository: str) -> GitHubReadme:
        data = await self._client.get_json(f"/repos/{repository}/readme")
        return self._readme_from_response(repository, data)

    async def fetch_pull_requests(self, repository: str, *, state: str = "open") -> list[GitHubPullRequest]:
        data = await self._client.get_json(f"/repos/{repository}/pulls", params={"state": state, "per_page": 100})
        return [self._pull_request_from_response(repository, item) for item in data]

    async def fetch_pull_request_comments(self, repository: str, pull_number: int) -> list[GitHubPullRequestComment]:
        data = await self._client.get_json(
            f"/repos/{repository}/pulls/{pull_number}/comments", params={"per_page": 100}
        )
        return [self._pull_request_comment_from_response(repository, pull_number, item) for item in data]

    async def fetch_commits(self, repository: str, *, ref: str | None = None) -> list[GitHubCommit]:
        params: dict[str, Any] = {"per_page": 100}
        if ref is not None:
            params["sha"] = ref
        data = await self._client.get_json(f"/repos/{repository}/commits", params=params)
        return [self._commit_from_response(repository, item) for item in data]

    async def fetch_markdown_documents(self, repository: str, *, ref: str | None = None) -> list[GitHubMarkdownDocument]:
        params: dict[str, Any] = {"recursive": "1"}
        if ref is not None:
            params["ref"] = ref
        tree = await self._client.get_json(f"/repos/{repository}/git/trees/{ref or 'HEAD'}", params=params)
        markdown_paths = [item["path"] for item in tree.get("tree", []) if item.get("type") == "blob" and item.get("path", "").lower().endswith((".md", ".mdx"))]
        documents: list[GitHubMarkdownDocument] = []
        for path in markdown_paths:
            contents = await self._client.get_json(f"/repos/{repository}/contents/{path}", params={"ref": ref} if ref else None)
            documents.append(self._markdown_document_from_response(repository, contents))
        return documents

    @staticmethod
    def _decode_content(data: dict[str, Any]) -> str:
        encoded = data.get("content", "").replace("\n", "")
        return base64.b64decode(encoded).decode("utf-8")

    @classmethod
    def _readme_from_response(cls, repository: str, data: dict[str, Any]) -> GitHubReadme:
        return GitHubReadme(repository=repository, path=data["path"], name=data["name"], content=cls._decode_content(data), sha=data["sha"], html_url=data.get("html_url"), download_url=data.get("download_url"))

    @classmethod
    def _markdown_document_from_response(cls, repository: str, data: dict[str, Any]) -> GitHubMarkdownDocument:
        return GitHubMarkdownDocument(repository=repository, path=data["path"], name=data["name"], content=cls._decode_content(data), sha=data["sha"], html_url=data.get("html_url"), download_url=data.get("download_url"))

    @staticmethod
    def _pull_request_from_response(repository: str, data: dict[str, Any]) -> GitHubPullRequest:
        return GitHubPullRequest(repository=repository, number=data["number"], title=data["title"], body=data.get("body"), state=data["state"], author_login=data.get("user", {}).get("login"), api_url=data["url"], html_url=data["html_url"], created_at=data["created_at"], updated_at=data["updated_at"], closed_at=data.get("closed_at"), merged_at=data.get("merged_at"), base_ref=data["base"]["ref"], head_ref=data["head"]["ref"], labels=[label["name"] for label in data.get("labels", [])])

    @staticmethod
    def _pull_request_comment_from_response(repository: str, pull_number: int, data: dict[str, Any]) -> GitHubPullRequestComment:
        return GitHubPullRequestComment(repository=repository, pull_number=pull_number, id=data["id"], body=data["body"], author_login=data.get("user", {}).get("login"), api_url=data["url"], html_url=data["html_url"], created_at=data["created_at"], updated_at=data["updated_at"], path=data.get("path"), commit_id=data.get("commit_id"))

    @staticmethod
    def _commit_from_response(repository: str, data: dict[str, Any]) -> GitHubCommit:
        commit = data["commit"]
        author = commit.get("author") or {}
        committer = commit.get("committer") or {}
        return GitHubCommit(repository=repository, sha=data["sha"], message=commit["message"], author_name=author.get("name"), author_email=author.get("email"), authored_at=author.get("date"), committer_name=committer.get("name"), committed_at=committer.get("date"), api_url=data["url"], html_url=data["html_url"])


async def get_github_service() -> AsyncIterator[GitHubService]:
    """Yield a request-scoped service and release its HTTP resources afterwards."""
    client = GitHubApiClient(get_github_settings())
    try:
        yield GitHubService(client)
    finally:
        await client.aclose()

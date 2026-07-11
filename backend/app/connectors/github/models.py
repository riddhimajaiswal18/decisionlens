"""Normalized source models returned by the GitHub connector."""

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class GitHubReadme(BaseModel):
    repository: str
    path: str
    name: str
    content: str
    sha: str
    html_url: HttpUrl | None = None
    download_url: HttpUrl | None = None


class GitHubMarkdownDocument(BaseModel):
    repository: str
    path: str
    name: str
    content: str
    sha: str
    html_url: HttpUrl | None = None
    download_url: HttpUrl | None = None


class GitHubPullRequest(BaseModel):
    repository: str
    number: int
    title: str
    body: str | None = None
    state: str
    author_login: str | None = None
    api_url: HttpUrl
    html_url: HttpUrl
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    merged_at: datetime | None = None
    base_ref: str
    head_ref: str
    labels: list[str]


class GitHubPullRequestComment(BaseModel):
    repository: str
    pull_number: int
    id: int
    body: str
    author_login: str | None = None
    api_url: HttpUrl
    html_url: HttpUrl
    created_at: datetime
    updated_at: datetime
    path: str | None = None
    commit_id: str | None = None


class GitHubCommit(BaseModel):
    repository: str
    sha: str
    message: str
    author_name: str | None = None
    author_email: str | None = None
    authored_at: datetime | None = None
    committer_name: str | None = None
    committed_at: datetime | None = None
    api_url: HttpUrl
    html_url: HttpUrl

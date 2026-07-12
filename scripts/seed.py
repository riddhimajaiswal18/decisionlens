"""Seed DecisionLens with the repository's deterministic engineering demo corpus.

The command intentionally composes the application contracts in their production
order: connector -> ingestion buffer -> ingestion engine -> queue -> EKPP ->
Supermemory.  Fixture adapters live here so the frozen backend remains unchanged.
"""

from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.connectors.github.connector import GitHubConnector
from backend.app.connectors.github.models import GitHubCommit, GitHubPullRequest, GitHubPullRequestComment, GitHubReadme
from backend.app.connectors.slack.connector import SlackConnector
from backend.app.ingestion.buffer.manager import IngestionBufferManager
from backend.app.ingestion.buffer.models import BufferConfig
from backend.app.ingestion.engine.engine import DefaultIngestionEngine
from backend.app.ingestion.queue.manager import InMemoryArtifactQueue
from backend.app.memory.deduplication.service import DefaultDeduplicationService
from backend.app.memory.ekpp.engine import DefaultEngineeringKnowledgeProcessingPipeline
from backend.app.memory.entity_resolution.interfaces import EntityCanonicalizer
from backend.app.memory.entity_resolution.service import DefaultEntityResolver
from backend.app.memory.extractors.config import get_extraction_settings
from backend.app.memory.extractors.factory import create_structured_extraction_client
from backend.app.memory.extractors.interfaces import PromptProvider
from backend.app.memory.extractors.models import ExtractionType
from backend.app.memory.extractors.prompts import PromptRegistry, PromptTemplates
from backend.app.memory.extractors.service import (
    AlternativeExtractor, ArchitectureChangeExtractor, CompositeInformationExtractor,
    DecisionExtractor, EntityExtractor, OpenQuestionExtractor,
    StatusExtractor, TopicExtractor, TradeoffExtractor,
)
from backend.app.memory.knowledge_objects.builder import DefaultKnowledgeObjectBuilder
from backend.app.memory.supermemory.client import HttpSupermemoryClient
from backend.app.memory.supermemory.config import get_supermemory_settings
from backend.app.models import ArtifactEventType, ArtifactSource, SourceRecord

DATA = ROOT / "sample-data"
REPOSITORY = "atlas/engineering-platform"


class FixtureGitHubService:
    """File-backed stand-in for the GitHub service used only by this demo command."""

    async def fetch_readme(self, repository: str) -> GitHubReadme:
        return GitHubReadme(repository=repository, path="README.md", name="README.md", content=(DATA / "github" / "README.md").read_text(encoding="utf-8"), sha="demo-readme")

    async def fetch_pull_requests(self, repository: str, *, state: str = "open") -> list[GitHubPullRequest]:
        return [GitHubPullRequest(repository=repository, number=int(row["id"].split("-")[1]), title=row["title"], body=row["content"], state="closed", author_login=row["author"], api_url=f"https://api.github.com/repos/{repository}/pulls/{row['id']}", html_url=f"https://github.com/{repository}/pull/{row['id']}", created_at=parse_time(row["timestamp"]), updated_at=parse_time(row["timestamp"]), closed_at=parse_time(row["timestamp"]), merged_at=parse_time(row["timestamp"]), base_ref="main", head_ref=f"demo/{row['id']}", labels=["architecture", "demo"]) for row in load_json("github/pull-requests.json")]

    async def fetch_pull_request_comments(self, repository: str, pull_number: int) -> list[GitHubPullRequestComment]:
        rows = [row for row in load_json("github/pull-request-comments.json") if int(row["pull_request"].split("-")[1]) == pull_number]
        return [GitHubPullRequestComment(repository=repository, pull_number=pull_number, id=index + 1, body=row["content"], author_login=row["author"], api_url=f"https://api.github.com/repos/{repository}/pulls/comments/{row['id']}", html_url=f"https://github.com/{repository}/pull/{pull_number}#discussion_{index + 1}", created_at=parse_time(row["timestamp"]), updated_at=parse_time(row["timestamp"])) for index, row in enumerate(rows)]

    async def fetch_commits(self, repository: str, *, ref: str | None = None) -> list[GitHubCommit]:
        return [GitHubCommit(repository=repository, sha=row["sha"], message=row["message"], author_name=row["author"], author_email=f"{row['author']}@atlas.example", authored_at=parse_time(row["timestamp"]), committer_name=row["author"], committed_at=parse_time(row["timestamp"]), api_url=f"https://api.github.com/repos/{repository}/commits/{row['sha']}", html_url=f"https://github.com/{repository}/commit/{row['sha']}") for row in load_json("github/commits.json")]


class FixtureSlackService:
    """File-backed normalized Slack service; SlackConnector remains the public boundary."""

    async def fetch_messages(self, channel_id: str, *, limit: int = 100) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        for conversation in load_json("slack/conversations.json"):
            if conversation["channel_id"] != channel_id:
                continue
            for index, (author, timestamp, text) in enumerate(conversation["messages"]):
                records.append(SourceRecord(source=ArtifactSource.SLACK, source_id=f"{channel_id}:{conversation['thread_ts']}:{index}", event_type=ArtifactEventType.THREAD, timestamp=parse_time(timestamp), author=author, title=conversation["channel"], raw_content=text, metadata={"channel_id": channel_id, "thread_ts": conversation["thread_ts"], "message_ts": f"{conversation['thread_ts']}{index:02d}"}))
        return records[:limit]


class DemoEntityCanonicalizer(EntityCanonicalizer):
    async def canonicalize(self, name: str) -> str | None:
        return name


def load_json(relative_path: str) -> list[dict[str, Any]]:
    return json.loads((DATA / relative_path).read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


async def github_records() -> list[SourceRecord]:
    connector = GitHubConnector(FixtureGitHubService())
    records: list[SourceRecord] = []
    readme = await connector.fetch_readme(REPOSITORY)
    records.append(SourceRecord(source=ArtifactSource.GITHUB, source_id=readme.sha, event_type=ArtifactEventType.README, timestamp=datetime(2026, 4, 1, tzinfo=UTC), author="atlas-engineering", title=readme.path, raw_content=readme.content, metadata={"repository": REPOSITORY, "path": readme.path}))
    pull_requests = await connector.fetch_pull_requests(REPOSITORY, state="all")
    for pull_request in pull_requests:
        records.append(SourceRecord(source=ArtifactSource.GITHUB, source_id=f"pr-{pull_request.number}", event_type=ArtifactEventType.PULL_REQUEST, timestamp=pull_request.updated_at, author=pull_request.author_login or "unknown", title=pull_request.title, raw_content=pull_request.body or "", metadata={"repository": REPOSITORY, "pull_number": pull_request.number, "labels": pull_request.labels}))
        for comment in await connector.fetch_pull_request_comments(REPOSITORY, pull_request.number):
            records.append(SourceRecord(source=ArtifactSource.GITHUB, source_id=f"comment-{comment.id}", event_type=ArtifactEventType.PULL_REQUEST_COMMENT, timestamp=comment.updated_at, author=comment.author_login or "unknown", title=f"PR #{pull_request.number} comment", raw_content=comment.body, metadata={"repository": REPOSITORY, "pull_number": pull_request.number, "path": comment.path or ""}))
    for commit in await connector.fetch_commits(REPOSITORY):
        records.append(SourceRecord(source=ArtifactSource.GITHUB, source_id=commit.sha, event_type=ArtifactEventType.COMMIT, timestamp=commit.committed_at or datetime.now(UTC), author=commit.author_name or "unknown", title=commit.message.splitlines()[0], raw_content=commit.message, metadata={"repository": REPOSITORY}))
    return records


def markdown_records() -> Iterable[SourceRecord]:
    for path in sorted((DATA / "markdown").glob("*.md")):
        event_type = ArtifactEventType.ADR if path.name.startswith("ADR-") else ArtifactEventType.RFC if path.name.startswith("RFC-") else ArtifactEventType.DOCUMENT
        yield SourceRecord(source=ArtifactSource.MARKDOWN, source_id=f"demo:{path.name}", event_type=event_type, timestamp=datetime(2026, 4, 1, tzinfo=UTC), author="atlas-engineering", title=path.stem, raw_content=path.read_text(encoding="utf-8"), metadata={"filename": path.name, "fixture": True})


def build_ekpp() -> DefaultEngineeringKnowledgeProcessingPipeline:
    settings = get_extraction_settings()
    client = create_structured_extraction_client(settings)
    prompts: PromptProvider = PromptRegistry(PromptTemplates.from_directory(settings.prompt_directory))
    extractors = (DecisionExtractor(client, prompts), TradeoffExtractor(client, prompts), AlternativeExtractor(client, prompts), TopicExtractor(client, prompts), StatusExtractor(client, prompts), ArchitectureChangeExtractor(client, prompts), EntityExtractor(client, prompts), OpenQuestionExtractor(client, prompts))
    return DefaultEngineeringKnowledgeProcessingPipeline(extractor=CompositeInformationExtractor(extractors), entity_resolver=DefaultEntityResolver(DemoEntityCanonicalizer()), builder=DefaultKnowledgeObjectBuilder(), deduplication=DefaultDeduplicationService())


async def run() -> None:
    # Read the same .env-backed settings contract used by the application.
    # Supermemory is the configured persistence boundary; intentionally do not
    # substitute an in-process store when the service URL is absent.
    settings = get_supermemory_settings()
    # Fixture conversations are deliberately batched as threads even where the
    # human discussion pauses longer than the production five-minute window.
    buffer = IngestionBufferManager(config=BufferConfig(inactivity_seconds=3600, max_messages=50))
    engine, queue, ekpp = DefaultIngestionEngine(), InMemoryArtifactQueue(), build_ekpp()
    artifacts = []
    for record in [*await github_records(), *markdown_records()]:
        artifact = await engine.ingest(record)
        await queue.enqueue(artifact)
        artifacts.append(artifact)
    slack = SlackConnector(FixtureSlackService())
    for channel_id in sorted({row["channel_id"] for row in load_json("slack/conversations.json")}):
        for record in await slack.fetch_messages(channel_id, limit=500):
            for transcript in await buffer.add(record):
                artifact = await engine.ingest(transcript)
                await queue.enqueue(artifact)
                artifacts.append(artifact)
    for transcript in await buffer.flush_all():
        artifact = await engine.ingest(transcript)
        await queue.enqueue(artifact)
        artifacts.append(artifact)
    client = HttpSupermemoryClient(settings)
    knowledge_count = 0
    try:
        while item := await queue.dequeue(timeout_seconds=0.1):
            await client.store_artifact(item.artifact)
            knowledge = await ekpp.process(item.artifact)
            await client.batch_store(knowledge)
            knowledge_count += len(knowledge)
            await queue.acknowledge(item.item_id)
    finally:
        await client.aclose()
        await queue.shutdown()
    print(f"Seeded {len(artifacts)} artifacts and {knowledge_count} knowledge objects into Supermemory container '{settings.container_tag}'.")


if __name__ == "__main__":
    asyncio.run(run())

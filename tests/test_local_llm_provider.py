"""Unit tests for local structured-extraction providers without an Ollama server."""

import json
import unittest
from datetime import UTC, datetime

import httpx

from backend.app.memory.extractors.config import ExtractionSettings
from backend.app.memory.extractors.factory import create_structured_extraction_client
from backend.app.memory.extractors.models import ExtractionType
from backend.app.memory.extractors.providers import DemoExtractionClient, OllamaProvider
from backend.app.models import Artifact, ArtifactEventType, ArtifactSource


def artifact() -> Artifact:
    return Artifact(
        source=ArtifactSource.SLACK,
        source_id="C1:1:1",
        event_type=ArtifactEventType.THREAD,
        timestamp=datetime(2026, 7, 12, tzinfo=UTC),
        author="maya",
        title="#platform",
        raw_content="We decided to use Redis for revocable sessions because logout must be immediate.",
    )


def settings(provider: str = "ollama") -> ExtractionSettings:
    return ExtractionSettings(
        EXTRACTION_PROVIDER=provider,
        OLLAMA_BASE_URL="http://ollama.test",
        OLLAMA_MODEL="qwen3:8b",
        OLLAMA_TIMEOUT=1,
    )


class OllamaProviderTests(unittest.IsolatedAsyncioTestCase):
    async def _provider(self, handler) -> OllamaProvider:
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://ollama.test")
        return OllamaProvider(settings(), http_client=client)

    async def test_successful_extraction(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api/generate")
            self.assertTrue(json.loads(request.content)["format"] == "json")
            return httpx.Response(
                200,
                json={"response": json.dumps({"facts": [{
                    "type": "decision", "entity": "Redis", "value": "Use Redis for revocable sessions.",
                    "status": None, "participants": ["maya"], "reason": "logout must be immediate",
                    "evidence": [{"excerpt": artifact().raw_content, "location": "message 1", "supporting_text": artifact().raw_content}],
                    "confidence": 0.91, "metadata": {"timestamp": None},
                }]})},
            )

        provider = await self._provider(handler)
        facts = await provider.extract(prompt="Extract decisions.", artifact=artifact(), extraction_type=ExtractionType.DECISION)
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].entity, "Redis")

    async def test_invalid_json_is_repaired_once(self) -> None:
        calls = 0

        async def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            if calls == 1:
                return httpx.Response(200, json={"response": "not-json"})
            return httpx.Response(
                200,
                json={"response": json.dumps({"facts": [{
                    "type": "decision", "entity": "Redis", "value": "Use Redis.", "status": None,
                    "participants": [], "reason": None,
                    "evidence": [{"excerpt": artifact().raw_content, "location": None, "supporting_text": None}],
                    "confidence": 0.8, "metadata": {},
                }]})},
            )

        provider = await self._provider(handler)
        facts = await provider.extract(prompt="Extract decisions.", artifact=artifact(), extraction_type=ExtractionType.DECISION)
        self.assertEqual(len(facts), 1)
        self.assertEqual(calls, 2)

    async def test_timeout_returns_empty_without_crashing(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("slow", request=request)

        provider = await self._provider(handler)
        self.assertEqual(
            await provider.extract(prompt="Extract decisions.", artifact=artifact(), extraction_type=ExtractionType.DECISION), []
        )

    async def test_ollama_unavailable_returns_empty_without_crashing(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("offline", request=request)

        provider = await self._provider(handler)
        self.assertEqual(
            await provider.extract(prompt="Extract decisions.", artifact=artifact(), extraction_type=ExtractionType.DECISION), []
        )


class ProviderFactoryTests(unittest.TestCase):
    def test_provider_switching(self) -> None:
        self.assertIsInstance(create_structured_extraction_client(settings("demo")), DemoExtractionClient)
        self.assertIsInstance(create_structured_extraction_client(settings("ollama")), OllamaProvider)

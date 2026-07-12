"""Run the local Ollama extractor against the realistic conversation corpus."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.memory.extractors.config import ExtractionSettings, get_extraction_settings
from backend.app.memory.extractors.models import ExtractedFact, ExtractionType
from backend.app.memory.extractors.prompts import PromptRegistry, PromptTemplates
from backend.app.memory.extractors.providers import OllamaProvider
from backend.app.models import Artifact, ArtifactEventType, ArtifactSource
from tests.extraction.report import prompt_recommendations, write_reports

DATA_DIRECTORY = Path(__file__).resolve().parent
CATEGORIES = tuple(ExtractionType)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_conversation(conversation: dict[str, Any]) -> str:
    return "\n".join(f"[{message['timestamp']}] {message['author']}: {message['text']}" for message in conversation["messages"])


def make_artifact(conversation: dict[str, Any]) -> Artifact:
    first = conversation["messages"][0]
    return Artifact(
        source=ArtifactSource.SLACK,
        source_id=conversation["id"],
        event_type=ArtifactEventType.THREAD,
        timestamp=datetime.fromisoformat(first["timestamp"].replace("Z", "+00:00")),
        author=first["author"],
        title=conversation.get("channel", "#engineering"),
        raw_content=render_conversation(conversation),
        metadata={"conversation_id": conversation["id"]},
    )


def normalized(value: str | None) -> set[str]:
    if not value:
        return set()
    return {"".join(character for character in word.casefold() if character.isalnum()) for word in value.split()} - {""}


def expected_matches_actual(expected: dict[str, Any], actual: ExtractedFact, category: ExtractionType) -> bool:
    expected_terms = set(expected.get("match_terms") or normalized(f"{expected.get('entity', '')} {expected.get('value', '')}"))
    actual_terms = normalized(" ".join(filter(None, [actual.entity, actual.value, actual.reason, actual.status])))
    if not expected_terms or not expected_terms.issubset(actual_terms):
        return False
    evidence = expected.get("evidence")
    if not evidence:
        return True
    return any(evidence in item.excerpt or item.excerpt in evidence for item in actual.evidence)


def public_fact(fact: ExtractedFact) -> dict[str, Any]:
    return fact.model_dump(mode="json")


def possible_cause(category: str, missing: list[dict[str, Any]], unexpected: list[dict[str, Any]]) -> str:
    if missing and unexpected:
        return f"The model found {category} facts, but its wording or evidence did not align with the expected source-grounded fact."
    if missing:
        return f"The natural-language {category} signal may be too implicit, hedged, interrupted, or obscured by nearby discussion."
    return f"The model may be over-extracting a {category} from a proposal, question, or non-final statement."


async def evaluate(conversations_directory: Path, expected_directory: Path, output_directory: Path) -> dict[str, Any]:
    settings = get_extraction_settings().model_copy(update={"provider": "ollama"})
    if not isinstance(settings, ExtractionSettings):  # Defensive guard for future settings changes.
        raise RuntimeError("Unable to load Ollama extraction settings.")
    provider = OllamaProvider(settings)
    prompts = PromptRegistry(PromptTemplates.from_directory(settings.prompt_directory))
    totals: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    failures: list[dict[str, Any]] = []
    call_count = validation_successes = extraction_failures = 0
    durations_ms: list[float] = []
    conversation_files = sorted(conversations_directory.glob("*.json"))
    try:
        for conversation_path in conversation_files:
            conversation = load_json(conversation_path)
            expected_path = expected_directory / conversation_path.name
            if not expected_path.exists():
                raise FileNotFoundError(f"Missing expected file for {conversation_path.name}")
            expected = load_json(expected_path)
            if expected["id"] != conversation["id"]:
                raise ValueError(f"Dataset ID mismatch in {conversation_path.name}")
            artifact = make_artifact(conversation)
            transcript = render_conversation(conversation)
            for category in CATEGORIES:
                call_count += 1
                started = perf_counter()
                try:
                    actual = await provider.extract(prompt=prompts.get(category), artifact=artifact, extraction_type=category)
                    durations_ms.append((perf_counter() - started) * 1000)
                    # The provider returns only Pydantic-validated facts. Round-tripping proves the public contract.
                    actual = [ExtractedFact.model_validate(item.model_dump()) for item in actual]
                    validation_successes += 1
                except Exception as exc:  # Evaluation must continue so failures are visible in the report.
                    durations_ms.append((perf_counter() - started) * 1000)
                    extraction_failures += 1
                    actual = []
                    failures.append({
                        "conversation_id": conversation["id"], "category": category.value, "conversation": transcript,
                        "expected": expected["facts"].get(category.value, []), "actual": {"error": str(exc)},
                        "missing": expected["facts"].get(category.value, []), "unexpected": [],
                        "possible_cause": "The extraction client raised an exception before it returned a validated result.",
                    })
                expected_facts = expected["facts"].get(category.value, [])
                unmatched_actual = list(actual)
                missing: list[dict[str, Any]] = []
                for expected_fact in expected_facts:
                    matched_index = next((index for index, fact in enumerate(unmatched_actual) if expected_matches_actual(expected_fact, fact, category)), None)
                    if matched_index is None:
                        totals[category.value]["fn"] += 1
                        missing.append(expected_fact)
                    else:
                        totals[category.value]["tp"] += 1
                        unmatched_actual.pop(matched_index)
                totals[category.value]["fp"] += len(unmatched_actual)
                if missing or unmatched_actual:
                    failures.append({
                        "conversation_id": conversation["id"], "category": category.value, "conversation": transcript,
                        "expected": expected_facts, "actual": [public_fact(fact) for fact in actual],
                        "missing": missing, "unexpected": [public_fact(fact) for fact in unmatched_actual],
                        "possible_cause": possible_cause(category.value, missing, [public_fact(fact) for fact in unmatched_actual]),
                    })
    finally:
        await provider.aclose()

    metrics: dict[str, dict[str, float]] = {}
    for category in CATEGORIES:
        counts = totals[category.value]
        precision = counts["tp"] / (counts["tp"] + counts["fp"]) if counts["tp"] + counts["fp"] else 1.0
        recall = counts["tp"] / (counts["tp"] + counts["fn"]) if counts["tp"] + counts["fn"] else 1.0
        metrics[category.value] = {**counts, "precision": precision, "recall": recall, "accuracy": counts["tp"] / sum(counts.values()) if sum(counts.values()) else 1.0}
    report = {
        "conversation_count": len(conversation_files), "call_count": call_count,
        "average_extraction_time_ms": sum(durations_ms) / len(durations_ms) if durations_ms else 0.0,
        "json_validation_success_rate": validation_successes / call_count if call_count else 0.0,
        "extraction_failure_rate": extraction_failures / call_count if call_count else 0.0,
        "metrics": metrics, "failures": failures,
    }
    report["prompt_recommendations"] = prompt_recommendations(metrics, failures)
    write_reports(report, output_directory)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate local Ollama extraction correctness.")
    parser.add_argument("--conversations", type=Path, default=DATA_DIRECTORY / "conversations")
    parser.add_argument("--expected", type=Path, default=DATA_DIRECTORY / "expected")
    parser.add_argument("--output", type=Path, default=DATA_DIRECTORY / "reports")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = asyncio.run(evaluate(args.conversations, args.expected, args.output))
    print(f"Evaluated {result['conversation_count']} conversations. Reports: {args.output}")

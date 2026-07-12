"""Reporting and prompt-tuning recommendations for extraction evaluation."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DISPLAY_NAMES = {
    "decision": "Decision",
    "entity": "Entity",
    "tradeoff": "Tradeoff",
    "alternative": "Alternative",
    "open_question": "Open Question",
    "architecture_change": "Architecture Change",
}


def prompt_recommendations(metrics: dict[str, dict[str, float]], failures: list[dict[str, Any]]) -> list[str]:
    """Suggest targeted template changes only when errors show a repeatable pattern."""
    missing_by_type = Counter(item["category"] for item in failures if item["missing"])
    recommendations: list[str] = []
    for category, count in missing_by_type.most_common():
        category_metrics = metrics.get(category, {})
        if count >= 2 and category_metrics.get("recall", 1.0) < 0.75:
            recommendations.append(
                f"{DISPLAY_NAMES.get(category, category)} recall is {category_metrics['recall']:.0%} with {count} repeated misses. "
                f"Consider adding few-shot natural-conversation examples to the {category} template, especially statements with hedging, disagreement, or partial agreement."
            )
    if not recommendations:
        recommendations.append("No repeated low-recall pattern crossed the recommendation threshold; retain the current prompts and inspect individual errors.")
    return recommendations


def write_reports(report: dict[str, Any], output_directory: Path) -> tuple[Path, Path]:
    """Write machine-readable results and a concise human review document."""
    output_directory.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).isoformat()
    report["generated_at"] = generated_at
    json_path = output_directory / "extraction-report.json"
    markdown_path = output_directory / "extraction-report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# DecisionLens Extraction Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Conversations evaluated: **{report['conversation_count']}**  ",
        f"Extraction calls: **{report['call_count']}**  ",
        f"Average extraction time: **{report['average_extraction_time_ms']:.1f} ms**",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "| --- | ---: |",
    ]
    for category in ("decision", "entity", "tradeoff", "alternative", "open_question", "architecture_change"):
        item = report["metrics"][category]
        label = DISPLAY_NAMES[category]
        if category in {"decision", "entity"}:
            lines.extend([f"| {label} Precision | {item['precision']:.1%} |", f"| {label} Recall | {item['recall']:.1%} |"])
        else:
            lines.append(f"| {label} Extraction Accuracy | {item['accuracy']:.1%} |")
    lines.extend([
        f"| JSON Validation Success Rate | {report['json_validation_success_rate']:.1%} |",
        f"| Extraction Failure Rate | {report['extraction_failure_rate']:.1%} |",
        "",
        "## Error Analysis",
        "",
    ])
    if not report["failures"]:
        lines.append("No unmatched expected or actual facts were found.")
    for failure in report["failures"]:
        lines.extend([
            f"### {failure['conversation_id']} — {failure['category']}",
            "",
            "**Conversation**",
            "",
            failure["conversation"],
            "",
            "**Expected**",
            "",
            "```json",
            json.dumps(failure["expected"], indent=2),
            "```",
            "",
            "**Actual**",
            "",
            "```json",
            json.dumps(failure["actual"], indent=2),
            "```",
            "",
            f"**Missing information:** {json.dumps(failure['missing'])}",
            "",
            f"**Possible cause:** {failure['possible_cause']}",
            "",
        ])
    lines.extend(["## Prompt Improvement Recommendations", ""])
    lines.extend(f"- {recommendation}" for recommendation in report["prompt_recommendations"])
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path

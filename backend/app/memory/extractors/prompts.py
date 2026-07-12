"""Reusable prompt templates for source-grounded engineering extraction."""

from dataclasses import dataclass
from pathlib import Path

from backend.app.memory.extractors.interfaces import PromptProvider
from backend.app.memory.extractors.models import ExtractionType
from backend.app.models import Artifact


class SystemPrompt:
    """The invariant role and output contract shared by every local provider."""

    text = """You are an Engineering Information Extraction Engine.
Extract only facts explicitly supported by the supplied engineering artifact. Do not infer,
summarize beyond the source, or invent names, dates, decisions, or rationale. The exact
evidence excerpt for every fact must be copied verbatim from the artifact.

Return only a JSON object with one key, \"facts\", whose value is an array. Each fact must
match this schema exactly: {\"type\": string, \"entity\": string, \"value\": string|null,
\"status\": string|null, \"participants\": [string], \"reason\": string|null,
\"evidence\": [{\"excerpt\": string, \"location\": string|null,
\"supporting_text\": string|null}], \"confidence\": number,
\"metadata\": object}. Put unavailable values in the existing nullable fields as null.
Use metadata only for source-grounded optional details such as timestamp. Never return
markdown, prose, or fields outside this schema. If no supported fact exists, return
{\"facts\": []}."""


class PromptTemplates:
    """Category instructions, optionally overridden by text files for prompt tuning."""

    defaults: dict[ExtractionType, str] = {
        ExtractionType.DECISION: "Extract explicit engineering choices that were made or approved.",
        ExtractionType.TRADEOFF: "Extract explicit compromises, costs, risks, or benefits that were accepted.",
        ExtractionType.ALTERNATIVE: "Extract options that were explicitly considered, proposed, or rejected.",
        ExtractionType.TOPIC: "Extract engineering subjects that are substantively discussed.",
        ExtractionType.STATUS: "Extract explicit delivery, rollout, operational, or approval status statements.",
        ExtractionType.ARCHITECTURE_CHANGE: "Extract explicit changes to system boundaries, components, or data flow.",
        ExtractionType.ENTITY: "Extract explicitly mentioned engineering systems, services, technologies, or components.",
        ExtractionType.OPEN_QUESTION: "Extract explicit unresolved engineering questions.",
    }

    def __init__(self, templates: dict[ExtractionType, str] | None = None) -> None:
        self._templates = {**self.defaults, **(templates or {})}

    @classmethod
    def from_directory(cls, directory: str | Path | None) -> "PromptTemplates":
        """Load optional ``<extraction-type>.txt`` overrides without code changes."""
        if not directory:
            return cls()
        root = Path(directory)
        if not root.is_dir():
            return cls()
        overrides: dict[ExtractionType, str] = {}
        for kind in ExtractionType:
            candidate = root / f"{kind.value}.txt"
            if candidate.is_file() and (template := candidate.read_text(encoding="utf-8").strip()):
                overrides[kind] = template
        return cls(overrides)

    def get(self, extraction_type: ExtractionType) -> str:
        return self._templates[extraction_type]


class PromptRegistry(PromptProvider):
    """PromptProvider adapter over reusable, externally overridable templates."""

    def __init__(self, templates: PromptTemplates | dict[ExtractionType, str] | None = None) -> None:
        self._templates = PromptTemplates(templates) if isinstance(templates, dict) else templates or PromptTemplates()

    def get(self, extraction_type: ExtractionType) -> str:
        return self._templates.get(extraction_type)


@dataclass(frozen=True)
class BuiltPrompt:
    """Provider-neutral system and user prompts ready for a local inference API."""

    system: str
    user: str


class ExtractionPromptBuilder:
    """Assembles templates with artifact context; transports never embed prompt text."""

    def build(self, *, instruction: str, artifact: Artifact, extraction_type: ExtractionType) -> BuiltPrompt:
        return BuiltPrompt(
            system=SystemPrompt.text,
            user=(
                f"Extraction category: {extraction_type.value}\n"
                f"Task: {instruction}\n\n"
                "Artifact metadata (context only):\n"
                f"source={artifact.source.value}; event_type={artifact.event_type.value}; "
                f"author={artifact.author}; timestamp={artifact.timestamp.isoformat()}; title={artifact.title or ''}\n\n"
                "Artifact content (the only evidence source):\n"
                f"{artifact.raw_content}"
            ),
        )

    def build_repair(self, *, original_prompt: BuiltPrompt, invalid_output: str) -> BuiltPrompt:
        return BuiltPrompt(
            system=SystemPrompt.text,
            user=(
                "Repair the following model output into the required JSON object. Preserve only facts "
                "whose evidence is present verbatim in the artifact context below. Return JSON only.\n\n"
                f"Original extraction context:\n{original_prompt.user}\n\n"
                f"Invalid output:\n{invalid_output}"
            ),
        )

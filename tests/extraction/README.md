# Extraction Quality Evaluation

This suite measures extraction correctness from realistic Slack-like conversations. It does
not execute EKPP, entity resolution, deduplication, Supermemory, or intelligence analyzers.
Instead, it invokes `OllamaProvider` directly through the unchanged
`StructuredExtractionClient` interface for every extraction category.

## Run

1. Start Ollama and download the configured model:

   ```bash
   ollama serve
   ollama pull qwen3:8b
   ```

2. Set `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT` in `.env`.
3. From the repository root, run:

   ```bash
   python tests/extraction/runner.py
   ```

The evaluator always uses Ollama, regardless of `EXTRACTION_PROVIDER`, because this is a
Local-LLM quality suite. It writes `reports/extraction-report.json` and
`reports/extraction-report.md`. Reports are ignored by Git because they are run artifacts.

## Dataset format

Each `conversations/*.json` file contains a Slack-style thread. The matching file in
`expected/` contains the expected facts by extraction type. `match_terms` allows fair
matching when the model paraphrases a value, while the evaluator still requires the expected
supporting evidence to match a verbatim evidence excerpt returned by the model.

Accuracy for tradeoffs, alternatives, open questions, and architecture changes is set-overlap
accuracy: `TP / (TP + FP + FN)`. Decisions and entities additionally report precision and
recall. JSON-validation success means the client returned facts that round-trip through the
existing strict Pydantic extraction schema; extraction failures are uncaught client exceptions.

## Improving prompts

The reports include every mismatch with the full conversation, expected facts, actual facts,
missing information, and a possible cause. Repeated low-recall categories generate prompt
recommendations only. The evaluator never edits prompt templates.

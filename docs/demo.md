# DecisionLens demo guide

## 30-second pitch

DecisionLens is an engineering memory workspace built on Supermemory. It connects to GitHub,
Slack, and Markdown, turns raw discussions into evidence-backed knowledge objects, and lets
teams ask why a technical decision happened months later without relying on tribal memory.

## What judges should understand

- **Problem:** engineering reasoning disappears inside PR comments, Slack threads, and stale docs.
- **Product:** DecisionLens extracts decisions, tradeoffs, alternatives, open questions, and timelines.
- **Supermemory fit:** Supermemory is the long-term semantic memory layer; DecisionLens supplies the engineering-specific ingestion, extraction, and intelligence layer.
- **Privacy story:** the same stack can run inside a company network with local Ollama extraction, or connect to a managed LLM when a team prefers speed over full local control.
- **Differentiator:** this is not generic document search. It preserves the reasoning trail behind architecture choices.

## Demo flow

1. Start the API and dashboard, then open `http://localhost:5173`.
2. Begin on **Overview**. Point out the source-to-memory pipeline, decision/tradeoff counts, and judge demo path.
3. Open **Memory graph**. Click nodes to show the Obsidian-style relationship map, evidence panel, and knowledge-object chart.
4. Open **Markdown upload** and upload an ADR or RFC. The backend queues it, and the frontend immediately extracts local session memories so the graph changes even without Supermemory.
5. Return to **Memory graph** and click the uploaded memory node.
6. Open **Ask DecisionLens** and ask about a term from the uploaded file. Review the local evidence-backed answer.
7. Open **Architecture timeline**. Follow the evolution from Supabase Auth and PostgreSQL RLS through Redis, Kafka, and background jobs.
8. Open **Technology trends** to compare adoption and rejection signals; Firebase is the useful contrast case.

## Talking points

- DecisionLens turns raw GitHub, Slack, and Markdown artifacts into source-grounded organizational memory.
- The dashboard never invents a citation: each insight keeps evidence and artifact references from the frozen backend pipeline.
- Recurring discussions and decision history expose the reasoning that would otherwise be lost.
- The UI gracefully uses demo content when a local Supermemory service is unavailable; live API responses take priority when configured.
- In a real company, employees would open a shared DecisionLens workspace, while connectors and workers run centrally inside company infrastructure.

## Questions to ask

- “Why do we persist Stripe webhook envelopes before publishing Kafka events?”
- “What tradeoffs did we accept for Redis session revocation?”
- “When did tenant authorization become PostgreSQL RLS-based?”
- “What alternatives were considered for Kafka billing audit events?”

## Expected outputs

| Question | Expected evidence-backed answer |
| --- | --- |
| Redis sessions | A 24-hour Redis registry enables immediate revocation; it adds a runtime dependency. |
| Stripe events | PostgreSQL persistence gives replay and idempotency before asynchronous Kafka publication. |
| Tenant authorization | Supabase Auth identifies users while PostgreSQL RLS enforces tenant data boundaries. |
| Kafka | Consumers commit only after PostgreSQL projections succeed; idempotency handles retries. |

## How to test

### No LLM, no Supermemory

This is the fastest hackathon demo path.

1. Run the frontend and API.
2. Upload a Markdown file containing lines such as:

   ```md
   # Session revocation ADR
   Decision: Use Redis for immediate session revocation.
   Tradeoff: Redis adds operational ownership.
   Alternative: Fully stateless JWT sessions.
   Architecture Change: Session middleware checks Redis before tenant queries.
   Open Question: Should enterprise sessions use a shorter TTL?
   ```

3. Open **Memory graph**. Uploaded memories appear immediately.
4. Open **Ask DecisionLens** and ask about `Redis`, `sessions`, or another uploaded term.

This mode uses a deterministic local demo extractor in the browser. It proves the workflow
without requiring a model, API key, or Supermemory instance.

### Local LLM extraction with Ollama

Use this when you want the backend EKPP to call a local model.

1. Run `ollama serve`.
2. Pull a model, for example `ollama pull qwen3:8b`.
3. Configure `.env`:

   ```env
   EXTRACTION_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3:8b
   ```

4. Configure Supermemory, then run `python scripts/seed.py`.

### Live Supermemory-backed intelligence

Set these values in `.env`:

```env
SUPERMEMORY_BASE_URL=
SUPERMEMORY_API_KEY=
SUPERMEMORY_CONTAINER_TAG=decisionlens
```

Then run `python scripts/seed.py`. The dashboard prefers live FastAPI/Supermemory responses
when available and falls back to demo data when they are not.

## Connector status

- **Markdown:** usable now through upload and sample-data ingestion.
- **GitHub:** connector code and sample-data seeding exist; real team usage needs token/OAuth configuration.
- **Slack:** connector code and sample-data seeding exist; real team usage needs a Slack app/bot token.
- **Notion:** not implemented in DecisionLens yet. It can be added as another connector using the same Artifact contract.

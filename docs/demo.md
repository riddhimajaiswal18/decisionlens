# DecisionLens demo guide

## Demo flow

1. Start the API and dashboard, then open `http://localhost:5173`.
2. Begin on **Overview**. Point out the decision, tradeoff, and architecture-change counts, plus the latest event card.
3. Open **Ask DecisionLens** and ask: “Why did we choose Redis for session management?” Review the answer, confidence, related technologies, and evidence panel.
4. Open **Architecture timeline**. Follow the evolution from Supabase Auth and PostgreSQL RLS through Redis, Kafka, and background jobs.
5. Open **Recurring discussions** to show that Redis, Kafka, and RLS have durable organizational context rather than isolated messages.
6. Open **Technology trends** to compare adoption and rejection signals; Firebase is the useful contrast case.
7. Search **Decision history** for `Supabase`, `Redis`, or `Kafka` to reveal a decision’s chronology, alternatives, and tradeoffs.
8. Finish with **Markdown upload**. Upload an ADR or RFC and show that it is accepted by the existing ingestion endpoint.

## Talking points

- DecisionLens turns raw GitHub, Slack, and Markdown artifacts into source-grounded organizational memory.
- The dashboard never invents a citation: each insight keeps evidence and artifact references from the frozen backend pipeline.
- Recurring discussions and decision history expose the reasoning that would otherwise be lost.
- The UI gracefully uses demo content when a local Supermemory service is unavailable; live API responses take priority when configured.

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

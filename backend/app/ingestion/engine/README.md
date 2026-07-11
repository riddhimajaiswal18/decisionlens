# Ingestion Engine

The Ingestion Engine is the sole boundary that creates canonical `Artifact` values. It accepts normalized GitHub or Markdown `SourceRecord` instances and Slack `AggregatedTranscript` instances, validates them, enriches metadata with the input type, and returns exactly one immutable Artifact.

The factory selects a source-specific builder, keeping the engine independent of connector details. Adding a future source requires only a builder and factory registration; validation and orchestration remain unchanged.

This boundary prevents downstream coupling: connectors provide external normalized data, the buffer provides conversational transcripts, and all later layers receive the same Artifact contract. It does not enqueue, extract, resolve entities, call EKPP, or communicate with Supermemory.

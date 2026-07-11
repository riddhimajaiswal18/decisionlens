# Engineering Intelligence Engine

The Intelligence Engine consumes only the typed `SupermemoryClient`. It has no connector, buffer, ingestion, EKPP, or direct HTTP dependency.

Each analyzer is a plugin implementing `analyze(request)`. The engine registers analyzers by name and dispatches one or all analyzers, so a future analyzer can be added by implementing the interface and registering it without modifying existing analyzers.

The analyzers are deterministic and evidence-bound: every output carries the Supermemory results that support it, and fields requiring unavailable evidence are omitted rather than inferred. Future API endpoints can call the engine and return its immutable insight models directly.

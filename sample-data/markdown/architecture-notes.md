# Architecture Notes: Sessions, caching, and work queues

Decision: Redis is the shared store for revocable session identifiers, cache keys, and short-lived rate-limit counters.

Tradeoff: Redis increases operational complexity, but it gives the platform immediate session revocation and predictable cache latency.

Alternative: use PostgreSQL for sessions and disable shared caching until traffic grows.

Architecture Change: report generation and email delivery run as PostgreSQL-backed background jobs instead of inline API work.

Status: the Redis session registry and background job dashboard are operating in production.

Open Question: when should cache invalidation move from time-based TTLs to Kafka-driven events?

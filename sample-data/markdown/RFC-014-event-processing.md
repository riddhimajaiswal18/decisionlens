# RFC-014: Durable event processing

Decision: write Stripe webhook envelopes to PostgreSQL, then publish committed events to Kafka.

Reason: payment events must be replayable and observable even when downstream consumers are unavailable.

Tradeoff: this introduces an outbox worker and delayed eventual consistency for downstream projections.

Alternative: process Stripe webhooks synchronously and call each consumer directly.

Architecture Change: background jobs own outbox publication and Kafka consumers own billing projections.

Open Question: should Kafka topics be compacted for the latest subscription state?

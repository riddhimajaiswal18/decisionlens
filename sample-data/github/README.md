# Atlas Engineering Platform

Atlas processes subscription events and serves authenticated workspace traffic for growing B2B teams.

## Current architecture

- Supabase Auth issues user identities and PostgreSQL Row Level Security protects tenant data.
- Redis stores short-lived session state and idempotency keys.
- Stripe webhooks are written to PostgreSQL before background workers process them.
- Kafka carries durable domain events for billing, audit, and analytics consumers.

Decision: use Supabase Auth with PostgreSQL RLS as the primary authorization boundary.
Tradeoff: centralizing session state in Redis adds operational ownership but allows immediate revocation.
Alternative: keep signed sessions entirely in browser cookies.
Architecture Change: webhook delivery now persists before Kafka publication.
Open Question: should enterprise SSO sessions use a shorter Redis TTL than password sessions?

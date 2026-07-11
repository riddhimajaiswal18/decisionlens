# ADR-001: Authentication and tenant authorization

Date: 2026-04-08

Decision: adopt Supabase Auth for identity and PostgreSQL Row Level Security for tenant authorization.

Reason: this keeps authorization close to tenant data and avoids a separate policy service during the first year.

Tradeoff: PostgreSQL policies require disciplined query review and make local debugging more involved.

Alternative: run a standalone authorization service with signed policy decisions.

Architecture Change: API middleware now resolves Supabase identities before opening tenant-scoped PostgreSQL transactions.

Open Question: how should support impersonation be audited without bypassing RLS?

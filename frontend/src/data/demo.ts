import type { ArchitectureTimeline, DecisionHistory, HistoricalContext, RecurringDiscussion, TechnologyTrend } from '../types'

const evidence = (content: string, artifact = 'slack:C-PLATFORM') => [{ content, original_snippet: content, source_location: 'Engineering discussion', artifact_reference: artifact, extraction_confidence: 0.92 }]
const base = { id: 'demo', confidence: 0.92, timestamp: '2026-08-10T10:20:00Z', related_artifacts: ['slack:C-PLATFORM'], related_entities: ['Supabase'], evidence: evidence('Decision evidence grounded in a source artifact.') }

export const demoTimeline: ArchitectureTimeline[] = [{ ...base, title: 'Architecture timeline', summary: 'The platform matured from hosted identity to event-driven operations.', events: [
  { timestamp: '2026-03-03T09:20:00Z', decision: 'Adopt Supabase Auth with PostgreSQL RLS for tenant authorization.', reason: 'Keeps policy close to tenant data.', confidence: .94, evidence: evidence('Use Supabase Auth and PostgreSQL RLS.', 'markdown:ADR-001') },
  { timestamp: '2026-04-04T13:20:00Z', decision: 'Cache Supabase profile lookups in Redis for five minutes.', reason: 'Reduce profile lookup latency.', confidence: .9, evidence: evidence('Cache profile lookups in Redis.', 'github:a9f4c20') },
  { timestamp: '2026-05-04T11:20:00Z', decision: 'Persist Stripe webhook envelopes before Kafka publication.', reason: 'Replayable, idempotent payment processing.', confidence: .96, evidence: evidence('Persist Stripe envelopes in PostgreSQL.', 'github:pr-184') },
  { timestamp: '2026-06-23T10:20:00Z', decision: 'Move report generation to PostgreSQL-backed background jobs.', reason: 'Protect API capacity.', confidence: .91, evidence: evidence('Report generation runs as background jobs.', 'github:bc3d881') },
] }]

export const demoRecurring: RecurringDiscussion[] = [
  { ...base, title: 'Recurring discussion: Redis', summary: 'Redis appears in session, cache, locking, and rate-limit decisions.', topic: 'Redis', discussion_count: 18, status: 'Adopted with guardrails', last_discussed: '2026-08-04T10:20:00Z' },
  { ...base, title: 'Recurring discussion: Kafka', summary: 'Kafka remains the durable event boundary for billing and audit flows.', topic: 'Kafka', discussion_count: 14, status: 'Active', last_discussed: '2026-08-10T10:20:00Z' },
  { ...base, title: 'Recurring discussion: PostgreSQL RLS', summary: 'Tenant isolation and support access are reviewed repeatedly.', topic: 'PostgreSQL RLS', discussion_count: 11, status: 'Approved', last_discussed: '2026-07-05T10:20:00Z' },
]

export const demoTrends: TechnologyTrend[] = [
  { ...base, title: 'Technology trend: Redis', summary: 'Redis is discussed across sessions, caching and limits.', technology: 'Redis', discussion_count: 24, accepted_count: 9, rejected_count: 1, is_new: false, is_deprecated: false },
  { ...base, title: 'Technology trend: PostgreSQL', summary: 'PostgreSQL is the primary consistency boundary.', technology: 'PostgreSQL', discussion_count: 21, accepted_count: 11, rejected_count: 0, is_new: false, is_deprecated: false },
  { ...base, title: 'Technology trend: Kafka', summary: 'Kafka is increasingly used for durable projections.', technology: 'Kafka', discussion_count: 17, accepted_count: 7, rejected_count: 2, is_new: true, is_deprecated: false },
  { ...base, title: 'Technology trend: Firebase', summary: 'Firebase was considered before the Supabase migration.', technology: 'Firebase', discussion_count: 6, accepted_count: 0, rejected_count: 5, is_new: false, is_deprecated: true },
]

export const demoHistory = (entity = 'Supabase'): DecisionHistory[] => [{ ...base, title: `Decision evolution: ${entity}`, summary: `Four source-grounded decisions show how ${entity} shaped the platform.`, decision: entity, participants: ['maya', 'liam', 'priya'], reasons: ['Tenant policy needs to stay close to data.', 'Immediate session revocation is required.'], timestamps: demoTimeline[0].events.map((event) => event.timestamp), history: demoTimeline[0].events }]
export const demoContext = (query: string): HistoricalContext[] => [{ ...base, title: `Historical context: ${query}`, summary: 'A concise answer based on the seeded engineering discussions.', topic: query, previous_decisions: ['Use Supabase Auth with PostgreSQL RLS.', 'Store revocable session IDs in Redis.'], tradeoffs: ['RLS increases local debugging effort.', 'Redis adds operational ownership.'], alternatives: ['Standalone authorization service.', 'Fully stateless JWT sessions.'], architecture_changes: ['Tenant middleware sets context before PostgreSQL transactions.'] }]

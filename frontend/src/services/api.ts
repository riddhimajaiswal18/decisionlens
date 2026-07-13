export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

import type { ArchitectureTimeline, DecisionHistory, QueryResults, RecurringDiscussion, TechnologyTrend } from '../types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: { ...(init?.body && !isFormData ? { 'Content-Type': 'application/json' } : {}), ...init?.headers },
  })
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`)
  return response.json() as Promise<T>
}

export const api = {
  health: (): Promise<{ status: string }> => request('/health'),
  query: (query: string): Promise<QueryResults> => request('/query', { method: 'POST', body: JSON.stringify({ query, filters: { limit: 100 } }) }),
  timeline: (): Promise<ArchitectureTimeline[]> => request('/timeline'),
  recurring: (): Promise<RecurringDiscussion[]> => request('/recurring-discussions'),
  trends: (): Promise<TechnologyTrend[]> => request('/technology-trends'),
  history: (entity: string): Promise<DecisionHistory[]> => request(`/decision-history/${encodeURIComponent(entity)}`),
  uploadMarkdown: (file: File) => { const body = new FormData(); body.append('file', file); return request<{ artifact_id: string; queue_item_id: string; status: string }>('/upload/markdown', { method: 'POST', body }) },
}

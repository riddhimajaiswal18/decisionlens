import { useEffect, useMemo, useRef, useState } from 'react'
import {
  AlertCircle, BarChart3, Bot, Brain,
  CheckCircle2, ChevronRight, DatabaseZap,
  FileText, GitCommit, GitPullRequest, GitBranch, Globe,
  Layers, LoaderCircle, Network, Route, Search, Send, Shield,
  Sparkles, TrendingUp, UploadCloud,
  Workflow, X, Zap, Activity, Eye, Lock, Server, Cpu,
  MessageSquare, Users, Award, Target, Flame,
  History as HistoryIcon,
} from 'lucide-react'
import { PageShell, type Page } from './components/PageShell'
import { demoContext, demoHistory, demoRecurring, demoTimeline, demoTrends } from './data/demo'
import { api } from './services/api'
import type { ArchitectureTimeline, DecisionHistory, HistoricalContext, RecurringDiscussion, TechnologyTrend } from './types'

/* ─── Utility helpers ─── */
const fmt = (d?: string | null) => d
  ? new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(d))
  : '—'

/* ─── Reusable Primitives ─── */
function SectionHeader({ eyebrow, title, desc, action }: {
  eyebrow: string; title: string; desc: string; action?: React.ReactNode
}) {
  return (
    <div className="section-header animate-fade-in">
      <div>
        <p className="section-eyebrow">{eyebrow}</p>
        <h1 className="section-title">{title}</h1>
        <p className="section-desc">{desc}</p>
      </div>
      {action}
    </div>
  )
}

function Panel({ children, className = '', style }: { children: React.ReactNode; className?: string; style?: React.CSSProperties }) {
  return <div className={`panel ${className}`} style={style}>{children}</div>
}

function Pill({ children, tone = 'slate' }: {
  children: React.ReactNode
  tone?: 'brand' | 'teal' | 'amber' | 'rose' | 'violet' | 'cyan' | 'green' | 'slate'
}) {
  return <span className={`pill pill-${tone}`}>{children}</span>
}

function Spinner() {
  return (
    <div className="flex min-h-52 items-center justify-center gap-3 text-sm text-slate-500">
      <LoaderCircle size={18} className="animate-spin text-indigo-400" />
      Loading intelligence…
    </div>
  )
}

/* ─── Inline SVG Bar Chart ─── */
function BarChart({ data, height = 140, colorClass = 'chart-bar' }: {
  data: { label: string; value: number; color?: string }[]
  height?: number
  colorClass?: string
}) {
  const max = Math.max(...data.map(d => d.value), 1)
  return (
    <div className="mt-4">
      <div className="flex items-end gap-2" style={{ height }}>
        {data.map((d, i) => (
          <div key={d.label} className="group flex flex-1 flex-col items-center gap-1">
            <span className="text-[11px] font-semibold text-slate-300 opacity-0 transition group-hover:opacity-100">
              {d.value}
            </span>
            <div
              className={`w-full rounded-t-md transition-all duration-700 ${d.color || colorClass}`}
              style={{
                height: `${(d.value / max) * (height - 20)}px`,
                animationDelay: `${i * 80}ms`,
              }}
            />
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-2">
        {data.map(d => (
          <div key={d.label} className="flex-1 text-center text-[10px] text-slate-600 truncate">{d.label}</div>
        ))}
      </div>
    </div>
  )
}

/* ─── Inline SVG Donut / Pie Chart ─── */
function DonutChart({ segments, size = 120, label }: {
  segments: { value: number; color: string; label: string }[]
  size?: number
  label?: string
}) {
  const total = segments.reduce((s, d) => s + d.value, 0)
  const r = 40; const cx = 50; const cy = 50
  let offset = -90
  const slices = segments.map(seg => {
    const pct = seg.value / total
    const deg = pct * 360
    const start = offset; offset += deg
    const toRad = (a: number) => (a * Math.PI) / 180
    const x1 = cx + r * Math.cos(toRad(start))
    const y1 = cy + r * Math.sin(toRad(start))
    const x2 = cx + r * Math.cos(toRad(start + deg))
    const y2 = cy + r * Math.sin(toRad(start + deg))
    const large = deg > 180 ? 1 : 0
    return { ...seg, path: `M${cx},${cy} L${x1.toFixed(2)},${y1.toFixed(2)} A${r},${r} 0 ${large},1 ${x2.toFixed(2)},${y2.toFixed(2)} Z`, pct }
  })
  return (
    <div className="flex items-center gap-6">
      <svg width={size} height={size} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="50" fill="rgba(13,17,38,0.8)" />
        {slices.map((s, i) => (
          <path key={i} d={s.path} fill={s.color} opacity="0.85" className="transition hover:opacity-100">
            <title>{s.label}: {s.value} ({(s.pct * 100).toFixed(1)}%)</title>
          </path>
        ))}
        <circle cx="50" cy="50" r="28" fill="rgba(6,11,24,0.95)" />
        {label && <text x="50" y="54" textAnchor="middle" fontSize="10" fill="#e2e8f0" fontWeight="700">{label}</text>}
      </svg>
      <div className="space-y-2">
        {segments.map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 rounded-sm flex-shrink-0" style={{ background: s.color }} />
            <span className="text-slate-400">{s.label}</span>
            <span className="ml-auto font-semibold text-slate-200">{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── Line Sparkline ─── */
function Sparkline({ values, color = '#6366f1', height = 40 }: {
  values: number[]; color?: string; height?: number
}) {
  const max = Math.max(...values)
  const min = Math.min(...values)
  const w = 120
  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * w
    const y = height - ((v - min) / (max - min + 1)) * height
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
  return (
    <svg width={w} height={height} viewBox={`0 0 ${w} ${height}`}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5"
        className="graph-line" strokeLinecap="round" strokeLinejoin="round" />
      <polyline
        points={`0,${height} ${points} ${w},${height}`}
        fill={color} fillOpacity="0.08"
        stroke="none"
      />
    </svg>
  )
}

/* ─── Pipeline Flowchart ─── */
/* ─── Vertical Pipeline Steps ─── */
function PipelineFlow() {
  const steps = [
    { icon: <GitBranch size={13}/>,  label: 'Sources',      sub: 'GitHub · Slack · Markdown',    color: '#6366f1', num: '01' },
    { icon: <Route size={13}/>,       label: 'Ingest',       sub: 'Normalize → Artifact queue',   color: '#8b5cf6', num: '02' },
    { icon: <Sparkles size={13}/>,    label: 'Extract',      sub: 'EKPP · Ollama / Demo brain',   color: '#14b8a6', num: '03' },
    { icon: <DatabaseZap size={13}/>, label: 'Memory',       sub: 'Supermemory @ localhost:6767', color: '#06b6d4', num: '04' },
    { icon: <Bot size={13}/>,         label: 'Intelligence', sub: 'Evidence-backed Q&A + trends', color: '#f59e0b', num: '05' },
  ]
  return (
    <div className="space-y-1.5">
      {steps.map((s, i) => (
        <div key={s.label} className="flex items-center gap-2 animate-fade-in" style={{ animationDelay: `${i * 90}ms` }}>
          <div className="flex flex-col items-center" style={{ width: 28 }}>
            <div className="grid h-7 w-7 flex-shrink-0 place-items-center rounded-lg text-[10px] font-black"
              style={{ background: `${s.color}20`, color: s.color, border: `1px solid ${s.color}35` }}>
              {s.num}
            </div>
            {i < steps.length - 1 && (
              <div style={{ width: 1, height: 8, background: `linear-gradient(to bottom, ${s.color}40, transparent)`, margin: '2px 0' }} />
            )}
          </div>
          <div className="flex flex-1 items-center gap-2 rounded-lg px-2.5 py-2"
            style={{ background: `${s.color}09`, border: `1px solid ${s.color}20` }}>
            <span style={{ color: s.color }}>{s.icon}</span>
            <div className="min-w-0">
              <p className="text-[11px] font-bold leading-tight" style={{ color: s.color }}>{s.label}</p>
              <p className="truncate text-[10px] text-slate-600">{s.sub}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

/* ─── Enhanced Radial Mindmap ─── */
function Mindmap() {
  const cx = 160; const cy = 118
  const satellites = [
    { label: 'GitHub PRs',    color: '#6366f1', angle: -90,  r: 82, icon: '🐙', desc: 'PRs & commits' },
    { label: 'Slack Threads', color: '#8b5cf6', angle: -25,  r: 86, icon: '💬', desc: 'Discussions' },
    { label: 'Supermemory',   color: '#06b6d4', angle:  45,  r: 83, icon: '🧠', desc: ':6767' },
    { label: 'Decisions',     color: '#f59e0b', angle: 120,  r: 82, icon: '📜', desc: 'Traceability' },
    { label: 'Markdown ADRs', color: '#14b8a6', angle: 195,  r: 84, icon: '📝', desc: 'Architecture' },
    { label: 'Evidence',      color: '#f43f5e', angle: 255,  r: 82, icon: '🔍', desc: 'Source proof' },
  ].map(n => ({
    ...n,
    x: cx + n.r * Math.cos((n.angle * Math.PI) / 180),
    y: cy + n.r * Math.sin((n.angle * Math.PI) / 180),
  }))
  return (
    <svg viewBox="0 0 320 236" className="w-full" style={{ maxHeight: 230 }}>
      <defs>
        <radialGradient id="hubgr" cx="50%" cy="50%">
          <stop offset="0%" stopColor="rgba(99,102,241,0.5)" />
          <stop offset="100%" stopColor="rgba(99,102,241,0.04)" />
        </radialGradient>
        <filter id="glw">
          <feGaussianBlur stdDeviation="2.5" result="b"/>
          <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      {/* Orbit ring */}
      <circle cx={cx} cy={cy} r="88" fill="none" stroke="rgba(99,102,241,0.06)" strokeWidth="1" strokeDasharray="3 6"/>
      {/* Glow ring behind center */}
      <circle cx={cx} cy={cy} r="38" fill="rgba(99,102,241,0.06)" filter="url(#glw)"/>
      {/* Spoke lines */}
      {satellites.map((n, i) => (
        <line key={i} x1={cx} y1={cy} x2={n.x} y2={n.y}
          stroke={n.color} strokeOpacity="0.4" strokeWidth="1.3"
          strokeDasharray="5 3" className="graph-line"
          style={{ animationDelay: `${i * 110}ms` }}/>
      ))}
      {/* Center hub */}
      <circle cx={cx} cy={cy} r="30" fill="url(#hubgr)" stroke="#6366f1" strokeWidth="1.5" filter="url(#glw)"/>
      <circle cx={cx} cy={cy} r="24" fill="rgba(7,10,26,0.94)" stroke="rgba(99,102,241,0.35)" strokeWidth="0.8"/>
      <text x={cx} y={cy-5} textAnchor="middle" fontSize="9" fill="#818cf8" fontWeight="800">Decision</text>
      <text x={cx} y={cy+7} textAnchor="middle" fontSize="9" fill="#818cf8" fontWeight="800">Lens 🧠</text>
      {/* Satellite nodes */}
      {satellites.map((n, i) => (
        <g key={i} className="graph-node" style={{ animationDelay: `${i * 80 + 400}ms` }}>
          <circle cx={n.x} cy={n.y} r="22" fill={`${n.color}12`} filter="url(#glw)"/>
          <circle cx={n.x} cy={n.y} r="20" fill="rgba(7,10,26,0.95)" stroke={n.color} strokeWidth="1.3"/>
          <text x={n.x} y={n.y - 5} textAnchor="middle" fontSize="10">{n.icon}</text>
          <text x={n.x} y={n.y + 6} textAnchor="middle" fontSize="5.8" fill={n.color} fontWeight="700">{n.label}</text>
          <text x={n.x} y={n.y + 13} textAnchor="middle" fontSize="4.5" fill="#475569">{n.desc}</text>
        </g>
      ))}
    </svg>
  )
}


/* ─── Memory type for session ─── */
type SessionMemory = {
  id: string; title: string; summary: string; entity: string
  kind: 'decision' | 'tradeoff' | 'alternative' | 'architecture_change' | 'open_question' | 'document'
  source: string; evidence: string; timestamp: string
}
const kindLabel = (k: SessionMemory['kind']) => k.replace(/_/g, ' ')
const readFile = (f: File) => new Promise<string>((res, rej) => {
  const r = new FileReader(); r.onload = () => res(String(r.result ?? '')); r.onerror = rej; r.readAsText(f)
})
const guessEntity = (t: string) =>
  ['Supermemory','Supabase','Redis','Kafka','PostgreSQL','GitHub','Slack','Ollama','RLS','Stripe','Firebase']
    .find(e => t.toLowerCase().includes(e.toLowerCase())) ?? 'Engineering'

function extractLocalMemories(filename: string, text: string): SessionMemory[] {
  const rows = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
  const patterns: [SessionMemory['kind'], RegExp][] = [
    ['decision',           /(?:^|\b)Decision\s*:\s*(.+)/i],
    ['tradeoff',           /(?:^|\b)Tradeoff\s*:\s*(.+)/i],
    ['alternative',        /(?:^|\b)Alternative\s*:\s*(.+)/i],
    ['architecture_change',/(?:^|\b)Architecture Change\s*:\s*(.+)/i],
    ['open_question',      /(?:^|\b)Open Question\s*:\s*(.+)/i],
  ]
  const extracted = rows.flatMap((line, idx) =>
    patterns.flatMap(([kind, pat]) => {
      const m = line.match(pat)
      if (!m) return []
      return [{ id: `${filename}-${kind}-${idx}`, title: m[1].trim(), summary: `${kindLabel(kind)} from ${filename}.`,
        entity: guessEntity(line), kind, source: filename, evidence: line, timestamp: new Date().toISOString() }]
    })
  )
  if (extracted.length) return extracted
  const heading = rows.find(l => l.startsWith('#'))?.replace(/^#+\s*/, '') || filename
  return [{ id: `${filename}-doc-${Date.now()}`, title: heading,
    summary: `Markdown captured as local memory. Add "Decision:" lines for richer extraction.`,
    entity: guessEntity(text), kind: 'document', source: filename,
    evidence: rows.find(l => !l.startsWith('#')) || '', timestamp: new Date().toISOString() }]
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: DASHBOARD
═══════════════════════════════════════════════════════════════════ */
function Dashboard({ onSearch }: { onSearch?: () => void }) {
  const stats = [
    { icon: <Target size={20}/>, value: '48', label: 'Decisions captured',     delta: '+12 this week', color: '#6366f1', sparkline: [12,18,14,22,19,27,31,25,35,38,42,48] },
    { icon: <Activity size={20}/>, value: '31', label: 'Tradeoffs tracked',    delta: '+8 this week',  color: '#14b8a6', sparkline: [5,9,11,13,14,18,20,22,25,27,29,31] },
    { icon: <Layers size={20}/>,   value: '16', label: 'Architecture changes', delta: '+3 this week',  color: '#8b5cf6', sparkline: [2,4,5,7,8,9,10,11,13,14,15,16] },
    { icon: <Users size={20}/>,    value: '142', label: 'Artifacts ingested',  delta: '+24 this week', color: '#f59e0b', sparkline: [30,45,52,60,70,85,95,108,118,128,136,142] },
  ]

  const sources = [
    { icon: <GitBranch size={16}/>, name: 'GitHub', count: '21 artifacts', pct: 82, color: '#6366f1', desc: 'PRs, commits, comments' },
    { icon: <MessageSquare size={16}/>, name: 'Slack',  count: '14 threads',  pct: 64, color: '#8b5cf6', desc: 'Engineering discussions' },
    { icon: <FileText size={16}/>, name: 'Markdown', count: '7 documents',  pct: 38, color: '#14b8a6', desc: 'ADRs & RFCs' },
  ]

  const recentActivity = [
    { type: 'ADR Updated',           name: 'Auth & Tenant Authorization ADR-001', time: '2h ago',    icon: <FileText size={15}/>,      color: '#6366f1' },
    { type: 'Pull Request Merged',   name: 'Persist Stripe envelopes → Kafka',    time: '5h ago',    icon: <GitPullRequest size={15}/>, color: '#14b8a6' },
    { type: 'Slack Discussion',      name: 'Redis session revocation strategy',    time: 'Yesterday', icon: <MessageSquare size={15}/>, color: '#f59e0b' },
    { type: 'Knowledge Extracted',   name: 'PostgreSQL RLS multi-tenant policy',  time: '2d ago',    icon: <Sparkles size={15}/>,      color: '#8b5cf6' },
  ]

  const techData = [
    { label: 'Redis',       value: 24, color: 'chart-bar' },
    { label: 'PostgreSQL',  value: 21, color: 'chart-bar-teal' },
    { label: 'Kafka',       value: 17, color: 'chart-bar-violet' },
    { label: 'Supabase',    value: 14, color: 'chart-bar-amber' },
    { label: 'Firebase',    value: 6,  color: 'chart-bar-rose' },
  ]

  const donutData = [
    { label: 'Decisions',   value: 48, color: '#6366f1' },
    { label: 'Tradeoffs',   value: 31, color: '#14b8a6' },
    { label: 'Arch changes',value: 16, color: '#8b5cf6' },
    { label: 'Recurring',   value: 18, color: '#f59e0b' },
    { label: 'Open Qs',     value: 6,  color: '#f43f5e' },
  ]

  return (
    <>
      {/* ── Hero Banner ── */}
      <div className="panel-glow relative mb-6 overflow-hidden rounded-2xl p-6 sm:p-8 animate-fade-in">
        {/* Decorative orbs */}
        <div className="pointer-events-none absolute right-0 top-0 h-64 w-64 rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, #6366f1, transparent)', transform: 'translate(30%, -30%)' }} />
        <div className="pointer-events-none absolute bottom-0 left-1/3 h-40 w-40 rounded-full opacity-8"
          style={{ background: 'radial-gradient(circle, #14b8a6, transparent)', transform: 'translateY(40%)' }} />

        <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <div className="mb-4 flex flex-wrap gap-2">
              <Pill tone="green">🟢 Supermemory Active</Pill>
              <Pill tone="brand">🧠 AI-Powered Memory</Pill>
              <Pill tone="teal">⚡ Hackathon Ready</Pill>
            </div>
            <p className="section-eyebrow">DecisionLens</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight text-slate-50 sm:text-4xl lg:text-5xl leading-tight">
              Turn engineering{' '}
              <span className="gradient-text">conversations</span>{' '}
              into <span className="gradient-text-warm">institutional memory.</span>
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-400">
              DecisionLens watches GitHub PRs, Slack threads, and Markdown ADRs — extracts structured
              knowledge objects — and stores them in <strong className="text-indigo-400">Supermemory</strong> for
              instant evidence-backed retrieval. Never lose context again.
            </p>

            {/* Stat pills row */}
            <div className="mt-6 grid grid-cols-3 gap-3 sm:grid-cols-3">
              {[['48','Decisions'],['31','Tradeoffs'],['16','Arch Changes']].map(([v,l]) => (
                <div key={l} className="stat-card text-center animate-count">
                  <p className="text-2xl font-black text-slate-50">{v}</p>
                  <p className="mt-1 text-[11px] text-slate-500">{l}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Pipeline flowchart */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
              <Workflow size={16} className="text-teal-400" />
              Live pipeline
            </div>
            <PipelineFlow />
            <div className="mt-2">
              <Mindmap />
            </div>
          </div>
        </div>
      </div>

      {/* ── Stats Row ── */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((s, i) => (
          <div
            key={s.label}
            className="stat-card animate-fade-in"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div className="flex items-start justify-between">
              <div
                className="grid h-10 w-10 place-items-center rounded-xl"
                style={{ background: `${s.color}22`, color: s.color }}
              >
                {s.icon}
              </div>
              <Sparkline values={s.sparkline} color={s.color} />
            </div>
            <p className="mt-3 text-2xl font-black text-slate-50">{s.value}</p>
            <p className="text-xs text-slate-500">{s.label}</p>
            <p className="mt-1 flex items-center gap-1 text-[11px] text-emerald-400">
              <TrendingUp size={11} />{s.delta}
            </p>
          </div>
        ))}
      </div>

      {/* ── Main content grid ── */}
      <div className="grid gap-5 xl:grid-cols-[1.4fr_0.6fr]">
        {/* Charts column */}
        <div className="space-y-5">
          {/* Bar chart */}
          <Panel className="p-5 animate-fade-in delay-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400">📊 Discussion Volume</p>
                <h2 className="mt-1 text-base font-bold text-slate-100">Technology Mentions</h2>
              </div>
              <Pill tone="brand">Last 90 days</Pill>
            </div>
            <BarChart data={techData} height={130} />
          </Panel>

          {/* Activity feed */}
          <Panel className="p-5 animate-fade-in delay-300">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-100">⚡ Recent Activity</h2>
              <Pill tone="teal">Live feed</Pill>
            </div>
            <div className="mt-4 space-y-0">
              {recentActivity.map(({ type, name, time, icon, color }, i) => (
                <div key={name} className="flex items-center gap-3 border-b border-white/5 py-3.5 last:border-0 animate-fade-in"
                  style={{ animationDelay: `${300 + i * 60}ms` }}>
                  <div className="grid h-9 w-9 flex-shrink-0 place-items-center rounded-xl"
                    style={{ background: `${color}18`, color }}>
                    {icon}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[11px] uppercase tracking-wide text-slate-600">{type}</p>
                    <p className="truncate text-sm font-medium text-slate-200">{name}</p>
                  </div>
                  <span className="flex-shrink-0 text-xs text-slate-600">{time}</span>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        {/* Right column */}
        <div className="space-y-5">
          {/* Donut chart */}
          <Panel className="p-5 animate-fade-in delay-200">
            <h2 className="mb-4 text-base font-bold text-slate-100">🧩 Knowledge Mix</h2>
            <DonutChart segments={donutData} label="119" />
          </Panel>

          {/* Sources */}
          <Panel className="p-5 animate-fade-in delay-300">
            <h2 className="mb-4 text-base font-bold text-slate-100">🔌 Active Sources</h2>
            <div className="space-y-4">
              {sources.map(s => (
                <div key={s.name}>
                  <div className="mb-1.5 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-slate-300" style={{ color: s.color }}>
                      {s.icon} {s.name}
                    </span>
                    <span className="text-slate-500">{s.count}</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${s.pct}%`, background: s.color }} />
                  </div>
                  <p className="mt-1 text-[10px] text-slate-600">{s.desc}</p>
                </div>
              ))}
            </div>
          </Panel>

          {/* Judge demo card */}
          <Panel className="p-5 animate-fade-in delay-400">
            <div className="flex items-center gap-2 text-sm font-bold text-slate-100">
              <Award size={16} className="text-amber-400" />
              Judge Demo Path
            </div>
            {[
              'Ask why Redis was chosen for sessions.',
              'Open the Architecture Timeline.',
              'Show Firebase as a rejected alternative.',
              'Upload an ADR via Markdown Upload.',
            ].map((step, i) => (
              <div key={step} className="mt-3 flex gap-3 border-t border-white/5 pt-3 text-xs first:mt-2 first:border-0 first:pt-0">
                <span className="grid h-5 w-5 flex-shrink-0 place-items-center rounded-lg text-[10px] font-bold text-emerald-400"
                  style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.2)' }}>
                  {i + 1}
                </span>
                <span className="text-slate-400 leading-relaxed">{step}</span>
              </div>
            ))}
          </Panel>
        </div>
      </div>

      {/* ── Architecture Banner ── */}
      <div className="mt-5 panel p-5 animate-fade-in delay-500">
        <div className="flex items-center gap-2 mb-4">
          <Cpu size={16} className="text-indigo-400" />
          <h2 className="text-sm font-bold text-slate-100">System Architecture</h2>
          <Pill tone="brand">Powered by Supermemory</Pill>
        </div>
        <div className="code-block text-[11px] leading-6">
          <span className="cmt"># DecisionLens Full Pipeline</span>{'\n'}
          GitHub · Slack · Markdown{'\n'}
          {'  '}<span className="kw">→</span> Source Connectors <span className="cmt">  # Normalize into Artifacts</span>{'\n'}
          {'  '}<span className="kw">→</span> Ingestion Engine  <span className="cmt">  # Queue + deduplicate</span>{'\n'}
          {'  '}<span className="kw">→</span> <span className="str">EKPP (Ollama / Demo)</span>  <span className="cmt"># Extract knowledge objects</span>{'\n'}
          {'  '}<span className="kw">→</span> <span className="num">Supermemory :6767</span>   <span className="cmt"># Long-term semantic memory</span>{'\n'}
          {'  '}<span className="kw">→</span> Intelligence Layer <span className="cmt">  # Timeline · Trends · Q&A</span>{'\n'}
          {'  '}<span className="kw">→</span> React Dashboard   <span className="cmt">  # You are here ✦</span>
        </div>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: MEMORY GRAPH
═══════════════════════════════════════════════════════════════════ */

// Graph data constants
const MG_NODES = [
  { id: 'DecisionLens', x: 50,  y: 50,  r: 8.5, type: 'hub',         color: '#6366f1', label: 'DecisionLens 🧠', desc: 'Central memory hub' },
  { id: 'Supermemory',  x: 50,  y: 17,  r: 6.5, type: 'memory',      color: '#818cf8', label: 'Supermemory',     desc: 'Semantic memory @ :6767' },
  { id: 'Redis',        x: 80,  y: 30,  r: 6,   type: 'decision',    color: '#f59e0b', label: 'Redis ⚡',         desc: 'Session revocation' },
  { id: 'Kafka',        x: 85,  y: 58,  r: 5.5, type: 'decision',    color: '#8b5cf6', label: 'Kafka 📨',         desc: 'Event streaming' },
  { id: 'PostgreSQL',   x: 50,  y: 83,  r: 6,   type: 'decision',    color: '#06b6d4', label: 'PostgreSQL 🐘',   desc: 'Primary DB' },
  { id: 'Supabase',     x: 20,  y: 58,  r: 5.5, type: 'source',      color: '#14b8a6', label: 'Supabase 🗄️',    desc: 'Auth + RLS' },
  { id: 'GitHub',       x: 18,  y: 30,  r: 5,   type: 'source',      color: '#818cf8', label: 'GitHub 🐙',       desc: 'PRs & commits' },
  { id: 'Firebase',     x: 70,  y: 10,  r: 4,   type: 'alternative', color: '#f43f5e', label: 'Firebase 🔥',     desc: '⛔ Rejected' },
  { id: 'Stripe',       x: 88,  y: 42,  r: 4,   type: 'source',      color: '#10b981', label: 'Stripe 💳',       desc: 'Payment events' },
  { id: 'Slack',        x: 10,  y: 45,  r: 4,   type: 'source',      color: '#818cf8', label: 'Slack 💬',        desc: 'Eng. threads' },
  { id: 'Markdown',     x: 30,  y: 90,  r: 3.8, type: 'source',      color: '#14b8a6', label: 'ADRs 📝',         desc: 'Architecture docs' },
  { id: 'JWT',          x: 70,  y: 90,  r: 3.8, type: 'alternative', color: '#f43f5e', label: 'JWT ⛔',           desc: 'Rejected alt.' },
]

const MG_EDGES = [
  ['DecisionLens','Supermemory'],['DecisionLens','Redis'],['DecisionLens','Kafka'],
  ['DecisionLens','PostgreSQL'],['DecisionLens','Supabase'],['DecisionLens','GitHub'],
  ['Supermemory','Redis'],['Supermemory','PostgreSQL'],
  ['Redis','Kafka'],['Supabase','PostgreSQL'],
  ['GitHub','Slack'],['Stripe','Kafka'],
  ['Firebase','Supabase'],['JWT','Redis'],['Markdown','PostgreSQL'],
]

const MG_DETAILS: Record<string, { decisions: string[]; source: string; tradeoff: string; status: 'active'|'rejected'|'hub'|'source' }> = {
  DecisionLens:{ decisions:['Central engineering memory OS — coordinates extraction + retrieval'],                       source:'Platform core',      tradeoff:'Connects all sources to Supermemory',               status:'hub' },
  Supermemory: { decisions:['Stores all knowledge objects as semantic memories'],                                         source:'localhost:6767',     tradeoff:'Long-term memory backbone — no cloud required',     status:'active' },
  Redis:       { decisions:['Use Redis for immediate session revocation'],                                                 source:'slack:C-PLATFORM',   tradeoff:'Operational overhead vs stateless JWT',             status:'active' },
  Kafka:       { decisions:['Kafka as durable event boundary for billing & audit'],                                       source:'github:pr-184',      tradeoff:'Complexity vs guaranteed delivery',                 status:'active' },
  PostgreSQL:  { decisions:['Primary consistency boundary for all writes'],                                               source:'github:bc3d881',     tradeoff:'ACID guarantees at cost of horizontal scale',       status:'active' },
  Supabase:    { decisions:['Supabase Auth + PostgreSQL RLS for multi-tenant isolation'],                                 source:'markdown:ADR-001',   tradeoff:'Debugging RLS policies is complex',                 status:'active' },
  GitHub:      { decisions:['Source of PR, commit, and comment knowledge artifacts'],                                     source:'github-connector',   tradeoff:'Needs token to access private repos',              status:'source' },
  Firebase:    { decisions:['❌ Considered before Supabase — rejected due to vendor lock-in'],                            source:'slack:C-PLATFORM',   tradeoff:'Cost at scale + limited self-hosting options',      status:'rejected' },
  Stripe:      { decisions:['Stripe webhook envelopes persisted before Kafka publication'],                               source:'github:pr-184',      tradeoff:'Idempotent payment processing',                     status:'source' },
  Slack:       { decisions:['Engineering thread extraction via Slack connector'],                                         source:'slack-connector',    tradeoff:'Requires bot token + signing secret',              status:'source' },
  Markdown:    { decisions:['ADR and RFC files ingested as memory artifacts'],                                            source:'markdown-connector', tradeoff:'Requires "Decision:" pattern for extraction',      status:'source' },
  JWT:         { decisions:['❌ Fully stateless JWT sessions rejected — cannot revoke'],                                  source:'slack:C-PLATFORM',   tradeoff:'Cannot revoke immediately — chose Redis instead',  status:'rejected' },
}

function MemoryGraph({ memories }: { memories: SessionMemory[] }) {
  const uploadedNodes = memories.slice(-3).map((m, i) => ({
    id: `uploaded-${i}`, x: 25 + i * 25, y: 97,
    r: 3.5, type: m.kind as string, color: '#10b981',
    label: `📄 ${m.entity.slice(0,8)}`, desc: m.kind.replace(/_/g,' '),
  }))
  const allNodes = [...MG_NODES, ...uploadedNodes]
  const [selId, setSelId] = useState<string>('Redis')
  const sel = allNodes.find(n => n.id === selId) ?? MG_NODES[2]
  const detail = MG_DETAILS[selId]

  const statusBadge = {
    active:   { tone: 'green'  as const, label: '✅ Adopted' },
    rejected: { tone: 'rose'   as const, label: '⛔ Rejected' },
    hub:      { tone: 'brand'  as const, label: '🧠 Hub' },
    source:   { tone: 'teal'   as const, label: '🔌 Source' },
  }[detail?.status ?? 'source']

  return (
    <>
      <SectionHeader eyebrow="Knowledge Graph" title="🕸️ Memory Graph"
        desc="Interactive hub-and-spoke knowledge map. Click any node to inspect decisions, tradeoffs, and source evidence."
        action={<Pill tone={memories.length ? 'teal' : 'brand'}>{memories.length ? `+${memories.length} uploaded` : 'Demo corpus'}</Pill>}
      />
      <div className="grid gap-5 xl:grid-cols-[1.6fr_0.4fr]">
        {/* ── SVG Graph ── */}
        <Panel className="overflow-hidden p-0 animate-fade-in">
          <div className="flex items-center justify-between px-5 py-3" style={{ borderBottom: '1px solid rgba(99,102,241,0.12)' }}>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
              <Network size={15} className="text-indigo-400" />
              Decision memory map
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-600">{allNodes.length} nodes · {MG_EDGES.length + uploadedNodes.length} edges</span>
              <Pill tone="violet">click to explore</Pill>
            </div>
          </div>
          <svg viewBox="0 0 100 105" className="w-full cursor-pointer" style={{ height: 500 }}>
            <defs>
              <radialGradient id="mg-bg" cx="50%" cy="48%">
                <stop offset="0%" stopColor="rgba(99,102,241,0.08)"/>
                <stop offset="60%" stopColor="rgba(6,8,22,0)"/>
              </radialGradient>
              <filter id="mg-glow" x="-60%" y="-60%" width="220%" height="220%">
                <feGaussianBlur stdDeviation="1.2" result="b"/>
                <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
              <filter id="mg-glow-sm" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="0.6" result="b"/>
                <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
              <pattern id="mg-dots" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="0.2" fill="rgba(99,102,241,0.18)"/>
              </pattern>
            </defs>

            {/* Background */}
            <rect x="0" y="0" width="100" height="105" fill="rgba(5,8,22,1)"/>
            <rect x="0" y="0" width="100" height="105" fill="url(#mg-dots)"/>
            <ellipse cx="50" cy="50" rx="48" ry="46" fill="url(#mg-bg)"/>

            {/* Edges */}
            {MG_EDGES.map(([a, b], i) => {
              const na = allNodes.find(n => n.id === a)
              const nb = allNodes.find(n => n.id === b)
              if (!na || !nb) return null
              const isActive = selId === a || selId === b
              return (
                <line key={i}
                  x1={na.x} y1={na.y} x2={nb.x} y2={nb.y}
                  stroke={isActive ? (na as any).color ?? '#6366f1' : 'rgba(99,102,241,0.2)'}
                  strokeWidth={isActive ? 0.55 : 0.22}
                  strokeOpacity={isActive ? 0.9 : 1}
                  strokeDasharray={isActive ? '' : '1.5 2'}
                  className="graph-line"
                  style={{ animationDelay: `${i * 50}ms` }}
                />
              )
            })}
            {/* Uploaded node edges */}
            {uploadedNodes.map((un, i) => {
              const hub = allNodes[0]
              return <line key={`ue${i}`} x1={hub.x} y1={hub.y} x2={un.x} y2={un.y}
                stroke="#10b981" strokeWidth="0.25" strokeOpacity="0.5" strokeDasharray="2 2"/>
            })}

            {/* Nodes */}
            {allNodes.map((n, i) => {
              const isSelected = selId === n.id
              const c = (n as any).color ?? '#6366f1'
              const r = (n as any).r ?? 4
              const isHub = n.type === 'hub'
              return (
                <g key={n.id} onClick={() => setSelId(n.id)}
                  style={{ cursor: 'pointer', animationDelay: `${i * 50}ms` }} className="graph-node">
                  {/* Outer pulse ring */}
                  {isSelected && <circle cx={n.x} cy={n.y} r={r + 5} fill={c} opacity="0.07"/>}
                  {isSelected && <circle cx={n.x} cy={n.y} r={r + 3.5} fill="none" stroke={c} strokeWidth="0.5" strokeOpacity="0.4"/>}
                  {/* Glow */}
                  <circle cx={n.x} cy={n.y} r={r + 1.5} fill={c}
                    opacity={isSelected ? 0.22 : isHub ? 0.12 : 0.04}
                    filter={isSelected || isHub ? 'url(#mg-glow)' : 'url(#mg-glow-sm)'}/>
                  {/* Body */}
                  <circle cx={n.x} cy={n.y} r={r}
                    fill={isHub ? `rgba(70,60,200,0.35)` : `rgba(5,8,22,0.97)`}
                    stroke={c}
                    strokeWidth={isSelected ? 0.85 : isHub ? 1.1 : 0.45}
                    filter={isSelected ? 'url(#mg-glow-sm)' : undefined}
                  />
                  {/* Label */}
                  <text x={n.x} y={n.y + (r > 5 ? 3 : 2.5)} textAnchor="middle"
                    fontSize={isHub ? 3.5 : r > 5 ? 2.9 : 2.6}
                    fill={isSelected ? c : isHub ? '#a5b4fc' : '#64748b'}
                    fontWeight={isSelected || isHub ? '700' : '500'}>
                    {(n as any).label ?? n.id}
                  </text>
                </g>
              )
            })}
          </svg>
        </Panel>

        {/* ── Detail Panel ── */}
        <div className="space-y-3">
          <Panel className="p-5 animate-fade-in">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="h-3 w-3 rounded-full flex-shrink-0" style={{ background: sel.color, boxShadow: `0 0 10px ${sel.color}` }}/>
              <h2 className="text-base font-black text-slate-100">{sel.id}</h2>
            </div>
            {detail && (
              <>
                <Pill tone={statusBadge.tone}>{statusBadge.label}</Pill>
                <div className="mt-3 space-y-3">
                  {detail.decisions.map(d => (
                    <div key={d} className="rounded-xl p-3 text-xs text-slate-300 leading-5"
                      style={{ background: `${sel.color}10`, border: `1px solid ${sel.color}20` }}>
                      {d}
                    </div>
                  ))}
                </div>
                <div className="mt-3 space-y-2">
                  <div className="flex items-start gap-2 text-xs text-slate-500">
                    <span className="text-amber-400 flex-shrink-0 mt-0.5">⚖️</span>
                    <span className="leading-5">{detail.tradeoff}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-600">
                    <span className="text-indigo-400">🔗</span>
                    <code className="text-[10px] text-indigo-400">{detail.source}</code>
                  </div>
                </div>
              </>
            )}
            {!detail && (
              <p className="text-xs text-slate-500 leading-5">
                Uploaded memory node. Click other nodes to explore the seeded corpus.
              </p>
            )}
          </Panel>

          <Panel className="p-4 animate-fade-in delay-100">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-widest text-slate-600">Legend</p>
            {[
              { label: 'Hub',         color: '#6366f1' },
              { label: 'Decision',    color: '#f59e0b' },
              { label: 'Rejected',    color: '#f43f5e' },
              { label: 'Memory',      color: '#818cf8' },
              { label: 'Source',      color: '#14b8a6' },
              { label: 'Uploaded',    color: '#10b981' },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-2 py-1 text-xs text-slate-500">
                <span className="h-2 w-2 rounded-full flex-shrink-0" style={{ background: item.color }}/>
                {item.label}
              </div>
            ))}
          </Panel>

          <Panel className="p-4 animate-fade-in delay-200">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-widest text-slate-600">Knowledge Mix</p>
            {[
              { kind: 'Decisions',   count: 7,  color: '#f59e0b' },
              { kind: 'Tradeoffs',   count: 5,  color: '#14b8a6' },
              { kind: 'Alternatives',count: 3,  color: '#f43f5e' },
              { kind: 'Sources',     count: 5,  color: '#818cf8' },
              ...memories.reduce<{kind:string;count:number;color:string}[]>((acc,m) => {
                const x = acc.find(a => a.kind === kindLabel(m.kind))
                if (x) x.count++; else acc.push({ kind: kindLabel(m.kind), count: 1, color: '#10b981' })
                return acc
              }, []),
            ].map(item => (
              <div key={item.kind} className="mb-2.5">
                <div className="mb-1 flex items-center justify-between text-[11px]">
                  <span className="capitalize text-slate-500">{item.kind}</span>
                  <span className="font-semibold text-slate-300">{item.count}</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(100, item.count * 14)}%`, background: item.color }}/>
                </div>
              </div>
            ))}
          </Panel>
        </div>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: TIMELINE
═══════════════════════════════════════════════════════════════════ */
function Timeline() {
  const [items, setItems] = useState<ArchitectureTimeline[]>(demoTimeline)
  const [loading, setLoading] = useState(false)
  useEffect(() => {
    setLoading(true)
    api.timeline().then(setItems).catch(() => {}).finally(() => setLoading(false))
  }, [])
  const events = items[0]?.events ?? []
  const colors = ['#6366f1', '#14b8a6', '#8b5cf6', '#f59e0b', '#f43f5e', '#06b6d4']

  return (
    <>
      <SectionHeader eyebrow="Architecture Intelligence" title="🕰️ Architecture Timeline"
        desc="A source-grounded, chronological evolution of the platform's key technical boundaries and decisions." />
      {loading ? <Spinner /> : (
        <div className="grid gap-5 lg:grid-cols-[2fr_1fr]">
          <Panel className="p-6 animate-fade-in">
            <div className="relative ml-3 border-l border-indigo-500/20 pl-6">
              {events.map((ev, i) => (
                <div key={ev.timestamp} className="relative pb-10 last:pb-0 animate-slide-in"
                  style={{ animationDelay: `${i * 100}ms` }}>
                  <div className="timeline-dot absolute -left-[29px] top-1" style={{ background: colors[i % colors.length], borderColor: `${colors[i % colors.length]}40`, boxShadow: `0 0 12px ${colors[i % colors.length]}50` }} />
                  <span className="text-xs font-semibold" style={{ color: colors[i % colors.length] }}>
                    {fmt(ev.timestamp)}
                  </span>
                  <h2 className="mt-2 text-base font-bold text-slate-100">{ev.decision}</h2>
                  <p className="mt-1.5 max-w-lg text-sm leading-6 text-slate-500">{ev.reason}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Pill tone="brand">{Math.round(ev.confidence * 100)}% confidence</Pill>
                    <Pill tone="teal">Evidence attached</Pill>
                    {ev.evidence?.[0] && (
                      <Pill tone="violet">Source: {ev.evidence[0].artifact_reference?.split(':')[0] ?? 'artifact'}</Pill>
                    )}
                  </div>
                  {ev.evidence?.[0] && (
                    <blockquote className="evidence-quote mt-3 text-[11px]">
                      {ev.evidence[0].content}
                    </blockquote>
                  )}
                </div>
              ))}
            </div>
          </Panel>

          {/* Side panel: timeline overview chart */}
          <div className="space-y-4">
            <Panel className="p-5 animate-fade-in delay-100">
              <h2 className="mb-4 text-sm font-bold text-slate-100">📊 Confidence Distribution</h2>
              <BarChart
                data={events.map((ev, i) => ({
                  label: `Event ${i + 1}`,
                  value: Math.round(ev.confidence * 100),
                  color: `chart-bar${i % 2 === 0 ? '' : '-teal'}`,
                }))}
                height={110}
              />
            </Panel>
            <Panel className="p-5 animate-fade-in delay-200">
              <h2 className="mb-4 text-sm font-bold text-slate-100">🏗️ Architecture Summary</h2>
              <div className="space-y-3">
                {[
                  { label: 'Auth Layer',    tech: 'Supabase + RLS', status: 'Active',    color: '#10b981' },
                  { label: 'Cache Layer',   tech: 'Redis (5-min)',  status: 'Active',    color: '#10b981' },
                  { label: 'Events Layer',  tech: 'Kafka + Stripe', status: 'Active',    color: '#10b981' },
                  { label: 'Reports Layer', tech: 'Background jobs',status: 'Stable',    color: '#f59e0b' },
                ].map(r => (
                  <div key={r.label} className="flex items-center justify-between rounded-lg border border-white/6 p-3">
                    <div>
                      <p className="text-xs font-semibold text-slate-300">{r.label}</p>
                      <p className="text-[11px] text-slate-600">{r.tech}</p>
                    </div>
                    <span className="text-[10px] font-semibold" style={{ color: r.color }}>{r.status}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </div>
      )}
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: RECURRING DISCUSSIONS
═══════════════════════════════════════════════════════════════════ */
function Recurring() {
  const [items, setItems] = useState<RecurringDiscussion[]>(demoRecurring)
  useEffect(() => { api.recurring().then(setItems).catch(() => {}) }, [])

  const topicColors: Record<string, string> = { Redis: '#f59e0b', Kafka: '#8b5cf6', 'PostgreSQL RLS': '#06b6d4' }
  const heatData = items.map(i => ({ label: i.topic, value: i.discussion_count, color: 'chart-bar' }))

  return (
    <>
      <SectionHeader eyebrow="Patterns" title="🔁 Recurring Discussions"
        desc="Topics that surface repeatedly across pull requests, Slack threads, and architecture documents." />
      <div className="grid gap-5 lg:grid-cols-[1fr_0.45fr]">
        <div className="space-y-4">
          {items.map((item, i) => {
            const c = topicColors[item.topic] || '#6366f1'
            return (
              <Panel key={item.topic} className="p-5 animate-slide-in" style={{ animationDelay: `${i * 100}ms` }}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="grid h-10 w-10 place-items-center rounded-xl" style={{ background: `${c}18`, color: c }}>
                      <Flame size={18} />
                    </div>
                    <div>
                      <h2 className="font-bold text-slate-100">{item.topic}</h2>
                      <p className="mt-0.5 max-w-lg text-sm text-slate-500">{item.summary}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-black" style={{ color: c }}>{item.discussion_count}</p>
                    <p className="text-[11px] text-slate-600">occurrences</p>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Pill tone="green">{item.status ?? 'Active'}</Pill>
                  <Pill tone="slate">Last: {fmt(item.last_discussed)}</Pill>
                  <Pill tone="brand">Evidence available</Pill>
                </div>
                {/* mini progress */}
                <div className="mt-4">
                  <div className="mb-1 flex justify-between text-[11px] text-slate-600">
                    <span>Discussion intensity</span>
                    <span>{Math.round((item.discussion_count / 20) * 100)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${(item.discussion_count / 20) * 100}%`, background: c }} />
                  </div>
                </div>
              </Panel>
            )
          })}
        </div>

        <div className="space-y-4">
          <Panel className="p-5 animate-fade-in">
            <h2 className="mb-1 text-sm font-bold text-slate-100">📊 Discussion Frequency</h2>
            <p className="mb-2 text-[11px] text-slate-600">Mentions across all sources</p>
            <BarChart data={heatData} height={120} />
          </Panel>
          <Panel className="p-5 animate-fade-in delay-100">
            <h2 className="mb-4 text-sm font-bold text-slate-100">💡 Why Topics Recur</h2>
            {[
              { icon: '⚖️', label: 'Unresolved tradeoffs', desc: 'Core tradeoffs without clear winners' },
              { icon: '📐', label: 'Architectural drift',  desc: 'Systems diverging from original design' },
              { icon: '🧩', label: 'Complexity creep',     desc: 'Increasing system complexity over time' },
            ].map(item => (
              <div key={item.label} className="mt-3 flex items-start gap-3 border-t border-white/5 pt-3 first:mt-0 first:border-0 first:pt-0">
                <span className="text-lg">{item.icon}</span>
                <div>
                  <p className="text-xs font-semibold text-slate-300">{item.label}</p>
                  <p className="text-[11px] text-slate-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </Panel>
        </div>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: TECHNOLOGY TRENDS
═══════════════════════════════════════════════════════════════════ */
function Trends() {
  const [items, setItems] = useState<TechnologyTrend[]>(demoTrends)
  useEffect(() => { api.trends().then(setItems).catch(() => {}) }, [])
  const max = Math.max(...items.map(i => i.discussion_count), 1)
  const trendColors: Record<string, string> = { Redis: '#f59e0b', PostgreSQL: '#06b6d4', Kafka: '#8b5cf6', Firebase: '#f43f5e', Supabase: '#10b981' }

  return (
    <>
      <SectionHeader eyebrow="Signals" title="📈 Technology Trends"
        desc="Adoption, rejection, and discussion volume signals across the engineering stack." />
      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        {/* Bar chart card */}
        <Panel className="p-5 animate-fade-in">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-base font-bold text-slate-100">Discussion Volume</h2>
            <Pill tone="brand">Last 90 days</Pill>
          </div>
          <p className="text-xs text-slate-600 mb-4">Mentions across GitHub · Slack · Markdown</p>
          <div className="space-y-4">
            {items.map(item => {
              const c = trendColors[item.technology] || '#6366f1'
              return (
                <div key={item.technology}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full" style={{ background: c }} />
                      <span className="font-medium text-slate-200">{item.technology}</span>
                    </div>
                    <span className="text-xs text-slate-500">{item.discussion_count} mentions</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${(item.discussion_count / max) * 100}%`, background: c }} />
                  </div>
                </div>
              )
            })}
          </div>
          <div className="mt-6 border-t border-white/6 pt-5">
            <h3 className="mb-3 text-xs font-bold text-slate-400 uppercase tracking-wider">Acceptance Rate</h3>
            <BarChart
              data={items.map(item => ({
                label: item.technology,
                value: item.accepted_count,
                color: item.is_deprecated ? 'chart-bar-rose' : item.is_new ? 'chart-bar' : 'chart-bar-teal',
              }))}
              height={90}
            />
          </div>
        </Panel>

        {/* Adoption signals cards */}
        <div className="space-y-3">
          <Panel className="p-4 animate-fade-in delay-100">
            <h2 className="mb-4 text-sm font-bold text-slate-100">⚡ Adoption Signals</h2>
            {items.map(item => {
              const c = trendColors[item.technology] || '#6366f1'
              const badge = item.is_deprecated
                ? { label: '⛔ Deprecated', tone: 'rose' as const }
                : item.is_new
                  ? { label: '🆕 Recently introduced', tone: 'brand' as const }
                  : { label: '✅ Adopted', tone: 'green' as const }
              return (
                <div key={item.technology} className="flex items-center justify-between border-t border-white/5 py-3.5 first:border-0 first:pt-0">
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 grid place-items-center rounded-lg" style={{ background: `${c}15`, color: c }}>
                      <Server size={14} />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-200">{item.technology}</p>
                      <p className="text-[11px] text-slate-600">
                        {item.accepted_count} adopted · {item.rejected_count} rejected
                      </p>
                    </div>
                  </div>
                  <Pill tone={badge.tone}>{badge.label}</Pill>
                </div>
              )
            })}
          </Panel>

          {/* Pie chart */}
          <Panel className="p-5 animate-fade-in delay-200">
            <h2 className="mb-4 text-sm font-bold text-slate-100">🥧 Adoption vs Rejection</h2>
            <DonutChart
              size={100}
              label="Total"
              segments={[
                { label: 'Adopted',  value: items.reduce((s,i)=>s+i.accepted_count,0), color: '#10b981' },
                { label: 'Rejected', value: items.reduce((s,i)=>s+i.rejected_count,0), color: '#f43f5e' },
                { label: 'Pending',  value: 5, color: '#6366f1' },
              ]}
            />
          </Panel>
        </div>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: DECISION HISTORY
═══════════════════════════════════════════════════════════════════ */
function History() {
  const [query, setQuery] = useState('Supabase')
  const [items, setItems] = useState<DecisionHistory[]>(demoHistory())
  const search = () => api.history(query).then(d => setItems(d.length ? d : demoHistory(query))).catch(() => setItems(demoHistory(query)))

  return (
    <>
      <SectionHeader eyebrow="Decision Intelligence" title="📜 Decision History"
        desc="Trace a technology from its first proposal through every tradeoff and architecture change."
        action={
          <form onSubmit={e => { e.preventDefault(); search() }} className="flex gap-2">
            <input value={query} onChange={e => setQuery(e.target.value)} className="dl-input w-40" placeholder="Redis, Kafka…" />
            <button type="submit" className="btn-brand">Search</button>
          </form>
        }
      />
      {items.map(item => (
        <div key={item.title} className="grid gap-5 lg:grid-cols-3 animate-fade-in">
          <Panel className="p-6 lg:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/10 text-indigo-400">
                <HistoryIcon size={20} />
              </div>
              <div>
                <h2 className="font-bold text-slate-100">{item.title}</h2>
                <p className="text-sm text-slate-500">{item.summary}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 mb-5">
              {item.participants.map(p => (
                <span key={p} className="flex items-center gap-1.5 rounded-full border border-white/8 bg-white/4 px-3 py-1 text-xs text-slate-400">
                  <Users size={11} className="text-indigo-400" /> {p}
                </span>
              ))}
            </div>
            <div className="space-y-5">
              {item.history.map((ev, i) => (
                <div key={ev.timestamp} className="flex gap-4 animate-slide-in" style={{ animationDelay: `${i * 80}ms` }}>
                  <div className="flex flex-col items-center gap-1">
                    <div className="timeline-dot" />
                    {i < item.history.length - 1 && <div className="w-px flex-1 bg-indigo-500/10" />}
                  </div>
                  <div className="pb-5">
                    <span className="text-xs font-semibold text-indigo-400">{fmt(ev.timestamp)}</span>
                    <h3 className="mt-1 text-sm font-semibold text-slate-200">{ev.decision}</h3>
                    <p className="mt-1 text-xs leading-5 text-slate-500">{ev.reason}</p>
                    <div className="mt-2 flex gap-2">
                      <Pill tone="brand">{Math.round(ev.confidence * 100)}%</Pill>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <div className="space-y-4">
            <Panel className="p-5 animate-fade-in delay-100">
              <h2 className="mb-4 text-sm font-bold text-slate-100">⚖️ Tradeoffs</h2>
              {['RLS increases local debugging effort.', 'Redis adds operational ownership.'].map((t, i) => (
                <div key={i} className="mt-3 border-t border-white/5 pt-3 first:mt-0 first:border-0 first:pt-0">
                  <div className="flex items-start gap-2 text-xs text-slate-400">
                    <AlertCircle size={13} className="mt-0.5 flex-shrink-0 text-amber-400" />
                    {t}
                  </div>
                </div>
              ))}
            </Panel>
            <Panel className="p-5 animate-fade-in delay-200">
              <h2 className="mb-4 text-sm font-bold text-slate-100">🔀 Alternatives</h2>
              {['Standalone policy service', 'Fully stateless JWT sessions'].map(alt => (
                <div key={alt} className="mt-2">
                  <Pill tone="rose">⛔ {alt}</Pill>
                </div>
              ))}
            </Panel>
            <Panel className="p-5 animate-fade-in delay-300">
              <h2 className="mb-3 text-sm font-bold text-slate-100">📊 Confidence Timeline</h2>
              <BarChart
                data={item.history.map((ev, i) => ({
                  label: `E${i + 1}`,
                  value: Math.round(ev.confidence * 100),
                  color: 'chart-bar',
                }))}
                height={80}
              />
            </Panel>
          </div>
        </div>
      ))}
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: ASK DECISIONLENS
═══════════════════════════════════════════════════════════════════ */
function Ask({ memories }: { memories: SessionMemory[] }) {
  const [input, setInput] = useState('Why did we choose Redis for session management?')
  const [answer, setAnswer] = useState<HistoricalContext[]>(demoContext('Redis'))
  const [loading, setLoading] = useState(false)

  const suggested = [
    'Why did we choose Redis?',
    'Why did we use PostgreSQL RLS?',
    'What alternatives were rejected?',
    'Explain the Kafka decision.',
  ]

  const ask = async () => {
    if (!input.trim()) return
    setLoading(true)
    const localHits = memories.filter(m =>
      `${m.title} ${m.entity} ${m.evidence}`.toLowerCase()
        .includes(input.toLowerCase().split(/\s+/).find(w => w.length > 3) ?? input.toLowerCase())
    )
    if (localHits.length) {
      setAnswer([{
        ...demoContext(input)[0],
        title: `Local context: ${input}`,
        summary: `Found ${localHits.length} uploaded memory item${localHits.length === 1 ? '' : 's'} related to your question.`,
        previous_decisions: localHits.map(m => m.title),
        tradeoffs: localHits.map(m => m.evidence),
        alternatives: localHits.filter(m => m.kind === 'alternative').map(m => m.title),
        architecture_changes: localHits.filter(m => m.kind === 'architecture_change').map(m => m.title),
        related_entities: [...new Set(localHits.map(m => m.entity))],
        related_artifacts: [...new Set(localHits.map(m => m.source))],
      }])
      setLoading(false)
      return
    }
    try {
      const result = await api.query(input)
      const ctx = (result.historical_context as HistoricalContext[]) || []
      setAnswer(ctx.length ? ctx : demoContext(input))
    } catch {
      setAnswer(demoContext(input))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <SectionHeader eyebrow="Ask Anything" title="💬 Ask DecisionLens"
        desc="Ask natural-language questions. Answers are grounded in captured engineering discussions and their source evidence."
        action={memories.length ? <Pill tone="teal">{memories.length} local memories</Pill> : undefined}
      />
      {/* Suggested queries */}
      <div className="mb-4 flex flex-wrap gap-2">
        {suggested.map(q => (
          <button key={q} onClick={() => setInput(q)}
            className="rounded-full border border-indigo-500/20 bg-indigo-500/8 px-3 py-1.5 text-xs text-indigo-300 transition hover:border-indigo-500/40 hover:bg-indigo-500/14">
            {q}
          </button>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        {/* Answer panel */}
        <Panel className="min-h-96 p-6 lg:col-span-2 animate-fade-in">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-300">
            <div className="grid h-8 w-8 place-items-center rounded-xl bg-indigo-500/12 text-indigo-400">
              <Sparkles size={15} />
            </div>
            DecisionLens Intelligence
            {loading && <LoaderCircle size={14} className="animate-spin text-indigo-400 ml-1" />}
          </div>

          <div className="mt-6 min-h-48">
            {loading ? (
              <div className="flex items-center gap-3 text-slate-500">
                <LoaderCircle size={18} className="animate-spin text-indigo-400" />
                Searching engineering memory…
              </div>
            ) : (
              <>
                <p className="text-base leading-8 text-slate-200">{answer[0]?.summary}</p>
                {answer[0]?.previous_decisions && (
                  <div className="mt-5 space-y-3">
                    {answer[0].previous_decisions.map(d => (
                      <div key={d} className="flex items-start gap-3 rounded-xl border border-indigo-500/12 bg-indigo-500/6 p-4 text-sm text-slate-300">
                        <CheckCircle2 size={15} className="mt-0.5 flex-shrink-0 text-emerald-400" />
                        {d}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>

          <form onSubmit={e => { e.preventDefault(); ask() }} className="mt-6 flex gap-3">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask about Redis, Supabase, or an uploaded ADR…"
              className="dl-input flex-1"
            />
            <button type="submit" disabled={loading}
              className="btn-brand flex items-center gap-2 disabled:cursor-not-allowed disabled:opacity-40">
              <Send size={15} />
              Ask
            </button>
          </form>
        </Panel>

        {/* Evidence panel */}
        <div className="space-y-4 animate-fade-in delay-100">
          <Panel className="p-5">
            <h2 className="mb-1 font-bold text-slate-100">🔍 Evidence Trail</h2>
            <p className="mb-4 text-xs text-slate-500">Every answer traces back to source material.</p>
            <div className="space-y-3">
              {(answer[0]?.tradeoffs ?? ['No evidence yet']).map((t, i) => (
                <blockquote key={i} className="evidence-quote">{t}</blockquote>
              ))}
            </div>
            <div className="mt-5 border-t border-white/6 pt-4">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>Confidence</span>
                <span className="text-2xl font-black text-slate-50">
                  {Math.round((answer[0]?.confidence ?? 0.92) * 100)}%
                </span>
              </div>
              <div className="progress-bar mt-2">
                <div className="progress-fill" style={{ width: `${Math.round((answer[0]?.confidence ?? 0.92) * 100)}%`, background: '#6366f1' }} />
              </div>
            </div>
          </Panel>

          <Panel className="p-5">
            <h2 className="mb-3 text-sm font-bold text-slate-100">🔗 Related</h2>
            {(answer[0]?.related_entities ?? ['Supabase', 'Redis', 'PostgreSQL RLS']).map(e => (
              <Pill key={e} tone="slate">{e}</Pill>
            )).reduce<React.ReactNode[]>((acc, el, i) => [...acc, i > 0 ? ' ' : '', el], [])}
            <div className="mt-3 flex flex-wrap gap-2">
              {(answer[0]?.alternatives ?? []).slice(0, 2).map(a => (
                <Pill key={a} tone="rose">⛔ {a}</Pill>
              ))}
            </div>
          </Panel>

          <Panel className="p-5">
            <h2 className="mb-3 text-sm font-bold text-slate-100">🏗️ Arch Changes</h2>
            {(answer[0]?.architecture_changes ?? ['Tenant middleware sets context before PostgreSQL transactions.']).map(c => (
              <div key={c} className="mt-2 flex items-start gap-2 text-xs text-slate-400">
                <GitCommit size={13} className="mt-0.5 flex-shrink-0 text-violet-400" />
                {c}
              </div>
            ))}
          </Panel>
        </div>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: UPLOAD
═══════════════════════════════════════════════════════════════════ */
function Upload({ toast, onMemory }: { toast: (t: string) => void; onMemory: (items: SessionMemory[]) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<SessionMemory[]>([])
  const [busy, setBusy] = useState(false)
  const ref = useRef<HTMLInputElement>(null)

  const choose = async (f?: File | null) => {
    setFile(f ?? null)
    setPreview(f ? extractLocalMemories(f.name, await readFile(f)) : [])
  }
  const submit = async () => {
    if (!file) return
    setBusy(true)
    const local = preview.length ? preview : extractLocalMemories(file.name, await readFile(file))
    onMemory(local)
    try {
      await api.uploadMarkdown(file)
      toast(`✅ Markdown queued — ${local.length} local memories added.`)
    } catch {
      toast(`⚠️ API offline — ${local.length} local demo memories added.`)
    } finally {
      setBusy(false) }
  }

  return (
    <>
      <SectionHeader eyebrow="Ingestion" title="📤 Ingest Documents"
        desc="Add ADRs, RFCs, and architecture notes. DecisionLens extracts structured memories immediately — no LLM needed for the demo brain." />
      <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        {/* Drop zone */}
        <Panel className="p-6 animate-fade-in">
          <button
            onClick={() => ref.current?.click()}
            className="drop-zone flex min-h-56 w-full flex-col items-center justify-center p-8 text-center"
          >
            <div className="animate-float grid h-16 w-16 place-items-center rounded-2xl bg-indigo-500/12 text-indigo-400 mb-4">
              <UploadCloud size={32} />
            </div>
            <p className="font-semibold text-slate-200">Drop a Markdown file here</p>
            <p className="mt-2 text-sm text-slate-600">or click to browse · .md and .mdx</p>
            <input ref={ref} onChange={e => choose(e.target.files?.[0])} type="file" accept=".md,.mdx,text/markdown" className="hidden" />
          </button>

          {file && (
            <div className="mt-4 flex items-center justify-between rounded-xl border border-white/8 bg-white/4 p-4 animate-fade-in">
              <div className="flex items-center gap-3">
                <FileText size={18} className="text-indigo-400" />
                <div>
                  <p className="text-sm font-semibold text-slate-200">{file.name}</p>
                  <p className="text-xs text-slate-600">{Math.ceil(file.size / 1024)} KB · {preview.length} extractable memories</p>
                </div>
              </div>
              <button onClick={() => choose(null)} className="text-slate-500 transition hover:text-slate-300">
                <X size={16} />
              </button>
            </div>
          )}

          <button
            disabled={!file || busy}
            onClick={submit}
            className="btn-brand mt-4 w-full justify-center disabled:cursor-not-allowed disabled:opacity-40"
          >
            {busy ? (
              <><LoaderCircle size={15} className="animate-spin" /> Sending to ingestion queue…</>
            ) : (
              <><Sparkles size={15} /> Upload and add to memory graph</>
            )}
          </button>

          {/* Sample ADR hint */}
          <div className="mt-5 rounded-xl border border-white/6 bg-white/2 p-4">
            <p className="text-xs font-semibold text-slate-400 mb-2">📝 Sample ADR format:</p>
            <div className="code-block text-[11px]">
              <span className="kw"># Session Revocation ADR</span>{'\n'}
              <span className="str">Decision: Use Redis for immediate session revocation.</span>{'\n'}
              <span className="cmt">Tradeoff: Redis adds operational ownership.</span>{'\n'}
              <span className="cmt">Alternative: Fully stateless JWT sessions.</span>{'\n'}
              <span className="num">Architecture Change: Session middleware checks Redis.</span>
            </div>
          </div>
        </Panel>

        {/* Extraction preview */}
        <Panel className="p-6 animate-fade-in delay-100">
          <div className="flex items-center gap-2 mb-1">
            <Eye size={15} className="text-teal-400" />
            <h2 className="font-bold text-slate-100">Local Extraction Preview</h2>
          </div>
          <p className="mb-4 text-xs text-slate-500">
            This deterministic demo brain works without Ollama. For richer extraction,{' '}
            set <code className="rounded bg-white/6 px-1 text-indigo-300">EXTRACTION_PROVIDER=ollama</code>.
          </p>
          <div className="space-y-3">
            {(preview.length ? preview : [{
              id: 'empty', title: 'No file selected yet',
              summary: 'Upload a Markdown file with "Decision:" or "Tradeoff:" lines to see instant memories.',
              kind: 'document' as const, entity: 'Demo', source: '', evidence: '', timestamp: '',
            }]).map(item => {
              const kindColors: Record<string, string> = {
                decision: 'brand', tradeoff: 'amber', alternative: 'rose',
                architecture_change: 'violet', open_question: 'cyan', document: 'slate',
              }
              return (
                <div key={item.id} className="rounded-xl border border-white/6 bg-white/4 p-4 animate-fade-in">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="text-sm font-semibold text-slate-200 leading-tight">{item.title}</p>
                    <Pill tone={kindColors[item.kind] as any}>{kindLabel(item.kind)}</Pill>
                  </div>
                  {item.evidence && (
                    <blockquote className="evidence-quote mt-2 text-[11px]">{item.evidence}</blockquote>
                  )}
                  {!item.evidence && (
                    <p className="text-xs text-slate-600">{item.summary}</p>
                  )}
                </div>
              )
            })}
          </div>

          {/* Upload stats */}
          {preview.length > 0 && (
            <div className="mt-5 grid grid-cols-3 gap-3 border-t border-white/6 pt-5">
              {[
                { label: 'Memories', value: preview.length },
                { label: 'Decisions', value: preview.filter(p => p.kind === 'decision').length },
                { label: 'Tradeoffs', value: preview.filter(p => p.kind === 'tradeoff').length },
              ].map(s => (
                <div key={s.label} className="text-center">
                  <p className="text-xl font-black text-slate-100">{s.value}</p>
                  <p className="text-[11px] text-slate-600">{s.label}</p>
                </div>
              ))}
            </div>
          )}
        </Panel>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   PAGE: SETTINGS
═══════════════════════════════════════════════════════════════════ */
function SettingsPage() {
  const integrations = [
    { icon: <GitBranch size={18}/>, name: 'GitHub', status: 'Sample data active', color: '#818cf8', configured: true },
    { icon: <MessageSquare size={18}/>, name: 'Slack', status: 'Sample data active', color: '#8b5cf6', configured: true },
    { icon: <FileText size={18}/>, name: 'Markdown', status: 'Upload working', color: '#14b8a6', configured: true },
    { icon: <Globe size={18}/>, name: 'Notion', status: 'Planned', color: '#64748b', configured: false },
  ]
  return (
    <>
      <SectionHeader eyebrow="Workspace" title="⚙️ Settings"
        desc="Configure your DecisionLens workspace, API connections, and extraction providers." />
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-4">
          <Panel className="p-5 animate-fade-in">
            <div className="flex items-center gap-2 mb-4">
              <Server size={16} className="text-indigo-400" />
              <h2 className="font-bold text-slate-100">API Connection</h2>
            </div>
            <div className="code-block">
              {import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'}
            </div>
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/6 p-3 text-sm text-emerald-400">
              <CheckCircle2 size={15} />
              Demo fallback data is enabled when API is unavailable.
            </div>
          </Panel>

          <Panel className="p-5 animate-fade-in delay-100">
            <div className="flex items-center gap-2 mb-4">
              <Brain size={16} className="text-violet-400" />
              <h2 className="font-bold text-slate-100">Brain Mode</h2>
            </div>
            {[
              { label: 'Browser Demo Brain', desc: 'No setup needed. Parses "Decision:" patterns instantly.', active: true, color: '#6366f1' },
              { label: 'Local Ollama Brain',  desc: 'qwen3:8b · Private extraction · Best accuracy.',         active: false, color: '#14b8a6' },
              { label: 'Enterprise LLM',      desc: 'GPT-4, Claude, Gemini · Production scale.',              active: false, color: '#f59e0b' },
            ].map(m => (
              <div key={m.label} className={`mt-3 rounded-xl border p-4 ${m.active ? 'border-indigo-500/25 bg-indigo-500/8' : 'border-white/6 bg-white/2'}`}>
                <div className="flex items-center justify-between">
                  <p className={`text-sm font-semibold ${m.active ? 'text-indigo-300' : 'text-slate-400'}`}>{m.label}</p>
                  {m.active && <Pill tone="brand">Active</Pill>}
                </div>
                <p className="mt-1 text-xs text-slate-600">{m.desc}</p>
              </div>
            ))}
          </Panel>
        </div>

        <div className="space-y-4">
          <Panel className="p-5 animate-fade-in delay-100">
            <div className="flex items-center gap-2 mb-4">
              <Zap size={16} className="text-amber-400" />
              <h2 className="font-bold text-slate-100">Integrations</h2>
            </div>
            {integrations.map(itg => (
              <div key={itg.name} className="flex items-center gap-3 border-t border-white/5 py-4 first:border-0 first:pt-0">
                <div className="grid h-9 w-9 place-items-center rounded-xl" style={{ background: `${itg.color}15`, color: itg.color }}>
                  {itg.icon}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-slate-200">{itg.name}</p>
                  <p className="text-xs text-slate-600">{itg.status}</p>
                </div>
                <Pill tone={itg.configured ? 'green' : 'slate'}>
                  {itg.configured ? '✅ Active' : '⚪ Planned'}
                </Pill>
              </div>
            ))}
          </Panel>

          <Panel className="p-5 animate-fade-in delay-200">
            <div className="flex items-center gap-2 mb-4">
              <Shield size={16} className="text-teal-400" />
              <h2 className="font-bold text-slate-100">Privacy & Deployment</h2>
            </div>
            {[
              { icon: <Lock size={13}/>, label: 'All data stays local', desc: 'No external APIs or cloud required' },
              { icon: <Server size={13}/>, label: 'Self-hosted on your infrastructure', desc: 'Docker Compose single-command deploy' },
              { icon: <Shield size={13}/>, label: 'Supermemory runs on localhost:6767', desc: 'Fully private long-term memory' },
            ].map(item => (
              <div key={item.label} className="flex items-start gap-3 border-t border-white/5 py-3 first:border-0 first:pt-0 text-xs">
                <span className="mt-0.5 text-teal-400 flex-shrink-0">{item.icon}</span>
                <div>
                  <p className="font-semibold text-slate-300">{item.label}</p>
                  <p className="text-slate-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </Panel>
        </div>
      </div>
    </>
  )
}

/* ══════════════════════════════════════════════════════════════════
   SEARCH COMMAND PALETTE
═══════════════════════════════════════════════════════════════════ */
const ALL_PAGES_META = [
  { id: 'dashboard'  as Page, label: 'Overview',              sub: 'Main dashboard · stats · pipeline', emoji: '🏠' },
  { id: 'graph'      as Page, label: 'Memory Graph',          sub: 'Interactive knowledge node map',    emoji: '🕸️' },
  { id: 'ask'        as Page, label: 'Ask DecisionLens',      sub: 'Natural-language Q&A over memory',  emoji: '💬' },
  { id: 'timeline'   as Page, label: 'Architecture Timeline', sub: 'Chronological decision history',    emoji: '🕰️' },
  { id: 'recurring'  as Page, label: 'Recurring Discussions', sub: 'Topics that keep surfacing',        emoji: '🔁' },
  { id: 'trends'     as Page, label: 'Technology Trends',     sub: 'Adoption & rejection signals',      emoji: '📈' },
  { id: 'history'    as Page, label: 'Decision History',      sub: 'Trace a technology decision',       emoji: '📜' },
  { id: 'upload'     as Page, label: 'Ingest Documents',      sub: 'Upload Markdown ADRs & RFCs',       emoji: '📤' },
  { id: 'settings'   as Page, label: 'Settings',              sub: 'Configure API, brain, integrations',emoji: '⚙️' },
]
const QUICK_Q = ['Why did we choose Redis?', 'PostgreSQL RLS decision', 'Kafka vs Stripe events', 'Firebase rejected alternative']

function SearchPalette({ onPage, onClose }: { onPage: (p: Page) => void; onClose: () => void }) {
  const [q, setQ] = useState('')
  const ref = useRef<HTMLInputElement>(null)
  useEffect(() => { ref.current?.focus() }, [])
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [onClose])

  const filtered = q.trim()
    ? ALL_PAGES_META.filter(p => `${p.label} ${p.sub}`.toLowerCase().includes(q.toLowerCase()))
    : ALL_PAGES_META

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center px-4 pt-[12vh]"
      style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(10px)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="w-full max-w-lg animate-fade-in overflow-hidden rounded-2xl"
        style={{ background: 'rgba(9,12,32,0.98)', border: '1px solid rgba(99,102,241,0.35)', boxShadow: '0 40px 100px rgba(0,0,0,0.8), 0 0 0 1px rgba(99,102,241,0.08)' }}>
        {/* Input */}
        <div className="flex items-center gap-3 px-5 py-4" style={{ borderBottom: '1px solid rgba(99,102,241,0.1)' }}>
          <Search size={17} className="flex-shrink-0 text-indigo-400" />
          <input ref={ref} value={q} onChange={e => setQ(e.target.value)}
            placeholder="Search pages, technologies, decisions…"
            className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-600 outline-none" />
          <button onClick={onClose}
            className="rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-[10px] text-slate-500 hover:text-slate-300">ESC</button>
        </div>
        {/* Quick searches */}
        {!q.trim() && (
          <div className="px-5 pt-3 pb-1">
            <p className="mb-2 text-[10px] font-bold uppercase tracking-widest text-slate-600">Quick searches</p>
            <div className="flex flex-wrap gap-1.5">
              {QUICK_Q.map(s => (
                <button key={s} onClick={() => { onPage('ask'); onClose() }}
                  className="rounded-full border border-indigo-500/20 bg-indigo-500/8 px-2.5 py-1 text-[11px] text-indigo-400 transition hover:bg-indigo-500/15">{s}</button>
              ))}
            </div>
          </div>
        )}
        {/* Results */}
        <div className="max-h-72 overflow-y-auto p-3">
          {!q.trim() && <p className="mb-1 px-1 text-[10px] font-bold uppercase tracking-widest text-slate-600">Navigate to</p>}
          {filtered.map(p => (
            <button key={p.id} onClick={() => { onPage(p.id); onClose() }}
              className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition hover:bg-indigo-500/10">
              <span className="text-xl flex-shrink-0">{p.emoji}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-slate-200">{p.label}</p>
                <p className="text-xs text-slate-600">{p.sub}</p>
              </div>
              <ChevronRight size={13} className="flex-shrink-0 text-slate-700" />
            </button>
          ))}
          {filtered.length === 0 && <p className="py-8 text-center text-sm text-slate-600">No results for "{q}"</p>}
        </div>
        <div className="flex items-center gap-5 border-t px-5 py-2.5 text-[10px] text-slate-700"
          style={{ borderColor: 'rgba(99,102,241,0.08)' }}>
          <span>↵ to navigate</span><span>ESC to close</span><span>⌘K to reopen</span>
        </div>
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════════════════════════
   ROOT APP
═══════════════════════════════════════════════════════════════════ */
export function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const [dark, setDarkState] = useState(true)
  const [searchOpen, setSearchOpen] = useState(false)
  const [toast, setToast] = useState('')
  const [apiStatus, setApiStatus] = useState<'checking' | 'live' | 'demo'>('checking')
  const [memories, setMemories] = useState<SessionMemory[]>([])
  const addMemories = (items: SessionMemory[]) => setMemories(cur => [...cur, ...items])

  // ── Dark/light mode toggle ──
  const applyTheme = (isDark: boolean) => {
    const html = document.documentElement
    const body = document.body
    if (isDark) {
      html.style.background = '#060b18'
      body.style.background = '#060b18'
      body.style.color = '#e2e8f0'
      html.setAttribute('data-theme', 'dark')
    } else {
      html.style.background = '#eef2ff'
      body.style.background = '#eef2ff'
      body.style.color = '#1e1b4b'
      html.setAttribute('data-theme', 'light')
    }
  }
  const toggleDark = (v: boolean) => { setDarkState(v); applyTheme(v) }
  useEffect(() => { applyTheme(true) }, [])

  // ── ⌘K / Ctrl+K global shortcut ──
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setSearchOpen(true) }
    }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [])

  useEffect(() => {
    api.health().then(() => setApiStatus('live')).catch(() => setApiStatus('demo'))
  }, [])
  useEffect(() => {
    if (!toast) return
    const id = setTimeout(() => setToast(''), 4000)
    return () => clearTimeout(id)
  }, [toast])

  const content = useMemo(() => ({
    dashboard: <Dashboard onSearch={() => setSearchOpen(true)} />,
    graph:     <MemoryGraph memories={memories} />,
    ask:       <Ask memories={memories} />,
    timeline:  <Timeline />,
    recurring: <Recurring />,
    trends:    <Trends />,
    history:   <History />,
    upload:    <Upload toast={setToast} onMemory={addMemories} />,
    settings:  <SettingsPage />,
  })[page], [page, memories])

  return (
    <>
      <PageShell
        page={page}
        onPage={setPage}
        dark={dark}
        setDark={toggleDark}
        apiStatus={apiStatus}
        onSearchOpen={() => setSearchOpen(true)}
      >
        {content}
        {toast && (
          <div className="toast fixed bottom-6 right-6 z-50 max-w-sm">{toast}</div>
        )}
      </PageShell>
      {searchOpen && (
        <SearchPalette onPage={p => setPage(p)} onClose={() => setSearchOpen(false)} />
      )}
    </>
  )
}

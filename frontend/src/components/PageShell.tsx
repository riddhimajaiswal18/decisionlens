import {
  Bell, BrainCircuit, ChevronRight, Clock3, DatabaseZap,
  GitBranch, History, Home, Network, Search, Settings,
  Sun, Moon, UploadCloud, Waves, Zap, Shield, TrendingUp,
  Activity, BookOpen, Star
} from 'lucide-react'
import type { ReactNode } from 'react'

export type Page = 'dashboard' | 'graph' | 'ask' | 'timeline' | 'recurring' | 'trends' | 'history' | 'upload' | 'settings'

const nav: { id: Page; label: string; icon: ReactNode; group?: string; emoji: string }[] = [
  { id: 'dashboard',  label: 'Overview',              icon: <Home size={15} />,        emoji: '🏠' },
  { id: 'graph',      label: 'Memory Graph',           icon: <Network size={15} />,     emoji: '🕸️' },
  { id: 'ask',        label: 'Ask DecisionLens',       icon: <Search size={15} />,      emoji: '💬' },
  { id: 'timeline',   label: 'Architecture Timeline',  icon: <GitBranch size={15} />,   emoji: '🕰️', group: 'Intelligence' },
  { id: 'recurring',  label: 'Recurring Discussions',  icon: <Waves size={15} />,       emoji: '🔁' },
  { id: 'trends',     label: 'Technology Trends',      icon: <TrendingUp size={15} />,  emoji: '📈' },
  { id: 'history',    label: 'Decision History',       icon: <History size={15} />,     emoji: '📜' },
  { id: 'upload',     label: 'Ingest Documents',       icon: <UploadCloud size={15} />, emoji: '📤', group: 'Workspace' },
  { id: 'settings',   label: 'Settings',               icon: <Settings size={15} />,    emoji: '⚙️' },
]

function StatusDot({ status }: { status: 'checking' | 'live' | 'demo' }) {
  const cfg = {
    live:     { color: '#10b981', label: 'API Connected',   pulse: true },
    checking: { color: '#f59e0b', label: 'Connecting…',     pulse: true },
    demo:     { color: '#6366f1', label: 'Demo Mode',       pulse: false },
  }[status]
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-white/8 bg-white/4 px-3 py-1.5 text-xs font-medium" style={{ color: cfg.color }}>
      <span className="relative flex h-2 w-2">
        <span className="h-full w-full rounded-full" style={{ background: cfg.color, opacity: cfg.pulse ? 0.4 : 1 }} />
        {cfg.pulse && (
          <span className="absolute inset-0 animate-ping rounded-full" style={{ background: cfg.color, opacity: 0.6 }} />
        )}
      </span>
      {cfg.label}
    </span>
  )
}

export function PageShell({
  page, onPage, dark, setDark, apiStatus, children,
}: {
  page: Page; onPage: (page: Page) => void
  dark: boolean; setDark: (v: boolean) => void
  apiStatus: 'checking' | 'live' | 'demo'; children: ReactNode
}) {
  return (
    <div className="app-grid min-h-screen text-slate-200">
      {/* ── Sidebar ── */}
      <aside className="sidebar fixed inset-y-0 left-0 hidden w-64 flex-col lg:flex" style={{ zIndex: 40 }}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-6">
          <div
            className="animate-brain relative grid h-10 w-10 place-items-center rounded-xl"
            style={{
              background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
              boxShadow: '0 4px 16px rgba(99,102,241,0.5)',
            }}
          >
            <BrainCircuit size={22} color="white" />
          </div>
          <div>
            <p className="text-sm font-bold tracking-tight text-slate-100">DecisionLens</p>
            <p className="text-[10px] text-slate-500">Engineering Memory OS</p>
          </div>
        </div>

        {/* Search hint */}
        <div className="mx-4 mb-3">
          <div className="flex items-center gap-2 rounded-lg border border-white/8 bg-white/4 px-3 py-2 text-xs text-slate-500">
            <Search size={12} />
            <span>Search memory</span>
            <kbd className="ml-auto rounded bg-white/8 px-1.5 py-0.5 text-[10px]">⌘K</kbd>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-2">
          {nav.map((item) => (
            <div key={item.id}>
              {item.group && (
                <p className="mb-1 mt-5 px-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-600">
                  {item.group}
                </p>
              )}
              <button
                onClick={() => onPage(item.id)}
                className={`nav-item ${page === item.id ? 'active' : ''}`}
              >
                <span className="flex items-center gap-2.5">
                  <span className={page === item.id ? 'text-indigo-400' : 'text-slate-600'}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </span>
                {page === item.id && <ChevronRight size={13} className="text-indigo-400" />}
              </button>
            </div>
          ))}
        </nav>

        {/* Bottom status card */}
        <div className="m-4 rounded-xl border border-white/8 bg-white/4 p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
            <Zap size={13} className="text-amber-400" />
            Supermemory Active
          </div>
          <p className="mt-1.5 text-[11px] leading-relaxed text-slate-600">
            GitHub · Slack · Markdown corpus seeded and ready.
          </p>
          <div className="mt-3">
            <StatusDot status={apiStatus} />
          </div>
        </div>

        {/* Decorative bottom gradient */}
        <div
          className="pointer-events-none absolute bottom-0 left-0 right-0 h-32"
          style={{ background: 'linear-gradient(to top, rgba(99,102,241,0.06), transparent)' }}
        />
      </aside>

      {/* ── Main ── */}
      <main className="flex min-h-screen flex-col lg:pl-64">
        {/* Topbar */}
        <header className="topbar sticky top-0 z-30 flex h-14 items-center justify-between px-5 lg:px-8">
          {/* Mobile logo */}
          <button
            className="focus-ring flex items-center gap-2 lg:hidden"
            onClick={() => onPage('dashboard')}
          >
            <BrainCircuit size={20} className="text-indigo-400" />
            <span className="text-sm font-bold">DecisionLens</span>
          </button>

          {/* Page breadcrumb (desktop) */}
          <div className="hidden items-center gap-2 text-sm text-slate-500 lg:flex">
            <BookOpen size={14} />
            <span>Engineering Memory OS</span>
            <ChevronRight size={12} />
            <span className="text-slate-300 font-medium">
              {nav.find(n => n.id === page)?.emoji} {nav.find(n => n.id === page)?.label}
            </span>
          </div>

          {/* Right actions */}
          <div className="ml-auto flex items-center gap-2">
            <StatusDot status={apiStatus} />
            <button
              aria-label="Toggle theme"
              onClick={() => setDark(!dark)}
              className="focus-ring rounded-lg p-2 text-slate-500 transition hover:bg-white/6 hover:text-slate-300"
            >
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <button
              aria-label="Notifications"
              className="focus-ring relative rounded-lg p-2 text-slate-500 transition hover:bg-white/6 hover:text-slate-300"
            >
              <Bell size={16} />
              <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-indigo-500" />
            </button>
            <div
              className="grid h-8 w-8 place-items-center rounded-lg text-xs font-bold text-white"
              style={{ background: 'linear-gradient(135deg,#6366f1,#4f46e5)' }}
              title="DecisionLens User"
            >
              DL
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="mx-auto w-full max-w-7xl flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </div>

        {/* Mobile bottom nav */}
        <nav
          className="fixed inset-x-2 bottom-2 z-40 grid grid-cols-4 gap-1 rounded-2xl border border-white/10 bg-[#060b18]/95 p-1.5 shadow-2xl backdrop-blur-xl lg:hidden"
        >
          {nav.slice(0, 4).map((item) => (
            <button
              key={item.id}
              onClick={() => onPage(item.id)}
              className={`flex flex-col items-center gap-1 rounded-xl px-1 py-2.5 text-[10px] font-medium transition ${
                page === item.id
                  ? 'bg-indigo-500/15 text-indigo-400'
                  : 'text-slate-600 hover:text-slate-400'
              }`}
            >
              <span className={page === item.id ? 'text-indigo-400' : ''}>
                {item.icon}
              </span>
              <span>{item.label.split(' ')[0]}</span>
            </button>
          ))}
        </nav>

        {/* Mobile bottom padding */}
        <div className="h-20 lg:hidden" />
      </main>
    </div>
  )
}

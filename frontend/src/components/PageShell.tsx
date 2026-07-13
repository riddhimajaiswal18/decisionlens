import { Bell, BrainCircuit, ChevronRight, Clock3, DatabaseZap, GitBranch, History, Home, Moon, Network, Search, Settings, Sun, UploadCloud, Waves } from 'lucide-react'
import type { ReactNode } from 'react'

export type Page = 'dashboard' | 'graph' | 'ask' | 'timeline' | 'recurring' | 'trends' | 'history' | 'upload' | 'settings'
const nav: { id: Page; label: string; group?: string; icon: ReactNode }[] = [
  { id: 'dashboard', label: 'Overview', icon: <Home size={16} /> },
  { id: 'graph', label: 'Memory graph', icon: <Network size={16} /> },
  { id: 'ask', label: 'Ask DecisionLens', icon: <Search size={16} /> },
  { id: 'timeline', label: 'Architecture timeline', group: 'Intelligence', icon: <GitBranch size={16} /> },
  { id: 'recurring', label: 'Recurring discussions', icon: <Waves size={16} /> },
  { id: 'trends', label: 'Technology trends', icon: <DatabaseZap size={16} /> },
  { id: 'history', label: 'Decision history', icon: <History size={16} /> },
  { id: 'upload', label: 'Markdown upload', group: 'Workspace', icon: <UploadCloud size={16} /> },
  { id: 'settings', label: 'Settings', icon: <Settings size={16} /> },
]

export function PageShell({ page, onPage, dark, setDark, apiStatus, children }: { page: Page; onPage: (page: Page) => void; dark: boolean; setDark: (value: boolean) => void; apiStatus: 'checking' | 'live' | 'demo'; children: ReactNode }) {
  const statusText = apiStatus === 'live' ? 'API connected' : apiStatus === 'checking' ? 'Checking API' : 'Demo mode'
  const statusClass = apiStatus === 'live' ? 'text-emerald-600' : apiStatus === 'checking' ? 'text-amber' : 'text-slate-500'
  return <div className={dark ? 'dark' : ''}><div className="app-grid min-h-screen bg-surface text-slate-900 dark:bg-[#090d18] dark:text-slate-100">
    <aside className="fixed inset-y-0 hidden w-64 border-r border-slate-200 bg-white/90 px-4 py-5 backdrop-blur lg:block dark:border-slate-800 dark:bg-[#0d1220]/90">
      <button onClick={() => onPage('dashboard')} className="focus-ring flex items-center gap-3 rounded-lg px-3 py-2 text-left"><span className="grid h-9 w-9 place-items-center rounded-lg bg-ink text-white shadow-sm dark:bg-brand"><BrainCircuit size={20}/></span><span><b className="block text-sm tracking-tight">DecisionLens</b><small className="text-xs text-slate-500">Engineering memory OS</small></span></button>
      <nav className="mt-8 space-y-1">{nav.map((item) => <div key={item.id}>{item.group && <p className="mb-2 mt-7 px-3 text-[10px] font-semibold uppercase tracking-[.16em] text-slate-400">{item.group}</p>}<button onClick={() => onPage(item.id)} className={`focus-ring flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition ${page === item.id ? 'bg-blue-50 font-medium text-brand dark:bg-blue-500/10 dark:text-blue-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}><span className="flex min-w-0 items-center gap-2"><span className="shrink-0">{item.icon}</span><span className="truncate">{item.label}</span></span>{page === item.id && <ChevronRight size={14}/>}</button></div>)}</nav>
      <div className="absolute bottom-5 left-4 right-4 rounded-lg border border-slate-200 p-3 dark:border-slate-800"><p className="text-xs font-medium">Hackathon workspace</p><p className="mt-1 text-xs leading-relaxed text-slate-500">GitHub, Slack, and Markdown demo corpus is ready.</p><span className={`mt-2 inline-flex items-center gap-1 text-[11px] ${statusClass}`}><i className={`h-1.5 w-1.5 rounded-full ${apiStatus === 'live' ? 'bg-emerald-500' : apiStatus === 'checking' ? 'bg-amber-500' : 'bg-slate-400'}`}/> {statusText}</span></div>
    </aside>
    <main className="min-h-screen pb-20 lg:pl-64 lg:pb-0"><header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/75 px-5 backdrop-blur dark:border-slate-800 dark:bg-[#0d1220]/75 lg:px-9"><button className="focus-ring rounded-lg text-sm font-semibold lg:hidden" onClick={() => onPage('dashboard')}>DecisionLens</button><div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400 md:flex dark:border-slate-700 dark:bg-slate-800"><Search size={15}/>Search engineering memory <kbd className="ml-10 text-[10px]">⌘ K</kbd></div><div className="ml-auto flex items-center gap-3"><span className={`hidden items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs dark:border-slate-800 sm:inline-flex ${statusClass}`}><Clock3 size={13}/>{statusText}</span><button aria-label="Toggle theme" onClick={() => setDark(!dark)} className="focus-ring rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">{dark ? <Sun size={17}/> : <Moon size={17}/>}</button><button aria-label="Notifications" className="focus-ring rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"><Bell size={17}/></button><span className="grid h-8 w-8 place-items-center rounded-lg bg-ink text-xs font-semibold text-white dark:bg-brand">DL</span></div></header>
      <div className="mx-auto max-w-7xl p-4 sm:p-5 lg:p-8">{children}</div>
      <nav className="fixed inset-x-3 bottom-3 z-40 grid grid-cols-4 gap-1 rounded-lg border border-slate-200 bg-white/95 p-1 shadow-lg backdrop-blur lg:hidden dark:border-slate-800 dark:bg-slate-900/95">{nav.slice(0, 4).map((item) => <button key={item.id} onClick={() => onPage(item.id)} className={`focus-ring flex flex-col items-center rounded-md px-1 py-2 text-[11px] ${page === item.id ? 'bg-blue-50 text-brand dark:bg-blue-500/10' : 'text-slate-500'}`}><span>{item.icon}</span><span className="mt-1 max-w-full truncate">{item.label.replace('DecisionLens', '')}</span></button>)}</nav>
    </main>
  </div></div>
}

import { Bell, BrainCircuit, ChevronRight, Moon, Search, Sun } from 'lucide-react'
import type { ReactNode } from 'react'

export type Page = 'dashboard' | 'ask' | 'timeline' | 'recurring' | 'trends' | 'history' | 'upload' | 'settings'
const nav: { id: Page; label: string; group?: string }[] = [
  { id: 'dashboard', label: 'Overview' }, { id: 'ask', label: 'Ask DecisionLens' }, { id: 'timeline', label: 'Architecture timeline', group: 'Intelligence' },
  { id: 'recurring', label: 'Recurring discussions' }, { id: 'trends', label: 'Technology trends' }, { id: 'history', label: 'Decision history' },
  { id: 'upload', label: 'Markdown upload', group: 'Workspace' }, { id: 'settings', label: 'Settings' },
]

export function PageShell({ page, onPage, dark, setDark, children }: { page: Page; onPage: (page: Page) => void; dark: boolean; setDark: (value: boolean) => void; children: ReactNode }) {
  return <div className={dark ? 'dark' : ''}><div className="app-grid min-h-screen bg-surface text-slate-900 dark:bg-[#090d18] dark:text-slate-100">
    <aside className="fixed inset-y-0 hidden w-64 border-r border-slate-200 bg-white/90 px-4 py-5 backdrop-blur lg:block dark:border-slate-800 dark:bg-[#0d1220]/90">
      <button onClick={() => onPage('dashboard')} className="flex items-center gap-3 px-3 text-left"><span className="grid h-9 w-9 place-items-center rounded-xl bg-brand text-white shadow-lg shadow-indigo-200 dark:shadow-none"><BrainCircuit size={20}/></span><span><b className="block text-sm tracking-tight">DecisionLens</b><small className="text-xs text-slate-500">Engineering intelligence</small></span></button>
      <nav className="mt-10 space-y-1">{nav.map((item) => <div key={item.id}>{item.group && <p className="mb-2 mt-7 px-3 text-[10px] font-semibold uppercase tracking-[.16em] text-slate-400">{item.group}</p>}<button onClick={() => onPage(item.id)} className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition ${page === item.id ? 'bg-indigo-50 font-medium text-brand dark:bg-indigo-500/10 dark:text-indigo-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}><span>{item.label}</span>{page === item.id && <ChevronRight size={14}/>}</button></div>)}</nav>
      <div className="absolute bottom-5 left-4 right-4 rounded-xl border border-slate-200 p-3 dark:border-slate-800"><p className="text-xs font-medium">Demo workspace</p><p className="mt-1 text-xs leading-relaxed text-slate-500">Seeded engineering memory is ready to explore.</p><span className="mt-2 inline-flex items-center gap-1 text-[11px] text-emerald-600"><i className="h-1.5 w-1.5 rounded-full bg-emerald-500"/> Memory connected</span></div>
    </aside>
    <main className="min-h-screen lg:pl-64"><header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white/75 px-5 backdrop-blur dark:border-slate-800 dark:bg-[#0d1220]/75 lg:px-9"><button className="lg:hidden text-sm font-semibold" onClick={() => onPage('dashboard')}>DecisionLens</button><div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400 md:flex dark:border-slate-700 dark:bg-slate-800"><Search size={15}/>Search engineering memory <kbd className="ml-10 text-[10px]">⌘ K</kbd></div><div className="ml-auto flex items-center gap-3"><button aria-label="Toggle theme" onClick={() => setDark(!dark)} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">{dark ? <Sun size={17}/> : <Moon size={17}/>}</button><button aria-label="Notifications" className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"><Bell size={17}/></button><span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-400 text-xs font-semibold text-white">AM</span></div></header>
      <div className="mx-auto max-w-7xl p-5 lg:p-9">{children}</div>
    </main>
  </div></div>
}

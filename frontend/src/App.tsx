import { useState } from 'react'
import { analyseRepo } from './api'
import type { AnalyseResponse, ComponentDebt } from './types'
import { SearchBar } from './components/SearchBar'
import { StatsCards } from './components/StatsCards'
import { DebtTreemap } from './components/DebtTreemap'
import { FileList } from './components/FileList'
import { FileDetail } from './components/FileDetail'
import { AIPanel } from './components/AIPanel'

export default function App() {
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState<string | null>(null)
  const [result, setResult]     = useState<AnalyseResponse | null>(null)
  const [selected, setSelected] = useState<ComponentDebt | null>(null)

  const handleSubmit = async (url: string) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setSelected(null)
    try {
      const data = await analyseRepo(url)
      setResult(data)
    } catch (e: any) {
      setError(e.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg text-white">
      <header className="border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
              <span className="text-accent font-mono text-sm font-bold">R</span>
            </div>
            <div>
              <h1 className="font-sans font-semibold text-white text-base leading-none">ReactLens</h1>
              <p className="text-muted text-xs mt-0.5">Technical Debt Analyser</p>
            </div>
          </div>
          {result && <span className="font-mono text-xs text-muted">{result.repo_name}</span>}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        <div className="flex flex-col items-center gap-3">
          <SearchBar onSubmit={handleSubmit} loading={loading} />
          <p className="text-muted text-xs font-sans">Enter any public GitHub repository URL</p>
        </div>

        {error && (
          <div className="card p-4 border-red-500/30 bg-red-500/10 animate-fade-in">
            <p className="text-red-400 text-sm font-sans">⚠ {error}</p>
          </div>
        )}

        {loading && (
          <div className="space-y-4 animate-pulse">
            <div className="grid grid-cols-4 gap-3">
              {[...Array(4)].map((_, i) => <div key={i} className="card h-20 bg-surface/50" />)}
            </div>
            <div className="card h-96 bg-surface/50" />
          </div>
        )}

        {result && !loading && (
          <div className="space-y-6 animate-fade-in">
            <StatsCards data={result} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                <DebtTreemap components={result.components} onSelect={setSelected} />
                <AIPanel data={result} />
              </div>
              <div className="space-y-4">
                {selected && <FileDetail component={selected} onClose={() => setSelected(null)} />}
                <FileList components={result.components} selected={selected} onSelect={setSelected} />
              </div>
            </div>
          </div>
        )}

        {!result && !loading && !error && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-16 h-16 rounded-2xl bg-surface border border-border flex items-center justify-center">
              <span className="text-3xl">🔍</span>
            </div>
            <div className="text-center">
              <p className="text-white font-sans font-medium">Analyse a React repository</p>
              <p className="text-muted text-sm mt-1">Enter a GitHub URL above to visualise technical debt</p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center mt-2">
              {[
                'https://github.com/typescript-rtti/typescript-rtti',
                'https://github.com/miladr0/task-do',
              ].map(url => (
                <button
                  key={url}
                  onClick={() => handleSubmit(url)}
                  className="text-xs font-mono text-accent hover:text-indigo-300 transition-colors bg-accent/10 px-3 py-1.5 rounded-lg border border-accent/20"
                >
                  {url.replace('https://github.com/', '')}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

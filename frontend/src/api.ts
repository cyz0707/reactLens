import type { AnalyseResponse } from './types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export async function analyseRepo(repoUrl: string): Promise<AnalyseResponse> {
  const res = await fetch(`${API_BASE}/api/analyse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo_url: repoUrl }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

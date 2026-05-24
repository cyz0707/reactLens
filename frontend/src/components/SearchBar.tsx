import { useState, type FormEvent } from 'react'

interface Props {
  onSubmit: (url: string) => void
  loading: boolean
}

export function SearchBar({ onSubmit, loading }: Props) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const trimmed = url.trim()
    if (trimmed) onSubmit(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 w-full max-w-3xl">
      <div className="flex-1 relative">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted font-mono text-sm">
          github.com/
        </span>
        <input
          type="text"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="owner/repository"
          disabled={loading}
          className="
            w-full pl-28 pr-4 py-3
            bg-surface border border-border rounded-xl
            font-mono text-sm text-white placeholder-muted
            focus:outline-none focus:border-accent
            transition-colors disabled:opacity-50
          "
        />
      </div>
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="
          px-6 py-3 rounded-xl font-sans font-medium text-sm
          bg-accent hover:bg-indigo-500 text-white
          disabled:opacity-40 disabled:cursor-not-allowed
          transition-colors flex items-center gap-2
        "
      >
        {loading ? (
          <>
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Analysing…
          </>
        ) : 'Analyse'}
      </button>
    </form>
  )
}

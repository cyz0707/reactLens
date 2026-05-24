import type { ComponentDebt } from '../types'

interface Props {
  components: ComponentDebt[]
  selected: ComponentDebt | null
  onSelect: (c: ComponentDebt) => void
}

const BADGE: Record<string, string> = {
  high:   'bg-red-500/20 text-red-400 border border-red-500/30',
  medium: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
  low:    'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
}

const BAR_COLOR: Record<string, string> = {
  high:   'bg-high',
  medium: 'bg-medium',
  low:    'bg-low',
}

export function FileList({ components, selected, onSelect }: Props) {
  return (
    <div className="card overflow-hidden">
      <div className="px-4 py-3 border-b border-border">
        <h2 className="font-sans font-medium text-sm text-white">Files by Debt Score</h2>
      </div>
      <div className="divide-y divide-border max-h-[480px] overflow-y-auto">
        {components.map(c => (
          <button
            key={c.filepath}
            onClick={() => onSelect(c)}
            className={`
              w-full text-left px-4 py-3 flex items-center gap-3
              hover:bg-white/5 transition-colors
              ${selected?.filepath === c.filepath ? 'bg-accent/10 border-l-2 border-accent' : ''}
            `}
          >
            {/* Score bar */}
            <div className="w-12 flex-shrink-0">
              <div className="h-1.5 bg-border rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${BAR_COLOR[c.debt_level]}`}
                  style={{ width: `${c.debt_score}%` }}
                />
              </div>
            </div>

            {/* Filename */}
            <span className="font-mono text-xs text-white flex-1 truncate">
              {c.filename}
            </span>

            {/* Score */}
            <span className="font-mono text-xs text-muted w-8 text-right flex-shrink-0">
              {c.debt_score}
            </span>

            {/* Badge */}
            <span className={`text-xs px-2 py-0.5 rounded font-sans flex-shrink-0 ${BADGE[c.debt_level]}`}>
              {c.debt_level}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

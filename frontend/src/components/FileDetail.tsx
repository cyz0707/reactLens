import type { ComponentDebt } from '../types'

interface Props {
  component: ComponentDebt
  onClose: () => void
}

const METRICS = [
  { key: 'loc',                    label: 'Lines of Code',        threshold: 200 },
  { key: 'props_count',            label: 'Props',                threshold: 10  },
  { key: 'any_count',              label: 'any usages',           threshold: 3   },
  { key: 'todo_count',             label: 'TODOs / FIXMEs',       threshold: 1   },
  { key: 'component_count',        label: 'Components in file',   threshold: 2   },
  { key: 'nested_ternary_count',   label: 'Nested ternaries',     threshold: 2   },
  { key: 'console_log_count',      label: 'console.log calls',    threshold: 1   },
  { key: 'missing_return_type_count', label: 'Missing return types', threshold: 1 },
] as const

export function FileDetail({ component: c, onClose }: Props) {
  return (
    <div className="card overflow-hidden animate-slide-up">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="font-mono text-sm text-white">{c.filename}</h2>
          <p className="text-muted text-xs mt-0.5">{c.filepath}</p>
        </div>
        <button
          onClick={onClose}
          className="text-muted hover:text-white transition-colors text-lg leading-none"
        >
          ×
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Debt score */}
        <div className="flex items-center gap-3">
          <div
            className={`text-3xl font-mono font-semibold ${
              c.debt_level === 'high' ? 'text-high' :
              c.debt_level === 'medium' ? 'text-medium' : 'text-low'
            }`}
          >
            {c.debt_score}
          </div>
          <div>
            <div className="text-white text-sm font-sans font-medium capitalize">{c.debt_level} debt</div>
            <div className="text-muted text-xs">out of 100</div>
          </div>
        </div>

        {/* Metrics grid */}
        <div className="grid grid-cols-2 gap-2">
          {METRICS.map(m => {
            const val = c[m.key]
            const bad = val > m.threshold
            return (
              <div
                key={m.key}
                className={`rounded-lg px-3 py-2 flex items-center justify-between ${
                  bad ? 'bg-red-500/10 border border-red-500/20' : 'bg-white/5'
                }`}
              >
                <span className="text-xs text-muted font-sans">{m.label}</span>
                <span className={`font-mono text-sm ${bad ? 'text-high' : 'text-white'}`}>
                  {val}
                </span>
              </div>
            )
          })}
        </div>

        {/* Issues */}
        {c.issues.length > 0 && (
          <div>
            <h3 className="text-xs text-muted uppercase tracking-wider mb-2 font-sans">Issues</h3>
            <ul className="space-y-1.5">
              {c.issues.map((issue, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-sans text-white/80">
                  <span className="text-high mt-0.5">▸</span>
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

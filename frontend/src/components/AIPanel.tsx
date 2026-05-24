import type { AnalyseResponse } from '../types'

interface Props {
  data: AnalyseResponse
}

export function AIPanel({ data }: Props) {
  if (!data.ai_summary) return null

  const isError = data.ai_summary.startsWith('AI recommendations unavailable')

  if (isError) {
    return (
      <div className="card p-4 border-amber-500/30">
        <p className="text-amber-400 text-xs font-sans">
          ⚠ AI recommendations unavailable. Add ANTHROPIC_API_KEY to your .env to enable.
        </p>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden animate-slide-up">
      <div className="px-4 py-3 border-b border-border flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
        <h2 className="font-sans font-medium text-sm text-white">AI Recommendations</h2>
        {data.ai_score_label && (
          <span className="ml-auto text-xs text-muted font-sans">
            {data.ai_overall_score}/100 · {data.ai_score_label}
          </span>
        )}
      </div>

      <div className="p-4 space-y-4">
        {/* Summary */}
        <p className="text-sm text-white/80 font-sans leading-relaxed">
          {data.ai_summary}
        </p>

        {/* Top issues */}
        {data.ai_top_issues && data.ai_top_issues.length > 0 && (
          <div>
            <h3 className="text-xs text-muted uppercase tracking-wider mb-2 font-sans">Top Issues</h3>
            <ul className="space-y-1.5">
              {data.ai_top_issues.map((issue, i) => (
                <li key={i} className="flex items-start gap-2 text-xs font-sans text-white/80">
                  <span className="text-high font-mono mt-0.5">{i + 1}.</span>
                  {issue}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Remediation plan */}
        {data.ai_remediation_plan && data.ai_remediation_plan.length > 0 && (
          <div>
            <h3 className="text-xs text-muted uppercase tracking-wider mb-2 font-sans">Remediation Plan</h3>
            <ol className="space-y-2">
              {data.ai_remediation_plan.map((step, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-accent/20 text-accent text-xs flex items-center justify-center font-mono">
                    {i + 1}
                  </span>
                  <span className="text-xs font-sans text-white/80 leading-relaxed">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}

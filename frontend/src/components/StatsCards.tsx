import type { AnalyseResponse } from '../types'

interface Props {
  data: AnalyseResponse
}

export function StatsCards({ data }: Props) {
  const scoreColor =
    (data.ai_overall_score ?? 0) >= 60 ? 'text-high' :
    (data.ai_overall_score ?? 0) >= 30 ? 'text-medium' :
    'text-low'

  const cards = [
    {
      label: 'Total Files',
      value: data.total_files,
      sub: 'analysed',
      color: 'text-white',
    },
    {
      label: 'High Debt',
      value: data.high_debt_count,
      sub: 'files',
      color: 'text-high',
    },
    {
      label: 'Medium Debt',
      value: data.medium_debt_count,
      sub: 'files',
      color: 'text-medium',
    },
    {
      label: 'Low Debt',
      value: data.low_debt_count,
      sub: 'files',
      color: 'text-low',
    },
    ...(data.ai_overall_score !== null ? [{
      label: 'AI Score',
      value: data.ai_overall_score,
      sub: data.ai_score_label ?? '',
      color: scoreColor,
    }] : []),
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 w-full">
      {cards.map(card => (
        <div key={card.label} className="card p-4 flex flex-col gap-1 animate-slide-up">
          <span className="text-muted text-xs font-sans uppercase tracking-wider">
            {card.label}
          </span>
          <span className={`font-mono text-3xl font-semibold ${card.color}`}>
            {card.value}
          </span>
          <span className="text-muted text-xs">{card.sub}</span>
        </div>
      ))}
    </div>
  )
}

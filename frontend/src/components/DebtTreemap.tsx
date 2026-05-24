import ReactECharts from 'echarts-for-react'
import type { ComponentDebt } from '../types'

interface Props {
  components: ComponentDebt[]
  onSelect: (c: ComponentDebt) => void
}

const LEVEL_COLOR: Record<string, string> = {
  high:   '#EF4444',
  medium: '#F59E0B',
  low:    '#10B981',
}

export function DebtTreemap({ components, onSelect }: Props) {
  const data = components
    .filter(c => c.debt_score > 0)
    .map(c => ({
      name: c.filename,
      value: Math.max(c.debt_score, 5),
      itemStyle: { color: LEVEL_COLOR[c.debt_level] },
      _raw: c,
    }))

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      formatter: (p: any) => {
        const c: ComponentDebt = p.data._raw
        return `
          <div style="font-family:monospace;font-size:12px;line-height:1.6">
            <b>${c.filename}</b><br/>
            Score: <b>${c.debt_score}</b><br/>
            LOC: ${c.loc}<br/>
            ${c.issues.slice(0,2).map(i => `• ${i}`).join('<br/>')}
          </div>
        `
      },
    },
    series: [{
      type: 'treemap',
      data,
      width: '100%',
      height: '100%',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      label: {
        show: true,
        formatter: (p: any) => p.data.name.replace('.tsx','').replace('.ts',''),
        fontSize: 12,
        fontFamily: 'JetBrains Mono, monospace',
        color: '#fff',
        textShadowBlur: 4,
        textShadowColor: 'rgba(0,0,0,0.8)',
      },
      upperLabel: { show: false },
      itemStyle: { borderColor: '#0A0E1A', borderWidth: 2, gapWidth: 2 },
      emphasis: {
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
      },
    }],
  }

  const onChartClick = (params: any) => {
    if (params.data?._raw) onSelect(params.data._raw)
  }

  if (data.length === 0) {
    return (
      <div className="card flex items-center justify-center h-72 text-muted text-sm">
        No debt detected — all files are clean ✓
      </div>
    )
  }

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-sans font-medium text-sm text-white">Debt Map</h2>
        <div className="flex gap-3 text-xs text-muted font-sans">
          {(['high','medium','low'] as const).map(level => (
            <span key={level} className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full inline-block" style={{ background: LEVEL_COLOR[level] }} />
              {level}
            </span>
          ))}
        </div>
      </div>
      <ReactECharts
        option={option}
        style={{ height: 360 }}
        onEvents={{ click: onChartClick }}
      />
      <p className="text-muted text-xs mt-2 font-sans">Click a cell to inspect</p>
    </div>
  )
}

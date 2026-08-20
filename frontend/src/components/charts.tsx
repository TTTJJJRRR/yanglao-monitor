import type { TrendPoint } from '../types'

// 手绘 SVG 图表：贴合原型的温馨扁平风，不引重型图表库

function pointsToPath(values: number[], width: number, height: number, pad = 6): string {
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min || 1
  const step = (width - pad * 2) / (values.length - 1 || 1)
  return values
    .map((v, i) => {
      const x = pad + i * step
      const y = height - pad - ((v - min) / span) * (height - pad * 2)
      return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
}

/** 面积趋势图（呼吸/心率趋势卡用） */
export function AreaTrend({ data, color }: { data: TrendPoint[]; color: string }) {
  const W = 500
  const H = 150
  const values = data.map((d) => d.value)
  const line = pointsToPath(values, W, H, 10)
  const area = `${line} L ${W - 10} ${H} L 10 ${H} Z`
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="h-40 w-full" preserveAspectRatio="none">
      <path d={area} fill={color} opacity={0.12} />
      <path d={line} fill="none" stroke={color} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

/** 实时波形（床位详情呼吸/心率大卡用）：真实 WS 数据驱动 */
export function LiveWave({ values, color }: { values: number[]; color: string }) {
  if (values.length < 2) return <div className="flex h-16 items-center text-xs text-ink-hint">等待实时数据…</div>
  const line = pointsToPath(values, 500, 64, 4)
  return (
    <svg viewBox="0 0 500 64" className="h-16 w-full" preserveAspectRatio="none">
      <path d={line} fill="none" stroke={color} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

/** 周柱状图（总览本周预警趋势用） */
export function WeekBars({ data, peakIndex }: { data: { day: string; value: number }[]; peakIndex: number }) {
  const max = Math.max(...data.map((d) => d.value)) || 1
  return (
    <div className="flex items-end gap-5 pt-2">
      {data.map((d, i) => (
        <div key={d.day} className="flex flex-col items-center gap-2">
          <div
            className={`w-[30px] rounded-md ${i === peakIndex ? 'bg-amber' : 'bg-sage'}`}
            style={{ height: `${Math.max(14, (d.value / max) * 96)}px` }}
            title={`${d.value} 条`}
          />
          <span className="text-[11px] text-ink-sub">{d.day}</span>
        </div>
      ))}
    </div>
  )
}

/** 横向进度条（楼层状态 / 活动量用） */
export function Meter({ ratio, color = '#6E8F74' }: { ratio: number; color?: string }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded bg-[#F0EDE3]">
      <div className="h-full rounded" style={{ width: `${Math.round(ratio * 100)}%`, background: color }} />
    </div>
  )
}

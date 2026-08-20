import { useState } from 'react'
import { breathTrend, heartTrend } from '../data/demo'
import { Btn, Card, CardHead, Chip } from '../components/ui'
import { AreaTrend, Meter } from '../components/charts'

// 健康趋势：对应原型「6-健康趋势」
// 演示数据：周/月趋势序列（后端暂无历史聚合 API，M4 数据集阶段补齐）
// 导出随访报告：调浏览器打印（可另存 PDF）

function monthify(week: { day: string; value: number }[]) {
  // 由一周基线插值出 30 天演示序列
  const out: { day: string; value: number }[] = []
  for (let i = 0; i < 30; i++) {
    const base = week[i % 7]
    const jitter = ((i * 37) % 11) / 10 - 0.5
    out.push({ day: `${i + 1}`, value: Math.round((base.value + jitter) * 10) / 10 })
  }
  return out
}

export default function Trends() {
  const [range, setRange] = useState<'week' | 'month'>('week')
  const breath = range === 'week' ? breathTrend : monthify(breathTrend)
  const heart = range === 'week' ? heartTrend : monthify(heartTrend)
  const avg = (arr: { value: number }[]) => Math.round((arr.reduce((s, d) => s + d.value, 0) / arr.length) * 10) / 10

  return (
    <>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 rounded-[10px] border border-line bg-white px-3.5 py-2.5 text-[13px] text-ink">
          3 床 · 张建国 ▾
        </div>
        <div className="flex gap-1 rounded-[10px] border border-line bg-white p-1">
          {(['week', 'month'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`rounded-lg px-4 py-1.5 text-xs transition-colors ${range === r ? 'bg-sage text-white' : 'text-ink-sub hover:bg-cream'}`}
            >
              {r === 'week' ? '周' : '月'}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-4">
        <Card className="flex-1 p-5">
          <CardHead
            title="呼吸率趋势"
            extra={<span className="text-[11px] text-ink-hint">近{range === 'week' ? ' 7 天' : ' 30 天'} · 平均 {avg(breath)} 次/分</span>}
          />
          <AreaTrend data={breath} color="#6E8F74" />
        </Card>
        <Card className="flex-1 p-5">
          <CardHead
            title="心率趋势"
            extra={<span className="text-[11px] text-ink-hint">近{range === 'week' ? ' 7 天' : ' 30 天'} · 平均 {Math.round(avg(heart))} bpm</span>}
          />
          <AreaTrend data={heart} color="#C97E5A" />
        </Card>
      </div>

      <div className="flex gap-4">
        <Card className="flex-1 p-5">
          <CardHead title="活动量 · 近 7 天" extra={<span className="rounded bg-[#F0EDE3] px-1.5 py-0.5 text-[10px] text-ink-hint">演示</span>} />
          <div className="space-y-3.5">
            <div>
              <div className="mb-1.5 text-xs text-ink-sub">日均活动时长　3.2 小时</div>
              <Meter ratio={0.64} />
            </div>
            <div>
              <div className="mb-1.5 text-xs text-ink-sub">日均步数　约 3200 步</div>
              <Meter ratio={0.48} />
            </div>
            <div>
              <div className="mb-1.5 text-xs text-ink-sub">夜间睡眠　7.1 小时 · 质量良好</div>
              <Meter ratio={0.76} />
            </div>
          </div>
        </Card>

        <Card className="flex w-[340px] shrink-0 flex-col p-5">
          <CardHead title="跌倒风险评估" />
          <div><Chip tone="sage">低风险</Chip></div>
          <p className="text-xs text-ink-sub">近 30 天无跌倒事件 · 步态稳定性良好</p>
          <div className="flex-1" />
          <Btn primary className="w-full" onClick={() => window.print()}>
            导出随访报告
          </Btn>
        </Card>
      </div>
    </>
  )
}

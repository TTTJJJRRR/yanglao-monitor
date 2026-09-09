import { useState } from 'react'
import { activityMeters, breathWeek, heartWeek, monthify } from '../data'
import { AreaMini, Card, Chip, Icon, SubNav } from '../ui'

// 健康趋势：对应原型「5-健康趋势」（周/月分段 + 面积图 + 活动量 + 跌倒风险 + 导出）

export default function Trends({ onBack, onExport }: { onBack: () => void; onExport: () => void }) {
  const [range, setRange] = useState<'week' | 'month'>('week')
  const breath = range === 'week' ? breathWeek : monthify(breathWeek)
  const heart = range === 'week' ? heartWeek : monthify(heartWeek)
  const avg = (arr: number[]) => Math.round((arr.reduce((s, v) => s + v, 0) / arr.length) * 10) / 10

  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav
        title="健康趋势"
        onBack={onBack}
        right={<Icon name="doc" size={18} color="#6B7280" />}
      />
      <div className="space-y-3.5 px-4 py-4">
        <div className="flex gap-1 self-start rounded-full border border-[#E8ECF1] bg-white p-1">
          {(['week', 'month'] as const).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`rounded-full px-5 py-1.5 text-xs transition-colors ${range === r ? 'bg-fam-teal text-white' : 'text-[#6B7280]'}`}
            >
              {r === 'week' ? '周' : '月'}
            </button>
          ))}
        </div>

        <Card className="p-4">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm text-[#1A2027]">呼吸率趋势</span>
            <span className="text-[11px] text-[#9AA3AD]">平均 {avg(breath)} 次/分</span>
          </div>
          <AreaMini values={breath} color="#10B9A8" />
        </Card>

        <Card className="p-4">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-sm text-[#1A2027]">心率趋势</span>
            <span className="text-[11px] text-[#9AA3AD]">平均 {Math.round(avg(heart))} bpm</span>
          </div>
          <AreaMini values={heart} color="#FF5C5C" />
        </Card>

        <Card className="p-4">
          <div className="mb-3 text-sm text-[#1A2027]">活动量 · 近 7 天</div>
          <div className="space-y-3">
            {activityMeters.map((m) => (
              <div key={m.label}>
                <div className="mb-1.5 flex items-center justify-between text-[11px]">
                  <span className="text-[#6B7280]">{m.label}</span>
                  <span className="text-[#1A2027]">{m.value}</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded bg-[#EFF1F4]">
                  <div className="h-full rounded bg-fam-teal" style={{ width: `${m.ratio * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="flex items-center gap-3 p-4">
          <Icon name="shield" size={22} color="#10B9A8" />
          <div className="flex-1">
            <div className="text-sm text-[#1A2027]">跌倒风险评估</div>
            <div className="mt-0.5 text-[11px] text-[#9AA3AD]">近 30 天无跌倒事件 · 步态稳定</div>
          </div>
          <Chip tone="green">低风险</Chip>
        </Card>

        <button
          onClick={onExport}
          className="h-11 w-full rounded-xl border border-fam-teal bg-white text-sm text-fam-deep active:bg-fam-bg"
        >
          导出随访报告
        </button>
      </div>
    </div>
  )
}

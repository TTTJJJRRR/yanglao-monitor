import { useState } from 'react'
import type { Bed, BedStatus, PageKey } from '../types'
import { demoBeds } from '../data/demo'
import { Card, Chip } from '../components/ui'

// 床位看板：对应原型「3-床位看板」（≥8 床单看板，R-P1-03）
// 演示数据：demoBeds（后端暂无床位 API）；点击卡片进入床位详情

const statusMeta: Record<BedStatus, { chip: 'sage' | 'alert' | 'gray'; label: string; hot: boolean }> = {
  normal: { chip: 'sage', label: '正常', hot: false },
  alert: { chip: 'alert', label: '预警', hot: true },
  offline: { chip: 'gray', label: '离线', hot: false },
}

type Filter = 'all' | BedStatus

export default function Beds({ onOpenBed }: { onOpenBed: (bed: Bed) => void }) {
  const [filter, setFilter] = useState<Filter>('all')
  const counts: Record<Filter, number> = {
    all: demoBeds.length,
    normal: demoBeds.filter((b) => b.status === 'normal').length,
    alert: demoBeds.filter((b) => b.status === 'alert').length,
    offline: demoBeds.filter((b) => b.status === 'offline').length,
  }
  const list = demoBeds.filter((b) => filter === 'all' || b.status === filter)
  const tabs: { key: Filter; label: string }[] = [
    { key: 'all', label: '全部' },
    { key: 'normal', label: '正常' },
    { key: 'alert', label: '预警' },
    { key: 'offline', label: '离线' },
  ]

  return (
    <>
      <div className="flex gap-2.5">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setFilter(t.key)}
            className={`rounded-full px-4 py-2 text-[13px] transition-colors ${
              filter === t.key ? 'bg-sage text-white' : 'border border-line bg-white text-ink-sub hover:bg-cream'
            }`}
          >
            {t.label} {counts[t.key]}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        {list.map((b) => {
          const meta = statusMeta[b.status]
          return (
            <Card
              key={b.id}
              className={`cursor-pointer p-4 transition-shadow hover:shadow-md ${meta.hot ? 'border-alert' : ''}`}
            >
              <button className="block w-full text-left" onClick={() => onOpenBed(b)}>
                <div className="mb-2.5 flex items-center justify-between">
                  <span className={`text-[15px] ${b.status === 'offline' ? 'text-ink-sub' : 'text-ink'}`}>
                    {b.id} 床 · {b.elder}
                  </span>
                  <Chip tone={meta.chip}>{meta.label}</Chip>
                </div>
                <div className={`text-xs ${meta.hot ? 'text-alert' : b.status === 'offline' ? 'text-ink-hint' : 'text-ink-sub'}`}>
                  {b.note} · {b.updateTime}
                </div>
              </button>
            </Card>
          )
        })}
      </div>
    </>
  )
}

import type { PageKey } from '../types'
import { elder, me, quickStats, vitals } from '../data'
import { Card, Chip, Icon, Wave } from '../ui'

// 首页：对应原型「2-首页」（问候 + 体征卡 + 快速统计 + 模块入口）

export default function Home({ unread, onNav }: { unread: number; onNav: (p: PageKey) => void }) {
  const entries: { key: PageKey; icon: string; label: string; desc: string; badge?: number }[] = [
    { key: 'trends', icon: 'trend', label: '健康趋势', desc: '呼吸 / 心率 / 活动量' },
    { key: 'daily', icon: 'smile', label: '安心日报', desc: '昨日父亲一切安好' },
    { key: 'alerts', icon: 'bell', label: '预警中心', desc: '关键预警始终送达', badge: unread },
  ]

  return (
    <div className="flex-1 space-y-3.5 overflow-y-auto bg-fam-bg px-4 py-4">
      <div>
        <div className="text-lg text-[#1A2027]">下午好，{me.name}</div>
        <div className="mt-0.5 text-xs text-[#6B7280]">父亲此刻{elder.status}中，一切平稳</div>
      </div>

      {/* 被监护人状态 + 实时体征卡 */}
      <Card className="p-4">
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#E2F5F2] text-base text-fam-deep">
            {elder.name[0]}
          </div>
          <div className="flex-1">
            <div className="text-[15px] text-[#1A2027]">{elder.name} · {elder.relation}</div>
            <div className="mt-0.5 text-[11px] text-[#6B7280]">{elder.room} · 当前{elder.status} · 更新于{elder.updated}</div>
          </div>
          <Chip tone="green">在线</Chip>
        </div>

        <div className="rounded-xl bg-fam-bg p-3">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs text-[#6B7280]">呼吸率</span>
            <span className="text-xs text-[#9AA3AD]">次/分</span>
          </div>
          <div className="flex items-end justify-between">
            <span className="text-2xl text-[#1A2027]">{vitals.breath}</span>
            <div className="w-40"><Wave color="#10B9A8" /></div>
          </div>
        </div>
        <div className="mt-2.5 rounded-xl bg-fam-bg p-3">
          <div className="mb-1 flex items-center justify-between">
            <span className="text-xs text-[#6B7280]">心率</span>
            <span className="text-xs text-[#9AA3AD]">bpm</span>
          </div>
          <div className="flex items-end justify-between">
            <span className="text-2xl text-[#1A2027]">{vitals.heart}</span>
            <div className="w-40"><Wave color="#FF5C5C" /></div>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-1.5 text-[10px] text-[#9AA3AD]">
          <Icon name="shield" size={12} color="#10B9A8" />
          端侧骨骼化监测 · 画面不上云（演示数据）
        </div>
      </Card>

      {/* 快速统计 */}
      <div className="flex gap-2.5">
        {quickStats.map((s) => (
          <Card key={s.label} className="flex-1 p-3">
            <div className="text-[11px] text-[#6B7280]">{s.label}</div>
            <div className={`mt-1 text-base ${s.hot ? 'text-fam-red' : 'text-[#1A2027]'}`}>{s.value}</div>
          </Card>
        ))}
      </div>

      {/* 模块入口 */}
      <Card className="divide-y divide-[#F0F2F5]">
        {entries.map((e) => (
          <button key={e.key} onClick={() => onNav(e.key)} className="flex w-full items-center gap-3 px-4 py-3.5 text-left active:bg-fam-bg">
            <div className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-fam-bg">
              <Icon name={e.icon} size={18} color="#10B9A8" />
            </div>
            <div className="flex-1">
              <div className="text-sm text-[#1A2027]">{e.label}</div>
              <div className="mt-0.5 text-[11px] text-[#9AA3AD]">{e.desc}</div>
            </div>
            {e.badge ? <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-fam-red px-1 text-[11px] text-white">{e.badge}</span> : null}
            <Icon name="chevR" size={16} color="#C4C9D2" />
          </button>
        ))}
      </Card>
    </div>
  )
}

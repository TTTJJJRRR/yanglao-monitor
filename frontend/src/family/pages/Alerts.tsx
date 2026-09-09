import type { ReactNode } from 'react'
import type { AlertItem } from '../types'
import { alertTimeline } from '../data'
import { Card, Chip, Icon, SubNav } from '../ui'

// 预警中心 + 跌倒预警详情：对应原型「4-预警中心」「8-跌倒预警详情」

const levelMeta = {
  red: { dot: 'bg-fam-red', chip: 'red' as const },
  orange: { dot: 'bg-fam-orange', chip: 'orange' as const },
  blue: { dot: 'bg-fam-blue', chip: 'blue' as const },
}

export function AlertsPage({ alerts, onSos, onOpen }: { alerts: AlertItem[]; onSos: () => void; onOpen: (a: AlertItem) => void }) {
  return (
    <div className="flex-1 space-y-3.5 overflow-y-auto bg-fam-bg px-4 py-4">
      <button
        onClick={onSos}
        className="flex h-14 w-full items-center justify-center gap-2 rounded-2xl bg-fam-red text-base text-white active:bg-[#e84f4f]"
      >
        <Icon name="sos" size={20} color="#fff" />
        SOS 紧急呼叫
      </button>

      <div className="space-y-2.5">
        {alerts.map((a) => {
          const meta = levelMeta[a.level]
          return (
            <Card key={a.id} className={a.level === 'red' && a.status === '未处理' ? 'border-fam-red' : ''}>
              <button onClick={() => onOpen(a)} className="flex w-full items-center gap-3 p-4 text-left">
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${meta.dot}`} />
                <div className="flex-1">
                  <div className="text-sm text-[#1A2027]">{a.title}</div>
                  <div className="mt-0.5 text-[11px] text-[#9AA3AD]">{a.place} · {a.time}</div>
                </div>
                <Chip tone={meta.chip}>{a.status}</Chip>
                <Icon name="chevR" size={16} color="#C4C9D2" />
              </button>
            </Card>
          )
        })}
      </div>

      <p className="pt-1 text-center text-[11px] text-[#9AA3AD]">关键预警始终送达 · 不可静音</p>
    </div>
  )
}

function ActionBtn({ danger, children, onClick, className = '' }: { danger?: boolean; children: ReactNode; onClick?: () => void; className?: string }) {
  return (
    <button onClick={onClick} className={`${className} ${danger ? 'bg-fam-red text-white active:bg-[#e84f4f]' : 'bg-white'} text-sm`}>
      {children}
    </button>
  )
}

export function AlertDetailPage({
  alert,
  onBack,
  onCall,
  onHandled,
}: {
  alert: AlertItem
  onBack: () => void
  onCall: () => void
  onHandled: () => void
}) {
  const handled = alert.status === '已处理'
  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav title="预警详情" onBack={onBack} />
      <div className="space-y-3.5 px-4 py-4">
        <div className="rounded-2xl bg-fam-red p-4 text-white">
          <div className="flex items-center gap-2 text-base">
            <Icon name="sos" size={20} color="#fff" />
            {alert.title}
          </div>
          <div className="mt-2 text-xs text-white/85">{alert.time} · {alert.place} · 雷达+视觉双模态确认</div>
        </div>

        <Card className="divide-y divide-[#F0F2F5] px-4">
          {[
            ['检测方式', '毫米波雷达 + 端侧视觉骨骼化'],
            ['融合置信度', '96%'],
            ['已通知对象', '家属微信 + 短信'],
            ['处理状态', alert.status],
          ].map(([k, v]) => (
            <div key={k} className="flex items-center justify-between py-3 text-[13px]">
              <span className="text-[#6B7280]">{k}</span>
              <span className={k === '处理状态' && !handled ? 'text-fam-red' : 'text-[#1A2027]'}>{v}</span>
            </div>
          ))}
        </Card>

        <Card className="p-4">
          <div className="mb-3 text-sm text-[#1A2027]">处置时间线</div>
          {alertTimeline.map((t, i) => (
            <div key={i} className="flex gap-3 pb-3 last:pb-0">
              <div className="flex flex-col items-center">
                <span className={`mt-1 h-2 w-2 rounded-full ${i === alertTimeline.length - 1 ? 'bg-fam-red' : 'bg-fam-teal'}`} />
                {i < alertTimeline.length - 1 && <span className="w-px flex-1 bg-[#E8ECF1]" />}
              </div>
              <div className="flex-1 pb-1">
                <div className="text-[13px] text-[#1A2027]">{t.text}</div>
                <div className="mt-0.5 text-[11px] text-[#9AA3AD]">{t.time}</div>
              </div>
            </div>
          ))}
        </Card>

        <div className="flex gap-2.5 pb-2">
          <ActionBtn danger className="h-11 flex-1 rounded-xl" onClick={onCall}>
            拨打紧急电话
          </ActionBtn>
          <button
            onClick={onHandled}
            disabled={handled}
            className={`h-11 flex-1 rounded-xl text-sm ${
              handled ? 'bg-[#EFF1F4] text-[#8A93A0]' : 'border border-fam-teal bg-white text-fam-deep active:bg-fam-bg'
            }`}
          >
            {handled ? '已处理 ✓' : '标记已处理'}
          </button>
        </div>
      </div>
    </div>
  )
}

import { useState } from 'react'
import type { AlertData } from '../types'
import { Btn, Card, Chip, EmptyHint } from '../components/ui'

// 预警中心：对应原型「5-预警中心」
// 真实数据：/api/alerts + WebSocket 实时推送。
// 注意：后端暂无「标记已处理」API，处理状态目前仅本地生效（刷新还原），接口就位后接通。

type Filter = 'all' | 'unhandled' | 'handled'

const levelDot: Record<string, string> = { red: 'bg-alert', yellow: 'bg-amber' }
const typeMap: Record<string, string> = { fall: '疑似跌倒', vital: '生命体征异常', device: '设备离线', test: '测试预警' }

export default function Alerts({ alerts, onHandled }: { alerts: AlertData[]; onHandled: (id: number) => void }) {
  const [filter, setFilter] = useState<Filter>('all')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const list = alerts.filter((a) =>
    filter === 'all' ? true : filter === 'unhandled' ? !a.is_handled : a.is_handled,
  )
  const selected = alerts.find((a) => a.id === selectedId) ?? list[0] ?? null
  const counts = {
    all: alerts.length,
    unhandled: alerts.filter((a) => !a.is_handled).length,
    handled: alerts.filter((a) => a.is_handled).length,
  }
  const tabs: { key: Filter; label: string }[] = [
    { key: 'all', label: '全部' },
    { key: 'unhandled', label: '未处理' },
    { key: 'handled', label: '已处理' },
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
            } ${t.key === 'unhandled' && filter !== t.key && counts.unhandled > 0 ? 'text-alert' : ''}`}
          >
            {t.label} {counts[t.key]}
          </button>
        ))}
      </div>

      <div className="flex gap-4">
        <Card className="min-h-[480px] flex-1 p-5">
          {list.length === 0 ? (
            <EmptyHint text="当前分类下暂无预警 · 一切安好" />
          ) : (
            list.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelectedId(a.id)}
                className={`flex w-full items-center gap-3 rounded-lg px-2 py-3.5 text-left transition-colors ${
                  selected?.id === a.id ? 'bg-cream' : 'hover:bg-cream/60'
                }`}
              >
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${levelDot[a.level] ?? 'bg-sage'}`} />
                <span className="flex-1 text-sm text-ink">{a.message}</span>
                <span className="text-xs text-ink-hint">
                  {new Date(a.timestamp_ms).toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </span>
                <Chip tone={a.is_handled ? 'gray' : a.level === 'red' ? 'alert' : 'amber'}>
                  {a.is_handled ? '已处理' : a.level === 'red' ? '未处理' : '已跟进'}
                </Chip>
              </button>
            ))
          )}
        </Card>

        <Card className="flex min-h-[480px] w-[400px] shrink-0 flex-col p-5">
          {selected ? (
            <>
              <div className="text-base text-ink">预警详情</div>
              <div className={`text-sm ${selected.level === 'red' ? 'text-alert' : 'text-amber'}`}>
                {typeMap[selected.type] ?? selected.type} · {selected.level === 'red' ? '红色预警' : '黄色提醒'}
              </div>
              <div className="space-y-2 text-xs text-ink-sub">
                <div>内容：{selected.message}</div>
                <div>时间：{new Date(selected.timestamp_ms).toLocaleString('zh-CN')}</div>
                <div>检测方式：毫米波雷达 + 端侧视觉骨骼化</div>
                <div>通知渠道：家属微信 + 短信（关键预警始终送达，不可静音）</div>
              </div>
              <div className="flex-1" />
              {!selected.is_handled && (
                <Btn danger className="w-full" onClick={() => onHandled(selected.id)}>
                  立即处理 · 联系床位护工
                </Btn>
              )}
              <Btn className="w-full" onClick={() => !selected.is_handled && onHandled(selected.id)}>
                {selected.is_handled ? '已处理 ✓' : '标记已处理'}
              </Btn>
              <p className="text-center text-[10px] text-ink-hint">处理状态暂存本地 · 后端接口就位后同步</p>
            </>
          ) : (
            <EmptyHint text="选择左侧预警查看详情" />
          )}
        </Card>
      </div>
    </>
  )
}

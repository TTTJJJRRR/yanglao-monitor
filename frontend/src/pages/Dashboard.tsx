import type { AlertData, PageKey } from '../types'
import { demoBeds, demoDevices, weekAlertBars } from '../data/demo'
import { Card, CardHead, Chip } from '../components/ui'
import { Meter, WeekBars } from '../components/charts'

// 总览：对应原型「2-总览」
// 真实数据：今日预警数、预警动态（/api/alerts + WebSocket）
// 演示数据：在住老人/日报/楼层床位/本周趋势（后端暂无对应 API）

function StatCard({ label, value, sub, subTone = 'sage', demo }: { label: string; value: string; sub: string; subTone?: 'sage' | 'alert' | 'gray'; demo?: boolean }) {
  return (
    <Card className="flex-1 p-[18px]">
      <div className="flex items-center gap-2 text-[13px] text-ink-sub">
        {label}
        {demo && <span className="rounded bg-[#F0EDE3] px-1.5 py-0.5 text-[10px] text-ink-hint">演示</span>}
      </div>
      <div className="mt-1.5 text-[28px] leading-8 text-ink">{value}</div>
      <div className={`mt-1.5 text-xs ${subTone === 'alert' ? 'text-alert' : subTone === 'gray' ? 'text-ink-sub' : 'text-sage'}`}>{sub}</div>
    </Card>
  )
}

const levelDot: Record<string, string> = { red: 'bg-alert', yellow: 'bg-amber' }

export default function Dashboard({ alerts, onNavigate }: { alerts: AlertData[]; onNavigate: (p: PageKey) => void }) {
  const today = new Date().toDateString()
  const todayAlerts = alerts.filter((a) => new Date(a.timestamp_ms).toDateString() === today)
  const unhandled = alerts.filter((a) => !a.is_handled)
  const onlineDevices = demoDevices.filter((d) => d.online).length

  const floor2 = demoBeds.filter((b) => b.floor === '2F')
  const floor3 = demoBeds.filter((b) => b.floor === '3F')
  const ok2 = floor2.filter((b) => b.status === 'normal').length
  const ok3 = floor3.filter((b) => b.status === 'normal').length

  return (
    <>
      <div className="flex gap-4">
        <StatCard label="在住老人" value="42 人" sub="较上周 +2" demo />
        <StatCard label="今日预警" value={`${todayAlerts.length} 条`} sub={unhandled.length ? `${unhandled.length} 条未处理 · 需跟进` : '均已处理'} subTone={unhandled.length ? 'alert' : 'sage'} />
        <StatCard label="设备在线" value={`${onlineDevices} / ${demoDevices.length}`} sub={onlineDevices === demoDevices.length ? '全部运行正常' : '1 台离线 · 已派单检修'} subTone={onlineDevices === demoDevices.length ? 'sage' : 'alert'} demo />
        <StatCard label="安心日报已读" value="36 / 42" sub="家属阅读率 85%" subTone="gray" demo />
      </div>

      <div className="flex gap-4">
        <Card className="flex-1 p-5">
          <CardHead
            title="预警动态"
            extra={
              <button className="text-xs text-sage hover:text-sage-deep" onClick={() => onNavigate('alerts')}>
                查看全部 →
              </button>
            }
          />
          {alerts.length === 0 ? (
            <div className="py-8 text-center text-sm text-ink-hint">暂无预警 · 一切安好</div>
          ) : (
            alerts.slice(0, 3).map((a) => (
              <div key={a.id} className="flex items-center gap-3 py-3">
                <span className={`h-2.5 w-2.5 rounded-full ${levelDot[a.level] ?? 'bg-sage'}`} />
                <span className="flex-1 text-sm text-ink">{a.message}</span>
                <span className="text-xs text-ink-hint">{new Date(a.timestamp_ms).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</span>
                <Chip tone={a.is_handled ? 'gray' : a.level === 'red' ? 'alert' : 'amber'}>{a.is_handled ? '已处理' : a.level === 'red' ? '未处理' : '已跟进'}</Chip>
              </div>
            ))
          )}
        </Card>

        <Card className="w-[340px] shrink-0 p-5">
          <CardHead title="床位状态" />
          <div className="mb-3 text-xs text-ink-sub">两栋照护楼 · {demoBeds.length} 床演示</div>
          <div className="space-y-4 pt-1">
            <div>
              <div className="mb-2 flex items-center justify-between text-[13px]">
                <span className="text-ink">2F · 自理区</span>
                <span className="text-xs text-sage">{ok2} / {floor2.length} 正常</span>
              </div>
              <Meter ratio={ok2 / floor2.length} />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-[13px]">
                <span className="text-ink">3F · 照护区</span>
                <span className="text-xs text-amber">{ok3} / {floor3.length} · {floor3.length - ok3} 床需关注</span>
              </div>
              <Meter ratio={ok3 / floor3.length} color="#D9A050" />
            </div>
            <p className="pt-1 text-[11px] text-ink-hint">离线设备 1 台 · 已派单检修</p>
          </div>
        </Card>
      </div>

      <Card className="p-5">
        <CardHead title="本周预警趋势" extra={<span className="rounded bg-[#F0EDE3] px-1.5 py-0.5 text-[10px] text-ink-hint">演示</span>} />
        <WeekBars data={weekAlertBars} peakIndex={5} />
      </Card>
    </>
  )
}

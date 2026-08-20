import type { Bed, BehaviorData, VitalData } from '../types'
import { behaviorTimeline, demoDevices } from '../data/demo'
import { Btn, Card, CardHead, Chip } from '../components/ui'
import { LiveWave } from '../components/charts'

// 床位详情：对应原型「4-床位详情」
// 真实数据：呼吸/心率数值与波形由 WebSocket 实时流驱动（当前为 mock 源，M1 切真实雷达）
// 演示数据：行为时间线、设备状态

const behaviorMap: Record<string, string> = {
  walking: '行走', standing: '站立', sitting_still: '静坐', standing_up: '起身',
  crouching: '弯腰/蹲下', lying: '卧床', lying_floor: '倒地不起', falling: '跌倒', normal_activity: '正常活动',
}

export default function BedDetail({
  bed,
  vitals,
  behavior,
  onBack,
}: {
  bed: Bed
  vitals: VitalData[]
  behavior: BehaviorData | null
  onBack: () => void
}) {
  const last = vitals[0]
  const breathSeries = vitals.slice(0, 30).reverse().map((v) => v.breath_rate ?? 0)
  const heartSeries = vitals.slice(0, 30).reverse().map((v) => v.heart_rate ?? 0)

  return (
    <>
      <button className="text-[13px] text-sage hover:text-sage-deep" onClick={onBack}>
        ← 返回床位看板
      </button>

      <Card className="flex h-[88px] items-center gap-4 px-5">
        <div className="flex h-[52px] w-[52px] items-center justify-center rounded-full bg-sage-tint text-xl text-sage-deep">
          {bed.elder[0]}
        </div>
        <div className="flex-1">
          <div className="text-[17px] text-ink">{bed.elder}</div>
          <div className="mt-1 text-xs text-ink-sub">{bed.id} 床 · {bed.floor} 自理区 · 入住 2025-03-12 · 高血压病史</div>
        </div>
        <Btn>联系家属</Btn>
        <Btn danger>紧急呼叫</Btn>
      </Card>

      <div className="flex gap-4">
        <Card className="flex-1 p-5">
          <CardHead
            title="呼吸率 · 实时"
            extra={<span className="rounded bg-sage-tint px-1.5 py-0.5 text-[10px] text-sage-deep">WS 实时流 · mock 源</span>}
          />
          <div className="text-3xl text-ink">{last?.breath_rate ?? '--'} <span className="text-sm text-ink-hint">次/分</span></div>
          <div className="mb-1 mt-1 text-[11px] text-sage">正常范围 12–20 · 平稳</div>
          <LiveWave values={breathSeries} color="#6E8F74" />
        </Card>
        <Card className="flex-1 p-5">
          <CardHead
            title="心率 · 实时"
            extra={<span className="rounded bg-sage-tint px-1.5 py-0.5 text-[10px] text-sage-deep">WS 实时流 · mock 源</span>}
          />
          <div className="text-3xl text-ink">{last?.heart_rate ?? '--'} <span className="text-sm text-ink-hint">bpm</span></div>
          <div className="mb-1 mt-1 text-[11px] text-sage">正常范围 60–100 · 平稳</div>
          <LiveWave values={heartSeries} color="#C97E5A" />
        </Card>
      </div>

      <div className="flex gap-4">
        <Card className="flex-1 p-5">
          <CardHead
            title="今日行为时间线"
            extra={
              behavior && (
                <Chip tone={behavior.action === 'falling' || behavior.action === 'lying_floor' ? 'alert' : 'sage'}>
                  当前：{behaviorMap[behavior.action] ?? behavior.action} {Math.round(behavior.confidence * 100)}%
                </Chip>
              )
            }
          />
          {behaviorTimeline.map((e) => (
            <div key={e.time} className="flex items-center gap-2.5 py-3">
              <span className={`h-2 w-2 rounded-full ${e.hot ? 'bg-alert' : 'bg-sage'}`} />
              <span className={`text-[13px] ${e.hot ? 'text-alert' : 'text-ink'}`}>{e.time}　{e.text}</span>
            </div>
          ))}
        </Card>

        <Card className="w-[340px] shrink-0 p-5">
          <CardHead title="设备状态" extra={<span className="rounded bg-[#F0EDE3] px-1.5 py-0.5 text-[10px] text-ink-hint">演示</span>} />
          {demoDevices.slice(0, 2).map((d) => (
            <div key={d.name} className="flex items-center justify-between py-2.5">
              <span className="text-[13px] text-ink">{d.name}</span>
              <Chip tone="sage">在线</Chip>
            </div>
          ))}
          <p className="pt-2 text-[11px] text-ink-hint">信号良好 · 画面端侧骨骼化 · 不上云</p>
        </Card>
      </div>
    </>
  )
}

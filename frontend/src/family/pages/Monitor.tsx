import { elder, vitals } from '../data'
import { Card, Icon, Wave } from '../ui'

// 实时监测：对应原型「3-实时监测」（呼吸/心率大卡 + 行为行）

export default function Monitor() {
  return (
    <div className="flex-1 space-y-3.5 overflow-y-auto bg-fam-bg px-4 py-4">
      <Card className="p-4">
        <div className="mb-1 flex items-center justify-between">
          <span className="text-sm text-[#6B7280]">呼吸率 · 实时</span>
          <span className="rounded bg-[#E2F5F2] px-2 py-0.5 text-[10px] text-fam-deep">演示数据</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-[34px] leading-10 text-[#1A2027]">{vitals.breath}</span>
          <span className="text-xs text-[#9AA3AD]">次/分 · 正常 12–20</span>
        </div>
        <Wave color="#10B9A8" />
      </Card>

      <Card className="p-4">
        <div className="mb-1 flex items-center justify-between">
          <span className="text-sm text-[#6B7280]">心率 · 实时</span>
          <span className="rounded bg-[#E2F5F2] px-2 py-0.5 text-[10px] text-fam-deep">演示数据</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-[34px] leading-10 text-[#1A2027]">{vitals.heart}</span>
          <span className="text-xs text-[#9AA3AD]">bpm · 正常 60–100</span>
        </div>
        <Wave color="#FF5C5C" />
      </Card>

      <Card className="flex items-center gap-3 p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-fam-bg">
          <Icon name="walk" size={20} color="#10B9A8" />
        </div>
        <div className="flex-1">
          <div className="text-sm text-[#1A2027]">当前行为：{elder.status} · {elder.room}</div>
          <div className="mt-0.5 text-[11px] text-[#9AA3AD]">情绪{elder.mood} · 更新于{elder.updated} · 雷达+视觉双模态</div>
        </div>
      </Card>
    </div>
  )
}

import { demoDevices } from '../data/demo'
import { Btn, Card } from '../components/ui'

// 设备管理：对应原型「7-设备管理」
// 演示数据：demoDevices（后端暂无设备注册表 API）；在线状态后续接 WS 心跳

export default function Devices() {
  const radar = demoDevices.filter((d) => d.kind.includes('雷达'))
  const vision = demoDevices.filter((d) => d.kind.includes('视觉'))
  const offline = demoDevices.filter((d) => !d.online)

  return (
    <>
      <div className="flex items-center justify-between">
        <div className="flex gap-2.5">
          <span className="rounded-full border border-line bg-white px-4 py-2 text-[13px] text-ink">
            毫米波雷达 {radar.length} 台 · {radar.filter((d) => d.online).length} 在线
          </span>
          <span className="rounded-full border border-line bg-white px-4 py-2 text-[13px] text-ink">
            视觉节点 {vision.length} 台 · 全部在线
          </span>
          {offline.length > 0 && (
            <span className="rounded-full bg-alert-tint px-4 py-2 text-[13px] text-alert">
              {offline.length} 台离线 · 已派单检修
            </span>
          )}
        </div>
        <Btn primary>+ 添加设备</Btn>
      </div>

      <Card className="overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="h-12 bg-cream text-xs text-ink-sub">
              <th className="w-[240px] px-5 font-normal">设备名称</th>
              <th className="w-[220px] font-normal">类型</th>
              <th className="w-[240px] font-normal">位置</th>
              <th className="w-[120px] font-normal">状态</th>
              <th className="font-normal">最近心跳</th>
            </tr>
          </thead>
          <tbody>
            {demoDevices.map((d, i) => (
              <tr key={d.name} className={`h-14 text-[13px] ${i > 0 ? 'border-t border-[#F0EDE3]' : ''}`}>
                <td className="px-5 text-ink">{d.name}</td>
                <td className="text-ink-sub">{d.kind}</td>
                <td className="text-ink-sub">{d.location}</td>
                <td className={d.online ? 'text-sage-deep' : 'text-alert'}>{d.online ? '● 在线' : '● 离线'}</td>
                <td className="text-ink-sub">{d.heartbeat}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </>
  )
}

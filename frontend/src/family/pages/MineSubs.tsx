import { useState } from 'react'
import type { FamilyDevice, Message, Ward } from '../types'
import { faqs } from '../data'
import { Card, Chip, Icon, SubNav, Toggle } from '../ui'

// 我的页 5 个下钻：被监护人管理 / 设备管理 / 消息通知 / 隐私与数据 / 帮助与关于
// 对应原型 9/10/11/12/14 五屏（13-通知与免打扰已按产品决策删除，永不提供）

/* ---------- 9-被监护人管理 ---------- */
export function WardsPage({ wards, onBack, onAdd }: { wards: Ward[]; onBack: () => void; onAdd: () => void }) {
  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav title="被监护人管理" onBack={onBack} />
      <div className="space-y-3 px-4 py-4">
        {wards.map((w) => (
          <Card key={w.name} className="flex items-center gap-3 p-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#E2F5F2] text-lg text-fam-deep">
              {w.name[0]}
            </div>
            <div className="flex-1">
              <div className="text-[15px] text-[#1A2027]">{w.name} · {w.relation}</div>
              <div className="mt-0.5 text-[11px] text-[#9AA3AD]">{w.age} 岁 · {w.tags}</div>
            </div>
            <Chip tone="teal">已绑定</Chip>
          </Card>
        ))}
        <button
          onClick={onAdd}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl border border-dashed border-fam-teal bg-white text-sm text-fam-deep active:bg-fam-bg"
        >
          <Icon name="plus" size={16} color="#0B8C80" />
          添加被监护人
        </button>
      </div>
    </div>
  )
}

/* ---------- 10-设备管理 ---------- */
export function DevicesPage({ devices, onBack, onBind }: { devices: FamilyDevice[]; onBack: () => void; onBind: () => void }) {
  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav title="设备管理" onBack={onBack} />
      <div className="space-y-3 px-4 py-4">
        {devices.map((d) => (
          <Card key={d.name} className="flex items-center gap-3 p-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-[10px] bg-fam-bg">
              <Icon name="radar" size={20} color="#10B9A8" />
            </div>
            <div className="flex-1">
              <div className="text-[15px] text-[#1A2027]">{d.name}</div>
              <div className="mt-0.5 text-[11px] text-[#9AA3AD]">{d.place}</div>
            </div>
            <Chip tone={d.online ? 'green' : 'gray'}>{d.online ? '在线' : '离线'}</Chip>
          </Card>
        ))}
        <button
          onClick={onBind}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl border border-dashed border-fam-teal bg-white text-sm text-fam-deep active:bg-fam-bg"
        >
          <Icon name="plus" size={16} color="#0B8C80" />
          绑定新设备
        </button>
        <p className="text-center text-[11px] text-[#9AA3AD]">视觉设备仅端侧骨骼化 · 画面不上云</p>
      </div>
    </div>
  )
}

/* ---------- 11-消息通知（仅收件箱，无免打扰） ---------- */
export function MessagesPage({ messages, onBack, onRead }: { messages: Message[]; onBack: () => void; onRead: (id: number) => void }) {
  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav title="消息通知" onBack={onBack} />
      <div className="px-4 py-4">
        <Card className="divide-y divide-[#F0F2F5]">
          {messages.map((m) => (
            <button key={m.id} onClick={() => onRead(m.id)} className="flex w-full items-start gap-3 px-4 py-3.5 text-left active:bg-fam-bg">
              <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${m.unread ? 'bg-fam-red' : 'bg-transparent'}`} />
              <div className="flex-1">
                <div className={`text-sm ${m.unread ? 'text-[#1A2027] font-medium' : 'text-[#6B7280]'}`}>{m.title}</div>
                <div className="mt-0.5 text-[11px] text-[#9AA3AD]">{m.desc}</div>
              </div>
              <span className="text-[11px] text-[#C4C9D2]">{m.time}</span>
            </button>
          ))}
        </Card>
        <p className="mt-3 text-center text-[11px] text-[#9AA3AD]">关键预警消息始终送达 · 点击可标记已读</p>
      </div>
    </div>
  )
}

/* ---------- 12-隐私与数据 ---------- */
export function PrivacyPage({
  boneOn,
  onToggleBone,
  onExport,
  onPolicy,
  onBack,
}: {
  boneOn: boolean
  onToggleBone: (v: boolean) => void
  onExport: () => void
  onPolicy: () => void
  onBack: () => void
}) {
  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav title="隐私与数据" onBack={onBack} />
      <div className="space-y-3.5 px-4 py-4">
        <Card className="divide-y divide-[#F0F2F5] px-4">
          <div className="flex items-center gap-3 py-4">
            <Icon name="shield" size={20} color="#10B9A8" />
            <div className="flex-1">
              <div className="text-sm text-[#1A2027]">视频端侧骨骼化</div>
              <div className="mt-0.5 text-[11px] text-[#9AA3AD]">只上传骨骼点坐标，原始画面不出设备</div>
            </div>
            <Toggle on={boneOn} onChange={onToggleBone} />
          </div>
          <div className="flex items-center gap-3 py-4">
            <Icon name="lock" size={20} color="#10B9A8" />
            <div className="flex-1">
              <div className="text-sm text-[#1A2027]">AES-256 加密存储</div>
              <div className="mt-0.5 text-[11px] text-[#9AA3AD]">体征与行为数据加密落盘</div>
            </div>
            <Chip tone="teal">已启用</Chip>
          </div>
        </Card>

        <Card className="divide-y divide-[#F0F2F5]">
          {[
            { label: '数据导出', action: onExport },
            { label: '隐私政策', action: onPolicy },
          ].map((r) => (
            <button key={r.label} onClick={r.action} className="flex w-full items-center justify-between px-4 py-3.5 text-left active:bg-fam-bg">
              <span className="text-sm text-[#1A2027]">{r.label}</span>
              <Icon name="chevR" size={16} color="#C4C9D2" />
            </button>
          ))}
        </Card>
      </div>
    </div>
  )
}

/* ---------- 14-帮助与关于 ---------- */
export function AboutPage({ onBack, onContact }: { onBack: () => void; onContact: (what: string) => void }) {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <div className="flex-1 overflow-y-auto bg-fam-bg">
      <SubNav title="帮助与关于" onBack={onBack} />
      <div className="space-y-3.5 px-4 py-4">
        <Card className="divide-y divide-[#F0F2F5]">
          {faqs.map((f, i) => (
            <div key={i}>
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="flex w-full items-center justify-between px-4 py-3.5 text-left active:bg-fam-bg"
              >
                <span className="text-sm text-[#1A2027]">{f.q}</span>
                <span className={`transition-transform ${open === i ? 'rotate-90' : ''}`}>
                  <Icon name="chevR" size={16} color="#C4C9D2" />
                </span>
              </button>
              {open === i && <div className="px-4 pb-4 text-xs leading-relaxed text-[#6B7280]">{f.a}</div>}
            </div>
          ))}
        </Card>

        <Card className="divide-y divide-[#F0F2F5]">
          {['联系客服', '关于我们'].map((label) => (
            <button key={label} onClick={() => onContact(label)} className="flex w-full items-center justify-between px-4 py-3.5 text-left active:bg-fam-bg">
              <span className="text-sm text-[#1A2027]">{label}</span>
              <Icon name="chevR" size={16} color="#C4C9D2" />
            </button>
          ))}
        </Card>

        <p className="pt-2 text-center text-[11px] text-[#C4C9D2]">智能康养监测系统 · v0.1.0-demo</p>
      </div>
    </div>
  )
}

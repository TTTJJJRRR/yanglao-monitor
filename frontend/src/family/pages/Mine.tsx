import type { PageKey } from '../types'
import { me } from '../data'
import { Card, Icon } from '../ui'

// 我的：对应原型「7-我的」（资料卡 + 账户与设置 + 通用 + 退出登录）
// 注意：无「免打扰/关闭推送」入口——关键预警始终送达（产品红线）

export default function Mine({
  unreadMessages,
  onNav,
  onLogout,
}: {
  unreadMessages: number
  onNav: (p: PageKey) => void
  onLogout: () => void
}) {
  const groups: { title: string; rows: { key: PageKey; icon: string; label: string; badge?: number }[] }[] = [
    {
      title: '账户与设置',
      rows: [
        { key: 'wards', icon: 'users', label: '被监护人管理' },
        { key: 'devices', icon: 'radar', label: '设备管理' },
        { key: 'messages', icon: 'bell', label: '消息通知', badge: unreadMessages },
        { key: 'privacy', icon: 'lock', label: '隐私与数据' },
      ],
    },
    {
      title: '通用',
      rows: [{ key: 'about', icon: 'question', label: '帮助与关于' }],
    },
  ]

  return (
    <div className="flex-1 space-y-4 overflow-y-auto bg-fam-bg px-4 py-4">
      {/* 资料卡 */}
      <Card className="flex items-center gap-3.5 p-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-fam-teal text-xl text-white">陈</div>
        <div className="flex-1">
          <div className="text-lg text-[#1A2027]">{me.name}</div>
          <div className="mt-1 text-xs text-[#6B7280]">{me.role}</div>
        </div>
        <Icon name="gear" size={20} color="#6B7280" />
      </Card>

      {groups.map((g) => (
        <div key={g.title}>
          <div className="mb-2 px-1 text-xs text-[#9AA3AD]">{g.title}</div>
          <Card className="divide-y divide-[#F0F2F5]">
            {g.rows.map((r) => (
              <button key={r.key} onClick={() => onNav(r.key)} className="flex w-full items-center gap-3 px-4 py-3.5 text-left active:bg-fam-bg">
                <div className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-fam-bg">
                  <Icon name={r.icon} size={18} color="#10B9A8" />
                </div>
                <span className="flex-1 text-sm text-[#1A2027]">{r.label}</span>
                {r.badge ? <span className="h-2 w-2 rounded-full bg-fam-red" /> : null}
                <Icon name="chevR" size={16} color="#C4C9D2" />
              </button>
            ))}
          </Card>
        </div>
      ))}

      <button
        onClick={onLogout}
        className="h-12 w-full rounded-2xl border border-fam-red/60 bg-white text-[15px] text-fam-red active:bg-[#FFEBEB]"
      >
        退出登录
      </button>
    </div>
  )
}

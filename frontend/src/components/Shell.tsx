import type { ReactNode } from 'react'
import type { PageKey } from '../types'

// 外壳：左侧导航 + 顶栏，1:1 对应 Ardot 原型

const stroke = (active: boolean) => (active ? '#55745C' : '#7C8274')

function Icon({ name, active }: { name: string; active: boolean }) {
  const c = stroke(active)
  const common = { width: 18, height: 18, viewBox: '0 0 18 18', fill: 'none' as const }
  switch (name) {
    case 'dashboard':
      return (
        <svg {...common}>
          <rect x="1.5" y="1.5" width="6" height="6" rx="1.5" stroke={c} strokeWidth="1.5" />
          <rect x="10.5" y="1.5" width="6" height="6" rx="1.5" stroke={c} strokeWidth="1.5" />
          <rect x="1.5" y="10.5" width="6" height="6" rx="1.5" stroke={c} strokeWidth="1.5" />
          <rect x="10.5" y="10.5" width="6" height="6" rx="1.5" stroke={c} strokeWidth="1.5" />
        </svg>
      )
    case 'beds':
      return (
        <svg {...common}>
          <path d="M2 13.5V5M2 10.5h14v3M5.5 7.5H9a2 2 0 0 1 2 2v1" stroke={c} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="4.2" cy="6.6" r="1.1" stroke={c} strokeWidth="1.5" />
        </svg>
      )
    case 'alerts':
      return (
        <svg {...common}>
          <path d="M9 2.8a4.2 4.2 0 0 0-4.2 4.2c0 2.8-.9 3.8-1.4 4.3h11.2c-.5-.5-1.4-1.5-1.4-4.3A4.2 4.2 0 0 0 9 2.8Z" stroke={c} strokeWidth="1.5" strokeLinejoin="round" />
          <path d="M7.4 13.8a1.6 1.6 0 0 0 3.2 0" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      )
    case 'trends':
      return (
        <svg {...common}>
          <path d="M2.5 2.5v13h13" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
          <path d="M5 11.5l3-4 2.5 2.5L14.5 5" stroke={c} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )
    case 'devices':
      return (
        <svg {...common}>
          <path d="M3.5 13a7.5 7.5 0 0 1 11 0" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
          <path d="M6 13a4 4 0 0 1 6 0" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="9" cy="13" r="1.3" fill={c} />
        </svg>
      )
    case 'elders':
      return (
        <svg {...common}>
          <circle cx="6.5" cy="5.5" r="2.5" stroke={c} strokeWidth="1.5" />
          <path d="M2.5 14.8c.5-2.6 2-4 4-4s3.5 1.4 4 4" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
          <path d="M11.6 3.3a2.3 2.3 0 1 1 .8 4.5" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
          <path d="M12.8 10.9c1.6.3 2.6 1.5 3 3.9" stroke={c} strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      )
    default:
      return null
  }
}

const MENU: { key: PageKey; label: string; icon: string }[] = [
  { key: 'dashboard', label: '总览', icon: 'dashboard' },
  { key: 'beds', label: '床位看板', icon: 'beds' },
  { key: 'alerts', label: '预警中心', icon: 'alerts' },
  { key: 'trends', label: '健康趋势', icon: 'trends' },
  { key: 'devices', label: '设备管理', icon: 'devices' },
  { key: 'elders', label: '老人档案', icon: 'elders' },
]

export function Shell({
  page,
  onNavigate,
  title,
  sub,
  unreadAlerts,
  online,
  onLogout,
  children,
}: {
  page: PageKey
  onNavigate: (p: PageKey) => void
  title: string
  sub: string
  unreadAlerts: number
  online: boolean
  onLogout: () => void
  children: ReactNode
}) {
  return (
    <div className="flex min-h-screen bg-cream">
      {/* 侧边栏 220px */}
      <aside className="flex w-[220px] shrink-0 flex-col items-center gap-1 bg-white py-0">
        <div className="flex h-[72px] w-full items-center gap-3 pl-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-[10px] bg-sage">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M2 9.5h3l2-4.5 3.5 9 2-4.5H16" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div>
            <div className="text-[15px] leading-tight text-ink">智能康养</div>
            <div className="text-[11px] text-ink-sub">机构管理端</div>
          </div>
        </div>
        <div className="h-px w-full bg-[#F0EDE3]" />
        {MENU.map((m) => {
          const active = page === m.key || (page === 'bedDetail' && m.key === 'beds')
          return (
            <button
              key={m.key}
              onClick={() => onNavigate(m.key)}
              className={`flex h-11 w-[188px] items-center gap-2.5 rounded-[10px] px-3 text-left text-sm transition-colors ${
                active ? 'bg-sage-tint text-sage-deep' : 'text-ink-sub hover:bg-cream'
              }`}
            >
              <Icon name={m.icon} active={active} />
              <span className="flex-1">{m.label}</span>
              {m.key === 'alerts' && unreadAlerts > 0 && (
                <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-alert px-1 text-[11px] text-white">
                  {unreadAlerts}
                </span>
              )}
            </button>
          )
        })}
        <div className="flex-1" />
        <button
          onClick={onLogout}
          className="mb-4 flex h-11 w-[188px] items-center gap-2.5 rounded-[10px] px-3 text-left text-sm text-ink-sub hover:bg-cream"
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M7 3H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3M11 12l3-3-3-3M14 9H7" stroke="#7C8274" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          退出登录
        </button>
      </aside>

      {/* 主区 */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[72px] items-center justify-between bg-white px-7">
          <div>
            <div className="text-xl text-ink">{title}</div>
            <div className="mt-0.5 text-xs text-ink-sub">{sub}</div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`flex items-center gap-1.5 text-xs ${online ? 'text-sage-deep' : 'text-ink-hint'}`}>
              <span className={`h-2 w-2 rounded-full ${online ? 'bg-sage' : 'bg-ink-hint'}`} />
              {online ? '实时数据已连接' : '实时数据未连接'}
            </span>
            <button
              onClick={() => onNavigate('alerts')}
              className="relative flex h-[38px] w-[38px] items-center justify-center rounded-full bg-cream"
              title="预警中心"
            >
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 2.8a4.2 4.2 0 0 0-4.2 4.2c0 2.8-.9 3.8-1.4 4.3h11.2c-.5-.5-1.4-1.5-1.4-4.3A4.2 4.2 0 0 0 9 2.8Z" stroke="#343B32" strokeWidth="1.5" strokeLinejoin="round" />
                <path d="M7.4 13.8a1.6 1.6 0 0 0 3.2 0" stroke="#343B32" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              {unreadAlerts > 0 && <span className="absolute right-1.5 top-2 h-2 w-2 rounded-full bg-alert" />}
            </button>
            <div className="flex h-[38px] w-[38px] items-center justify-center rounded-full bg-sage-tint text-sm text-sage-deep">陈</div>
            <span className="text-[13px] text-ink">陈静 · 院长</span>
          </div>
        </header>
        <main className="flex-1 space-y-4 p-6">{children}</main>
      </div>
    </div>
  )
}

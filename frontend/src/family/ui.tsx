import type { ReactNode } from 'react'

// 家属小程序基础组件：图标 / 卡片 / 标章 / 弹窗 / 状态栏 / 底部胶囊栏 / 子页导航 / 开关 / 图表

const PATHS: Record<string, string> = {
  pulse: 'M2 9.5h3l2-4.5 3.5 9 2-4.5H16',
  home: 'M2.5 8.5 9 3l6.5 5.5M4.5 7.5V15h9V7.5',
  wave: 'M2 9h2.5l2-5 3 10 2-7 1.5 2H16',
  bell: 'M9 2.8a4.2 4.2 0 0 0-4.2 4.2c0 2.8-.9 3.8-1.4 4.3h11.2c-.5-.5-1.4-1.5-1.4-4.3A4.2 4.2 0 0 0 9 2.8ZM7.4 13.8a1.6 1.6 0 0 0 3.2 0',
  user: 'M9 8.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM3 15.5c.8-3 3-4.5 6-4.5s5.2 1.5 6 4.5',
  users: 'M6.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM2.5 14.8c.5-2.6 2-4 4-4s3.5 1.4 4 4M11.6 3.3a2.3 2.3 0 1 1 .8 4.5M12.8 10.9c1.6.3 2.6 1.5 3 3.9',
  chevL: 'M11 3.5 5.5 9 11 14.5',
  chevR: 'M7 3.5 12.5 9 7 14.5',
  heart: 'M9 15S2.5 11 2.5 6.8A3.6 3.6 0 0 1 9 5a3.6 3.6 0 0 1 6.5 1.8C15.5 11 9 15 9 15Z',
  trend: 'M2.5 15.5h13M4 12l3.5-4 3 2.5 4-5.5',
  smile: 'M9 16a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM6 10.5c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5M6.2 6.8h.01M11.8 6.8h.01',
  shield: 'M9 2 3.5 4v4.5c0 3.5 2.3 6 5.5 7.5 3.2-1.5 5.5-4 5.5-7.5V4L9 2Z',
  phone: 'M3.5 3.5c.5-1 1.5-1.5 2-1l1.5 2.5c.3.5 0 1.2-.5 1.7l-.7.7c1 2 3 4 5 5l.7-.7c.5-.5 1.2-.8 1.7-.5l2.5 1.5c.5.5 0 1.5-1 2-3 1.5-8.5-3-10-7s-.5-3.3-.2-3.7Z',
  share: 'M11 3.5 14.5 7 11 10.5M14 7H7a4 4 0 0 0-4 4v3.5',
  plus: 'M9 3v12M3 9h12',
  radar: 'M3.5 13a7.5 7.5 0 0 1 11 0M6 13a4 4 0 0 1 6 0M9 13h.01',
  doc: 'M4.5 2.5h6L14 6v9.5h-9.5v-13ZM10.5 2.5V6H14M7 9h4M7 12h4',
  question: 'M9 16a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM6.8 6.8A2.3 2.3 0 0 1 9 5.5c1.3 0 2.3 1 2.3 2.1 0 1.5-2 1.7-2.3 3.1M9 12.5h.01',
  lock: 'M5 8V6a4 4 0 0 1 8 0v2M4 8h10v7H4V8ZM9 11v1.5',
  check: 'M3 9.5 7 13.5 15 4.5',
  walk: 'M10 3.5a1.5 1.5 0 1 0 0 .01ZM8 16l1-4-2-1 1.5-4L11 8l2 1.5M7 8l1.5-1M11 8l1 3.5 2 1-1 3.5',
  moon: 'M14 10.5A6 6 0 0 1 7.5 4a6 6 0 1 0 6.5 6.5Z',
  gear: 'M9 11.2a2.2 2.2 0 1 0 0-4.4 2.2 2.2 0 0 0 0 4.4ZM9 2.2v1.8M9 14v1.8M2.2 9H4M14 9h1.8M4.3 4.3l1.3 1.3M12.4 12.4l1.3 1.3M13.7 4.3l-1.3 1.3M5.6 12.4l-1.3 1.3',
  sos: 'M9 16a7 7 0 1 0 0-14 7 7 0 0 0 0 14ZM9 5.5V10M9 12.5h.01',
}

export function Icon({ name, size = 18, color = 'currentColor', sw = 1.5 }: { name: string; size?: number; color?: string; sw?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="none">
      <path d={PATHS[name] ?? ''} stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-2xl border border-[#E8ECF1] bg-white ${className}`}>{children}</div>
}

type Tone = 'red' | 'orange' | 'blue' | 'teal' | 'gray' | 'green'
const tones: Record<Tone, string> = {
  red: 'bg-[#FFEBEB] text-fam-red',
  orange: 'bg-[#FDF1E3] text-fam-orange',
  blue: 'bg-[#E9F1FF] text-fam-blue',
  teal: 'bg-[#E2F5F2] text-fam-deep',
  gray: 'bg-[#EFF1F4] text-[#8A93A0]',
  green: 'bg-[#E3F6E9] text-fam-green',
}

export function Chip({ tone = 'teal', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] ${tones[tone]}`}>{children}</span>
}

export function StatusBar() {
  return (
    <div className="flex h-[46px] shrink-0 items-center justify-between px-6 pt-2">
      <span className="text-[15px] font-medium text-[#1A2027]">9:41</span>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect x="2" y="8" width="16" height="8" rx="2" stroke="#1A2027" />
        <rect x="4" y="10" width="10" height="4" rx="1" fill="#1A2027" />
        <rect x="20" y="10.5" width="2" height="3" rx="1" fill="#1A2027" />
      </svg>
    </div>
  )
}

const TABS = [
  { key: 'home', label: '首页', icon: 'home' },
  { key: 'monitor', label: '监测', icon: 'wave' },
  { key: 'alerts', label: '预警', icon: 'bell' },
  { key: 'mine', label: '我的', icon: 'user' },
] as const

export function TabBar({ active, unread, onNav }: { active: string; unread: number; onNav: (k: 'home' | 'monitor' | 'alerts' | 'mine') => void }) {
  return (
    <div className="shrink-0 px-5 pb-4 pt-1">
      <div className="flex h-[62px] items-center rounded-full border border-[#E8ECF1] bg-white px-1.5">
        {TABS.map((t) => {
          const on = active === t.key
          return (
            <button
              key={t.key}
              onClick={() => onNav(t.key)}
              className={`relative flex flex-1 flex-col items-center justify-center gap-0.5 rounded-full py-2 ${on ? 'bg-fam-teal' : ''}`}
            >
              <Icon name={t.icon} size={18} color={on ? '#fff' : '#6B7280'} />
              <span className={`text-[10px] ${on ? 'text-white' : 'text-[#6B7280]'}`}>{t.label}</span>
              {t.key === 'alerts' && unread > 0 && (
                <span className="absolute right-4 top-1.5 h-2 w-2 rounded-full bg-fam-red" />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export function SubNav({ title, onBack, right }: { title: string; onBack: () => void; right?: ReactNode }) {
  return (
    <div className="flex h-[52px] shrink-0 items-center gap-3 bg-white px-4">
      <button onClick={onBack} className="flex h-7 w-7 items-center justify-center" aria-label="返回">
        <Icon name="chevL" size={18} color="#1A2027" sw={2} />
      </button>
      <span className="flex-1 text-[17px] text-black">{title}</span>
      {right}
    </div>
  )
}

export function Toggle({ on, onChange }: { on: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!on)}
      className={`flex h-6 w-11 shrink-0 items-center rounded-full px-0.5 transition-colors ${on ? 'bg-fam-teal justify-end' : 'bg-[#D6DCE3] justify-start'}`}
    >
      <span className="h-5 w-5 rounded-full bg-white shadow" />
    </button>
  )
}

export function Wave({ color = '#10B9A8' }: { color?: string }) {
  return (
    <svg viewBox="0 0 300 48" className="h-12 w-full" preserveAspectRatio="none">
      <path
        d="M0 24 Q 15 6 30 24 T 60 24 T 90 24 T 120 24 T 150 24 T 180 24 T 210 24 T 240 24 T 270 24 T 300 24"
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeLinecap="round"
      />
    </svg>
  )
}

export function AreaMini({ values, color }: { values: number[]; color: string }) {
  const W = 300
  const H = 96
  const pad = 8
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min || 1
  const step = (W - pad * 2) / (values.length - 1 || 1)
  const line = values
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${(pad + i * step).toFixed(1)} ${(H - pad - ((v - min) / span) * (H - pad * 2)).toFixed(1)}`)
    .join(' ')
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="h-24 w-full" preserveAspectRatio="none">
      <path d={`${line} L ${W - pad} ${H} L ${pad} ${H} Z`} fill={color} opacity={0.14} />
      <path d={line} fill="none" stroke={color} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function Toast({ text }: { text: string }) {
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-24 z-40 flex justify-center">
      <div className="rounded-full bg-[#1A2027]/90 px-4 py-2 text-xs text-white shadow-lg">{text}</div>
    </div>
  )
}

export function Modal({
  title,
  children,
  actions,
  onClose,
}: {
  title: string
  children: ReactNode
  actions: { label: string; danger?: boolean; primary?: boolean; onClick: () => void }[]
  onClose: () => void
}) {
  return (
    <div className="absolute inset-0 z-30 flex items-center justify-center bg-black/35 px-8" onClick={onClose}>
      <div className="w-full rounded-2xl bg-white p-5" onClick={(e) => e.stopPropagation()}>
        <div className="mb-3 text-base text-ink">{title}</div>
        <div className="mb-5 text-sm text-[#4B5563]">{children}</div>
        <div className="flex gap-2.5">
          {actions.map((a) => (
            <button
              key={a.label}
              onClick={a.onClick}
              className={`h-10 flex-1 rounded-xl text-sm ${
                a.danger ? 'bg-fam-red text-white' : a.primary ? 'bg-fam-teal text-white' : 'border border-[#E8ECF1] bg-white text-ink'
              }`}
            >
              {a.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

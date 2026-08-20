import type { ReactNode } from 'react'

// 基础组件：严格对应 Ardot 原型的卡片/标章/按钮样式

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl border border-line bg-white ${className}`}>{children}</div>
  )
}

type ChipTone = 'sage' | 'alert' | 'amber' | 'gray'

const chipTone: Record<ChipTone, string> = {
  sage: 'bg-sage-tint text-sage-deep',
  alert: 'bg-alert-tint text-alert',
  amber: 'bg-amber-tint text-amber',
  gray: 'bg-[#F0EDE3] text-ink-sub',
}

export function Chip({ tone = 'sage', children }: { tone?: ChipTone; children: ReactNode }) {
  return (
    <span className={`inline-flex items-center rounded-[10px] px-2.5 py-1 text-[11px] ${chipTone[tone]}`}>
      {children}
    </span>
  )
}

export function Btn({
  primary = false,
  danger = false,
  children,
  onClick,
  className = '',
}: {
  primary?: boolean
  danger?: boolean
  children: ReactNode
  onClick?: () => void
  className?: string
}) {
  const base = 'rounded-[10px] px-4 py-2.5 text-[13px] transition-colors'
  const style = danger
    ? 'bg-alert text-white hover:bg-[#a84c41]'
    : primary
      ? 'bg-sage text-white hover:bg-sage-deep'
      : 'border border-line bg-white text-ink hover:bg-cream'
  return (
    <button className={`${base} ${style} ${className}`} onClick={onClick}>
      {children}
    </button>
  )
}

export function PageTitle({ title, sub }: { title: string; sub: string }) {
  return (
    <div>
      <div className="text-xl text-ink">{title}</div>
      <div className="mt-1 text-xs text-ink-sub">{sub}</div>
    </div>
  )
}

export function CardHead({ title, extra }: { title: string; extra?: ReactNode }) {
  return (
    <div className="mb-2 flex items-center justify-between">
      <span className="text-base text-ink">{title}</span>
      {extra}
    </div>
  )
}

export function EmptyHint({ text }: { text: string }) {
  return <div className="py-10 text-center text-sm text-ink-hint">{text}</div>
}

import { useState } from 'react'
import { login, setToken } from '../api/client'

// 登录页：对应原型「1-登录」

export default function Login({ onSuccess }: { onSuccess: () => void }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleLogin() {
    setError('')
    setBusy(true)
    try {
      const res = await login(username, password)
      setToken(res.access_token)
      onSuccess()
    } catch {
      setError('登录失败：请确认后端已启动，且账号为 admin / admin123')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-cream">
      {/* 暖色装饰圆（对应原型） */}
      <div className="absolute -left-36 -top-40 h-[480px] w-[480px] rounded-full bg-sage-tint" />
      <div className="absolute -bottom-40 -right-24 h-[380px] w-[380px] rounded-full bg-apricot" />
      <div className="absolute -top-16 right-40 h-[220px] w-[220px] rounded-full bg-sage-tint" />

      <div className="relative z-10 flex w-[420px] flex-col items-center rounded-[20px] border border-line bg-white px-10 py-11">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-sage">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <path d="M3 15h5l3-7 5 13 3-6h6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="mt-5 text-[22px] text-ink">智能康养监测系统</div>
        <div className="mt-2 text-[13px] text-ink-sub">机构管理端 · 守护每一位长辈</div>

        <div className="mt-8 w-full space-y-3.5">
          <input
            className="h-12 w-full rounded-xl border border-line bg-white px-4 text-sm text-ink outline-none placeholder:text-ink-hint focus:border-sage"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="账号 / 工号"
          />
          <input
            className="h-12 w-full rounded-xl border border-line bg-white px-4 text-sm text-ink outline-none placeholder:text-ink-hint focus:border-sage"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            placeholder="密码"
          />
        </div>

        {error && <div className="mt-4 w-full rounded-lg bg-alert-tint px-3 py-2 text-sm text-alert">{error}</div>}

        <button
          className="mt-6 h-12 w-full rounded-xl bg-sage text-base text-white transition-colors hover:bg-sage-deep disabled:opacity-60"
          onClick={handleLogin}
          disabled={busy}
        >
          {busy ? '登录中…' : '登 录'}
        </button>
        <p className="mt-7 text-[11px] text-ink-hint">数据端侧处理 · 画面不上云 · 隐私优先</p>
      </div>
    </div>
  )
}

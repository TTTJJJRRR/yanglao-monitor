import { useEffect, useMemo, useState } from 'react'
import { login, setToken, getToken, getDataSource, setDataSource } from './api/client'
import { createWs } from './api/ws'
import type { AlertData, BehaviorAction, BehaviorData, RadarStatusData, PoseData, StreamMessage, VitalData } from './types'

const emotionMap = {
  happy: '愉快',
  sad: '悲伤',
  angry: '愤怒',
  anxious: '焦虑',
  calm: '平静',
  surprised: '惊讶',
} as const

const SOURCES = ['mock', 'mmfi', 'real'] as const
type SourceType = (typeof SOURCES)[number]
const sourceLabel: Record<SourceType, string> = {
  mock: 'Mock 模拟',
  mmfi: 'MMFi 样例',
  real: '真实雷达(占位)',
}

const behaviorMap: Record<BehaviorAction, string> = {
  walking: '行走',
  standing: '站立',
  sitting_still: '静坐',
  standing_up: '起身',
  crouching: '弯腰/蹲下',
  lying: '卧床',
  lying_floor: '倒地不起',
  falling: '跌倒',
  normal_activity: '正常活动',
}

type Theme = 'light' | 'dark'

export default function App() {
  const [online, setOnline] = useState(false)
  const [token, setTokenState] = useState(getToken() || '')
  const [vitals, setVitals] = useState<VitalData[]>([])
  const [behaviors, setBehaviors] = useState<BehaviorData[]>([])
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [radarStatus, setRadarStatus] = useState<RadarStatusData>({ action: null, confidence: 0, model_loaded: false })
  const [pose, setPose] = useState<PoseData>({ fall_score: 0, confidence: 0 })
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [dataSource, setDataSourceState] = useState<SourceType>('mock')
  const [loginError, setLoginError] = useState('')
  const [theme, setTheme] = useState<Theme>(
    () =>
      (localStorage.getItem('theme') as Theme) ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
  )

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    if (!token) return
    getDataSource()
      .then((d) => {
        if ((SOURCES as readonly string[]).includes(d.source)) setDataSourceState(d.source as SourceType)
      })
      .catch(() => {})
  }, [token])

  async function handleSwitchSource() {
    const next = SOURCES[(SOURCES.indexOf(dataSource) + 1) % SOURCES.length]
    try {
      const d = await setDataSource(next)
      if ((SOURCES as readonly string[]).includes(d.source)) setDataSourceState(d.source as SourceType)
    } catch {
      // 切换失败静默忽略，保持当前显示
    }
  }

  useEffect(() => {
    if (!token) return
    return createWs(
      token,
      (msg: StreamMessage) => {
        if (msg.type === 'vital') setVitals((prev) => [msg.data, ...prev].slice(0, 30))
        if (msg.type === 'behavior') setBehaviors((prev) => [msg.data, ...prev].slice(0, 10))
        if (msg.type === 'alert') setAlerts((prev) => [msg.data, ...prev].slice(0, 20))
        if (msg.type === 'radar_status') setRadarStatus(msg.data)
        if (msg.type === 'pose') setPose(msg.data)
      },
      setOnline,
      dataSource,
    )
  }, [token, dataSource])

  const lastVital = vitals[0]

  const chartData = useMemo(
    () =>
      vitals
        .slice()
        .reverse()
        .map((v) => ({ t: new Date(v.timestamp_ms).toLocaleTimeString(), breath: v.breath_rate, heart: v.heart_rate })),
    [vitals],
  )

  const latestBehaviorLabel = behaviors[0]?.action ? behaviorMap[behaviors[0].action] : '等待数据'

  async function handleLogin() {
    setLoginError('')
    try {
      const res = await login(username, password)
      setToken(res.access_token)
      setTokenState(res.access_token)
    } catch {
      setLoginError('登录失败：请确认后端已启动，且账号为 admin / admin123')
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 transition-colors dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto max-w-6xl p-4">
        <header className="mb-4 flex items-center justify-between rounded-2xl border border-slate-200 bg-white/80 px-6 py-4 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
          <h1 className="text-2xl font-bold tracking-wide text-sky-700 dark:text-sky-300">智能康养监测系统 · 实时大屏</h1>
          <div className="flex items-center gap-3 text-sm">
            <span className={`h-3 w-3 rounded-full ${online ? 'bg-emerald-500' : 'bg-rose-500'}`} />
            <span className="text-slate-500 dark:text-slate-400">{online ? 'WebSocket 已连接' : 'WebSocket 未连接'}</span>
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="rounded-lg border border-slate-300 bg-slate-100 px-3 py-1 text-slate-700 hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
            >
              {theme === 'dark' ? '切换浅色' : '切换深色'}
            </button>
            {token && (
              <button
                onClick={handleSwitchSource}
                className="rounded-lg border border-sky-300 bg-sky-50 px-3 py-1 text-sky-700 hover:bg-sky-100 dark:border-sky-700 dark:bg-slate-800 dark:text-sky-300"
                title="切换演示数据源：mock 模拟 / mmfi 朋友验证样例（生命体征为 null，仅验证管道）/ real 真实雷达占位（M1 接 mmVital，写库+广播有效帧）"
              >
                数据源: {sourceLabel[dataSource]}
              </button>
            )}
          </div>
        </header>

        {!token ? (
          <div className="mx-auto mt-24 max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-lg dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-4 text-lg font-semibold text-slate-800 dark:text-slate-100">登录</div>
            <input
              className="mb-3 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-800 outline-none focus:border-sky-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="用户名"
            />
            <input
              className="mb-4 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-800 outline-none focus:border-sky-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="密码"
            />
            {loginError && (
              <div className="mb-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-600 dark:bg-rose-900/40 dark:text-rose-300">
                {loginError}
              </div>
            )}
            <button
              className="w-full rounded-lg bg-sky-600 px-4 py-3 font-semibold text-white hover:bg-sky-700"
              onClick={handleLogin}
            >
              登录并进入大屏
            </button>
            <p className="mt-3 text-center text-xs text-slate-400">默认账号 admin / admin123</p>
          </div>
        ) : (
          <>
            <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/70">
              <div className="mb-3 text-sm font-semibold text-slate-600 dark:text-slate-300">活动识别（融合状态）</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-950">
                  <div className="text-xs text-slate-400">雷达行为</div>
                  <div className="mt-1 text-xl font-bold text-sky-700 dark:text-sky-300">
                    {radarStatus.action ? behaviorMap[radarStatus.action] : '等待雷达信号'}
                    {radarStatus.action && (
                      <span className="ml-2 text-xs font-normal text-slate-400">置信 {Math.round(radarStatus.confidence * 100)}%</span>
                    )}
                  </div>
                  <div className={`mt-1 text-xs ${radarStatus.model_loaded ? 'text-emerald-500' : 'text-slate-400'}`}>
                    {radarStatus.model_loaded ? '模型已接入（真实推理）' : '模型未接入（空挡接口）'}
                  </div>
                </div>
                <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-950">
                  <div className="text-xs text-slate-400">视觉跌倒分</div>
                  <div className="mt-1 text-xl font-bold text-rose-600 dark:text-rose-400">
                    {Math.round(pose.fall_score * 100)}%
                    {pose.fall_score > 0 && (
                      <span className="ml-2 text-xs font-normal text-slate-400">置信 {Math.round(pose.confidence * 100)}%</span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-slate-400">MediaPipe 关键点实时计算</div>
                </div>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
            <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/70">
              <Stat title="呼吸率" value={lastVital?.breath_rate ?? '--'} unit="次/分" />
              <Stat title="心率" value={lastVital?.heart_rate ?? '--'} unit="次/分" />
              <Chart data={chartData} />
            </section>
            <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/70">
              <div className="rounded-xl bg-slate-50 p-4 text-slate-700 dark:bg-slate-950 dark:text-slate-200">
                <span className={behaviors[0]?.action === 'falling' ? 'font-bold text-rose-600' : ''}>
                  最新行为: {latestBehaviorLabel}
                </span>{' '}
                {behaviors[0] && emotionMap[behaviors[0].emotion]}
              </div>
              <RadarCanvas vital={lastVital} />
            </section>
            <section className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/70">
              {alerts.length === 0 ? (
                <div className="text-slate-400">暂无报警</div>
              ) : (
                alerts.map((a) => (
                  <div
                    key={a.id}
                    className={`mb-3 rounded-lg p-3 text-slate-800 dark:text-slate-100 ${
                      a.level === 'red' ? 'bg-rose-100 dark:bg-rose-900/70' : 'bg-amber-100 dark:bg-amber-900/60'
                    }`}
                  >
                    {new Date(a.timestamp_ms).toLocaleTimeString()} · {a.type} · {a.message}
                  </div>
                ))
              )}
            </section>
          </div>
          </>
        )}
      </div>
    </div>
  )
}

function Stat({ title, value, unit }: { title: string; value: number | string; unit: string }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-950">
      <div className="text-slate-500 dark:text-slate-400">{title}</div>
      <div className="mt-2 text-3xl font-bold text-sky-700 dark:text-sky-300">
        {value}
        <span className="ml-2 text-sm text-slate-400">{unit}</span>
      </div>
    </div>
  )
}

function Chart({ data }: { data: any }) {
  return (
    <div className="h-64 rounded-xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-slate-950 dark:text-slate-400">
      折线图数据点: {data.length}
    </div>
  )
}

function RadarCanvas({ vital }: { vital?: VitalData }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4 text-slate-600 dark:bg-slate-950 dark:text-slate-300">
      雷达图示意: {vital ? `${vital.breath_rate ?? '--'}/${vital.heart_rate ?? '--'}` : '--'}
    </div>
  )
}

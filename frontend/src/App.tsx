import { useEffect, useMemo, useState } from 'react'
import { login, setToken, getToken, getDataSource, setDataSource } from './api/client'
import { createWs } from './api/ws'
import type { AlertData, BehaviorData, StreamMessage, VitalData } from './types'

const emotionMap = { happy: '😊', sad: '😢', angry: '😠', anxious: '😟', calm: '😌', surprised: '😲' } as const

const SOURCES = ['mock', 'mmfi', 'real'] as const
type SourceType = (typeof SOURCES)[number]

const sourceLabel: Record<SourceType, string> = {
  mock: 'Mock 模拟',
  mmfi: 'MMFi 样例',
  real: '真实雷达(占位)',
}

export default function App() {
  const [online, setOnline] = useState(false)
  const [token, setTokenState] = useState(getToken() || '')
  const [vitals, setVitals] = useState<VitalData[]>([])
  const [behaviors, setBehaviors] = useState<BehaviorData[]>([])
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [dataSource, setDataSourceState] = useState<SourceType>('mock')

  useEffect(() => {
    if (!token) return
    getDataSource().then((d) => {
      if ((SOURCES as readonly string[]).includes(d.source)) setDataSourceState(d.source as SourceType)
    }).catch(() => {})
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
    return createWs(token, (msg: StreamMessage) => {
      if (msg.type === 'vital') setVitals((prev) => [msg.data, ...prev].slice(0, 30))
      if (msg.type === 'behavior') setBehaviors((prev) => [msg.data, ...prev].slice(0, 10))
      if (msg.type === 'alert') setAlerts((prev) => [msg.data, ...prev].slice(0, 20))
    }, setOnline)
  }, [token])

  const lastVital = vitals[0]

  const chartData = useMemo(() => vitals.slice().reverse().map((v) => ({ t: new Date(v.timestamp_ms).toLocaleTimeString(), breath: v.breath_rate, heart: v.heart_rate })), [vitals])

  async function handleLogin() {
    const res = await login(username, password)
    setToken(res.access_token)
    setTokenState(res.access_token)
  }

  return (
    <div className="min-h-screen bg-slate-950 p-4 text-slate-100">
      <div className="mb-4 flex items-center justify-between rounded-2xl border border-cyan-400/20 bg-slate-900/80 px-6 py-4 shadow-lg shadow-cyan-950/30">
        <h1 className="text-2xl font-bold tracking-wide text-cyan-300">智能康养监测系统 · 实时大屏</h1>
        <div className="flex items-center gap-3 text-sm">
          <span className={`h-3 w-3 rounded-full ${online ? 'bg-emerald-400' : 'bg-rose-500'}`} />
          {online ? 'WebSocket 已连接' : 'WebSocket 未连接'}
          <button
            onClick={handleSwitchSource}
            className="rounded-lg border border-cyan-400/30 bg-slate-800 px-3 py-1 text-cyan-200 hover:bg-slate-700"
            title="切换演示数据源：mock 模拟数据 / mmfi 朋友提供的 MMFi 验证样例（生命体征为 null，仅验证管道）/ real 真实雷达占位（M1 接 mmVital，现在写库+广播有效帧）"
          >
            数据源: {sourceLabel[dataSource]}
          </button>
        </div>
      </div>

      {!token ? (
        <div className="mx-auto mt-24 max-w-md rounded-2xl border border-cyan-400/20 bg-slate-900 p-6 shadow-2xl">
          <div className="mb-4 text-lg font-semibold text-cyan-200">登录</div>
          <input className="mb-3 w-full rounded-lg bg-slate-800 px-4 py-3 outline-none" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input className="mb-4 w-full rounded-lg bg-slate-800 px-4 py-3 outline-none" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="w-full rounded-lg bg-cyan-500 px-4 py-3 font-semibold text-slate-950" onClick={handleLogin}>登录并进入大屏</button>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          <section className="space-y-4 rounded-2xl border border-cyan-400/20 bg-slate-900/70 p-4">
            <Stat title="呼吸率" value={lastVital?.breath_rate ?? '--'} unit="次/分" />
            <Stat title="心率" value={lastVital?.heart_rate ?? '--'} unit="次/分" />
            <Chart data={chartData} />
          </section>
          <section className="space-y-4 rounded-2xl border border-cyan-400/20 bg-slate-900/70 p-4">
            <div className="rounded-xl bg-slate-950 p-4">最新行为: {behaviors[0]?.action ?? '等待数据'} {behaviors[0] && emotionMap[behaviors[0].emotion]}</div>
            <RadarCanvas vital={lastVital} />
          </section>
          <section className="rounded-2xl border border-cyan-400/20 bg-slate-900/70 p-4">
            {alerts.map((a) => <div key={a.id} className={`mb-3 rounded-lg p-3 ${a.level === 'red' ? 'bg-rose-900/80' : 'bg-amber-900/70'}`}>{new Date(a.timestamp_ms).toLocaleTimeString()} · {a.type} · {a.message}</div>)}
          </section>
        </div>
      )}
    </div>
  )
}

function Stat({ title, value, unit }: any) { return <div className="rounded-xl bg-slate-950 p-4"><div className="text-slate-400">{title}</div><div className="mt-2 text-3xl font-bold text-cyan-300">{value}<span className="ml-2 text-sm text-slate-400">{unit}</span></div></div> }
function Chart({ data }: any) { return <div className="h-64 rounded-xl bg-slate-950 p-4 text-sm text-slate-400">折线图数据点: {data.length}</div> }
function RadarCanvas({ vital }: { vital?: VitalData }) { return <div className="rounded-xl bg-slate-950 p-4">雷达图示意: {vital ? `${vital.breath_rate ?? '--'}/${vital.heart_rate ?? '--'}` : '--'}</div> }

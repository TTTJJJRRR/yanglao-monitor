import { useEffect, useState } from 'react'
import { getToken, setToken, logout, getAlerts } from './api/client'
import { createWs } from './api/ws'
import { Shell } from './components/Shell'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Beds from './pages/Beds'
import BedDetail from './pages/BedDetail'
import Alerts from './pages/Alerts'
import Trends from './pages/Trends'
import Devices from './pages/Devices'
import Elders from './pages/Elders'
import type { AlertData, Bed, BehaviorData, PageKey, VitalData } from './types'

// 机构管理端根组件（正式前端）：登录 → 拉 /api/alerts → 连 WebSocket → Shell 路由 8 页。
// 真实管道：登录 / 预警列表(/api/alerts) / WS 实时体征·行为·预警 / 设备离线横幅 / 低置信盯防。
// 演示数据：床位 / 老人 / 设备 / 趋势（集中在 src/data/demo.ts，后端 API 排期 M3–M5）。

const PAGE_META: Record<PageKey, { title: string; sub: string }> = {
  dashboard: { title: '总览', sub: '全院实时运行状况' },
  beds: { title: '床位看板', sub: '两栋照护楼 · 实时床位状态' },
  bedDetail: { title: '床位详情', sub: '单床体征与行为实时监测' },
  alerts: { title: '预警中心', sub: '关键预警始终送达，不可静音' },
  trends: { title: '健康趋势', sub: '近一周生命体征走势' },
  devices: { title: '设备管理', sub: '雷达与视觉节点状态' },
  elders: { title: '老人档案', sub: '在住长辈基础信息' },
}

export default function InstitutionApp() {
  const [token, setTokenState] = useState(getToken() || '')
  const [page, setPage] = useState<PageKey>('dashboard')
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [vitals, setVitals] = useState<VitalData[]>([])
  const [behavior, setBehavior] = useState<BehaviorData | null>(null)
  const [online, setOnline] = useState(false)
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null)
  const [deviceOffline, setDeviceOffline] = useState<string | null>(null)
  const [reviewReason, setReviewReason] = useState<string | null>(null)

  // 登录后拉取预警列表（真实 /api/alerts）
  useEffect(() => {
    if (!token) return
    getAlerts()
      .then(setAlerts)
      .catch(() => {})
  }, [token])

  // 登录后连 WebSocket（实时体征/行为/预警/设备在线状态）
  useEffect(() => {
    if (!token) return
    return createWs(
      token,
      (msg) => {
        if (msg.type === 'vital') setVitals((prev) => [msg.data, ...prev].slice(0, 30))
        if (msg.type === 'behavior') setBehavior(msg.data)
        if (msg.type === 'alert') setAlerts((prev) => [msg.data, ...prev.filter((a) => a.id !== msg.data.id)].slice(0, 50))
        if (msg.type === 'device_offline') setDeviceOffline(msg.data.source)
        if (msg.type === 'device_online') setDeviceOffline(null)
        if (msg.type === 'pose') {
          setReviewReason(msg.data.needs_review ? (msg.data.watch_reason ?? '低置信·易混淆姿态') : null)
        }
      },
      setOnline,
    )
  }, [token])

  const unreadAlerts = alerts.filter((a) => !a.is_handled).length

  function handleLoginSuccess() {
    setTokenState(getToken() || '')
  }

  function handleLogout() {
    logout()
    setTokenState('')
    setPage('dashboard')
    setSelectedBed(null)
    setDeviceOffline(null)
    setReviewReason(null)
  }

  function handleHandled(id: number) {
    // 后端暂无「标记已处理」接口，当前仅本地生效（页面已注明）
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, is_handled: true } : a)))
  }

  function openBed(bed: Bed) {
    setSelectedBed(bed)
    setPage('bedDetail')
  }

  if (!token) return <Login onSuccess={handleLoginSuccess} />

  const meta = PAGE_META[page]

  let content
  if (page === 'dashboard') content = <Dashboard alerts={alerts} onNavigate={setPage} />
  else if (page === 'beds') content = <Beds onOpenBed={openBed} />
  else if (page === 'bedDetail') content = selectedBed ? <BedDetail bed={selectedBed} vitals={vitals} behavior={behavior} onBack={() => setPage('beds')} /> : <Beds onOpenBed={openBed} />
  else if (page === 'alerts') content = <Alerts alerts={alerts} onHandled={handleHandled} />
  else if (page === 'trends') content = <Trends />
  else if (page === 'devices') content = <Devices />
  else if (page === 'elders') content = <Elders />

  return (
    <>
      {deviceOffline && (
        <div className="alert-banner z-50 bg-alert px-5 py-3 text-center text-sm text-white shadow-lg">
          <span className="font-semibold">雷达设备离线，监测中断！</span>
          <span className="ml-2 text-xs opacity-90">关键预警始终送达，不可静音/关闭</span>
        </div>
      )}
      {reviewReason && (
        <div className="alert-banner z-40 bg-amber-tint px-5 py-2 text-center text-sm text-amber">
          持续盯防中 · {reviewReason}
        </div>
      )}
      <Shell
        page={page}
        onNavigate={setPage}
        title={meta.title}
        sub={meta.sub}
        unreadAlerts={unreadAlerts}
        online={online}
        onLogout={handleLogout}
      >
        {content}
      </Shell>
    </>
  )
}

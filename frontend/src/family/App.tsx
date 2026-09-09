import { useEffect, useState } from 'react'
import type { AlertItem, FamilyDevice, Message, PageKey, Role, Ward } from './types'
import { initialAlerts, initialDevices, initialMessages, initialWards, me } from './data'
import { Modal, StatusBar, TabBar, Toast } from './ui'
import Login from './pages/Login'
import Home from './pages/Home'
import Monitor from './pages/Monitor'
import { AlertDetailPage, AlertsPage } from './pages/Alerts'
import Trends from './pages/Trends'
import Daily from './pages/Daily'
import Mine from './pages/Mine'
import { AboutPage, DevicesPage, MessagesPage, PrivacyPage, WardsPage } from './pages/MineSubs'

// 家属小程序 App：390×844 手机壳 + 全页面路由 + 交互状态
// 本阶段全部本地演示数据，无任何后端调用；交互验收通过后再接 /api。

type ModalKind = 'sos' | 'call' | 'logout' | 'addWard' | 'bindDevice'

const TAB_PAGES: PageKey[] = ['home', 'monitor', 'alerts', 'mine']

export default function App() {
  const [page, setPage] = useState<PageKey>('login')
  const [role, setRole] = useState<Role>('家属')
  const [alerts, setAlerts] = useState<AlertItem[]>(initialAlerts)
  const [selectedId, setSelectedId] = useState<number>(1)
  const [wards, setWards] = useState<Ward[]>(initialWards)
  const [devices, setDevices] = useState<FamilyDevice[]>(initialDevices)
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [boneOn, setBoneOn] = useState(true)
  const [toast, setToast] = useState<string | null>(null)
  const [modal, setModal] = useState<ModalKind | null>(null)
  const [wardName, setWardName] = useState('')
  const [wardRelation, setWardRelation] = useState('')
  const [deviceCode, setDeviceCode] = useState('')

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 1800)
    return () => clearTimeout(t)
  }, [toast])

  const nav = (p: PageKey) => setPage(p)
  const unreadAlerts = alerts.filter((a) => a.status === '未处理').length
  const unreadMessages = messages.filter((m) => m.unread).length
  const selected = alerts.find((a) => a.id === selectedId) ?? alerts[0]

  const openAlert = (a: AlertItem) => {
    setSelectedId(a.id)
    setPage('alertDetail')
  }

  const markHandled = () => {
    setAlerts((prev) => prev.map((a) => (a.id === selected.id ? { ...a, status: '已处理' as const } : a)))
    setToast('已标记为已处理（演示）')
  }

  const confirmAddWard = () => {
    if (!wardName.trim()) return setToast('请填写姓名')
    setWards((prev) => [...prev, { name: wardName.trim(), relation: wardRelation.trim() || '家人', age: 70, tags: '待完善' }])
    setWardName('')
    setWardRelation('')
    setModal(null)
    setToast('已添加被监护人（演示）')
  }

  const confirmBindDevice = () => {
    if (!deviceCode.trim()) return setToast('请填写设备号')
    setDevices((prev) => [...prev, { name: `毫米波雷达-${deviceCode.trim()}`, place: '待配置房间', online: true }])
    setDeviceCode('')
    setModal(null)
    setToast('绑定成功（演示）')
  }

  const modalNode = (() => {
    switch (modal) {
      case 'sos':
        return (
          <Modal
            title="SOS 紧急呼叫"
            onClose={() => setModal(null)}
            actions={[
              { label: '取消', onClick: () => setModal(null) },
              { label: '立即呼叫', danger: true, onClick: () => { setModal(null); setToast('已发起紧急呼叫并通知紧急联系人（演示）') } },
            ]}
          >
            将为{me.role.includes('父亲') ? '父亲' : '被监护人'}发起紧急呼叫，并同步通知紧急联系人（微信 + 短信 + 电话）。请确认当前情况紧急。
          </Modal>
        )
      case 'call':
        return (
          <Modal
            title="拨打紧急电话"
            onClose={() => setModal(null)}
            actions={[
              { label: '取消', onClick: () => setModal(null) },
              { label: '立即拨打', danger: true, onClick: () => { setModal(null); setToast('正在呼叫 138****6621（演示）') } },
            ]}
          >
            紧急联系人：陈志远（子）138****6621。同时已为您保留预警现场记录。
          </Modal>
        )
      case 'logout':
        return (
          <Modal
            title="退出登录"
            onClose={() => setModal(null)}
            actions={[
              { label: '取消', onClick: () => setModal(null) },
              { label: '退出', danger: true, onClick: () => { setModal(null); setPage('login'); setToast('已退出（演示）') } },
            ]}
          >
            退出后仍可收到关键预警推送（生命安全预警始终送达）。确定退出当前账号吗？
          </Modal>
        )
      case 'addWard':
        return (
          <Modal
            title="添加被监护人"
            onClose={() => setModal(null)}
            actions={[
              { label: '取消', onClick: () => setModal(null) },
              { label: '确认添加', primary: true, onClick: confirmAddWard },
            ]}
          >
            <div className="space-y-2.5">
              <input
                className="h-10 w-full rounded-lg border border-[#E8ECF1] px-3 text-sm outline-none focus:border-fam-teal"
                placeholder="姓名，如：张建国"
                value={wardName}
                onChange={(e) => setWardName(e.target.value)}
              />
              <input
                className="h-10 w-full rounded-lg border border-[#E8ECF1] px-3 text-sm outline-none focus:border-fam-teal"
                placeholder="关系，如：父亲"
                value={wardRelation}
                onChange={(e) => setWardRelation(e.target.value)}
              />
            </div>
          </Modal>
        )
      case 'bindDevice':
        return (
          <Modal
            title="绑定新设备"
            onClose={() => setModal(null)}
            actions={[
              { label: '取消', onClick: () => setModal(null) },
              { label: '确认绑定', primary: true, onClick: confirmBindDevice },
            ]}
          >
            <input
              className="h-10 w-full rounded-lg border border-[#E8ECF1] px-3 text-sm outline-none focus:border-fam-teal"
              placeholder="输入设备号，如：RDR-3F-021"
              value={deviceCode}
              onChange={(e) => setDeviceCode(e.target.value)}
            />
          </Modal>
        )
      default:
        return null
    }
  })()

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#E9E5DC] py-6">
      {/* 手机壳 390×844（对应原型手机框） */}
      <div className="relative flex h-[844px] w-[390px] flex-col overflow-hidden rounded-[40px] border border-[#E8ECF1] bg-white shadow-2xl">
        <StatusBar />

        {page === 'login' && (
          <Login
            role={role}
            onRole={setRole}
            onLogin={() => {
              setPage('home')
              setToast(`以「${role}」身份登录成功（演示）`)
            }}
          />
        )}
        {page === 'home' && <Home unread={unreadAlerts} onNav={nav} />}
        {page === 'monitor' && <Monitor />}
        {page === 'alerts' && <AlertsPage alerts={alerts} onSos={() => setModal('sos')} onOpen={openAlert} />}
        {page === 'alertDetail' && (
          <AlertDetailPage alert={selected} onBack={() => setPage('alerts')} onCall={() => setModal('call')} onHandled={markHandled} />
        )}
        {page === 'trends' && <Trends onBack={() => setPage('home')} onExport={() => setToast('随访报告已生成（演示）')} />}
        {page === 'daily' && <Daily onBack={() => setPage('home')} onShare={() => setToast('分享卡片已生成（演示）')} />}
        {page === 'mine' && <Mine unreadMessages={unreadMessages} onNav={nav} onLogout={() => setModal('logout')} />}
        {page === 'wards' && <WardsPage wards={wards} onBack={() => setPage('mine')} onAdd={() => setModal('addWard')} />}
        {page === 'devices' && <DevicesPage devices={devices} onBack={() => setPage('mine')} onBind={() => setModal('bindDevice')} />}
        {page === 'messages' && (
          <MessagesPage
            messages={messages}
            onBack={() => setPage('mine')}
            onRead={(id) => setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, unread: false } : m)))}
          />
        )}
        {page === 'privacy' && (
          <PrivacyPage
            boneOn={boneOn}
            onToggleBone={(v) => {
              setBoneOn(v)
              setToast(v ? '已开启端侧骨骼化（演示）' : '已关闭端侧骨骼化（演示）')
            }}
            onExport={() => setToast('导出申请已提交（演示）')}
            onPolicy={() => setToast('隐私政策（演示页）')}
            onBack={() => setPage('mine')}
          />
        )}
        {page === 'about' && <AboutPage onBack={() => setPage('mine')} onContact={(w) => setToast(`${w}（演示）`)} />}

        {TAB_PAGES.includes(page) && <TabBar active={page} unread={unreadAlerts} onNav={nav} />}

        {modalNode}
        {toast && <Toast text={toast} />}
      </div>
    </div>
  )
}

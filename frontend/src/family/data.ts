import type { AlertItem, FamilyDevice, Message, Ward } from './types'

// ============================================================
// 演示数据（静态）：家属小程序全部内容均为本地演示数据
// 交互验收通过后，按 src/api/client.ts 的同构方式接真实后端。
// ============================================================

export const elder = {
  name: '张建国',
  relation: '父亲',
  age: 78,
  room: '卧室',
  status: '静卧',
  mood: '平静',
  updated: '刚刚',
}

export const me = { name: '陈志远', role: '家属 · 已绑定父亲' }

export const vitals = { breath: 16, heart: 72 }

export const quickStats = [
  { label: '今日预警', value: '1 条', hot: true },
  { label: '夜间睡眠', value: '7.2 h', hot: false },
  { label: '今日活动', value: '3.2 h', hot: false },
]

export const initialAlerts: AlertItem[] = [
  { id: 1, level: 'red', title: '疑似跌倒', place: '卧室', time: '今天 14:32', status: '未处理' },
  { id: 2, level: 'orange', title: '心率短时升高', place: '活动室', time: '今天 11:05', status: '已跟进' },
  { id: 3, level: 'blue', title: '情绪焦虑提示', place: '心率 > 基线 1.3 倍', time: '昨天 21:40', status: '已处理' },
]

export const alertTimeline = [
  { text: '雷达检测到异常倒地姿态', time: '14:32:05' },
  { text: '视觉骨骼化二次确认（端侧，不上云）', time: '14:32:08' },
  { text: '已通知家属（微信 + 短信）', time: '14:32:10' },
  { text: '护工前往现场跟进', time: '14:33:01' },
]

export const breathWeek = [15.2, 15.8, 15.5, 16.4, 15.9, 16.8, 15.8]
export const heartWeek = [70, 72, 69, 74, 71, 76, 71]

export function monthify(week: number[]) {
  const out: number[] = []
  for (let i = 0; i < 30; i++) {
    const jitter = ((i * 37) % 11) / 10 - 0.5
    out.push(Math.round((week[i % 7] + jitter) * 10) / 10)
  }
  return out
}

export const activityMeters = [
  { label: '日均活动时长', value: '3.2 小时', ratio: 0.64 },
  { label: '日均步数', value: '约 3200 步', ratio: 0.48 },
  { label: '夜间睡眠', value: '7.1 小时 · 质量良好', ratio: 0.76 },
]

export const dailyCards = [
  { title: '体征平稳', desc: '呼吸 15.8 · 心率 71，均在正常范围', icon: 'heart' },
  { title: '活动正常', desc: '活动 3.2 小时 · 散步 2 次', icon: 'walk' },
  { title: '睡眠良好', desc: '夜间睡眠 7.2 小时 · 起夜 1 次', icon: 'moon' },
  { title: '无异常事件', desc: '昨日全天无跌倒与异常预警', icon: 'check' },
]

export const initialWards: Ward[] = [
  { name: '张建国', relation: '父亲', age: 78, tags: '高血压 · 糖尿病' },
  { name: '李秀兰', relation: '母亲', age: 75, tags: '冠心病' },
]

export const initialDevices: FamilyDevice[] = [
  { name: '卧室毫米波雷达', place: '主卧', online: true },
  { name: '客厅视觉节点', place: '客厅 · 端侧骨骼化', online: true },
]

export const initialMessages: Message[] = [
  { id: 1, title: '跌倒预警', desc: '疑似跌倒 · 卧室 · 请及时查看', time: '14:32', unread: true },
  { id: 2, title: '安心日报已生成', desc: '父亲昨日一切安好，点击查看', time: '08:00', unread: true },
  { id: 3, title: '设备提醒', desc: '客厅视觉节点固件已自动更新', time: '昨天', unread: false },
]

export const faqs = [
  { q: '毫米波雷达有辐射吗？安全吗？', a: '毫米波雷达功率仅为手机的几十分之一，非接触、无感监测，长期使用安全。' },
  { q: '视频画面会上传到云端吗？', a: '不会。视觉节点在设备端完成骨骼化提取，只上传骨骼点坐标，原始画面不出设备。' },
  { q: '误报了怎么办？', a: '可在预警中心将该条标记为「已处理 · 误报」，系统会据此优化后续判断。关键预警仍会始终送达。' },
]

import type { Bed, DeviceRow, Elder, TrendPoint } from '../types'

// ============================================================
// 演示数据（静态）：床位 / 老人 / 设备 / 趋势
// 后端尚无这些实体的 API（R-P1-03 多床位看板排期 M3–M5），
// 这里按 Ardot 原型 1:1 填充，后续接口就位后整体替换为本文件同构数据。
// 实时体征 / 预警走 WebSocket 与 /api/alerts（真实管道，见各页面）。
// ============================================================

export const demoBeds: Bed[] = [
  { id: '3', elder: '张建国', floor: '2F', status: 'alert', note: '疑似跌倒 · 需立即跟进', updateTime: '14:32' },
  { id: '5', elder: '王有福', floor: '2F', status: 'normal', note: '呼吸 15 · 心率 70 · 当前：阅读', updateTime: '14:30' },
  { id: '7', elder: '李秀兰', floor: '2F', status: 'normal', note: '呼吸 17 · 心率 76 · 当前：散步', updateTime: '14:31' },
  { id: '8', elder: '赵桂芳', floor: '2F', status: 'normal', note: '呼吸 14 · 心率 68 · 当前：午休', updateTime: '14:31' },
  { id: '9', elder: '刘长顺', floor: '2F', status: 'normal', note: '呼吸 16 · 心率 74 · 当前：看电视', updateTime: '14:30' },
  { id: '12', elder: '孙玉兰', floor: '3F', status: 'offline', note: '设备离线 · 已派单检修', updateTime: '最后在线 09:12' },
  { id: '15', elder: '周德海', floor: '3F', status: 'normal', note: '呼吸 15 · 心率 71 · 当前：下棋', updateTime: '14:29' },
  { id: '16', elder: '吴桂英', floor: '3F', status: 'normal', note: '呼吸 16 · 心率 73 · 当前：浇花', updateTime: '14:31' },
  { id: '18', elder: '郑建国', floor: '3F', status: 'normal', note: '呼吸 14 · 心率 69 · 当前：午休', updateTime: '14:30' },
]

export const demoElders: Elder[] = [
  { name: '张建国', age: 78, gender: '男', bed: '3 床 · 2F', tags: '高血压 · 糖尿病', contact: '陈志远（子）138****6621', status: '在住' },
  { name: '李秀兰', age: 75, gender: '女', bed: '7 床 · 2F', tags: '冠心病', contact: '李文静（女）139****8830', status: '在住' },
  { name: '王有福', age: 82, gender: '男', bed: '5 床 · 3F', tags: '轻度认知障碍', contact: '王强（子）137****2245', status: '在住' },
  { name: '孙玉兰', age: 79, gender: '女', bed: '12 床 · 3F', tags: '关节炎', contact: '孙丽（女）136****9012', status: '在住' },
]

export const demoDevices: DeviceRow[] = [
  { name: '卧室雷达-3床', kind: '毫米波雷达', location: '2F · 3 床卧室', online: true, heartbeat: '14:32:10' },
  { name: '卧室雷达-5床', kind: '毫米波雷达', location: '2F · 5 床卧室', online: true, heartbeat: '14:32:08' },
  { name: '客厅视觉节点-2F', kind: '视觉节点 · 端侧骨骼化', location: '2F · 公共客厅', online: true, heartbeat: '14:32:11' },
  { name: '卧室雷达-12床', kind: '毫米波雷达', location: '3F · 12 床卧室', online: false, heartbeat: '最后在线 09:12' },
]

export const breathTrend: TrendPoint[] = [
  { day: '一', value: 15.2 }, { day: '二', value: 15.8 }, { day: '三', value: 15.5 },
  { day: '四', value: 16.4 }, { day: '五', value: 15.9 }, { day: '六', value: 16.8 }, { day: '日', value: 15.8 },
]

export const heartTrend: TrendPoint[] = [
  { day: '一', value: 70 }, { day: '二', value: 72 }, { day: '三', value: 69 },
  { day: '四', value: 74 }, { day: '五', value: 71 }, { day: '六', value: 76 }, { day: '日', value: 71 },
]

export const weekAlertBars = [
  { day: '一', value: 2 }, { day: '二', value: 3 }, { day: '三', value: 1 },
  { day: '四', value: 4 }, { day: '五', value: 2 }, { day: '六', value: 5 }, { day: '日', value: 3 },
]

export const behaviorTimeline = [
  { time: '07:30', text: '起床 · 夜间睡眠 7.2 小时 · 质量良好', hot: false },
  { time: '08:00', text: '早餐 · 餐厅 · 进食正常', hot: false },
  { time: '12:00', text: '午休 · 时长 1.5 小时', hot: false },
  { time: '14:32', text: '疑似跌倒 · 已通知家属并跟进', hot: true },
]

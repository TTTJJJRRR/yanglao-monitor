// 家属小程序：页面路由与共享数据类型（本阶段全部演示数据，后端链接留待交互验收后）

export type PageKey =
  | 'login'
  | 'home'
  | 'monitor'
  | 'alerts'
  | 'alertDetail'
  | 'trends'
  | 'daily'
  | 'mine'
  | 'wards'
  | 'devices'
  | 'messages'
  | 'privacy'
  | 'about'

export type Role = '家属' | '管理员' | '老人'

export type AlertLevel = 'red' | 'orange' | 'blue'

export type AlertItem = {
  id: number
  level: AlertLevel
  title: string
  place: string
  time: string
  status: '未处理' | '已跟进' | '已处理'
}

export type Ward = {
  name: string
  relation: string
  age: number
  tags: string
}

export type FamilyDevice = {
  name: string
  place: string
  online: boolean
}

export type Message = {
  id: number
  title: string
  desc: string
  time: string
  unread: boolean
}

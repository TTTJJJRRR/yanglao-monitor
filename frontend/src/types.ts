export type PageKey = 'dashboard' | 'beds' | 'bedDetail' | 'alerts' | 'trends' | 'devices' | 'elders'

export type BedStatus = 'normal' | 'alert' | 'offline'

export type Bed = {
  id: string
  elder: string
  floor: '2F' | '3F'
  status: BedStatus
  note: string
  updateTime: string
}

export type DeviceRow = {
  name: string
  kind: string
  location: string
  online: boolean
  heartbeat: string
}

export type Elder = {
  name: string
  age: number
  gender: '男' | '女'
  bed: string
  tags: string
  contact: string
  status: string
}

export type TrendPoint = { day: string; value: number }

export type VitalData = {
  id?: number
  timestamp_ms: number
  device_id: string
  breath_rate: number | null
  heart_rate: number | null
  chest_displacement_mm: number | null
  motion_flag: boolean
  ahi_index: number | null
  source?: 'mock' | 'real' | 'mmfi' | 'replay'
}

export type BehaviorAction = 'walking' | 'standing' | 'sitting_still' | 'standing_up' | 'crouching' | 'lying' | 'lying_floor' | 'falling' | 'normal_activity'

export type BehaviorData = {
  id?: number
  timestamp_ms: number
  action: BehaviorAction
  emotion: 'happy' | 'sad' | 'angry' | 'anxious' | 'calm' | 'surprised'
  confidence: number
  source?: 'mock' | 'real' | 'mmfi' | 'replay'
}

export type AlertData = {
  id: number
  timestamp_ms: number
  level: 'red' | 'yellow' | 'critical'
  type: string
  message: string
  is_handled: boolean
}

export type RadarStatusData = {
  action: BehaviorAction | null
  confidence: number
  model_loaded: boolean
}

export type PoseData = {
  fall_score: number
  confidence: number
  is_fall?: boolean
  alert_level?: 'red' | 'yellow' | null
  watch?: boolean
  needs_review?: boolean
  watch_reason?: string | null
}

export type StreamMessage =
  | { type: 'vital'; data: VitalData }
  | { type: 'behavior'; data: BehaviorData }
  | { type: 'alert'; data: AlertData }
  | { type: 'radar_status'; data: RadarStatusData }
  | { type: 'pose'; data: PoseData }
  | { type: 'device_offline'; data: { source: string; timestamp_ms: number; last_seen_ms: number; level: 'critical' } }
  | { type: 'device_online'; data: { source: string; timestamp_ms: number; last_seen_ms: number; level: 'yellow' } }

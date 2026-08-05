export type VitalData = {
  id?: number
  timestamp_ms: number
  device_id: string
  breath_rate: number | null
  heart_rate: number | null
  chest_displacement_mm: number | null
  motion_flag: boolean
  ahi_index: number | null
  source?: 'mock' | 'real' | 'mmfi'
}

export type BehaviorAction = 'walking' | 'falling' | 'sitting_still' | 'standing_up' | 'lying' | 'normal_activity'

export type BehaviorData = {
  id?: number
  timestamp_ms: number
  action: BehaviorAction
  emotion: 'happy' | 'sad' | 'angry' | 'anxious' | 'calm' | 'surprised'
  confidence: number
  source?: 'mock' | 'real' | 'mmfi'
}

export type AlertData = {
  id: number
  timestamp_ms: number
  level: 'red' | 'yellow'
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
}

export type StreamMessage =
  | { type: 'vital'; data: VitalData }
  | { type: 'behavior'; data: BehaviorData }
  | { type: 'alert'; data: AlertData }
  | { type: 'radar_status'; data: RadarStatusData }
  | { type: 'pose'; data: PoseData }

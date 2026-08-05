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

export type BehaviorData = {
  id?: number
  timestamp_ms: number
  action: 'walking' | 'sitting' | 'lying' | 'crouching' | 'falling' | 'still'
  emotion: 'happy' | 'sad' | 'angry' | 'anxious' | 'calm' | 'surprised'
  confidence: number
  source?: 'mock' | 'real'
}

export type AlertData = {
  id: number
  timestamp_ms: number
  level: 'red' | 'yellow'
  type: string
  message: string
  is_handled: boolean
}

export type StreamMessage =
  | { type: 'vital'; data: VitalData }
  | { type: 'behavior'; data: BehaviorData }
  | { type: 'alert'; data: AlertData }

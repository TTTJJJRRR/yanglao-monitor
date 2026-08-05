import type { StreamMessage } from '../types'

export function createWs(token: string, onMessage: (msg: StreamMessage) => void, onStatus: (online: boolean) => void) {
  let ws: WebSocket | null = null
  let closed = false

  const connect = () => {
    ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws?token=${token}`)
    ws.onopen = () => onStatus(true)
    ws.onclose = () => {
      onStatus(false)
      if (!closed) setTimeout(connect, 3000)
    }
    ws.onmessage = (event) => onMessage(JSON.parse(event.data))
  }

  connect()

  return () => {
    closed = true
    ws?.close()
  }
}

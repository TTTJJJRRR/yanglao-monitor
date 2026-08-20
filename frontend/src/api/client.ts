const API_BASE = (import.meta.env.VITE_API_BASE as string) || '/api'

import type { AlertData } from '../types'

export function getToken() {
  return localStorage.getItem('access_token')
}

export function setToken(token: string) {
  localStorage.setItem('access_token', token)
}

export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error('登录失败')
  return res.json() as Promise<{ access_token: string; token_type: string; role: string }>
}

function authHeaders() {
  return { Authorization: `Bearer ${getToken() || ''}` }
}

export async function getAlerts(limit = 50) {
  const res = await fetch(`${API_BASE}/alerts?limit=${limit}`, { headers: authHeaders() })
  if (!res.ok) throw new Error('获取预警列表失败')
  return res.json() as Promise<AlertData[]>
}

export async function logout() {
  localStorage.removeItem('access_token')
}

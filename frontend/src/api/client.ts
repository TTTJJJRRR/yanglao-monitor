const API_BASE = 'http://localhost:8000/api'

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

export async function getDataSource() {
  const res = await fetch(`${API_BASE}/data-source`)
  if (!res.ok) throw new Error('获取数据源失败')
  return res.json() as Promise<{ source: string; options: string[] }>
}

export async function setDataSource(source: string) {
  const res = await fetch(`${API_BASE}/data-source`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  })
  if (!res.ok) throw new Error('切换数据源失败')
  return res.json() as Promise<{ source: string; options: string[] }>
}

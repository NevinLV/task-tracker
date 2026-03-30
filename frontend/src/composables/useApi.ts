import { useAuth } from './useAuth'

export function useApi() {
  const { token } = useAuth()

  async function request<T>(
    path: string,
    init: RequestInit = {},
  ): Promise<T> {
    const headers = new Headers(init.headers)
    if (token.value) headers.set('Authorization', `Bearer ${token.value}`)
    if (init.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }
    const res = await fetch(path, { ...init, headers })
    if (res.status === 204) return undefined as T
    const text = await res.text()
    if (!res.ok) {
      let detail = res.statusText
      try {
        const j = JSON.parse(text) as { detail?: string | string[] }
        if (typeof j.detail === 'string') detail = j.detail
        else if (Array.isArray(j.detail)) detail = j.detail.map(String).join(', ')
      } catch {
        /* ignore */
      }
      throw new Error(detail)
    }
    if (!text) return undefined as T
    return JSON.parse(text) as T
  }

  return { request }
}

import { computed, ref } from 'vue'

import type { UserProfile } from '@/types/api'

const TOKEN_KEY = 'tasktracker_token'

const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
const user = ref<UserProfile | null>(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)

  function setToken(t: string | null) {
    token.value = t
    if (t) localStorage.setItem(TOKEN_KEY, t)
    else localStorage.removeItem(TOKEN_KEY)
  }

  async function loadMe() {
    if (!token.value) {
      user.value = null
      return
    }
    const res = await fetch('https://task-tracker-5nzw.onrender.com/api/auth/me', {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    if (!res.ok) {
      setToken(null)
      user.value = null
      return
    }
    const data = (await res.json()) as UserProfile
    user.value = {
      ...data,
      first_name: data.first_name ?? null,
      last_name: data.last_name ?? null,
      hourly_rate: String(data.hourly_rate ?? '0'),
    }
  }

  function logout() {
    setToken(null)
    user.value = null
  }

  return {
    token,
    user,
    isAuthenticated,
    setToken,
    loadMe,
    logout,
  }
}

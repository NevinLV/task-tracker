import type { UserProfile } from '@/types/api'

type NameFields = Pick<UserProfile, 'email' | 'first_name' | 'last_name'>

export function userDisplayName(u: NameFields | null): string {
  if (!u) return ''
  const p = [u.first_name?.trim(), u.last_name?.trim()].filter(Boolean).join(' ')
  return p || u.email
}

export function userInitials(u: NameFields | null): string {
  if (!u) return '?'
  const fn = u.first_name?.trim()
  const ln = u.last_name?.trim()
  if (fn && ln) return (fn[0]! + ln[0]!).toUpperCase()
  if (fn) return fn.slice(0, 2).toUpperCase()
  if (ln) return ln.slice(0, 2).toUpperCase()
  return u.email.slice(0, 2).toUpperCase()
}

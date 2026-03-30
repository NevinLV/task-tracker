import type { TaskStatus } from '@/types/api'

/** Подписи + иконки Lucide для статусов */
export const TASK_STATUS_OPTIONS: { value: TaskStatus; label: string; icon: string }[] = [
  { value: 'familiarization', label: 'Ознакомление', icon: 'i-lucide-book-open' },
  { value: 'development', label: 'Разработка', icon: 'i-lucide-code-2' },
  { value: 'testing', label: 'Тестирование', icon: 'i-lucide-flask-conical' },
  { value: 'deployment', label: 'Развёртывание', icon: 'i-lucide-rocket' },
  { value: 'done', label: 'Готово', icon: 'i-lucide-circle-check' },
]

export function statusLabel(status: TaskStatus): string {
  return TASK_STATUS_OPTIONS.find((o) => o.value === status)?.label ?? status
}

export function statusIcon(status: TaskStatus): string {
  return TASK_STATUS_OPTIONS.find((o) => o.value === status)?.icon ?? 'i-lucide-circle-dashed'
}

/** Цвета из гайда: Pine, Forest, Frog, Mint, Caribbean */
export const STATUS_BADGE_CLASS: Record<TaskStatus, string> = {
  familiarization: 'bg-[#063E13] text-white',
  development: 'bg-[#095544] text-[#F1F1F6]',
  testing: 'bg-[#17876D] text-white',
  deployment: 'bg-[#2F958C] text-[#022221]',
  done: 'bg-[#00E891] text-[#022221] font-semibold',
}

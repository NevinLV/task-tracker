<template>
  <div>
    <AppHeader title="Задачи" :subtitle="userSubtitle" icon="i-lucide-layout-list" />
    <UContainer class="py-8">
      <div class="mb-6 flex flex-wrap items-end gap-3">
        <UFormField label="С даты">
          <UInput v-model="filterFrom" type="date" class="w-40" />
        </UFormField>
        <UFormField label="По дату">
          <UInput v-model="filterTo" type="date" class="w-40" />
        </UFormField>
        <UFormField label="Статус">
          <USelect
            v-model="filterStatus"
            :items="filterStatusItems"
            placeholder="Не выбран"
            value-key="value"
            label-key="label"
            class="min-w-[12rem]"
          />
        </UFormField>
        <UButton color="primary" variant="soft" @click="applyFilters">Применить</UButton>
        <UButton color="neutral" variant="ghost" @click="clearFilters">Сбросить</UButton>
      </div>
      <div v-if="loading" class="flex items-center gap-2 text-muted">
        <UIcon name="i-lucide-loader-2" class="size-5 animate-spin" />
        <span>Загрузка…</span>
      </div>
      <UAlert v-else-if="err" color="error" variant="soft" :title="err" />
      <div v-else-if="!tasks.length" class="flex flex-col items-center gap-3 py-12 text-center text-muted">
        <UIcon name="i-lucide-inbox" class="size-12 opacity-50" />
        <p>Пока нет задач. Нажмите «+», чтобы создать.</p>
      </div>
      <ul v-else class="space-y-3">
        <li v-for="t in tasks" :key="t.id">
          <UCard class="border-default/80 p-4 transition-shadow hover:shadow-md sm:p-5">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0 flex-1">
                <RouterLink
                  :to="{ name: 'task-edit', params: { id: t.id } }"
                  class="font-medium text-highlighted transition-colors hover:text-primary"
                >
                  {{ t.title }}
                </RouterLink>
                <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
                  <span class="inline-flex items-center gap-1" title="Учтённое время">
                    <UIcon name="i-lucide-clock" class="size-4 text-toned" />
                    {{ formatDuration(liveDurationSeconds(t)) }}
                  </span>
                  <span
                    v-if="t.active_timer_entry_id"
                    class="inline-flex items-center gap-1 text-primary"
                    title="Таймер активен"
                  >
                    <UIcon name="i-lucide-timer" class="size-4" />
                  </span>
                </div>
              </div>
              <div class="flex w-full flex-col gap-2 sm:w-auto sm:min-w-[13rem] sm:items-stretch">
                <USelect
                  :model-value="t.status"
                  :items="rowStatusItems"
                  value-key="value"
                  label-key="label"
                  @update:model-value="(v) => patchStatus(t, v as TaskStatus)"
                />
                <div class="flex flex-wrap items-center justify-end gap-2">
                  <UButton
                    v-if="!t.active_timer_entry_id"
                    color="primary"
                    size="sm"
                    icon="i-lucide-play"
                    @click="toggleTimer(t)"
                  >
                    Старт
                  </UButton>
                  <UButton
                    v-else
                    color="error"
                    variant="soft"
                    size="sm"
                    icon="i-lucide-square"
                    @click="toggleTimer(t)"
                  >
                    Стоп
                  </UButton>
                </div>
              </div>
            </div>
          </UCard>
        </li>
      </ul>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import { TASK_STATUS_OPTIONS } from '@/lib/statuses'
import { userDisplayName } from '@/lib/userDisplay'
import type { Task, TaskStatus } from '@/types/api'

const { request } = useApi()
const { user, loadMe } = useAuth()

const tasks = ref<Task[]>([])
const loading = ref(true)
const err = ref('')

const filterFrom = ref('')
const filterTo = ref('')
const filterStatus = ref<TaskStatus | undefined>(undefined)

const filterStatusItems = [
  ...TASK_STATUS_OPTIONS.map((o) => ({ value: o.value, label: o.label })),
]

const rowStatusItems = TASK_STATUS_OPTIONS

const userSubtitle = computed(() =>
  user.value ? userDisplayName(user.value) || user.value.email : '',
)

function buildQuery(): string {
  const p = new URLSearchParams()
  if (filterFrom.value) p.set('date_from', filterFrom.value)
  if (filterTo.value) p.set('date_to', filterTo.value)
  if (filterStatus.value) p.set('status', filterStatus.value)
  const q = p.toString()
  return q ? `?${q}` : ''
}

function totalSecondsFromEntries(t: Task) {
  let secs = 0
  for (const e of t.time_entries) {
    if (e.ended_at === null) {
      const start = new Date(e.started_at).getTime()
      secs += Math.floor((Date.now() - start) / 1000)
    } else {
      secs += e.duration_seconds ?? 0
    }
  }
  return secs
}

const tick = ref(0)
let tickId: ReturnType<typeof setInterval> | null = null
watch(
  () => tasks.value.some((t) => t.active_timer_entry_id),
  (active) => {
    if (tickId) {
      clearInterval(tickId)
      tickId = null
    }
    if (active) {
      tickId = setInterval(() => {
        tick.value++
      }, 1000)
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  if (tickId) clearInterval(tickId)
})

function liveDurationSeconds(t: Task) {
  tick.value
  return totalSecondsFromEntries(t)
}

function formatDuration(totalSeconds: number) {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  if (h > 0) return `${h}ч ${m}м`
  if (m > 0) return `${m}м ${s}с`
  return `${s}с`
}

async function load() {
  loading.value = true
  err.value = ''
  try {
    tasks.value = await request<Task[]>(`/api/tasks${buildQuery()}`)
  } catch (e) {
    err.value = e instanceof Error ? e.message : 'Не удалось загрузить задачи'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  void load()
}

function clearFilters() {
  filterFrom.value = ''
  filterTo.value = ''
  filterStatus.value = undefined
  void load()
}

async function patchStatus(task: Task, status: TaskStatus) {
  if (status === task.status) return
  err.value = ''
  try {
    const updated = await request<Task>(`/api/tasks/${task.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
    const i = tasks.value.findIndex((x) => x.id === task.id)
    if (i >= 0) tasks.value[i] = updated
  } catch (e) {
    err.value = e instanceof Error ? e.message : 'Не удалось обновить статус'
  }
}

function replaceTask(updated: Task) {
  const i = tasks.value.findIndex((x) => x.id === updated.id)
  if (i >= 0) tasks.value[i] = updated
}

async function toggleTimer(t: Task) {
  err.value = ''
  try {
    if (t.active_timer_entry_id) {
      const updated = await request<Task>(`/api/tasks/${t.id}/time/stop`, { method: 'POST' })
      replaceTask(updated)
    } else {
      await request<Task>(`/api/tasks/${t.id}/time/start`, { method: 'POST' })
      await load()
    }
  } catch (e) {
    err.value = e instanceof Error ? e.message : 'Ошибка таймера'
  }
}

onMounted(async () => {
  await loadMe()
  await load()
})
</script>

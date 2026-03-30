<template>
  <div>
    <AppHeader
      title="Профиль"
      icon="i-lucide-user-cog"
      :show-back="true"
      back-to="/tasks"
      back-title="К задачам"
    />

    <UContainer class="space-y-8 py-8">
      <div class="grid gap-8 lg:grid-cols-2">
        <UCard>
          <template #header>
            <span class="inline-flex items-center gap-2 font-medium">
              <UIcon name="i-lucide-image" class="size-5 text-primary" />
              Аватар
            </span>
          </template>
          <div class="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
            <div
              class="flex size-28 shrink-0 items-center justify-center overflow-hidden rounded-full border-2 border-default bg-muted"
            >
              <img
                v-if="avatarPreview"
                :src="avatarPreview"
                alt=""
                class="size-full object-cover"
              />
              <UIcon v-else name="i-lucide-user" class="size-14 text-muted" />
            </div>
            <div class="flex flex-col gap-2">
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="onAvatarFile"
              />
              <UButton color="primary" variant="soft" @click="fileInput?.click()">Выбрать файл</UButton>
              <UButton :loading="avatarLoading" :disabled="!avatarFile" @click="uploadAvatar">
                Загрузить
              </UButton>
            </div>
          </div>
        </UCard>

        <UCard>
          <template #header>
            <span class="inline-flex items-center gap-2 font-medium">
              <UIcon name="i-lucide-banknote" class="size-5 text-primary" />
              Стоимость часа
            </span>
          </template>
          <form class="space-y-3" @submit.prevent="saveRate">
            <UInput
              v-model="hourlyRateStr"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
            <UButton type="submit" :loading="rateLoading">Сохранить ставку</UButton>
          </form>
        </UCard>
      </div>

      <UCard>
        <template #header>
          <span class="inline-flex items-center gap-2 font-medium">
            <UIcon name="i-lucide-user" class="size-5 text-primary" />
            Имя и фамилия
          </span>
        </template>
        <form class="max-w-md space-y-3" @submit.prevent="saveNames">
          <UInput v-model="firstNameStr" placeholder="Имя" autocomplete="given-name" />
          <UInput v-model="lastNameStr" placeholder="Фамилия" autocomplete="family-name" />
          <UButton type="submit" :loading="nameLoading">Сохранить</UButton>
        </form>
      </UCard>

      <UCard>
        <template #header>
          <span class="inline-flex items-center gap-2 font-medium">
            <UIcon name="i-lucide-key-round" class="size-5 text-primary" />
            Смена пароля
          </span>
        </template>
        <form class="max-w-md space-y-3" @submit.prevent="changePassword">
          <UInput v-model="pwdCurrent" type="password" autocomplete="current-password" placeholder="Текущий пароль" />
          <UInput v-model="pwdNew" type="password" autocomplete="new-password" placeholder="Новый пароль (от 8 символов)" minlength="8" />
          <UButton type="submit" color="neutral" :loading="pwdLoading">Обновить пароль</UButton>
          <UAlert v-if="pwdMsg" color="success" variant="soft" :title="pwdMsg" />
          <UAlert v-if="pwdErr" color="error" variant="soft" :title="pwdErr" />
        </form>
      </UCard>

      <UCard>
        <template #header>
          <span class="inline-flex items-center gap-2 font-medium">
            <UIcon name="i-lucide-table" class="size-5 text-primary" />
            Задачи и расчёт
          </span>
        </template>

        <div class="mb-4 flex flex-wrap items-end gap-3">
          <UFormField label="С даты">
            <UInput v-model="filterFrom" type="date" />
          </UFormField>
          <UFormField label="По дату">
            <UInput v-model="filterTo" type="date" />
          </UFormField>
          <UButton color="primary" variant="soft" @click="loadTasks">Применить фильтр</UButton>
          <UButton color="neutral" variant="ghost" @click="clearFilter">Сбросить</UButton>
        </div>

        <div v-if="tasksLoading" class="text-muted">Загрузка…</div>
        <div v-else class="overflow-x-auto rounded-lg border border-default">
          <table class="w-full min-w-[640px] text-left text-sm">
            <thead class="border-b border-default bg-elevated/50">
              <tr>
                <th class="w-10 p-2">
                  <input
                    type="checkbox"
                    class="size-4 rounded border-default"
                    :checked="allSelected"
                    @change="onToggleAll(($event.target as HTMLInputElement).checked)"
                  />
                </th>
                <th class="p-2 font-medium">Задача</th>
                <th class="p-2 font-medium">Создана</th>
                <th class="p-2 font-medium">Время</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="t in tasks"
                :key="t.id"
                class="border-b border-default/60 hover:bg-muted/20"
              >
                <td class="p-2">
                  <input
                    type="checkbox"
                    class="size-4 rounded border-default"
                    :checked="selectedIds.has(t.id)"
                    @change="onToggleRow(t.id, ($event.target as HTMLInputElement).checked)"
                  />
                </td>
                <td class="p-2">
                  <RouterLink :to="{ name: 'task-edit', params: { id: t.id } }" class="text-primary hover:underline">
                    {{ t.title }}
                  </RouterLink>
                </td>
                <td class="p-2 text-muted">{{ formatShortDate(t.created_at) }}</td>
                <td class="p-2 font-mono text-xs">{{ formatDuration(t.total_tracked_seconds) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="!tasksLoading && !tasks.length" class="mt-4 text-sm text-muted">Нет задач в выбранном диапазоне.</p>

        <div class="mt-6 flex flex-wrap items-center gap-3">
          <UButton
            color="primary"
            icon="i-lucide-calculator"
            :disabled="selectedIds.size === 0 || summaryLoading"
            :loading="summaryLoading"
            @click="runSummary"
          >
            Посчитать по выбранным
          </UButton>
        </div>

        <div v-if="summary" class="mt-4 rounded-lg border border-primary/40 bg-primary/5 p-4">
          <p class="text-sm text-muted">Время</p>
          <p class="font-mono text-xl text-highlighted">{{ formatDuration(summary.total_seconds) }}</p>
          <p class="mt-3 text-sm text-muted">Ставка / час</p>
          <p class="font-medium">{{ summary.hourly_rate }}</p>
          <p class="mt-3 text-sm text-muted">Сумма</p>
          <p class="text-2xl font-semibold text-primary">{{ summary.total_amount }}</p>
        </div>
      </UCard>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import AppHeader from '@/components/AppHeader.vue'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'
import type { Task, TimeMoneySummary, UserProfile } from '@/types/api'

const { request } = useApi()
const { user, loadMe } = useAuth()

const fileInput = ref<HTMLInputElement | null>(null)
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)
const avatarLoading = ref(false)

const hourlyRateStr = ref('0')
const rateLoading = ref(false)

const firstNameStr = ref('')
const lastNameStr = ref('')
const nameLoading = ref(false)

const pwdCurrent = ref('')
const pwdNew = ref('')
const pwdLoading = ref(false)
const pwdMsg = ref('')
const pwdErr = ref('')

const filterFrom = ref('')
const filterTo = ref('')
const tasks = ref<Task[]>([])
const tasksLoading = ref(false)
const selectedIds = ref<Set<string>>(new Set())
const summaryLoading = ref(false)
const summary = ref<TimeMoneySummary | null>(null)

const allSelected = computed(() => tasks.value.length > 0 && tasks.value.every((t) => selectedIds.value.has(t.id)))

function applyUser(u: UserProfile | null) {
  if (!u) return
  hourlyRateStr.value = u.hourly_rate ?? '0'
  firstNameStr.value = u.first_name ?? ''
  lastNameStr.value = u.last_name ?? ''
  avatarPreview.value = u.avatar_url ? u.avatar_url : null
}

watch(
  () => user.value,
  (u) => applyUser(u),
  { immediate: true },
)

onMounted(async () => {
  await loadMe()
  applyUser(user.value)
  await loadTasks()
})

function buildQuery(): string {
  const p = new URLSearchParams()
  if (filterFrom.value) p.set('date_from', filterFrom.value)
  if (filterTo.value) p.set('date_to', filterTo.value)
  const q = p.toString()
  return q ? `?${q}` : ''
}

async function loadTasks() {
  tasksLoading.value = true
  summary.value = null
  try {
    tasks.value = await request<Task[]>(`/api/tasks${buildQuery()}`)
    selectedIds.value = new Set()
  } finally {
    tasksLoading.value = false
  }
}

function clearFilter() {
  filterFrom.value = ''
  filterTo.value = ''
  void loadTasks()
}

function formatShortDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString('ru-RU')
  } catch {
    return iso
  }
}

function formatDuration(totalSeconds: number) {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  if (h > 0) return `${h}ч ${m}м ${s}с`
  if (m > 0) return `${m}м ${s}с`
  return `${s}с`
}

function onToggleRow(id: string, checked: boolean) {
  const next = new Set(selectedIds.value)
  if (checked) next.add(id)
  else next.delete(id)
  selectedIds.value = next
}

function onToggleAll(checked: boolean) {
  if (checked) selectedIds.value = new Set(tasks.value.map((t) => t.id))
  else selectedIds.value = new Set()
}

function onAvatarFile(ev: Event) {
  const f = (ev.target as HTMLInputElement).files?.[0]
  avatarFile.value = f ?? null
  if (avatarPreview.value?.startsWith('blob:')) URL.revokeObjectURL(avatarPreview.value)
  if (f) avatarPreview.value = URL.createObjectURL(f)
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  avatarLoading.value = true
  try {
    const fd = new FormData()
    fd.append('file', avatarFile.value)
    const { url } = await request<{ url: string }>('/api/users/me/avatar', { method: 'POST', body: fd })
    avatarPreview.value = url
    avatarFile.value = null
    await loadMe()
  } finally {
    avatarLoading.value = false
  }
}

async function saveRate() {
  rateLoading.value = true
  try {
    await request('/api/users/me', {
      method: 'PATCH',
      body: JSON.stringify({ hourly_rate: Number(hourlyRateStr.value) || 0 }),
    })
    await loadMe()
  } finally {
    rateLoading.value = false
  }
}

async function saveNames() {
  nameLoading.value = true
  try {
    await request('/api/users/me', {
      method: 'PATCH',
      body: JSON.stringify({
        first_name: firstNameStr.value.trim() || null,
        last_name: lastNameStr.value.trim() || null,
      }),
    })
    await loadMe()
  } finally {
    nameLoading.value = false
  }
}

async function changePassword() {
  pwdMsg.value = ''
  pwdErr.value = ''
  pwdLoading.value = true
  try {
    await request('/api/users/me/password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: pwdCurrent.value,
        new_password: pwdNew.value,
      }),
    })
    pwdMsg.value = 'Пароль обновлён'
    pwdCurrent.value = ''
    pwdNew.value = ''
  } catch (e) {
    pwdErr.value = e instanceof Error ? e.message : 'Ошибка'
  } finally {
    pwdLoading.value = false
  }
}

async function runSummary() {
  if (selectedIds.value.size === 0) return
  summaryLoading.value = true
  try {
    summary.value = await request<TimeMoneySummary>('/api/tasks/aggregate-time', {
      method: 'POST',
      body: JSON.stringify({ task_ids: [...selectedIds.value] }),
    })
  } finally {
    summaryLoading.value = false
  }
}
</script>

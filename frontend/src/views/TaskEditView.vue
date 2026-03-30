<template>
  <div>
    <AppHeader
      :title="isNew ? 'Новая задача' : 'Задача'"
      icon="i-lucide-file-text"
      :show-back="true"
      back-to="/tasks"
      back-title="К списку"
    />
    <UContainer class="max-w-6xl py-8">
      <UAlert v-if="loadError" color="error" variant="soft" :title="loadError" />
      <div v-else-if="loading" class="flex items-center gap-2 text-muted">
        <UIcon name="i-lucide-loader-2" class="size-5 animate-spin" />
        <span>Загрузка…</span>
      </div>
      <div v-else class="grid gap-8 lg:grid-cols-[1fr_300px] lg:items-start">
        <div class="min-w-0 space-y-6">
          <div class="flex flex-wrap items-center gap-2">
            <UButton
              v-if="isNew"
              color="primary"
              icon="i-lucide-save"
              :loading="saving"
              @click="save"
            >
              Создать
            </UButton>
            <UButton
              v-if="!isNew && !isEditing"
              color="neutral"
              variant="soft"
              icon="i-lucide-pencil"
              @click="enterEditMode"
            >
              Редактировать
            </UButton>
            <UAlert
              v-if="!isNew && !isEditing"
              color="neutral"
              variant="soft"
              title="Для изменения задачи сначала нажмите «Редактировать»"
            />
          </div>
          <UFormField>
            <template #label>
              <span class="inline-flex items-center gap-2">
                <UIcon name="i-lucide-heading" class="size-4 text-muted" />
                Название
              </span>
            </template>
            <UInput v-model="title" class="w-full" maxlength="500" :disabled="!canEditFields" />
          </UFormField>
          
          <UFormField>
            <template #label>
              <span class="inline-flex items-center gap-2">
                <UIcon name="i-lucide-align-left" class="size-4 text-muted" />
                Описание
              </span>
            </template>
            <TipTapEditor v-model="contentJson" :editable="canEditFields" />
          </UFormField>
          <TaskComments v-if="task?.id" :task-id="task.id" />
        </div>

        <aside v-if="!isNew && task" class="lg:sticky lg:top-19">
          <div class="mb-5 space-y-2">
            <UButton
              color="primary"
              icon="i-lucide-save"
              :loading="saving"
              :disabled="!isEditing"
              @click="saveAndExitEditMode"
            >
              Сохранить
            </UButton>
            <UButton color="error" variant="soft" icon="i-lucide-trash-2" @click="remove">Удалить</UButton>
          </div>

          <UFormField class="mb-5">
            <template #label>
              <span class="inline-flex items-center gap-2">
                <UIcon name="i-lucide-git-branch" class="size-4 text-muted" />
                Статус
              </span>
            </template>
            <USelect
              v-model="status"
              :items="statusItems"
              value-key="value"
              label-key="label"
              class="w-full"
              :disabled="!canEditFields"
            />
          </UFormField>

          <UCard class="border-primary/20">
            <template #header>
              <span class="inline-flex items-center gap-2 font-medium" title="Учёт времени">
                <UIcon name="i-lucide-timer" class="size-5 text-primary" />
                <span class="hidden sm:inline">Учёт времени</span>
              </span>
            </template>
            <div class="flex gap-4">
              <div>
                <p class="font-mono text-2xl tabular-nums tracking-tight text-highlighted">{{ displayTime }}</p>
              </div>
              <div class="flex gap-2">
                <UButton
                  v-if="!task.active_timer_entry_id"
                  color="primary"
                  square
                  icon="i-lucide-play"
                  title="Старт"
                  aria-label="Старт таймера"
                  @click="startTimer"
                />
                <UButton
                  v-else
                  color="error"
                  variant="soft"
                  square
                  icon="i-lucide-square"
                  title="Стоп"
                  aria-label="Стоп таймера"
                  @click="stopTimer"
                />
              </div>
            </div>
            <div class="mt-4 flex flex-wrap items-end gap-2 border-t border-default/60 pt-4">
              <UFormField label="Добавить вручную (мин)">
                <UInput v-model.number="manualMinutes" type="number" min="1" step="1" class="w-36" />
              </UFormField>
              <UButton
                color="neutral"
                variant="soft"
                icon="i-lucide-plus-circle"
                :loading="manualAdding"
                :disabled="manualMinutes < 1"
                @click="addManualTime"
              >
                Добавить
              </UButton>
            </div>
          </UCard>
        </aside>
      </div>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppHeader from '@/components/AppHeader.vue'
import TaskComments from '@/components/TaskComments.vue'
import TipTapEditor from '@/components/TipTapEditor.vue'
import { useApi } from '@/composables/useApi'
import { TASK_STATUS_OPTIONS } from '@/lib/statuses'
import type { Task, TaskStatus } from '@/types/api'

const route = useRoute()
const router = useRouter()
const { request } = useApi()

const isNew = computed(() => route.name === 'task-new')

const title = ref('')
const status = ref<TaskStatus>('familiarization')
const contentJson = ref<string | null>(null)
const task = ref<Task | null>(null)
const loading = ref(true)
const saving = ref(false)
const loadError = ref('')
const tick = ref(0)
const manualMinutes = ref(15)
const manualAdding = ref(false)
const isEditing = ref(false)

const statusItems = TASK_STATUS_OPTIONS
const canEditFields = computed(() => isNew.value || isEditing.value)

let timerId: ReturnType<typeof setInterval> | null = null

function totalSecondsFromEntries(t: { time_entries: { started_at: string; ended_at: string | null; duration_seconds: number | null }[] }) {
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

const displayTime = computed(() => {
  tick.value
  const t = task.value
  if (!t) return '0:00:00'
  const secs = totalSecondsFromEntries(t)
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60
  return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

watch(
  () => task.value?.active_timer_entry_id,
  (active) => {
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }
    if (active) {
      timerId = setInterval(() => {
        tick.value++
      }, 1000)
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})

async function loadTask() {
  if (isNew.value) {
    title.value = ''
    status.value = 'familiarization'
    contentJson.value = null
    task.value = null
    loading.value = false
    return
  }
  const id = route.params.id as string
  loading.value = true
  loadError.value = ''
  try {
    const t = await request<Task>(`/api/tasks/${id}`)
    task.value = t
    title.value = t.title
    status.value = t.status
    contentJson.value = t.content_json
    isEditing.value = false
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

onMounted(loadTask)
watch(
  () => route.params.id,
  () => {
    void loadTask()
  },
)

async function save() {
  saving.value = true
  try {
    if (isNew.value) {
      const created = await request<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({
          title: title.value || 'Без названия',
          content_json: contentJson.value,
          status: status.value,
        }),
      })
      await router.replace({ name: 'task-edit', params: { id: created.id } })
      task.value = created
      isEditing.value = false
    } else if (task.value) {
      task.value = await request<Task>(`/api/tasks/${task.value.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          title: title.value,
          content_json: contentJson.value,
          status: status.value,
        }),
      })
    }
  } finally {
    saving.value = false
  }
}

function enterEditMode() {
  isEditing.value = true
}

async function saveAndExitEditMode() {
  if (!isEditing.value) return
  await save()
  isEditing.value = false
}

async function startTimer() {
  if (!task.value) return
  task.value = await request<Task>(`/api/tasks/${task.value.id}/time/start`, { method: 'POST' })
}

async function stopTimer() {
  if (!task.value) return
  task.value = await request<Task>(`/api/tasks/${task.value.id}/time/stop`, { method: 'POST' })
}

async function addManualTime() {
  if (!task.value) return
  const minutes = Math.floor(Number(manualMinutes.value) || 0)
  if (minutes < 1) return
  manualAdding.value = true
  try {
    task.value = await request<Task>(`/api/tasks/${task.value.id}/time/manual`, {
      method: 'POST',
      body: JSON.stringify({ minutes }),
    })
  } finally {
    manualAdding.value = false
  }
}

async function remove() {
  if (!task.value || !confirm('Удалить задачу?')) return
  await request(`/api/tasks/${task.value.id}`, { method: 'DELETE' })
  await router.push({ name: 'tasks' })
}
</script>

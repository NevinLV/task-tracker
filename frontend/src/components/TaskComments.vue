<template>
  <UCard class="border-default/80">
    <template #header>
      <span class="inline-flex items-center gap-2 font-medium">
        <UIcon name="i-lucide-message-square" class="size-5 text-primary" />
        Комментарии
      </span>
    </template>
    <div v-if="loading" class="text-sm text-muted">Загрузка…</div>
    <div v-else class="space-y-4">
      <ul v-if="comments.length" class="space-y-3 overflow-y-auto">
        <li
          v-for="c in comments"
          :key="c.id"
          class="rounded-lg border border-default/60 bg-muted/30 p-3 text-sm"
        >
          <div class="flex items-start gap-3">
            <div
              class="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-full border border-default bg-muted"
            >
              <img
                v-if="c.author.avatar_url"
                :src="c.author.avatar_url"
                alt=""
                class="size-full object-cover"
              />
              <span v-else class="text-[10px] font-semibold text-muted">{{ authorInitials(c.author) }}</span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-highlighted">{{ c.author.display_name }}</p>
              <p class="mt-1 whitespace-pre-wrap text-default">{{ c.body }}</p>
              <p class="mt-2 text-xs text-muted">{{ formatDate(c.created_at) }}</p>
            </div>
          </div>
        </li>
      </ul>
      <p v-else class="text-sm text-muted">Комментариев пока нет.</p>
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end">
        <UFormField class="flex-1">
          <UTextarea v-model="draft" class="w-full" :rows="3" autoresize placeholder="Текст комментария…" />
        </UFormField>
        
      </div>
      <div class="w-full">
      <UButton
          color="primary"
          icon="i-lucide-send"
          :loading="sending"
          :disabled="!draft.trim()"
          @click="submit"
        >
          Отправить
        </UButton>
      </div>
    
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { useApi } from '@/composables/useApi'
import type { CommentAuthor, TaskComment } from '@/types/api'

function authorInitials(a: CommentAuthor) {
  const fn = a.first_name?.trim()
  const ln = a.last_name?.trim()
  if (fn && ln) return (fn[0]! + ln[0]!).toUpperCase()
  if (fn) return fn.slice(0, 2).toUpperCase()
  if (ln) return ln.slice(0, 2).toUpperCase()
  return a.display_name.slice(0, 2).toUpperCase()
}

const props = defineProps<{
  taskId: string
}>()

const { request } = useApi()

const comments = ref<TaskComment[]>([])
const loading = ref(true)
const sending = ref(false)
const draft = ref('')

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString('ru-RU', {
      dateStyle: 'short',
      timeStyle: 'short',
    })
  } catch {
    return iso
  }
}

async function load() {
  loading.value = true
  try {
    comments.value = await request<TaskComment[]>(`/api/tasks/${props.taskId}/comments`)
  } finally {
    loading.value = false
  }
}

async function submit() {
  const text = draft.value.trim()
  if (!text) return
  sending.value = true
  try {
    const c = await request<TaskComment>(`/api/tasks/${props.taskId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ body: text }),
    })
    comments.value = [c, ...comments.value]
    draft.value = ''
  } finally {
    sending.value = false
  }
}

onMounted(load)
watch(
  () => props.taskId,
  () => {
    void load()
  },
)
</script>

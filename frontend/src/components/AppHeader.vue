<template>
  <header class="sticky top-0 z-40 border-b border-default bg-elevated/50 backdrop-blur-md">
    <UContainer class="flex flex-wrap items-center justify-between gap-3 py-3">
      <div class="flex min-w-0 items-center gap-3">
        <UButton
          v-if="showBack"
          color="neutral"
          variant="ghost"
          square
          icon="i-lucide-arrow-left"
          :title="backTitle"
          :aria-label="backTitle"
          @click="goBack"
        />
        <UIcon v-if="icon" :name="icon" class="size-8 shrink-0 text-primary" />
        <div class="min-w-0">
          <h1 class="truncate text-lg font-semibold tracking-tight text-highlighted">{{ title }}</h1>
          <p v-if="subtitle" class="truncate text-xs text-muted">{{ subtitle }}</p>
        </div>
      </div>

      <div class="flex items-center gap-1">
        <UserAvatarLink />
        <ThemeToggle />
        <UButton
          icon="i-lucide-plus"
          color="primary"
          square
          title="Новая задача"
          aria-label="Новая задача"
          @click="goNewTask"
        />
        <UButton
          icon="i-lucide-log-out"
          color="neutral"
          variant="ghost"
          square
          title="Выйти"
          aria-label="Выйти"
          @click="onLogout"
        />
      </div>
    </UContainer>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

import { useAuth } from '@/composables/useAuth'
import ThemeToggle from './ThemeToggle.vue'
import UserAvatarLink from './UserAvatarLink.vue'

const props = withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    icon?: string
    showBack?: boolean
    backTo?: string
    backTitle?: string
  }>(),
  {
    subtitle: '',
    icon: '',
    showBack: false,
    backTo: '/tasks',
    backTitle: 'Назад',
  },
)

const router = useRouter()
const { logout } = useAuth()

function goBack() {
  void router.push(props.backTo)
}

function goNewTask() {
  void router.push({ name: 'task-new' })
}

async function onLogout() {
  logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="relative min-h-[80vh]">
    <div class="absolute right-4 top-4 z-10">
      <ThemeToggle />
    </div>
    <UContainer class="py-16">
      <UCard class="mx-auto max-w-md border-default/80 shadow-lg">
        <template #header>
          <div class="flex items-center gap-3">
            <UIcon name="i-lucide-log-in" class="size-8 text-primary" />
            <h1 class="text-lg font-semibold tracking-tight">Вход</h1>
          </div>
        </template>
        <form class="space-y-4" @submit.prevent="submit">
          <UFormField>
            <template #label>
              <span class="inline-flex items-center gap-2">
                <UIcon name="i-lucide-mail" class="size-4 text-muted" />
                Email
              </span>
            </template>
            <UInput v-model="email" type="email"  class="w-full" autocomplete="email" required />
          </UFormField>
          <UFormField>
            <template #label>
              <span class="inline-flex items-center gap-2">
                <UIcon name="i-lucide-key-round" class="size-4 text-muted" />
                Пароль
              </span>
            </template>
            <UInput v-model="password" class="w-full" type="password" autocomplete="current-password" required />
          </UFormField>
          <UAlert v-if="error" color="error" variant="soft" :title="error" />
          <UButton type="submit" block :loading="loading" icon="i-lucide-arrow-right" trailing>Войти</UButton>
          <p class="text-center text-sm text-muted">
            Нет аккаунта?
            <RouterLink to="/register" class="font-medium text-primary hover:underline">Регистрация</RouterLink>
          </p>
        </form>
      </UCard>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import ThemeToggle from '@/components/ThemeToggle.vue'
import { useApi } from '@/composables/useApi'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { request } = useApi()
const { setToken, loadMe } = useAuth()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const res = await request<{ access_token: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.value, password: password.value }),
    })
    setToken(res.access_token)
    await loadMe()
    await router.push({ name: 'tasks' })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

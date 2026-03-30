<template>
  <RouterLink
    to="/profile"
    class="flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-full border border-default bg-elevated transition hover:ring-2 hover:ring-primary/40"
    :title="title"
    :aria-label="title"
  >
    <img v-if="user?.avatar_url" :src="user.avatar_url" alt="" class="size-full object-cover" />
    <span v-else class="text-xs font-semibold text-muted">{{ initials }}</span>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { useAuth } from '@/composables/useAuth'
import { userDisplayName, userInitials } from '@/lib/userDisplay'

const { user } = useAuth()

const title = computed(() => userDisplayName(user.value) || 'Профиль')
const initials = computed(() => userInitials(user.value))
</script>

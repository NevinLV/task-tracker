<template>
  <UButton
    color="neutral"
    variant="ghost"
    square
    :icon="isDark ? 'i-lucide-sun' : 'i-lucide-moon'"
    :aria-label="isDark ? 'Светлая тема' : 'Тёмная тема'"
    :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
    @click="toggle()"
  />
</template>

<script setup lang="ts">
import { useDark, useToggle } from '@vueuse/core'

const isDark = useDark({
  storageKey: 'tasktracker-color-mode',
  valueDark: 'dark',
  valueLight: '',
})

const toggle = useToggle(isDark)
</script>

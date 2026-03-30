import './assets/main.css'

import ui from '@nuxt/ui/vue-plugin'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import { useAuth } from './composables/useAuth'
import { routes } from './router'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const auth = useAuth()
router.beforeEach(async (to) => {
  if (to.meta.requiresAuth && !auth.token.value) return { name: 'login' }
  if (to.meta.guest && auth.token.value) return { name: 'tasks' }
  if (to.meta.requiresAuth && auth.token.value) await auth.loadMe()
  return true
})

const app = createApp(App)
app.use(router)
app.use(ui)
app.mount('#app')

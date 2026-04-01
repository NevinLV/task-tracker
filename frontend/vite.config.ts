import ui from '@nuxt/ui/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), ui()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': { target: 'https://task-tracker-5nzw.onrender.com', changeOrigin: true },
      '/static': { target: 'https://task-tracker-5nzw.onrender.com', changeOrigin: true },
    },
  },
})

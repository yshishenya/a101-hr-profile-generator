import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // Vuetify plugin with auto-import
    vuetify({ autoImport: true })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to backend
      // Use environment variable or default to localhost
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8022',
        changeOrigin: true,
        secure: false
      }
    }
  }
})

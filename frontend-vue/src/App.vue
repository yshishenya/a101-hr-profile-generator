<!--
  Root Application Component
  Entry point for the Vue application
-->

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const auth = useAuthStore()
const { initTheme } = useTheme()

/**
 * Initialize application on mount
 * - Restore theme from localStorage
 * - Load user session if token exists
 */
onMounted(async () => {
  initTheme()
  await auth.initialize()
})
</script>

<template>
  <v-app>
    <router-view />
  </v-app>
</template>

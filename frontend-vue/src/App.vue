<!--
  Root Application Component
  Entry point for the Vue application
-->

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { initTheme } = useTheme()

/**
 * Initialize application on mount
 * - Restore theme from localStorage
 * Note: Auth initialization is handled in router guard (see router/index.ts)
 */
onMounted(() => {
  initTheme()
})
</script>

<template>
  <v-app>
    <router-view />
  </v-app>
</template>

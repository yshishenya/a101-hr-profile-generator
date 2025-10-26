<!--
  App Header Component
  Top app bar with title, user info, theme toggle, and logout button
-->

<template>
  <v-app-bar elevation="1" color="primary">
    <v-toolbar-title class="text-h6 font-weight-bold">
      A101 HR Profile Generator
    </v-toolbar-title>

    <v-spacer />

    <!-- User info chip -->
    <v-chip
      v-if="auth.user"
      class="ma-2"
      color="white"
      text-color="primary"
      prepend-icon="mdi-account-circle"
    >
      {{ auth.user.full_name }}
    </v-chip>

    <!-- Theme toggle button -->
    <v-btn
      :icon="isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'"
      variant="text"
      color="white"
      @click="toggleTheme"
    />

    <!-- Logout button -->
    <v-btn
      icon="mdi-logout"
      variant="text"
      color="white"
      @click="handleLogout"
    />
  </v-app-bar>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const router = useRouter()
const auth = useAuthStore()
const { isDark, toggleTheme } = useTheme()

/**
 * Handle logout action
 * Clears auth state and redirects to login page
 */
const handleLogout = async () => {
  await auth.logout()
  router.push('/login')
}
</script>

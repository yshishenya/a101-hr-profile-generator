<!--
  Main Application Layout
  Authenticated layout with navigation drawer, app bar, and content area
-->

<template>
  <v-app>
    <!-- Left navigation drawer -->
    <v-navigation-drawer
      v-model="drawer"
      :permanent="display.mdAndUp.value"
      :temporary="display.smAndDown.value"
      color="surface"
    >
      <!-- App title in drawer -->
      <v-list-item
        class="pa-4"
        title="A101 HR"
        subtitle="Profile Generator"
      >
        <template #prepend>
          <v-icon size="40" color="primary">mdi-account-box</v-icon>
        </template>
      </v-list-item>

      <v-divider />

      <!-- Navigation menu -->
      <v-list nav density="comfortable">
        <v-list-item
          v-for="item in menuItems"
          :key="item.route"
          :to="item.route"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="xl"
          class="ma-2"
        />
      </v-list>
    </v-navigation-drawer>

    <!-- App bar with header component -->
    <AppHeader />

    <!-- Main content area -->
    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDisplay } from 'vuetify'
import AppHeader from './AppHeader.vue'

const display = useDisplay()
const drawer = ref(true)

// Navigation menu items
const menuItems = [
  {
    title: 'Profiles',
    icon: 'mdi-briefcase-outline',
    route: '/',
  },
]
</script>

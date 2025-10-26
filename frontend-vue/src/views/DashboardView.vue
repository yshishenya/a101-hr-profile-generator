<template>
  <v-container fluid class="pa-6">
    <!-- Page Title with Refresh Button -->
    <div class="d-flex align-center justify-space-between mb-6">
      <h1 class="text-h4 font-weight-bold">
        Dashboard
      </h1>
      <v-btn
        color="primary"
        variant="tonal"
        prepend-icon="mdi-refresh"
        :loading="loading"
        @click="refresh"
      >
        Refresh
      </v-btn>
    </div>

    <!-- Error Alert -->
    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      closable
      class="mb-6"
      @click:close="error = null"
    >
      {{ error }}
    </v-alert>

    <!-- Welcome Card -->
    <BaseCard class="mb-6">
      <v-card-text class="pa-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon size="48" color="primary" class="mr-4">
              mdi-hand-wave
            </v-icon>
            <div>
              <h2 class="text-h5 font-weight-medium mb-1">
                Welcome, {{ authStore.user?.full_name || 'User' }}!
              </h2>
              <p class="text-subtitle-1 text-medium-emphasis mb-0">
                {{ stats ? 'Real-time dashboard statistics' : 'Loading statistics...' }}
              </p>
            </div>
          </div>
          <div v-if="stats" class="text-right">
            <div class="text-caption text-medium-emphasis">
              Last Updated
            </div>
            <div class="text-subtitle-2">
              {{ formattedLastUpdated }}
            </div>
          </div>
        </div>
      </v-card-text>
    </BaseCard>

    <!-- Loading State -->
    <v-row v-if="loading && !stats">
      <v-col cols="12">
        <div class="text-center py-12">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          />
          <p class="text-subtitle-1 text-medium-emphasis mt-4">
            Loading dashboard statistics...
          </p>
        </div>
      </v-col>
    </v-row>

    <!-- Stats Cards Row -->
    <v-row v-else-if="stats">
      <v-col cols="12" sm="6" md="3">
        <StatsCard
          icon="mdi-briefcase-outline"
          icon-color="primary"
          label="Всего позиций"
          :value="stats.positions_count || 0"
        />
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <StatsCard
          icon="mdi-account-check-outline"
          icon-color="success"
          label="Сгенерировано"
          :value="stats.profiles_count || 0"
          :progress-value="dashboardStore.coverageProgress"
        />
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <StatsCard
          icon="mdi-chart-arc"
          icon-color="info"
          label="Покрытие"
          :value="`${(stats.completion_percentage ?? 0).toFixed(1)}%`"
          :progress-value="stats.completion_percentage ?? 0"
        />
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <StatsCard
          icon="mdi-clock-outline"
          icon-color="warning"
          label="В процессе"
          :value="stats.active_tasks_count ?? 0"
        />
      </v-col>
    </v-row>

    <!-- Content Row -->
    <v-row v-if="stats" class="mt-6">
      <v-col cols="12" md="8">
        <BaseCard>
          <v-card-title class="pa-4">
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Recent Activity
          </v-card-title>
          <v-card-text class="pa-6">
            <div class="text-center py-12">
              <v-icon size="64" color="grey-lighten-1" class="mb-4">
                mdi-chart-timeline-variant
              </v-icon>
              <p class="text-subtitle-1 text-medium-emphasis">
                Activity chart coming in Week 4
              </p>
              <p class="text-caption text-medium-emphasis">
                Will display recent generation tasks and trends
              </p>
            </div>
          </v-card-text>
        </BaseCard>
      </v-col>

      <v-col cols="12" md="4">
        <BaseCard>
          <v-card-title class="pa-4">
            <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
            Quick Actions
          </v-card-title>
          <v-card-text class="pa-4">
            <v-list lines="two" class="pa-0">
              <v-list-item
                prepend-icon="mdi-file-document-plus"
                title="Generate Profile"
                subtitle="Create a new employee profile"
                disabled
              >
                <template #append>
                  <v-chip size="small" color="primary" variant="flat">
                    Week 4
                  </v-chip>
                </template>
              </v-list-item>
              <v-list-item
                prepend-icon="mdi-file-multiple"
                title="View Profiles"
                subtitle="Browse generated profiles"
                disabled
              >
                <template #append>
                  <v-chip size="small" color="primary" variant="flat">
                    Week 5
                  </v-chip>
                </template>
              </v-list-item>
              <v-list-item
                prepend-icon="mdi-download-multiple"
                title="Bulk Generate"
                subtitle="Generate multiple profiles"
                disabled
              >
                <template #append>
                  <v-chip size="small" color="primary" variant="flat">
                    Week 6
                  </v-chip>
                </template>
              </v-list-item>
              <v-list-item
                prepend-icon="mdi-cog"
                title="Settings"
                subtitle="Configure application"
                disabled
              >
                <template #append>
                  <v-chip size="small" color="grey" variant="flat">
                    TBD
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </BaseCard>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import BaseCard from '@/components/common/BaseCard.vue'
import StatsCard from '@/components/common/StatsCard.vue'

// Stores
const authStore = useAuthStore()
const dashboardStore = useDashboardStore()

// Local state for polling interval
const refreshInterval = ref<number | null>(null)
let isPolling = false // Prevent overlapping polls

// Computed properties from store
const stats = dashboardStore.stats
const loading = dashboardStore.loading
const error = dashboardStore.error
const formattedLastUpdated = dashboardStore.formattedLastUpdated

/**
 * Refresh stats manually
 */
async function refresh() {
  await dashboardStore.refresh()
}

// Lifecycle hooks
onMounted(() => {
  // Initial fetch
  dashboardStore.fetchStats()

  // Auto-refresh every 30 seconds if there are active tasks
  refreshInterval.value = window.setInterval(async () => {
    if (dashboardStore.hasActiveGenerations && !isPolling) {
      isPolling = true
      try {
        await dashboardStore.fetchStats()
      } catch (error: unknown) {
        // Error is already logged and stored in dashboardStore.error
        // No need to show additional notification
      } finally {
        isPolling = false
      }
    }
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
  // Reset polling flag to prevent stale state on remount
  isPolling = false
})
</script>

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
    <v-card elevation="2" rounded="lg" class="mb-6">
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
    </v-card>

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
      <!-- Total Positions Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="primary" class="mr-3">
              mdi-briefcase-outline
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                {{ stats.positions_count.toLocaleString() }}
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Total Positions
              </div>
            </div>
          </div>
          <v-progress-linear
            color="primary"
            :model-value="100"
            height="4"
            rounded
          />
        </v-card>
      </v-col>

      <!-- Profiles Generated Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="success" class="mr-3">
              mdi-account-check-outline
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                {{ stats.profiles_count.toLocaleString() }}
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Profiles Generated
              </div>
            </div>
          </div>
          <v-progress-linear
            color="success"
            :model-value="(stats.profiles_count / stats.positions_count) * 100"
            height="4"
            rounded
          />
        </v-card>
      </v-col>

      <!-- Completion Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="info" class="mr-3">
              mdi-chart-arc
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                {{ stats.completion_percentage.toFixed(1) }}%
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Completion
              </div>
            </div>
          </div>
          <v-progress-linear
            color="info"
            :model-value="stats.completion_percentage"
            height="4"
            rounded
          />
        </v-card>
      </v-col>

      <!-- Active Tasks Card -->
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" rounded="lg" class="pa-4">
          <div class="d-flex align-center mb-3">
            <v-icon size="40" color="warning" class="mr-3">
              mdi-clock-outline
            </v-icon>
            <div>
              <div class="text-h4 font-weight-bold">
                {{ stats.active_tasks_count }}
              </div>
              <div class="text-subtitle-2 text-medium-emphasis">
                Active Tasks
              </div>
            </div>
          </div>
          <v-progress-linear
            color="warning"
            :model-value="stats.active_tasks_count > 0 ? 100 : 0"
            :indeterminate="stats.active_tasks_count > 0"
            height="4"
            rounded
          />
        </v-card>
      </v-col>
    </v-row>

    <!-- Content Row -->
    <v-row v-if="stats" class="mt-6">
      <v-col cols="12" md="8">
        <v-card elevation="2" rounded="lg">
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
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2" rounded="lg">
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
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import dashboardService from '@/services/dashboard.service'
import type { DashboardStats } from '@/types/api'

// Access auth store for user info
const authStore = useAuthStore()

// Dashboard state
const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const refreshInterval = ref<number | null>(null)

// Computed properties
const formattedLastUpdated = computed(() => {
  if (!stats.value?.last_updated) return 'Never'
  const date = new Date(stats.value.last_updated)
  return date.toLocaleTimeString()
})

/**
 * Fetch dashboard statistics
 */
async function fetchStats() {
  try {
    error.value = null
    const response = await dashboardService.getStats()
    // Handle both wrapped and unwrapped responses
    stats.value = response.data || response as any
  } catch (err: any) {
    console.error('Failed to fetch dashboard stats:', err)
    error.value = err.response?.data?.error?.message || err.message || 'Failed to load dashboard statistics'
  } finally {
    loading.value = false
  }
}

/**
 * Refresh stats manually
 */
async function refresh() {
  loading.value = true
  await fetchStats()
}

// Lifecycle hooks
onMounted(() => {
  fetchStats()

  // Auto-refresh every 30 seconds if there are active tasks
  refreshInterval.value = window.setInterval(() => {
    if (stats.value && stats.value.active_tasks_count > 0) {
      fetchStats()
    }
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

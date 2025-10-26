<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
    <v-row>
      <v-col>
        <div class="d-flex align-center mb-4">
          <v-icon size="32" class="mr-3">mdi-account-plus-outline</v-icon>
          <h1 class="text-h4">Profile Generator</h1>
        </div>

        <!-- Coverage Stats -->
        <v-row class="mb-4">
          <v-col cols="12" sm="6" md="3">
            <StatsCard
              icon="mdi-briefcase-outline"
              icon-color="primary"
              label="Всего позиций"
              :value="dashboardStore.stats?.positions_count || 0"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <StatsCard
              icon="mdi-account-check-outline"
              icon-color="success"
              label="Сгенерировано"
              :value="dashboardStore.stats?.profiles_count || 0"
              :progress-value="((dashboardStore.stats?.profiles_count || 0) / (dashboardStore.stats?.positions_count || 1)) * 100"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <StatsCard
              icon="mdi-chart-arc"
              icon-color="info"
              label="Покрытие"
              :value="`${(dashboardStore.stats?.completion_percentage || 0).toFixed(1)}%`"
              :progress-value="dashboardStore.stats?.completion_percentage || 0"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <StatsCard
              icon="mdi-clock-outline"
              icon-color="warning"
              label="В процессе"
              :value="dashboardStore.stats?.active_tasks_count || 0"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="isLoading">
      <v-col>
        <BaseCard>
          <v-card-text class="text-center py-12">
            <v-progress-circular indeterminate color="primary" size="64" />
            <div class="text-h6 mt-4">Loading catalog data...</div>
          </v-card-text>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-row v-else>
      <v-col>
        <BaseCard>
          <v-tabs v-model="activeTab" bg-color="surface">
            <v-tab value="search">
              <v-icon start>mdi-magnify</v-icon>
              Quick Search
            </v-tab>
            <v-tab value="tree">
              <v-icon start>mdi-file-tree-outline</v-icon>
              Browse Tree
            </v-tab>
          </v-tabs>

          <v-divider />

          <v-card-text>
            <v-window v-model="activeTab">
              <v-window-item value="search">
                <QuickSearchTab />
              </v-window-item>

              <v-window-item value="tree">
                <BrowseTreeTab />
              </v-window-item>
            </v-window>
          </v-card-text>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Active Tasks Summary -->
    <v-row v-if="generatorStore.hasPendingTasks">
      <v-col>
        <BaseCard color="info">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <v-icon class="mr-2">mdi-information-outline</v-icon>
                <span class="font-weight-medium">
                  {{ generatorStore.totalCount }} tasks active
                </span>
                <span class="ml-2 text-medium-emphasis">
                  ({{ generatorStore.completedCount }} completed,
                  {{ generatorStore.failedCount }} failed)
                </span>
              </div>
              <div>
                <v-btn
                  variant="text"
                  color="white"
                  @click="generatorStore.clearCompleted()"
                >
                  Clear Completed
                </v-btn>
              </div>
            </div>
            <v-progress-linear
              :model-value="generatorStore.progressPercentage"
              height="4"
              color="white"
              class="mt-2"
            />
          </v-card-text>
        </BaseCard>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useGeneratorStore } from '@/stores/generator'
import { useDashboardStore } from '@/stores/dashboard'
import { logger } from '@/utils/logger'
import BaseCard from '@/components/common/BaseCard.vue'
import StatsCard from '@/components/common/StatsCard.vue'
import QuickSearchTab from '@/components/generator/QuickSearchTab.vue'
import BrowseTreeTab from '@/components/generator/BrowseTreeTab.vue'

// Stores
const catalogStore = useCatalogStore()
const generatorStore = useGeneratorStore()
const dashboardStore = useDashboardStore()

// State
const activeTab = ref('search')
const isLoading = ref(true)

// Lifecycle
onMounted(async () => {
  // Load catalog data and stats on mount
  try {
    await Promise.all([
      catalogStore.loadSearchableItems(),
      dashboardStore.fetchStats()
    ])
  } catch (error: unknown) {
    logger.error('Failed to load catalog data on mount', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.v-progress-linear {
  border-radius: 4px;
}
</style>

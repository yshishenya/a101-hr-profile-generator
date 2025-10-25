<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row>
      <v-col>
        <div class="d-flex align-center mb-4">
          <v-icon size="32" class="mr-3">mdi-account-plus-outline</v-icon>
          <h1 class="text-h4">Profile Generator</h1>
        </div>

        <!-- Coverage Stats -->
        <v-card class="mb-4" color="surface-variant">
          <v-card-text>
            <v-row align="center">
              <v-col cols="12" md="3">
                <div class="text-caption text-medium-emphasis">Total Positions</div>
                <div class="text-h6">{{ catalogStore.totalPositions }}</div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="text-caption text-medium-emphasis">Profiles Created</div>
                <div class="text-h6 text-success">
                  {{ catalogStore.positionsWithProfiles }}
                </div>
              </v-col>
              <v-col cols="12" md="3">
                <div class="text-caption text-medium-emphasis">Coverage</div>
                <div class="text-h6">{{ catalogStore.coveragePercentage }}%</div>
              </v-col>
              <v-col cols="12" md="3">
                <v-progress-linear
                  :model-value="catalogStore.coveragePercentage"
                  height="8"
                  color="primary"
                  rounded
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-row>
      <v-col>
        <v-card>
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
        </v-card>
      </v-col>
    </v-row>

    <!-- Active Tasks Summary -->
    <v-row v-if="generatorStore.hasPendingTasks">
      <v-col>
        <v-card color="info">
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
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useGeneratorStore } from '@/stores/generator'
import QuickSearchTab from '@/components/generator/QuickSearchTab.vue'
import BrowseTreeTab from '@/components/generator/BrowseTreeTab.vue'

// Stores
const catalogStore = useCatalogStore()
const generatorStore = useGeneratorStore()

// State
const activeTab = ref('search')

// Lifecycle
onMounted(async () => {
  // Load catalog data on mount
  try {
    await catalogStore.loadSearchableItems()
  } catch (error) {
    console.error('Failed to load catalog data:', error)
  }
})
</script>

<style scoped>
.v-progress-linear {
  border-radius: 4px;
}
</style>

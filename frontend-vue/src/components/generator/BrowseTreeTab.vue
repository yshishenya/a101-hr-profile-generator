<template>
  <v-container fluid>
    <v-row>
      <!-- Left Column: Tree Navigation -->
      <v-col cols="12" md="7">
        <v-card flat>
          <v-card-title class="d-flex align-center justify-space-between">
            <div>
              <v-icon class="mr-2">mdi-file-tree-outline</v-icon>
              Organization Structure
            </div>

            <!-- Tree controls -->
            <div>
              <v-btn
                size="small"
                variant="text"
                @click="expandAll"
              >
                <v-icon start size="small">mdi-chevron-down</v-icon>
                Expand All
              </v-btn>

              <v-btn
                size="small"
                variant="text"
                @click="collapseAll"
              >
                <v-icon start size="small">mdi-chevron-up</v-icon>
                Collapse All
              </v-btn>

              <v-btn
                size="small"
                variant="text"
                :loading="catalogStore.isLoading"
                @click="loadTree"
              >
                <v-icon start size="small">mdi-refresh</v-icon>
                Refresh
              </v-btn>
            </div>
          </v-card-title>

          <v-divider />

          <v-card-text style="max-height: 600px; overflow-y: auto;">
            <!-- Loading state -->
            <div v-if="catalogStore.isLoading" class="text-center py-8">
              <v-progress-circular indeterminate color="primary" />
              <div class="text-body-2 mt-2">Loading organization structure...</div>
            </div>

            <!-- Tree -->
            <OrganizationTree
              v-else-if="catalogStore.organizationTree.length > 0"
              ref="treeRef"
              v-model="selectedPositions"
              :items="catalogStore.organizationTree"
              @select="handleSelectionChange"
            />

            <!-- Empty state -->
            <v-alert v-else type="info" variant="tonal">
              No organization structure available. Please contact your administrator.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column: Selection Summary and Actions -->
      <v-col cols="12" md="5">
        <v-card flat sticky style="position: sticky; top: 20px;">
          <v-card-title>
            <v-icon class="mr-2">mdi-checkbox-marked-circle</v-icon>
            Selected Positions
          </v-card-title>

          <v-divider />

          <v-card-text>
            <!-- Selection summary -->
            <v-alert
              v-if="selectedPositions.length === 0"
              type="info"
              variant="tonal"
              density="compact"
            >
              Select positions from the tree to generate profiles
            </v-alert>

            <div v-else>
              <!-- Stats -->
              <div class="mb-4">
                <v-chip
                  color="primary"
                  variant="flat"
                  class="mr-2"
                >
                  <v-icon start size="small">mdi-check-circle</v-icon>
                  {{ selectedPositions.length }} selected
                </v-chip>

                <v-chip
                  color="success"
                  variant="outlined"
                >
                  {{ positionsWithProfiles }} with profiles
                </v-chip>
              </div>

              <!-- Selected items list -->
              <div style="max-height: 200px; overflow-y: auto;" class="mb-4">
                <v-list density="compact">
                  <v-list-item
                    v-for="position in selectedPositions"
                    :key="position.position_id"
                    :title="position.position_name"
                    :subtitle="position.department_path"
                  >
                    <template #prepend>
                      <v-icon
                        size="small"
                        :color="position.profile_exists ? 'success' : 'grey'"
                      >
                        {{
                          position.profile_exists
                            ? 'mdi-check-circle'
                            : 'mdi-circle-outline'
                        }}
                      </v-icon>
                    </template>

                    <template #append>
                      <v-btn
                        icon
                        size="x-small"
                        variant="text"
                        @click="removeSelection(position)"
                      >
                        <v-icon size="small">mdi-close</v-icon>
                      </v-btn>
                    </template>
                  </v-list-item>
                </v-list>
              </div>

              <!-- Actions -->
              <div class="d-flex flex-column gap-2">
                <v-btn
                  color="primary"
                  size="large"
                  block
                  :loading="isGenerating"
                  :disabled="selectedPositions.length === 0"
                  @click="handleBulkGenerate"
                >
                  <v-icon start>mdi-rocket-launch</v-icon>
                  Generate {{ selectedPositions.length }} Profile{{ selectedPositions.length !== 1 ? 's' : '' }}
                </v-btn>

                <v-btn
                  variant="outlined"
                  block
                  @click="clearSelection"
                >
                  Clear Selection
                </v-btn>
              </div>

              <!-- Info message -->
              <v-alert
                v-if="positionsWithProfiles > 0"
                type="warning"
                variant="tonal"
                density="compact"
                class="mt-4"
              >
                {{ positionsWithProfiles }} position{{ positionsWithProfiles !== 1 ? 's' : '' }} already have profiles.
                New profiles will be created without affecting existing ones.
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Bulk Progress Tracker -->
    <v-dialog v-model="showBulkProgress" persistent max-width="700">
      <BaseCard>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-progress-check</v-icon>
          Bulk Generation Progress
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-6">
          <div class="mb-4">
            <div class="d-flex justify-space-between align-center mb-2">
              <span class="text-body-2">Overall Progress</span>
              <span class="text-body-2 font-weight-bold">
                {{ generatorStore.completedCount + generatorStore.failedCount }}/{{ generatorStore.totalCount }}
              </span>
            </div>

            <v-progress-linear
              :model-value="generatorStore.progressPercentage"
              color="primary"
              height="8"
              rounded
            />
          </div>

          <!-- Task list -->
          <div style="max-height: 300px; overflow-y: auto;">
            <v-list density="compact">
              <v-list-item
                v-for="task in bulkTasks"
                :key="task.task_id"
                :title="task.position_name"
                :subtitle="`${task.status} - ${task.progress || 0}%`"
              >
                <template #prepend>
                  <v-icon :color="getTaskStatusColor(task.status)">
                    {{ getTaskStatusIcon(task.status) }}
                  </v-icon>
                </template>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-spacer />
          <v-btn
            v-if="!generatorStore.hasPendingTasks"
            color="primary"
            @click="handleBulkComplete"
          >
            Done
          </v-btn>
        </v-card-actions>
      </BaseCard>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useGeneratorStore } from '@/stores/generator'
import { useTaskStatus } from '@/composables/useTaskStatus'
import { logger } from '@/utils/logger'
import type { SearchableItem } from '@/stores/catalog'
import BaseCard from '@/components/common/BaseCard.vue'
import OrganizationTree from './OrganizationTree.vue'

// Constants
const POLL_INTERVAL_MS = 2000 // Poll every 2 seconds

// Composables
const catalogStore = useCatalogStore()
const generatorStore = useGeneratorStore()
const { getTaskStatusColor, getTaskStatusIcon } = useTaskStatus()

// Refs
const treeRef = ref<InstanceType<typeof OrganizationTree> | null>(null)

// State
const selectedPositions = ref<SearchableItem[]>([])
const isGenerating = ref(false)
const showBulkProgress = ref(false)

// Computed
const positionsWithProfiles = computed(() => {
  return selectedPositions.value.filter(p => p.profile_exists).length
})

const bulkTasks = computed(() => {
  return Array.from(generatorStore.activeTasks.values())
    .sort((a, b) => b.created_at.getTime() - a.created_at.getTime())
})

// Lifecycle
onMounted(async () => {
  await loadTree()
})

// Methods
async function loadTree(): Promise<void> {
  try {
    await catalogStore.loadOrganizationTree()
  } catch (error: unknown) {
    logger.error('Failed to load organization tree for browse view', error)
  }
}

function expandAll(): void {
  treeRef.value?.expandAll()
}

function collapseAll(): void {
  treeRef.value?.collapseAll()
}

function handleSelectionChange(items: SearchableItem[]): void {
  selectedPositions.value = items
}

function removeSelection(position: SearchableItem): void {
  selectedPositions.value = selectedPositions.value.filter(
    p => p.position_id !== position.position_id
  )
}

function clearSelection(): void {
  selectedPositions.value = []
}

async function handleBulkGenerate(): Promise<void> {
  if (selectedPositions.value.length === 0) return

  isGenerating.value = true
  showBulkProgress.value = true

  try {
    await generatorStore.startBulkGeneration(selectedPositions.value)

    // Start polling for all tasks
    const pollInterval = setInterval(() => {
      if (!generatorStore.hasPendingTasks) {
        clearInterval(pollInterval)
        isGenerating.value = false
      }
    }, POLL_INTERVAL_MS)
  } catch (error: unknown) {
    logger.error('Failed to start bulk generation', error)
    // TODO(developer): Replace alert() with toast notification system (Week 8)
    const message = error instanceof Error ? error.message : 'Unknown error'
    alert(`Failed to start bulk generation: ${message}`)
    isGenerating.value = false
    showBulkProgress.value = false
  }
}

function handleBulkComplete(): void {
  showBulkProgress.value = false
  clearSelection()
  generatorStore.clearCompleted()

  // Refresh tree to show updated coverage
  loadTree()
}
</script>

<style scoped>
.mdi-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.gap-2 {
  gap: 0.5rem;
}
</style>

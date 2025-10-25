<template>
  <v-container fluid>
    <v-row>
      <!-- Left Column: Search and Form -->
      <v-col cols="12" md="6">
        <v-card flat class="pa-4">
          <v-card-title class="text-h6 pa-0 mb-4">
            Quick Search
          </v-card-title>

          <v-card-text class="pa-0">
            <!-- Step 1: Search -->
            <div class="mb-6">
              <div class="text-subtitle-2 mb-2">Step 1: Find Position</div>
              <PositionSearchAutocomplete
                v-model="selectedPosition"
                @select="handlePositionSelect"
              />

              <!-- Selected position info -->
              <v-alert
                v-if="selectedPosition"
                type="info"
                variant="tonal"
                class="mt-4"
                density="compact"
              >
                <div class="text-subtitle-2">Selected Position</div>
                <div class="text-body-2">{{ selectedPosition.position_name }}</div>
                <div class="text-caption">{{ selectedPosition.department_path }}</div>

                <v-chip
                  v-if="selectedPosition.profile_exists"
                  size="small"
                  color="success"
                  class="mt-2"
                >
                  <v-icon start size="small">mdi-check-circle</v-icon>
                  Profile already exists (ID: {{ selectedPosition.profile_id }})
                </v-chip>
              </v-alert>
            </div>

            <!-- Step 2: Configuration -->
            <div v-if="selectedPosition" class="mb-6">
              <GenerationForm
                v-model:temperature="temperature"
                v-model:employee-name="employeeName"
              />
            </div>

            <!-- Step 3: Generate -->
            <div v-if="selectedPosition">
              <v-btn
                :loading="isGenerating"
                :disabled="!canGenerate"
                color="primary"
                size="large"
                block
                @click="handleGenerate"
              >
                <v-icon start>mdi-rocket-launch</v-icon>
                {{ selectedPosition.profile_exists ? 'Regenerate Profile' : 'Generate Profile' }}
              </v-btn>

              <div v-if="selectedPosition.profile_exists" class="text-caption text-center mt-2 text-warning">
                Warning: This will create a new profile. The existing one will remain unchanged.
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column: Tips and Recent Activity -->
      <v-col cols="12" md="6">
        <v-card flat class="pa-4">
          <v-card-title class="text-h6 pa-0 mb-4">
            Tips & Recent Activity
          </v-card-title>

          <v-card-text class="pa-0">
            <!-- Tips -->
            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mb-4"
            >
              <div class="text-subtitle-2 mb-2">💡 Quick Tips</div>
              <ul class="text-body-2 pl-4">
                <li>Use fuzzy search - try abbreviations or partial names</li>
                <li>Positions without profiles are prioritized in results</li>
                <li>Generation typically takes 15-30 seconds</li>
                <li>You can adjust temperature for more creative profiles</li>
              </ul>
            </v-alert>

            <!-- Recent generations -->
            <div v-if="recentTasks.length > 0">
              <div class="text-subtitle-2 mb-2">Recent Generations</div>

              <v-list density="compact">
                <v-list-item
                  v-for="task in recentTasks"
                  :key="task.task_id"
                  :title="task.position_name"
                  :subtitle="task.business_unit_name"
                >
                  <template #prepend>
                    <v-icon :color="getTaskStatusColor(task.status)">
                      {{ getTaskStatusIcon(task.status) }}
                    </v-icon>
                  </template>

                  <template #append>
                    <v-chip
                      :color="getTaskStatusColor(task.status)"
                      size="small"
                      variant="flat"
                    >
                      {{ task.status }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </div>

            <!-- Empty state -->
            <v-alert
              v-else
              type="info"
              variant="tonal"
              density="compact"
            >
              No recent generations. Start by searching for a position above.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Progress Tracker Dialog -->
    <GenerationProgressTracker
      v-if="currentTaskId"
      :task-id="currentTaskId"
      @complete="handleGenerationComplete"
      @error="handleGenerationError"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { useTaskStatus } from '@/composables/useTaskStatus'
import type { SearchableItem } from '@/stores/catalog'
import type { GenerationResult } from '@/stores/generator'
import PositionSearchAutocomplete from './PositionSearchAutocomplete.vue'
import GenerationForm from './GenerationForm.vue'
import GenerationProgressTracker from './GenerationProgressTracker.vue'

// Constants
const DEFAULT_TEMPERATURE = 0.7

// Composables
const generatorStore = useGeneratorStore()
const { getTaskStatusColor, getTaskStatusIcon } = useTaskStatus()

// State
const selectedPosition = ref<SearchableItem | null>(null)
const temperature = ref<number>(DEFAULT_TEMPERATURE)
const employeeName = ref<string>('')
const isGenerating = ref<boolean>(false)
const currentTaskId = ref<string | null>(null)

// Computed
const canGenerate = computed(() => {
  return selectedPosition.value !== null && !isGenerating.value
})

const recentTasks = computed(() => {
  const tasks = Array.from(generatorStore.activeTasks.values())
  return tasks
    .sort((a, b) => b.created_at.getTime() - a.created_at.getTime())
    .slice(0, 5)
})

// Methods
function handlePositionSelect(position: SearchableItem): void {
  selectedPosition.value = position
  generatorStore.setSelectedPosition(position)
}

async function handleGenerate(): Promise<void> {
  if (!selectedPosition.value) return

  isGenerating.value = true

  try {
    const taskId = await generatorStore.startGeneration({
      position_id: selectedPosition.value.position_id,
      position_name: selectedPosition.value.position_name,
      business_unit_name: selectedPosition.value.business_unit_name,
      temperature: temperature.value,
      employee_name: employeeName.value || undefined
    })

    currentTaskId.value = taskId
  } catch (error: any) {
    console.error('Failed to start generation:', error)
    // Show error notification (TODO: add notification system)
    alert(`Failed to start generation: ${error.message}`)
  } finally {
    isGenerating.value = false
  }
}

function handleGenerationComplete(result: GenerationResult): void {
  currentTaskId.value = null
  isGenerating.value = false

  if (import.meta.env.DEV) {
    console.log('Generation completed:', result)
  }

  // TODO(developer): Replace with toast notification system (Week 8)
  // For now, rely on the progress tracker dialog for user feedback

  // Reset form for next generation
  selectedPosition.value = null
  employeeName.value = ''
}

function handleGenerationError(error: string): void {
  currentTaskId.value = null
  isGenerating.value = false

  if (import.meta.env.DEV) {
    console.error('Generation error:', error)
  }

  // TODO(developer): Replace alert() with toast notification system (Week 8)
  alert(`Generation failed: ${error}`)
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
</style>

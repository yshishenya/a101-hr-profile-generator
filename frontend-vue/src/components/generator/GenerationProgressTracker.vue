<template>
  <v-dialog v-model="dialog" persistent max-width="600">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2" :color="statusColor">{{ statusIcon }}</v-icon>
        <span>{{ dialogTitle }}</span>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-6">
        <!-- Progress Information -->
        <div v-if="task">
          <div class="mb-4">
            <div class="text-subtitle-2 mb-1">Position</div>
            <div class="text-body-1 font-weight-medium">{{ task.position_name }}</div>
            <div class="text-caption text-medium-emphasis">{{ task.business_unit_name }}</div>
          </div>

          <!-- Progress Bar -->
          <div class="mb-4">
            <div class="d-flex justify-space-between align-center mb-2">
              <span class="text-body-2">Progress</span>
              <span class="text-body-2 font-weight-bold">{{ task.progress || 0 }}%</span>
            </div>

            <v-progress-linear
              :model-value="task.progress || 0"
              :color="progressColor"
              :indeterminate="task.status === 'queued'"
              height="8"
              rounded
            />
          </div>

          <!-- Current Step -->
          <div v-if="task.current_step" class="mb-4">
            <v-alert
              :type="alertType"
              variant="tonal"
              density="compact"
            >
              <div class="text-body-2">
                <v-icon size="small" class="mr-1">{{ stepIcon }}</v-icon>
                {{ task.current_step }}
              </div>
            </v-alert>
          </div>

          <!-- Timing Information -->
          <div class="d-flex justify-space-between text-caption text-medium-emphasis mb-4">
            <div>
              <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
              Elapsed: {{ elapsedTime }}s
            </div>
            <div v-if="task.estimated_duration">
              Est. total: {{ task.estimated_duration }}s
            </div>
          </div>

          <!-- Error Message -->
          <v-alert
            v-if="task.status === 'failed' && task.error"
            type="error"
            variant="tonal"
            class="mb-4"
          >
            <div class="text-subtitle-2 mb-1">Error Details</div>
            <div class="text-body-2">{{ task.error }}</div>
          </v-alert>

          <!-- Completion Message -->
          <v-alert
            v-if="task.status === 'completed'"
            type="success"
            variant="tonal"
            class="mb-4"
          >
            <div class="text-subtitle-2 mb-1">✅ Profile Generated Successfully!</div>
            <div class="text-body-2">The profile has been created and saved to the database.</div>
          </v-alert>
        </div>

        <!-- Loading state -->
        <div v-else class="text-center py-4">
          <v-progress-circular indeterminate color="primary" />
          <div class="text-body-2 mt-2">Loading task information...</div>
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />

        <!-- Cancel button (only when processing) -->
        <v-btn
          v-if="canCancel"
          variant="text"
          color="error"
          @click="handleCancel"
        >
          Cancel
        </v-btn>

        <!-- Close button (when completed or failed) -->
        <v-btn
          v-if="canClose"
          variant="text"
          color="primary"
          @click="handleClose"
        >
          {{ task?.status === 'completed' ? 'View Profile' : 'Close' }}
        </v-btn>

        <v-btn
          v-if="canClose"
          variant="flat"
          color="primary"
          @click="handleDismiss"
        >
          Dismiss
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import type { GenerationTask, GenerationResult } from '@/stores/generator'

// Constants
const POLL_INTERVAL_MS = 2000 // Poll every 2 seconds

// Props
interface Props {
  taskId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'complete': [result: GenerationResult]
  'error': [error: string]
  'cancel': []
}>()

// Store
const generatorStore = useGeneratorStore()

// State
const dialog = ref(true)
const elapsedTime = ref(0)
const pollInterval = ref<number | null>(null)

// Computed
const task = computed((): GenerationTask | undefined => {
  return generatorStore.activeTasks.get(props.taskId)
})

const dialogTitle = computed(() => {
  if (!task.value) return 'Loading...'

  switch (task.value.status) {
    case 'queued':
      return 'Queued for Generation'
    case 'processing':
      return 'Generating Profile'
    case 'completed':
      return 'Generation Complete'
    case 'failed':
      return 'Generation Failed'
    default:
      return 'Profile Generation'
  }
})

const statusColor = computed(() => {
  if (!task.value) return 'grey'

  switch (task.value.status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'processing':
      return 'primary'
    case 'queued':
      return 'info'
    default:
      return 'grey'
  }
})

const statusIcon = computed(() => {
  if (!task.value) return 'mdi-help-circle'

  switch (task.value.status) {
    case 'completed':
      return 'mdi-check-circle'
    case 'failed':
      return 'mdi-alert-circle'
    case 'processing':
      return 'mdi-sync mdi-spin'
    case 'queued':
      return 'mdi-clock-outline'
    default:
      return 'mdi-help-circle'
  }
})

const progressColor = computed(() => {
  if (!task.value) return 'grey'

  switch (task.value.status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'processing':
      return 'primary'
    default:
      return 'info'
  }
})

const alertType = computed<'info' | 'success' | 'warning' | 'error'>(() => {
  if (!task.value) return 'info'

  switch (task.value.status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'processing':
      return 'info'
    default:
      return 'info'
  }
})

const stepIcon = computed(() => {
  if (!task.value) return 'mdi-information'
  return task.value.status === 'processing' ? 'mdi-loading mdi-spin' : 'mdi-information'
})

const canCancel = computed(() => {
  return task.value?.status === 'queued' || task.value?.status === 'processing'
})

const canClose = computed(() => {
  return task.value?.status === 'completed' || task.value?.status === 'failed'
})

// Watch for task status changes
watch(
  () => task.value?.status,
  (newStatus) => {
    if (newStatus === 'completed' && task.value?.result) {
      emit('complete', task.value.result)
    } else if (newStatus === 'failed' && task.value?.error) {
      emit('error', task.value.error)
    }
  }
)

// Start polling on mount
function startPolling(): void {
  pollInterval.value = window.setInterval(async () => {
    if (task.value?.status === 'processing' || task.value?.status === 'queued') {
      await generatorStore.pollTaskStatus(props.taskId)
      elapsedTime.value++
    } else if (canClose.value) {
      stopPolling()
    }
  }, POLL_INTERVAL_MS)

  // Initial poll
  generatorStore.pollTaskStatus(props.taskId)
}

function stopPolling(): void {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

// Start polling immediately
startPolling()

// Watch dialog close and stop polling
watch(dialog, (newValue) => {
  if (!newValue) {
    stopPolling()
  }
})

// Cleanup before unmount (prevents race condition with interval)
onBeforeUnmount(() => {
  stopPolling()
})

// Methods
async function handleCancel(): Promise<void> {
  try {
    await generatorStore.cancelTask(props.taskId)
    emit('cancel')
    dialog.value = false
  } catch (error) {
    console.error('Failed to cancel task:', error)
  }
}

function handleClose(): void {
  if (task.value?.status === 'completed' && task.value.result) {
    // TODO(developer): Implement profile view navigation once ProfileView is created (Week 5)
    // Will navigate to profile detail page: router.push(`/profiles/${task.value.result.profile_id}`)
    if (import.meta.env.DEV) {
      console.log('Navigate to profile:', task.value.result)
    }
  }
  dialog.value = false
}

function handleDismiss(): void {
  dialog.value = false
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

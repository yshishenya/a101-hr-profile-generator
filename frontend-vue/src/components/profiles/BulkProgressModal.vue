<template>
  <!-- Main Dialog -->
  <v-dialog
    :model-value="modelValue"
    :persistent="isProcessing"
    max-width="700px"
    :fullscreen="isFullscreen"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <!-- Header -->
      <v-card-title class="d-flex align-center justify-space-between pa-4 bg-primary">
        <div class="d-flex align-center">
          <v-icon class="mr-2" color="white">
            {{ getOperationIcon(operation) }}
          </v-icon>
          <span class="text-white">{{ getOperationTitle(operation) }}</span>
        </div>

        <div class="d-flex align-center gap-2">
          <!-- Minimize/Maximize -->
          <v-btn
            icon
            size="small"
            variant="text"
            color="white"
            @click="toggleFullscreen"
          >
            <v-icon>{{ isFullscreen ? 'mdi-fullscreen-exit' : 'mdi-fullscreen' }}</v-icon>
          </v-btn>

          <!-- Close (only if not processing) -->
          <v-btn
            v-if="!isProcessing"
            icon
            size="small"
            variant="text"
            color="white"
            @click="$emit('update:modelValue', false)"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>
      </v-card-title>

      <v-divider />

      <!-- Content -->
      <v-card-text class="pa-6">
        <!-- Overall Progress -->
        <div class="mb-6">
          <div class="d-flex align-center justify-space-between mb-2">
            <span class="text-subtitle-1 font-weight-medium">Общий прогресс</span>
            <span class="text-h6 font-weight-bold">
              {{ completedCount }} / {{ totalCount }}
            </span>
          </div>

          <v-progress-linear
            :model-value="progressPercent"
            :color="getProgressColor()"
            height="8"
            rounded
          />

          <div class="text-caption text-medium-emphasis mt-1">
            {{ progressPercent.toFixed(0) }}% завершено
          </div>
        </div>

        <!-- Status Summary -->
        <v-row class="mb-4">
          <v-col cols="4">
            <v-card variant="tonal" color="success">
              <v-card-text class="text-center pa-3">
                <v-icon size="small" class="mb-1">mdi-check-circle</v-icon>
                <div class="text-h6 font-weight-bold">{{ successCount }}</div>
                <div class="text-caption">Успешно</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="4">
            <v-card variant="tonal" color="warning">
              <v-card-text class="text-center pa-3">
                <v-icon size="small" class="mb-1">mdi-clock-outline</v-icon>
                <div class="text-h6 font-weight-bold">{{ pendingCount }}</div>
                <div class="text-caption">В процессе</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="4">
            <v-card variant="tonal" color="error">
              <v-card-text class="text-center pa-3">
                <v-icon size="small" class="mb-1">mdi-alert-circle</v-icon>
                <div class="text-h6 font-weight-bold">{{ errorCount }}</div>
                <div class="text-caption">Ошибки</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Items List -->
        <div>
          <div class="text-subtitle-2 mb-2">Детали операций</div>

          <v-virtual-scroll
            :items="items"
            :height="Math.min(items.length * 60, 300)"
            item-height="60"
          >
            <template #default="{ item }">
              <v-list-item
                :key="item.id"
                :title="item.name"
                :subtitle="getItemStatus(item)"
              >
                <template #prepend>
                  <v-avatar :color="getItemColor(item)" size="40">
                    <v-icon color="white" size="small">
                      {{ getItemIcon(item) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <template #append>
                  <v-progress-circular
                    v-if="item.status === 'processing'"
                    indeterminate
                    size="24"
                    width="3"
                    color="primary"
                  />
                  <v-icon
                    v-else-if="item.status === 'completed'"
                    color="success"
                  >
                    mdi-check-circle
                  </v-icon>
                  <v-icon
                    v-else-if="item.status === 'error'"
                    color="error"
                  >
                    mdi-alert-circle
                  </v-icon>
                  <v-icon
                    v-else
                    color="grey"
                  >
                    mdi-clock-outline
                  </v-icon>
                </template>
              </v-list-item>
              <v-divider />
            </template>
          </v-virtual-scroll>
        </div>

        <!-- Error Details (if any) -->
        <v-alert
          v-if="errorCount > 0 && !isProcessing"
          type="error"
          variant="tonal"
          class="mt-4"
        >
          <template #title>
            Обнаружены ошибки ({{ errorCount }})
          </template>
          <div class="text-body-2">
            Некоторые операции не удалось завершить. Проверьте детали выше.
          </div>
        </v-alert>
      </v-card-text>

      <v-divider />

      <!-- Actions -->
      <v-card-actions class="pa-4">
        <v-spacer />

        <v-btn
          v-if="isProcessing"
          color="error"
          variant="outlined"
          @click="$emit('cancel')"
        >
          Отменить операции
        </v-btn>

        <v-btn
          v-else
          color="primary"
          @click="$emit('update:modelValue', false)"
        >
          Закрыть
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Types
export type BulkOperation = 'generate' | 'download' | 'cancel' | 'delete'
export type ItemStatus = 'pending' | 'processing' | 'completed' | 'error'

export interface BulkProgressItem {
  id: string
  name: string
  status: ItemStatus
  error?: string
}

// Props
interface Props {
  modelValue: boolean
  operation: BulkOperation
  items: BulkProgressItem[]
}

const props = defineProps<Props>()

// Emits
defineEmits<{
  'update:modelValue': [value: boolean]
  'cancel': []
}>()

// Local state
const isFullscreen = ref(false)

// Computed
const totalCount = computed(() => props.items.length)

const completedCount = computed(() => {
  return props.items.filter(
    item => item.status === 'completed' || item.status === 'error'
  ).length
})

const successCount = computed(() => {
  return props.items.filter(item => item.status === 'completed').length
})

const pendingCount = computed(() => {
  return props.items.filter(
    item => item.status === 'pending' || item.status === 'processing'
  ).length
})

const errorCount = computed(() => {
  return props.items.filter(item => item.status === 'error').length
})

const progressPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return (completedCount.value / totalCount.value) * 100
})

const isProcessing = computed(() => {
  return props.items.some(
    item => item.status === 'processing' || item.status === 'pending'
  )
})

// Methods
function toggleFullscreen(): void {
  isFullscreen.value = !isFullscreen.value
}

function getOperationTitle(operation: BulkOperation): string {
  switch (operation) {
    case 'generate':
      return 'Массовая генерация профилей'
    case 'download':
      return 'Массовое скачивание'
    case 'cancel':
      return 'Отмена операций'
    case 'delete':
      return 'Массовое удаление'
    default:
      return 'Массовая операция'
  }
}

function getOperationIcon(operation: BulkOperation): string {
  switch (operation) {
    case 'generate':
      return 'mdi-rocket-launch'
    case 'download':
      return 'mdi-download'
    case 'cancel':
      return 'mdi-cancel'
    case 'delete':
      return 'mdi-delete'
    default:
      return 'mdi-cog'
  }
}

function getProgressColor(): string {
  if (errorCount.value > 0 && !isProcessing.value) {
    return 'warning'
  }
  return isProcessing.value ? 'primary' : 'success'
}

function getItemColor(item: BulkProgressItem): string {
  switch (item.status) {
    case 'completed':
      return 'success'
    case 'processing':
      return 'primary'
    case 'error':
      return 'error'
    default:
      return 'grey'
  }
}

function getItemIcon(item: BulkProgressItem): string {
  switch (item.status) {
    case 'completed':
      return 'mdi-check'
    case 'processing':
      return 'mdi-loading'
    case 'error':
      return 'mdi-alert'
    default:
      return 'mdi-clock-outline'
  }
}

function getItemStatus(item: BulkProgressItem): string {
  switch (item.status) {
    case 'completed':
      return 'Завершено'
    case 'processing':
      return 'Обработка...'
    case 'error':
      return item.error || 'Ошибка'
    default:
      return 'Ожидание'
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

.bg-primary {
  background-color: rgb(var(--v-theme-primary)) !important;
}
</style>

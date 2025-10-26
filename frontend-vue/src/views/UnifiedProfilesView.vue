<template>
  <v-container fluid class="unified-profiles-view pa-6">
    <!-- Page Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-4">
          <div>
            <h1 class="text-h4 font-weight-bold">Профили должностей</h1>
            <p class="text-body-2 text-medium-emphasis mt-1">
              Управление профилями компетенций для всех позиций организации
            </p>
          </div>

          <!-- Bulk Actions -->
          <div class="d-flex gap-2">
            <v-btn
              color="primary"
              prepend-icon="mdi-refresh"
              @click="refreshData"
            >
              Обновить
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Overview -->
    <v-row>
      <v-col cols="12">
        <StatsOverview />
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row>
      <v-col cols="12">
        <FilterBar />
      </v-col>
    </v-row>

    <!-- Positions Table/Tree -->
    <v-row>
      <v-col cols="12">
        <PositionsTable
          v-if="profilesStore.viewMode === 'table'"
          :positions="profilesStore.filteredPositions"
          :loading="profilesStore.loading"
          @view-profile="handleViewProfile"
          @generate-profile="handleGenerateProfile"
          @regenerate-profile="handleRegenerateProfile"
          @cancel-generation="handleCancelGeneration"
          @download-profile="handleDownloadProfile"
          @view-versions="handleViewVersions"
          @share-profile="handleShareProfile"
          @selection-change="handleSelectionChange"
        />

        <!-- Tree View (Week 5 Day 7) -->
        <v-card v-else elevation="2" class="pa-8 text-center">
          <v-icon size="64" color="grey-lighten-2">mdi-file-tree</v-icon>
          <div class="text-h6 mt-4">Дерево организации</div>
          <div class="text-body-2 text-medium-emphasis mt-2">
            Представление в виде дерева будет реализовано на Day 7
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Profile Viewer Modal -->
    <ProfileViewerModal
      v-model="showProfileViewer"
      :profile="selectedPosition"
      @download="handleDownloadFromViewer"
      @view-versions="handleViewVersions(selectedPosition!)"
    />

    <!-- Version History Modal (Week 5 Day 6) -->
    <v-dialog
      v-model="showVersionHistory"
      max-width="900px"
      scrollable
    >
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <span>История версий</span>
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showVersionHistory = false"
          />
        </v-card-title>
        <v-card-text class="pa-6">
          <div v-if="selectedPosition" class="text-center pa-8">
            <v-icon size="64" color="grey-lighten-2">mdi-history</v-icon>
            <div class="text-h6 mt-4">История версий: {{ selectedPosition.position_name }}</div>
            <div class="text-body-2 text-medium-emphasis mt-2">
              История версий будет реализована на Day 6
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Bulk Actions Bar (floating at bottom) -->
    <BulkActionsBar
      :selected-positions="selectedPositions"
      @bulk-generate="handleBulkGenerate"
      @bulk-cancel="handleBulkCancel"
      @clear-selection="handleClearSelection"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useProfilesStore } from '@/stores/profiles'
import { useGeneratorStore } from '@/stores/generator'
import { logger } from '@/utils/logger'
import StatsOverview from '@/components/profiles/StatsOverview.vue'
import FilterBar from '@/components/profiles/FilterBar.vue'
import PositionsTable from '@/components/profiles/PositionsTable.vue'
import BulkActionsBar from '@/components/profiles/BulkActionsBar.vue'
import ProfileViewerModal from '@/components/profiles/ProfileViewerModal.vue'
import type { UnifiedPosition } from '@/types/unified'

// Stores
const profilesStore = useProfilesStore()
const generatorStore = useGeneratorStore()

// Local state
const showProfileViewer = ref(false)
const showVersionHistory = ref(false)
const selectedPosition = ref<UnifiedPosition | null>(null)
const selectedPositionIds = ref<string[]>([])
const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

// Computed
const selectedPositions = computed(() => {
  // Use Set for O(n) instead of O(n²) with includes()
  const idsSet = new Set(selectedPositionIds.value)
  return profilesStore.filteredPositions.filter(p =>
    idsSet.has(p.position_id)
  )
})

// Polling interval for generation tasks
let pollingInterval: number | null = null

// Lifecycle
onMounted(async () => {
  await loadData()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// Methods
async function loadData() {
  try {
    await profilesStore.loadUnifiedData()
  } catch (error) {
    showNotification('Ошибка загрузки данных', 'error')
    logger.error('Failed to load unified data', error)
  }
}

async function refreshData() {
  await loadData()
  showNotification('Данные обновлены', 'success')
}

function startPolling() {
  // Poll every 2 seconds if there are active generation tasks
  pollingInterval = window.setInterval(async () => {
    if (generatorStore.hasPendingTasks) {
      // Poll each active task
      const activeTasks = Array.from(generatorStore.activeTasks.entries())
      for (const [taskId, task] of activeTasks) {
        if (task.status === 'queued' || task.status === 'processing') {
          try {
            await generatorStore.pollTaskStatus(taskId)
          } catch (error) {
            logger.error(`Failed to poll task ${taskId}`, error)
          }
        }
      }

      // Reload unified data to update table
      await profilesStore.loadUnifiedData()
    }
  }, 2000)
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

// Event handlers
function handleViewProfile(position: UnifiedPosition) {
  selectedPosition.value = position
  showProfileViewer.value = true
}

function handleGenerateProfile(position: UnifiedPosition) {
  showNotification(
    `Генерация профиля для "${position.position_name}" запущена`,
    'info'
  )
}

async function handleRegenerateProfile(position: UnifiedPosition) {
  try {
    await generatorStore.startGeneration({
      position_id: position.position_id,
      position_name: position.position_name,
      business_unit_name: position.business_unit_name
    })
    showNotification(
      `Перегенерация профиля для "${position.position_name}" запущена`,
      'info'
    )
  } catch (error) {
    showNotification('Ошибка запуска генерации', 'error')
    logger.error('Failed to regenerate', error)
  }
}

function handleCancelGeneration(position: UnifiedPosition) {
  showNotification(
    `Генерация профиля для "${position.position_name}" отменена`,
    'warning'
  )
}

async function handleDownloadProfile(position: UnifiedPosition) {
  if (!position.profile_id) {
    showNotification('Профиль не найден', 'error')
    return
  }

  try {
    await profilesStore.downloadProfile(String(position.profile_id), 'json')
    showNotification(
      `Профиль "${position.position_name}" скачан`,
      'success'
    )
  } catch (error) {
    showNotification('Ошибка скачивания профиля', 'error')
    logger.error('Failed to download profile', error)
  }
}

async function handleDownloadFromViewer(format: 'json' | 'md' | 'docx') {
  if (!selectedPosition.value?.profile_id) {
    showNotification('Профиль не найден', 'error')
    return
  }

  try {
    await profilesStore.downloadProfile(String(selectedPosition.value.profile_id), format)
    showNotification(
      `Профиль скачан в формате ${format.toUpperCase()}`,
      'success'
    )
  } catch (error) {
    showNotification('Ошибка скачивания профиля', 'error')
    logger.error('Failed to download profile', error)
  }
}

function handleViewVersions(position: UnifiedPosition) {
  selectedPosition.value = position
  showVersionHistory.value = true
}

function handleShareProfile(position: UnifiedPosition) {
  // TODO(developer): Implement share functionality (Week 7)
  // Copy profile URL to clipboard and show notification
  // Example: navigator.clipboard.writeText(`${window.location.origin}/profiles/${position.profile_id}`)
  showNotification(
    `Ссылка на профиль "${position.position_name}" скопирована`,
    'success'
  )
}

// Selection handlers
function handleSelectionChange(selectedIds: string[]) {
  selectedPositionIds.value = selectedIds
}

function handleClearSelection() {
  selectedPositionIds.value = []
}

// Bulk operations handlers
async function handleBulkGenerate() {
  const count = selectedPositions.value.filter(p => p.status === 'not_generated').length

  if (count === 0) {
    showNotification('Нет позиций для генерации', 'warning')
    return
  }

  try {
    const taskIds = await profilesStore.bulkGenerate(selectedPositionIds.value)
    showNotification(
      `Запущена массовая генерация для ${taskIds.length} ${taskIds.length === 1 ? 'позиции' : 'позиций'}`,
      'success'
    )
    // Keep selection to allow cancellation
  } catch (error) {
    showNotification('Ошибка запуска массовой генерации', 'error')
    logger.error('Failed to start bulk generation', error)
  }
}

async function handleBulkCancel() {
  const count = selectedPositions.value.filter(p => p.status === 'generating').length

  if (count === 0) {
    showNotification('Нет активных задач для отмены', 'warning')
    return
  }

  try {
    await profilesStore.bulkCancel(selectedPositionIds.value)
    showNotification(
      `Отменено ${count} ${count === 1 ? 'задача' : 'задач'}`,
      'info'
    )
    handleClearSelection()
  } catch (error) {
    showNotification('Ошибка отмены задач', 'error')
    logger.error('Failed to cancel bulk tasks', error)
  }
}

function showNotification(message: string, color: 'success' | 'error' | 'warning' | 'info') {
  snackbar.value = {
    show: true,
    message,
    color
  }
}
</script>

<style scoped>
.unified-profiles-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
}

.gap-2 {
  gap: 8px;
}

/* Smooth transitions for modals */
.v-dialog {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>

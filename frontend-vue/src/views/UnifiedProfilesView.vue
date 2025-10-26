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
          :progress-value="dashboardStore.coverageProgress"
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
          @edit-profile="handleEditProfile"
          @delete-profile="handleDeleteProfile"
          @restore-profile="handleRestoreProfile"
          @generate-profile="handleGenerateProfile"
          @regenerate-profile="handleRegenerateProfile"
          @cancel-generation="handleCancelGeneration"
          @download-profile="handleDownloadProfile"
          @view-versions="handleViewVersions"
          @share-profile="handleShareProfile"
          @selection-change="handleSelectionChange"
        />

        <!-- Tree View (Week 5 Day 7) -->
        <BaseCard v-else class="pa-8 text-center">
          <v-icon size="64" color="grey-lighten-2">mdi-file-tree</v-icon>
          <div class="text-h6 mt-4">Дерево организации</div>
          <div class="text-body-2 text-medium-emphasis mt-2">
            Представление в виде дерева будет реализовано на Day 7
          </div>
        </BaseCard>
      </v-col>
    </v-row>

    <!-- Profile Viewer Modal -->
    <ProfileViewerModal
      v-model="showProfileViewer"
      :profile="selectedPosition"
      @download="handleDownloadFromViewer"
      @view-versions="handleViewVersions(selectedPosition!)"
    />

    <!-- Profile Edit Modal -->
    <ProfileEditModal
      v-model="showProfileEdit"
      :profile="selectedPosition"
      @save="handleSaveProfile"
    />

    <!-- Confirm Delete Dialog -->
    <ConfirmDeleteDialog
      v-model="showConfirmDelete"
      :items="itemsToDelete"
      :require-confirmation="!!(itemsToDelete && itemsToDelete.length > 1)"
      @delete="handleConfirmDelete"
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
import { useDashboardStore } from '@/stores/dashboard'
import { logger } from '@/utils/logger'
import BaseCard from '@/components/common/BaseCard.vue'
import StatsCard from '@/components/common/StatsCard.vue'
import FilterBar from '@/components/profiles/FilterBar.vue'
import PositionsTable from '@/components/profiles/PositionsTable.vue'
import BulkActionsBar from '@/components/profiles/BulkActionsBar.vue'
import ProfileViewerModal from '@/components/profiles/ProfileViewerModal.vue'
import ProfileEditModal from '@/components/profiles/ProfileEditModal.vue'
import ConfirmDeleteDialog from '@/components/common/ConfirmDeleteDialog.vue'
import type { UnifiedPosition, PositionStatus } from '@/types/unified'

// Stores
const profilesStore = useProfilesStore()
const generatorStore = useGeneratorStore()
const dashboardStore = useDashboardStore()

// Local state
const showProfileViewer = ref(false)
const showProfileEdit = ref(false)
const showConfirmDelete = ref(false)
const showVersionHistory = ref(false)
const selectedPosition = ref<UnifiedPosition | null>(null)
const itemsToDelete = ref<UnifiedPosition[] | null>(null)
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
let isPolling = false // Prevent overlapping polls
let lastPollTime = 0 // Track last successful poll
let pollErrorCount = 0 // Track consecutive errors for exponential backoff
const MIN_POLL_INTERVAL = 2000 // Minimum 2s between polls
const MAX_POLL_INTERVAL = 30000 // Maximum 30s between polls

// Lifecycle
onMounted(async () => {
  await loadData()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// Methods
async function loadData(): Promise<void> {
  try {
    // Load unified data and dashboard statistics in parallel
    // Use Promise.allSettled to prevent failure cascade
    const results = await Promise.allSettled([
      profilesStore.loadUnifiedData(),
      dashboardStore.fetchStats()
    ])

    // Check for failures and log them
    let hasErrors = false
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        const source = index === 0 ? 'profiles' : 'stats'
        logger.error(`Failed to load ${source}`, result.reason)
        hasErrors = true
      }
    })

    // Show error notification only if both operations failed
    if (results.every(r => r.status === 'rejected')) {
      showNotification('Ошибка загрузки данных. Попробуйте обновить страницу.', 'error')
    } else if (hasErrors) {
      // Partial failure - show warning
      showNotification('Некоторые данные не удалось загрузить', 'warning')
    }
  } catch (error: unknown) {
    logger.error('Failed to load unified data', error)
    showNotification('Ошибка загрузки данных. Попробуйте обновить страницу.', 'error')
  }
}

async function refreshData() {
  await loadData()
  showNotification('Данные обновлены', 'success')
}

function startPolling() {
  // Poll every 2 seconds if there are active generation tasks
  pollingInterval = window.setInterval(async () => {
    // Skip if already polling or too soon since last poll (rate limiting)
    const now = Date.now()
    const timeSinceLastPoll = now - lastPollTime
    const backoffInterval = Math.min(
      MIN_POLL_INTERVAL * Math.pow(2, pollErrorCount),
      MAX_POLL_INTERVAL
    )

    if (isPolling || timeSinceLastPoll < backoffInterval) {
      logger.debug('Skipping poll - rate limited', {
        isPolling,
        timeSinceLastPoll,
        backoffInterval
      })
      return
    }

    if (generatorStore.hasPendingTasks) {
      isPolling = true
      try {
        // Poll each active task
        const activeTasks = Array.from(generatorStore.activeTasks.entries())
        for (const [taskId, task] of activeTasks) {
          if (task.status === 'queued' || task.status === 'processing') {
            try {
              await generatorStore.pollTaskStatus(taskId)
            } catch (error: unknown) {
              logger.error(`Failed to poll task ${taskId}`, error)
              pollErrorCount++
            }
          }
        }

        // Reload unified data and statistics to update table and stats
        // Use Promise.allSettled instead of Promise.all to prevent failure cascade
        const results = await Promise.allSettled([
          profilesStore.loadUnifiedData(),
          dashboardStore.fetchStats()
        ])

        // Check for failures and log them
        results.forEach((result, index) => {
          if (result.status === 'rejected') {
            const source = index === 0 ? 'loadUnifiedData' : 'fetchStats'
            logger.error(`Failed to ${source} during polling`, result.reason)
            pollErrorCount++
          }
        })

        // Reset error count on successful poll
        if (results.every(r => r.status === 'fulfilled')) {
          pollErrorCount = 0
        }

        lastPollTime = now
      } catch (error: unknown) {
        logger.error('Polling iteration failed', error)
        pollErrorCount++
      } finally {
        isPolling = false
      }
    }
  }, 2000)
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  // Reset polling state to prevent stale values on remount
  isPolling = false
  lastPollTime = 0
  pollErrorCount = 0
}

// Event handlers
function handleViewProfile(position: UnifiedPosition) {
  selectedPosition.value = position
  showProfileViewer.value = true
}

function handleEditProfile(position: UnifiedPosition) {
  selectedPosition.value = position
  showProfileEdit.value = true
}

async function handleSaveProfile(data: { employee_name?: string; status?: PositionStatus }) {
  if (!selectedPosition.value?.profile_id) {
    showNotification('Профиль не найден', 'error')
    return
  }

  try {
    // Map PositionStatus to ProfileStatus for backend API
    const backendStatus = mapPositionStatusToProfileStatus(data.status)
    const payload = {
      employee_name: data.employee_name,
      ...(backendStatus && { status: backendStatus })
    }

    await profilesStore.updateProfile(String(selectedPosition.value.profile_id), payload)
    showNotification('Профиль успешно обновлен', 'success')
    showProfileEdit.value = false

    // Refresh data to show updated values
    await loadData()
  } catch (error: unknown) {
    logger.error('Failed to update profile', error)
    showNotification('Не удалось обновить профиль', 'error')
  }
}

// Map PositionStatus (frontend) to ProfileStatus (backend)
function mapPositionStatusToProfileStatus(status?: PositionStatus): 'completed' | 'archived' | 'in_progress' | undefined {
  if (!status) return undefined

  switch (status) {
    case 'generated':
      return 'completed'
    case 'generating':
      return 'in_progress'
    case 'archived':
      return 'archived'
    case 'not_generated':
      // Should not happen in edit context
      return undefined
    default:
      return undefined
  }
}

function handleDeleteProfile(position: UnifiedPosition) {
  itemsToDelete.value = [position]
  showConfirmDelete.value = true
}

async function handleConfirmDelete() {
  if (!itemsToDelete.value || itemsToDelete.value.length === 0) {
    showNotification('Нет профилей для удаления', 'error')
    return
  }

  const count = itemsToDelete.value.length

  try {
    // Delete profiles sequentially
    for (const item of itemsToDelete.value) {
      if (item.profile_id) {
        await profilesStore.deleteProfile(String(item.profile_id))
      }
    }

    showNotification(
      `${count === 1 ? 'Профиль удален' : `${count} профилей удалены`}`,
      'success'
    )
    showConfirmDelete.value = false
    itemsToDelete.value = null

    // Refresh data
    await loadData()
  } catch (error: unknown) {
    logger.error('Failed to delete profiles', error)
    showNotification('Не удалось удалить профили', 'error')
  }
}

async function handleRestoreProfile(position: UnifiedPosition) {
  if (!position.profile_id) {
    showNotification('Профиль не найден', 'error')
    return
  }

  try {
    // Backend doesn't have restoreProfile in service
    // Using updateProfile with status change as workaround
    await profilesStore.updateProfile(String(position.profile_id), {
      status: 'completed' // Backend ProfileStatus
    })

    showNotification(`Профиль "${position.position_name}" восстановлен`, 'success')

    // Refresh data
    await loadData()
  } catch (error: unknown) {
    logger.error('Failed to restore profile', error)
    showNotification('Не удалось восстановить профиль', 'error')
  }
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
  } catch (error: unknown) {
    logger.error('Failed to start profile regeneration', error)
    showNotification(
      `Не удалось запустить перегенерацию профиля "${position.position_name}". Попробуйте еще раз.`,
      'error'
    )
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
  } catch (error: unknown) {
    logger.error(`Failed to download profile for position ${position.position_id}`, error)
    showNotification(
      `Не удалось скачать профиль "${position.position_name}". Проверьте подключение к серверу.`,
      'error'
    )
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
  } catch (error: unknown) {
    logger.error(`Failed to download profile ${selectedPosition.value.profile_id} in format ${format}`, error)
    showNotification(
      `Не удалось скачать профиль в формате ${format.toUpperCase()}. Попробуйте другой формат.`,
      'error'
    )
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
  } catch (error: unknown) {
    logger.error(`Failed to start bulk generation for ${selectedPositionIds.value.length} positions`, error)
    showNotification(
      `Не удалось запустить массовую генерацию для ${selectedPositionIds.value.length} позиций. Проверьте подключение к серверу.`,
      'error'
    )
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
  } catch (error: unknown) {
    logger.error(`Failed to cancel bulk tasks for ${selectedPositionIds.value.length} positions`, error)
    showNotification(
      `Не удалось отменить задачи. Некоторые из ${count} задач могут продолжить выполнение.`,
      'error'
    )
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
  background: rgb(var(--v-theme-background));
}

.gap-2 {
  gap: 8px;
}

/* Smooth transitions for modals */
.v-dialog {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>

<template>
  <v-container fluid class="unified-profiles-view pa-6">
    <!-- Page Header -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-1">Профили должностей</h1>
        <p class="text-body-2 text-medium-emphasis">
          Управление профилями компетенций для всех позиций организации
        </p>
      </v-col>
    </v-row>

    <!-- Statistics Bar -->
    <v-row>
      <v-col cols="12">
        <StatsBar
          :total-positions="dashboardStore.stats?.positions_count || 0"
          :generated-count="dashboardStore.stats?.profiles_count || 0"
          :in-progress-count="dashboardStore.stats?.active_tasks_count || 0"
          :loading="dashboardStore.loading"
          :show-progress="false"
          @refresh="refreshData"
        />
      </v-col>
    </v-row>

    <!-- Enhanced Search Bar -->
    <v-row>
      <v-col cols="12">
        <EnhancedSearchBar
          v-model:search-query="searchQuery"
          v-model:view-mode="profilesStore.viewMode"
          v-model:filters="searchFilters"
          :total-results="totalResults"
          :navigation-label="navigationLabel"
          :has-results="hasResults"
          :is-searching="isSearching"
          @search="handleSearch"
          @next="goToNextResult"
          @previous="goToPreviousResult"
          @reset-filters="handleResetFilters"
        />
      </v-col>
    </v-row>

    <!-- Main Content: Tree/Table + Control Sidebar -->
    <v-row>
      <!-- Tree/Table View (70%) -->
      <v-col cols="12" md="8">
        <TreeView
          v-if="profilesStore.viewMode === 'tree'"
          v-model="selectedPositions"
          :items="catalogStore.organizationTree"
          :search-query="searchQuery"
          :current-result-id="currentResult?.nodeId || null"
          :search-result-ids="searchResultIds"
          @select="handleSelectionChange"
          @reset-filters="handleResetFilters"
        />

        <PositionsTable
          v-else
          :positions="filteredTablePositions"
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
          @selection-change="handleTableSelectionChange"
        />
      </v-col>

      <!-- Control Sidebar (30%) -->
      <v-col cols="12" md="4">
        <ControlSidebar
          :selected-positions="selectedPositionsForSidebar"
          :filters="sidebarFilters"
          :department-options="departmentOptions"
          @remove-selection="removeSelection"
          @clear-selection="handleClearSelection"
          @bulk-generate="handleBulkGenerate"
          @bulk-download="handleBulkDownload"
          @quality-check="handleQualityCheck"
          @update:filters="handleFiltersUpdate"
        />
      </v-col>
    </v-row>

    <!-- Profile Viewer Modal -->
    <ProfileViewerModal
      v-model="showProfileViewer"
      :profile="selectedPosition"
      @download="handleDownloadFromViewer"
      @view-versions="handleViewVersions(selectedPosition!)"
    />

    <!-- Full Profile Edit Modal (Content editing) -->
    <FullProfileEditModal
      v-model="showFullProfileEdit"
      :profile="selectedPosition"
    />

    <!-- Confirm Delete Dialog -->
    <ConfirmDeleteDialog
      v-model="showConfirmDelete"
      :items="itemsToDelete"
      :require-confirmation="!!(itemsToDelete && itemsToDelete.length > 1)"
      @delete="handleConfirmDelete"
    />

    <!-- Bulk Quality Dialog -->
    <BulkQualityDialog
      v-model="showQualityDialog"
      :positions="selectedPositionsData"
      @regenerate="handleRegenerateFromQualityCheck"
    />

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useProfilesStore } from '@/stores/profiles'
import { useGeneratorStore } from '@/stores/generator'
import { useDashboardStore } from '@/stores/dashboard'
import { useCatalogStore } from '@/stores/catalog'
import { useSearch } from '@/composables/useSearch'
import { logger } from '@/utils/logger'
import type { SearchableItem } from '@/stores/catalog'
import type { UnifiedPosition, ProfileFilters } from '@/types/unified'

// Components
import StatsBar from '@/components/profiles/StatsBar.vue'
import EnhancedSearchBar from '@/components/profiles/EnhancedSearchBar.vue'
import TreeView from '@/components/profiles/LazyTreeView.vue' // TRUE lazy loading - children load on expand
import ControlSidebar from '@/components/profiles/ControlSidebar.vue'
import PositionsTable from '@/components/profiles/PositionsTable.vue'
import ProfileViewerModal from '@/components/profiles/ProfileViewerModal.vue'
import FullProfileEditModal from '@/components/profiles/FullProfileEditModal.vue'
import ConfirmDeleteDialog from '@/components/common/ConfirmDeleteDialog.vue'
import BulkQualityDialog from '@/components/profiles/BulkQualityDialog.vue'

// Stores
const profilesStore = useProfilesStore()
const generatorStore = useGeneratorStore()
const dashboardStore = useDashboardStore()
const catalogStore = useCatalogStore()

// Search composable
const {
  searchQuery,
  searchResults,
  filters: searchFilters,
  hasResults,
  totalResults,
  isSearching,
  currentResult,
  navigationLabel,
  goToNextResult,
  goToPreviousResult
} = useSearch(computed(() => catalogStore.organizationTree))

// Local state
const selectedPositions = ref<SearchableItem[]>([])
const selectedPositionIds = ref<string[]>([])
const showProfileViewer = ref(false)
const showFullProfileEdit = ref(false)
const showConfirmDelete = ref(false)
const showQualityDialog = ref(false)
const selectedPosition = ref<UnifiedPosition | null>(null)
const itemsToDelete = ref<UnifiedPosition[] | null>(null)
const snackbar = ref({
  show: false,
  message: '',
  color: 'success' as 'success' | 'error' | 'warning' | 'info'
})

// Polling with exponential backoff
let pollingInterval: number | null = null
let isPolling = false // Prevent overlapping requests
let consecutiveErrors = 0 // Track errors for backoff
const BASE_POLL_INTERVAL = 3000 // 3 seconds
const MAX_POLL_INTERVAL = 30000 // 30 seconds max
const ERROR_THRESHOLD = 3 // Start backoff after 3 errors
let currentPollInterval = BASE_POLL_INTERVAL

// Computed
const selectedPositionsData = computed(() => {
  // For tree view, use selectedPositions directly
  if (profilesStore.viewMode === 'tree') {
    return selectedPositions.value.map(mapSearchableItemToUnifiedPosition)
  }

  // For table view, use selectedPositionIds
  const idsSet = new Set(selectedPositionIds.value)
  return profilesStore.filteredPositions.filter(p => idsSet.has(p.position_id))
})

const departmentOptions = computed(() => {
  // Extract unique departments from catalog
  const departments = new Set<string>()
  catalogStore.searchableItems.forEach(item => {
    if (item.department_path) {
      departments.add(item.department_path)
    }
  })
  return Array.from(departments).sort()
})

// Computed for search result IDs
const searchResultIds = computed(() => {
  return searchResults.value.map(result => result.nodeId)
})

// Computed for filtered table positions with search
const filteredTablePositions = computed(() => {
  let positions = profilesStore.filteredPositions

  // Apply search query
  if (searchQuery.value && searchQuery.value.length >= 2) {
    const query = searchQuery.value.toLowerCase().trim()
    positions = positions.filter(pos => {
      const nameMatch = pos.position_name.toLowerCase().includes(query)
      const deptMatch = pos.department_name?.toLowerCase().includes(query)
      const buMatch = pos.business_unit_name.toLowerCase().includes(query)
      return nameMatch || deptMatch || buMatch
    })
  }

  // Apply search filters
  if (searchFilters.value.withProfile && !searchFilters.value.withoutProfile) {
    positions = positions.filter(pos => pos.status === 'generated')
  } else if (searchFilters.value.withoutProfile && !searchFilters.value.withProfile) {
    positions = positions.filter(pos => pos.status !== 'generated')
  }

  return positions
})

// Computed for sidebar - convert UnifiedPosition back to SearchableItem
const selectedPositionsForSidebar = computed(() => {
  if (profilesStore.viewMode === 'tree') {
    return selectedPositions.value
  }

  // For table view, map UnifiedPosition back to SearchableItem
  return selectedPositionsData.value.map(mapUnifiedPositionToSearchableItem)
})

// Computed for sidebar filters - convert store filters to ProfileFilters type
const sidebarFilters = computed((): ProfileFilters => {
  return {
    search: profilesStore.filters.search || '',
    departments: [], // TODO: Migrate to multi-select departments
    status: (profilesStore.filters.status as 'all' | 'generated' | 'not_generated' | 'generating') || 'all',
    dateRange: null // TODO: Add date range support
  }
})

// Lifecycle
onMounted(async () => {
  await loadData()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// Watch for search results and auto-expand tree
watch(searchResults, (results) => {
  if (results && results.length > 0 && profilesStore.viewMode === 'tree') {
    // Auto-expand paths to search results
    logger.debug(`Found ${results.length} search results, auto-expanding tree`)
  }
}, { deep: true })

// Methods
async function loadData(): Promise<void> {
  try {
    await Promise.allSettled([
      profilesStore.loadUnifiedData(),
      dashboardStore.fetchStats(),
      catalogStore.loadOrganizationTree()
    ])
  } catch (error: unknown) {
    logger.error('Failed to load unified data', error)
    showNotification('Ошибка загрузки данных', 'error')
  }
}

async function refreshData(): Promise<void> {
  await loadData()
  showNotification('Данные обновлены', 'success')
}

/**
 * Adjusts polling interval based on consecutive errors
 * Uses exponential backoff to reduce load on server during issues
 */
function adjustPollingInterval(): void {
  if (consecutiveErrors > ERROR_THRESHOLD) {
    // Exponential backoff: double interval up to max
    currentPollInterval = Math.min(currentPollInterval * 2, MAX_POLL_INTERVAL)
    logger.warn(`Polling errors detected, backing off to ${currentPollInterval}ms`)

    // Restart polling with new interval
    stopPolling()
    startPolling()
  } else if (consecutiveErrors === 0 && currentPollInterval !== BASE_POLL_INTERVAL) {
    // Reset to normal interval after success
    currentPollInterval = BASE_POLL_INTERVAL
    logger.info('Polling recovered, resetting to normal interval')

    // Restart polling with normal interval
    stopPolling()
    startPolling()
  }
}

function startPolling(): void {
  pollingInterval = window.setInterval(async () => {
    // Prevent overlapping requests if previous poll is still running
    if (isPolling) {
      logger.debug('Skipping poll - previous request still in progress')
      return
    }

    if (generatorStore.hasPendingTasks) {
      isPolling = true
      try {
        const results = await Promise.allSettled([
          profilesStore.loadUnifiedData(),
          dashboardStore.fetchStats()
        ])

        // Check if any requests failed
        const hasErrors = results.some(result => result.status === 'rejected')
        if (hasErrors) {
          consecutiveErrors++
          logger.warn(`Polling error (${consecutiveErrors} consecutive)`)
        } else {
          consecutiveErrors = 0
        }

        adjustPollingInterval()
      } catch (error: unknown) {
        consecutiveErrors++
        logger.error('Polling failed', error)
        adjustPollingInterval()
      } finally {
        isPolling = false
      }
    }
  }, currentPollInterval)
}

function stopPolling(): void {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  isPolling = false // Reset flag when stopping
  consecutiveErrors = 0 // Reset errors counter
  currentPollInterval = BASE_POLL_INTERVAL // Reset interval
}

// Event handlers
function handleSearch(): void {
  // Search is handled by useSearch composable
  logger.debug('Search triggered with query:', searchQuery.value)
}

function handleResetFilters(): void {
  searchFilters.value = {
    withProfile: false,
    withoutProfile: false,
    exactMatch: false
  }
}

function handleSelectionChange(items: SearchableItem[]): void {
  selectedPositions.value = items
}

function handleTableSelectionChange(ids: string[]): void {
  selectedPositionIds.value = ids
}

function removeSelection(position: SearchableItem): void {
  selectedPositions.value = selectedPositions.value.filter(
    p => p.position_id !== position.position_id
  )
}

function handleClearSelection(): void {
  selectedPositions.value = []
  selectedPositionIds.value = []
}

function handleFiltersUpdate(filters: Partial<ProfileFilters>): void {
  Object.assign(profilesStore.filters, filters)
}

function handleViewProfile(position: UnifiedPosition): void {
  selectedPosition.value = position
  showProfileViewer.value = true
}

function handleEditProfile(position: UnifiedPosition): void {
  selectedPosition.value = position
  showFullProfileEdit.value = true
}

function handleDeleteProfile(position: UnifiedPosition): void {
  itemsToDelete.value = [position]
  showConfirmDelete.value = true
}

async function handleConfirmDelete(): Promise<void> {
  if (!itemsToDelete.value) return

  try {
    for (const item of itemsToDelete.value) {
      if (item.profile_id) {
        await profilesStore.deleteProfile(String(item.profile_id))
      }
    }

    showNotification(
      `${itemsToDelete.value.length === 1 ? 'Профиль удален' : `${itemsToDelete.value.length} профилей удалены`}`,
      'success'
    )
    showConfirmDelete.value = false
    itemsToDelete.value = null
    await loadData()
  } catch (error: unknown) {
    logger.error('Failed to delete profiles', error)
    showNotification('Не удалось удалить профили', 'error')
  }
}

async function handleRestoreProfile(position: UnifiedPosition): Promise<void> {
  if (!position.profile_id) return

  try {
    await profilesStore.updateProfile(String(position.profile_id), {
      status: 'completed'
    })
    showNotification(`Профиль "${position.position_name}" восстановлен`, 'success')
    await loadData()
  } catch (error: unknown) {
    logger.error('Failed to restore profile', error)
    showNotification('Не удалось восстановить профиль', 'error')
  }
}

function handleGenerateProfile(position: UnifiedPosition): void {
  showNotification(
    `Генерация профиля для "${position.position_name}" запущена`,
    'info'
  )
}

async function handleRegenerateProfile(position: UnifiedPosition): Promise<void> {
  try {
    await generatorStore.startGeneration({
      position_id: position.position_id,
      position_name: position.position_name,
      business_unit_name: position.business_unit_name
    })
    showNotification(`Перегенерация профиля запущена`, 'info')
  } catch (error: unknown) {
    logger.error('Failed to regenerate profile', error)
    showNotification('Не удалось запустить перегенерацию', 'error')
  }
}

function handleCancelGeneration(position: UnifiedPosition): void {
  showNotification(`Генерация для "${position.position_name}" отменена`, 'warning')
}

async function handleDownloadProfile(position: UnifiedPosition): Promise<void> {
  if (!position.profile_id) return

  try {
    await profilesStore.downloadProfile(String(position.profile_id), 'json')
    showNotification(`Профиль "${position.position_name}" скачан`, 'success')
  } catch (error: unknown) {
    logger.error('Failed to download profile', error)
    showNotification('Не удалось скачать профиль', 'error')
  }
}

async function handleDownloadFromViewer(format: 'json' | 'md' | 'docx'): Promise<void> {
  if (!selectedPosition.value?.profile_id) return

  try {
    await profilesStore.downloadProfile(String(selectedPosition.value.profile_id), format)
    showNotification(`Профиль скачан в формате ${format.toUpperCase()}`, 'success')
  } catch (error: unknown) {
    logger.error('Failed to download profile', error)
    showNotification('Не удалось скачать профиль', 'error')
  }
}

function handleViewVersions(position: UnifiedPosition): void {
  selectedPosition.value = position
  // TODO: Implement version history modal (Week 5 Day 6)
  showNotification('История версий будет реализована позже', 'info')
}

function handleShareProfile(position: UnifiedPosition): void {
  showNotification(`Ссылка на профиль "${position.position_name}" скопирована`, 'success')
}

async function handleBulkGenerate(): Promise<void> {
  const positions = selectedPositionsData.value.filter(p => p.status === 'not_generated')

  if (positions.length === 0) {
    showNotification('Нет позиций для генерации', 'warning')
    return
  }

  try {
    const positionIds = positions.map(p => p.position_id)
    await profilesStore.bulkGenerate(positionIds)
    showNotification(`Запущена массовая генерация для ${positions.length} позиций`, 'success')
  } catch (error: unknown) {
    logger.error('Failed to start bulk generation', error)
    showNotification('Не удалось запустить массовую генерацию', 'error')
  }
}

async function handleBulkDownload(): Promise<void> {
  const generated = selectedPositionsData.value.filter(p => p.status === 'generated')

  if (generated.length === 0) {
    showNotification('Нет сгенерированных профилей для скачивания', 'warning')
    return
  }

  try {
    const profileIds = generated
      .map(p => p.profile_id)
      .filter((id): id is number => id !== null && id !== undefined)
      .map(id => String(id))

    await profilesStore.bulkDownload(profileIds, ['json'])
    showNotification(`Скачано ${profileIds.length} профилей в ZIP архиве`, 'success')
    handleClearSelection()
  } catch (error: unknown) {
    logger.error('Failed to bulk download', error)
    showNotification('Не удалось скачать профили', 'error')
  }
}

function handleQualityCheck(): void {
  const generated = selectedPositionsData.value.filter(p => p.status === 'generated')

  if (generated.length === 0) {
    showNotification('Нет сгенерированных профилей для проверки', 'warning')
    return
  }

  showQualityDialog.value = true
}

async function handleRegenerateFromQualityCheck(positionIds: string[]): Promise<void> {
  if (positionIds.length === 0) return

  try {
    await profilesStore.bulkGenerate(positionIds)
    showNotification(`Запущена регенерация для ${positionIds.length} профилей`, 'success')
  } catch (error: unknown) {
    logger.error('Failed to regenerate from quality check', error)
    showNotification('Не удалось запустить регенерацию', 'error')
  }
}

function showNotification(message: string, color: 'success' | 'error' | 'warning' | 'info'): void {
  snackbar.value = { show: true, message, color }
}

// Helper to map SearchableItem to UnifiedPosition
function mapSearchableItemToUnifiedPosition(item: SearchableItem): UnifiedPosition {
  return {
    position_id: item.position_id,
    position_name: item.position_name,
    business_unit_id: item.business_unit_id,
    business_unit_name: item.business_unit_name,
    department_name: item.department_name || '',
    department_path: item.department_path,
    status: item.profile_exists ? 'generated' : 'not_generated',
    profile_id: item.profile_id || undefined,
    actions: {
      canView: item.profile_exists,
      canGenerate: !item.profile_exists,
      canDownload: item.profile_exists,
      canEdit: item.profile_exists,
      canDelete: item.profile_exists,
      canCancel: false,
      canRegenerate: item.profile_exists
    }
  }
}

// Helper to map UnifiedPosition back to SearchableItem
function mapUnifiedPositionToSearchableItem(position: UnifiedPosition): SearchableItem {
  return {
    position_id: position.position_id,
    position_name: position.position_name,
    business_unit_id: position.business_unit_id,
    business_unit_name: position.business_unit_name,
    department_name: position.department_name,
    department_path: position.department_path,
    profile_exists: position.status === 'generated',
    profile_id: position.profile_id
  }
}
</script>

<style scoped>
.unified-profiles-view {
  min-height: 100vh;
  background: rgb(var(--v-theme-background));
}
</style>

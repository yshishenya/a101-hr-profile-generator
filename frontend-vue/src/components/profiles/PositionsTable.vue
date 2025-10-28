<!-- eslint-disable vue/valid-v-slot -->
<template>
  <BaseCard>
    <v-data-table
      v-model="selected"
      :headers="headers"
      :items="positions"
      :loading="loading"
      :items-per-page="25"
      :items-per-page-options="[10, 25, 50, 100]"
      show-select
      item-value="position_id"
      class="positions-table"
      @update:model-value="onSelectionChange"
    >
      <!-- Position Name Column (with breadcrumbs) -->
      <template #item.position_name="{ item }">
        <div class="position-cell-enhanced">
          <!-- Position name (large, bold) -->
          <div class="position-name-main text-body-1 font-weight-medium mb-1">
            {{ item.position_name }}
          </div>

          <!-- Breadcrumbs (small, muted) with full hierarchy tooltip -->
          <div
            class="department-breadcrumbs text-caption text-medium-emphasis"
            @mouseenter="showFullPath = item.position_id"
            @mouseleave="showFullPath = null"
          >
            <!-- eslint-disable-next-line vue/no-v-html -->
            <span v-html="formatBreadcrumbs(item)" />

            <!-- Tooltip with full hierarchy path -->
            <v-tooltip
              :model-value="showFullPath === item.position_id"
              activator="parent"
              location="bottom start"
              max-width="500"
            >
              <div class="pa-2">
                <div class="text-subtitle-2 mb-2">📋 Полная иерархия:</div>
                <div
                  v-for="(level, index) in getHierarchyLevels(item)"
                  :key="index"
                  class="d-flex align-center mb-1"
                  :style="{ marginLeft: `${index * 12}px` }"
                >
                  {{ level.icon }} {{ level.name }}
                  <v-icon
                    v-if="index < getHierarchyLevels(item).length - 1"
                    size="x-small"
                    class="mx-1"
                  >
                    mdi-chevron-down
                  </v-icon>
                </div>
              </div>
            </v-tooltip>
          </div>
        </div>
      </template>

      <!-- Status Column (compact badges) -->
      <template #item.status="{ item }">
        <v-chip
          :color="getStatusColor(item.status)"
          :prepend-icon="getStatusIcon(item.status)"
          size="small"
          variant="tonal"
        >
          {{ getStatusText(item.status) }}
        </v-chip>
      </template>

      <!-- Profile Info Column (version, quality, date) -->
      <template #item.profile_info="{ item }">
        <div v-if="item.profile_id" class="profile-info-compact">
          <!-- Version -->
          <div class="d-flex align-center mb-1">
            <v-chip
              v-if="item.version_count && item.version_count > 1"
              size="x-small"
              prepend-icon="mdi-layers"
              variant="tonal"
            >
              v{{ item.current_version || 1 }} ({{ item.version_count }})
            </v-chip>
            <span v-else class="text-caption">
              v{{ item.current_version || 1 }}
            </span>
          </div>

          <!-- Quality score -->
          <div v-if="item.quality_score" class="d-flex align-center mb-1">
            <v-icon size="x-small" color="warning" class="mr-1">mdi-star</v-icon>
            <span class="text-caption font-weight-medium">{{ item.quality_score }}%</span>
          </div>

          <!-- Creation date -->
          <div class="text-caption text-medium-emphasis">
            {{ formatDate(item.created_at) }}
          </div>
        </div>
        <div v-else class="text-center text-medium-emphasis">
          —
        </div>
      </template>

      <!-- Actions Column -->
      <template #item.actions="{ item }">
        <div class="actions-cell">
          <!-- View Profile -->
          <v-btn
            v-if="item.actions.canView"
            icon="mdi-eye"
            size="small"
            variant="text"
            @click="onViewProfile(item)"
          >
            <v-icon>mdi-eye</v-icon>
            <v-tooltip activator="parent" location="bottom">Просмотр профиля</v-tooltip>
          </v-btn>

          <!-- Generate Profile -->
          <v-btn
            v-if="item.actions.canGenerate"
            icon="mdi-magic-staff"
            size="small"
            variant="text"
            color="primary"
            @click="onGenerateProfile(item)"
          >
            <v-icon>mdi-magic-staff</v-icon>
            <v-tooltip activator="parent" location="bottom">Сгенерировать профиль</v-tooltip>
          </v-btn>

          <!-- Regenerate Profile -->
          <v-btn
            v-if="item.actions.canRegenerate"
            icon="mdi-refresh"
            size="small"
            variant="text"
            color="warning"
            @click="onRegenerateProfile(item)"
          >
            <v-icon>mdi-refresh</v-icon>
            <v-tooltip activator="parent" location="bottom">Перегенерировать</v-tooltip>
          </v-btn>

          <!-- Cancel Generation -->
          <v-btn
            v-if="item.actions.canCancel"
            icon="mdi-close-circle"
            size="small"
            variant="text"
            color="error"
            @click="onCancelGeneration(item)"
          >
            <v-icon>mdi-close-circle</v-icon>
            <v-tooltip activator="parent" location="bottom">Отменить генерацию</v-tooltip>
          </v-btn>

          <!-- Download Profile -->
          <v-btn
            v-if="item.actions.canDownload"
            icon="mdi-download"
            size="small"
            variant="text"
            @click="onDownloadProfile(item)"
          >
            <v-icon>mdi-download</v-icon>
            <v-tooltip activator="parent" location="bottom">Скачать профиль</v-tooltip>
          </v-btn>

          <!-- More Actions Menu -->
          <v-menu v-if="item.actions.canView">
            <template #activator="{ props: menuProps }">
              <v-btn
                icon="mdi-dots-vertical"
                size="small"
                variant="text"
                v-bind="menuProps"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>

            <v-list density="compact">
              <v-list-item
                v-if="item.version_count && item.version_count > 1"
                prepend-icon="mdi-history"
                @click="onViewVersions(item)"
              >
                <v-list-item-title>История версий</v-list-item-title>
              </v-list-item>

              <v-list-item
                v-if="item.actions.canEdit"
                prepend-icon="mdi-pencil"
                @click="onEditProfile(item)"
              >
                <v-list-item-title>Редактировать</v-list-item-title>
              </v-list-item>

              <v-list-item
                v-if="item.actions.canDelete"
                prepend-icon="mdi-delete"
                @click="onDeleteProfile(item)"
              >
                <v-list-item-title>Удалить</v-list-item-title>
              </v-list-item>

              <v-list-item
                v-if="item.status === 'archived'"
                prepend-icon="mdi-restore"
                @click="onRestoreProfile(item)"
              >
                <v-list-item-title>Восстановить</v-list-item-title>
              </v-list-item>

              <v-divider />

              <v-list-item
                prepend-icon="mdi-content-copy"
                @click="copyPositionId(item.position_id)"
              >
                <v-list-item-title>Копировать ID</v-list-item-title>
              </v-list-item>

              <v-list-item
                prepend-icon="mdi-share-variant"
                @click="onShareProfile(item)"
              >
                <v-list-item-title>Поделиться</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </template>

      <!-- Loading State -->
      <template #loading>
        <div class="text-center pa-4">
          <v-progress-circular indeterminate color="primary" />
          <div class="mt-2">Загрузка позиций...</div>
        </div>
      </template>

      <!-- Empty State -->
      <template #no-data>
        <div class="empty-state pa-8 text-center">
          <v-icon size="64" color="grey-lighten-2">mdi-briefcase-outline</v-icon>
          <div class="text-h6 mt-4">Позиции не найдены</div>
          <div class="text-body-2 text-medium-emphasis mt-2">
            Попробуйте изменить фильтры поиска
          </div>
        </div>
      </template>
    </v-data-table>

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
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { logger } from '@/utils/logger'
import BaseCard from '@/components/common/BaseCard.vue'
import type { UnifiedPosition } from '@/types/unified'

// Props
interface Props {
  positions: UnifiedPosition[]
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
const emit = defineEmits<{
  viewProfile: [position: UnifiedPosition]
  editProfile: [position: UnifiedPosition]
  deleteProfile: [position: UnifiedPosition]
  restoreProfile: [position: UnifiedPosition]
  generateProfile: [position: UnifiedPosition]
  regenerateProfile: [position: UnifiedPosition]
  cancelGeneration: [position: UnifiedPosition]
  downloadProfile: [position: UnifiedPosition]
  viewVersions: [position: UnifiedPosition]
  shareProfile: [position: UnifiedPosition]
  selectionChange: [selectedIds: string[]]
}>()

// State
const selected = ref<string[]>([])
const showFullPath = ref<string | null>(null)  // Controls tooltip visibility
const snackbar = ref({
  show: false,
  message: '',
  color: 'success' as 'success' | 'error'
})

// Stores
const generatorStore = useGeneratorStore()

// Table headers (department_name removed, widths optimized)
const headers = computed(() => [
  {
    title: 'Позиция',
    key: 'position_name',
    align: 'start' as const,
    sortable: true,
    width: '45%'  // Increased from 30% to include breadcrumbs
  },
  {
    title: 'Статус',
    key: 'status',
    align: 'center' as const,
    sortable: true,
    width: '15%'
  },
  {
    title: 'Профиль',
    key: 'profile_info',
    align: 'start' as const,  // Changed from center to start
    sortable: false,
    width: '20%'  // Increased from 15% for better readability
  },
  {
    title: 'Действия',
    key: 'actions',
    align: 'end' as const,
    sortable: false,
    width: '20%'  // Increased from 15% for better spacing
  }
])

// Action handlers
function onViewProfile(position: UnifiedPosition): void {
  emit('viewProfile', position)
}

function onEditProfile(position: UnifiedPosition): void {
  emit('editProfile', position)
}

function onDeleteProfile(position: UnifiedPosition): void {
  emit('deleteProfile', position)
}

function onRestoreProfile(position: UnifiedPosition): void {
  emit('restoreProfile', position)
}

async function onGenerateProfile(position: UnifiedPosition): Promise<void> {
  try {
    await generatorStore.startGeneration({
      position_id: position.position_id,
      position_name: position.position_name,
      business_unit_name: position.business_unit_name
    })
    emit('generateProfile', position)
  } catch (error: unknown) {
    logger.error(`Failed to start generation for position ${position.position_id} (${position.position_name})`, error)
  }
}

function onRegenerateProfile(position: UnifiedPosition): void {
  emit('regenerateProfile', position)
}

async function onCancelGeneration(position: UnifiedPosition): Promise<void> {
  if (position.task_id) {
    try {
      await generatorStore.cancelTask(position.task_id)
      emit('cancelGeneration', position)
    } catch (error: unknown) {
      logger.error(`Failed to cancel generation task ${position.task_id} for position ${position.position_id}`, error)
    }
  }
}

function onDownloadProfile(position: UnifiedPosition): void {
  emit('downloadProfile', position)
}

function onViewVersions(position: UnifiedPosition): void {
  emit('viewVersions', position)
}

function onShareProfile(position: UnifiedPosition): void {
  emit('shareProfile', position)
}

// Selection handler
function onSelectionChange(selectedIds: string[]): void {
  emit('selectionChange', selectedIds)
}

// ====================================
// BREADCRUMBS FORMATTING FUNCTIONS
// ====================================

/**
 * Format department hierarchy as breadcrumbs with icons and HTML
 * @param item - UnifiedPosition object
 * @returns HTML string with formatted breadcrumbs
 */
function formatBreadcrumbs(item: UnifiedPosition): string {
  const path = item.department_path || item.business_unit_name || ''
  const levels = path.split(' > ').filter(Boolean)

  // If only one level (no duplication needed)
  if (levels.length === 1 && levels[0]) {
    return `${getLevelIcon(0)} ${smartTruncate(levels[0], 50)}`
  }

  // Multiple levels - show full path with icons and separators
  const formatted = levels.map((level, index) => {
    const icon = getLevelIcon(index)
    const truncated = smartTruncate(level, 35)
    return `${icon} ${truncated}`
  }).join(' <span class="breadcrumb-separator">›</span> ')

  return formatted
}

/**
 * Get icon emoji for hierarchy level
 * @param level - Level index (0 = top level, 1 = second level, etc.)
 * @returns Emoji icon as string
 */
function getLevelIcon(level: number): string {
  const icons = [
    '🏢',  // Level 0: Block/Division
    '📂',  // Level 1: Department/Management
    '📋',  // Level 2: Office/Unit
    '📄'   // Level 3+: Sub-unit
  ]
  const icon = icons[Math.min(level, icons.length - 1)]
  return icon !== undefined ? icon : '📄'
}

/**
 * Smart text truncation with word boundary awareness
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text with ellipsis if needed
 */
function smartTruncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text

  // Try to truncate at word boundary
  const truncated = text.slice(0, maxLength)
  const lastSpace = truncated.lastIndexOf(' ')

  // If found a good word boundary (not too far from end)
  if (lastSpace > maxLength * 0.7) {
    return truncated.slice(0, lastSpace) + '...'
  }

  // No good word boundary, just cut with ellipsis
  return truncated + '...'
}

/**
 * Get full hierarchy levels for tooltip display
 * @param item - UnifiedPosition object
 * @returns Array of hierarchy level objects with icon and name
 */
function getHierarchyLevels(item: UnifiedPosition): Array<{ icon: string; name: string }> {
  const path = item.department_path || item.business_unit_name || ''
  const levels = path.split(' > ').filter(Boolean)

  return levels.map((level, index) => ({
    icon: getLevelIcon(index),
    name: level
  }))
}

// ====================================
// STATUS FORMATTING FUNCTIONS
// ====================================

/**
 * Get Vuetify color for status badge
 */
function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    generated: 'success',
    not_generated: 'default',
    generating: 'primary',
    archived: 'default'
  }
  return colors[status] || 'default'
}

/**
 * Get Material Design icon for status
 */
function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    generated: 'mdi-check-circle',
    not_generated: 'mdi-circle-outline',
    generating: 'mdi-loading',
    archived: 'mdi-archive'
  }
  const icon = icons[status]
  return icon !== undefined ? icon : 'mdi-help-circle'
}

/**
 * Get human-readable status text in Russian
 */
function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    generated: 'Готово',
    not_generated: 'Не создан',
    generating: 'Генерация',
    archived: 'Архив'
  }
  return texts[status] || status
}

// ====================================
// UTILITY FUNCTIONS
// ====================================

/**
 * Format date as DD.MM.YY
 */
function formatDate(dateString: string | undefined): string {
  if (!dateString) return '—'

  const date = new Date(dateString)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear().toString().slice(2)

  return `${day}.${month}.${year}`
}

/**
 * Copy position ID to clipboard and show notification
 */
function copyPositionId(positionId: string): void {
  navigator.clipboard.writeText(positionId)
  snackbar.value = {
    show: true,
    message: 'ID позиции скопирован в буфер обмена',
    color: 'success'
  }
}
</script>

<style scoped>
/* ================================== */
/* ENHANCED TABLE STYLES */
/* ================================== */

.positions-table {
  background: transparent;
}

/* Position cell with breadcrumbs */
.position-cell-enhanced {
  padding: 8px 0;
  min-height: 56px;
}

.position-name-main {
  line-height: 1.4;
  color: rgb(var(--v-theme-on-surface));
}

.department-breadcrumbs {
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  cursor: help;
  transition: opacity 0.2s;
}

.department-breadcrumbs:hover {
  opacity: 0.8;
}

.department-breadcrumbs :deep(.breadcrumb-separator) {
  margin: 0 4px;
  color: rgb(var(--v-theme-on-surface-variant));
  opacity: 0.5;
}

/* Profile info compact layout */
.profile-info-compact {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Actions cell compact */
.actions-cell {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  min-width: 140px;
}

/* Empty state */
.empty-state {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .actions-cell {
    flex-wrap: wrap;
  }
}
</style>

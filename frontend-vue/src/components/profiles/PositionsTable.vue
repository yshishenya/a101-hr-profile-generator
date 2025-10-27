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
      <!-- Position Name Column -->
      <template #item.position_name="{ item }">
        <div class="position-cell">
          <div class="position-name">{{ item.position_name }}</div>
          <div class="position-id text-caption text-medium-emphasis">
            ID: {{ item.position_id }}
          </div>
        </div>
      </template>

      <!-- Department Column -->
      <template #item.department_name="{ item }">
        <div class="department-cell">
          <div class="department-name">{{ item.department_name }}</div>
          <div class="business-unit text-caption text-medium-emphasis">
            {{ item.business_unit_name }}
          </div>
        </div>
      </template>

      <!-- Status Column -->
      <template #item.status="{ item }">
        <StatusBadge
          :status="item.status"
          :progress="item.progress"
        />
      </template>

      <!-- Profile Info Column -->
      <template #item.profile_info="{ item }">
        <div v-if="item.profile_id" class="profile-info">
          <div>
            <v-chip
              v-if="item.version_count && item.version_count > 1"
              size="small"
              prepend-icon="mdi-layers"
            >
              v{{ item.current_version || 1 }} ({{ item.version_count }})
            </v-chip>
            <span v-else class="text-caption text-medium-emphasis">
              v{{ item.current_version || 1 }}
            </span>
          </div>
          <div v-if="item.quality_score" class="quality-score">
            <span class="text-caption text-medium-emphasis">
              Качество: {{ item.quality_score }}%
            </span>
            <v-icon size="x-small" class="ml-1">mdi-information-outline</v-icon>
            <v-tooltip activator="parent" location="bottom" max-width="300">
              <div class="text-body-2">
                <strong>Оценка полноты и качества профиля</strong>
                <div class="mt-1">
                  Учитывается структура данных, детализация описаний и соответствие стандартам.
                  Рекомендуется регенерация при оценке ниже 70%.
                </div>
              </div>
            </v-tooltip>
          </div>
        </div>
        <div v-else class="text-caption text-medium-emphasis">
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
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGeneratorStore } from '@/stores/generator'
import { logger } from '@/utils/logger'
import BaseCard from '@/components/common/BaseCard.vue'
import StatusBadge from './StatusBadge.vue'
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

// Stores
const generatorStore = useGeneratorStore()

// Table headers
const headers = computed(() => [
  {
    title: 'Позиция',
    key: 'position_name',
    align: 'start' as const,
    sortable: true,
    width: '30%'
  },
  {
    title: 'Подразделение',
    key: 'department_name',
    align: 'start' as const,
    sortable: true,
    width: '25%'
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
    align: 'center' as const,
    sortable: false,
    width: '15%'
  },
  {
    title: 'Действия',
    key: 'actions',
    align: 'end' as const,
    sortable: false,
    width: '15%'
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
</script>

<style scoped>
.positions-table {
  background: transparent;
}

.position-cell,
.department-cell {
  min-height: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
}

.position-name,
.department-name {
  font-weight: 500;
  line-height: 1.3;
}

.position-id {
  font-size: 0.7rem;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}

.quality-score {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: help;
}

.actions-cell {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

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

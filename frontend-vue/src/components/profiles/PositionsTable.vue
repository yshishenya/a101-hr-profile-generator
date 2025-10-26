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
          <div class="text-caption">
            v{{ item.current_version || 1 }}
            <span v-if="item.version_count && item.version_count > 1">
              ({{ item.version_count }} версий)
            </span>
          </div>
          <div v-if="item.quality_score" class="text-caption text-medium-emphasis">
            Качество: {{ item.quality_score }}%
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
                disabled
              >
                <v-list-item-title>Редактировать (Week 7)</v-list-item-title>
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
function onViewProfile(position: UnifiedPosition) {
  emit('viewProfile', position)
}

async function onGenerateProfile(position: UnifiedPosition) {
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

function onRegenerateProfile(position: UnifiedPosition) {
  emit('regenerateProfile', position)
}

async function onCancelGeneration(position: UnifiedPosition) {
  if (position.task_id) {
    try {
      await generatorStore.cancelTask(position.task_id)
      emit('cancelGeneration', position)
    } catch (error: unknown) {
      logger.error(`Failed to cancel generation task ${position.task_id} for position ${position.position_id}`, error)
    }
  }
}

function onDownloadProfile(position: UnifiedPosition) {
  emit('downloadProfile', position)
}

function onViewVersions(position: UnifiedPosition) {
  emit('viewVersions', position)
}

function onShareProfile(position: UnifiedPosition) {
  emit('shareProfile', position)
}

// Selection handler
function onSelectionChange(selectedIds: string[]) {
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

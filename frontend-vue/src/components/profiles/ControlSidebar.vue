<template>
  <v-card flat class="control-sidebar pa-4">
    <!-- Selection Summary -->
    <div class="mb-6">
      <div class="text-subtitle-2 mb-3">Выбранные позиции</div>

      <v-alert
        v-if="selectedPositions.length === 0"
        type="info"
        variant="tonal"
        density="compact"
      >
        Выберите позиции из дерева для выполнения действий
      </v-alert>

      <div v-else>
        <!-- Selection Stats -->
        <div class="mb-3">
          <v-chip
            color="primary"
            variant="flat"
            class="mr-2"
          >
            <v-icon start size="small">mdi-check-circle</v-icon>
            {{ selectedPositions.length }} выбрано
          </v-chip>

          <v-chip
            v-if="generatedCount > 0"
            color="success"
            variant="outlined"
          >
            {{ generatedCount }} с профилями
          </v-chip>
        </div>

        <!-- Selected Items List -->
        <div style="max-height: 200px; overflow-y: auto;" class="mb-3">
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
      </div>
    </div>

    <v-divider class="mb-4" />

    <!-- Bulk Actions -->
    <div class="mb-6">
      <div class="text-subtitle-2 mb-3">Действия</div>

      <div class="d-flex flex-column gap-2">
        <v-btn
          color="primary"
          size="large"
          block
          :disabled="selectedPositions.length === 0"
          prepend-icon="mdi-rocket-launch"
          @click="$emit('bulk-generate')"
        >
          Генерировать ({{ selectedPositions.length }})
        </v-btn>

        <v-btn
          variant="outlined"
          block
          :disabled="generatedCount === 0"
          prepend-icon="mdi-download"
          @click="$emit('bulk-download')"
        >
          Скачать ({{ generatedCount }})
        </v-btn>

        <v-btn
          variant="outlined"
          block
          :disabled="generatedCount === 0"
          prepend-icon="mdi-file-check"
          @click="$emit('quality-check')"
        >
          Проверить качество
        </v-btn>

        <v-btn
          variant="text"
          block
          :disabled="selectedPositions.length === 0"
          @click="$emit('clear-selection')"
        >
          Очистить выбор
        </v-btn>
      </div>

      <v-alert
        v-if="generatedCount > 0 && generatedCount < selectedPositions.length"
        type="warning"
        variant="tonal"
        density="compact"
        class="mt-3"
      >
        {{ generatedCount }} {{ getRussianPluralForm(generatedCount, 'позиция', 'позиции', 'позиций') }}
        уже {{ getRussianPluralForm(generatedCount, 'имеет', 'имеют', 'имеют') }} профили.
        Новые профили будут созданы без изменения существующих.
      </v-alert>
    </div>

    <v-divider class="mb-4" />

    <!-- Filters -->
    <div>
      <div class="text-subtitle-2 mb-3">Фильтры</div>

      <!-- Status Filter -->
      <v-select
        :model-value="filters.status"
        :items="statusFilterOptions"
        label="Статус"
        density="compact"
        variant="outlined"
        hide-details
        class="mb-3"
        @update:model-value="handleFilterChange('status', $event)"
      />

      <!-- Department Filter -->
      <v-autocomplete
        :model-value="filters.departments"
        :items="departmentOptions"
        label="Подразделения"
        density="compact"
        variant="outlined"
        multiple
        chips
        closable-chips
        hide-details
        class="mb-3"
        @update:model-value="handleFilterChange('departments', $event)"
      />

      <!-- Date Range Filter -->
      <v-menu
        v-model="showDateRangePicker"
        :close-on-content-click="false"
      >
        <template #activator="{ props: menuProps }">
          <v-text-field
            :model-value="dateRangeText"
            label="Период создания"
            density="compact"
            variant="outlined"
            readonly
            prepend-inner-icon="mdi-calendar"
            clearable
            hide-details
            v-bind="menuProps"
            @click:clear="clearDateRange"
          />
        </template>

        <v-card>
          <v-card-text>
            <div class="text-subtitle-2 mb-2">Выберите период</div>
            <!-- Date range picker would go here -->
            <div class="text-body-2 text-medium-emphasis">
              (Календарь будет добавлен в следующей итерации)
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn size="small" @click="showDateRangePicker = false">
              Закрыть
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { SearchableItem } from '@/stores/catalog'
import type { ProfileFilters } from '@/types/unified'

// Props
interface Props {
  selectedPositions: SearchableItem[]
  filters: ProfileFilters
  departmentOptions?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  departmentOptions: () => []
})

// Emits
const emit = defineEmits<{
  'remove-selection': [position: SearchableItem]
  'clear-selection': []
  'bulk-generate': []
  'bulk-download': []
  'quality-check': []
  'update:filters': [filters: Partial<ProfileFilters>]
}>()

// Local state
const showDateRangePicker = ref(false)

// Filter options
const statusFilterOptions = [
  { title: 'Все статусы', value: 'all' },
  { title: 'Сгенерировано', value: 'generated' },
  { title: 'Не сгенерировано', value: 'not_generated' },
  { title: 'В процессе', value: 'generating' }
]

// Computed
const generatedCount = computed(() => {
  return props.selectedPositions.filter(p => p.profile_exists).length
})

const dateRangeText = computed(() => {
  const range = props.filters.dateRange
  if (!range || !range.from || !range.to) return ''
  return `${range.from} - ${range.to}`
})

// Methods
function removeSelection(position: SearchableItem): void {
  emit('remove-selection', position)
}

function handleFilterChange(key: string, value: unknown): void {
  emit('update:filters', { [key]: value })
}

function clearDateRange(): void {
  emit('update:filters', { dateRange: null })
}

function getRussianPluralForm(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100

  if (mod10 === 1 && mod100 !== 11) {
    return one
  } else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return few
  } else {
    return many
  }
}
</script>

<style scoped>
.control-sidebar {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  height: 100%;
  overflow-y: auto;
}

.gap-2 {
  gap: 8px;
}
</style>

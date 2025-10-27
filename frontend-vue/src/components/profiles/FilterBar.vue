<template>
  <BaseCard class="filter-bar">
    <v-card-text class="pa-4">
      <!-- Row 1: Search -->
      <v-row dense class="mb-2">
        <v-col cols="12">
          <v-text-field
            v-model="localFilters.search"
            prepend-inner-icon="mdi-magnify"
            placeholder="Поиск по позиции или подразделению"
            density="comfortable"
            variant="outlined"
            hide-details
            clearable
            @update:model-value="onSearchChange"
          />
        </v-col>
      </v-row>

      <!-- Row 2: Main Filters -->
      <v-row dense class="mb-2">
        <!-- Department Multi-Select -->
        <v-col cols="12" sm="6" md="4">
          <v-select
            v-model="localFilters.departments"
            :items="departmentItems"
            prepend-inner-icon="mdi-office-building"
            placeholder="Все подразделения"
            density="comfortable"
            variant="outlined"
            hide-details
            clearable
            multiple
            chips
            @update:model-value="onFilterChange"
          >
            <template #prepend-item>
              <v-list-item @click="toggleAllDepartments">
                <template #prepend>
                  <v-checkbox-btn
                    :model-value="allDepartmentsSelected"
                    :indeterminate="someDepartmentsSelected"
                  />
                </template>
                <v-list-item-title>
                  {{ allDepartmentsSelected ? 'Снять все' : 'Выбрать все' }}
                </v-list-item-title>
              </v-list-item>
              <v-divider />
            </template>
            <template #selection="{ item, index }">
              <v-chip v-if="index < 2" size="small">
                {{ item.title }}
              </v-chip>
              <span v-if="index === 2" class="text-caption text-medium-emphasis">
                (+{{ localFilters.departments.length - 2 }} еще)
              </span>
            </template>
          </v-select>
        </v-col>

        <!-- Status Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="localFilters.status"
            :items="statusItems"
            prepend-inner-icon="mdi-filter"
            placeholder="Все статусы"
            density="comfortable"
            variant="outlined"
            hide-details
            @update:model-value="onFilterChange"
          >
            <template #selection="{ item }">
              <span>{{ item.title }}</span>
            </template>
            <template #item="{ item, props: itemProps }">
              <v-list-item v-bind="itemProps">
                <template #prepend>
                  <v-icon :color="item.raw.color">{{ item.raw.icon }}</v-icon>
                </template>
              </v-list-item>
            </template>
          </v-select>
        </v-col>

        <!-- Date Range Filter -->
        <v-col cols="12" sm="6" md="3">
          <DateRangeFilter
            v-model="localFilters.dateRange"
            @update:model-value="onFilterChange"
          />
        </v-col>

        <!-- Actions Column -->
        <v-col cols="12" sm="6" md="2" class="d-flex align-center justify-md-end gap-2">
          <!-- View Mode Toggle -->
          <v-btn-toggle
            v-model="localViewMode"
            density="comfortable"
            mandatory
            variant="outlined"
            class="flex-shrink-0"
            @update:model-value="onViewModeChange"
          >
            <v-btn value="table" size="small">
              <v-icon>mdi-table</v-icon>
              <v-tooltip activator="parent" location="bottom">Таблица</v-tooltip>
            </v-btn>
            <v-btn value="tree" size="small">
              <v-icon>mdi-file-tree</v-icon>
              <v-tooltip activator="parent" location="bottom">Дерево</v-tooltip>
            </v-btn>
          </v-btn-toggle>

          <!-- Clear Filters -->
          <v-btn
            v-if="hasActiveFilters"
            icon="mdi-filter-remove"
            size="small"
            variant="text"
            class="flex-shrink-0"
            @click="clearFilters"
          >
            <v-icon>mdi-filter-remove</v-icon>
            <v-tooltip activator="parent" location="bottom">Очистить фильтры</v-tooltip>
          </v-btn>
        </v-col>
      </v-row>

      <!-- Row 4: Active Filters Chips -->
      <v-row v-if="hasActiveFilters" dense>
        <v-col cols="12">
          <div class="active-filters-container">
            <span class="text-caption text-medium-emphasis mr-2 flex-shrink-0">
              Активные фильтры:
            </span>
            <div class="filters-chips-wrapper">
              <v-chip
                v-if="localFilters.search"
                size="small"
                closable
                variant="tonal"
                class="ma-1"
                @click:close="clearSearch"
              >
                Поиск: {{ localFilters.search }}
              </v-chip>

              <v-chip
                v-for="dept in localFilters.departments"
                :key="dept"
                size="small"
                closable
                variant="tonal"
                color="primary"
                class="ma-1"
                @click:close="removeDepartment(dept)"
              >
                {{ dept }}
              </v-chip>

              <v-chip
                v-if="localFilters.status !== 'all'"
                size="small"
                closable
                variant="tonal"
                color="secondary"
                class="ma-1"
                @click:close="clearStatus"
              >
                Статус: {{ getStatusLabel(localFilters.status) }}
              </v-chip>

              <v-chip
                v-if="localFilters.dateRange"
                size="small"
                closable
                variant="tonal"
                color="info"
                class="ma-1"
                @click:close="clearDateRange"
              >
                {{ formatDateRangeChip(localFilters.dateRange) }}
              </v-chip>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProfilesStore } from '@/stores/profiles'
import BaseCard from '@/components/common/BaseCard.vue'
import DateRangeFilter from './DateRangeFilter.vue'
import type { ProfileFilters, StatusFilter, ViewMode, DateRangeFilter as DateRangeFilterType } from '@/types/unified'

// Store
const profilesStore = useProfilesStore()

// State
const localFilters = ref<ProfileFilters>({
  search: '',
  departments: [],
  status: 'all',
  dateRange: null
})

const localViewMode = ref<ViewMode>('table')

// Computed
const departmentItems = computed(() => {
  return profilesStore.departments.map(dept => ({
    title: dept,
    value: dept
  }))
})

const statusItems = computed(() => [
  { title: 'Все статусы', value: 'all', icon: 'mdi-filter-outline', color: 'default' },
  { title: 'Сгенерирован', value: 'generated', icon: 'mdi-check-circle', color: 'success' },
  { title: 'Не сгенерирован', value: 'not_generated', icon: 'mdi-help-circle', color: 'grey' },
  { title: 'Генерируется', value: 'generating', icon: 'mdi-clock-outline', color: 'warning' }
])

const allDepartmentsSelected = computed(() => {
  return departmentItems.value.length > 0 &&
    localFilters.value.departments.length === departmentItems.value.length
})

const someDepartmentsSelected = computed(() => {
  return localFilters.value.departments.length > 0 && !allDepartmentsSelected.value
})

const hasActiveFilters = computed(() => {
  return (
    localFilters.value.search !== '' ||
    localFilters.value.departments.length > 0 ||
    localFilters.value.status !== 'all' ||
    localFilters.value.dateRange !== null
  )
})

// Initialize from store
onMounted(() => {
  localFilters.value = { ...profilesStore.unifiedFilters }
  localViewMode.value = profilesStore.viewMode
})

// Watch store changes
watch(
  () => profilesStore.unifiedFilters,
  (newFilters) => {
    localFilters.value = { ...newFilters }
  },
  { deep: true }
)

watch(() => profilesStore.viewMode, (newMode) => {
  localViewMode.value = newMode
})

// Methods

/**
 * Handle search input change
 * Triggers filter update in store
 */
function onSearchChange(): void {
  onFilterChange()
}

/**
 * Sync local filters to store
 * Emits filter change event to parent store for unified positions update
 */
function onFilterChange(): void {
  profilesStore.unifiedFilters = { ...localFilters.value }
}

/**
 * Handle view mode toggle between table and tree
 *
 * @param mode - ViewMode ('table' | 'tree')
 */
function onViewModeChange(mode: ViewMode): void {
  profilesStore.viewMode = mode
}

/**
 * Toggle all departments selection
 * If all selected: deselects all
 * If none/some selected: selects all
 */
function toggleAllDepartments(): void {
  if (allDepartmentsSelected.value) {
    localFilters.value.departments = []
  } else {
    localFilters.value.departments = departmentItems.value.map(d => d.value)
  }
  onFilterChange()
}

/**
 * Remove specific department from filter
 *
 * @param dept - Department name to remove
 */
function removeDepartment(dept: string): void {
  localFilters.value.departments = localFilters.value.departments.filter(d => d !== dept)
  onFilterChange()
}

/**
 * Clear search filter
 * Resets search input to empty string
 */
function clearSearch(): void {
  localFilters.value.search = ''
  onFilterChange()
}

/**
 * Clear status filter
 * Resets status to 'all' (show all statuses)
 */
function clearStatus(): void {
  localFilters.value.status = 'all'
  onFilterChange()
}

/**
 * Clear date range filter
 * Removes date range constraint
 */
function clearDateRange(): void {
  localFilters.value.dateRange = null
  onFilterChange()
}

/**
 * Clear all active filters
 * Resets all filters to default state
 * - Search: empty
 * - Departments: none
 * - Status: all
 * - Date range: none
 */
function clearFilters(): void {
  localFilters.value = {
    search: '',
    departments: [],
    status: 'all',
    dateRange: null
  }
  onFilterChange()
}

/**
 * Get localized status label
 *
 * @param status - Status filter value
 * @returns Localized status label (e.g., 'Сгенерирован', 'Не сгенерирован')
 */
function getStatusLabel(status: StatusFilter): string {
  const item = statusItems.value.find(s => s.value === status)
  return item?.title || status
}

/**
 * Format date range for chip display
 *
 * @param dateRange - Date range filter object
 * @returns Formatted string (e.g., 'Создано: 01.01.2024 - 31.01.2024')
 */
function formatDateRangeChip(dateRange: DateRangeFilterType): string {
  const typeLabel = dateRange.type === 'created' ? 'Создано' : 'Обновлено'
  const from = dateRange.from ? new Date(dateRange.from).toLocaleDateString('ru-RU') : '...'
  const to = dateRange.to ? new Date(dateRange.to).toLocaleDateString('ru-RU') : '...'
  return `${typeLabel}: ${from} - ${to}`
}
</script>

<style scoped>
/* Utility classes */
.gap-2 {
  gap: 8px;
}

.gap-4 {
  gap: 16px;
}

/* Active filters container */
.active-filters-container {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px 0;
}

.filters-chips-wrapper {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  flex: 1;
  margin: -4px; /* Compensate for chip margins */
}

/* Responsive adjustments */
@media (max-width: 1279px) {
  /* Large screens and below */
  .v-col.d-flex.align-center {
    justify-content: flex-start !important;
  }
}

@media (max-width: 959px) {
  /* Medium screens and below */
  .gap-2 {
    gap: 4px;
  }

  .active-filters-container {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 599px) {
  /* Small screens (mobile) */
  .v-btn-toggle {
    width: 100%;
  }

  .gap-2 {
    flex-direction: column;
    width: 100%;
  }

  .gap-2 > * {
    width: 100%;
  }

  /* Stack action buttons vertically on mobile */
  .v-col.d-flex.align-center.gap-2 {
    flex-direction: column;
    gap: 8px;
  }

  .flex-shrink-0 {
    width: 100%;
  }
}

/* Ensure cards and inputs don't overflow */
.filter-bar :deep(.v-field) {
  min-width: 0;
}

.filter-bar :deep(.v-select__selection) {
  max-width: 100%;
}
</style>

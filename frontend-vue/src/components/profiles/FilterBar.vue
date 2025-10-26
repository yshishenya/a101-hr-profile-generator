<template>
  <v-card class="filter-bar" elevation="1">
    <v-card-text>
      <v-row dense align="center">
        <!-- Search Input -->
        <v-col cols="12" sm="6" md="4">
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

        <!-- Department Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-select
            v-model="localFilters.department"
            :items="departmentItems"
            prepend-inner-icon="mdi-office-building"
            placeholder="Все подразделения"
            density="comfortable"
            variant="outlined"
            hide-details
            clearable
            @update:model-value="onFilterChange"
          />
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

        <!-- View Mode Toggle & Clear Filters -->
        <v-col cols="12" sm="6" md="2" class="d-flex justify-end align-center gap-2">
          <!-- View Mode Toggle -->
          <v-btn-toggle
            v-model="localViewMode"
            density="comfortable"
            mandatory
            variant="outlined"
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
            @click="clearFilters"
          >
            <v-icon>mdi-filter-remove</v-icon>
            <v-tooltip activator="parent" location="bottom">Очистить фильтры</v-tooltip>
          </v-btn>
        </v-col>
      </v-row>

      <!-- Active Filters Chips -->
      <v-row v-if="hasActiveFilters" dense class="mt-2">
        <v-col cols="12">
          <div class="d-flex align-center gap-2 flex-wrap">
            <span class="text-caption text-medium-emphasis">Активные фильтры:</span>

            <v-chip
              v-if="localFilters.search"
              size="small"
              closable
              @click:close="localFilters.search = ''; onFilterChange()"
            >
              Поиск: {{ localFilters.search }}
            </v-chip>

            <v-chip
              v-if="localFilters.department"
              size="small"
              closable
              @click:close="localFilters.department = null; onFilterChange()"
            >
              Подразделение: {{ localFilters.department }}
            </v-chip>

            <v-chip
              v-if="localFilters.status !== 'all'"
              size="small"
              closable
              @click:close="localFilters.status = 'all'; onFilterChange()"
            >
              Статус: {{ getStatusLabel(localFilters.status) }}
            </v-chip>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useProfilesStore } from '@/stores/profiles'
import type { ProfileFilters, StatusFilter, ViewMode } from '@/types/unified'

// Store
const profilesStore = useProfilesStore()

// Local state (synced with store)
const localFilters = ref<ProfileFilters>({
  search: '',
  department: null,
  status: 'all'
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
  {
    title: 'Все статусы',
    value: 'all',
    icon: 'mdi-filter-outline',
    color: 'default'
  },
  {
    title: 'Сгенерирован',
    value: 'generated',
    icon: 'mdi-check-circle',
    color: 'success'
  },
  {
    title: 'Не сгенерирован',
    value: 'not_generated',
    icon: 'mdi-help-circle',
    color: 'grey'
  },
  {
    title: 'Генерируется',
    value: 'generating',
    icon: 'mdi-clock-outline',
    color: 'warning'
  }
])

const hasActiveFilters = computed(() => {
  return (
    localFilters.value.search !== '' ||
    localFilters.value.department !== null ||
    localFilters.value.status !== 'all'
  )
})

// Initialize from store
onMounted(() => {
  localFilters.value = { ...profilesStore.unifiedFilters }
  localViewMode.value = profilesStore.viewMode
})

// Watch store changes (for external updates)
watch(
  () => profilesStore.unifiedFilters,
  (newFilters) => {
    localFilters.value = { ...newFilters }
  },
  { deep: true }
)

watch(
  () => profilesStore.viewMode,
  (newMode) => {
    localViewMode.value = newMode
  }
)

// Methods
function onSearchChange() {
  // Debounced search will be handled by watcher
  onFilterChange()
}

function onFilterChange() {
  // Update store filters
  profilesStore.unifiedFilters = { ...localFilters.value }
}

function onViewModeChange(mode: ViewMode) {
  profilesStore.viewMode = mode
}

function clearFilters() {
  localFilters.value = {
    search: '',
    department: null,
    status: 'all'
  }
  onFilterChange()
}

function getStatusLabel(status: StatusFilter): string {
  const item = statusItems.value.find(s => s.value === status)
  return item?.title || status
}
</script>

<style scoped>
.filter-bar {
  background: rgb(var(--v-theme-surface));
}

.gap-2 {
  gap: 8px;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .v-btn-toggle {
    width: 100%;
  }
}
</style>

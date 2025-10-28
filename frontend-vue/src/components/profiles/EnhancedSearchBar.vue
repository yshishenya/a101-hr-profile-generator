<template>
  <v-card flat class="search-bar px-4 py-3">
    <v-row no-gutters align="center">
      <!-- Search Input -->
      <v-col>
        <v-text-field
          :model-value="searchQuery"
          placeholder="Поиск по названию позиции или подразделению..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          hide-details
          clearable
          aria-label="Поиск позиций"
          @update:model-value="handleSearchInput"
          @keyup.enter="handleEnter"
          @keyup.shift.enter.prevent="handleShiftEnter"
        >
          <template #append-inner>
            <!-- Results Counter Badge -->
            <v-chip
              v-if="isSearching"
              size="small"
              :color="totalResults > 0 ? 'primary' : 'error'"
              variant="flat"
              class="mr-2"
            >
              {{ totalResults }}
            </v-chip>

            <!-- Navigation Buttons -->
            <div v-if="hasResults" class="d-flex gap-1 mr-2">
              <v-btn
                icon
                size="x-small"
                variant="text"
                :disabled="totalResults <= 1"
                aria-label="Предыдущий результат (Shift+Enter)"
                @click="$emit('previous')"
              >
                <v-icon size="small">mdi-chevron-left</v-icon>
                <v-tooltip activator="parent" location="bottom">
                  Предыдущий (Shift+Enter)
                </v-tooltip>
              </v-btn>

              <v-btn
                icon
                size="x-small"
                variant="text"
                :disabled="totalResults <= 1"
                aria-label="Следующий результат (Enter)"
                @click="$emit('next')"
              >
                <v-icon size="small">mdi-chevron-right</v-icon>
                <v-tooltip activator="parent" location="bottom">
                  Следующий (Enter)
                </v-tooltip>
              </v-btn>

              <!-- Current/Total Label -->
              <v-chip size="x-small" variant="text" class="px-1">
                {{ navigationLabel }}
              </v-chip>
            </div>

            <!-- Filters Menu -->
            <v-menu offset-y>
              <template #activator="{ props: menuProps }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  aria-label="Фильтры поиска"
                  v-bind="menuProps"
                >
                  <v-badge
                    :content="activeFiltersCount"
                    :model-value="activeFiltersCount > 0"
                    color="primary"
                    offset-x="-2"
                    offset-y="-2"
                  >
                    <v-icon>mdi-filter-variant</v-icon>
                  </v-badge>
                  <v-tooltip activator="parent" location="bottom">
                    Фильтры поиска
                  </v-tooltip>
                </v-btn>
              </template>

              <v-list density="compact" class="py-2">
                <v-list-subheader>Наличие профиля</v-list-subheader>
                <v-list-item>
                  <v-checkbox
                    :model-value="filters.withProfile"
                    label="С профилем"
                    density="compact"
                    hide-details
                    @update:model-value="updateFilter('withProfile', $event)"
                  />
                </v-list-item>
                <v-list-item>
                  <v-checkbox
                    :model-value="filters.withoutProfile"
                    label="Без профиля"
                    density="compact"
                    hide-details
                    @update:model-value="updateFilter('withoutProfile', $event)"
                  />
                </v-list-item>

                <v-divider class="my-2" />

                <v-list-subheader>Параметры</v-list-subheader>
                <v-list-item>
                  <v-checkbox
                    :model-value="filters.exactMatch"
                    label="Точное совпадение"
                    density="compact"
                    hide-details
                    @update:model-value="updateFilter('exactMatch', $event)"
                  />
                </v-list-item>

                <v-divider class="my-2" />

                <v-list-item>
                  <v-btn
                    block
                    size="small"
                    variant="text"
                    color="primary"
                    :disabled="activeFiltersCount === 0"
                    @click="$emit('reset-filters')"
                  >
                    Сбросить фильтры
                  </v-btn>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-text-field>
      </v-col>

      <v-spacer />

      <!-- View Toggle -->
      <v-col cols="auto" class="ml-4">
        <v-btn-toggle
          :model-value="viewMode"
          mandatory
          density="compact"
          variant="outlined"
          @update:model-value="$emit('update:viewMode', $event)"
        >
          <v-btn value="tree" size="small">
            <v-icon>mdi-file-tree</v-icon>
            <span class="ml-1">Дерево</span>
          </v-btn>
          <v-btn value="table" size="small">
            <v-icon>mdi-table</v-icon>
            <span class="ml-1">Таблица</span>
          </v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ViewMode } from '@/types/unified'
import type { SearchFilters } from '@/composables/useSearch'

// Props
interface Props {
  searchQuery: string
  viewMode: ViewMode
  totalResults: number
  navigationLabel: string
  hasResults: boolean
  isSearching: boolean
  filters: SearchFilters
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:searchQuery': [value: string]
  'update:viewMode': [value: ViewMode]
  'search': []
  'next': []
  'previous': []
  'update:filters': [filters: SearchFilters]
  'reset-filters': []
}>()

// Computed
const activeFiltersCount = computed(() => {
  let count = 0
  if (props.filters.withProfile) count++
  if (props.filters.withoutProfile) count++
  if (props.filters.exactMatch) count++
  return count
})

// Methods
function handleSearchInput(value: string | null): void {
  const searchValue = value || ''
  emit('update:searchQuery', searchValue)
}

function updateFilter(key: keyof SearchFilters, value: boolean | null): void {
  // Handle Vuetify checkbox null values
  const newFilters = { ...props.filters, [key]: value ?? false }
  emit('update:filters', newFilters)
}

/**
 * Handles Enter key press - navigate to next result
 */
function handleEnter(): void {
  if (props.hasResults) {
    emit('next')
  } else {
    emit('search')
  }
}

/**
 * Handles Shift+Enter key press - navigate to previous result
 */
function handleShiftEnter(): void {
  if (props.hasResults) {
    emit('previous')
  }
}
</script>

<style scoped>
.search-bar {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
}

.gap-1 {
  gap: 4px;
}
</style>

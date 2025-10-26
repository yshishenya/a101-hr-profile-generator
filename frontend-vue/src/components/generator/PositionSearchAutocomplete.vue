<template>
  <v-autocomplete
    v-model="selectedItem"
    v-model:search="searchQuery"
    :items="filteredResults"
    :loading="isSearching"
    :disabled="disabled"
    item-title="position_name"
    item-value="position_id"
    return-object
    clearable
    auto-select-first
    label="Search for a position"
    placeholder="Start typing to search..."
    prepend-inner-icon="mdi-magnify"
    variant="outlined"
    density="comfortable"
    :no-data-text="noDataText"
    @update:model-value="handleSelection"
  >
    <template #item="{ props, item }">
      <v-list-item
        v-bind="props"
        :title="item.raw.position_name"
        :subtitle="item.raw.department_path"
      >
        <template #prepend>
          <v-avatar :color="item.raw.profile_exists ? 'success' : 'grey-darken-1'" size="small">
            <v-icon size="small">
              {{ item.raw.profile_exists ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
          </v-avatar>
        </template>

        <template #append v-if="item.raw.profile_exists">
          <v-chip size="x-small" color="success" variant="flat">
            Profile exists
          </v-chip>
        </template>
      </v-list-item>
    </template>

    <template #chip="{ item }">
      <v-chip>
        {{ item.raw.position_name }}
      </v-chip>
    </template>
  </v-autocomplete>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { logger } from '@/utils/logger'
import type { SearchableItem } from '@/stores/catalog'
import Fuse from 'fuse.js'
import { useDebounceFn } from '@vueuse/core'

// Constants
const SEARCH_DEBOUNCE_MS = 300
const FUZZY_SEARCH_THRESHOLD = 0.3
const FUZZY_SEARCH_DISTANCE = 100
const MIN_SEARCH_LENGTH = 2
const DEFAULT_MAX_RESULTS = 50
const POSITION_NAME_WEIGHT = 2
const BUSINESS_UNIT_WEIGHT = 1.5
const DEPARTMENT_PATH_WEIGHT = 1

// Props
interface Props {
  modelValue?: SearchableItem | null
  disabled?: boolean
  maxResults?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  disabled: false,
  maxResults: DEFAULT_MAX_RESULTS
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: SearchableItem | null]
  'select': [value: SearchableItem]
}>()

// Store
const catalogStore = useCatalogStore()

// State
const selectedItem = ref<SearchableItem | null>(props.modelValue)
const searchQuery = ref<string>('')
const filteredResults = ref<SearchableItem[]>([])
const isSearching = ref<boolean>(false)

// Fuse.js instance for fuzzy search
const fuse = computed(() => {
  return new Fuse(catalogStore.searchableItems, {
    keys: [
      { name: 'position_name', weight: POSITION_NAME_WEIGHT },
      { name: 'business_unit_name', weight: BUSINESS_UNIT_WEIGHT },
      { name: 'department_path', weight: DEPARTMENT_PATH_WEIGHT }
    ],
    threshold: FUZZY_SEARCH_THRESHOLD,
    distance: FUZZY_SEARCH_DISTANCE,
    minMatchCharLength: MIN_SEARCH_LENGTH,
    includeScore: true,
    useExtendedSearch: false
  })
})

// Computed
const noDataText = computed(() => {
  if (catalogStore.isLoading) {
    return 'Loading positions...'
  }
  if (searchQuery.value && searchQuery.value.length < MIN_SEARCH_LENGTH) {
    return `Type at least ${MIN_SEARCH_LENGTH} characters to search`
  }
  if (searchQuery.value && filteredResults.value.length === 0) {
    return 'No positions found'
  }
  return 'Start typing to search'
})

// Watch for external modelValue changes
watch(() => props.modelValue, (newValue) => {
  selectedItem.value = newValue
})

// Watch for selection changes
watch(selectedItem, (newValue) => {
  emit('update:modelValue', newValue)
})

// Debounced search handler
const handleSearch = useDebounceFn((query: string) => {
  if (!query || query.trim().length < MIN_SEARCH_LENGTH) {
    filteredResults.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true

  try {
    // Perform fuzzy search
    const results = fuse.value.search(query, { limit: props.maxResults })

    // Extract items from Fuse results and sort by score
    filteredResults.value = results
      .map(result => result.item)
      .sort((a, b) => {
        // Sort by profile_exists (positions without profiles first)
        if (a.profile_exists !== b.profile_exists) {
          return a.profile_exists ? 1 : -1
        }
        // Then alphabetically by position name
        return a.position_name.localeCompare(b.position_name)
      })
  } catch (error) {
    logger.error('Search error', error)
    filteredResults.value = []
  } finally {
    isSearching.value = false
  }
}, SEARCH_DEBOUNCE_MS)

// Watch search query and trigger debounced search
watch(searchQuery, (newQuery) => {
  handleSearch(newQuery)
})

// Handle selection
function handleSelection(item: SearchableItem | null): void {
  if (item) {
    emit('select', item)
  }
}
</script>

<style scoped>
:deep(mark) {
  background-color: rgb(var(--v-theme-primary));
  color: white;
  padding: 0 2px;
  border-radius: 2px;
}

:deep(.v-list-item) {
  min-height: 64px;
}

:deep(.v-list-item__subtitle) {
  font-size: 0.75rem;
  opacity: 0.7;
}
</style>

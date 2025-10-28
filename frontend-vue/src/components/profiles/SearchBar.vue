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
          @update:model-value="handleSearchInput"
          @keyup.enter="handleSearchSubmit"
        >
          <template #append-inner>
            <v-btn
              variant="text"
              size="small"
              color="primary"
              :disabled="!searchQuery"
              @click="handleSearchSubmit"
            >
              Поиск
            </v-btn>
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
import { ref } from 'vue'
import type { ViewMode } from '@/types/unified'

// Props
interface Props {
  searchQuery?: string
  viewMode: ViewMode
}

const props = withDefaults(defineProps<Props>(), {
  searchQuery: ''
})

// Emits
const emit = defineEmits<{
  'update:searchQuery': [value: string]
  'update:viewMode': [value: ViewMode]
  'search': [query: string]
}>()

// Local state for input
const localSearch = ref(props.searchQuery)

// Methods
function handleSearchInput(value: string | null): void {
  const searchValue = value || ''
  localSearch.value = searchValue
  emit('update:searchQuery', searchValue)
}

function handleSearchSubmit(): void {
  emit('search', localSearch.value)
}
</script>

<style scoped>
.search-bar {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
}
</style>

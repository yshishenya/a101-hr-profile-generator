<template>
  <div class="competencies-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-chip
        v-for="(item, index) in localItems"
        :key="index"
        class="ma-1"
        variant="outlined"
      >
        {{ item }}
      </v-chip>

      <div v-if="localItems.length === 0" class="text-body-2 text-medium-emphasis">
        Нет данных. Нажмите "Редактировать" для добавления.
      </div>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <v-combobox
        v-model="localItems"
        chips
        closable-chips
        multiple
        variant="outlined"
        :label="label"
        :hint="hint"
        :placeholder="placeholder"
        :items="suggestions"
        persistent-hint
        class="mb-3"
        @update:model-value="handleUpdate"
      >
        <template #chip="{ props: chipProps, item }">
          <v-chip
            v-bind="chipProps"
            closable
            variant="flat"
            color="primary"
            @click:close="removeItem(item.value)"
          >
            {{ item.value }}
          </v-chip>
        </template>

        <template #prepend-inner>
          <v-icon>{{ icon }}</v-icon>
        </template>
      </v-combobox>

      <!-- Helper Text -->
      <div class="text-caption text-medium-emphasis mb-3">
        💡 {{ helperText }}
      </div>

      <!-- Statistics -->
      <v-alert
        v-if="showStats"
        type="info"
        variant="tonal"
        density="compact"
      >
        <div class="text-caption">
          Добавлено: {{ localItems.length }} {{ itemsLabel }}
          <span v-if="minItems && localItems.length < minItems" class="text-warning">
            (минимум: {{ minItems }})
          </span>
          <span v-if="maxItems && localItems.length > maxItems" class="text-error">
            (максимум: {{ maxItems }})
          </span>
        </div>
      </v-alert>

      <!-- Popular Suggestions (if available) -->
      <div v-if="suggestions.length > 0 && showPopularSuggestions" class="mt-4">
        <div class="text-subtitle-2 mb-2">Популярные варианты:</div>
        <v-chip
          v-for="(suggestion, index) in popularSuggestions"
          :key="index"
          class="ma-1"
          size="small"
          variant="outlined"
          :disabled="localItems.includes(suggestion)"
          @click="addSuggestion(suggestion)"
        >
          <v-icon size="small" class="mr-1">mdi-plus</v-icon>
          {{ suggestion }}
        </v-chip>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

// Props
interface Props {
  modelValue: string[]
  readonly?: boolean
  label?: string
  hint?: string
  placeholder?: string
  icon?: string
  helperText?: string
  itemsLabel?: string
  minItems?: number
  maxItems?: number
  showStats?: boolean
  showPopularSuggestions?: boolean
  suggestions?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
  label: 'Добавьте элементы',
  hint: 'Нажмите Enter для добавления нового элемента',
  placeholder: 'Начните вводить...',
  icon: 'mdi-tag-multiple',
  helperText: 'Нажмите Enter после ввода каждого элемента',
  itemsLabel: 'элементов',
  minItems: undefined,
  maxItems: undefined,
  showStats: true,
  showPopularSuggestions: true,
  suggestions: () => [],
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

// Local state
const localItems = ref<string[]>([...(props.modelValue || [])])

// Computed
const popularSuggestions = computed(() => {
  // Show only first 10 suggestions that aren't already added
  return props.suggestions
    .filter((s) => !localItems.value.includes(s))
    .slice(0, 10)
})

// Methods
function handleUpdate(): void {
  // Clean up empty strings
  localItems.value = localItems.value.filter((item) => item && item.trim() !== '')

  emit('update:modelValue', localItems.value)
}

function removeItem(item: string): void {
  localItems.value = localItems.value.filter((i) => i !== item)
  handleUpdate()
}

function addSuggestion(suggestion: string): void {
  if (!localItems.value.includes(suggestion)) {
    localItems.value.push(suggestion)
    handleUpdate()
  }
}

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    if (JSON.stringify(newValue) !== JSON.stringify(localItems.value)) {
      localItems.value = [...(newValue || [])]
    }
  },
  { deep: true }
)
</script>

<style scoped>
.competencies-editor {
  min-height: 100px;
}

.readonly-view {
  padding: 8px 0;
}

.edit-mode {
  padding: 0;
}

/* Hover effect for read-only chips */
.readonly-view .v-chip {
  transition: all 0.2s ease;
}

.readonly-view .v-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

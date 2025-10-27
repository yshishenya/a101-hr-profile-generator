<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    location="bottom"
    offset="4"
  >
    <template #activator="{ props: activatorProps }">
      <v-text-field
        :model-value="displayValue"
        prepend-inner-icon="mdi-calendar-range"
        placeholder="Выберите диапазон дат"
        density="comfortable"
        variant="outlined"
        hide-details
        readonly
        clearable
        v-bind="activatorProps"
        @click:clear="clearDateRange"
      >
        <template #append-inner>
          <v-icon>mdi-menu-down</v-icon>
        </template>
      </v-text-field>
    </template>

    <v-card min-width="400" max-width="600">
      <v-card-title class="d-flex align-center justify-space-between">
        <span>Фильтр по дате</span>
        <v-btn
          icon="mdi-close"
          size="small"
          variant="text"
          @click="menu = false"
        />
      </v-card-title>

      <v-card-text>
        <!-- Date Type Selector -->
        <v-btn-toggle
          v-model="localDateType"
          density="comfortable"
          mandatory
          variant="outlined"
          class="mb-4"
          style="width: 100%"
        >
          <v-btn value="created" style="flex: 1">
            <v-icon start>mdi-calendar-plus</v-icon>
            Дата создания
          </v-btn>
          <v-btn value="updated" style="flex: 1">
            <v-icon start>mdi-calendar-edit</v-icon>
            Дата обновления
          </v-btn>
        </v-btn-toggle>

        <!-- Quick Presets -->
        <div class="mb-4">
          <div class="text-caption text-medium-emphasis mb-2">Быстрый выбор:</div>
          <v-chip-group
            v-model="selectedPreset"
            filter
            mandatory
            @update:model-value="onPresetChange"
          >
            <v-chip
              v-for="preset in datePresets"
              :key="preset.value"
              :value="preset.value"
              size="small"
            >
              {{ preset.label }}
            </v-chip>
          </v-chip-group>
        </div>

        <!-- Custom Date Range (only show for custom preset) -->
        <div v-if="selectedPreset === 'custom'" class="date-pickers">
          <v-row dense>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis mb-1">От:</div>
              <input
                v-model="localFromDate"
                type="date"
                class="date-input"
                :max="localToDate || undefined"
              >
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-medium-emphasis mb-1">До:</div>
              <input
                v-model="localToDate"
                type="date"
                class="date-input"
                :min="localFromDate || undefined"
              >
            </v-col>
          </v-row>
        </div>

        <!-- Current Range Display -->
        <v-alert
          v-if="localFromDate || localToDate"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          <div class="text-caption">
            <strong>Выбранный период:</strong>
            {{ formatDateRange(localFromDate, localToDate) }}
          </div>
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-btn
          variant="text"
          @click="clearDateRange"
        >
          Очистить
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          variant="elevated"
          @click="applyDateRange"
        >
          Применить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { DateRangeFilter, DateRangePreset } from '@/types/unified'

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: DateRangeFilter | null]
}>()

// Constants
const DATE_PRESETS = [
  { label: 'Последние 7 дней', value: 'last_7_days' as DateRangePreset },
  { label: 'Последние 30 дней', value: 'last_30_days' as DateRangePreset },
  { label: 'Последние 90 дней', value: 'last_90_days' as DateRangePreset },
  { label: 'Все время', value: 'all_time' as DateRangePreset },
  { label: 'Произвольный', value: 'custom' as DateRangePreset }
]

// Props
interface Props {
  modelValue: DateRangeFilter | null
}
// State
const menu = ref(false)
const localDateType = ref<'created' | 'updated'>('created')
const selectedPreset = ref<DateRangePreset>('all_time')
const localFromDate = ref<string | null>(null)
const localToDate = ref<string | null>(null)

// Computed
const datePresets = computed(() => DATE_PRESETS)

const displayValue = computed(() => {
  if (!props.modelValue || (!props.modelValue.from && !props.modelValue.to)) {
    return ''
  }

  const typeLabel = props.modelValue.type === 'created' ? 'Создано' : 'Обновлено'
  const rangeLabel = formatDateRange(props.modelValue.from, props.modelValue.to)
  return `${typeLabel}: ${rangeLabel}`
})

// Initialize from props
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      localDateType.value = newValue.type
      localFromDate.value = newValue.from
      localToDate.value = newValue.to

      // Determine which preset is active
      if (!newValue.from && !newValue.to) {
        selectedPreset.value = 'all_time'
      } else {
        selectedPreset.value = 'custom'
      }
    } else {
      localDateType.value = 'created'
      localFromDate.value = null
      localToDate.value = null
      selectedPreset.value = 'all_time'
    }
  },
  { immediate: true }
)

// Methods
/**
 * Format date range for display
 */
function formatDateRange(from: string | null, to: string | null): string {
  if (!from && !to) {
    return 'Все время'
  }

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  if (from && to) {
    return `${formatDate(from)} - ${formatDate(to)}`
  } else if (from) {
    return `с ${formatDate(from)}`
  } else {
    return `до ${formatDate(to)}`
  }
}

/**
 * Calculate date range based on preset
 */
function calculatePresetDates(preset: DateRangePreset): { from: string | null; to: string | null } {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  switch (preset) {
    case 'last_7_days': {
      const from = new Date(today)
      from.setDate(from.getDate() - 7)
      return {
        from: (from.toISOString().split('T')[0] || null) as string | null,
        to: (today.toISOString().split('T')[0] || null) as string | null
      }
    }
    case 'last_30_days': {
      const from = new Date(today)
      from.setDate(from.getDate() - 30)
      return {
        from: (from.toISOString().split('T')[0] || null) as string | null,
        to: (today.toISOString().split('T')[0] || null) as string | null
      }
    }
    case 'last_90_days': {
      const from = new Date(today)
      from.setDate(from.getDate() - 90)
      return {
        from: (from.toISOString().split('T')[0] || null) as string | null,
        to: (today.toISOString().split('T')[0] || null) as string | null
      }
    }
    case 'all_time':
      return { from: null, to: null }
    case 'custom':
      return { from: localFromDate.value || null, to: localToDate.value || null }
    default:
      return { from: null, to: null }
  }
}

/**
 * Handle preset selection
 */
function onPresetChange(preset: DateRangePreset): void {
  if (preset !== 'custom') {
    const dates = calculatePresetDates(preset)
    localFromDate.value = dates.from
    localToDate.value = dates.to
  }
  // For 'custom', keep current localFromDate and localToDate values
}

/**
 * Apply date range filter
 */
function applyDateRange(): void {
  if (!localFromDate.value && !localToDate.value) {
    // No dates selected - clear filter
    emit('update:modelValue', null)
  } else {
    emit('update:modelValue', {
      type: localDateType.value,
      from: localFromDate.value,
      to: localToDate.value
    })
  }
  menu.value = false
}

/**
 * Clear date range filter
 */
function clearDateRange(): void {
  localFromDate.value = null
  localToDate.value = null
  selectedPreset.value = 'all_time'
  emit('update:modelValue', null)
  menu.value = false
}
</script>

<style scoped>
.date-pickers {
  margin-top: 8px;
}

.date-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  background-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-on-surface));
}

.date-input:focus {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: -1px;
}

.date-input:hover {
  border-color: rgba(var(--v-border-color), calc(var(--v-border-opacity) * 1.5));
}

/* Dark theme support */
:deep(.v-theme--dark) .date-input {
  color-scheme: dark;
}
</style>

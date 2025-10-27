<template>
  <div class="performance-metrics-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-list lines="two">
        <!-- Quantitative KPIs -->
        <v-list-item prepend-icon="mdi-chart-line">
          <v-list-item-title class="mb-2">Количественные KPI</v-list-item-title>
          <v-list class="pa-0" density="compact">
            <v-list-item
              v-for="(kpi, idx) in localData.quantitative_kpis"
              :key="idx"
              class="px-0"
            >
              <template #prepend>
                <v-icon size="small" color="primary">mdi-checkbox-marked-circle</v-icon>
              </template>
              <v-list-item-subtitle class="text-wrap">{{ kpi }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="localData.quantitative_kpis.length === 0" class="px-0">
              <v-list-item-subtitle class="text-medium-emphasis">Не указано</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-list-item>

        <v-divider />

        <!-- Qualitative Indicators -->
        <v-list-item prepend-icon="mdi-star-check">
          <v-list-item-title class="mb-2">Качественные показатели</v-list-item-title>
          <v-list class="pa-0" density="compact">
            <v-list-item
              v-for="(indicator, idx) in localData.qualitative_indicators"
              :key="idx"
              class="px-0"
            >
              <template #prepend>
                <v-icon size="small" color="success">mdi-checkbox-marked-circle</v-icon>
              </template>
              <v-list-item-subtitle class="text-wrap">{{ indicator }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="localData.qualitative_indicators.length === 0" class="px-0">
              <v-list-item-subtitle class="text-medium-emphasis">Не указано</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-list-item>

        <v-divider />

        <!-- Evaluation Frequency -->
        <v-list-item
          prepend-icon="mdi-calendar-clock"
          :title="localData.evaluation_frequency || 'Не указано'"
          subtitle="Периодичность оценки"
        />
      </v-list>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Определите KPI и показатели эффективности для позиции. Используйте SMART-критерии.
        </div>
      </v-alert>

      <!-- Quantitative KPIs -->
      <div class="mb-4">
        <div class="text-subtitle-2 mb-2">
          <v-icon size="small" class="mr-2">mdi-chart-line</v-icon>
          Количественные KPI
        </div>

        <v-combobox
          v-model="localData.quantitative_kpis"
          chips
          closable-chips
          multiple
          variant="outlined"
          label="Добавить KPI"
          placeholder="Введите KPI и нажмите Enter"
          hint="Нажмите Enter после каждого показателя. Минимум 3 KPI."
          persistent-hint
          class="mb-2"
          :rules="kpiRules"
        >
          <template #chip="{ props: chipProps, item }">
            <v-chip
              v-bind="chipProps"
              closable
              color="primary"
              @click:close="removeKpi(item.value)"
            >
              {{ item.value }}
            </v-chip>
          </template>
        </v-combobox>

        <!-- Popular KPI suggestions -->
        <div class="text-caption text-medium-emphasis mb-2">Популярные метрики:</div>
        <div class="d-flex flex-wrap gap-2 mb-3">
          <v-chip
            v-for="suggestion in kpiSuggestions"
            :key="suggestion"
            size="small"
            variant="outlined"
            @click="addKpi(suggestion)"
          >
            <v-icon start size="small">mdi-plus</v-icon>
            {{ suggestion }}
          </v-chip>
        </div>

        <!-- Statistics -->
        <v-alert type="info" variant="tonal" density="compact">
          <div class="text-caption">
            Добавлено: {{ localData.quantitative_kpis.length }} KPI
            <span v-if="localData.quantitative_kpis.length < 3" class="text-warning">
              (минимум: 3)
            </span>
          </div>
        </v-alert>
      </div>

      <v-divider class="my-4" />

      <!-- Qualitative Indicators -->
      <div class="mb-4">
        <div class="text-subtitle-2 mb-2">
          <v-icon size="small" class="mr-2">mdi-star-check</v-icon>
          Качественные показатели
        </div>

        <v-combobox
          v-model="localData.qualitative_indicators"
          chips
          closable-chips
          multiple
          variant="outlined"
          label="Добавить показатель"
          placeholder="Введите показатель и нажмите Enter"
          hint="Нажмите Enter после каждого показателя. Минимум 2 показателя."
          persistent-hint
          class="mb-2"
          :rules="indicatorRules"
        >
          <template #chip="{ props: chipProps, item }">
            <v-chip
              v-bind="chipProps"
              closable
              color="success"
              @click:close="removeIndicator(item.value)"
            >
              {{ item.value }}
            </v-chip>
          </template>
        </v-combobox>

        <!-- Popular indicator suggestions -->
        <div class="text-caption text-medium-emphasis mb-2">Популярные показатели:</div>
        <div class="d-flex flex-wrap gap-2 mb-3">
          <v-chip
            v-for="suggestion in indicatorSuggestions"
            :key="suggestion"
            size="small"
            variant="outlined"
            @click="addIndicator(suggestion)"
          >
            <v-icon start size="small">mdi-plus</v-icon>
            {{ suggestion }}
          </v-chip>
        </div>

        <!-- Statistics -->
        <v-alert type="info" variant="tonal" density="compact">
          <div class="text-caption">
            Добавлено: {{ localData.qualitative_indicators.length }} показателей
            <span v-if="localData.qualitative_indicators.length < 2" class="text-warning">
              (минимум: 2)
            </span>
          </div>
        </v-alert>
      </div>

      <v-divider class="my-4" />

      <!-- Evaluation Frequency -->
      <v-select
        v-model="localData.evaluation_frequency"
        :items="frequencyOptions"
        variant="outlined"
        label="Периодичность оценки"
        density="comfortable"
        :rules="[(v: string) => !!v || 'Выберите периодичность оценки']"
      >
        <template #prepend-inner>
          <v-icon>mdi-calendar-clock</v-icon>
        </template>
      </v-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Types
interface PerformanceMetrics {
  quantitative_kpis: string[]
  qualitative_indicators: string[]
  evaluation_frequency: string
}

// Props
interface Props {
  modelValue: PerformanceMetrics
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: PerformanceMetrics]
}>()

// Local state
const localData = ref<PerformanceMetrics>({
  quantitative_kpis: [],
  qualitative_indicators: [],
  evaluation_frequency: '',
})

// Frequency options
const frequencyOptions = [
  'Ежемесячно',
  'Ежеквартально',
  'Раз в полгода',
  'Ежегодно',
]

// KPI suggestions
const kpiSuggestions = [
  'Выполнение плана продаж',
  'Количество закрытых задач',
  'Время выполнения проектов',
  'Доля выполненных задач в срок',
]

// Indicator suggestions
const indicatorSuggestions = [
  'Качество работы',
  'Удовлетворённость клиентов',
  'Инициативность',
  'Профессиональное развитие',
]

// Validation rules
const kpiRules = [
  (v: string[]) => (v && v.length >= 3) || 'Минимум 3 количественных KPI',
  (v: string[]) => (v && v.length <= 10) || 'Максимум 10 KPI',
]

const indicatorRules = [
  (v: string[]) => (v && v.length >= 2) || 'Минимум 2 качественных показателя',
  (v: string[]) => (v && v.length <= 8) || 'Максимум 8 показателей',
]

// Methods
function addKpi(kpi: string): void {
  if (!localData.value.quantitative_kpis.includes(kpi)) {
    localData.value.quantitative_kpis.push(kpi)
  }
}

function removeKpi(kpi: string): void {
  const index = localData.value.quantitative_kpis.indexOf(kpi)
  if (index > -1) {
    localData.value.quantitative_kpis.splice(index, 1)
  }
}

function addIndicator(indicator: string): void {
  if (!localData.value.qualitative_indicators.includes(indicator)) {
    localData.value.qualitative_indicators.push(indicator)
  }
}

function removeIndicator(indicator: string): void {
  const index = localData.value.qualitative_indicators.indexOf(indicator)
  if (index > -1) {
    localData.value.qualitative_indicators.splice(index, 1)
  }
}

// Initialize
function initialize(): void {
  localData.value = {
    quantitative_kpis: [...(props.modelValue?.quantitative_kpis || [])],
    qualitative_indicators: [...(props.modelValue?.qualitative_indicators || [])],
    evaluation_frequency: props.modelValue?.evaluation_frequency || '',
  }
}

// Handle updates
function handleUpdate(): void {
  emit('update:modelValue', {
    quantitative_kpis: localData.value.quantitative_kpis.filter((k) => k && k.trim()),
    qualitative_indicators: localData.value.qualitative_indicators.filter((i) => i && i.trim()),
    evaluation_frequency: localData.value.evaluation_frequency,
  })
}

// Initialize on mount
initialize()

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    const currentJson = JSON.stringify(localData.value)
    const newJson = JSON.stringify(newValue)
    if (currentJson !== newJson) {
      initialize()
    }
  },
  { deep: true }
)

// Watch for local changes
watch(
  localData,
  () => {
    handleUpdate()
  },
  { deep: true }
)
</script>

<style scoped>
.performance-metrics-editor {
  min-height: 200px;
}

.readonly-view,
.edit-mode {
  padding: 0;
}

.text-wrap {
  white-space: normal;
  word-wrap: break-word;
}

.gap-2 {
  gap: 8px;
}
</style>

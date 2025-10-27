<template>
  <div class="additional-info-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-expansion-panels variant="accordion">
        <!-- Working Conditions -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-calendar-clock</v-icon>
              <span class="font-weight-medium">Условия работы</span>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-list lines="two" density="compact">
              <v-list-item prepend-icon="mdi-clock-outline">
                <v-list-item-title>График работы</v-list-item-title>
                <v-list-item-subtitle class="text-wrap mt-1">
                  {{ localData.working_conditions.work_schedule || 'Не указано' }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item prepend-icon="mdi-home-account">
                <v-list-item-title>Удалённая работа</v-list-item-title>
                <v-list-item-subtitle class="text-wrap mt-1">
                  {{ localData.working_conditions.remote_work_options || 'Не указано' }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider />

              <v-list-item prepend-icon="mdi-airplane">
                <v-list-item-title>Командировки</v-list-item-title>
                <v-list-item-subtitle class="text-wrap mt-1">
                  {{ localData.working_conditions.business_travel || 'Не указано' }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>

        <!-- Special Requirements -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-shield-check</v-icon>
              <span class="font-weight-medium">Особые требования</span>
              <v-chip size="x-small" variant="outlined">
                {{ localData.special_requirements.length }}
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-list density="compact">
              <v-list-item
                v-for="(req, idx) in localData.special_requirements"
                :key="idx"
                class="px-0"
              >
                <template #prepend>
                  <v-icon size="small" color="warning">mdi-alert-circle</v-icon>
                </template>
                <v-list-item-subtitle class="text-wrap">{{ req }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item v-if="localData.special_requirements.length === 0" class="px-0">
                <v-list-item-subtitle class="text-medium-emphasis">Нет требований</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>

        <!-- Risk Factors -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-alert</v-icon>
              <span class="font-weight-medium">Факторы риска</span>
              <v-chip size="x-small" variant="outlined">
                {{ localData.risk_factors.length }}
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-list density="compact">
              <v-list-item
                v-for="(risk, idx) in localData.risk_factors"
                :key="idx"
                class="px-0"
              >
                <template #prepend>
                  <v-icon size="small" color="error">mdi-alert-octagon</v-icon>
                </template>
                <v-list-item-subtitle class="text-wrap">{{ risk }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item v-if="localData.risk_factors.length === 0" class="px-0">
                <v-list-item-subtitle class="text-medium-emphasis">Рисков не выявлено</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Укажите условия работы, особые требования и возможные факторы риска.
        </div>
      </v-alert>

      <!-- Working Conditions -->
      <v-card variant="outlined" class="mb-4">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-calendar-clock</v-icon>
          Условия работы
        </v-card-title>

        <v-card-text>
          <!-- Work Schedule -->
          <v-text-field
            v-model="localData.working_conditions.work_schedule"
            variant="outlined"
            label="График работы"
            placeholder="Например: 5/2 с 9:00 до 18:00"
            density="comfortable"
            class="mb-4"
            :rules="scheduleRules"
          >
            <template #prepend-inner>
              <v-icon>mdi-clock-outline</v-icon>
            </template>
          </v-text-field>

          <!-- Remote Work Options -->
          <v-textarea
            v-model="localData.working_conditions.remote_work_options"
            variant="outlined"
            label="Возможности удалённой работы"
            placeholder="Например: Гибридный режим, 2-3 дня удалённо..."
            rows="2"
            auto-grow
            class="mb-4"
            :rules="remoteWorkRules"
          >
            <template #prepend-inner>
              <v-icon>mdi-home-account</v-icon>
            </template>
          </v-textarea>

          <!-- Business Travel -->
          <v-textarea
            v-model="localData.working_conditions.business_travel"
            variant="outlined"
            label="Командировки"
            placeholder="Например: Редкие командировки по РФ (до 10%)..."
            rows="2"
            auto-grow
            :rules="businessTravelRules"
          >
            <template #prepend-inner>
              <v-icon>mdi-airplane</v-icon>
            </template>
          </v-textarea>
        </v-card-text>
      </v-card>

      <!-- Special Requirements -->
      <v-card variant="outlined" class="mb-4">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-shield-check</v-icon>
          Особые требования
        </v-card-title>

        <v-card-text>
          <v-combobox
            v-model="localData.special_requirements"
            chips
            closable-chips
            multiple
            variant="outlined"
            label="Добавить требование"
            placeholder="Введите требование и нажмите Enter"
            hint="Необязательно. Специальные требования к кандидату"
            persistent-hint
          >
            <template #chip="{ props: chipProps, item }">
              <v-chip v-bind="chipProps" closable color="warning">
                <v-icon start size="small">mdi-alert-circle</v-icon>
                {{ item.value }}
              </v-chip>
            </template>
          </v-combobox>

          <!-- Suggestions -->
          <div class="mt-2">
            <div class="text-caption text-medium-emphasis mb-1">Популярные:</div>
            <v-chip
              v-for="suggestion in requirementsSuggestions"
              :key="suggestion"
              size="small"
              variant="outlined"
              class="mr-2 mb-1"
              @click="addRequirement(suggestion)"
            >
              <v-icon start size="small">mdi-plus</v-icon>
              {{ suggestion }}
            </v-chip>
          </div>
        </v-card-text>
      </v-card>

      <!-- Risk Factors -->
      <v-card variant="outlined">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-alert</v-icon>
          Факторы риска
        </v-card-title>

        <v-card-text>
          <v-combobox
            v-model="localData.risk_factors"
            chips
            closable-chips
            multiple
            variant="outlined"
            label="Добавить фактор риска"
            placeholder="Введите фактор и нажмите Enter"
            hint="Необязательно. Потенциальные риски и сложности позиции"
            persistent-hint
          >
            <template #chip="{ props: chipProps, item }">
              <v-chip v-bind="chipProps" closable color="error">
                <v-icon start size="small">mdi-alert-octagon</v-icon>
                {{ item.value }}
              </v-chip>
            </template>
          </v-combobox>

          <!-- Suggestions -->
          <div class="mt-2">
            <div class="text-caption text-medium-emphasis mb-1">Популярные:</div>
            <v-chip
              v-for="suggestion in riskSuggestions"
              :key="suggestion"
              size="small"
              variant="outlined"
              class="mr-2 mb-1"
              @click="addRisk(suggestion)"
            >
              <v-icon start size="small">mdi-plus</v-icon>
              {{ suggestion }}
            </v-chip>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Types
interface WorkingConditions {
  work_schedule: string
  remote_work_options: string
  business_travel: string
}

interface AdditionalInfo {
  working_conditions: WorkingConditions
  special_requirements: string[]
  risk_factors: string[]
}

// Props
interface Props {
  modelValue: AdditionalInfo
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: AdditionalInfo]
}>()

// Local state
const localData = ref<AdditionalInfo>({
  working_conditions: {
    work_schedule: '',
    remote_work_options: '',
    business_travel: '',
  },
  special_requirements: [],
  risk_factors: [],
})

// Suggestions
const requirementsSuggestions = [
  'Прохождение проверки безопасности',
  'Медосмотр',
  'Знание корпоративных политик',
  'Двухфакторная аутентификация',
]

const riskSuggestions = [
  'Высокая нагрузка в периоды дедлайнов',
  'Работа с legacy-системами',
  'Зависимость от внешних подрядчиков',
  'Частые изменения приоритетов',
]

// Validation rules
const scheduleRules = [
  (v: string) => !!v || 'Укажите график работы',
  (v: string) => (v && v.length >= 5) || 'Минимум 5 символов',
  (v: string) => (v && v.length <= 200) || 'Максимум 200 символов',
]

const remoteWorkRules = [
  (v: string) => !!v || 'Укажите возможности удалённой работы',
  (v: string) => (v && v.length >= 10) || 'Минимум 10 символов',
  (v: string) => (v && v.length <= 500) || 'Максимум 500 символов',
]

const businessTravelRules = [
  (v: string) => !!v || 'Укажите информацию о командировках',
  (v: string) => (v && v.length >= 10) || 'Минимум 10 символов',
  (v: string) => (v && v.length <= 500) || 'Максимум 500 символов',
]

// Methods
function addRequirement(req: string): void {
  if (!localData.value.special_requirements.includes(req)) {
    localData.value.special_requirements.push(req)
  }
}

function addRisk(risk: string): void {
  if (!localData.value.risk_factors.includes(risk)) {
    localData.value.risk_factors.push(risk)
  }
}

// Initialize
function initialize(): void {
  localData.value = {
    working_conditions: {
      work_schedule: props.modelValue?.working_conditions?.work_schedule || '',
      remote_work_options: props.modelValue?.working_conditions?.remote_work_options || '',
      business_travel: props.modelValue?.working_conditions?.business_travel || '',
    },
    special_requirements: [...(props.modelValue?.special_requirements || [])],
    risk_factors: [...(props.modelValue?.risk_factors || [])],
  }
}

// Handle updates
function handleUpdate(): void {
  emit('update:modelValue', {
    working_conditions: {
      work_schedule: localData.value.working_conditions.work_schedule.trim(),
      remote_work_options: localData.value.working_conditions.remote_work_options.trim(),
      business_travel: localData.value.working_conditions.business_travel.trim(),
    },
    special_requirements: localData.value.special_requirements.filter((r) => r && r.trim()),
    risk_factors: localData.value.risk_factors.filter((r) => r && r.trim()),
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
.additional-info-editor {
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

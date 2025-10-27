<template>
  <div class="additional-info-editor">
    <!-- Read-only View Mode -->
    <AdditionalInfoReadonly
      v-if="readonly"
      :working-conditions="localData.working_conditions"
      :special-requirements="localData.special_requirements"
      :risk-factors="localData.risk_factors"
    />

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Укажите условия работы, особые требования и возможные факторы риска.
        </div>
      </v-alert>

      <!-- Working Conditions -->
      <WorkingConditionsSection
        :working-conditions="localData.working_conditions"
        @update:schedule="updateSchedule"
        @update:remote-work="updateRemoteWork"
        @update:business-travel="updateBusinessTravel"
      />

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
import WorkingConditionsSection from './sub-components/WorkingConditionsSection.vue'
import AdditionalInfoReadonly from './sub-components/AdditionalInfoReadonly.vue'
import { REQUIREMENTS_SUGGESTIONS, RISK_SUGGESTIONS } from './constants/additionalInfoSuggestions'

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

// Constants
const requirementsSuggestions = REQUIREMENTS_SUGGESTIONS
const riskSuggestions = RISK_SUGGESTIONS

// Methods
function updateSchedule(value: string): void {
  localData.value.working_conditions.work_schedule = value
}

function updateRemoteWork(value: string): void {
  localData.value.working_conditions.remote_work_options = value
}

function updateBusinessTravel(value: string): void {
  localData.value.working_conditions.business_travel = value
}

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

.edit-mode {
  padding: 0;
}

.gap-2 {
  gap: 8px;
}
</style>

<template>
  <div class="experience-education-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-list lines="two">
        <v-list-item prepend-icon="mdi-briefcase-clock">
          <v-list-item-title>Опыт на предыдущей позиции</v-list-item-title>
          <v-list-item-subtitle class="text-wrap mt-2">
            {{ localData.previous_position_experience || 'Не указано' }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider />

        <v-list-item prepend-icon="mdi-clock">
          <v-list-item-title>Общий стаж работы</v-list-item-title>
          <v-list-item-subtitle class="text-wrap mt-2">
            {{ localData.total_work_experience || 'Не указано' }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider />

        <v-list-item
          prepend-icon="mdi-school"
          :title="localData.education_level || 'Не указано'"
          subtitle="Уровень образования"
        />

        <v-divider />

        <v-list-item prepend-icon="mdi-book-open-variant">
          <v-list-item-title>Направление подготовки</v-list-item-title>
          <v-list-item-subtitle class="text-wrap mt-2">
            {{ localData.field_of_study || 'Не указано' }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider />

        <v-list-item prepend-icon="mdi-certificate">
          <v-list-item-title>Дополнительное образование</v-list-item-title>
          <v-list-item-subtitle class="text-wrap mt-2">
            {{ localData.additional_education || 'Не указано' }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Укажите требования к опыту работы и образованию для данной позиции.
        </div>
      </v-alert>

      <!-- Previous Position Experience -->
      <v-textarea
        v-model="localData.previous_position_experience"
        variant="outlined"
        label="Опыт на предыдущей позиции"
        placeholder="Например: Минимальный срок на предыдущей позиции: от 2 лет..."
        rows="2"
        auto-grow
        class="mb-4"
        :rules="requiredTextRules"
      >
        <template #prepend-inner>
          <v-icon>mdi-briefcase-clock</v-icon>
        </template>
      </v-textarea>

      <!-- Total Work Experience -->
      <v-textarea
        v-model="localData.total_work_experience"
        variant="outlined"
        label="Общий стаж работы"
        placeholder="Например: От 5 лет общего опыта работы..."
        rows="2"
        auto-grow
        class="mb-4"
        :rules="requiredTextRules"
      >
        <template #prepend-inner>
          <v-icon>mdi-clock</v-icon>
        </template>
      </v-textarea>

      <!-- Education Level -->
      <v-select
        v-model="localData.education_level"
        :items="educationLevels"
        variant="outlined"
        label="Уровень образования"
        density="comfortable"
        class="mb-4"
        :rules="[(v: string) => !!v || 'Выберите уровень образования']"
      >
        <template #prepend-inner>
          <v-icon>mdi-school</v-icon>
        </template>
      </v-select>

      <!-- Field of Study -->
      <v-textarea
        v-model="localData.field_of_study"
        variant="outlined"
        label="Направление подготовки"
        placeholder="Например: 09.03.01 Информатика и вычислительная техника..."
        rows="2"
        auto-grow
        class="mb-4"
        :rules="requiredTextRules"
      >
        <template #prepend-inner>
          <v-icon>mdi-book-open-variant</v-icon>
        </template>
      </v-textarea>

      <!-- Additional Education -->
      <v-textarea
        v-model="localData.additional_education"
        variant="outlined"
        label="Дополнительное образование"
        placeholder="Курсы, сертификаты, тренинги..."
        rows="3"
        auto-grow
        hint="Необязательно. Укажите желательные курсы и сертификаты"
        persistent-hint
      >
        <template #prepend-inner>
          <v-icon>mdi-certificate</v-icon>
        </template>
      </v-textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Types
interface ExperienceEducation {
  previous_position_experience: string
  total_work_experience: string
  education_level: string
  field_of_study: string
  additional_education: string
}

// Props
interface Props {
  modelValue: ExperienceEducation
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: ExperienceEducation]
}>()

// Local state
const localData = ref<ExperienceEducation>({
  previous_position_experience: '',
  total_work_experience: '',
  education_level: '',
  field_of_study: '',
  additional_education: '',
})

// Education levels
const educationLevels = [
  'Среднее',
  'Среднее специальное',
  'Неоконченное высшее',
  'Высшее',
  'Два и более высших',
  'Кандидат наук',
  'Доктор наук',
]

// Validation rules
const requiredTextRules = [
  (v: string) => !!v || 'Это поле обязательно',
  (v: string) => (v && v.length >= 10) || 'Минимум 10 символов',
  (v: string) => (v && v.length <= 500) || 'Максимум 500 символов',
]

// Initialize
function initialize(): void {
  localData.value = {
    previous_position_experience: props.modelValue?.previous_position_experience || '',
    total_work_experience: props.modelValue?.total_work_experience || '',
    education_level: props.modelValue?.education_level || '',
    field_of_study: props.modelValue?.field_of_study || '',
    additional_education: props.modelValue?.additional_education || '',
  }
}

// Handle updates
function handleUpdate(): void {
  emit('update:modelValue', {
    previous_position_experience: localData.value.previous_position_experience.trim(),
    total_work_experience: localData.value.total_work_experience.trim(),
    education_level: localData.value.education_level,
    field_of_study: localData.value.field_of_study.trim(),
    additional_education: localData.value.additional_education.trim(),
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
.experience-education-editor {
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
</style>

<template>
  <div class="basic-info-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-list lines="two">
        <v-list-item
          prepend-icon="mdi-account-supervisor"
          :title="localData.direct_manager || 'Не указано'"
          subtitle="Прямой руководитель"
        />

        <v-divider />

        <v-list-item prepend-icon="mdi-briefcase">
          <v-list-item-title>Основной вид деятельности</v-list-item-title>
          <v-list-item-subtitle class="text-wrap mt-2">
            {{ localData.primary_activity_type || 'Не указано' }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Укажите прямого руководителя и основной вид деятельности для позиции.
        </div>
      </v-alert>

      <!-- Direct Manager -->
      <v-text-field
        v-model="localData.direct_manager"
        variant="outlined"
        label="Прямой руководитель"
        placeholder="Например: Руководитель отдела"
        density="comfortable"
        class="mb-4"
        :rules="directManagerRules"
      >
        <template #prepend-inner>
          <v-icon>mdi-account-supervisor</v-icon>
        </template>
      </v-text-field>

      <!-- Primary Activity Type -->
      <v-textarea
        v-model="localData.primary_activity_type"
        variant="outlined"
        label="Основной вид деятельности"
        placeholder="Опишите ключевую функцию позиции..."
        rows="4"
        auto-grow
        :rules="primaryActivityRules"
      >
        <template #prepend-inner>
          <v-icon>mdi-briefcase</v-icon>
        </template>
      </v-textarea>

      <!-- Character Count -->
      <v-alert
        type="info"
        variant="tonal"
        density="compact"
        class="mt-2"
      >
        <div class="text-caption">
          Символов: {{ localData.primary_activity_type?.length || 0 }} / 1000
        </div>
      </v-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Types
interface BasicInfo {
  direct_manager: string
  primary_activity_type: string
}

// Props
interface Props {
  modelValue: BasicInfo
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: BasicInfo]
}>()

// Local state
const localData = ref<BasicInfo>({
  direct_manager: '',
  primary_activity_type: '',
})

// Validation rules
const directManagerRules = [
  (v: string) => !!v || 'Укажите прямого руководителя',
  (v: string) => (v && v.length >= 5) || 'Минимум 5 символов',
  (v: string) => (v && v.length <= 200) || 'Максимум 200 символов',
]

const primaryActivityRules = [
  (v: string) => !!v || 'Опишите основной вид деятельности',
  (v: string) => (v && v.length >= 20) || 'Минимум 20 символов',
  (v: string) => (v && v.length <= 1000) || 'Максимум 1000 символов',
]

// Initialize
function initialize(): void {
  localData.value = {
    direct_manager: props.modelValue?.direct_manager || '',
    primary_activity_type: props.modelValue?.primary_activity_type || '',
  }
}

// Handle updates
function handleUpdate(): void {
  emit('update:modelValue', {
    direct_manager: localData.value.direct_manager.trim(),
    primary_activity_type: localData.value.primary_activity_type.trim(),
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
.basic-info-editor {
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

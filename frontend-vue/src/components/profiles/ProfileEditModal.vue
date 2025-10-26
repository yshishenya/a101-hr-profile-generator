<template>
  <v-dialog :model-value="modelValue" max-width="600px" persistent @update:model-value="handleClose">
    <v-card>
      <!-- Header -->
      <v-card-title class="d-flex align-center justify-space-between pa-4 bg-primary">
        <div class="d-flex align-center gap-2">
          <v-icon color="white">mdi-pencil</v-icon>
          <span class="text-white">Редактирование профиля</span>
        </div>
        <v-btn icon="mdi-close" variant="text" color="white" @click="handleClose" />
      </v-card-title>

      <v-divider />

      <!-- Form Content -->
      <v-card-text class="pa-6">
        <v-form ref="formRef" v-model="formValid" @submit.prevent="handleSubmit">
          <!-- Position Info (Read-only) -->
          <div class="mb-6">
            <div class="text-subtitle-2 text-medium-emphasis mb-2">Должность</div>
            <div class="text-body-1">{{ profile?.position_name || 'Не указано' }}</div>
          </div>

          <div class="mb-6">
            <div class="text-subtitle-2 text-medium-emphasis mb-2">Департамент</div>
            <div class="text-body-1">{{ profile?.department_name || 'Не указано' }}</div>
          </div>

          <v-divider class="my-4" />

          <!-- Employee Name (Editable) -->
          <v-text-field
            v-model="formData.employee_name"
            label="Имя сотрудника"
            placeholder="Иванов Иван Иванович"
            variant="outlined"
            density="comfortable"
            clearable
            :rules="employeeNameRules"
            :hint="'Необязательно. Только кириллица, пробелы и дефисы'"
            persistent-hint
            class="mb-4"
          >
            <template #prepend-inner>
              <v-icon>mdi-account</v-icon>
            </template>
          </v-text-field>

          <!-- Status (Editable) -->
          <v-select
            v-model="formData.status"
            :items="statusOptions"
            item-title="label"
            item-value="value"
            label="Статус"
            variant="outlined"
            density="comfortable"
            :rules="statusRules"
            class="mb-4"
          >
            <template #prepend-inner>
              <v-icon>mdi-tag</v-icon>
            </template>

            <template #item="{ props: itemProps, item }">
              <v-list-item v-bind="itemProps">
                <template #prepend>
                  <v-icon :color="item.raw.color">{{ item.raw.icon }}</v-icon>
                </template>
              </v-list-item>
            </template>

            <template #selection="{ item }">
              <div class="d-flex align-center gap-2">
                <v-icon :color="item.raw.color" size="small">{{ item.raw.icon }}</v-icon>
                <span>{{ item.raw.label }}</span>
              </div>
            </template>
          </v-select>

          <!-- Info message -->
          <v-alert type="info" variant="tonal" density="compact" class="mt-2">
            <div class="text-caption">
              <strong>Примечание:</strong> Редактирование содержимого профиля будет доступно в Week
              8 (Inline Editing).
            </div>
          </v-alert>
        </v-form>
      </v-card-text>

      <v-divider />

      <!-- Actions -->
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" :disabled="saving" @click="handleClose"> Отмена </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="saving"
          :disabled="!formValid || !hasChanges"
          @click="handleSubmit"
        >
          Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { UnifiedPosition, PositionStatus } from '@/types/unified'

// Props
interface Props {
  modelValue: boolean
  profile: UnifiedPosition | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: [data: { employee_name?: string; status?: PositionStatus }]
}>()

// Form state
const formRef = ref()
const formValid = ref(false)
const saving = ref(false)

// Form data
const formData = ref<{
  employee_name: string
  status: PositionStatus
}>({
  employee_name: '',
  status: 'generated'
})

// Status options
const statusOptions = [
  {
    label: 'Сгенерирован',
    value: 'generated' as PositionStatus,
    icon: 'mdi-check-circle',
    color: 'success'
  },
  {
    label: 'Генерация',
    value: 'generating' as PositionStatus,
    icon: 'mdi-progress-clock',
    color: 'warning'
  },
  {
    label: 'Архивирован',
    value: 'archived' as PositionStatus,
    icon: 'mdi-archive',
    color: 'grey'
  }
]

// Validation rules
const employeeNameRules = [
  (v: string) => {
    if (!v) return true // Optional field
    if (v.length > 200) return 'Максимум 200 символов'
    // Allow only Cyrillic, spaces, and hyphens
    if (!/^[А-Яа-яЁё\s-]+$/.test(v)) {
      return 'Только кириллица, пробелы и дефисы'
    }
    return true
  }
]

const statusRules = [(v: string) => !!v || 'Выберите статус']

// Check if form has changes
const hasChanges = computed(() => {
  if (!props.profile) return false

  const nameChanged = formData.value.employee_name !== (props.profile.employee_name || '')
  const statusChanged = formData.value.status !== props.profile.status

  return nameChanged || statusChanged
})

// Watch for profile changes to initialize form
watch(
  () => props.profile,
  (newProfile) => {
    if (newProfile) {
      formData.value = {
        employee_name: newProfile.employee_name || '',
        status: newProfile.status || 'generated'
      }
    }
  },
  { immediate: true }
)

// Watch for dialog open to reset form
watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen && props.profile) {
      formData.value = {
        employee_name: props.profile.employee_name || '',
        status: props.profile.status || 'generated'
      }
      // Reset validation
      formRef.value?.resetValidation()
    }
  }
)

// Methods
function handleClose(): void {
  if (!saving.value) {
    emit('update:modelValue', false)
  }
}

async function handleSubmit(): Promise<void> {
  // Validate form
  const { valid } = await formRef.value.validate()
  if (!valid || !hasChanges.value) return

  saving.value = true

  try {
    // Build update payload (only changed fields)
    const payload: { employee_name?: string; status?: PositionStatus } = {}

    if (formData.value.employee_name !== (props.profile?.employee_name || '')) {
      payload.employee_name = formData.value.employee_name || undefined
    }

    if (formData.value.status !== props.profile?.status) {
      payload.status = formData.value.status
    }

    // Emit save event
    emit('save', payload)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

/* Ensure proper text wrapping */
.v-alert {
  word-break: break-word;
}
</style>

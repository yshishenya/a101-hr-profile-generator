<template>
  <v-dialog :model-value="modelValue" :theme="theme.global.name.value" max-width="500px" persistent @update:model-value="handleClose">
    <v-card>
      <!-- Header -->
      <v-sheet bg-color="surface-variant" class="pa-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center gap-3">
            <v-icon color="error">mdi-alert-circle</v-icon>
            <span class="text-h6">Подтверждение удаления</span>
          </div>
          <v-btn icon="mdi-close" variant="text" @click="handleClose" />
        </div>
      </v-sheet>

      <v-divider />

      <!-- Content -->
      <v-card-text class="pa-6">
        <!-- Warning Icon -->
        <div class="text-center mb-4">
          <v-icon size="64" color="error">mdi-delete-alert</v-icon>
        </div>

        <!-- Main Message -->
        <div class="text-h6 text-center mb-2">
          Вы действительно хотите удалить {{ itemCount === 1 ? 'профиль' : `${itemCount} профилей` }}?
        </div>

        <!-- Details -->
        <div v-if="items && items.length > 0" class="mt-4">
          <v-divider class="mb-3" />

          <div class="text-subtitle-2 text-medium-emphasis mb-2">
            {{ itemCount === 1 ? 'Профиль для удаления:' : 'Профили для удаления:' }}
          </div>

          <!-- Single item -->
          <v-sheet
            v-if="itemCount === 1 && items[0]"
            bg-color="surface-variant"
            class="pa-3 rounded"
          >
            <div class="text-body-1 font-weight-medium">{{ items[0]?.position_name }}</div>
            <div class="text-caption text-medium-emphasis">{{ items[0]?.department_name }}</div>
            <div v-if="items[0]?.employee_name" class="text-caption mt-1">
              Сотрудник: {{ items[0]?.employee_name }}
            </div>
          </v-sheet>

          <!-- Multiple items -->
          <div v-else class="items-list">
            <v-chip
              v-for="item in displayedItems"
              :key="item.profile_id"
              size="small"
              class="ma-1"
              label
            >
              {{ item.position_name }}
            </v-chip>
            <div v-if="itemCount > maxDisplayItems" class="text-caption text-medium-emphasis mt-2">
              и еще {{ itemCount - maxDisplayItems }}...
            </div>
          </div>
        </div>

        <!-- Info Alert -->
        <v-alert
          type="warning"
          variant="tonal"
          density="compact"
          class="mt-4"
          icon="mdi-information"
        >
          <div class="text-caption">
            <strong>Примечание:</strong> Профили будут архивированы и могут быть восстановлены
            позже.
          </div>
        </v-alert>

        <!-- Confirmation Checkbox (optional for multiple items) -->
        <v-checkbox
          v-if="requireConfirmation"
          v-model="confirmed"
          color="error"
          density="compact"
          class="mt-4"
          hide-details
        >
          <template #label>
            <span class="text-body-2">
              Я понимаю, что {{ itemCount === 1 ? 'профиль будет архивирован' : `${itemCount} профилей будут архивированы` }}
            </span>
          </template>
        </v-checkbox>
      </v-card-text>

      <v-divider />

      <!-- Actions -->
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" :disabled="deleting" @click="handleClose"> Отмена </v-btn>
        <v-btn
          color="error"
          variant="elevated"
          :loading="deleting"
          :disabled="requireConfirmation && !confirmed"
          @click="handleDelete"
        >
          Удалить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTheme } from 'vuetify'
import type { UnifiedPosition } from '@/types/unified'

// Props
interface Props {
  modelValue: boolean
  items: UnifiedPosition[] | null
  requireConfirmation?: boolean
  maxDisplayItems?: number
}

const props = withDefaults(defineProps<Props>(), {
  requireConfirmation: false,
  maxDisplayItems: 5
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  delete: []
}>()

// Theme
const theme = useTheme()

// Local state
const confirmed = ref(false)
const deleting = ref(false)

// Computed
const itemCount = computed(() => props.items?.length || 0)

const displayedItems = computed(() => {
  if (!props.items) return []
  return props.items.slice(0, props.maxDisplayItems)
})

// Watch for dialog close to reset state
watch(
  () => props.modelValue,
  (isOpen) => {
    if (!isOpen) {
      confirmed.value = false
      deleting.value = false
    }
  }
)

// Methods
function handleClose(): void {
  if (!deleting.value) {
    emit('update:modelValue', false)
  }
}

async function handleDelete(): Promise<void> {
  if (props.requireConfirmation && !confirmed.value) return

  deleting.value = true

  try {
    // Emit delete event - parent handles actual deletion
    emit('delete')
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.items-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
}

/* Ensure proper text wrapping */
.v-alert {
  word-break: break-word;
}
</style>

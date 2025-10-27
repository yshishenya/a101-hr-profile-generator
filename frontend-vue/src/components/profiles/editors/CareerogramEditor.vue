<template>
  <div class="careerogram-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-expansion-panels variant="accordion">
        <!-- Source Positions -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-arrow-down-bold</v-icon>
              <span class="font-weight-medium">Исходные позиции (откуда приходят)</span>
              <v-chip size="x-small" variant="outlined">
                {{ localData.source_positions.length }}
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-list density="compact">
              <v-list-item
                v-for="(pos, idx) in localData.source_positions"
                :key="idx"
                class="px-0"
              >
                <template #prepend>
                  <v-icon size="small" color="info">mdi-account-arrow-right</v-icon>
                </template>
                <v-list-item-subtitle class="text-wrap">{{ pos }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item v-if="localData.source_positions.length === 0" class="px-0">
                <v-list-item-subtitle class="text-medium-emphasis">Не указано</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>

        <!-- Target Positions -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-arrow-up-bold</v-icon>
              <span class="font-weight-medium">Целевые позиции (куда могут перейти)</span>
              <v-chip size="x-small" variant="outlined">
                {{ localData.target_positions.length }}
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-list density="compact">
              <v-list-item
                v-for="(pos, idx) in localData.target_positions"
                :key="idx"
                class="px-0 mb-3"
              >
                <template #prepend>
                  <v-icon size="small" color="success">mdi-arrow-top-right</v-icon>
                </template>
                <v-list-item-subtitle class="text-wrap">
                  <div class="text-body-2">{{ pos }}</div>
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item v-if="localData.target_positions.length === 0" class="px-0">
                <v-list-item-subtitle class="text-medium-emphasis">Не указано</v-list-item-subtitle>
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
          💡 Карьерограмма показывает возможные пути карьерного развития: откуда приходят на эту
          позицию и куда могут перейти.
        </div>
      </v-alert>

      <!-- Source Positions -->
      <v-card variant="outlined" class="mb-4">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-arrow-down-bold</v-icon>
          Исходные позиции (donor positions)
        </v-card-title>

        <v-card-text>
          <v-combobox
            v-model="localData.source_positions"
            chips
            closable-chips
            multiple
            variant="outlined"
            label="Добавить исходную позицию"
            placeholder="Введите позицию и нажмите Enter"
            hint="С каких позиций обычно приходят на данную должность. Минимум 2 позиции."
            persistent-hint
            :rules="sourcePositionsRules"
          >
            <template #chip="{ props: chipProps, item }">
              <v-chip v-bind="chipProps" closable color="info">
                <v-icon start size="small">mdi-account-arrow-right</v-icon>
                {{ item.value }}
              </v-chip>
            </template>
          </v-combobox>

          <!-- Statistics -->
          <v-alert type="info" variant="tonal" density="compact" class="mt-2">
            <div class="text-caption">
              Добавлено: {{ localData.source_positions.length }} позиций
              <span v-if="localData.source_positions.length < 2" class="text-warning">
                (минимум: 2)
              </span>
            </div>
          </v-alert>
        </v-card-text>
      </v-card>

      <!-- Target Positions -->
      <v-card variant="outlined">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-arrow-up-bold</v-icon>
          Целевые позиции (карьерные треки)
        </v-card-title>

        <v-card-text>
          <!-- Info about format -->
          <v-alert type="info" variant="tonal" density="compact" class="mb-4">
            <div class="text-caption">
              <strong>Формат:</strong> Тип роста: Название позиции → Блок → Департамент;
              rationale: обоснование; competency_bridge: strengthen_skills: [...],
              acquire_skills: [...]
            </div>
          </v-alert>

          <!-- Existing target positions -->
          <v-expansion-panels v-model="openTargetPanels" multiple class="mb-3">
            <v-expansion-panel
              v-for="(target, index) in localData.target_positions"
              :key="`target-${index}`"
              :value="index"
            >
              <v-expansion-panel-title>
                <div class="d-flex align-center justify-space-between" style="width: 100%">
                  <div class="d-flex align-center gap-2">
                    <v-icon size="small">mdi-arrow-top-right</v-icon>
                    <span class="text-truncate">
                      {{ getTargetPositionPreview(target) }}
                    </span>
                  </div>
                  <v-btn
                    icon
                    variant="text"
                    size="x-small"
                    color="error"
                    @click.stop="removeTargetPosition(index)"
                  >
                    <v-icon size="small">mdi-delete</v-icon>
                  </v-btn>
                </div>
              </v-expansion-panel-title>

              <v-expansion-panel-text>
                <v-textarea
                  v-model="localData.target_positions[index]"
                  variant="outlined"
                  label="Описание карьерного трека"
                  rows="6"
                  auto-grow
                  :rules="targetPositionRules"
                  placeholder="Вертикальный рост: Название позиции → Блок → Департамент; rationale: обоснование..."
                />
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- Add Target Position Button -->
          <v-btn prepend-icon="mdi-plus" variant="outlined" block @click="addTargetPosition">
            Добавить целевую позицию
          </v-btn>

          <!-- Statistics -->
          <v-alert type="info" variant="tonal" density="compact" class="mt-3">
            <div class="text-caption">
              Добавлено: {{ localData.target_positions.length }} карьерных треков
              <span v-if="localData.target_positions.length < 2" class="text-warning">
                (рекомендуется минимум 2: вертикальный и горизонтальный/экспертный)
              </span>
            </div>
          </v-alert>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Types
interface Careerogram {
  source_positions: string[]
  target_positions: string[]
}

// Props
interface Props {
  modelValue: Careerogram
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: Careerogram]
}>()

// Local state
const localData = ref<Careerogram>({
  source_positions: [],
  target_positions: [],
})

const openTargetPanels = ref<number[]>([])

// Validation rules
const sourcePositionsRules = [
  (v: string[]) => (v && v.length >= 2) || 'Минимум 2 исходные позиции',
  (v: string[]) => (v && v.length <= 10) || 'Максимум 10 позиций',
]

const targetPositionRules = [
  (v: string) => !!v || 'Опишите карьерный трек',
  (v: string) => (v && v.length >= 50) || 'Минимум 50 символов для полного описания',
  (v: string) => (v && v.length <= 2000) || 'Максимум 2000 символов',
]

// Methods
function getTargetPositionPreview(target: string): string {
  // Extract first 80 characters
  const preview = target.substring(0, 80)
  return target.length > 80 ? `${preview}...` : preview
}

function addTargetPosition(): void {
  const newIndex = localData.value.target_positions.length
  localData.value.target_positions.push('')
  // Auto-open the new panel
  openTargetPanels.value.push(newIndex)
}

function removeTargetPosition(index: number): void {
  localData.value.target_positions.splice(index, 1)
  // Update open panels
  openTargetPanels.value = openTargetPanels.value
    .filter((i) => i !== index)
    .map((i) => (i > index ? i - 1 : i))
}

// Initialize
function initialize(): void {
  localData.value = {
    source_positions: [...(props.modelValue?.source_positions || [])],
    target_positions: [...(props.modelValue?.target_positions || [])],
  }

  // Open all target panels in edit mode
  if (!props.readonly) {
    openTargetPanels.value = localData.value.target_positions.map((_, idx) => idx)
  }
}

// Handle updates
function handleUpdate(): void {
  emit('update:modelValue', {
    source_positions: localData.value.source_positions.filter((p) => p && p.trim()),
    target_positions: localData.value.target_positions.filter((p) => p && p.trim()),
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
.careerogram-editor {
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

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gap-2 {
  gap: 8px;
}
</style>

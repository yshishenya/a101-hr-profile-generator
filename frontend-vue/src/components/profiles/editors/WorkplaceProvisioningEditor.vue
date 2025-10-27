<template>
  <div class="workplace-provisioning-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-expansion-panels variant="accordion">
        <!-- Software -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-application</v-icon>
              <span class="font-weight-medium">Программное обеспечение</span>
              <v-chip size="x-small" variant="outlined">
                {{
                  (localData.software.standard_package?.length || 0) +
                  (localData.software.specialized_tools?.length || 0)
                }}
                программ
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <div class="mb-3">
              <div class="text-subtitle-2 mb-2">Стандартный пакет:</div>
              <v-chip
                v-for="(item, idx) in localData.software.standard_package"
                :key="idx"
                size="small"
                class="mr-2 mb-2"
              >
                {{ item }}
              </v-chip>
              <div v-if="!localData.software.standard_package?.length" class="text-caption text-medium-emphasis">
                Не указано
              </div>
            </div>

            <v-divider class="my-3" />

            <div>
              <div class="text-subtitle-2 mb-2">Специализированное ПО:</div>
              <v-chip
                v-for="(item, idx) in localData.software.specialized_tools"
                :key="idx"
                size="small"
                color="primary"
                class="mr-2 mb-2"
              >
                {{ item }}
              </v-chip>
              <div v-if="!localData.software.specialized_tools?.length" class="text-caption text-medium-emphasis">
                Не указано
              </div>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>

        <!-- Hardware -->
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-laptop</v-icon>
              <span class="font-weight-medium">Оборудование</span>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <div class="mb-3">
              <div class="text-subtitle-2 mb-2">Стандартная рабочая станция:</div>
              <div class="text-body-2">
                {{ localData.hardware.standard_workstation || 'Не указано' }}
              </div>
            </div>

            <v-divider class="my-3" />

            <div>
              <div class="text-subtitle-2 mb-2">Специализированное оборудование:</div>
              <v-chip
                v-for="(item, idx) in localData.hardware.specialized_equipment"
                :key="idx"
                size="small"
                color="success"
                class="mr-2 mb-2"
              >
                {{ item }}
              </v-chip>
              <div v-if="!localData.hardware.specialized_equipment?.length" class="text-caption text-medium-emphasis">
                Не указано
              </div>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Укажите необходимое ПО и оборудование для рабочего места.
        </div>
      </v-alert>

      <!-- Software Section -->
      <v-card variant="outlined" class="mb-4">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-application</v-icon>
          Программное обеспечение
        </v-card-title>

        <v-card-text>
          <!-- Standard Package -->
          <div class="mb-4">
            <div class="text-subtitle-2 mb-2">Стандартный пакет</div>
            <v-combobox
              v-model="localData.software.standard_package"
              chips
              closable-chips
              multiple
              variant="outlined"
              label="Добавить программу"
              placeholder="Введите название и нажмите Enter"
              hint="Стандартное ПО для всех сотрудников"
              persistent-hint
            >
              <template #chip="{ props: chipProps, item }">
                <v-chip v-bind="chipProps" closable>{{ item.value }}</v-chip>
              </template>
            </v-combobox>

            <!-- Suggestions -->
            <div class="mt-2">
              <div class="text-caption text-medium-emphasis mb-1">Популярные:</div>
              <v-chip
                v-for="suggestion in standardSoftwareSuggestions"
                :key="suggestion"
                size="small"
                variant="outlined"
                class="mr-2 mb-1"
                @click="addToStandardPackage(suggestion)"
              >
                <v-icon start size="small">mdi-plus</v-icon>
                {{ suggestion }}
              </v-chip>
            </div>
          </div>

          <v-divider class="my-4" />

          <!-- Specialized Tools -->
          <div>
            <div class="text-subtitle-2 mb-2">Специализированное ПО</div>
            <v-combobox
              v-model="localData.software.specialized_tools"
              chips
              closable-chips
              multiple
              variant="outlined"
              label="Добавить инструмент"
              placeholder="Введите название и нажмите Enter"
              hint="Специфичное ПО для данной позиции"
              persistent-hint
              :rules="[(v: string[]) => !v || v.length <= 20 || 'Максимум 20 инструментов']"
            >
              <template #chip="{ props: chipProps, item }">
                <v-chip v-bind="chipProps" closable color="primary">{{ item.value }}</v-chip>
              </template>
            </v-combobox>
          </div>
        </v-card-text>
      </v-card>

      <!-- Hardware Section -->
      <v-card variant="outlined">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon>mdi-laptop</v-icon>
          Оборудование
        </v-card-title>

        <v-card-text>
          <!-- Standard Workstation -->
          <v-textarea
            v-model="localData.hardware.standard_workstation"
            variant="outlined"
            label="Стандартная рабочая станция"
            placeholder="Опишите конфигурацию рабочей станции..."
            rows="3"
            auto-grow
            class="mb-4"
            :rules="workstationRules"
          >
            <template #prepend-inner>
              <v-icon>mdi-desktop-tower</v-icon>
            </template>
          </v-textarea>

          <!-- Specialized Equipment -->
          <div>
            <div class="text-subtitle-2 mb-2">Специализированное оборудование</div>
            <v-combobox
              v-model="localData.hardware.specialized_equipment"
              chips
              closable-chips
              multiple
              variant="outlined"
              label="Добавить оборудование"
              placeholder="Введите название и нажмите Enter"
              hint="Необязательно. Дополнительное оборудование для позиции"
              persistent-hint
            >
              <template #chip="{ props: chipProps, item }">
                <v-chip v-bind="chipProps" closable color="success">{{ item.value }}</v-chip>
              </template>
            </v-combobox>

            <!-- Suggestions -->
            <div class="mt-2">
              <div class="text-caption text-medium-emphasis mb-1">Популярные:</div>
              <v-chip
                v-for="suggestion in hardwareSuggestions"
                :key="suggestion"
                size="small"
                variant="outlined"
                class="mr-2 mb-1"
                @click="addToSpecializedEquipment(suggestion)"
              >
                <v-icon start size="small">mdi-plus</v-icon>
                {{ suggestion }}
              </v-chip>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// Types
interface WorkplaceProvisioning {
  software: {
    standard_package: string[]
    specialized_tools: string[]
  }
  hardware: {
    standard_workstation: string
    specialized_equipment: string[]
  }
}

// Props
interface Props {
  modelValue: WorkplaceProvisioning
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: WorkplaceProvisioning]
}>()

// Local state
const localData = ref<WorkplaceProvisioning>({
  software: {
    standard_package: [],
    specialized_tools: [],
  },
  hardware: {
    standard_workstation: '',
    specialized_equipment: [],
  },
})

// Suggestions
const standardSoftwareSuggestions = [
  'MS Office',
  'Outlook',
  'Teams',
  'Корпоративный мессенджер',
  'Веб-браузер',
]

const hardwareSuggestions = [
  'Дополнительный монитор',
  'Внешняя клавиатура',
  'Мышь',
  'Наушники с микрофоном',
  'Веб-камера',
]

// Validation rules
const workstationRules = [
  (v: string) => !!v || 'Опишите стандартную рабочую станцию',
  (v: string) => (v && v.length >= 20) || 'Минимум 20 символов',
  (v: string) => (v && v.length <= 1000) || 'Максимум 1000 символов',
]

// Methods
function addToStandardPackage(item: string): void {
  if (!localData.value.software.standard_package.includes(item)) {
    localData.value.software.standard_package.push(item)
  }
}

function addToSpecializedEquipment(item: string): void {
  if (!localData.value.hardware.specialized_equipment.includes(item)) {
    localData.value.hardware.specialized_equipment.push(item)
  }
}

// Initialize
function initialize(): void {
  localData.value = {
    software: {
      standard_package: [...(props.modelValue?.software?.standard_package || [])],
      specialized_tools: [...(props.modelValue?.software?.specialized_tools || [])],
    },
    hardware: {
      standard_workstation: props.modelValue?.hardware?.standard_workstation || '',
      specialized_equipment: [...(props.modelValue?.hardware?.specialized_equipment || [])],
    },
  }
}

// Handle updates
function handleUpdate(): void {
  emit('update:modelValue', {
    software: {
      standard_package: localData.value.software.standard_package.filter((s) => s && s.trim()),
      specialized_tools: localData.value.software.specialized_tools.filter((s) => s && s.trim()),
    },
    hardware: {
      standard_workstation: localData.value.hardware.standard_workstation.trim(),
      specialized_equipment: localData.value.hardware.specialized_equipment.filter(
        (e) => e && e.trim()
      ),
    },
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
.workplace-provisioning-editor {
  min-height: 200px;
}

.readonly-view,
.edit-mode {
  padding: 0;
}

.gap-2 {
  gap: 8px;
}
</style>

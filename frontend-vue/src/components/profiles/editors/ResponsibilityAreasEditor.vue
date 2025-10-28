<template>
  <div class="responsibility-areas-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-expansion-panels variant="accordion">
        <v-expansion-panel
          v-for="(area, index) in localAreas"
          :key="index"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-clipboard-list</v-icon>
              <span class="font-weight-medium">
                {{ area.area.join(', ') }}
              </span>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <div v-if="area.tasks.length > 0">
              <v-list density="compact">
                <v-list-item
                  v-for="(task, taskIdx) in area.tasks"
                  :key="taskIdx"
                  class="pl-0"
                >
                  <template #prepend>
                    <v-icon size="small" class="mr-2">mdi-check</v-icon>
                  </template>
                  <v-list-item-title class="text-body-2">
                    {{ task }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </div>
            <div v-else class="text-caption text-medium-emphasis">
              Нет задач
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <div v-if="localAreas.length === 0" class="text-body-2 text-medium-emphasis pa-4">
        Нет зон ответственности. Нажмите "Редактировать" для добавления.
      </div>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Добавьте зоны ответственности и задачи для каждой области.
          Минимум {{ minAreas }} {{ minAreas === 1 ? 'зона' : 'зоны' }}.
        </div>
      </v-alert>

      <!-- Editable Areas -->
      <v-expansion-panels
        v-model="openPanels"
        variant="accordion"
        multiple
        class="mb-4"
      >
        <v-expansion-panel
          v-for="(area, index) in localAreas"
          :key="area.id"
          :value="area.id"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center justify-space-between" style="width: 100%">
              <div class="d-flex align-center gap-2">
                <v-icon size="small">mdi-clipboard-list</v-icon>
                <span class="font-weight-medium">
                  {{ area.area.join(', ') || 'Новая зона ответственности' }}
                </span>
                <v-chip size="x-small" variant="outlined">
                  {{ area.tasks.length }} {{ area.tasks.length === 1 ? 'задача' : 'задач' }}
                </v-chip>
              </div>

              <v-btn
                icon
                variant="text"
                size="x-small"
                color="error"
                @click.stop="removeArea(index)"
              >
                <v-icon size="small">mdi-delete</v-icon>
                <v-tooltip activator="parent" location="bottom">
                  Удалить зону
                </v-tooltip>
              </v-btn>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <!-- Area Name -->
            <div class="mb-4">
              <div class="text-subtitle-2 mb-2">Название области</div>
              <v-combobox
                v-model="area.area"
                chips
                closable-chips
                multiple
                variant="outlined"
                label="Зона ответственности"
                hint="Можно указать несколько названий через Enter"
                placeholder="Например: Разработка backend-сервисов"
                persistent-hint
                density="comfortable"
              >
                <template #prepend-inner>
                  <v-icon>mdi-tag</v-icon>
                </template>
              </v-combobox>
            </div>

            <!-- Tasks -->
            <div class="mb-2">
              <div class="text-subtitle-2 mb-2">Задачи в этой области</div>
              <v-combobox
                v-model="area.tasks"
                chips
                closable-chips
                multiple
                variant="outlined"
                label="Задачи"
                hint="Нажмите Enter после каждой задачи"
                placeholder="Добавьте задачу..."
                persistent-hint
                density="comfortable"
              >
                <template #prepend-inner>
                  <v-icon>mdi-check-circle</v-icon>
                </template>

                <template #chip="{ props: chipProps, item }">
                  <v-chip
                    v-bind="chipProps"
                    closable
                    variant="flat"
                    size="small"
                  >
                    {{ item.value }}
                  </v-chip>
                </template>
              </v-combobox>
            </div>

            <!-- Task Statistics -->
            <v-alert
              v-if="area.tasks.length === 0"
              type="warning"
              variant="tonal"
              density="compact"
              class="mt-2"
            >
              <div class="text-caption">
                ⚠️ Добавьте хотя бы одну задачу для этой зоны
              </div>
            </v-alert>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Add New Area Button -->
      <v-btn
        prepend-icon="mdi-plus"
        variant="outlined"
        color="primary"
        block
        @click="addArea"
      >
        Добавить зону ответственности
      </v-btn>

      <!-- Overall Statistics -->
      <v-alert
        type="info"
        variant="tonal"
        density="compact"
        class="mt-4"
      >
        <div class="text-caption">
          Всего: {{ localAreas.length }} {{ areasLabel }},
          {{ totalTasks }} {{ tasksLabel }}
          <span v-if="localAreas.length < minAreas" class="text-warning">
            (минимум: {{ minAreas }} {{ minAreas === 1 ? 'зона' : 'зоны' }})
          </span>
        </div>
      </v-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

// Types
interface ResponsibilityArea {
  id: string
  area: string[]
  tasks: string[]
}

// Props
interface Props {
  modelValue: Array<{ area: string[]; tasks: string[] }>
  readonly?: boolean
  minAreas?: number
  maxAreas?: number
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
  minAreas: 1,
  maxAreas: 20,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: Array<{ area: string[]; tasks: string[] }>]
}>()

// Local state
const localAreas = ref<ResponsibilityArea[]>([])
const openPanels = ref<string[]>([])

// Computed
const totalTasks = computed(() => {
  return localAreas.value.reduce((sum, area) => sum + area.tasks.length, 0)
})

const areasLabel = computed(() => {
  const count = localAreas.value.length
  if (count === 1) return 'зона'
  if (count >= 2 && count <= 4) return 'зоны'
  return 'зон'
})

const tasksLabel = computed(() => {
  const count = totalTasks.value
  if (count === 1) return 'задача'
  if (count >= 2 && count <= 4) return 'задачи'
  return 'задач'
})

// Methods
function initializeAreas(): void {
  localAreas.value = (props.modelValue || []).map((area, index) => ({
    id: `area-${Date.now()}-${index}`,
    area: Array.isArray(area.area) ? [...area.area] : [],
    tasks: Array.isArray(area.tasks) ? [...area.tasks] : [],
  }))

  // Open all panels in edit mode
  if (!props.readonly) {
    openPanels.value = localAreas.value.map((a) => a.id)
  }
}

function addArea(): void {
  const newArea: ResponsibilityArea = {
    id: `area-${Date.now()}`,
    area: [],
    tasks: [],
  }
  localAreas.value.push(newArea)

  // Auto-open the new panel
  openPanels.value.push(newArea.id)

  handleUpdate()
}

function removeArea(index: number): void {
  const area = localAreas.value[index]
  if (!area) return

  const areaId = area.id
  localAreas.value.splice(index, 1)

  // Remove from open panels
  openPanels.value = openPanels.value.filter((id) => id !== areaId)

  handleUpdate()
}

function handleUpdate(): void {
  // Clean up and emit
  const cleanedAreas = localAreas.value
    .map((area) => ({
      area: area.area.filter((a) => a && a.trim() !== ''),
      tasks: area.tasks.filter((t) => t && t.trim() !== ''),
    }))
    .filter((area) => area.area.length > 0 || area.tasks.length > 0)

  emit('update:modelValue', cleanedAreas)
}

// Initialize on mount
initializeAreas()

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    const currentJson = JSON.stringify(
      localAreas.value.map((a) => ({ area: a.area, tasks: a.tasks }))
    )
    const newJson = JSON.stringify(newValue)

    if (currentJson !== newJson) {
      initializeAreas()
    }
  },
  { deep: true }
)

// Watch for changes in local areas
watch(
  localAreas,
  () => {
    handleUpdate()
  },
  { deep: true }
)
</script>

<style scoped>
.responsibility-areas-editor {
  min-height: 150px;
}

.readonly-view {
  padding: 0;
}

.edit-mode {
  padding: 0;
}

.gap-2 {
  gap: 8px;
}

/* Smooth expansion */
.v-expansion-panel {
  transition: all 0.3s ease;
}

.v-expansion-panel:hover {
  background-color: rgba(var(--v-theme-surface-variant), 0.3);
}

/* Task list styling */
.v-list-item {
  border-left: 2px solid rgb(var(--v-theme-primary));
  margin-bottom: 4px;
}
</style>

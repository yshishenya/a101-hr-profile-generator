<template>
  <div class="filter-presets">
    <!-- Preset Selector Dropdown -->
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      location="bottom"
      offset="4"
    >
      <template #activator="{ props: activatorProps }">
        <v-btn
          v-bind="activatorProps"
          :prepend-icon="activePresetIcon"
          :color="activePresetColor"
          variant="outlined"
          density="comfortable"
        >
          {{ activePresetName }}
          <v-icon end>mdi-menu-down</v-icon>
        </v-btn>
      </template>

      <v-card min-width="350" max-width="450">
        <v-card-title class="d-flex align-center justify-space-between">
          <span>Пресеты фильтров</span>
          <v-btn
            icon="mdi-close"
            size="small"
            variant="text"
            @click="menu = false"
          />
        </v-card-title>

        <v-divider />

        <!-- Preset List -->
        <v-list density="compact">
          <!-- Default Presets -->
          <v-list-subheader>Готовые пресеты</v-list-subheader>
          <v-list-item
            v-for="preset in defaultPresets"
            :key="preset.id"
            :active="isActive(preset.id)"
            :title="preset.name"
            @click="applyPreset(preset)"
          >
            <template #prepend>
              <v-icon :color="preset.color">{{ preset.icon }}</v-icon>
            </template>
            <template #append>
              <v-icon v-if="isActive(preset.id)" color="primary">mdi-check</v-icon>
            </template>
          </v-list-item>

          <!-- Custom Presets -->
          <template v-if="customPresets.length > 0">
            <v-divider />
            <v-list-subheader>
              Мои пресеты
              <span class="text-caption text-medium-emphasis ml-2">
                ({{ customPresets.length }}/{{ MAX_PRESETS }})
              </span>
            </v-list-subheader>
            <v-list-item
              v-for="preset in customPresets"
              :key="preset.id"
              :active="isActive(preset.id)"
              :title="preset.name"
              @click="applyPreset(preset)"
            >
              <template #prepend>
                <v-icon :color="preset.color || 'default'">
                  {{ preset.icon || 'mdi-filter' }}
                </v-icon>
              </template>
              <template #append>
                <div class="d-flex align-center gap-1">
                  <v-icon v-if="isActive(preset.id)" color="primary">mdi-check</v-icon>
                  <v-btn
                    icon="mdi-pencil"
                    size="x-small"
                    variant="text"
                    @click.stop="editPreset(preset)"
                  />
                  <v-btn
                    icon="mdi-delete"
                    size="x-small"
                    variant="text"
                    color="error"
                    @click.stop="deletePresetConfirm(preset)"
                  />
                </div>
              </template>
            </v-list-item>
          </template>
        </v-list>

        <v-divider />

        <!-- Actions -->
        <v-card-actions>
          <v-btn
            prepend-icon="mdi-content-save"
            variant="text"
            :disabled="customPresets.length >= MAX_PRESETS"
            @click="showSaveDialog = true"
          >
            Сохранить текущие
          </v-btn>
          <v-spacer />
          <v-btn
            v-if="activePresetId"
            prepend-icon="mdi-filter-remove"
            variant="text"
            color="warning"
            @click="clearActivePreset"
          >
            Сбросить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>

    <!-- Save Preset Dialog -->
    <v-dialog
      v-model="showSaveDialog"
      max-width="500"
      persistent
    >
      <v-card>
        <v-card-title>Сохранить пресет</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newPresetName"
            label="Название пресета"
            placeholder="Например: IT отдел - сгенерированные"
            density="comfortable"
            variant="outlined"
            :error-messages="nameError"
            counter
            maxlength="50"
            autofocus
            @update:model-value="validatePresetName"
          />

          <!-- Icon & Color Selection (Optional) -->
          <v-row dense class="mt-2">
            <v-col cols="6">
              <v-select
                v-model="newPresetIcon"
                :items="iconOptions"
                label="Иконка (опционально)"
                density="comfortable"
                variant="outlined"
              >
                <template #selection="{ item }">
                  <div class="d-flex align-center gap-2">
                    <v-icon>{{ item.value }}</v-icon>
                    <span>{{ item.title }}</span>
                  </div>
                </template>
                <template #item="{ item, props: itemProps }">
                  <v-list-item v-bind="itemProps">
                    <template #prepend>
                      <v-icon>{{ item.value }}</v-icon>
                    </template>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="newPresetColor"
                :items="colorOptions"
                label="Цвет (опционально)"
                density="comfortable"
                variant="outlined"
              >
                <template #selection="{ item }">
                  <v-chip :color="item.value" size="small">
                    {{ item.title }}
                  </v-chip>
                </template>
                <template #item="{ item, props: itemProps }">
                  <v-list-item v-bind="itemProps">
                    <template #prepend>
                      <v-chip :color="item.value" size="small" />
                    </template>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="cancelSave">Отмена</v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="elevated"
            :disabled="!canSave"
            @click="saveNewPreset"
          >
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-error">
          <v-icon start>mdi-alert-circle</v-icon>
          Удалить пресет?
        </v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить пресет "{{ presetToDelete?.name }}"?
          Это действие нельзя отменить.
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="showDeleteDialog = false">Отмена</v-btn>
          <v-spacer />
          <v-btn
            color="error"
            variant="elevated"
            @click="confirmDelete"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useProfilesStore } from '@/stores/profiles'
import type { FilterPreset } from '@/types/presets'
import {
  getAllPresets,
  addPreset,
  createPreset,
  deletePreset as deletePresetUtil,
  setActivePreset,
  getActivePresetId,
  isPresetNameAvailable
} from '@/utils/filterPresets'
import { getErrorMessage } from '@/utils/errors'

// Constants
const MAX_PRESETS = 10

const ICON_OPTIONS = [
  { title: 'Фильтр', value: 'mdi-filter' },
  { title: 'Звезда', value: 'mdi-star' },
  { title: 'Часы', value: 'mdi-clock-outline' },
  { title: 'Офис', value: 'mdi-office-building' },
  { title: 'Галочка', value: 'mdi-check-circle' }
]

const COLOR_OPTIONS = [
  { title: 'По умолчанию', value: 'default' },
  { title: 'Синий', value: 'primary' },
  { title: 'Зеленый', value: 'success' },
  { title: 'Оранжевый', value: 'warning' },
  { title: 'Красный', value: 'error' },
  { title: 'Фиолетовый', value: 'purple' }
]

// Store
const profilesStore = useProfilesStore()

// State
const menu = ref(false)
const showSaveDialog = ref(false)
const showDeleteDialog = ref(false)
const allPresets = ref<FilterPreset[]>([])
const activePresetId = ref<string | null>(null)
const newPresetName = ref('')
const newPresetIcon = ref<string | undefined>()
const newPresetColor = ref<string | undefined>()
const nameError = ref<string | null>(null)
const presetToDelete = ref<FilterPreset | null>(null)

// Computed
const defaultPresets = computed(() =>
  allPresets.value.filter(p => p.is_default)
)

const customPresets = computed(() =>
  allPresets.value.filter(p => !p.is_default)
)

const activePreset = computed(() =>
  allPresets.value.find(p => p.id === activePresetId.value)
)

const activePresetName = computed(() =>
  activePreset.value?.name || 'Выбрать пресет'
)

const activePresetIcon = computed(() =>
  activePreset.value?.icon || 'mdi-filter-outline'
)

const activePresetColor = computed(() =>
  activePreset.value?.color || 'default'
)

const iconOptions = computed(() => ICON_OPTIONS)
const colorOptions = computed(() => COLOR_OPTIONS)

const canSave = computed(() => {
  return newPresetName.value.trim().length > 0 && !nameError.value
})

// Lifecycle
onMounted(() => {
  loadAllPresets()
})

// Methods
function loadAllPresets(): void {
  allPresets.value = getAllPresets()
  activePresetId.value = getActivePresetId()
}

function validatePresetName(): void {
  const name = newPresetName.value.trim()

  if (!name) {
    nameError.value = null
    return
  }

  if (!isPresetNameAvailable(name)) {
    nameError.value = 'Пресет с таким названием уже существует'
  } else {
    nameError.value = null
  }
}

function isActive(presetId: string): boolean {
  return activePresetId.value === presetId
}

function applyPreset(preset: FilterPreset): void {
  profilesStore.unifiedFilters = { ...preset.filters }
  activePresetId.value = preset.id
  setActivePreset(preset.id)
  menu.value = false
}

function clearActivePreset(): void {
  activePresetId.value = null
  setActivePreset(null)
  menu.value = false
}

function saveNewPreset(): void {
  try {
    const preset = createPreset({
      name: newPresetName.value.trim(),
      filters: profilesStore.unifiedFilters,
      icon: newPresetIcon.value,
      color: newPresetColor.value
    })

    addPreset(preset)
    loadAllPresets()

    // Apply the new preset
    applyPreset(preset)

    // Close dialog and reset
    showSaveDialog.value = false
    resetSaveDialog()
  } catch (error: unknown) {
    nameError.value = getErrorMessage(error, 'Failed to save preset')
  }
}

function cancelSave(): void {
  showSaveDialog.value = false
  resetSaveDialog()
}

function resetSaveDialog(): void {
  newPresetName.value = ''
  newPresetIcon.value = undefined
  newPresetColor.value = undefined
  nameError.value = null
}

function editPreset(preset: FilterPreset): void {
  // For now, just apply the preset
  // TODO: Implement edit functionality in future
  applyPreset(preset)
}

function deletePresetConfirm(preset: FilterPreset): void {
  presetToDelete.value = preset
  showDeleteDialog.value = true
}

function confirmDelete(): void {
  if (!presetToDelete.value) return

  try {
    deletePresetUtil(presetToDelete.value.id)
    loadAllPresets()

    // Clear active if deleted
    if (activePresetId.value === presetToDelete.value.id) {
      clearActivePreset()
    }

    showDeleteDialog.value = false
    presetToDelete.value = null
  } catch (error: unknown) {
    console.error('Failed to delete preset:', error)
  }
}
</script>

<style scoped>
.gap-1 {
  gap: 4px;
}
</style>

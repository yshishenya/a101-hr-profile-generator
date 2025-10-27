<template>
  <v-dialog
    :model-value="modelValue"
    :theme="theme.global.name.value"
    max-width="1400px"
    scrollable
    persistent
    @update:model-value="handleClose"
  >
    <v-card v-if="profile">
      <!-- Header -->
      <v-sheet bg-color="surface-variant" class="pa-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center gap-4">
            <v-icon size="32" color="primary">mdi-pencil</v-icon>
            <div>
              <h2 class="text-h5">Редактирование профиля</h2>
              <div class="text-caption text-medium-emphasis">
                {{ profile.position_name }} • {{ profile.department_name }}
              </div>
            </div>
          </div>

          <div class="d-flex align-center gap-3">
            <!-- Save All Button -->
            <v-btn
              color="success"
              variant="elevated"
              prepend-icon="mdi-content-save"
              :loading="saving"
              :disabled="!hasUnsavedChanges"
              @click="handleSaveAll"
            >
              Сохранить
              <v-badge
                v-if="hasUnsavedChanges"
                color="warning"
                :content="unsavedChangesCount"
                inline
                class="ml-2"
              />
            </v-btn>

            <!-- Cancel Button -->
            <v-btn
              icon="mdi-close"
              variant="text"
              :disabled="saving"
              @click="handleClose"
            >
              <v-icon>mdi-close</v-icon>
              <v-tooltip activator="parent" location="bottom">
                Закрыть
              </v-tooltip>
            </v-btn>
          </div>
        </div>
      </v-sheet>

      <v-divider />

      <!-- Content with Sidebar -->
      <v-card-text class="pa-0" style="height: calc(100vh - 200px)">
        <v-row no-gutters style="height: 100%">
          <!-- Main Content Area (9 cols) -->
          <v-col cols="12" md="9" class="overflow-y-auto pa-6">
            <div class="content-area">
              <!-- Placeholder: ProfileContentEditor будет здесь -->
              <v-alert type="info" variant="tonal" class="mb-4">
                <v-alert-title>Редактор профиля</v-alert-title>
                <div class="text-body-2 mt-2">
                  Здесь будет редактор секций профиля. На данный момент это placeholder.
                </div>
              </v-alert>

              <!-- Example Section Card (will be replaced by ProfileContentEditor) -->
              <v-card class="mb-4">
                <v-sheet bg-color="surface-variant" class="pa-4">
                  <div class="d-flex align-center justify-space-between">
                    <div class="d-flex align-center">
                      <v-icon class="mr-2">mdi-brain</v-icon>
                      <span class="text-h6">Компетенции</span>
                      <v-chip size="small" color="success" class="ml-2">
                        <v-icon size="small">mdi-check</v-icon>
                      </v-chip>
                    </div>
                    <v-btn
                      icon="mdi-pencil"
                      variant="text"
                      size="small"
                    />
                  </div>
                </v-sheet>

                <v-card-text class="pa-4">
                  <v-chip
                    v-for="(skill, idx) in exampleSkills"
                    :key="idx"
                    class="ma-1"
                    variant="outlined"
                  >
                    {{ skill }}
                  </v-chip>
                </v-card-text>
              </v-card>

              <!-- More sections will be rendered here -->
            </div>
          </v-col>

          <!-- Metadata Sidebar (3 cols) -->
          <v-col
            cols="12"
            md="3"
            bg-color="surface-variant"
            class="overflow-y-auto pa-4"
          >
            <!-- Position Info (Read-only) -->
            <div class="mb-6">
              <div class="text-subtitle-2 text-medium-emphasis mb-1">Позиция</div>
              <div class="text-body-1 font-weight-medium">
                {{ profile.position_name }}
              </div>
            </div>

            <div class="mb-6">
              <div class="text-subtitle-2 text-medium-emphasis mb-1">Департамент</div>
              <div class="text-body-1">{{ profile.department_name }}</div>
            </div>

            <v-divider class="my-4" />

            <!-- Quick Navigation -->
            <div class="quick-nav mb-6">
              <div class="text-subtitle-2 mb-2">Быстрая навигация</div>
              <v-list density="compact" nav>
                <v-list-item
                  v-for="section in sections"
                  :key="section.id"
                  :active="activeSection === section.id"
                  @click="scrollToSection(section.id)"
                >
                  <template #prepend>
                    <v-icon :icon="section.icon" size="small" />
                    <v-badge
                      v-if="section.hasChanges"
                      dot
                      color="warning"
                      offset-x="-8"
                      offset-y="8"
                    />
                  </template>
                  <v-list-item-title>{{ section.title }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </div>

            <v-divider class="my-4" />

            <!-- Validation Status -->
            <div class="validation-status mb-6">
              <div class="text-subtitle-2 mb-2">Статус заполнения</div>
              <div
                v-for="section in sections"
                :key="`status-${section.id}`"
                class="d-flex align-center mb-2"
              >
                <v-icon
                  :icon="section.isValid ? 'mdi-check-circle' : 'mdi-alert-circle'"
                  :color="section.isValid ? 'success' : 'warning'"
                  size="small"
                  class="mr-2"
                />
                <span class="text-caption">{{ section.title }}</span>
              </div>
            </div>

            <v-divider class="my-4" />

            <!-- Keyboard Shortcuts -->
            <div class="shortcuts">
              <div class="text-subtitle-2 mb-2">💡 Горячие клавиши</div>
              <div class="text-caption text-medium-emphasis">
                <div class="mb-1">
                  <kbd class="px-2 py-1 rounded" style="background: rgba(var(--v-theme-surface-variant))">Ctrl+S</kbd>
                  Сохранить
                </div>
                <div class="mb-1">
                  <kbd class="px-2 py-1 rounded" style="background: rgba(var(--v-theme-surface-variant))">Esc</kbd>
                  Отменить
                </div>
                <div>
                  <kbd class="px-2 py-1 rounded" style="background: rgba(var(--v-theme-surface-variant))">Tab</kbd>
                  Следующая секция
                </div>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Unsaved Changes Dialog -->
    <v-dialog v-model="showUnsavedDialog" max-width="500px" persistent>
      <v-card>
        <v-sheet bg-color="surface-variant" class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div class="d-flex align-center gap-3">
              <v-icon color="warning">mdi-alert-circle</v-icon>
              <span class="text-h6">Несохраненные изменения</span>
            </div>
          </div>
        </v-sheet>

        <v-divider />

        <v-card-text class="pa-6">
          <div class="text-body-1 mb-4">
            У вас есть несохраненные изменения в {{ unsavedChangesCount }}
            {{ unsavedChangesCount === 1 ? 'секции' : 'секциях' }}.
            Сохранить перед выходом?
          </div>

          <v-alert type="info" variant="tonal" density="compact">
            <div class="text-caption">
              Несохраненные изменения будут потеряны, если вы выйдете без сохранения.
            </div>
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-btn variant="text" @click="cancelClose">
            Отмена
          </v-btn>
          <v-spacer />
          <v-btn
            variant="text"
            color="error"
            @click="discardAndClose"
          >
            Не сохранять
          </v-btn>
          <v-btn
            color="success"
            variant="elevated"
            :loading="saving"
            @click="saveAndClose"
          >
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTheme } from 'vuetify'
import type { UnifiedPosition } from '@/types/unified'

// Props
interface Props {
  modelValue: boolean
  profile: UnifiedPosition | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  save: []
}>()

// Theme
const theme = useTheme()

// Local state
const saving = ref(false)
const hasUnsavedChanges = ref(false)
const showUnsavedDialog = ref(false)
const activeSection = ref<string | null>(null)
const unsavedChangesCount = ref(0)

// Example data (will be replaced with real data from store)
const exampleSkills = ['Vue.js', 'TypeScript', 'Python', 'Docker', 'PostgreSQL']

// Section definitions (будет заменено на реальные данные)
const sections = ref([
  { id: 'competencies', title: 'Компетенции', icon: 'mdi-brain', isValid: true, hasChanges: false },
  { id: 'responsibilities', title: 'Обязанности', icon: 'mdi-clipboard-list', isValid: true, hasChanges: true },
  { id: 'skills', title: 'Навыки', icon: 'mdi-toolbox', isValid: true, hasChanges: false },
  { id: 'education', title: 'Образование', icon: 'mdi-school', isValid: false, hasChanges: false },
  { id: 'experience', title: 'Опыт работы', icon: 'mdi-briefcase', isValid: true, hasChanges: false },
])

// Methods
function handleClose(): void {
  if (hasUnsavedChanges.value && !saving.value) {
    showUnsavedDialog.value = true
  } else {
    emit('update:modelValue', false)
  }
}

function cancelClose(): void {
  showUnsavedDialog.value = false
}

function discardAndClose(): void {
  showUnsavedDialog.value = false
  hasUnsavedChanges.value = false
  emit('update:modelValue', false)
}

async function saveAndClose(): Promise<void> {
  await handleSaveAll()
  showUnsavedDialog.value = false
  emit('update:modelValue', false)
}

async function handleSaveAll(): Promise<void> {
  saving.value = true
  try {
    // TODO: Implement actual save logic via store
    emit('save')
    hasUnsavedChanges.value = false
  } catch (error: unknown) {
    console.error('Failed to save profile', error)
  } finally {
    saving.value = false
  }
}

function scrollToSection(sectionId: string): void {
  activeSection.value = sectionId
  // TODO: Implement smooth scroll to section
  console.log('Scroll to section:', sectionId)
}
</script>

<style scoped>
/* Ensure proper scrolling */
.overflow-y-auto {
  overflow-y: auto;
  overflow-x: hidden;
}

.content-area {
  max-width: 1000px;
}

.gap-3 {
  gap: 12px;
}

.gap-4 {
  gap: 16px;
}

/* Keyboard shortcut badge */
kbd {
  font-family: monospace;
  font-size: 0.875rem;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

/* Mobile adjustments */
@media (max-width: 960px) {
  .v-card-text {
    height: calc(100vh - 150px) !important;
  }
}
</style>

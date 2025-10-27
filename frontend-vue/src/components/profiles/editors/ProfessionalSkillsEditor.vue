<template>
  <div class="professional-skills-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-expansion-panels variant="accordion">
        <v-expansion-panel
          v-for="(category, index) in localSkills"
          :key="index"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center gap-2">
              <v-icon size="small">mdi-toolbox</v-icon>
              <span class="font-weight-medium">{{ category.skill_category }}</span>
              <v-chip size="x-small" variant="outlined">
                {{ category.specific_skills.length }} навыков
              </v-chip>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-table density="compact">
              <thead>
                <tr>
                  <th>Навык</th>
                  <th style="width: 100px">Уровень</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(skill, skillIdx) in category.specific_skills"
                  :key="skillIdx"
                >
                  <td>{{ skill.skill_name }}</td>
                  <td>
                    <v-chip
                      size="small"
                      :color="getProficiencyColor(skill.proficiency_level)"
                      variant="flat"
                    >
                      {{ skill.proficiency_level }}
                    </v-chip>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <div v-if="localSkills.length === 0" class="text-body-2 text-medium-emphasis pa-4">
        Нет навыков. Нажмите "Редактировать" для добавления.
      </div>
    </div>

    <!-- Edit Mode -->
    <div v-else class="edit-mode">
      <!-- Info Alert -->
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        <div class="text-caption">
          💡 Группируйте навыки по категориям. Уровень владения: 1 (базовый) - 4 (экспертный).
        </div>
      </v-alert>

      <!-- Skill Categories -->
      <v-expansion-panels
        v-model="openPanels"
        variant="accordion"
        multiple
        class="mb-4"
      >
        <v-expansion-panel
          v-for="(category, catIndex) in localSkills"
          :key="category.id"
          :value="category.id"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center justify-space-between" style="width: 100%">
              <div class="d-flex align-center gap-2">
                <v-icon size="small">mdi-folder</v-icon>
                <span class="font-weight-medium">
                  {{ category.skill_category || 'Новая категория' }}
                </span>
                <v-chip size="x-small" variant="outlined">
                  {{ category.specific_skills.length }} навыков
                </v-chip>
              </div>

              <v-btn
                icon
                variant="text"
                size="x-small"
                color="error"
                @click.stop="removeCategory(catIndex)"
              >
                <v-icon size="small">mdi-delete</v-icon>
                <v-tooltip activator="parent" location="bottom">
                  Удалить категорию
                </v-tooltip>
              </v-btn>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <!-- Category Name -->
            <v-text-field
              v-model="category.skill_category"
              variant="outlined"
              label="Название категории"
              placeholder="Например: Технические навыки"
              density="comfortable"
              class="mb-4"
            >
              <template #prepend-inner>
                <v-icon>mdi-tag</v-icon>
              </template>
            </v-text-field>

            <!-- Skills Table -->
            <div class="skills-table mb-3">
              <div class="text-subtitle-2 mb-2">Навыки в категории</div>

              <v-table density="compact" class="mb-2">
                <thead>
                  <tr>
                    <th style="width: 60%">Название навыка</th>
                    <th style="width: 30%">Уровень (1-4)</th>
                    <th style="width: 10%">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(skill, skillIdx) in category.specific_skills"
                    :key="skillIdx"
                  >
                    <td>
                      <v-text-field
                        v-model="skill.skill_name"
                        variant="plain"
                        density="compact"
                        hide-details
                        placeholder="Название навыка"
                      />
                    </td>
                    <td>
                      <v-select
                        v-model="skill.proficiency_level"
                        :items="proficiencyLevels"
                        item-title="label"
                        item-value="value"
                        variant="plain"
                        density="compact"
                        hide-details
                      >
                        <template #selection="{ item }">
                          <v-chip
                            size="small"
                            :color="getProficiencyColor(item.value)"
                            variant="flat"
                          >
                            {{ item.value }}
                          </v-chip>
                        </template>
                      </v-select>
                    </td>
                    <td>
                      <v-btn
                        icon
                        variant="text"
                        size="x-small"
                        color="error"
                        @click="removeSkill(catIndex, skillIdx)"
                      >
                        <v-icon size="small">mdi-delete</v-icon>
                      </v-btn>
                    </td>
                  </tr>

                  <!-- Empty state -->
                  <tr v-if="category.specific_skills.length === 0">
                    <td colspan="3" class="text-center text-caption text-medium-emphasis pa-4">
                      Нет навыков. Нажмите "Добавить навык" ниже.
                    </td>
                  </tr>
                </tbody>
              </v-table>

              <!-- Add Skill Button -->
              <v-btn
                prepend-icon="mdi-plus"
                variant="outlined"
                size="small"
                @click="addSkill(catIndex)"
              >
                Добавить навык
              </v-btn>
            </div>

            <!-- Category Validation -->
            <v-alert
              v-if="!category.skill_category || category.specific_skills.length === 0"
              type="warning"
              variant="tonal"
              density="compact"
            >
              <div class="text-caption">
                ⚠️ {{ !category.skill_category ? 'Укажите название категории. ' : '' }}
                {{ category.specific_skills.length === 0 ? 'Добавьте хотя бы один навык.' : '' }}
              </div>
            </v-alert>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Add Category Button -->
      <v-btn
        prepend-icon="mdi-plus"
        variant="outlined"
        color="primary"
        block
        @click="addCategory"
      >
        Добавить категорию навыков
      </v-btn>

      <!-- Proficiency Level Legend -->
      <v-card variant="tonal" class="mt-4 pa-3">
        <div class="text-subtitle-2 mb-2">Уровни владения:</div>
        <div class="d-flex flex-wrap gap-2">
          <v-chip
            v-for="level in proficiencyLevels"
            :key="level.value"
            size="small"
            :color="getProficiencyColor(level.value)"
            variant="flat"
          >
            {{ level.value }} - {{ level.label }}
          </v-chip>
        </div>
      </v-card>

      <!-- Overall Statistics -->
      <v-alert
        type="info"
        variant="tonal"
        density="compact"
        class="mt-4"
      >
        <div class="text-caption">
          Всего: {{ localSkills.length }} {{ categoriesLabel }},
          {{ totalSkills }} {{ skillsLabel }}
        </div>
      </v-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

// Types
interface Skill {
  skill_name: string
  proficiency_level: number
}

interface SkillCategory {
  id: string
  skill_category: string
  specific_skills: Skill[]
}

// Props
interface Props {
  modelValue: Array<{
    skill_category: string
    specific_skills: Array<{
      skill_name: string
      proficiency_level: number
    }>
  }>
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [
    value: Array<{
      skill_category: string
      specific_skills: Array<{ skill_name: string; proficiency_level: number }>
    }>
  ]
}>()

// Local state
const localSkills = ref<SkillCategory[]>([])
const openPanels = ref<string[]>([])

// Proficiency levels
const proficiencyLevels = [
  { value: 1, label: 'Базовый' },
  { value: 2, label: 'Средний' },
  { value: 3, label: 'Продвинутый' },
  { value: 4, label: 'Экспертный' },
]

// Computed
const totalSkills = computed(() => {
  return localSkills.value.reduce(
    (sum, cat) => sum + cat.specific_skills.length,
    0
  )
})

const categoriesLabel = computed(() => {
  const count = localSkills.value.length
  if (count === 1) return 'категория'
  if (count >= 2 && count <= 4) return 'категории'
  return 'категорий'
})

const skillsLabel = computed(() => {
  const count = totalSkills.value
  if (count === 1) return 'навык'
  if (count >= 2 && count <= 4) return 'навыка'
  return 'навыков'
})

// Methods
function getProficiencyColor(level: number): string {
  switch (level) {
    case 1:
      return 'grey'
    case 2:
      return 'info'
    case 3:
      return 'success'
    case 4:
      return 'primary'
    default:
      return 'grey'
  }
}

function initializeSkills(): void {
  localSkills.value = (props.modelValue || []).map((cat, index) => ({
    id: `cat-${Date.now()}-${index}`,
    skill_category: cat.skill_category,
    specific_skills: [...cat.specific_skills],
  }))

  // Open all panels in edit mode
  if (!props.readonly) {
    openPanels.value = localSkills.value.map((c) => c.id)
  }
}

function addCategory(): void {
  const newCategory: SkillCategory = {
    id: `cat-${Date.now()}`,
    skill_category: '',
    specific_skills: [],
  }
  localSkills.value.push(newCategory)

  // Auto-open the new panel
  openPanels.value.push(newCategory.id)

  handleUpdate()
}

function removeCategory(index: number): void {
  const categoryId = localSkills.value[index].id
  localSkills.value.splice(index, 1)

  // Remove from open panels
  openPanels.value = openPanels.value.filter((id) => id !== categoryId)

  handleUpdate()
}

function addSkill(categoryIndex: number): void {
  localSkills.value[categoryIndex].specific_skills.push({
    skill_name: '',
    proficiency_level: 2,
  })
  handleUpdate()
}

function removeSkill(categoryIndex: number, skillIndex: number): void {
  localSkills.value[categoryIndex].specific_skills.splice(skillIndex, 1)
  handleUpdate()
}

function handleUpdate(): void {
  // Clean up and emit
  const cleanedSkills = localSkills.value
    .map((cat) => ({
      skill_category: cat.skill_category.trim(),
      specific_skills: cat.specific_skills.filter(
        (s) => s.skill_name && s.skill_name.trim() !== ''
      ),
    }))
    .filter((cat) => cat.skill_category && cat.specific_skills.length > 0)

  emit('update:modelValue', cleanedSkills)
}

// Initialize on mount
initializeSkills()

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    const currentJson = JSON.stringify(
      localSkills.value.map((c) => ({
        skill_category: c.skill_category,
        specific_skills: c.specific_skills,
      }))
    )
    const newJson = JSON.stringify(newValue)

    if (currentJson !== newJson) {
      initializeSkills()
    }
  },
  { deep: true }
)

// Watch for changes in local skills
watch(
  localSkills,
  () => {
    handleUpdate()
  },
  { deep: true }
)
</script>

<style scoped>
.professional-skills-editor {
  min-height: 200px;
}

.readonly-view,
.edit-mode {
  padding: 0;
}

.gap-2 {
  gap: 8px;
}

.skills-table {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  padding: 8px;
}

/* Table styling */
.v-table thead th {
  font-weight: 600;
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
}

.v-table tbody tr:hover {
  background-color: rgba(var(--v-theme-surface-variant), 0.3);
}
</style>

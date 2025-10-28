<template>
  <div class="professional-skills-editor">
    <!-- Read-only View Mode -->
    <div v-if="readonly" class="readonly-view">
      <v-expansion-panels variant="accordion">
        <SkillCategoryReadonly
          v-for="(category, index) in localSkills"
          :key="index"
          :category="category"
        />
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

          <SkillCategoryEdit
            :category="category"
            @update:name="(value) => updateCategoryName(catIndex, value)"
            @update:skill-name="(skillIdx, value) => updateSkillName(catIndex, skillIdx, value)"
            @update:proficiency-level="(skillIdx, value) => updateProficiencyLevel(catIndex, skillIdx, value)"
            @add-skill="addSkill(catIndex)"
            @remove-skill="(skillIdx) => removeSkill(catIndex, skillIdx)"
          />
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

      <!-- Legend and Statistics -->
      <ProficiencyLegend
        :categories-count="localSkills.length"
        :total-skills="totalSkills"
        class="mt-4"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import SkillCategoryReadonly from './sub-components/SkillCategoryReadonly.vue'
import SkillCategoryEdit from './sub-components/SkillCategoryEdit.vue'
import ProficiencyLegend from './sub-components/ProficiencyLegend.vue'

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

// Computed
const totalSkills = computed(() => {
  return localSkills.value.reduce(
    (sum, cat) => sum + cat.specific_skills.length,
    0
  )
})

// Methods
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
  const category = localSkills.value[index]
  if (!category) return

  const categoryId = category.id
  localSkills.value.splice(index, 1)

  // Remove from open panels
  openPanels.value = openPanels.value.filter((id) => id !== categoryId)

  handleUpdate()
}

function updateCategoryName(categoryIndex: number, value: string): void {
  const category = localSkills.value[categoryIndex]
  if (!category) return

  category.skill_category = value
}

function addSkill(categoryIndex: number): void {
  const category = localSkills.value[categoryIndex]
  if (!category) return

  category.specific_skills.push({
    skill_name: '',
    proficiency_level: 2,
  })
  handleUpdate()
}

function removeSkill(categoryIndex: number, skillIndex: number): void {
  const category = localSkills.value[categoryIndex]
  if (!category) return

  category.specific_skills.splice(skillIndex, 1)
  handleUpdate()
}

function updateSkillName(categoryIndex: number, skillIndex: number, value: string): void {
  const category = localSkills.value[categoryIndex]
  const skill = category?.specific_skills[skillIndex]
  if (!skill) return

  skill.skill_name = value
}

function updateProficiencyLevel(categoryIndex: number, skillIndex: number, value: number): void {
  const category = localSkills.value[categoryIndex]
  const skill = category?.specific_skills[skillIndex]
  if (!skill) return

  skill.proficiency_level = value
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

/* Table styling */
.v-table thead th {
  font-weight: 600;
  background-color: rgba(var(--v-theme-surface-variant), 0.5);
}

.v-table tbody tr:hover {
  background-color: rgba(var(--v-theme-surface-variant), 0.3);
}
</style>

<template>
  <v-expansion-panel-text>
    <!-- Category Name -->
    <v-text-field
      :model-value="category.skill_category"
      variant="outlined"
      label="Название категории"
      placeholder="Например: Технические навыки"
      density="comfortable"
      class="mb-4"
      @update:model-value="emit('update:name', $event)"
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
          <SkillTableRow
            v-for="(skill, skillIdx) in category.specific_skills"
            :key="skillIdx"
            :skill="skill"
            @update:skill-name="(value) => emit('update:skill-name', skillIdx, value)"
            @update:proficiency-level="(value) => emit('update:proficiency-level', skillIdx, value)"
            @remove="emit('remove-skill', skillIdx)"
          />

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
        @click="emit('add-skill')"
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
</template>

<script setup lang="ts">
import SkillTableRow from './SkillTableRow.vue'

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
  category: SkillCategory
}

defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:name': [value: string]
  'update:skill-name': [skillIdx: number, value: string]
  'update:proficiency-level': [skillIdx: number, value: number]
  'add-skill': []
  'remove-skill': [skillIdx: number]
}>()
</script>

<style scoped>
.skills-table {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
  padding: 8px;
}
</style>

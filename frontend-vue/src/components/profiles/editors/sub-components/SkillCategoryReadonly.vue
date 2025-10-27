<template>
  <v-expansion-panel>
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
</template>

<script setup lang="ts">
import { getProficiencyColor } from '../constants/proficiencyLevels'

// Types
interface Skill {
  skill_name: string
  proficiency_level: number
}

interface SkillCategory {
  skill_category: string
  specific_skills: Skill[]
}

// Props
interface Props {
  category: SkillCategory
}

defineProps<Props>()
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>

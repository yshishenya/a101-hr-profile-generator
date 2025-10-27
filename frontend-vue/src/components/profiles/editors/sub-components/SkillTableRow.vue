<template>
  <tr>
    <td>
      <v-text-field
        :model-value="skill.skill_name"
        variant="plain"
        density="compact"
        hide-details
        placeholder="Название навыка"
        @update:model-value="updateSkillName"
      />
    </td>
    <td>
      <v-select
        :model-value="skill.proficiency_level"
        :items="proficiencyLevels"
        item-title="label"
        item-value="value"
        variant="plain"
        density="compact"
        hide-details
        @update:model-value="updateProficiencyLevel"
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
        @click="emit('remove')"
      >
        <v-icon size="small">mdi-delete</v-icon>
      </v-btn>
    </td>
  </tr>
</template>

<script setup lang="ts">
import { PROFICIENCY_LEVELS, getProficiencyColor } from '../constants/proficiencyLevels'

// Types
interface Skill {
  skill_name: string
  proficiency_level: number
}

// Props
interface Props {
  skill: Skill
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:skill-name': [value: string]
  'update:proficiency-level': [value: number]
  remove: []
}>()

// Constants
const proficiencyLevels = PROFICIENCY_LEVELS

// Methods
function updateSkillName(value: string): void {
  emit('update:skill-name', value)
}

function updateProficiencyLevel(value: number): void {
  emit('update:proficiency-level', value)
}
</script>

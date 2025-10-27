<template>
  <div>
    <!-- Proficiency Level Legend -->
    <v-card variant="tonal" class="pa-3">
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
        Всего: {{ categoriesCount }} {{ categoriesLabel }},
        {{ totalSkills }} {{ skillsLabel }}
      </div>
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PROFICIENCY_LEVELS, getProficiencyColor } from '../constants/proficiencyLevels'

// Props
interface Props {
  categoriesCount: number
  totalSkills: number
}

const props = defineProps<Props>()

// Constants
const proficiencyLevels = PROFICIENCY_LEVELS

// Computed
const categoriesLabel = computed(() => {
  const count = props.categoriesCount
  if (count === 1) return 'категория'
  if (count >= 2 && count <= 4) return 'категории'
  return 'категорий'
})

const skillsLabel = computed(() => {
  const count = props.totalSkills
  if (count === 1) return 'навык'
  if (count >= 2 && count <= 4) return 'навыка'
  return 'навыков'
})
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>

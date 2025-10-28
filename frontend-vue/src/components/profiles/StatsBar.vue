<template>
  <v-card flat class="stats-bar px-6 py-4">
    <v-row no-gutters align="center" class="stats-row">
      <!-- Total Positions -->
      <v-col cols="auto" class="stat-item">
        <div class="d-flex align-center">
          <v-icon :color="iconColor('primary')" size="small" class="mr-2">
            mdi-briefcase-outline
          </v-icon>
          <div>
            <div class="text-caption text-medium-emphasis">Всего</div>
            <div class="text-h6 font-weight-bold">{{ totalPositions }}</div>
          </div>
        </div>
      </v-col>

      <v-divider vertical class="mx-4" />

      <!-- Generated Profiles -->
      <v-col cols="auto" class="stat-item">
        <div class="d-flex align-center">
          <v-icon :color="iconColor('success')" size="small" class="mr-2">
            mdi-check-circle
          </v-icon>
          <div>
            <div class="text-caption text-medium-emphasis">Сгенерировано</div>
            <div class="text-h6 font-weight-bold">{{ generatedCount }}</div>
          </div>
        </div>
      </v-col>

      <v-divider vertical class="mx-4" />

      <!-- Coverage Percentage -->
      <v-col cols="auto" class="stat-item">
        <div class="d-flex align-center">
          <v-icon :color="iconColor('info')" size="small" class="mr-2">
            mdi-chart-arc
          </v-icon>
          <div>
            <div class="text-caption text-medium-emphasis">Покрытие</div>
            <div class="text-h6 font-weight-bold">{{ coveragePercent }}%</div>
          </div>
        </div>
      </v-col>

      <v-divider vertical class="mx-4" />

      <!-- In Progress -->
      <v-col cols="auto" class="stat-item">
        <div class="d-flex align-center">
          <v-icon :color="iconColor('warning')" size="small" class="mr-2">
            mdi-clock-outline
          </v-icon>
          <div>
            <div class="text-caption text-medium-emphasis">В процессе</div>
            <div class="text-h6 font-weight-bold">{{ inProgressCount }}</div>
          </div>
        </div>
      </v-col>

      <v-spacer />

      <!-- Refresh Button -->
      <v-col cols="auto">
        <v-btn
          :loading="loading"
          variant="text"
          size="small"
          prepend-icon="mdi-refresh"
          @click="$emit('refresh')"
        >
          Обновить
        </v-btn>
      </v-col>
    </v-row>

    <!-- Progress Bar (optional visual indicator) -->
    <v-progress-linear
      v-if="showProgress"
      :model-value="coveragePercent"
      color="success"
      height="2"
      class="mt-2"
    />
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  totalPositions: number
  generatedCount: number
  inProgressCount: number
  loading?: boolean
  showProgress?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showProgress: false
})

// Emits
defineEmits<{
  refresh: []
}>()

// Computed
const coveragePercent = computed(() => {
  if (props.totalPositions === 0) return 0
  return Math.round((props.generatedCount / props.totalPositions) * 100)
})

// Helper to get icon color from Vuetify theme
function iconColor(color: string): string {
  return color
}
</script>

<style scoped>
.stats-bar {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
}

.stats-row {
  min-height: 60px;
}

.stat-item {
  min-width: 120px;
}
</style>

<template>
  <v-card class="stats-overview" elevation="2">
    <v-card-text>
      <v-row dense>
        <!-- Total Positions -->
        <v-col cols="12" sm="6" md="3">
          <div class="stat-item">
            <div class="stat-icon">
              <v-icon color="primary" size="x-large">mdi-briefcase-outline</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Всего позиций</div>
              <div class="stat-value">{{ statistics.total_positions }}</div>
            </div>
          </div>
        </v-col>

        <!-- Generated Profiles -->
        <v-col cols="12" sm="6" md="3">
          <div class="stat-item">
            <div class="stat-icon">
              <v-icon color="success" size="x-large">mdi-check-circle-outline</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Сгенерировано</div>
              <div class="stat-value">{{ statistics.generated_count }}</div>
            </div>
          </div>
        </v-col>

        <!-- Generating -->
        <v-col cols="12" sm="6" md="3">
          <div class="stat-item">
            <div class="stat-icon">
              <v-icon color="warning" size="x-large">mdi-clock-outline</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">В процессе</div>
              <div class="stat-value">{{ statistics.generating_count }}</div>
            </div>
          </div>
        </v-col>

        <!-- Coverage Percentage -->
        <v-col cols="12" sm="6" md="3">
          <div class="stat-item">
            <div class="stat-icon">
              <v-icon color="info" size="x-large">mdi-chart-donut</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">Покрытие</div>
              <div class="stat-value">
                {{ statistics.coverage_percentage }}%
                <v-progress-linear
                  :model-value="statistics.coverage_percentage"
                  color="info"
                  height="4"
                  class="mt-1"
                />
              </div>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- Last Updated -->
      <v-row v-if="statistics.last_updated" dense class="mt-2">
        <v-col cols="12">
          <div class="text-caption text-medium-emphasis text-center">
            Обновлено: {{ formatTimestamp(statistics.last_updated) }}
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useProfilesStore } from '@/stores/profiles'
import type { ProfileStatistics } from '@/types/unified'

// Store
const profilesStore = useProfilesStore()

// Get statistics from store
const statistics = computed<ProfileStatistics>(() => profilesStore.statistics)

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'только что'
  if (diffMins < 60) return `${diffMins} мин назад`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} ч назад`

  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}
</script>

<style scoped>
.stats-overview {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.stat-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 0.75rem;
  color: rgb(var(--v-theme-on-surface-variant));
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgb(var(--v-theme-on-surface));
  line-height: 1.2;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .stat-item {
    padding: 12px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
  }

  .stat-value {
    font-size: 1.25rem;
  }
}

@media (max-width: 600px) {
  .stat-item {
    justify-content: center;
    text-align: center;
    flex-direction: column;
    gap: 8px;
  }
}
</style>

<template>
  <BaseCard class="stats-card">
    <v-card-text class="pa-4">
      <div class="d-flex align-center" :class="{ 'mb-3': showProgress }">
        <div v-if="icon" class="stat-icon mr-3">
          <v-icon :color="iconColor" size="40">{{ icon }}</v-icon>
        </div>
        <div class="stat-content">
          <div class="text-h4 font-weight-bold">{{ formattedValue }}</div>
          <div class="text-subtitle-2 text-medium-emphasis">{{ label }}</div>
        </div>
      </div>

      <!-- Progress Bar (optional) -->
      <v-progress-linear
        v-if="showProgress"
        :model-value="progressValue"
        :color="progressColor || iconColor"
        height="4"
        rounded
      />

      <!-- Last Updated (optional) -->
      <div v-if="lastUpdated" class="stat-timestamp">
        {{ formatTimestamp(lastUpdated) }}
      </div>
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseCard from './BaseCard.vue'

/**
 * StatsCard - Reusable statistics card component
 *
 * Unified component for displaying statistics with icon, value, label, and optional progress bar.
 * Ensures consistency across Dashboard, Generator, and Profiles views.
 *
 * @example Basic usage
 * <StatsCard
 *   icon="mdi-briefcase-outline"
 *   icon-color="primary"
 *   label="Total Positions"
 *   :value="1234"
 * />
 *
 * @example With progress bar
 * <StatsCard
 *   icon="mdi-account-check-outline"
 *   icon-color="success"
 *   label="Profiles Generated"
 *   :value="856"
 *   :progress-value="69.5"
 * />
 *
 * @example With timestamp
 * <StatsCard
 *   icon="mdi-chart-arc"
 *   icon-color="info"
 *   label="Completion"
 *   value="69.5%"
 *   :progress-value="69.5"
 *   last-updated="2025-10-26T15:30:00Z"
 * />
 */

interface Props {
  /**
   * Material Design icon name
   * @example "mdi-briefcase-outline"
   */
  icon?: string

  /**
   * Icon and progress bar color
   * @default "primary"
   * @example "success", "warning", "info", "error"
   */
  iconColor?: string

  /**
   * Label text displayed below value
   * @example "Total Positions"
   */
  label: string

  /**
   * Main stat value (number or formatted string)
   * @example 1234 or "69.5%"
   */
  value: number | string

  /**
   * Progress bar value (0-100)
   * If provided, displays progress bar
   * @example 69.5
   */
  progressValue?: number

  /**
   * Override progress bar color (defaults to iconColor)
   * @example "success"
   */
  progressColor?: string

  /**
   * ISO 8601 timestamp for last update
   * @example "2025-10-26T15:30:00Z"
   */
  lastUpdated?: string

  /**
   * Number of decimal places for numeric values
   * @default 0
   */
  decimals?: number
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'primary',
  decimals: 0
})

// Computed
const formattedValue = computed(() => {
  if (typeof props.value === 'string') {
    return props.value
  }

  // Format number with locale
  return props.value.toLocaleString('ru-RU', {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals
  })
})

const showProgress = computed(() => props.progressValue !== undefined)

/**
 * Format ISO 8601 timestamp for display
 * Uses relative time for recent updates, absolute date for older ones
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
.stats-card {
  height: 100%;
}

.d-flex {
  display: flex;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-timestamp {
  font-size: 0.75rem;
  color: rgb(var(--v-theme-on-surface-variant));
  text-align: center;
  margin-top: 8px;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .stat-icon {
    width: 48px;
    height: 48px;
  }

  .stat-value {
    font-size: 1.25rem;
  }
}

@media (max-width: 600px) {
  .d-flex {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 8px;
  }
}
</style>

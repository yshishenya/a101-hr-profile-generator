<template>
  <div class="profile-metadata">
    <h3 class="text-h6 mb-4">Метаданные</h3>

    <!-- Profile Info -->
    <v-card variant="outlined" class="mb-4">
      <v-list density="compact">
        <v-list-item>
          <template #prepend>
            <v-icon color="primary">mdi-identifier</v-icon>
          </template>
          <v-list-item-title class="text-caption text-medium-emphasis">
            ID профиля
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ profile.profile_id }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider />

        <v-list-item v-if="profile.current_version">
          <template #prepend>
            <v-icon color="info">mdi-source-branch</v-icon>
          </template>
          <v-list-item-title class="text-caption text-medium-emphasis">
            Версия
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            v{{ profile.current_version }}
            <v-chip
              v-if="profile.version_count && profile.version_count > 1"
              size="x-small"
              class="ml-2"
              color="info"
            >
              +{{ profile.version_count - 1 }}
            </v-chip>
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider v-if="profile.current_version" />

        <v-list-item v-if="profile.created_at">
          <template #prepend>
            <v-icon color="success">mdi-calendar-clock</v-icon>
          </template>
          <v-list-item-title class="text-caption text-medium-emphasis">
            Создан
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ formatDate(profile.created_at) }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider v-if="profile.created_at" />

        <v-list-item v-if="profile.created_by">
          <template #prepend>
            <v-icon color="warning">mdi-account</v-icon>
          </template>
          <v-list-item-title class="text-caption text-medium-emphasis">
            Автор
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ profile.created_by }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card>

    <!-- Quality Scores -->
    <v-card variant="outlined" class="mb-4">
      <v-card-title class="text-subtitle-2 pa-3">
        <v-icon class="mr-2" size="small">mdi-star-check</v-icon>
        Оценки качества
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-3">
        <div v-if="profile.quality_score !== undefined" class="mb-3">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-caption">Качество</span>
            <span class="text-body-2 font-weight-bold">{{ profile.quality_score }}%</span>
          </div>
          <v-progress-linear
            :model-value="profile.quality_score"
            :color="getScoreColor(profile.quality_score)"
            height="8"
            rounded
          />
        </div>

        <div v-if="profile.completeness_score !== undefined">
          <div class="d-flex justify-space-between align-center mb-1">
            <span class="text-caption">Полнота</span>
            <span class="text-body-2 font-weight-bold">{{ profile.completeness_score }}%</span>
          </div>
          <v-progress-linear
            :model-value="profile.completeness_score"
            :color="getScoreColor(profile.completeness_score)"
            height="8"
            rounded
          />
        </div>

        <div v-if="!profile.quality_score && !profile.completeness_score" class="text-caption text-medium-emphasis">
          Оценки качества недоступны
        </div>
      </v-card-text>
    </v-card>

    <!-- Generation Metadata (if available) -->
    <v-card v-if="metadata" variant="outlined" class="mb-4">
      <v-card-title class="text-subtitle-2 pa-3">
        <v-icon class="mr-2" size="small">mdi-cog</v-icon>
        Параметры генерации
      </v-card-title>

      <v-divider />

      <v-list density="compact">
        <v-list-item v-if="metadata.generation?.timestamp">
          <v-list-item-title class="text-caption text-medium-emphasis">
            Дата генерации
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ formatDate(metadata.generation.timestamp) }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider v-if="metadata.generation?.timestamp" />

        <v-list-item v-if="metadata.generation?.duration">
          <v-list-item-title class="text-caption text-medium-emphasis">
            Длительность
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ formatDuration(metadata.generation.duration) }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider v-if="metadata.generation?.duration" />

        <v-list-item v-if="metadata.llm?.model">
          <v-list-item-title class="text-caption text-medium-emphasis">
            Модель
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ metadata.llm.model }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-divider v-if="metadata.llm?.model" />

        <v-list-item v-if="metadata.llm?.tokens">
          <v-list-item-title class="text-caption text-medium-emphasis">
            Токены
          </v-list-item-title>
          <v-list-item-subtitle class="text-body-2 mt-1">
            {{ formatNumber(metadata.llm.tokens.total) }}
            (вход: {{ formatNumber(metadata.llm.tokens.input) }},
            выход: {{ formatNumber(metadata.llm.tokens.output) }})
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import type { UnifiedPosition } from '@/types/unified'
import type { GenerationMetadata } from '@/types/profile'
import { formatDate, formatDuration, formatNumber } from '@/utils/formatters'

// Props
interface Props {
  profile: UnifiedPosition
  metadata?: GenerationMetadata
}

defineProps<Props>()

// Score thresholds for quality color coding
const SCORE_THRESHOLDS = {
  EXCELLENT: 80,  // Green - excellent quality
  GOOD: 60,       // Blue - good quality
  FAIR: 40        // Orange - fair quality (below this is red/error)
} as const

// Methods
function getScoreColor(score: number): string {
  if (score >= SCORE_THRESHOLDS.EXCELLENT) return 'success'
  if (score >= SCORE_THRESHOLDS.GOOD) return 'info'
  if (score >= SCORE_THRESHOLDS.FAIR) return 'warning'
  return 'error'
}
</script>

<style scoped>
.profile-metadata {
  position: sticky;
  top: 0;
}

.v-list-item {
  min-height: auto;
  padding: 8px 12px;
}

.v-list-item-title {
  font-size: 0.75rem;
  line-height: 1.2;
}

.v-list-item-subtitle {
  opacity: 1;
  word-break: break-word;
}
</style>

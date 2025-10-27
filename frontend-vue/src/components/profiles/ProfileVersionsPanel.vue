<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-history</v-icon>
      История версий
      <v-chip class="ml-auto" size="small" color="primary">
        {{ versions.length }} версий
      </v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text v-if="loading" class="py-4">
      <v-timeline align="start" density="compact" side="end">
        <v-timeline-item
          v-for="i in 3"
          :key="i"
          dot-color="grey"
          icon="mdi-file-document"
          size="small"
        >
          <template #opposite>
            <v-skeleton-loader type="text" width="30" />
          </template>

          <v-card variant="outlined">
            <v-card-title class="py-2">
              <v-skeleton-loader type="chip" width="80" />
              <v-spacer />
              <v-skeleton-loader type="button" width="40" />
            </v-card-title>

            <v-card-text class="py-2">
              <v-skeleton-loader type="text" width="200" />
              <div class="mt-2">
                <v-skeleton-loader type="text" width="100%" />
              </div>
              <div class="mt-1">
                <v-skeleton-loader type="text" width="100%" />
              </div>
            </v-card-text>
          </v-card>
        </v-timeline-item>
      </v-timeline>
    </v-card-text>

    <v-card-text v-else-if="error" class="text-center py-8">
      <v-icon size="64" color="error">mdi-alert-circle</v-icon>
      <p class="text-body-1 mt-4 text-error">{{ error }}</p>
      <v-btn variant="outlined" @click="emit('retry')">
        Повторить
      </v-btn>
    </v-card-text>

    <v-card-text v-else-if="versions.length === 0" class="text-center py-8">
      <v-icon size="64" color="grey">mdi-file-document-outline</v-icon>
      <p class="text-body-1 mt-4">Версии не найдены</p>
    </v-card-text>

    <v-timeline v-else align="start" density="compact" side="end">
      <v-timeline-item
        v-for="version in versions"
        :key="version.version_number"
        :dot-color="version.is_current ? 'primary' : 'grey'"
        :icon="getVersionIcon(version.version_type)"
        size="small"
      >
        <template #opposite>
          <div class="text-caption text-grey">
            v{{ version.version_number }}
          </div>
        </template>

        <v-card :variant="version.is_current ? 'tonal' : 'outlined'">
          <v-card-title class="d-flex align-center py-2">
            <v-chip
              v-if="version.is_current"
              size="x-small"
              color="success"
              class="mr-2"
            >
              Текущая
            </v-chip>
            <v-chip
              v-if="version.version_number === 1"
              size="x-small"
              color="grey"
              class="mr-2"
            >
              Оригинал
            </v-chip>
            <span class="text-body-2">
              {{ getVersionTypeLabel(version.version_type) }}
            </span>
            <v-spacer />
            <v-menu>
              <template #activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  variant="text"
                  size="small"
                  v-bind="props"
                />
              </template>
              <v-list density="compact">
                <v-list-item
                  v-if="!version.is_current"
                  prepend-icon="mdi-check-circle"
                  @click="emit('set-active', version.version_number)"
                >
                  <v-list-item-title>Сделать текущей</v-list-item-title>
                </v-list-item>

                <v-list-subheader>Скачать</v-list-subheader>
                <v-list-item
                  prepend-icon="mdi-code-json"
                  @click="emit('download', version.version_number, 'json')"
                >
                  <v-list-item-title>JSON</v-list-item-title>
                </v-list-item>
                <v-list-item
                  prepend-icon="mdi-file-document"
                  @click="emit('download', version.version_number, 'md')"
                >
                  <v-list-item-title>Markdown</v-list-item-title>
                </v-list-item>
                <v-list-item
                  prepend-icon="mdi-file-word"
                  @click="emit('download', version.version_number, 'docx')"
                >
                  <v-list-item-title>Word</v-list-item-title>
                </v-list-item>

                <v-divider v-if="!version.is_current && versions.length > 1" />

                <v-list-item
                  v-if="!version.is_current && versions.length > 1"
                  prepend-icon="mdi-delete"
                  @click="emit('delete', version.version_number)"
                >
                  <v-list-item-title class="text-error">
                    Удалить
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-title>

          <v-card-text class="py-2">
            <div class="text-caption text-grey">
              <v-icon size="x-small" class="mr-1">mdi-account</v-icon>
              {{ version.created_by_username }}
              <v-icon size="x-small" class="ml-3 mr-1">mdi-clock-outline</v-icon>
              {{ formatDate(version.created_at) }}
            </div>

            <div v-if="version.validation_score !== null" class="mt-2">
              <div class="d-flex align-center text-caption">
                <span class="text-grey mr-2">Качество:</span>
                <v-progress-linear
                  :model-value="version.validation_score * 100"
                  :color="getScoreColor(version.validation_score)"
                  height="6"
                  rounded
                  class="flex-grow-1"
                />
                <span class="ml-2">{{ Math.round(version.validation_score * 100) }}%</span>
              </div>
            </div>

            <div v-if="version.completeness_score !== null" class="mt-1">
              <div class="d-flex align-center text-caption">
                <span class="text-grey mr-2">Полнота:</span>
                <v-progress-linear
                  :model-value="version.completeness_score * 100"
                  :color="getScoreColor(version.completeness_score)"
                  height="6"
                  rounded
                  class="flex-grow-1"
                />
                <span class="ml-2">{{ Math.round(version.completeness_score * 100) }}%</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-timeline-item>
    </v-timeline>
  </v-card>
</template>

<script setup lang="ts">
import type { ProfileVersion } from '@/types/version'

interface Props {
  versions: ProfileVersion[]
  loading?: boolean
  error?: string | null
}

interface Emits {
  (e: 'set-active', versionNumber: number): void
  (e: 'download', versionNumber: number, format: 'json' | 'md' | 'docx'): void
  (e: 'delete', versionNumber: number): void
  (e: 'retry'): void
}

withDefaults(defineProps<Props>(), {
  loading: false,
  error: null
})

const emit = defineEmits<Emits>()

function getVersionIcon(versionType: string): string {
  switch (versionType) {
    case 'generated':
      return 'mdi-magic-staff'
    case 'regenerated':
      return 'mdi-refresh'
    case 'edited':
      return 'mdi-pencil'
    default:
      return 'mdi-file-document'
  }
}

function getVersionTypeLabel(versionType: string): string {
  switch (versionType) {
    case 'generated':
      return 'Сгенерирована'
    case 'regenerated':
      return 'Регенерирована'
    case 'edited':
      return 'Отредактирована'
    default:
      return 'Неизвестный тип'
  }
}

function getScoreColor(score: number): string {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'error'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>

<style scoped>
.v-timeline {
  padding-top: 0;
}
</style>

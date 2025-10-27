<template>
  <BaseThemedDialog
    v-model="dialogModel"
    title="Проверка качества профилей"
    max-width="800px"
    persistent
  >
    <template #default>
      <v-card-text>
        <!-- Summary Stats -->
        <v-row dense class="mb-4">
          <v-col cols="4">
            <v-card variant="tonal" color="success">
              <v-card-text class="text-center">
                <div class="text-h4">{{ qualityGroups.good.length }}</div>
                <div class="text-caption">Отличное качество (≥80%)</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="4">
            <v-card variant="tonal" color="warning">
              <v-card-text class="text-center">
                <div class="text-h4">{{ qualityGroups.ok.length }}</div>
                <div class="text-caption">Приемлемое (60-79%)</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="4">
            <v-card variant="tonal" color="error">
              <v-card-text class="text-center">
                <div class="text-h4">{{ qualityGroups.poor.length }}</div>
                <div class="text-caption">Низкое качество (&lt;60%)</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Recommendation Alert -->
        <v-alert
          v-if="qualityGroups.poor.length > 0"
          type="warning"
          variant="tonal"
          class="mb-4"
        >
          <template #title>
            Рекомендуется регенерация
          </template>
          Найдено {{ qualityGroups.poor.length }} {{ pluralize(qualityGroups.poor.length, 'профиль', 'профиля', 'профилей') }}
          с низким качеством (&lt;60%). Рекомендуется регенерировать эти профили для улучшения качества.
        </v-alert>

        <!-- Tabs for Quality Groups -->
        <v-tabs v-model="activeTab" bg-color="transparent">
          <v-tab value="poor" :disabled="qualityGroups.poor.length === 0">
            <v-icon class="mr-2">mdi-alert-circle</v-icon>
            Низкое ({{ qualityGroups.poor.length }})
          </v-tab>
          <v-tab value="ok" :disabled="qualityGroups.ok.length === 0">
            <v-icon class="mr-2">mdi-check-circle</v-icon>
            Приемлемое ({{ qualityGroups.ok.length }})
          </v-tab>
          <v-tab value="good" :disabled="qualityGroups.good.length === 0">
            <v-icon class="mr-2">mdi-star-circle</v-icon>
            Отличное ({{ qualityGroups.good.length }})
          </v-tab>
        </v-tabs>

        <v-divider class="my-4" />

        <!-- Tab Content -->
        <v-window v-model="activeTab">
          <!-- Poor Quality Profiles -->
          <v-window-item value="poor">
            <v-list density="compact">
              <v-list-item
                v-for="profile in qualityGroups.poor"
                :key="profile.profile_id"
                class="mb-2"
              >
                <template #prepend>
                  <v-icon color="error">mdi-alert</v-icon>
                </template>

                <v-list-item-title>{{ profile.position_name }}</v-list-item-title>
                <v-list-item-subtitle>{{ profile.department_name }}</v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" color="error">
                    {{ Math.round((profile.quality_score || 0) * 100) }}%
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-window-item>

          <!-- OK Quality Profiles -->
          <v-window-item value="ok">
            <v-list density="compact">
              <v-list-item
                v-for="profile in qualityGroups.ok"
                :key="profile.profile_id"
                class="mb-2"
              >
                <template #prepend>
                  <v-icon color="warning">mdi-check</v-icon>
                </template>

                <v-list-item-title>{{ profile.position_name }}</v-list-item-title>
                <v-list-item-subtitle>{{ profile.department_name }}</v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" color="warning">
                    {{ Math.round((profile.quality_score || 0) * 100) }}%
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-window-item>

          <!-- Good Quality Profiles -->
          <v-window-item value="good">
            <v-list density="compact">
              <v-list-item
                v-for="profile in qualityGroups.good"
                :key="profile.profile_id"
                class="mb-2"
              >
                <template #prepend>
                  <v-icon color="success">mdi-star</v-icon>
                </template>

                <v-list-item-title>{{ profile.position_name }}</v-list-item-title>
                <v-list-item-subtitle>{{ profile.department_name }}</v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" color="success">
                    {{ Math.round((profile.quality_score || 0) * 100) }}%
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-window-item>
        </v-window>
      </v-card-text>
    </template>

    <template #actions>
      <v-spacer />
      <v-btn
        v-if="qualityGroups.poor.length > 0"
        color="warning"
        variant="elevated"
        prepend-icon="mdi-refresh"
        @click="handleRegeneratePoor"
      >
        Регенерировать низкокачественные ({{ qualityGroups.poor.length }})
      </v-btn>
      <v-btn
        variant="text"
        @click="handleClose"
      >
        Закрыть
      </v-btn>
    </template>
  </BaseThemedDialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import BaseThemedDialog from '@/components/common/BaseThemedDialog.vue'
import type { UnifiedPosition } from '@/types/unified'

/**
 * Props
 */
interface Props {
  /**
   * Dialog visibility state
   */
  modelValue: boolean

  /**
   * Positions with profile quality data
   */
  positions: UnifiedPosition[]
}

const props = defineProps<Props>()

/**
 * Emits
 */
interface Emits {
  /**
   * Update visibility state
   */
  (e: 'update:modelValue', value: boolean): void

  /**
   * Regenerate profiles with poor quality
   */
  (e: 'regenerate', positionIds: string[]): void
}

const emit = defineEmits<Emits>()

/**
 * Two-way binding for dialog visibility
 */
const dialogModel = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

/**
 * Active tab
 */
const activeTab = ref<'poor' | 'ok' | 'good'>('poor')

/**
 * Group positions by quality score
 *
 * - Good: validation_score >= 0.8 (80%)
 * - OK: validation_score >= 0.6 and < 0.8 (60-79%)
 * - Poor: validation_score < 0.6 (<60%)
 */
const qualityGroups = computed(() => {
  const good: UnifiedPosition[] = []
  const ok: UnifiedPosition[] = []
  const poor: UnifiedPosition[] = []

  for (const position of props.positions) {
    const score = position.quality_score || 0

    if (score >= 0.8) {
      good.push(position)
    } else if (score >= 0.6) {
      ok.push(position)
    } else {
      poor.push(position)
    }
  }

  return { good, ok, poor }
})

/**
 * Pluralize Russian words based on count
 */
function pluralize(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100

  if (mod10 === 1 && mod100 !== 11) {
    return one
  }

  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return few
  }

  return many
}

/**
 * Handle regenerate button click
 */
function handleRegeneratePoor(): void {
  const positionIds = qualityGroups.value.poor
    .map(p => p.position_id)
    .filter((id): id is string => id !== null && id !== undefined)

  emit('regenerate', positionIds)
  handleClose()
}

/**
 * Close dialog
 */
function handleClose(): void {
  emit('update:modelValue', false)
}
</script>

<style scoped>
/* Custom styles if needed */
</style>

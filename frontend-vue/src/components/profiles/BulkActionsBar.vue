<template>
  <!-- Floating action bar at bottom -->
  <v-slide-y-reverse-transition>
    <v-sheet
      v-if="selectedCount > 0"
      class="bulk-actions-bar elevation-8"
      color="primary"
      rounded
    >
      <v-container fluid>
        <v-row align="center" dense>
          <!-- Selection Info -->
          <v-col cols="12" sm="auto">
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-checkbox-multiple-marked</v-icon>
              <div>
                <div class="text-body-1 font-weight-bold">
                  {{ selectedCount }} {{ selectedCount === 1 ? 'позиция выбрана' : 'позиций выбрано' }}
                </div>
                <div class="text-caption">
                  <span v-if="stats.canGenerate > 0">
                    {{ stats.canGenerate }} можно сгенерировать
                  </span>
                  <span v-if="stats.canGenerate > 0 && stats.generating > 0"> • </span>
                  <span v-if="stats.generating > 0">
                    {{ stats.generating }} генерируется
                  </span>
                  <span v-if="(stats.canGenerate > 0 || stats.generating > 0) && stats.generated > 0"> • </span>
                  <span v-if="stats.generated > 0">
                    {{ stats.generated }} сгенерировано
                  </span>
                </div>
              </div>
            </div>
          </v-col>

          <v-spacer class="d-none d-sm-block" />

          <!-- Actions -->
          <v-col cols="12" sm="auto">
            <div class="d-flex align-center gap-2">
              <!-- Generate All -->
              <v-btn
                v-if="stats.canGenerate > 0"
                variant="elevated"
                color="white"
                prepend-icon="mdi-magic-staff"
                @click="emit('bulkGenerate')"
              >
                Сгенерировать все ({{ stats.canGenerate }})
              </v-btn>

              <!-- Cancel All -->
              <v-btn
                v-if="stats.generating > 0"
                variant="elevated"
                color="warning"
                prepend-icon="mdi-stop-circle"
                @click="emit('bulkCancel')"
              >
                Отменить все ({{ stats.generating }})
              </v-btn>

              <!-- Quality Check (Week 6 Phase 4) -->
              <v-btn
                v-if="stats.generated > 0"
                variant="elevated"
                color="white"
                prepend-icon="mdi-clipboard-check"
                @click="emit('qualityCheck')"
              >
                Проверить качество
              </v-btn>

              <!-- Download ZIP (Week 6 Phase 4) -->
              <v-menu v-if="stats.generated > 0">
                <template #activator="{ props: menuProps }">
                  <v-btn
                    variant="elevated"
                    color="white"
                    prepend-icon="mdi-download"
                    v-bind="menuProps"
                  >
                    Скачать ZIP ({{ stats.generated }})
                  </v-btn>
                </template>
                <v-list density="compact">
                  <v-list-subheader>Выберите форматы</v-list-subheader>
                  <v-list-item
                    prepend-icon="mdi-file-document-multiple"
                    @click="emit('bulkDownload', ['json', 'md', 'docx'])"
                  >
                    <v-list-item-title>Все форматы (JSON + MD + DOCX)</v-list-item-title>
                  </v-list-item>
                  <v-divider />
                  <v-list-item
                    prepend-icon="mdi-code-json"
                    @click="emit('bulkDownload', ['json'])"
                  >
                    <v-list-item-title>Только JSON</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    prepend-icon="mdi-file-document"
                    @click="emit('bulkDownload', ['md'])"
                  >
                    <v-list-item-title>Только Markdown</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    prepend-icon="mdi-file-word"
                    @click="emit('bulkDownload', ['docx'])"
                  >
                    <v-list-item-title>Только DOCX</v-list-item-title>
                  </v-list-item>
                  <v-divider />
                  <v-list-item
                    prepend-icon="mdi-file-document-outline"
                    @click="emit('bulkDownload', ['json', 'docx'])"
                  >
                    <v-list-item-title>JSON + DOCX</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>

              <!-- Clear Selection -->
              <v-btn
                variant="text"
                icon
                @click="emit('clearSelection')"
              >
                <v-icon>mdi-close</v-icon>
                <v-tooltip activator="parent" location="top">
                  Очистить выбор
                </v-tooltip>
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>
  </v-slide-y-reverse-transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UnifiedPosition } from '@/types/unified'

// Props
interface Props {
  selectedPositions: UnifiedPosition[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  bulkGenerate: []
  bulkCancel: []
  bulkDownload: [formats: Array<'json' | 'md' | 'docx'>]
  qualityCheck: []
  clearSelection: []
}>()

// Computed
const selectedCount = computed(() => props.selectedPositions.length)

const stats = computed(() => {
  const canGenerate = props.selectedPositions.filter(p => p.status === 'not_generated').length
  const generating = props.selectedPositions.filter(p => p.status === 'generating').length
  const generated = props.selectedPositions.filter(p => p.status === 'generated').length

  return { canGenerate, generating, generated }
})
</script>

<style scoped>
.bulk-actions-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  max-width: 1200px;
  width: calc(100% - 48px);
  padding: 16px 24px;
  color: white;
}

.gap-2 {
  gap: 8px;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .bulk-actions-bar {
    bottom: 16px;
    width: calc(100% - 32px);
    padding: 12px 16px;
  }

  .bulk-actions-bar .v-btn {
    min-width: auto !important;
  }

  .bulk-actions-bar .v-btn:not(.v-btn--icon) {
    font-size: 0.75rem;
    padding: 0 12px;
  }
}
</style>

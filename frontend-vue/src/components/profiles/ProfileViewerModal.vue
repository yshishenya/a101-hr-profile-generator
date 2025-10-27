<template>
  <v-dialog
    :model-value="modelValue"
    :theme="theme.global.name.value"
    max-width="1400px"
    scrollable
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card v-if="profile">
      <!-- Header -->
      <v-sheet bg-color="surface-variant" class="pa-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center gap-4">
            <v-icon size="32" color="primary">mdi-file-document-outline</v-icon>
            <div>
              <h2 class="text-h5">{{ profile.position_name }}</h2>
              <div class="text-caption text-medium-emphasis">
                {{ profile.department_name }}
              </div>
            </div>
          </div>

          <div class="d-flex align-center gap-3">
          <!-- Download Menu -->
          <v-menu>
            <template #activator="{ props: menuProps }">
              <v-btn
                icon="mdi-download"
                variant="text"
                v-bind="menuProps"
              >
                <v-icon>mdi-download</v-icon>
                <v-tooltip activator="parent" location="bottom">Скачать</v-tooltip>
              </v-btn>
            </template>

            <v-list density="compact">
              <!-- For Work -->
              <v-list-subheader>Для работы</v-list-subheader>
              <v-list-item
                prepend-icon="mdi-file-word"
                @click="handleDownload('docx')"
              >
                <v-list-item-title>Microsoft Word</v-list-item-title>
                <v-list-item-subtitle>Готовый документ для печати</v-list-item-subtitle>
              </v-list-item>
              <v-list-item
                prepend-icon="mdi-language-markdown"
                @click="handleDownload('md')"
              >
                <v-list-item-title>Markdown</v-list-item-title>
                <v-list-item-subtitle>Текстовый формат для редактирования</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-2" />

              <!-- For Developers -->
              <v-list-subheader>Для разработчиков</v-list-subheader>
              <v-list-item
                prepend-icon="mdi-code-json"
                @click="handleDownload('json')"
              >
                <v-list-item-title>JSON (технический)</v-list-item-title>
                <v-list-item-subtitle>Данные в структурированном формате</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>

          <!-- Version History (Day 6) -->
          <v-btn
            v-if="profile.version_count && profile.version_count > 1"
            icon="mdi-history"
            variant="text"
            @click="emit('viewVersions')"
          >
            <v-badge
              :content="profile.version_count"
              color="info"
              offset-x="8"
              offset-y="8"
            >
              <v-icon>mdi-history</v-icon>
            </v-badge>
            <v-tooltip activator="parent" location="bottom">
              История версий ({{ profile.version_count }})
            </v-tooltip>
          </v-btn>

          <!-- Edit (Week 7) -->
          <v-btn
            icon="mdi-pencil"
            variant="text"
            disabled
          >
            <v-icon>mdi-pencil</v-icon>
            <v-tooltip activator="parent" location="bottom">
              Редактировать (Week 7)
            </v-tooltip>
          </v-btn>

          <!-- Close -->
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="emit('update:modelValue', false)"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
          </div>
        </div>
      </v-sheet>

      <v-divider />

      <!-- Content with Sidebar -->
      <v-card-text class="pa-0" style="height: calc(100vh - 200px)">
        <v-row no-gutters style="height: 100%">
          <!-- Main Content Area -->
          <v-col cols="12" md="9" class="overflow-y-auto pa-6">
            <ProfileContent
              v-if="profileDetail"
              :profile="profileDetail.profile"
              :loading="loadingDetail"
              @download-json="handleDownload('json')"
            />

            <!-- Loading State -->
            <div v-else-if="loadingDetail" class="text-center pa-8">
              <v-progress-circular indeterminate color="primary" size="64" />
              <div class="text-h6 mt-4">Загрузка профиля...</div>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="text-center pa-8">
              <v-icon size="64" color="error">mdi-alert-circle</v-icon>
              <div class="text-h6 mt-4">Ошибка загрузки</div>
              <div class="text-body-2 text-medium-emphasis mt-2">{{ error }}</div>
              <v-btn color="primary" class="mt-4" @click="loadProfileDetail">
                Попробовать снова
              </v-btn>
            </div>
          </v-col>

          <!-- Metadata Sidebar -->
          <v-col
            cols="12"
            md="3"
            bg-color="surface-variant"
            class="overflow-y-auto pa-4"
          >
            <ProfileMetadata
              v-if="profileDetail"
              :profile="profile"
              :metadata="profileDetail.metadata"
            />

            <!-- Loading Skeleton -->
            <div v-else-if="loadingDetail">
              <v-skeleton-loader type="list-item-three-line" />
              <v-skeleton-loader type="list-item-three-line" class="mt-4" />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useTheme } from 'vuetify'
import { useProfilesStore } from '@/stores/profiles'
import { logger } from '@/utils/logger'
import ProfileContent from './ProfileContent.vue'
import ProfileMetadata from './ProfileMetadata.vue'
import type { UnifiedPosition } from '@/types/unified'

// Props
interface Props {
  modelValue: boolean
  profile: UnifiedPosition | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'download': [format: 'json' | 'md' | 'docx']
  'viewVersions': []
}>()

// Theme
const theme = useTheme()

// Store
const profilesStore = useProfilesStore()

// Computed - use store's currentProfile
const profileDetail = computed(() => profilesStore.currentProfile)
const loadingDetail = computed(() => profilesStore.loading)
const error = computed(() => profilesStore.error)

// Watch for profile changes
watch(
  () => props.profile?.profile_id,
  async (newProfileId) => {
    if (newProfileId && props.modelValue) {
      await loadProfileDetail()
    }
  },
  { immediate: true }
)

// Watch for dialog open/close
watch(
  () => props.modelValue,
  async (isOpen) => {
    if (isOpen && props.profile?.profile_id && !profileDetail.value) {
      await loadProfileDetail()
    }
  }
)

// Methods
async function loadProfileDetail(): Promise<void> {
  if (!props.profile?.profile_id) return

  try {
    await profilesStore.loadProfile(String(props.profile.profile_id))
  } catch (err) {
    logger.error('Failed to load profile detail', err)
    // Error is already set in store
  }
}

function handleDownload(format: 'json' | 'md' | 'docx'): void {
  emit('download', format)
}
</script>

<style scoped>
/* Ensure proper scrolling */
.overflow-y-auto {
  overflow-y: auto;
  overflow-x: hidden;
}

/* Mobile adjustments */
@media (max-width: 960px) {
  .v-card-text {
    height: calc(100vh - 150px) !important;
  }
}
</style>

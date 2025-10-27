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

      <!-- Tabs Navigation -->
      <v-tabs v-model="activeTab" bg-color="surface">
        <v-tab value="content">Контент</v-tab>
        <v-tab value="metadata">Метаданные</v-tab>
        <v-tab value="versions">
          Версии
          <v-badge
            v-if="profile.version_count && profile.version_count > 1"
            :content="profile.version_count"
            inline
            color="primary"
            class="ml-2"
          />
        </v-tab>
      </v-tabs>

      <v-divider />

      <!-- Tabs Content -->
      <v-card-text class="pa-0" style="height: calc(100vh - 260px)">
        <v-window v-model="activeTab">
          <!-- Content Tab -->
          <v-window-item value="content" class="overflow-y-auto pa-6" style="height: 100%">
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
          </v-window-item>

          <!-- Metadata Tab -->
          <v-window-item value="metadata" class="overflow-y-auto pa-6" style="height: 100%">
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
          </v-window-item>

          <!-- Versions Tab -->
          <v-window-item value="versions" class="overflow-y-auto" style="height: 100%">
            <ProfileVersionsPanel
              :versions="versions"
              :loading="versionsLoading"
              :error="versionsError"
              @set-active="handleSetActive"
              @download="handleVersionDownload"
              @delete="handleDeleteVersion"
              @retry="loadVersions"
            />
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>

    <!-- Notification Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTheme } from 'vuetify'
import { useProfilesStore } from '@/stores/profiles'
import { useProfileVersions } from '@/composables/useProfileVersions'
import { logger } from '@/utils/logger'
import ProfileContent from './ProfileContent.vue'
import ProfileMetadata from './ProfileMetadata.vue'
import ProfileVersionsPanel from './ProfileVersionsPanel.vue'
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

// State
const activeTab = ref<string>('content')

// Computed - use store's currentProfile
const profileDetail = computed(() => profilesStore.currentProfile)
const loadingDetail = computed(() => profilesStore.loading)
const error = computed(() => profilesStore.error)
const profileId = computed(() => props.profile?.profile_id ? String(props.profile.profile_id) : undefined)

// Methods
async function loadProfileDetail(): Promise<void> {
  if (!props.profile?.profile_id) return

  try {
    await profilesStore.loadProfile(String(props.profile.profile_id))
  } catch (err: unknown) {
    logger.error('Failed to load profile detail', err)
    // Error is already set in store
  }
}

function handleDownload(format: 'json' | 'md' | 'docx'): void {
  emit('download', format)
}

// Versions Management Composable
const {
  versions,
  versionsLoading,
  versionsError,
  snackbar,
  loadVersions,
  handleSetActive,
  handleVersionDownload,
  handleDeleteVersion
} = useProfileVersions(profileId, activeTab, loadProfileDetail)

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

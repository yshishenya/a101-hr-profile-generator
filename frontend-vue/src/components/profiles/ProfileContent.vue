<template>
  <div class="profile-content">
    <!-- Loading State -->
    <div v-if="loading" class="text-center pa-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <!-- Profile Content -->
    <div v-else-if="profile" class="content-sections">
      <!-- Render each section of the profile -->
      <div
        v-for="(section, index) in profileSections"
        :key="index"
        class="section mb-6"
      >
        <v-card variant="outlined">
          <v-card-title class="bg-surface-variant">
            <v-icon class="mr-2" :icon="section.icon" />
            {{ section.title }}
          </v-card-title>

          <v-card-text class="pa-4">
            <!-- List items -->
            <div v-if="section.type === 'list' && section.items">
              <v-chip
                v-for="(item, idx) in section.items"
                :key="idx"
                class="ma-1"
                variant="outlined"
              >
                {{ item }}
              </v-chip>
            </div>

            <!-- Text content -->
            <div v-else-if="section.type === 'text' && section.content" class="text-body-1">
              <div v-html="formatText(section.content)" />
            </div>

            <!-- Table data -->
            <v-table v-else-if="section.type === 'table' && section.rows" density="comfortable">
              <tbody>
                <tr v-for="(row, idx) in section.rows" :key="idx">
                  <td class="font-weight-bold" style="width: 30%">{{ row.label }}</td>
                  <td>{{ row.value }}</td>
                </tr>
              </tbody>
            </v-table>

            <!-- Nested sections -->
            <div v-else-if="section.type === 'nested' && section.subsections">
              <v-expansion-panels>
                <v-expansion-panel
                  v-for="(subsection, subIdx) in section.subsections"
                  :key="subIdx"
                >
                  <v-expansion-panel-title>
                    {{ subsection.title }}
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <div v-if="subsection.content" class="text-body-2" v-html="formatText(subsection.content)" />
                    <v-chip
                      v-else-if="subsection.items"
                      v-for="(item, itemIdx) in subsection.items"
                      :key="itemIdx"
                      class="ma-1"
                      size="small"
                      variant="outlined"
                    >
                      {{ item }}
                    </v-chip>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>

            <!-- JSON fallback -->
            <pre v-else class="json-content">{{ JSON.stringify(section, null, 2) }}</pre>
          </v-card-text>
        </v-card>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center pa-8">
      <v-icon size="64" color="grey-lighten-2">mdi-file-document-outline</v-icon>
      <div class="text-h6 mt-4">Нет данных для отображения</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Props {
  profile: any
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Profile section structure
interface ProfileSection {
  title: string
  icon: string
  type: 'list' | 'text' | 'table' | 'nested'
  items?: string[]
  content?: string
  rows?: Array<{ label: string; value: string }>
  subsections?: Array<{ title: string; content?: string; items?: string[] }>
}

// Computed
const profileSections = computed<ProfileSection[]>(() => {
  if (!props.profile) return []

  const sections: ProfileSection[] = []

  // Parse profile structure
  // Common profile fields from backend
  if (props.profile.competencies) {
    sections.push({
      title: 'Компетенции',
      icon: 'mdi-brain',
      type: 'nested',
      subsections: Object.entries(props.profile.competencies || {}).map(([key, value]: [string, any]) => ({
        title: key,
        items: Array.isArray(value) ? value : [String(value)]
      }))
    })
  }

  if (props.profile.responsibilities) {
    sections.push({
      title: 'Обязанности',
      icon: 'mdi-clipboard-list',
      type: 'list',
      items: Array.isArray(props.profile.responsibilities)
        ? props.profile.responsibilities
        : [String(props.profile.responsibilities)]
    })
  }

  if (props.profile.requirements) {
    sections.push({
      title: 'Требования',
      icon: 'mdi-check-circle',
      type: 'nested',
      subsections: Object.entries(props.profile.requirements || {}).map(([key, value]: [string, any]) => ({
        title: key,
        items: Array.isArray(value) ? value : [String(value)]
      }))
    })
  }

  if (props.profile.skills) {
    sections.push({
      title: 'Навыки',
      icon: 'mdi-toolbox',
      type: 'list',
      items: Array.isArray(props.profile.skills) ? props.profile.skills : [String(props.profile.skills)]
    })
  }

  if (props.profile.education) {
    sections.push({
      title: 'Образование',
      icon: 'mdi-school',
      type: 'text',
      content: typeof props.profile.education === 'string'
        ? props.profile.education
        : JSON.stringify(props.profile.education, null, 2)
    })
  }

  if (props.profile.experience) {
    sections.push({
      title: 'Опыт работы',
      icon: 'mdi-briefcase',
      type: 'text',
      content: typeof props.profile.experience === 'string'
        ? props.profile.experience
        : JSON.stringify(props.profile.experience, null, 2)
    })
  }

  // If no structured data, show raw JSON
  if (sections.length === 0) {
    sections.push({
      title: 'Содержимое профиля',
      icon: 'mdi-file-document',
      type: 'text',
      content: JSON.stringify(props.profile, null, 2)
    })
  }

  return sections
})

// Methods
function formatText(text: string): string {
  // Convert line breaks to <br>
  return text.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.profile-content {
  min-height: 400px;
}

.content-sections {
  max-width: 1000px;
}

.section {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.json-content {
  background: rgb(var(--v-theme-surface-variant));
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
}

/* Improve text readability */
.text-body-1 {
  line-height: 1.75;
}

.v-chip {
  font-size: 0.875rem;
}
</style>

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
        <v-card>
          <v-sheet bg-color="surface-variant" class="pa-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2" :icon="section.icon" />
              <span class="text-h6">{{ section.title }}</span>
            </div>
          </v-sheet>

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
              <v-expansion-panels variant="accordion">
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
                      v-for="(item, itemIdx) in subsection.items"
                      v-else-if="subsection.items"
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
import DOMPurify from 'dompurify'
import type { ProfileData } from '@/types/profile'

// Props
interface Props {
  profile: ProfileData
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

/**
 * Section builders - extract complex logic into testable functions
 */

function buildCompetenciesSection(competencies: unknown): ProfileSection | null {
  if (!competencies) return null

  return {
    title: 'Компетенции',
    icon: 'mdi-brain',
    type: 'nested',
    subsections: Object.entries(competencies as Record<string, unknown>).map(([key, value]) => ({
      title: key,
      items: Array.isArray(value) ? value : [String(value)]
    }))
  }
}

function buildResponsibilitiesSection(responsibilities: unknown): ProfileSection | null {
  if (!responsibilities) return null

  const items = Array.isArray(responsibilities)
    ? responsibilities.map(r =>
        typeof r === 'string' ? r : `${r.title}: ${r.description}`
      )
    : [String(responsibilities)]

  return {
    title: 'Обязанности',
    icon: 'mdi-clipboard-list',
    type: 'list',
    items
  }
}

function buildRequirementsSection(requirements: unknown): ProfileSection | null {
  if (!requirements) return null

  return {
    title: 'Требования',
    icon: 'mdi-check-circle',
    type: 'nested',
    subsections: Object.entries(requirements as Record<string, unknown>).map(([key, value]) => ({
      title: key,
      items: Array.isArray(value) ? value : [String(value)]
    }))
  }
}

function buildSkillsSection(skills: unknown): ProfileSection | null {
  if (!skills) return null

  return {
    title: 'Навыки',
    icon: 'mdi-toolbox',
    type: 'list',
    items: Array.isArray(skills) ? skills : [String(skills)]
  }
}

function buildEducationSection(education: unknown): ProfileSection | null {
  if (!education) return null

  return {
    title: 'Образование',
    icon: 'mdi-school',
    type: 'text',
    content: typeof education === 'string'
      ? education
      : JSON.stringify(education, null, 2)
  }
}

function buildExperienceSection(experience: unknown): ProfileSection | null {
  if (!experience) return null

  return {
    title: 'Опыт работы',
    icon: 'mdi-briefcase',
    type: 'text',
    content: typeof experience === 'string'
      ? experience
      : JSON.stringify(experience, null, 2)
  }
}

function buildFallbackSection(profile: ProfileData): ProfileSection {
  return {
    title: 'Содержимое профиля',
    icon: 'mdi-file-document',
    type: 'text',
    content: JSON.stringify(profile, null, 2)
  }
}

// Computed
const profileSections = computed<ProfileSection[]>(() => {
  if (!props.profile) return []

  const sections = [
    buildCompetenciesSection(props.profile.competencies),
    buildResponsibilitiesSection(props.profile.responsibilities),
    buildRequirementsSection(props.profile.requirements),
    buildSkillsSection(props.profile.skills),
    buildEducationSection(props.profile.education),
    buildExperienceSection(props.profile.experience)
  ].filter((section): section is ProfileSection => section !== null)

  // If no structured data, show raw JSON fallback
  if (sections.length === 0) {
    sections.push(buildFallbackSection(props.profile))
  }

  return sections
})

// Methods
function formatText(text: string): string {
  // Convert line breaks to <br> and sanitize HTML to prevent XSS attacks
  const formatted = text.replace(/\n/g, '<br>')

  // Sanitize HTML with DOMPurify - allows only safe tags
  return DOMPurify.sanitize(formatted, {
    ALLOWED_TAGS: ['br', 'p', 'strong', 'em', 'u', 'b', 'i', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: [],
    ALLOW_DATA_ATTR: false
  })
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

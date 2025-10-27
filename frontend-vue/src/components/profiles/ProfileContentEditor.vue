<template>
  <div class="profile-content-editor">
    <!-- Section Cards -->
    <div
      v-for="section in sections"
      :key="section.id"
      class="section-wrapper mb-4"
    >
      <SectionCard
        :section-id="section.id"
        :title="section.title"
        :icon="section.icon"
        :is-editing="editingSections[section.id]"
        :is-valid="validationStatus[section.id]?.isValid ?? true"
        :validation-error="validationStatus[section.id]?.error"
        :has-changes="hasChanges[section.id]"
        @edit="handleEditSection(section.id)"
        @save="handleSaveSection(section.id)"
        @cancel="handleCancelSection(section.id)"
      >
        <template #content>
          <!-- Render appropriate editor based on section type -->
          <component
            :is="getSectionComponent(section.id)"
            v-model="sectionData[section.id]"
            :readonly="!editingSections[section.id]"
            @update:model-value="handleSectionChange(section.id)"
          />
        </template>
      </SectionCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useProfilesStore } from '@/stores/profiles'
import SectionCard from './SectionCard.vue'
import BasicInfoEditor from './editors/BasicInfoEditor.vue'
import ResponsibilityAreasEditor from './editors/ResponsibilityAreasEditor.vue'
import ProfessionalSkillsEditor from './editors/ProfessionalSkillsEditor.vue'
import CompetenciesEditor from './editors/CompetenciesEditor.vue'
import ExperienceEducationEditor from './editors/ExperienceEducationEditor.vue'
import CareerogramEditor from './editors/CareerogramEditor.vue'
import WorkplaceProvisioningEditor from './editors/WorkplaceProvisioningEditor.vue'
import PerformanceMetricsEditor from './editors/PerformanceMetricsEditor.vue'
import AdditionalInfoEditor from './editors/AdditionalInfoEditor.vue'
import type { ProfileData } from '@/types/profile'

// Props
interface Props {
  profileId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'section-edited': [sectionId: string]
  'section-saved': [sectionId: string]
}>()

// Store
const profilesStore = useProfilesStore()
const { currentProfile } = storeToRefs(profilesStore)

// Local state
const editingSections = ref<Record<string, boolean>>({})
const sectionData = ref<Record<string, unknown>>({})
const hasChanges = ref<Record<string, boolean>>({})
const validationStatus = ref<Record<string, { isValid: boolean; error?: string }>>({})

// Section definitions
const sections = ref([
  {
    id: 'basic_info',
    title: 'Основная информация',
    icon: 'mdi-information',
    component: 'BasicInfoEditor',
  },
  {
    id: 'responsibility_areas',
    title: 'Зоны ответственности',
    icon: 'mdi-clipboard-list',
    component: 'ResponsibilityAreasEditor',
  },
  {
    id: 'professional_skills',
    title: 'Профессиональные навыки',
    icon: 'mdi-toolbox',
    component: 'ProfessionalSkillsEditor',
  },
  {
    id: 'corporate_competencies',
    title: 'Корпоративные компетенции',
    icon: 'mdi-brain',
    component: 'CompetenciesEditor',
  },
  {
    id: 'personal_qualities',
    title: 'Личные качества',
    icon: 'mdi-account-heart',
    component: 'CompetenciesEditor', // Reuse same editor
  },
  {
    id: 'experience_and_education',
    title: 'Опыт и образование',
    icon: 'mdi-school',
    component: 'ExperienceEducationEditor',
  },
  {
    id: 'careerogram',
    title: 'Карьерограмма',
    icon: 'mdi-chart-timeline-variant',
    component: 'CareerogramEditor',
  },
  {
    id: 'workplace_provisioning',
    title: 'Обеспечение рабочего места',
    icon: 'mdi-laptop',
    component: 'WorkplaceProvisioningEditor',
  },
  {
    id: 'performance_metrics',
    title: 'Показатели эффективности',
    icon: 'mdi-chart-line',
    component: 'PerformanceMetricsEditor',
  },
  {
    id: 'additional_information',
    title: 'Дополнительная информация',
    icon: 'mdi-information-outline',
    component: 'AdditionalInfoEditor',
  },
])

// Computed
const totalSections = computed(() => sections.value.length)
const editedSectionsCount = computed(
  () => Object.values(hasChanges.value).filter(Boolean).length
)

// Component map
const componentMap: Record<string, ReturnType<typeof import('vue').defineComponent>> = {
  BasicInfoEditor,
  ResponsibilityAreasEditor,
  ProfessionalSkillsEditor,
  CompetenciesEditor,
  ExperienceEducationEditor,
  CareerogramEditor,
  WorkplaceProvisioningEditor,
  PerformanceMetricsEditor,
  AdditionalInfoEditor,
}

// Methods
function getSectionComponent(
  sectionId: string
): ReturnType<typeof import('vue').defineComponent> | string {
  const section = sections.value.find((s) => s.id === sectionId)
  if (!section) return 'div'

  return componentMap[section.component] || 'div'
}

function handleEditSection(sectionId: string): void {
  editingSections.value[sectionId] = true
  emit('section-edited', sectionId)
}

function handleSaveSection(sectionId: string): void {
  // Validate section data
  const isValid = validateSection(sectionId, sectionData.value[sectionId])

  if (!isValid) {
    return
  }

  // Save to store
  profilesStore.updateSectionData(sectionId, sectionData.value[sectionId])

  // Exit edit mode
  editingSections.value[sectionId] = false
  hasChanges.value[sectionId] = false

  emit('section-saved', sectionId)
}

function handleCancelSection(sectionId: string): void {
  // Restore original data
  if (currentProfile.value?.profile) {
    sectionData.value[sectionId] = extractSectionData(
      sectionId,
      currentProfile.value.profile
    )
  }

  // Exit edit mode
  editingSections.value[sectionId] = false
  hasChanges.value[sectionId] = false
}

function handleSectionChange(sectionId: string): void {
  hasChanges.value[sectionId] = true

  // Validate on change
  validateSection(sectionId, sectionData.value[sectionId])
}

function validateSection(sectionId: string, data: unknown): boolean {
  // Basic validation - will be replaced with comprehensive validation
  let isValid = true
  let error: string | undefined

  if (!data) {
    isValid = false
    error = 'Секция не может быть пустой'
  }

  // Section-specific validation
  switch (sectionId) {
    case 'basic_info':
      if (
        !data ||
        typeof data !== 'object' ||
        !(data as Record<string, unknown>).direct_manager ||
        !(data as Record<string, unknown>).primary_activity_type
      ) {
        isValid = false
        error = 'Укажите руководителя и вид деятельности'
      }
      break

    case 'responsibility_areas':
      if (!Array.isArray(data) || data.length === 0) {
        isValid = false
        error = 'Добавьте хотя бы одну зону ответственности'
      }
      break

    case 'professional_skills':
      if (!Array.isArray(data) || data.length === 0) {
        isValid = false
        error = 'Добавьте хотя бы один навык'
      }
      break

    case 'corporate_competencies':
    case 'personal_qualities':
      if (!Array.isArray(data) || data.length === 0) {
        isValid = false
        error = 'Добавьте хотя бы одно значение'
      }
      break

    case 'experience_and_education':
      if (
        !data ||
        typeof data !== 'object' ||
        !(data as Record<string, unknown>).education_level
      ) {
        isValid = false
        error = 'Укажите уровень образования'
      }
      break
  }

  validationStatus.value[sectionId] = { isValid, error }
  return isValid
}

function extractSectionData(sectionId: string, profileData: ProfileData): unknown {
  // Extract section data from profile
  // This maps section IDs to actual profile_data fields
  const fieldMap: Record<string, string> = {
    basic_info: 'position_title',
    responsibility_areas: 'responsibility_areas',
    professional_skills: 'professional_skills',
    corporate_competencies: 'corporate_competencies',
    personal_qualities: 'personal_qualities',
    experience_and_education: 'experience_and_education',
    careerogram: 'careerogram',
    workplace_provisioning: 'workplace_provisioning',
    performance_metrics: 'performance_metrics',
    additional_information: 'additional_information',
  }

  const field = fieldMap[sectionId]
  if (!field) return null

  // For basic_info, extract only the fields that BasicInfoEditor handles
  if (sectionId === 'basic_info') {
    return {
      direct_manager: (profileData as Record<string, unknown>).direct_manager as string,
      primary_activity_type: (profileData as Record<string, unknown>)
        .primary_activity_type as string,
    }
  }

  return (profileData as Record<string, unknown>)[field]
}

function initializeSectionData(): void {
  if (!currentProfile.value?.profile) return

  // Initialize all section data from current profile
  sections.value.forEach((section) => {
    sectionData.value[section.id] = extractSectionData(
      section.id,
      currentProfile.value!.profile
    )

    // Initialize edit/change states
    editingSections.value[section.id] = false
    hasChanges.value[section.id] = false

    // Initial validation
    validateSection(section.id, sectionData.value[section.id])
  })
}

// Lifecycle
onMounted(() => {
  initializeSectionData()
})

// Watch for profile changes
watch(
  () => currentProfile.value,
  () => {
    initializeSectionData()
  },
  { deep: true }
)

// Expose for parent component
defineExpose({
  editedSectionsCount,
  totalSections,
  hasUnsavedChanges: computed(() => editedSectionsCount.value > 0),
  validateAllSections: () => {
    let allValid = true
    sections.value.forEach((section) => {
      const isValid = validateSection(section.id, sectionData.value[section.id])
      if (!isValid) allValid = false
    })
    return allValid
  },
  saveAllSections: async () => {
    // Save all sections with changes
    const sectionsToSave = Object.keys(hasChanges.value).filter(
      (key) => hasChanges.value[key]
    )

    for (const sectionId of sectionsToSave) {
      handleSaveSection(sectionId)
    }
  },
})
</script>

<style scoped>
.profile-content-editor {
  max-width: 1000px;
}

.section-wrapper {
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
</style>

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
import { PROFILE_SECTIONS, SECTION_FIELD_MAP } from './constants/profileSections'
import { validateSection } from './utils/sectionValidation'
import { extractSectionData } from './utils/sectionDataExtractor'

// Props
interface Props {
  profileId: string
}

defineProps<Props>()

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
const sections = ref(PROFILE_SECTIONS)

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

async function handleSaveSection(sectionId: string): Promise<void> {
  // Validate section data
  const validation = validateSection(sectionId, sectionData.value[sectionId])
  validationStatus.value[sectionId] = validation

  if (!validation.isValid) {
    return
  }

  // Build full profile_data with updated section
  if (!currentProfile.value?.profile) return

  const updatedProfileData = { ...currentProfile.value.profile }

  // Update the specific section
  if (sectionId === 'basic_info') {
    // For basic_info, merge the fields
    Object.assign(updatedProfileData, sectionData.value[sectionId])
  } else {
    // For other sections, directly set the value
    const field = SECTION_FIELD_MAP[sectionId]
    if (field) {
      ;(updatedProfileData as Record<string, unknown>)[field] = sectionData.value[sectionId]
    }
  }

  try {
    // Save to backend via store
    await profilesStore.updateProfileContent(
      currentProfile.value.profile_id,
      updatedProfileData as Record<string, unknown>
    )

    // Exit edit mode
    editingSections.value[sectionId] = false
    hasChanges.value[sectionId] = false

    emit('section-saved', sectionId)
  } catch (error: unknown) {
    // Handle error - validation status will show the error
    const errorMessage = error instanceof Error ? error.message : 'Failed to save section'
    validationStatus.value[sectionId] = { isValid: false, error: errorMessage }
  }
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
  const validation = validateSection(sectionId, sectionData.value[sectionId])
  validationStatus.value[sectionId] = validation
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
    const validation = validateSection(section.id, sectionData.value[section.id])
    validationStatus.value[section.id] = validation
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
      const validation = validateSection(section.id, sectionData.value[section.id])
      validationStatus.value[section.id] = validation
      if (!validation.isValid) allValid = false
    })
    return allValid
  },
  saveAllSections: async () => {
    // Save all sections with changes
    const sectionsToSave = Object.keys(hasChanges.value).filter(
      (key) => hasChanges.value[key]
    )

    for (const sectionId of sectionsToSave) {
      await handleSaveSection(sectionId)
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

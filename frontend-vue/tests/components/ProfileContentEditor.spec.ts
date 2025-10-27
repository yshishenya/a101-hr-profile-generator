/**
 * Unit tests for ProfileContentEditor component
 * Tests section initialization, edit mode switching, validation, and save functionality
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { setActivePinia, createPinia } from 'pinia'
import ProfileContentEditor from '@/components/profiles/ProfileContentEditor.vue'
import SectionCard from '@/components/profiles/SectionCard.vue'
import { useProfilesStore } from '@/stores/profiles'
import type { UnifiedPosition } from '@/types/unified'
import type { ProfileData } from '@/types/profile'

// Create vuetify instance for tests
const vuetify = createVuetify()

// Stub all editor components to avoid complex data requirements
const stubComponents = {
  BasicInfoEditor: { template: '<div class="stub-basic-info"></div>' },
  ResponsibilityAreasEditor: { template: '<div class="stub-responsibility"></div>' },
  ProfessionalSkillsEditor: { template: '<div class="stub-skills"></div>' },
  CompetenciesEditor: { template: '<div class="stub-competencies"></div>' },
  ExperienceEducationEditor: { template: '<div class="stub-experience"></div>' },
  CareerogramEditor: { template: '<div class="stub-careerogram"></div>' },
  WorkplaceProvisioningEditor: { template: '<div class="stub-workplace"></div>' },
  PerformanceMetricsEditor: { template: '<div class="stub-metrics"></div>' },
  AdditionalInfoEditor: { template: '<div class="stub-additional"></div>' },
}

describe('ProfileContentEditor', () => {
  let wrapper: VueWrapper<InstanceType<typeof ProfileContentEditor>>
  let profilesStore: ReturnType<typeof useProfilesStore>
  let mockProfile: UnifiedPosition & { profile: ProfileData }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    profilesStore = useProfilesStore()

    // Mock profile data with all sections
    mockProfile = {
      position_id: 'P001',
      position_name: 'Software Architect',
      business_unit_id: 'BU001',
      business_unit_name: 'Engineering',
      department_name: 'Backend Development',
      department_path: 'Engineering > Backend Development',
      status: 'generated',
      profile_id: 123,
      employee_name: 'John Doe',
      current_version: 1,
      version_count: 1,
      quality_score: 85,
      completeness_score: 90,
      created_at: '2024-01-15T10:30:00Z',
      created_by: 'admin',
      actions: {
        canView: true,
        canGenerate: false,
        canDownload: true,
        canEdit: true,
        canDelete: true,
        canCancel: false,
        canRegenerate: true,
      },
      profile: {
        direct_manager: 'Jane Smith',
        primary_activity_type: 'Software Development',
        responsibility_areas: ['Architecture Design', 'Code Review'],
        professional_skills: ['Python', 'TypeScript', 'Docker'],
        corporate_competencies: ['Leadership', 'Communication'],
        personal_qualities: ['Analytical', 'Detail-oriented'],
        experience_and_education: {
          education_level: 'Masters',
          years_of_experience: 10,
        },
        careerogram: {
          current_position: 'Software Architect',
          next_positions: ['Principal Architect', 'VP Engineering'],
        },
        workplace_provisioning: {
          equipment: ['Laptop', 'Monitor'],
          software: ['IDE', 'Docker'],
        },
        performance_metrics: {
          kpis: ['Code Quality', 'Team Velocity'],
        },
        additional_information: {
          notes: 'Excellent performance',
        },
      } as ProfileData,
    }

    // Set current profile in store
    profilesStore.currentProfile = mockProfile
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('Section Initialization', () => {
    it('should render all section cards', () => {
      // Arrange & Act
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })

      // Assert
      const sections = wrapper.findAllComponents(SectionCard)
      expect(sections.length).toBe(10) // All 10 sections
    })

    it('should initialize section data from profile', async () => {
      // Arrange & Act
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.sectionData).toBeDefined()
      expect(wrapper.vm.sectionData.responsibility_areas).toEqual([
        'Architecture Design',
        'Code Review',
      ])
      expect(wrapper.vm.sectionData.professional_skills).toEqual([
        'Python',
        'TypeScript',
        'Docker',
      ])
    })

    it('should initialize all sections in non-editing mode', () => {
      // Arrange & Act
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })

      // Assert
      const editingStates = Object.values(wrapper.vm.editingSections)
      expect(editingStates.every(state => state === false)).toBe(true)
    })

    it('should initialize validation status for all sections', async () => {
      // Arrange & Act
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.validationStatus).toBeDefined()
      expect(Object.keys(wrapper.vm.validationStatus).length).toBeGreaterThan(0)
    })

    it('should handle missing profile gracefully', () => {
      // Arrange
      profilesStore.currentProfile = null

      // Act
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })

      // Assert - should not crash
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Edit Mode Switching', () => {
    beforeEach(() => {
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
    })

    it('should enter edit mode when handleEditSection called', () => {
      // Arrange
      const sectionId = 'professional_skills'

      // Act
      wrapper.vm.handleEditSection(sectionId)

      // Assert
      expect(wrapper.vm.editingSections[sectionId]).toBe(true)
    })

    it('should emit section-edited event when entering edit mode', () => {
      // Arrange
      const sectionId = 'corporate_competencies'

      // Act
      wrapper.vm.handleEditSection(sectionId)

      // Assert
      expect(wrapper.emitted('section-edited')).toBeTruthy()
      expect(wrapper.emitted('section-edited')?.[0]).toEqual([sectionId])
    })

    it('should exit edit mode when handleCancelSection called', () => {
      // Arrange
      const sectionId = 'professional_skills'
      wrapper.vm.handleEditSection(sectionId)
      expect(wrapper.vm.editingSections[sectionId]).toBe(true)

      // Act
      wrapper.vm.handleCancelSection(sectionId)

      // Assert
      expect(wrapper.vm.editingSections[sectionId]).toBe(false)
    })

    it('should restore original data when canceling edit', () => {
      // Arrange
      const sectionId = 'professional_skills'
      const originalData = [...wrapper.vm.sectionData[sectionId] as string[]]

      wrapper.vm.handleEditSection(sectionId)
      wrapper.vm.sectionData[sectionId] = ['Modified Skill']

      // Act
      wrapper.vm.handleCancelSection(sectionId)

      // Assert
      expect(wrapper.vm.sectionData[sectionId]).toEqual(originalData)
    })

    it('should reset hasChanges flag when canceling', () => {
      // Arrange
      const sectionId = 'professional_skills'
      wrapper.vm.hasChanges[sectionId] = true

      // Act
      wrapper.vm.handleCancelSection(sectionId)

      // Assert
      expect(wrapper.vm.hasChanges[sectionId]).toBe(false)
    })
  })

  describe('Validation', () => {
    beforeEach(() => {
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
    })

    it('should validate basic_info requires direct_manager', () => {
      // Arrange
      const sectionId = 'basic_info'
      const invalidData = { primary_activity_type: 'Development' } // Missing direct_manager

      // Act
      const isValid = wrapper.vm.validateSection(sectionId, invalidData)

      // Assert
      expect(isValid).toBe(false)
      expect(wrapper.vm.validationStatus[sectionId].error).toContain('руководителя')
    })

    it('should validate responsibility_areas requires at least one item', () => {
      // Arrange
      const sectionId = 'responsibility_areas'
      const invalidData: string[] = []

      // Act
      const isValid = wrapper.vm.validateSection(sectionId, invalidData)

      // Assert
      expect(isValid).toBe(false)
      expect(wrapper.vm.validationStatus[sectionId].error).toContain('зону ответственности')
    })

    it('should validate professional_skills requires at least one item', () => {
      // Arrange
      const sectionId = 'professional_skills'
      const invalidData: string[] = []

      // Act
      const isValid = wrapper.vm.validateSection(sectionId, invalidData)

      // Assert
      expect(isValid).toBe(false)
      expect(wrapper.vm.validationStatus[sectionId].error).toContain('навык')
    })

    it('should validate experience_and_education requires education_level', () => {
      // Arrange
      const sectionId = 'experience_and_education'
      const invalidData = { years_of_experience: 5 } // Missing education_level

      // Act
      const isValid = wrapper.vm.validateSection(sectionId, invalidData)

      // Assert
      expect(isValid).toBe(false)
      expect(wrapper.vm.validationStatus[sectionId].error).toContain('образования')
    })

    it('should pass validation with valid data', () => {
      // Arrange
      const sectionId = 'professional_skills'
      const validData = ['Python', 'TypeScript']

      // Act
      const isValid = wrapper.vm.validateSection(sectionId, validData)

      // Assert
      expect(isValid).toBe(true)
      expect(wrapper.vm.validationStatus[sectionId].isValid).toBe(true)
    })

    it('should validate section on data change', () => {
      // Arrange
      const sectionId = 'professional_skills'
      const validateSpy = vi.spyOn(wrapper.vm, 'validateSection')

      // Act
      wrapper.vm.handleSectionChange(sectionId)

      // Assert
      expect(validateSpy).toHaveBeenCalledWith(sectionId, wrapper.vm.sectionData[sectionId])
    })
  })

  describe('Save Section Functionality', () => {
    beforeEach(() => {
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })

      // Mock store method
      vi.spyOn(profilesStore, 'updateProfileContent').mockResolvedValue(undefined)
    })

    it('should not save if validation fails', async () => {
      // Arrange
      const sectionId = 'professional_skills'
      wrapper.vm.sectionData[sectionId] = [] // Invalid: empty array

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(profilesStore.updateProfileContent).not.toHaveBeenCalled()
    })

    it('should call store updateProfileContent with correct data', async () => {
      // Arrange
      const sectionId = 'professional_skills'
      const newSkills = ['Vue.js', 'React', 'Angular']
      wrapper.vm.sectionData[sectionId] = newSkills

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(profilesStore.updateProfileContent).toHaveBeenCalledWith(
        123,
        expect.objectContaining({
          professional_skills: newSkills,
        })
      )
    })

    it('should exit edit mode after successful save', async () => {
      // Arrange
      const sectionId = 'professional_skills'
      wrapper.vm.editingSections[sectionId] = true

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(wrapper.vm.editingSections[sectionId]).toBe(false)
    })

    it('should reset hasChanges flag after successful save', async () => {
      // Arrange
      const sectionId = 'professional_skills'
      wrapper.vm.hasChanges[sectionId] = true

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(wrapper.vm.hasChanges[sectionId]).toBe(false)
    })

    it('should emit section-saved event after successful save', async () => {
      // Arrange
      const sectionId = 'professional_skills'

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(wrapper.emitted('section-saved')).toBeTruthy()
      expect(wrapper.emitted('section-saved')?.[0]).toEqual([sectionId])
    })

    it('should handle save errors and update validation status', async () => {
      // Arrange
      const sectionId = 'professional_skills'
      const errorMessage = 'Network error'
      vi.spyOn(profilesStore, 'updateProfileContent').mockRejectedValue(
        new Error(errorMessage)
      )

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(wrapper.vm.validationStatus[sectionId].isValid).toBe(false)
      expect(wrapper.vm.validationStatus[sectionId].error).toBe(errorMessage)
    })

    it('should merge basic_info fields correctly', async () => {
      // Arrange
      const sectionId = 'basic_info'
      const basicInfoData = {
        direct_manager: 'New Manager',
        primary_activity_type: 'Architecture',
      }
      wrapper.vm.sectionData[sectionId] = basicInfoData

      // Act
      await wrapper.vm.handleSaveSection(sectionId)

      // Assert
      expect(profilesStore.updateProfileContent).toHaveBeenCalledWith(
        123,
        expect.objectContaining(basicInfoData)
      )
    })
  })

  describe('Section Data Management', () => {
    beforeEach(() => {
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
    })

    it('should mark section as changed when data is modified', () => {
      // Arrange
      const sectionId = 'professional_skills'

      // Act
      wrapper.vm.handleSectionChange(sectionId)

      // Assert
      expect(wrapper.vm.hasChanges[sectionId]).toBe(true)
    })

    it('should extract section data correctly for arrays', () => {
      // Arrange
      const sectionId = 'professional_skills'

      // Act
      const data = wrapper.vm.extractSectionData(sectionId, mockProfile.profile)

      // Assert
      expect(Array.isArray(data)).toBe(true)
      expect(data).toEqual(['Python', 'TypeScript', 'Docker'])
    })

    it('should extract basic_info fields correctly', () => {
      // Arrange
      const sectionId = 'basic_info'

      // Act
      const data = wrapper.vm.extractSectionData(sectionId, mockProfile.profile)

      // Assert
      expect(data).toEqual({
        direct_manager: 'Jane Smith',
        primary_activity_type: 'Software Development',
      })
    })

    it('should return null for unknown section', () => {
      // Arrange
      const sectionId = 'unknown_section'

      // Act
      const data = wrapper.vm.extractSectionData(sectionId, mockProfile.profile)

      // Assert
      expect(data).toBeNull()
    })
  })

  describe('Component Mapping', () => {
    beforeEach(() => {
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
    })

    it('should return correct component for each section', () => {
      // Arrange
      const testCases = [
        { sectionId: 'basic_info', expectedComponent: 'BasicInfoEditor' },
        { sectionId: 'responsibility_areas', expectedComponent: 'ResponsibilityAreasEditor' },
        { sectionId: 'professional_skills', expectedComponent: 'ProfessionalSkillsEditor' },
        { sectionId: 'corporate_competencies', expectedComponent: 'CompetenciesEditor' },
      ]

      // Act & Assert
      testCases.forEach(({ sectionId }) => {
        const component = wrapper.vm.getSectionComponent(sectionId)
        expect(component).toBeDefined()
        expect(component).not.toBe('div')
      })
    })

    it('should return div for unknown section', () => {
      // Act
      const component = wrapper.vm.getSectionComponent('unknown_section')

      // Assert
      expect(component).toBe('div')
    })
  })

  describe('Exposed Methods', () => {
    beforeEach(() => {
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
    })

    it('should expose editedSectionsCount', () => {
      // Arrange
      wrapper.vm.hasChanges.professional_skills = true
      wrapper.vm.hasChanges.corporate_competencies = true

      // Assert
      expect(wrapper.vm.editedSectionsCount).toBe(2)
    })

    it('should expose totalSections', () => {
      // Assert
      expect(wrapper.vm.totalSections).toBe(10)
    })

    it('should expose hasUnsavedChanges computed property', async () => {
      // Arrange
      wrapper.vm.hasChanges.professional_skills = true
      await wrapper.vm.$nextTick()

      // Act
      const exposed = wrapper.vm as unknown as {
        hasUnsavedChanges: boolean
      }

      // Assert
      expect(exposed.hasUnsavedChanges).toBe(true)
    })

    it('should validate all sections with validateAllSections', () => {
      // Arrange
      const validateSpy = vi.spyOn(wrapper.vm, 'validateSection')

      // Act
      const exposed = wrapper.vm as unknown as {
        validateAllSections: () => boolean
      }
      exposed.validateAllSections()

      // Assert
      expect(validateSpy).toHaveBeenCalledTimes(wrapper.vm.sections.length)
    })

    it('should return false from validateAllSections if any section invalid', () => {
      // Arrange
      wrapper.vm.sectionData.professional_skills = [] // Invalid

      // Act
      const exposed = wrapper.vm as unknown as {
        validateAllSections: () => boolean
      }
      const result = exposed.validateAllSections()

      // Assert
      expect(result).toBe(false)
    })

    it('should save all changed sections with saveAllSections', async () => {
      // Arrange
      wrapper.vm.hasChanges.professional_skills = true
      wrapper.vm.hasChanges.corporate_competencies = true
      const saveSpy = vi.spyOn(wrapper.vm, 'handleSaveSection')

      // Act
      const exposed = wrapper.vm as unknown as {
        saveAllSections: () => Promise<void>
      }
      await exposed.saveAllSections()

      // Assert
      expect(saveSpy).toHaveBeenCalledTimes(2)
    })
  })

  describe('Profile Change Watcher', () => {
    it('should reinitialize when currentProfile changes', async () => {
      // Arrange
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
      const initSpy = vi.spyOn(wrapper.vm, 'initializeSectionData')

      // Act
      const newProfile = { ...mockProfile }
      newProfile.profile.professional_skills = ['New Skill']
      profilesStore.currentProfile = newProfile
      await wrapper.vm.$nextTick()

      // Assert
      expect(initSpy).toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('should handle null section data', () => {
      // Arrange
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })

      // Act
      const isValid = wrapper.vm.validateSection('professional_skills', null)

      // Assert
      expect(isValid).toBe(false)
      expect(wrapper.vm.validationStatus.professional_skills.error).toBeDefined()
    })

    it('should handle non-array data for array sections', () => {
      // Arrange
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })

      // Act
      const isValid = wrapper.vm.validateSection(
        'professional_skills',
        'not-an-array' as unknown as string[]
      )

      // Assert
      expect(isValid).toBe(false)
    })

    it('should handle save without currentProfile', async () => {
      // Arrange
      wrapper = mount(ProfileContentEditor, {
        props: {
          profileId: 'P001',
        },
        global: {
          stubs: stubComponents,
          plugins: [vuetify],
        },
      })
      profilesStore.currentProfile = null

      // Act
      await wrapper.vm.handleSaveSection('professional_skills')

      // Assert
      expect(profilesStore.updateProfileContent).not.toHaveBeenCalled()
    })
  })
})

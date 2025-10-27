/**
 * Unit tests for FullProfileEditModal component
 * Tests dialog opening/closing, unsaved changes handling, save functionality, and keyboard shortcuts
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { setActivePinia, createPinia } from 'pinia'
import FullProfileEditModal from '@/components/profiles/FullProfileEditModal.vue'
import type { UnifiedPosition } from '@/types/unified'

// Create vuetify instance for tests
const vuetify = createVuetify()

describe('FullProfileEditModal', () => {
  let wrapper: VueWrapper<InstanceType<typeof FullProfileEditModal>>
  let mockProfile: UnifiedPosition

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Mock profile data
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
    }
  })

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('Dialog Opening/Closing', () => {
    it('should render dialog when modelValue is true', () => {
      // Arrange & Act
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.v-dialog').exists()).toBe(true)
      expect(wrapper.find('.v-card').exists()).toBe(true)
    })

    it('should not render dialog when modelValue is false', () => {
      // Arrange & Act
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: false,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const dialog = wrapper.findComponent({ name: 'VDialog' })
      expect(dialog.props('modelValue')).toBe(false)
    })

    it('should display profile position and department in header', () => {
      // Arrange & Act
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const headerText = wrapper.text()
      expect(headerText).toContain('Software Architect')
      expect(headerText).toContain('Backend Development')
      expect(headerText).toContain('Редактирование профиля')
    })

    it('should emit update:modelValue false when close button clicked', async () => {
      // Arrange
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      const closeButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-close')
      )
      await closeButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
    })

    it('should not close immediately if there are unsaved changes', async () => {
      // Arrange
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Set unsaved changes
      await wrapper.vm.$nextTick()
      wrapper.vm.hasUnsavedChanges = true
      await wrapper.vm.$nextTick()

      // Act
      const closeButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-close')
      )
      await closeButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Assert - unsaved dialog should appear
      expect(wrapper.vm.showUnsavedDialog).toBe(true)
      expect(wrapper.text()).toContain('Несохраненные изменения')
    })
  })

  describe('Unsaved Changes Dialog', () => {
    beforeEach(() => {
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should show unsaved changes count in dialog', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.unsavedChangesCount = 3
      wrapper.vm.showUnsavedDialog = true
      await wrapper.vm.$nextTick()

      // Assert
      const dialogText = wrapper.text()
      expect(dialogText).toContain('У вас есть несохраненные изменения в 3')
      expect(dialogText).toContain('Сохранить перед выходом?')
    })

    it('should handle singular form for 1 unsaved section', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.unsavedChangesCount = 1
      wrapper.vm.showUnsavedDialog = true
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.text()).toContain('секции')
    })

    it('should cancel close when clicking "Отмена" button', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.showUnsavedDialog = true
      await wrapper.vm.$nextTick()

      // Act
      const cancelButton = wrapper.findAll('button').find(btn =>
        btn.text() === 'Отмена'
      )
      await cancelButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.showUnsavedDialog).toBe(false)
      expect(wrapper.emitted('update:modelValue')).toBeFalsy()
    })

    it('should discard changes and close when clicking "Не сохранять"', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.showUnsavedDialog = true
      await wrapper.vm.$nextTick()

      // Act
      const discardButton = wrapper.findAll('button').find(btn =>
        btn.text() === 'Не сохранять'
      )
      await discardButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.hasUnsavedChanges).toBe(false)
      expect(wrapper.vm.showUnsavedDialog).toBe(false)
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
    })

    it('should save and close when clicking "Сохранить" button', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.showUnsavedDialog = true
      await wrapper.vm.$nextTick()

      // Act
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.text() === 'Сохранить'
      )
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.emitted('save')).toBeTruthy()
    })
  })

  describe('Save Functionality', () => {
    beforeEach(() => {
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should disable save button when no unsaved changes', () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = false

      // Assert
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Сохранить')
      )
      expect(saveButton?.attributes('disabled')).toBeDefined()
    })

    it('should enable save button when there are unsaved changes', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.unsavedChangesCount = 2
      await wrapper.vm.$nextTick()

      // Assert
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Сохранить')
      )
      expect(saveButton?.attributes('disabled')).toBeUndefined()
    })

    it('should show badge with unsaved changes count', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.unsavedChangesCount = 3
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.find('.v-badge').exists()).toBe(true)
      expect(wrapper.find('.v-badge__badge').text()).toBe('3')
    })

    it('should emit save event when save button clicked', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      await wrapper.vm.$nextTick()

      // Act
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Сохранить') && !btn.text().includes('Отмена')
      )
      await saveButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('save')).toBeTruthy()
    })

    it('should show loading state while saving', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true
      await wrapper.vm.$nextTick()

      // Act
      wrapper.vm.saving = true
      await wrapper.vm.$nextTick()

      // Assert
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Сохранить')
      )
      expect(saveButton?.classes()).toContain('v-btn--loading')
    })

    it('should reset hasUnsavedChanges after successful save', async () => {
      // Arrange
      wrapper.vm.hasUnsavedChanges = true

      // Act
      await wrapper.vm.handleSaveAll()
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.hasUnsavedChanges).toBe(false)
    })
  })

  describe('Section Navigation', () => {
    beforeEach(() => {
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should render quick navigation section', () => {
      // Assert
      expect(wrapper.text()).toContain('Быстрая навигация')
    })

    it('should display all section items in navigation', () => {
      // Assert
      const sections = wrapper.vm.sections
      expect(sections.length).toBeGreaterThan(0)

      sections.forEach(section => {
        expect(wrapper.text()).toContain(section.title)
      })
    })

    it('should mark section as active when clicked', async () => {
      // Arrange
      const firstSection = wrapper.vm.sections[0]

      // Act
      wrapper.vm.scrollToSection(firstSection.id)
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.activeSection).toBe(firstSection.id)
    })

    it('should show badge on sections with unsaved changes', async () => {
      // Arrange
      wrapper.vm.sections[0].hasChanges = true
      await wrapper.vm.$nextTick()

      // Assert
      const navList = wrapper.find('.quick-nav')
      expect(navList.findAll('.v-badge').length).toBeGreaterThan(0)
    })
  })

  describe('Validation Status', () => {
    beforeEach(() => {
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should render validation status section', () => {
      // Assert
      expect(wrapper.text()).toContain('Статус заполнения')
    })

    it('should show success icon for valid sections', async () => {
      // Arrange
      wrapper.vm.sections[0].isValid = true
      await wrapper.vm.$nextTick()

      // Assert
      const validationIcons = wrapper.findAll('.validation-status .v-icon')
      const successIcons = validationIcons.filter(icon =>
        icon.text().includes('mdi-check-circle')
      )
      expect(successIcons.length).toBeGreaterThan(0)
    })

    it('should show warning icon for invalid sections', async () => {
      // Arrange
      wrapper.vm.sections[0].isValid = false
      await wrapper.vm.$nextTick()

      // Assert
      const validationIcons = wrapper.findAll('.validation-status .v-icon')
      const warningIcons = validationIcons.filter(icon =>
        icon.text().includes('mdi-alert-circle')
      )
      expect(warningIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Keyboard Shortcuts', () => {
    beforeEach(() => {
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should display keyboard shortcuts section', () => {
      // Assert
      expect(wrapper.text()).toContain('Горячие клавиши')
      expect(wrapper.text()).toContain('Ctrl+S')
      expect(wrapper.text()).toContain('Esc')
      expect(wrapper.text()).toContain('Tab')
    })

    it('should show proper keyboard shortcut labels', () => {
      // Assert
      const kbd = wrapper.findAll('kbd')
      expect(kbd.length).toBeGreaterThanOrEqual(3)

      const shortcuts = kbd.map(k => k.text())
      expect(shortcuts).toContain('Ctrl+S')
      expect(shortcuts).toContain('Esc')
      expect(shortcuts).toContain('Tab')
    })
  })

  describe('Props Handling', () => {
    it('should handle null profile gracefully', () => {
      // Arrange & Act
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: null,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert - should not crash, should not render card content
      expect(wrapper.find('.v-card').exists()).toBe(false)
    })

    it('should update when modelValue prop changes', async () => {
      // Arrange
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: false,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      await wrapper.setProps({ modelValue: true })

      // Assert
      const dialog = wrapper.findComponent({ name: 'VDialog' })
      expect(dialog.props('modelValue')).toBe(true)
    })

    it('should update when profile prop changes', async () => {
      // Arrange
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      const newProfile = { ...mockProfile, position_name: 'Senior Developer' }
      await wrapper.setProps({ profile: newProfile })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.text()).toContain('Senior Developer')
    })
  })

  describe('Edge Cases', () => {
    it('should handle saving while already saving', async () => {
      // Arrange
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
      wrapper.vm.hasUnsavedChanges = true
      wrapper.vm.saving = true
      await wrapper.vm.$nextTick()

      // Act
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.text().includes('Сохранить')
      )

      // Assert - button should be disabled while saving
      expect(saveButton?.attributes('disabled')).toBeDefined()
    })

    it('should not allow closing while saving', async () => {
      // Arrange
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
      wrapper.vm.saving = true
      await wrapper.vm.$nextTick()

      // Act
      const closeButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-close')
      )

      // Assert - close button should be disabled while saving
      expect(closeButton?.attributes('disabled')).toBeDefined()
    })

    it('should handle empty sections array', () => {
      // Arrange & Act
      wrapper = mount(FullProfileEditModal, {
        props: {
          modelValue: true,
          profile: mockProfile,
        },
        global: {
          plugins: [vuetify],
        },
      })
      wrapper.vm.sections = []

      // Assert - should not crash
      expect(wrapper.exists()).toBe(true)
    })
  })
})

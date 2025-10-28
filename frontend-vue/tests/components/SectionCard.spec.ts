/**
 * Unit tests for SectionCard component
 * Tests view/edit mode switching, status badges display, validation error display, and action buttons
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import SectionCard from '@/components/profiles/SectionCard.vue'

// Create vuetify instance for tests
const vuetify = createVuetify()

describe('SectionCard', () => {
  let wrapper: VueWrapper<InstanceType<typeof SectionCard>>

  const defaultProps = {
    sectionId: 'test-section',
    title: 'Test Section',
    icon: 'mdi-test',
    isEditing: false,
    isValid: true,
    validationError: undefined,
    hasChanges: false,
  }

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('Basic Rendering', () => {
    it('should render card with title and icon', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: defaultProps,
        global: {
          plugins: [vuetify],
        },
        slots: {
          content: '<div>Test Content</div>',
        },
      })

      // Assert
      expect(wrapper.find('.v-card').exists()).toBe(true)
      expect(wrapper.text()).toContain('Test Section')
      expect(wrapper.find('.v-icon').text()).toContain('mdi-test')
    })

    it('should render slot content', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: defaultProps,
        global: {
          plugins: [vuetify],
        },
        slots: {
          content: '<div class="test-content">Custom Content</div>',
        },
      })

      // Assert
      expect(wrapper.find('.test-content').exists()).toBe(true)
      expect(wrapper.text()).toContain('Custom Content')
    })

    it('should apply correct CSS classes to card', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: defaultProps,
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.section-card').exists()).toBe(true)
    })
  })

  describe('View Mode', () => {
    beforeEach(() => {
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
        },
        global: {
          plugins: [vuetify],
        },
        slots: {
          content: '<div>Content</div>',
        },
      })
    })

    it('should display edit button in view mode', () => {
      // Assert
      const editButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-pencil')
      )
      expect(editButton).toBeDefined()
    })

    it('should not display save and cancel buttons in view mode', () => {
      // Assert
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-check')
      )
      const cancelButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-close')
      )
      expect(saveButton).toBeUndefined()
      expect(cancelButton).toBeUndefined()
    })

    it('should emit edit event when edit button clicked', async () => {
      // Arrange
      const editButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-pencil')
      )

      // Act
      await editButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('edit')).toBeTruthy()
    })

    it('should not display footer actions in view mode', () => {
      // Assert
      expect(wrapper.find('.v-card-actions').exists()).toBe(false)
    })
  })

  describe('Edit Mode', () => {
    beforeEach(() => {
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
        slots: {
          content: '<div>Content</div>',
        },
      })
    })

    it('should not display edit button in edit mode', () => {
      // Assert
      const editButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-pencil') &&
        !btn.find('.v-chip')?.exists()
      )
      expect(editButton).toBeUndefined()
    })

    it('should display save button in edit mode', () => {
      // Assert
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-check')
      )
      expect(saveButton).toBeDefined()
    })

    it('should display cancel button in edit mode', () => {
      // Assert
      const cancelButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-close')
      )
      expect(cancelButton).toBeDefined()
    })

    it('should emit save event when save button clicked', async () => {
      // Arrange
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-check')
      )

      // Act
      await saveButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('save')).toBeTruthy()
    })

    it('should emit cancel event when cancel button clicked', async () => {
      // Arrange
      const cancelButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-close')
      )

      // Act
      await cancelButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should display footer actions in edit mode', () => {
      // Assert
      expect(wrapper.find('.v-card-actions').exists()).toBe(true)
      expect(wrapper.text()).toContain('Отмена')
      expect(wrapper.text()).toContain('Сохранить секцию')
    })

    it('should emit save when footer save button clicked', async () => {
      // Arrange
      const footerSaveButton = wrapper.find('.v-card-actions button:last-child')

      // Act
      await footerSaveButton.trigger('click')

      // Assert
      expect(wrapper.emitted('save')).toBeTruthy()
    })

    it('should emit cancel when footer cancel button clicked', async () => {
      // Arrange
      const footerCancelButton = wrapper.find('.v-card-actions button:first-child')

      // Act
      await footerCancelButton.trigger('click')

      // Assert
      expect(wrapper.emitted('cancel')).toBeTruthy()
    })

    it('should apply editing CSS class', () => {
      // Assert
      expect(wrapper.find('.section-card--editing').exists()).toBe(true)
    })

    it('should change header background color in edit mode', () => {
      // Assert
      const sheet = wrapper.findComponent({ name: 'VSheet' })
      expect(sheet.props('bgColor')).toBe('primary-lighten-5')
    })

    it('should apply editing content class', () => {
      // Assert
      expect(wrapper.find('.section-content--editing').exists()).toBe(true)
    })
  })

  describe('Status Badges', () => {
    it('should display success badge when valid in view mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
          isValid: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const successChip = wrapper.findAllComponents({ name: 'VChip' }).find(chip =>
        chip.props('color') === 'success'
      )
      expect(successChip).toBeDefined()
      expect(successChip?.find('.v-icon')?.text()).toContain('mdi-check')
    })

    it('should display warning badge when invalid in view mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
          isValid: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const warningChip = wrapper.findAllComponents({ name: 'VChip' }).find(chip =>
        chip.props('color') === 'warning'
      )
      expect(warningChip).toBeDefined()
      expect(warningChip?.find('.v-icon')?.text()).toContain('mdi-alert')
    })

    it('should display editing badge in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const editingChip = wrapper.findAllComponents({ name: 'VChip' }).find(chip =>
        chip.text().includes('Редактирование')
      )
      expect(editingChip).toBeDefined()
      expect(editingChip?.props('color')).toBe('primary')
    })

    it('should display unsaved changes badge when hasChanges is true', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
          hasChanges: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Не сохранено')
      const badge = wrapper.findComponent({ name: 'VBadge' })
      expect(badge.exists()).toBe(true)
      expect(badge.props('color')).toBe('warning')
    })

    it('should not display unsaved changes badge in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
          hasChanges: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const unsavedChip = wrapper.findAllComponents({ name: 'VChip' }).find(chip =>
        chip.text().includes('Не сохранено')
      )
      expect(unsavedChip).toBeUndefined()
    })
  })

  describe('Validation Error Display', () => {
    it('should display validation error alert when invalid in view mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
          isValid: false,
          validationError: 'This field is required',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const alert = wrapper.findComponent({ name: 'VAlert' })
      expect(alert.exists()).toBe(true)
      expect(alert.props('type')).toBe('warning')
      expect(alert.text()).toContain('This field is required')
    })

    it('should not display validation error in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
          isValid: false,
          validationError: 'This field is required',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const alert = wrapper.findComponent({ name: 'VAlert' })
      expect(alert.exists()).toBe(false)
    })

    it('should not display validation error when valid', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
          isValid: true,
          validationError: undefined,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const alert = wrapper.findComponent({ name: 'VAlert' })
      expect(alert.exists()).toBe(false)
    })

    it('should not display alert if no validation error message', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
          isValid: false,
          validationError: undefined,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const alert = wrapper.findComponent({ name: 'VAlert' })
      expect(alert.exists()).toBe(false)
    })
  })

  describe('CSS Classes and Styling', () => {
    it('should apply invalid class when isValid is false', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isValid: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.section-card--invalid').exists()).toBe(true)
    })

    it('should not apply invalid class when isValid is true', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isValid: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.section-card--invalid').exists()).toBe(false)
    })

    it('should apply readonly content class in view mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.section-content--readonly').exists()).toBe(true)
    })

    it('should apply editing content class in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.section-content--editing').exists()).toBe(true)
    })
  })

  describe('Props Default Values', () => {
    it('should use default values for optional props', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          sectionId: 'test',
          title: 'Test',
          icon: 'mdi-test',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.vm.$props.isEditing).toBe(false)
      expect(wrapper.vm.$props.isValid).toBe(true)
      expect(wrapper.vm.$props.validationError).toBeUndefined()
      expect(wrapper.vm.$props.hasChanges).toBe(false)
    })
  })

  describe('Tooltips', () => {
    it('should show tooltip on edit button hover', async () => {
      // Arrange
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      const editButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-pencil')
      )
      await editButton?.trigger('mouseenter')
      await wrapper.vm.$nextTick()

      // Assert
      const tooltip = wrapper.findComponent({ name: 'VTooltip' })
      expect(tooltip.exists()).toBe(true)
      expect(wrapper.text()).toContain('Редактировать секцию')
    })

    it('should show tooltip on save button in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Сохранить изменения')
    })

    it('should show tooltip on cancel button in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Отменить изменения')
    })
  })

  describe('Icon Rendering', () => {
    it('should change icon color in edit mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const icon = wrapper.findAllComponents({ name: 'VIcon' })[0]
      expect(icon.props('color')).toBe('primary')
    })

    it('should not set icon color in view mode', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const icon = wrapper.findAllComponents({ name: 'VIcon' })[0]
      expect(icon.props('color')).toBeUndefined()
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long titles', () => {
      // Arrange & Act
      const longTitle = 'A'.repeat(200)
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          title: longTitle,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain(longTitle)
    })

    it('should handle very long validation errors', () => {
      // Arrange & Act
      const longError = 'Error: ' + 'x'.repeat(500)
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isValid: false,
          validationError: longError,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain(longError)
    })

    it('should handle rapid mode switching', async () => {
      // Arrange
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      await wrapper.setProps({ isEditing: true })
      await wrapper.setProps({ isEditing: false })
      await wrapper.setProps({ isEditing: true })

      // Assert
      expect(wrapper.find('.section-card--editing').exists()).toBe(true)
    })

    it('should handle special characters in section ID', () => {
      // Arrange & Act
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          sectionId: 'test-section!@#$%',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Multiple Event Emissions', () => {
    it('should emit multiple save events correctly', async () => {
      // Arrange
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      const saveButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-check')
      )
      await saveButton?.trigger('click')
      await saveButton?.trigger('click')
      await saveButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('save')?.length).toBe(3)
    })

    it('should emit both header and footer save events', async () => {
      // Arrange
      wrapper = mount(SectionCard, {
        props: {
          ...defaultProps,
          isEditing: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      const headerSaveButton = wrapper.findAll('button').find(btn =>
        btn.find('.v-icon')?.text().includes('mdi-check')
      )
      const footerSaveButton = wrapper.find('.v-card-actions button:last-child')

      await headerSaveButton?.trigger('click')
      await footerSaveButton?.trigger('click')

      // Assert
      expect(wrapper.emitted('save')?.length).toBe(2)
    })
  })
})

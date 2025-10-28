/**
 * Unit tests for CompetenciesEditor component
 * Tests add/remove items, validation (min/max), readonly mode, and v-model binding
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import CompetenciesEditor from '@/components/profiles/editors/CompetenciesEditor.vue'

// Create vuetify instance for tests
const vuetify = createVuetify()

describe('CompetenciesEditor', () => {
  let wrapper: VueWrapper<InstanceType<typeof CompetenciesEditor>>

  const defaultProps = {
    modelValue: ['Skill 1', 'Skill 2', 'Skill 3'],
    readonly: false,
  }

  afterEach(() => {
    wrapper?.unmount()
  })

  describe('Readonly Mode', () => {
    it('should display items as chips in readonly mode', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['JavaScript', 'TypeScript', 'Python'],
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.readonly-view').exists()).toBe(true)
      const chips = wrapper.findAllComponents({ name: 'VChip' })
      expect(chips.length).toBe(3)
      expect(wrapper.text()).toContain('JavaScript')
      expect(wrapper.text()).toContain('TypeScript')
      expect(wrapper.text()).toContain('Python')
    })

    it('should show empty state message when no items in readonly mode', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Нет данных')
      expect(wrapper.text()).toContain('Нажмите "Редактировать" для добавления')
    })

    it('should not display combobox in readonly mode', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Skill 1'],
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.findComponent({ name: 'VCombobox' }).exists()).toBe(false)
    })

    it('should not display edit controls in readonly mode', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Skill 1'],
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.edit-mode').exists()).toBe(false)
    })
  })

  describe('Edit Mode', () => {
    beforeEach(() => {
      wrapper = mount(CompetenciesEditor, {
        props: defaultProps,
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should display combobox in edit mode', () => {
      // Assert
      expect(wrapper.find('.edit-mode').exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'VCombobox' }).exists()).toBe(true)
    })

    it('should not display readonly view in edit mode', () => {
      // Assert
      expect(wrapper.find('.readonly-view').exists()).toBe(false)
    })

    it('should display helper text in edit mode', () => {
      // Assert
      expect(wrapper.text()).toContain('Нажмите Enter после ввода каждого элемента')
    })

    it('should render combobox with correct label', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          ...defaultProps,
          label: 'Custom Label',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const combobox = wrapper.findComponent({ name: 'VCombobox' })
      expect(combobox.props('label')).toBe('Custom Label')
    })

    it('should render combobox with correct placeholder', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          ...defaultProps,
          placeholder: 'Enter values...',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const combobox = wrapper.findComponent({ name: 'VCombobox' })
      expect(combobox.props('placeholder')).toBe('Enter values...')
    })

    it('should display icon in combobox', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          ...defaultProps,
          icon: 'mdi-star',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const icon = wrapper.findComponent({ name: 'VIcon' })
      expect(icon.exists()).toBe(true)
    })
  })

  describe('Add/Remove Items', () => {
    beforeEach(() => {
      wrapper = mount(CompetenciesEditor, {
        props: defaultProps,
        global: {
          plugins: [vuetify],
        },
      })
    })

    it('should emit update:modelValue when items are added', async () => {
      // Arrange
      const newItems = [...defaultProps.modelValue, 'New Skill']

      // Act
      wrapper.vm.localItems = newItems
      wrapper.vm.handleUpdate()
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      const emittedValue = wrapper.emitted('update:modelValue')?.[0]?.[0] as string[]
      expect(emittedValue).toContain('New Skill')
    })

    it('should remove item when removeItem is called', async () => {
      // Arrange
      const itemToRemove = 'Skill 2'

      // Act
      wrapper.vm.removeItem(itemToRemove)
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      const emittedValue = wrapper.emitted('update:modelValue')?.[0]?.[0] as string[]
      expect(emittedValue).not.toContain(itemToRemove)
      expect(emittedValue.length).toBe(2)
    })

    it('should filter out empty strings when updating', async () => {
      // Arrange
      wrapper.vm.localItems = ['Valid', '', '  ', 'Another Valid', '']

      // Act
      wrapper.vm.handleUpdate()
      await wrapper.vm.$nextTick()

      // Assert
      const emittedValue = wrapper.emitted('update:modelValue')?.[0]?.[0] as string[]
      expect(emittedValue).toEqual(['Valid', 'Another Valid'])
    })

    it('should handle removing all items', async () => {
      // Act
      wrapper.vm.removeItem('Skill 1')
      wrapper.vm.removeItem('Skill 2')
      wrapper.vm.removeItem('Skill 3')
      await wrapper.vm.$nextTick()

      // Assert
      const emittedValue = wrapper.emitted('update:modelValue')?.slice(-1)[0]?.[0] as string[]
      expect(emittedValue.length).toBe(0)
    })
  })

  describe('Validation (Min/Max)', () => {
    it('should display warning when below minimum items', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1'],
          readonly: false,
          minItems: 3,
          showStats: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('минимум: 3')
      expect(wrapper.find('.text-warning').exists()).toBe(true)
    })

    it('should display error when above maximum items', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5', 'Item 6'],
          readonly: false,
          maxItems: 5,
          showStats: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('максимум: 5')
      expect(wrapper.find('.text-error').exists()).toBe(true)
    })

    it('should not show validation messages when within range', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2', 'Item 3'],
          readonly: false,
          minItems: 2,
          maxItems: 5,
          showStats: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.find('.text-warning').exists()).toBe(false)
      expect(wrapper.find('.text-error').exists()).toBe(false)
    })

    it('should display item count in statistics', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2', 'Item 3'],
          readonly: false,
          showStats: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Добавлено: 3')
    })

    it('should not show stats when showStats is false', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2'],
          readonly: false,
          showStats: false,
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

  describe('V-Model Binding', () => {
    it('should initialize local items from modelValue prop', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Vue', 'React', 'Angular'],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.vm.localItems).toEqual(['Vue', 'React', 'Angular'])
    })

    it('should update local items when modelValue prop changes', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Initial'],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      await wrapper.setProps({ modelValue: ['Updated', 'Values'] })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.localItems).toEqual(['Updated', 'Values'])
    })

    it('should not update local items if values are the same', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2'],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      const originalItems = [...wrapper.vm.localItems]

      // Act
      await wrapper.setProps({ modelValue: ['Item 1', 'Item 2'] })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.localItems).toEqual(originalItems)
    })

    it('should emit update:modelValue with current values', () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1'],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      wrapper.vm.localItems = ['New Item 1', 'New Item 2']
      wrapper.vm.handleUpdate()

      // Assert
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([['New Item 1', 'New Item 2']])
    })
  })

  describe('Suggestions', () => {
    const suggestions = ['JavaScript', 'TypeScript', 'Python', 'Java', 'C++']

    it('should display popular suggestions in edit mode', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          suggestions,
          showPopularSuggestions: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Популярные варианты:')
      expect(wrapper.text()).toContain('JavaScript')
      expect(wrapper.text()).toContain('TypeScript')
    })

    it('should not show suggestions when showPopularSuggestions is false', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          suggestions,
          showPopularSuggestions: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).not.toContain('Популярные варианты:')
    })

    it('should add suggestion when clicked', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          suggestions,
          showPopularSuggestions: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      wrapper.vm.addSuggestion('JavaScript')
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.emitted('update:modelValue')?.[0]?.[0]).toContain('JavaScript')
    })

    it('should disable suggestion chip if already added', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['JavaScript'],
          readonly: false,
          suggestions,
          showPopularSuggestions: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const suggestionChips = wrapper.findAll('.ma-1')
      const jsChip = suggestionChips.find(chip => chip.text().includes('JavaScript'))
      expect(jsChip?.attributes('disabled')).toBeDefined()
    })

    it('should not add duplicate suggestion', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['JavaScript'],
          readonly: false,
          suggestions,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      wrapper.vm.addSuggestion('JavaScript')
      await wrapper.vm.$nextTick()

      // Assert - should not emit because item already exists
      expect(wrapper.emitted('update:modelValue')).toBeFalsy()
    })

    it('should show only first 10 suggestions', () => {
      // Arrange
      const manySuggestions = Array.from({ length: 20 }, (_, i) => `Skill ${i}`)

      // Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          suggestions: manySuggestions,
          showPopularSuggestions: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.vm.popularSuggestions.length).toBeLessThanOrEqual(10)
    })

    it('should filter out already added items from suggestions', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['JavaScript', 'TypeScript'],
          readonly: false,
          suggestions,
          showPopularSuggestions: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const popularSuggestions = wrapper.vm.popularSuggestions
      expect(popularSuggestions).not.toContain('JavaScript')
      expect(popularSuggestions).not.toContain('TypeScript')
      expect(popularSuggestions).toContain('Python')
    })
  })

  describe('Custom Props', () => {
    it('should use custom label', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          label: 'Custom Skills Label',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const combobox = wrapper.findComponent({ name: 'VCombobox' })
      expect(combobox.props('label')).toBe('Custom Skills Label')
    })

    it('should use custom helper text', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          helperText: 'Custom helper instructions',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('Custom helper instructions')
    })

    it('should use custom items label in stats', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2'],
          readonly: false,
          itemsLabel: 'компетенций',
          showStats: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain('2 компетенций')
    })

    it('should use custom icon', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
          icon: 'mdi-brain',
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      const icon = wrapper.findComponent({ name: 'VIcon' })
      expect(icon.text()).toContain('mdi-brain')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty modelValue', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.vm.localItems).toEqual([])
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle very long item text', () => {
      // Arrange
      const longItem = 'A'.repeat(500)

      // Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [longItem],
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      expect(wrapper.text()).toContain(longItem)
    })

    it('should handle items with special characters', () => {
      // Arrange
      const specialItems = ['C++', 'C#', 'F#', 'Node.js', 'Vue.js 3.0']

      // Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: specialItems,
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert
      specialItems.forEach(item => {
        expect(wrapper.text()).toContain(item)
      })
    })

    it('should handle null modelValue gracefully', () => {
      // Arrange & Act
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: null as unknown as string[],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Assert - should not crash
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle rapid item additions', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: [],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      for (let i = 0; i < 50; i++) {
        wrapper.vm.localItems.push(`Skill ${i}`)
      }
      wrapper.vm.handleUpdate()
      await wrapper.vm.$nextTick()

      // Assert
      const emittedValue = wrapper.emitted('update:modelValue')?.slice(-1)[0]?.[0] as string[]
      expect(emittedValue.length).toBe(50)
    })

    it('should handle removing non-existent item', () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1', 'Item 2'],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      wrapper.vm.removeItem('Non-existent Item')

      // Assert - should not crash
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Switching Between Modes', () => {
    it('should switch from readonly to edit mode', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1'],
          readonly: true,
        },
        global: {
          plugins: [vuetify],
        },
      })
      expect(wrapper.find('.readonly-view').exists()).toBe(true)

      // Act
      await wrapper.setProps({ readonly: false })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.find('.edit-mode').exists()).toBe(true)
      expect(wrapper.find('.readonly-view').exists()).toBe(false)
    })

    it('should switch from edit to readonly mode', async () => {
      // Arrange
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: ['Item 1'],
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })
      expect(wrapper.find('.edit-mode').exists()).toBe(true)

      // Act
      await wrapper.setProps({ readonly: true })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.find('.readonly-view').exists()).toBe(true)
      expect(wrapper.find('.edit-mode').exists()).toBe(false)
    })

    it('should maintain data when switching modes', async () => {
      // Arrange
      const testData = ['Skill A', 'Skill B', 'Skill C']
      wrapper = mount(CompetenciesEditor, {
        props: {
          modelValue: testData,
          readonly: false,
        },
        global: {
          plugins: [vuetify],
        },
      })

      // Act
      await wrapper.setProps({ readonly: true })
      await wrapper.vm.$nextTick()

      // Assert
      expect(wrapper.vm.localItems).toEqual(testData)
      testData.forEach(skill => {
        expect(wrapper.text()).toContain(skill)
      })
    })
  })
})

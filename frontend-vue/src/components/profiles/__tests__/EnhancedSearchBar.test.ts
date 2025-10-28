/**
 * Unit tests for EnhancedSearchBar component
 * Tests search input, navigation, filters, and view toggle
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import EnhancedSearchBar from '../EnhancedSearchBar.vue'
import type { SearchFilters } from '@/composables/useSearch'

const vuetify = createVuetify({
  components,
  directives
})

describe('EnhancedSearchBar', () => {
  const defaultProps = {
    searchQuery: '',
    viewMode: 'tree' as const,
    totalResults: 0,
    navigationLabel: '0/0',
    hasResults: false,
    isSearching: false,
    filters: {
      withProfile: false,
      withoutProfile: false,
      exactMatch: false
    } as SearchFilters
  }

  const createWrapper = (props = {}) => {
    return mount(EnhancedSearchBar, {
      props: { ...defaultProps, ...props },
      global: {
        plugins: [vuetify]
      }
    })
  }

  describe('Rendering', () => {
    it('should render search input', () => {
      const wrapper = createWrapper()
      const input = wrapper.find('input[type="text"]')
      expect(input.exists()).toBe(true)
    })

    it('should render view toggle buttons', () => {
      const wrapper = createWrapper()
      const buttons = wrapper.findAll('.v-btn')
      const treeButton = buttons.find(btn => btn.text().includes('Дерево'))
      const tableButton = buttons.find(btn => btn.text().includes('Таблица'))

      expect(treeButton).toBeDefined()
      expect(tableButton).toBeDefined()
    })

    it('should display results counter badge when searching', () => {
      const wrapper = createWrapper({
        isSearching: true,
        totalResults: 5
      })

      const badge = wrapper.find('.v-chip')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('5')
    })

    it('should not display results counter when not searching', () => {
      const wrapper = createWrapper({
        isSearching: false,
        totalResults: 0
      })

      const badges = wrapper.findAll('.v-chip').filter(chip =>
        chip.text() === '0'
      )
      expect(badges.length).toBe(0)
    })

    it('should show error color when no results found', () => {
      const wrapper = createWrapper({
        isSearching: true,
        totalResults: 0
      })

      const badge = wrapper.find('.v-chip')
      expect(badge.classes()).toContain('bg-error')
    })

    it('should show primary color when results found', () => {
      const wrapper = createWrapper({
        isSearching: true,
        totalResults: 5
      })

      const badge = wrapper.find('.v-chip')
      expect(badge.classes()).toContain('bg-primary')
    })
  })

  describe('Search Input', () => {
    it('should emit update:searchQuery on input change', async () => {
      const wrapper = createWrapper()
      const input = wrapper.find('input[type="text"]')

      await input.setValue('test query')

      expect(wrapper.emitted('update:searchQuery')).toBeTruthy()
      expect(wrapper.emitted('update:searchQuery')?.[0]).toEqual(['test query'])
    })

    it('should emit empty string when input is cleared', async () => {
      const wrapper = createWrapper({ searchQuery: 'test' })
      const input = wrapper.find('input[type="text"]')

      await input.setValue('')

      expect(wrapper.emitted('update:searchQuery')).toBeTruthy()
      expect(wrapper.emitted('update:searchQuery')?.[0]).toEqual([''])
    })

    it('should emit next on Enter key when has results', async () => {
      const wrapper = createWrapper({ hasResults: true })
      const input = wrapper.find('input[type="text"]')

      await input.trigger('keyup.enter')

      expect(wrapper.emitted('next')).toBeTruthy()
    })

    it('should emit search on Enter key when no results', async () => {
      const wrapper = createWrapper({ hasResults: false })
      const input = wrapper.find('input[type="text"]')

      await input.trigger('keyup.enter')

      expect(wrapper.emitted('search')).toBeTruthy()
    })

    it('should emit previous on Shift+Enter', async () => {
      const wrapper = createWrapper({ hasResults: true })
      const input = wrapper.find('input[type="text"]')

      await input.trigger('keyup.shift.enter')

      expect(wrapper.emitted('previous')).toBeTruthy()
    })

    it('should not emit previous on Shift+Enter when no results', async () => {
      const wrapper = createWrapper({ hasResults: false })
      const input = wrapper.find('input[type="text"]')

      await input.trigger('keyup.shift.enter')

      expect(wrapper.emitted('previous')).toBeFalsy()
    })
  })

  describe('Navigation Buttons', () => {
    it('should show navigation buttons when hasResults', () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 3,
        navigationLabel: '1/3'
      })

      const navButtons = wrapper.findAll('.v-btn').filter(btn =>
        btn.html().includes('mdi-chevron-left') || btn.html().includes('mdi-chevron-right')
      )

      expect(navButtons.length).toBeGreaterThanOrEqual(2)
    })

    it('should not show navigation buttons when no results', () => {
      const wrapper = createWrapper({
        hasResults: false,
        totalResults: 0
      })

      const navButtons = wrapper.findAll('.v-btn').filter(btn =>
        btn.html().includes('mdi-chevron-left') || btn.html().includes('mdi-chevron-right')
      )

      expect(navButtons.length).toBe(0)
    })

    it('should disable navigation when totalResults <= 1', () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 1
      })

      const navButtons = wrapper.findAll('.v-btn').filter(btn =>
        btn.html().includes('mdi-chevron-left') || btn.html().includes('mdi-chevron-right')
      )

      navButtons.forEach(btn => {
        expect(btn.attributes('disabled')).toBeDefined()
      })
    })

    it('should enable navigation when totalResults > 1', () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 3
      })

      const navButtons = wrapper.findAll('.v-btn').filter(btn =>
        btn.html().includes('mdi-chevron-left') || btn.html().includes('mdi-chevron-right')
      )

      navButtons.forEach(btn => {
        expect(btn.attributes('disabled')).toBeUndefined()
      })
    })

    it('should emit next when chevron-right clicked', async () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 3
      })

      const nextButton = wrapper.findAll('.v-btn').find(btn =>
        btn.html().includes('mdi-chevron-right')
      )

      await nextButton?.trigger('click')

      expect(wrapper.emitted('next')).toBeTruthy()
    })

    it('should emit previous when chevron-left clicked', async () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 3
      })

      const prevButton = wrapper.findAll('.v-btn').find(btn =>
        btn.html().includes('mdi-chevron-left')
      )

      await prevButton?.trigger('click')

      expect(wrapper.emitted('previous')).toBeTruthy()
    })

    it('should display navigation label', () => {
      const wrapper = createWrapper({
        hasResults: true,
        navigationLabel: '2/5'
      })

      expect(wrapper.text()).toContain('2/5')
    })
  })

  describe('Filters', () => {
    it('should display active filters count badge', () => {
      const wrapper = createWrapper({
        filters: {
          withProfile: true,
          withoutProfile: true,
          exactMatch: false
        }
      })

      const filterBadge = wrapper.find('.v-badge')
      expect(filterBadge.exists()).toBe(true)
    })

    it('should not show badge when no active filters', () => {
      const wrapper = createWrapper({
        filters: {
          withProfile: false,
          withoutProfile: false,
          exactMatch: false
        }
      })

      const badge = wrapper.find('.v-badge[content="0"]')
      // Badge should not be visible when count is 0
      expect(badge.attributes('style')).toContain('display: none')
    })

    it('should emit update:filters when filter checkbox changed', async () => {
      const wrapper = createWrapper()

      // Open filters menu
      const filterButton = wrapper.findAll('.v-btn').find(btn =>
        btn.html().includes('mdi-filter-variant')
      )
      await filterButton?.trigger('click')

      // Find and click a checkbox
      const checkboxes = wrapper.findAll('.v-checkbox')
      if (checkboxes.length > 0) {
        const checkbox = checkboxes[0]
        await checkbox.trigger('click')

        expect(wrapper.emitted('update:filters')).toBeTruthy()
      }
    })

    it('should emit reset-filters when reset button clicked', async () => {
      const wrapper = createWrapper({
        filters: {
          withProfile: true,
          withoutProfile: false,
          exactMatch: false
        }
      })

      // Open filters menu
      const filterButton = wrapper.findAll('.v-btn').find(btn =>
        btn.html().includes('mdi-filter-variant')
      )
      await filterButton?.trigger('click')

      // Find reset button
      const resetButton = wrapper.findAll('.v-btn').find(btn =>
        btn.text().includes('Сбросить фильтры')
      )

      await resetButton?.trigger('click')

      expect(wrapper.emitted('reset-filters')).toBeTruthy()
    })

    it('should disable reset button when no active filters', async () => {
      const wrapper = createWrapper({
        filters: {
          withProfile: false,
          withoutProfile: false,
          exactMatch: false
        }
      })

      // Open filters menu
      const filterButton = wrapper.findAll('.v-btn').find(btn =>
        btn.html().includes('mdi-filter-variant')
      )
      await filterButton?.trigger('click')

      // Find reset button
      const resetButton = wrapper.findAll('.v-btn').find(btn =>
        btn.text().includes('Сбросить фильтры')
      )

      expect(resetButton?.attributes('disabled')).toBeDefined()
    })

    it('should count all active filters correctly', () => {
      const wrapper = createWrapper({
        filters: {
          withProfile: true,
          withoutProfile: true,
          exactMatch: true
        }
      })

      // activeFiltersCount should be 3
      const badge = wrapper.find('.v-badge__badge')
      expect(badge.text()).toBe('3')
    })
  })

  describe('View Toggle', () => {
    it('should emit update:viewMode when view toggle clicked', async () => {
      const wrapper = createWrapper({ viewMode: 'tree' })

      const tableButton = wrapper.findAll('.v-btn').find(btn =>
        btn.text().includes('Таблица')
      )

      await tableButton?.trigger('click')

      expect(wrapper.emitted('update:viewMode')).toBeTruthy()
      expect(wrapper.emitted('update:viewMode')?.[0]).toEqual(['table'])
    })

    it('should highlight current view mode', () => {
      const wrapper = createWrapper({ viewMode: 'tree' })

      const toggleGroup = wrapper.find('.v-btn-toggle')
      expect(toggleGroup.exists()).toBe(true)
    })
  })

  describe('Accessibility', () => {
    it('should have aria-label on search input', () => {
      const wrapper = createWrapper()
      const input = wrapper.find('input[type="text"]')

      expect(input.attributes('aria-label')).toBe('Поиск позиций')
    })

    it('should have aria-labels on navigation buttons', () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 3
      })

      const nextButton = wrapper.findAll('.v-btn').find(btn =>
        btn.attributes('aria-label')?.includes('Следующий')
      )
      const prevButton = wrapper.findAll('.v-btn').find(btn =>
        btn.attributes('aria-label')?.includes('Предыдущий')
      )

      expect(nextButton?.attributes('aria-label')).toContain('Enter')
      expect(prevButton?.attributes('aria-label')).toContain('Shift+Enter')
    })

    it('should have aria-label on filter button', () => {
      const wrapper = createWrapper()

      const filterButton = wrapper.findAll('.v-btn').find(btn =>
        btn.html().includes('mdi-filter-variant')
      )

      expect(filterButton?.attributes('aria-label')).toBe('Фильтры поиска')
    })

    it('should have tooltips on navigation buttons', () => {
      const wrapper = createWrapper({
        hasResults: true,
        totalResults: 3
      })

      const tooltips = wrapper.findAll('.v-tooltip')
      expect(tooltips.length).toBeGreaterThan(0)
    })
  })

  describe('Edge Cases', () => {
    it('should handle null search query', async () => {
      const wrapper = createWrapper()

      // Simulate clearing input (Vuetify emits null)
      await wrapper.vm.handleSearchInput(null)

      expect(wrapper.emitted('update:searchQuery')?.[0]).toEqual([''])
    })

    it('should handle filter value as null from Vuetify checkbox', () => {
      const wrapper = createWrapper()

      wrapper.vm.updateFilter('withProfile', null)

      expect(wrapper.emitted('update:filters')?.[0]).toBeDefined()
      const emittedFilters = wrapper.emitted('update:filters')?.[0][0] as SearchFilters
      expect(emittedFilters.withProfile).toBe(false)
    })

    it('should preserve other filters when updating one', () => {
      const wrapper = createWrapper({
        filters: {
          withProfile: true,
          withoutProfile: false,
          exactMatch: true
        }
      })

      wrapper.vm.updateFilter('withoutProfile', true)

      const emittedFilters = wrapper.emitted('update:filters')?.[0][0] as SearchFilters
      expect(emittedFilters.withProfile).toBe(true)
      expect(emittedFilters.exactMatch).toBe(true)
      expect(emittedFilters.withoutProfile).toBe(true)
    })
  })

  describe('Props Handling', () => {
    it('should display correct placeholder text', () => {
      const wrapper = createWrapper()
      const input = wrapper.find('input[type="text"]')

      expect(input.attributes('placeholder')).toContain('Поиск по названию позиции')
    })

    it('should bind searchQuery prop to input value', () => {
      const wrapper = createWrapper({ searchQuery: 'test search' })
      const textField = wrapper.findComponent({ name: 'VTextField' })

      expect(textField.props('modelValue')).toBe('test search')
    })

    it('should update when totalResults prop changes', async () => {
      const wrapper = createWrapper({
        isSearching: true,
        totalResults: 3
      })

      let badge = wrapper.find('.v-chip')
      expect(badge.text()).toBe('3')

      await wrapper.setProps({ totalResults: 7 })

      badge = wrapper.find('.v-chip')
      expect(badge.text()).toBe('7')
    })

    it('should react to viewMode prop changes', async () => {
      const wrapper = createWrapper({ viewMode: 'tree' })

      await wrapper.setProps({ viewMode: 'table' })

      const toggleGroup = wrapper.findComponent({ name: 'VBtnToggle' })
      expect(toggleGroup.props('modelValue')).toBe('table')
    })
  })
})

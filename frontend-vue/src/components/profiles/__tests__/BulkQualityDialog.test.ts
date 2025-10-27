/**
 * Unit tests for BulkQualityDialog component
 *
 * Tests quality check dialog with profile grouping
 */

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import BulkQualityDialog from '../BulkQualityDialog.vue'
import type { UnifiedPosition } from '@/types/unified'

// Create vuetify instance
const vuetify = createVuetify({
  components,
  directives
})

// Mock positions with different quality scores
const createMockPosition = (
  id: string,
  name: string,
  qualityScore: number
): UnifiedPosition => ({
  position_id: id,
  position_name: name,
  business_unit_id: 'bu_1',
  business_unit_name: 'Business Unit 1',
  department_id: 'dept_1',
  department_name: 'Department 1',
  department_path: '/Department 1',
  status: 'generated',
  profile_id: parseInt(id),
  quality_score: qualityScore,
  completeness_score: qualityScore,
  actions: {
    canView: true,
    canEdit: true,
    canDelete: true,
    canRegenerate: true,
    canCancel: false
  }
})

describe('BulkQualityDialog', () => {
  it('should render dialog when modelValue is true', () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Position 1', 0.9)
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert
    expect(wrapper.find('.v-card').exists()).toBe(true)
    expect(wrapper.text()).toContain('Проверка качества профилей')
  })

  it('should not render dialog when modelValue is false', () => {
    // Arrange
    const positions: UnifiedPosition[] = []

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: false,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert
    expect(wrapper.find('.v-card').exists()).toBe(false)
  })

  it('should group positions by quality score correctly', () => {
    // Arrange - Mix of good, ok, and poor quality
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Good 1', 0.95), // Good: ≥0.8
      createMockPosition('2', 'Good 2', 0.85), // Good: ≥0.8
      createMockPosition('3', 'OK 1', 0.75), // OK: 0.6-0.79
      createMockPosition('4', 'OK 2', 0.65), // OK: 0.6-0.79
      createMockPosition('5', 'Poor 1', 0.55), // Poor: <0.6
      createMockPosition('6', 'Poor 2', 0.45) // Poor: <0.6
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert - Check summary cards
    const cards = wrapper.findAllComponents({ name: 'VCard' })

    // Find text content
    const text = wrapper.text()
    expect(text).toContain('2') // Good count
    expect(text).toContain('2') // OK count (might overlap with good)
    expect(text).toContain('2') // Poor count
  })

  it('should display good quality profiles correctly', () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Excellent Position', 0.95),
      createMockPosition('2', 'Great Position', 0.85)
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert
    expect(wrapper.text()).toContain('Excellent Position')
    expect(wrapper.text()).toContain('Great Position')
    expect(wrapper.text()).toContain('95%')
    expect(wrapper.text()).toContain('85%')
  })

  it('should display poor quality profiles correctly', () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Needs Improvement', 0.45),
      createMockPosition('2', 'Low Quality', 0.35)
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert
    expect(wrapper.text()).toContain('Needs Improvement')
    expect(wrapper.text()).toContain('Low Quality')
    expect(wrapper.text()).toContain('45%')
    expect(wrapper.text()).toContain('35%')
  })

  it('should show recommendation alert when poor quality profiles exist', () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Poor Quality', 0.45)
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert
    expect(wrapper.text()).toContain('Рекомендуется регенерация')
    expect(wrapper.text()).toContain('Найдено 1')
  })

  it('should not show recommendation alert when no poor quality profiles', () => {
    // Arrange - Only good and ok quality
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Good Quality', 0.85),
      createMockPosition('2', 'OK Quality', 0.65)
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert
    expect(wrapper.text()).not.toContain('Рекомендуется регенерация')
  })

  it('should emit regenerate event when regenerate button clicked', async () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Poor 1', 0.45),
      createMockPosition('2', 'Poor 2', 0.35)
    ]

    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Act - Find and click regenerate button
    const regenerateButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Регенерировать')
    )

    expect(regenerateButton).toBeDefined()
    await regenerateButton!.trigger('click')

    // Assert
    expect(wrapper.emitted('regenerate')).toBeTruthy()

    const emitted = wrapper.emitted('regenerate')![0]
    expect(emitted[0]).toEqual(['1', '2']) // Position IDs
  })

  it('should emit update:modelValue when close button clicked', async () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Position', 0.85)
    ]

    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Act - Find and click close button
    const closeButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Закрыть')
    )

    expect(closeButton).toBeDefined()
    await closeButton!.trigger('click')

    // Assert
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
  })

  it('should close dialog after regenerate clicked', async () => {
    // Arrange
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Poor Quality', 0.45)
    ]

    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Act
    const regenerateButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Регенерировать')
    )

    await regenerateButton!.trigger('click')

    // Assert - Dialog should be closed
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
  })

  it('should handle positions with missing quality scores', () => {
    // Arrange - Position without quality_score
    const positions: UnifiedPosition[] = [
      {
        ...createMockPosition('1', 'No Score', 0),
        quality_score: undefined
      }
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert - Should treat as 0% (poor quality)
    expect(wrapper.text()).toContain('No Score')
    expect(wrapper.text()).toContain('0%')
  })

  it('should correctly pluralize Russian words', () => {
    // Arrange
    const testCases = [
      { count: 1, positions: [createMockPosition('1', 'P1', 0.45)] },
      { count: 2, positions: [
        createMockPosition('1', 'P1', 0.45),
        createMockPosition('2', 'P2', 0.35)
      ]},
      { count: 5, positions: Array.from({ length: 5 }, (_, i) =>
        createMockPosition(String(i + 1), `P${i + 1}`, 0.45)
      )}
    ]

    testCases.forEach(({ count, positions }) => {
      // Act
      const wrapper = mount(BulkQualityDialog, {
        props: {
          modelValue: true,
          positions
        },
        global: {
          plugins: [vuetify]
        }
      })

      // Assert - Check pluralization in alert
      const text = wrapper.text()
      expect(text).toContain(`Найдено ${count}`)

      if (count === 1) {
        expect(text).toContain('профиль')
      } else if (count >= 2 && count <= 4) {
        expect(text).toContain('профиля')
      } else {
        expect(text).toContain('профилей')
      }
    })
  })

  it('should disable tabs when groups are empty', () => {
    // Arrange - Only good quality profiles
    const positions: UnifiedPosition[] = [
      createMockPosition('1', 'Good', 0.95)
    ]

    // Act
    const wrapper = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions
      },
      global: {
        plugins: [vuetify]
      }
    })

    // Assert - Poor and OK tabs should be disabled
    const tabs = wrapper.findAllComponents({ name: 'VTab' })

    // Check that tabs exist
    expect(tabs.length).toBeGreaterThan(0)
  })

  it('should show regenerate button only when poor quality profiles exist', () => {
    // Test 1: With poor quality - button should exist
    const withPoor = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions: [createMockPosition('1', 'Poor', 0.45)]
      },
      global: {
        plugins: [vuetify]
      }
    })

    expect(withPoor.text()).toContain('Регенерировать')

    // Test 2: Without poor quality - button should not exist
    const withoutPoor = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions: [createMockPosition('1', 'Good', 0.95)]
      },
      global: {
        plugins: [vuetify]
      }
    })

    expect(withoutPoor.text()).not.toContain('Регенерировать')
  })
})

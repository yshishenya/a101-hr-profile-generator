/**
 * Unit tests for BulkQualityDialog component
 *
 * Tests quality check dialog with profile grouping
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import { nextTick } from 'vue'
import { h } from 'vue'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import BulkQualityDialog from '../BulkQualityDialog.vue'
import type { UnifiedPosition } from '@/types/unified'

// Create vuetify instance with SSR settings for tests
const vuetify = createVuetify({
  components,
  directives,
  ssr: true // Disable teleport for tests
})

// Stub VTabs and VWindow to avoid VSlideGroup rendering issues
const VTabsStub = {
  name: 'VTabs',
  props: ['modelValue', 'bgColor'],
  emits: ['update:modelValue'],
  template: '<div class="v-tabs"><slot /></div>'
}

const VTabStub = {
  name: 'VTab',
  props: ['value', 'disabled'],
  template: '<button :disabled="disabled"><slot /></button>'
}

const VWindowStub = {
  name: 'VWindow',
  props: ['modelValue'],
  setup(props: { modelValue: string }, { slots }: { slots: any }) {
    return () => h('div', { class: 'v-window' }, slots.default?.())
  }
}

const VWindowItemStub = {
  name: 'VWindowItem',
  props: ['value'],
  template: '<div class="v-window-item"><slot /></div>'
}

const VSlideGroupStub = {
  name: 'VSlideGroup',
  template: '<div class="v-slide-group"><slot /></div>'
}

// Global mount options with stubs
const globalMountOptions = {
  plugins: [vuetify],
  stubs: {
    VTabs: VTabsStub,
    VTab: VTabStub,
    VWindow: VWindowStub,
    VWindowItem: VWindowItemStub,
    VSlideGroup: VSlideGroupStub
  }
}

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
  it('should render dialog when modelValue is true', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert
    expect(wrapper.props('modelValue')).toBe(true)
    expect(wrapper.props('positions').length).toBe(1)

    wrapper.unmount()
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

  it('should group positions by quality score correctly', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert - Check all position names appear
    const text = wrapper.text()
    expect(text).toContain('Good 1')
    expect(text).toContain('Good 2')
    expect(text).toContain('OK 1')
    expect(text).toContain('OK 2')
    expect(text).toContain('Poor 1')
    expect(text).toContain('Poor 2')

    wrapper.unmount()
  })

  it('should display good quality profiles correctly', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert
    expect(wrapper.text()).toContain('Excellent Position')
    expect(wrapper.text()).toContain('Great Position')
    expect(wrapper.text()).toContain('95%')
    expect(wrapper.text()).toContain('85%')

    wrapper.unmount()
  })

  it('should display poor quality profiles correctly', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert
    expect(wrapper.text()).toContain('Needs Improvement')
    expect(wrapper.text()).toContain('Low Quality')
    expect(wrapper.text()).toContain('45%')
    expect(wrapper.text()).toContain('35%')

    wrapper.unmount()
  })

  it('should show recommendation alert when poor quality profiles exist', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert
    expect(wrapper.text()).toContain('Рекомендуется регенерация')
    expect(wrapper.text()).toContain('Найдено 1')

    wrapper.unmount()
  })

  it('should not show recommendation alert when no poor quality profiles', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert
    expect(wrapper.text()).not.toContain('Рекомендуется регенерация')

    wrapper.unmount()
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Act - Find and click regenerate button
    const regenerateButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Регенерировать')
    )

    expect(regenerateButton).toBeDefined()
    await regenerateButton!.trigger('click')
    await nextTick()

    // Assert
    expect(wrapper.emitted('regenerate')).toBeTruthy()

    const emitted = wrapper.emitted('regenerate')![0]
    expect(emitted[0]).toEqual(['1', '2']) // Position IDs

    wrapper.unmount()
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Act - Find and click close button
    const closeButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Закрыть')
    )

    expect(closeButton).toBeDefined()
    await closeButton!.trigger('click')
    await nextTick()

    // Assert
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])

    wrapper.unmount()
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Act
    const regenerateButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Регенерировать')
    )

    await regenerateButton!.trigger('click')
    await nextTick()

    // Assert - Dialog should be closed
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])

    wrapper.unmount()
  })

  it('should handle positions with missing quality scores', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert - Should treat as 0% (poor quality)
    expect(wrapper.text()).toContain('No Score')
    expect(wrapper.text()).toContain('0%')

    wrapper.unmount()
  })

  it('should correctly pluralize Russian words', async () => {
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

    for (const { count, positions } of testCases) {
      // Act
      const wrapper = mount(BulkQualityDialog, {
        props: {
          modelValue: true,
          positions
        },
        global: {
          plugins: [vuetify]
        },
        attachTo: document.body
      })
      await nextTick()

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

      wrapper.unmount()
    }
  })

  it('should disable tabs when groups are empty', async () => {
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
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    // Assert - Check that good quality position is displayed
    expect(wrapper.text()).toContain('Good')
    expect(wrapper.text()).toContain('95%')

    wrapper.unmount()
  })

  it('should show regenerate button only when poor quality profiles exist', async () => {
    // Test 1: With poor quality - button should exist
    const withPoor = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions: [createMockPosition('1', 'Poor', 0.45)]
      },
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    expect(withPoor.text()).toContain('Регенерировать')
    withPoor.unmount()

    // Test 2: Without poor quality - button should not exist
    const withoutPoor = mount(BulkQualityDialog, {
      props: {
        modelValue: true,
        positions: [createMockPosition('1', 'Good', 0.95)]
      },
      global: globalMountOptions,
      attachTo: document.body
    })
    await nextTick()

    expect(withoutPoor.text()).not.toContain('Регенерировать')
    withoutPoor.unmount()
  })
})

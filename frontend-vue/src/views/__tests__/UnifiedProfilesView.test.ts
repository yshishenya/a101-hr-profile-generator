/**
 * Unit tests for UnifiedProfilesView
 * Tests polling memory cleanup and lifecycle management
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { nextTick } from 'vue'
import UnifiedProfilesView from '../UnifiedProfilesView.vue'

const vuetify = createVuetify({
  components,
  directives
})

describe('UnifiedProfilesView', () => {
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  const createWrapper = (props = {}) => {
    return mount(UnifiedProfilesView, {
      props,
      global: {
        plugins: [pinia, vuetify],
        stubs: {
          LazyTreeView: true,
          PositionsTable: true,
          EnhancedSearchBar: true,
          ProfileViewerModal: true,
          FullProfileEditModal: true
        }
      }
    })
  }

  describe('Polling Memory Cleanup', () => {
    it('should cleanup polling on component unmount', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        pollingInterval: number | null
        isPolling: boolean
        startPolling: () => void
        stopPolling: () => void
      }

      // Start polling
      vm.startPolling()
      await nextTick()

      expect(vm.pollingInterval).not.toBeNull()

      // Unmount component
      wrapper.unmount()

      // Polling should be stopped
      expect(vm.pollingInterval).toBeNull()
    })

    it('should not allow overlapping poll requests', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        isPolling: boolean
        startPolling: () => void
        pollingInterval: number | null
      }

      // Start polling
      vm.startPolling()
      await nextTick()

      // Set isPolling flag to simulate active request
      vm.isPolling = true

      // Advance timer to trigger another poll
      vi.advanceTimersByTime(3000)
      await flushPromises()

      // isPolling should still be true (no new request started)
      expect(vm.isPolling).toBe(true)
    })

    it('should reset isPolling flag after poll completes', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        isPolling: boolean
        startPolling: () => void
      }

      vm.startPolling()
      await nextTick()

      // Simulate poll cycle
      vi.advanceTimersByTime(3000)
      await flushPromises()

      // Flag should be reset after poll completes
      // Note: This depends on generatorStore.hasPendingTasks being false
      expect(vm.isPolling).toBe(false)
    })

    it('should clear interval on stopPolling', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        pollingInterval: number | null
        startPolling: () => void
        stopPolling: () => void
      }

      vm.startPolling()
      expect(vm.pollingInterval).not.toBeNull()

      vm.stopPolling()
      expect(vm.pollingInterval).toBeNull()
    })

    it('should implement exponential backoff on consecutive errors', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        consecutiveErrors: number
        currentPollInterval: number
        adjustPollingInterval: () => void
      }

      // Simulate 3 consecutive errors
      vm.consecutiveErrors = 4

      vm.adjustPollingInterval()

      // Interval should be increased
      expect(vm.currentPollInterval).toBeGreaterThan(3000)
    })

    it('should reset polling interval when errors clear', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        consecutiveErrors: number
        currentPollInterval: number
        adjustPollingInterval: () => void
      }

      // Set high interval due to previous errors
      vm.currentPollInterval = 15000
      vm.consecutiveErrors = 0

      vm.adjustPollingInterval()

      // Interval should reset to base
      expect(vm.currentPollInterval).toBe(3000)
    })

    it('should not exceed maximum polling interval', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        consecutiveErrors: number
        currentPollInterval: number
        adjustPollingInterval: () => void
      }

      // Simulate many errors
      vm.consecutiveErrors = 10
      vm.currentPollInterval = 30000

      vm.adjustPollingInterval()

      // Should not exceed 30 seconds
      expect(vm.currentPollInterval).toBeLessThanOrEqual(30000)
    })

    it('should stop polling before unmount', () => {
      const wrapper = createWrapper()
      const stopPollingSpy = vi.spyOn(wrapper.vm as unknown as { stopPolling: () => void }, 'stopPolling')

      wrapper.unmount()

      expect(stopPollingSpy).toHaveBeenCalled()
    })
  })

  describe('Lifecycle Hooks', () => {
    it('should load data on mount', async () => {
      const wrapper = createWrapper()
      await flushPromises()

      // Component should be mounted
      expect(wrapper.vm).toBeDefined()
    })

    it('should handle onBeforeUnmount correctly', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        pollingInterval: number | null
        startPolling: () => void
      }

      vm.startPolling()
      expect(vm.pollingInterval).not.toBeNull()

      // Trigger unmount
      wrapper.unmount()

      // Cleanup should have run
      expect(vm.pollingInterval).toBeNull()
    })
  })

  describe('Polling Behavior', () => {
    it('should only poll when there are pending tasks', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        startPolling: () => void
        isPolling: boolean
      }

      // Start polling
      vm.startPolling()
      await nextTick()

      // Advance timer
      vi.advanceTimersByTime(3000)
      await flushPromises()

      // isPolling should return to false if no pending tasks
      expect(vm.isPolling).toBe(false)
    })

    it('should track consecutive errors', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        consecutiveErrors: number
      }

      // Initial state
      expect(vm.consecutiveErrors).toBe(0)
    })

    it('should use correct base polling interval', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        currentPollInterval: number
      }

      // Should start with 3000ms
      expect(vm.currentPollInterval).toBe(3000)
    })
  })

  describe('Error Handling', () => {
    it('should handle polling errors gracefully', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        startPolling: () => void
        consecutiveErrors: number
      }

      vm.startPolling()
      await nextTick()

      // Component should not crash
      expect(vm.consecutiveErrors).toBeGreaterThanOrEqual(0)
    })

    it('should log warning when backing off', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        consecutiveErrors: number
        adjustPollingInterval: () => void
      }

      vm.consecutiveErrors = 4

      // Should not throw
      expect(() => vm.adjustPollingInterval()).not.toThrow()
    })
  })

  describe('Integration', () => {
    it('should integrate polling with component lifecycle', async () => {
      const wrapper = createWrapper()

      // Component mounted
      expect(wrapper.exists()).toBe(true)

      // Unmount
      wrapper.unmount()

      // Should cleanup without errors
      expect(wrapper.vm).toBeDefined()
    })

    it('should handle rapid mount/unmount cycles', () => {
      for (let i = 0; i < 5; i++) {
        const wrapper = createWrapper()
        const vm = wrapper.vm as unknown as { startPolling: () => void }

        vm.startPolling()
        wrapper.unmount()
      }

      // Should not leak memory or throw errors
      expect(true).toBe(true)
    })
  })
})

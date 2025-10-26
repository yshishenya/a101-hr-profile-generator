/**
 * Unit tests for dashboard store
 * Tests state management, statistics fetching, error handling, and computed properties
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDashboardStore } from '../dashboard'
import dashboardService from '@/services/dashboard.service'
import type { DashboardStats } from '@/types/api'

// Mock dependencies
vi.mock('@/services/dashboard.service')
vi.mock('@/utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}))

describe('dashboardStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with empty state', () => {
      const store = useDashboardStore()

      expect(store.stats).toBe(null)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.lastFetchTime).toBe(null)
    })
  })

  describe('Computed Properties', () => {
    it('should compute formattedLastUpdated as "Never" when no last_updated', () => {
      const store = useDashboardStore()

      store.stats = null

      expect(store.formattedLastUpdated).toBe('Never')
    })

    it('should compute formattedLastUpdated correctly when last_updated exists', () => {
      const store = useDashboardStore()

      store.stats = createMockStats({
        last_updated: '2025-10-26T12:00:00Z'
      })

      const result = store.formattedLastUpdated
      // Result will depend on timezone, so just check it's not "Never"
      expect(result).not.toBe('Never')
      expect(result).toMatch(/\d{1,2}:\d{2}:\d{2}/)
    })

    it('should compute hasActiveGenerations as false when no active tasks', () => {
      const store = useDashboardStore()

      store.stats = createMockStats({ active_tasks_count: 0 })

      expect(store.hasActiveGenerations).toBe(false)
    })

    it('should compute hasActiveGenerations as true when active tasks exist', () => {
      const store = useDashboardStore()

      store.stats = createMockStats({ active_tasks_count: 3 })

      expect(store.hasActiveGenerations).toBe(true)
    })

    it('should handle null stats in hasActiveGenerations', () => {
      const store = useDashboardStore()

      store.stats = null

      expect(store.hasActiveGenerations).toBe(false)
    })
  })

  describe('fetchStats', () => {
    it('should fetch stats successfully with flat response', async () => {
      const store = useDashboardStore()
      const mockStats = createMockStats()

      vi.mocked(dashboardService.getStats).mockResolvedValue(mockStats)

      await store.fetchStats()

      expect(store.stats).toEqual(mockStats)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.lastFetchTime).toBeInstanceOf(Date)
    })

    it('should fetch stats successfully with nested response', async () => {
      const store = useDashboardStore()
      const mockNestedResponse = {
        summary: {
          positions_count: 100,
          profiles_count: 50,
          completion_percentage: 50.0,
          active_tasks_count: 5
        },
        metadata: {
          last_updated: '2025-10-26T12:00:00Z'
        }
      }

      vi.mocked(dashboardService.getStats).mockResolvedValue(mockNestedResponse as any)

      await store.fetchStats()

      expect(store.stats).toEqual({
        positions_count: 100,
        profiles_count: 50,
        completion_percentage: 50.0,
        active_tasks_count: 5,
        last_updated: '2025-10-26T12:00:00Z'
      })
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should handle wrapped response with data property', async () => {
      const store = useDashboardStore()
      const mockStats = createMockStats()
      const wrappedResponse = { data: mockStats }

      vi.mocked(dashboardService.getStats).mockResolvedValue(wrappedResponse as any)

      await store.fetchStats()

      expect(store.stats).toEqual(mockStats)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should set loading state during fetch', async () => {
      const store = useDashboardStore()

      vi.mocked(dashboardService.getStats).mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(createMockStats()), 100)
          })
      )

      const fetchPromise = store.fetchStats()

      // Check loading state is true during fetch
      expect(store.loading).toBe(true)

      await fetchPromise

      // Check loading state is false after fetch
      expect(store.loading).toBe(false)
    })

    it('should handle errors correctly', async () => {
      const store = useDashboardStore()
      const errorMessage = 'Network error'

      vi.mocked(dashboardService.getStats).mockRejectedValue(new Error(errorMessage))

      await expect(store.fetchStats()).rejects.toThrow(errorMessage)

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
      expect(store.stats).toBe(null)
    })

    it('should handle non-Error exceptions', async () => {
      const store = useDashboardStore()

      vi.mocked(dashboardService.getStats).mockRejectedValue('String error')

      await expect(store.fetchStats()).rejects.toBe('String error')

      expect(store.error).toBe('Failed to load dashboard statistics')
      expect(store.loading).toBe(false)
    })

    it('should clear previous error on successful fetch', async () => {
      const store = useDashboardStore()

      // First fetch fails
      vi.mocked(dashboardService.getStats).mockRejectedValueOnce(new Error('First error'))
      await expect(store.fetchStats()).rejects.toThrow()
      expect(store.error).toBe('First error')

      // Second fetch succeeds
      vi.mocked(dashboardService.getStats).mockResolvedValue(createMockStats())
      await store.fetchStats()

      expect(store.error).toBe(null)
      expect(store.stats).not.toBe(null)
    })

    it('should use nullish coalescing for missing fields in nested response', async () => {
      const store = useDashboardStore()
      const incompleteResponse = {
        summary: {
          positions_count: null as any,
          profiles_count: undefined as any,
          completion_percentage: 0,
          active_tasks_count: 0
        },
        metadata: {}
      }

      vi.mocked(dashboardService.getStats).mockResolvedValue(incompleteResponse as any)

      await store.fetchStats()

      expect(store.stats?.positions_count).toBe(0)
      expect(store.stats?.profiles_count).toBe(0)
      expect(store.stats?.last_updated).toBeUndefined()
    })
  })

  describe('refresh', () => {
    it('should call fetchStats', async () => {
      const store = useDashboardStore()
      const mockStats = createMockStats()

      vi.mocked(dashboardService.getStats).mockResolvedValue(mockStats)

      await store.refresh()

      expect(dashboardService.getStats).toHaveBeenCalledTimes(1)
      expect(store.stats).toEqual(mockStats)
    })
  })

  describe('clearError', () => {
    it('should clear error state', () => {
      const store = useDashboardStore()

      store.error = 'Some error'

      store.clearError()

      expect(store.error).toBe(null)
    })
  })

  describe('$reset', () => {
    it('should reset all state to initial values', async () => {
      const store = useDashboardStore()

      // Set some state
      vi.mocked(dashboardService.getStats).mockResolvedValue(createMockStats())
      await store.fetchStats()

      expect(store.stats).not.toBe(null)
      expect(store.lastFetchTime).not.toBe(null)

      // Reset
      store.$reset()

      expect(store.stats).toBe(null)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.lastFetchTime).toBe(null)
    })

    it('should reset error state', () => {
      const store = useDashboardStore()

      store.error = 'Some error'

      store.$reset()

      expect(store.error).toBe(null)
    })
  })

  describe('Edge Cases', () => {
    it('should handle concurrent fetch calls', async () => {
      const store = useDashboardStore()
      const mockStats = createMockStats()

      vi.mocked(dashboardService.getStats).mockResolvedValue(mockStats)

      // Start multiple fetches concurrently
      const [result1, result2, result3] = await Promise.all([
        store.fetchStats(),
        store.fetchStats(),
        store.fetchStats()
      ])

      // All should succeed
      expect(store.stats).toEqual(mockStats)
      expect(store.error).toBe(null)
      // API should be called 3 times
      expect(dashboardService.getStats).toHaveBeenCalledTimes(3)
    })

    it('should handle zero values correctly', async () => {
      const store = useDashboardStore()
      const zeroStats: DashboardStats = {
        positions_count: 0,
        profiles_count: 0,
        completion_percentage: 0,
        active_tasks_count: 0
      }

      vi.mocked(dashboardService.getStats).mockResolvedValue(zeroStats)

      await store.fetchStats()

      expect(store.stats).toEqual(zeroStats)
      expect(store.hasActiveGenerations).toBe(false)
    })

    it('should handle very large numbers', async () => {
      const store = useDashboardStore()
      const largeStats: DashboardStats = {
        positions_count: 999999999,
        profiles_count: 888888888,
        completion_percentage: 88.88,
        active_tasks_count: 100
      }

      vi.mocked(dashboardService.getStats).mockResolvedValue(largeStats)

      await store.fetchStats()

      expect(store.stats).toEqual(largeStats)
      expect(store.hasActiveGenerations).toBe(true)
    })
  })

  describe('State Consistency', () => {
    it('should maintain consistency after multiple operations', async () => {
      const store = useDashboardStore()

      // Fetch
      vi.mocked(dashboardService.getStats).mockResolvedValue(createMockStats())
      await store.fetchStats()
      const firstFetchTime = store.lastFetchTime

      // Wait a bit
      await new Promise((resolve) => setTimeout(resolve, 10))

      // Refresh
      await store.refresh()
      const secondFetchTime = store.lastFetchTime

      expect(secondFetchTime).not.toBe(firstFetchTime)
      expect(store.stats).not.toBe(null)
    })

    it('should not leave loading state stuck after error', async () => {
      const store = useDashboardStore()

      vi.mocked(dashboardService.getStats).mockRejectedValue(new Error('Test error'))

      try {
        await store.fetchStats()
      } catch {
        // Expected
      }

      expect(store.loading).toBe(false)
    })
  })
})

// Helper functions
function createMockStats(overrides?: Partial<DashboardStats>): DashboardStats {
  return {
    positions_count: 100,
    profiles_count: 50,
    completion_percentage: 50.0,
    active_tasks_count: 0,
    last_updated: '2025-10-26T12:00:00Z',
    ...overrides
  }
}

/**
 * Dashboard Store - Single source of truth for application statistics
 *
 * This store provides unified access to dashboard statistics across all views.
 * All pages should use this store instead of loading stats locally.
 *
 * @example
 * const dashboardStore = useDashboardStore()
 * await dashboardStore.fetchStats()
 * console.log(dashboardStore.stats?.positions_count)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import dashboardService from '@/services/dashboard.service'
import type { DashboardStats } from '@/types/api'
import { isDashboardStatsResponse } from '@/types/api'
import { logger } from '@/utils/logger'

/**
 * Type guard to check if response has a data property
 */
function hasDataProperty<T>(obj: unknown): obj is { data: T } {
  return typeof obj === 'object' && obj !== null && 'data' in obj
}

export const useDashboardStore = defineStore('dashboard', () => {
  // Configuration
  const CACHE_TTL = 5000 // 5 seconds cache TTL
  const REQUEST_TIMEOUT = 15000 // 15 seconds request timeout

  // State
  const stats = ref<DashboardStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchTime = ref<Date | null>(null)
  const cacheTimestamp = ref<number | null>(null)

  // Computed
  const formattedLastUpdated = computed(() => {
    if (!stats.value?.last_updated) return 'Never'
    const date = new Date(stats.value.last_updated)
    return date.toLocaleTimeString()
  })

  const hasActiveGenerations = computed(() => {
    return (stats.value?.active_tasks_count ?? 0) > 0
  })

  const coverageProgress = computed(() => {
    const total = stats.value?.positions_count || 1
    const generated = stats.value?.profiles_count || 0
    return Math.min((generated / total) * 100, 100) // Cap at 100%
  })

  const isCacheFresh = computed(() => {
    if (!cacheTimestamp.value) return false
    const now = Date.now()
    return (now - cacheTimestamp.value) < CACHE_TTL
  })

  /**
   * Fetch dashboard statistics from API
   * Implements cache-aside pattern with TTL
   *
   * @param force - Force refresh bypassing cache
   */
  async function fetchStats(force = false): Promise<void> {
    // Check cache freshness - return early if cache is valid
    if (!force && isCacheFresh.value && stats.value) {
      logger.debug('Using cached dashboard stats', {
        cacheAge: Date.now() - (cacheTimestamp.value ?? 0),
        ttl: CACHE_TTL
      })
      return
    }

    try {
      loading.value = true
      error.value = null

      // Add request timeout protection
      const fetchPromise = dashboardService.getStats()
      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Request timeout')), REQUEST_TIMEOUT)
      )

      const response = await Promise.race([fetchPromise, timeoutPromise])

      // Handle both possible response structures safely using type guard
      // Backend may wrap response in { data: ... } or return directly
      const rawData = hasDataProperty(response) ? response.data : response

      // Use type guard to check for nested structure
      if (isDashboardStatsResponse(rawData)) {
        // Backend returns nested structure with summary and metadata
        stats.value = {
          positions_count: rawData.summary.positions_count ?? 0,
          profiles_count: rawData.summary.profiles_count ?? 0,
          completion_percentage: rawData.summary.completion_percentage ?? 0,
          active_tasks_count: rawData.summary.active_tasks_count ?? 0,
          last_updated: rawData.metadata?.last_updated
        }
      } else {
        // Fallback: assume data is already in flat DashboardStats format
        stats.value = rawData as DashboardStats
      }

      // Update cache timestamp
      cacheTimestamp.value = Date.now()
      lastFetchTime.value = new Date()
      logger.info('Dashboard stats fetched successfully')
    } catch (err: unknown) {
      logger.error('Failed to fetch dashboard stats', err)

      // Safe error message extraction
      const errorMessage = err instanceof Error
        ? err.message
        : 'Failed to load dashboard statistics'

      error.value = errorMessage
      throw err // Re-throw for caller to handle
    } finally {
      loading.value = false
    }
  }

  /**
   * Refresh stats - force bypass cache
   */
  async function refresh(): Promise<void> {
    await fetchStats(true) // Force refresh
  }

  /**
   * Clear error state
   */
  function clearError(): void {
    error.value = null
  }

  /**
   * Reset store to initial state
   */
  function $reset(): void {
    stats.value = null
    loading.value = false
    error.value = null
    lastFetchTime.value = null
    cacheTimestamp.value = null
  }

  return {
    // State
    stats,
    loading,
    error,
    lastFetchTime,

    // Computed
    formattedLastUpdated,
    hasActiveGenerations,
    coverageProgress,
    isCacheFresh,

    // Actions
    fetchStats,
    refresh,
    clearError,
    $reset
  }
})

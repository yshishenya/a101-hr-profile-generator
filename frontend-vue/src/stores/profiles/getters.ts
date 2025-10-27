/**
 * Computed properties for profiles store
 * Contains all derived state and getters
 */

import { computed } from 'vue'
import type { ProfileStatistics } from '@/types/unified'
import {
  pagination,
  profiles,
  filters,
  unifiedPositions,
  unifiedFilters
} from './state'

/**
 * Total number of profiles across all pages
 */
export const totalProfiles = computed(() => pagination.value.total)

/**
 * Current page number
 */
export const currentPage = computed(() => pagination.value.page)

/**
 * Whether there are more pages available
 */
export const hasMore = computed(() => pagination.value.has_next)

/**
 * Whether there are previous pages available
 */
export const hasPrevious = computed(() => pagination.value.has_prev)

/**
 * Number of profiles on current page
 */
export const profilesCount = computed(() => profiles.value.length)

/**
 * Whether any filters are applied
 */
export const hasActiveFilters = computed(() => {
  return !!(
    filters.value.department ||
    filters.value.position ||
    filters.value.search ||
    (filters.value.status && filters.value.status !== 'all')
  )
})

/**
 * Filtered unified positions based on active filters
 */
export const filteredPositions = computed(() => {
  let result = unifiedPositions.value

  // Search filter
  if (unifiedFilters.value.search) {
    const search = unifiedFilters.value.search.toLowerCase()
    result = result.filter(p =>
      p.position_name.toLowerCase().includes(search) ||
      p.department_name.toLowerCase().includes(search)
    )
  }

  // Department filter (multi-select)
  if (unifiedFilters.value.departments.length > 0) {
    result = result.filter(p =>
      unifiedFilters.value.departments.includes(p.department_name)
    )
  }

  // Status filter
  if (unifiedFilters.value.status !== 'all') {
    result = result.filter(p => p.status === unifiedFilters.value.status)
  }

  return result
})

/**
 * Statistics for unified overview
 */
export const statistics = computed<ProfileStatistics>(() => {
  const total = unifiedPositions.value.length
  const generated = unifiedPositions.value.filter(p => p.status === 'generated').length
  const generating = unifiedPositions.value.filter(p => p.status === 'generating').length
  const notGenerated = unifiedPositions.value.filter(p => p.status === 'not_generated').length

  return {
    total_positions: total,
    generated_count: generated,
    generating_count: generating,
    not_generated_count: notGenerated,
    coverage_percentage: total > 0 ? Math.round((generated / total) * 100) : 0,
    last_updated: new Date().toISOString()
  }
})

/**
 * Unique departments from unified positions
 */
export const departments = computed(() => {
  const depts = new Set(unifiedPositions.value.map(p => p.department_name))
  return Array.from(depts).sort()
})

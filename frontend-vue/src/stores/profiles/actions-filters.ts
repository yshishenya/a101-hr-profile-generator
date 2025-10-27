/**
 * Filter and pagination management for profiles store
 * Contains filter operations and page navigation
 */

import type { FilterParams } from '@/types/api'
import { ProfileError, DEFAULT_PAGE } from './types'
import { pagination, filters } from './state'
import { loadProfiles } from './actions-crud'

/**
 * Set active filters and reload profiles
 *
 * @param newFilters - Filters to apply
 *
 * @example
 * ```typescript
 * setFilters({ department: 'IT', status: 'completed' })
 * ```
 */
export async function setFilters(newFilters: Partial<FilterParams>): Promise<void> {
  filters.value = {
    ...filters.value,
    ...newFilters
  }

  // Reset to first page when filters change
  pagination.value.page = DEFAULT_PAGE

  await loadProfiles()
}

/**
 * Clear all active filters and reload
 */
export async function clearFilters(): Promise<void> {
  filters.value = {
    department: undefined,
    position: undefined,
    search: undefined,
    status: undefined
  }

  pagination.value.page = DEFAULT_PAGE
  await loadProfiles()
}

/**
 * Go to specific page
 *
 * @param page - Page number (1-indexed)
 */
export async function goToPage(page: number): Promise<void> {
  if (page < 1 || page > pagination.value.total_pages) {
    throw new ProfileError('Invalid page number', 'VALIDATION_ERROR')
  }

  pagination.value.page = page
  await loadProfiles()
}

/**
 * Go to next page
 */
export async function nextPage(): Promise<void> {
  if (!pagination.value.has_next) {
    throw new ProfileError('No next page available', 'VALIDATION_ERROR')
  }

  await goToPage(pagination.value.page + 1)
}

/**
 * Go to previous page
 */
export async function previousPage(): Promise<void> {
  if (!pagination.value.has_prev) {
    throw new ProfileError('No previous page available', 'VALIDATION_ERROR')
  }

  await goToPage(pagination.value.page - 1)
}

/**
 * Apply advanced filters to unified positions (client-side)
 * Filters positions based on search, departments, status, date range, and quality range
 *
 * @param positions - Array of unified positions to filter
 * @returns Filtered array of positions
 *
 * @example
 * ```typescript
 * const filtered = applyAdvancedFilters(allPositions)
 * console.log(`Filtered ${filtered.length} positions`)
 * ```
 */
export function applyAdvancedFilters<T extends {
  position_name: string
  department_name: string
  department_path: string
  status: string
  created_at?: string
  quality_score?: number
}>(positions: T[]): T[] {
  const { unifiedFilters } = require('./state')

  let filtered = [...positions]

  // Search filter (position name, department name, department path)
  if (unifiedFilters.value.search) {
    const searchLower = unifiedFilters.value.search.toLowerCase()
    filtered = filtered.filter(p =>
      p.position_name.toLowerCase().includes(searchLower) ||
      p.department_name.toLowerCase().includes(searchLower) ||
      p.department_path.toLowerCase().includes(searchLower)
    )
  }

  // Department multi-select filter
  if (unifiedFilters.value.departments.length > 0) {
    filtered = filtered.filter(p =>
      unifiedFilters.value.departments.includes(p.department_name)
    )
  }

  // Status filter
  if (unifiedFilters.value.status !== 'all') {
    filtered = filtered.filter(p => p.status === unifiedFilters.value.status)
  }

  // Date range filter
  if (unifiedFilters.value.dateRange) {
    const { from, to } = unifiedFilters.value.dateRange

    filtered = filtered.filter(p => {
      if (!p.created_at) return false

      const itemDate = new Date(p.created_at)

      if (from && to) {
        const fromDate = new Date(from)
        const toDate = new Date(to)
        return itemDate >= fromDate && itemDate <= toDate
      } else if (from) {
        const fromDate = new Date(from)
        return itemDate >= fromDate
      } else if (to) {
        const toDate = new Date(to)
        return itemDate <= toDate
      }

      return true
    })
  }

  return filtered
}

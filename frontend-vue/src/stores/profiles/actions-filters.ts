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

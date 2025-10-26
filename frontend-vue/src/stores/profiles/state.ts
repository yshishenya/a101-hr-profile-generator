/**
 * State management for profiles store
 * Contains all reactive state and initial values
 */

import { ref } from 'vue'
import type { Ref } from 'vue'
import type { Profile, ProfileDetail } from '@/types/profile'
import type { FilterParams } from '@/types/api'
import type { UnifiedPosition, ViewMode, ProfileFilters } from '@/types/unified'
import { DEFAULT_PAGE_SIZE, DEFAULT_PAGE } from './types'

/**
 * Unified positions (combines catalog + profiles + tasks)
 */
export const unifiedPositions: Ref<UnifiedPosition[]> = ref([])

/**
 * Legacy profiles array (for backward compatibility)
 */
export const profiles: Ref<Profile[]> = ref([])

/**
 * Currently loaded profile detail
 */
export const currentProfile: Ref<ProfileDetail | null> = ref(null)

/**
 * Loading state for async operations
 */
export const loading = ref<boolean>(false)

/**
 * Error message from last failed operation
 */
export const error = ref<string | null>(null)

/**
 * View mode for unified interface (table or cards)
 */
export const viewMode: Ref<ViewMode> = ref('table')

/**
 * Unified filters for positions
 */
export const unifiedFilters: Ref<ProfileFilters> = ref({
  search: '',
  department: null,
  status: 'all'
})

/**
 * Pagination state (legacy)
 */
export const pagination = ref({
  page: DEFAULT_PAGE,
  limit: DEFAULT_PAGE_SIZE,
  total: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false
})

/**
 * Filters state (legacy)
 */
export const filters = ref<FilterParams>({
  department: undefined,
  position: undefined,
  search: undefined,
  status: undefined
})

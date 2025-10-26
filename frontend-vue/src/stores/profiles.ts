/**
 * Profiles Store - Unified profiles and positions management
 * Handles unified view of all positions with their profile status
 * Combines catalog data, profile data, and generation tasks
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import type { AxiosError } from 'axios'
import profileService from '@/services/profile.service'
import { logger } from '@/utils/logger'
import { useCatalogStore } from './catalog'
import { useGeneratorStore } from './generator'
import type {
  Profile,
  ProfileDetail,
  ProfilesListResponse,
  ProfileUpdateRequest
} from '@/types/profile'
import type { PaginationParams, FilterParams } from '@/types/api'
import type {
  UnifiedPosition,
  ViewMode,
  ProfileFilters,
  PositionActions,
  ProfileStatistics
} from '@/types/unified'

// Constants
const DEFAULT_PAGE_SIZE = 20
const DEFAULT_PAGE = 1

// Custom error class for profile operations
class ProfileError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly originalError?: unknown
  ) {
    super(message)
    this.name = 'ProfileError'
  }
}

export const useProfilesStore = defineStore('profiles', () => {
  const catalogStore = useCatalogStore()
  const generatorStore = useGeneratorStore()

  // ===== State =====

  // Unified positions (combines catalog + profiles + tasks)
  const unifiedPositions: Ref<UnifiedPosition[]> = ref([])

  // Legacy state (for backward compatibility)
  const profiles: Ref<Profile[]> = ref([])
  const currentProfile: Ref<ProfileDetail | null> = ref(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // View mode for unified interface
  const viewMode: Ref<ViewMode> = ref('table')

  // Unified filters
  const unifiedFilters: Ref<ProfileFilters> = ref({
    search: '',
    department: null,
    status: 'all'
  })

  // Pagination state (legacy)
  const pagination = ref({
    page: DEFAULT_PAGE,
    limit: DEFAULT_PAGE_SIZE,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  })

  // Filters state (legacy)
  const filters = ref<FilterParams>({
    department: undefined,
    position: undefined,
    search: undefined,
    status: undefined
  })

  // ===== Computed =====

  /**
   * Total number of profiles across all pages
   */
  const totalProfiles = computed(() => pagination.value.total)

  /**
   * Current page number
   */
  const currentPage = computed(() => pagination.value.page)

  /**
   * Whether there are more pages available
   */
  const hasMore = computed(() => pagination.value.has_next)

  /**
   * Whether there are previous pages available
   */
  const hasPrevious = computed(() => pagination.value.has_prev)

  /**
   * Number of profiles on current page
   */
  const profilesCount = computed(() => profiles.value.length)

  /**
   * Whether any filters are applied
   */
  const hasActiveFilters = computed(() => {
    return !!(
      filters.value.department ||
      filters.value.position ||
      filters.value.search ||
      (filters.value.status && filters.value.status !== 'all')
    )
  })

  // ===== Unified Computed =====

  /**
   * Filtered unified positions based on active filters
   */
  const filteredPositions = computed(() => {
    let result = unifiedPositions.value

    // Search filter
    if (unifiedFilters.value.search) {
      const search = unifiedFilters.value.search.toLowerCase()
      result = result.filter(p =>
        p.position_name.toLowerCase().includes(search) ||
        p.department_name.toLowerCase().includes(search)
      )
    }

    // Department filter
    if (unifiedFilters.value.department) {
      result = result.filter(p =>
        p.department_name === unifiedFilters.value.department
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
  const statistics = computed<ProfileStatistics>(() => {
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
  const departments = computed(() => {
    const depts = new Set(unifiedPositions.value.map(p => p.department_name))
    return Array.from(depts).sort()
  })

  // ===== Actions =====

  /**
   * Load profiles with pagination and filters
   *
   * @param options - Override pagination/filter options
   * @throws ProfileError if loading fails
   *
   * @example
   * ```typescript
   * await loadProfiles({ page: 2, department: 'IT' })
   * ```
   */
  async function loadProfiles(options?: Partial<PaginationParams & FilterParams>): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const params = {
        page: options?.page ?? pagination.value.page,
        limit: options?.limit ?? pagination.value.limit,
        department: options?.department ?? filters.value.department,
        position: options?.position ?? filters.value.position,
        search: options?.search ?? filters.value.search,
        status: options?.status ?? filters.value.status
      }

      // Remove undefined values
      const cleanParams = Object.fromEntries(
        Object.entries(params).filter(([_, v]) => v !== undefined)
      )

      const response: ProfilesListResponse = await profileService.listProfiles(cleanParams)

      // Update state
      profiles.value = response.profiles
      pagination.value = response.pagination

      // Store filters that were actually applied
      if (response.filters_applied) {
        filters.value = {
          department: response.filters_applied.department || undefined,
          position: response.filters_applied.position || undefined,
          search: response.filters_applied.search || undefined,
          status: response.filters_applied.status || undefined
        }
      }

      loading.value = false
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to load profiles'
      loading.value = false

      throw new ProfileError(
        error.value,
        'LOAD_FAILED',
        err
      )
    }
  }

  /**
   * Load single profile by ID
   *
   * @param id - Profile ID
   * @throws ProfileError if loading fails
   *
   * @example
   * ```typescript
   * await loadProfile('prof_123')
   * console.log(currentProfile.value?.profile)
   * ```
   */
  async function loadProfile(id: string): Promise<void> {
    if (!id?.trim()) {
      throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
    }

    loading.value = true
    error.value = null

    try {
      const profile = await profileService.getProfile(id)
      currentProfile.value = profile
      loading.value = false
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to load profile'
      loading.value = false

      throw new ProfileError(
        error.value,
        axiosError.response?.status === 404 ? 'NOT_FOUND' : 'LOAD_FAILED',
        err
      )
    }
  }

  /**
   * Update profile metadata or content
   * Automatically refreshes profile after update
   *
   * @param id - Profile ID
   * @param data - Fields to update
   * @throws ProfileError if update fails
   *
   * @example
   * ```typescript
   * await updateProfile('prof_123', {
   *   employee_name: 'Иван Петров',
   *   status: 'completed'
   * })
   * ```
   */
  async function updateProfile(id: string, data: ProfileUpdateRequest): Promise<void> {
    if (!id?.trim()) {
      throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
    }

    loading.value = true
    error.value = null

    try {
      await profileService.updateProfile(id, data)

      // Refresh the profile if it's currently loaded
      if (currentProfile.value?.profile_id === id) {
        await loadProfile(id)
      }

      // Refresh list if profile is in current page
      const profileIndex = profiles.value.findIndex(p => p.profile_id === id)
      if (profileIndex !== -1) {
        await loadProfiles()
      }

      loading.value = false
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to update profile'
      loading.value = false

      throw new ProfileError(
        error.value,
        'UPDATE_FAILED',
        err
      )
    }
  }

  /**
   * Archive (soft delete) a profile
   * Removes profile from list after archiving
   *
   * @param id - Profile ID to archive
   * @throws ProfileError if archiving fails
   *
   * @example
   * ```typescript
   * await deleteProfile('prof_123')
   * ```
   */
  async function deleteProfile(id: string): Promise<void> {
    if (!id?.trim()) {
      throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
    }

    loading.value = true
    error.value = null

    try {
      await profileService.archiveProfile(id)

      // Remove from local state
      profiles.value = profiles.value.filter(p => p.profile_id !== id)

      // Clear current profile if it was deleted
      if (currentProfile.value?.profile_id === id) {
        currentProfile.value = null
      }

      // Update pagination total
      if (pagination.value.total > 0) {
        pagination.value.total--
      }

      loading.value = false
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to delete profile'
      loading.value = false

      throw new ProfileError(
        error.value,
        'DELETE_FAILED',
        err
      )
    }
  }

  /**
   * Download profile in specified format
   * Creates temporary download link
   *
   * @param id - Profile ID
   * @param format - Download format (json, md, docx)
   * @throws ProfileError if download fails
   *
   * @example
   * ```typescript
   * await downloadProfile('prof_123', 'json')
   * ```
   */
  async function downloadProfile(id: string, format: 'json' | 'md' | 'docx'): Promise<void> {
    if (!id?.trim()) {
      throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
    }

    try {
      let blob: Blob

      switch (format) {
        case 'json':
          blob = await profileService.downloadJSON(id)
          break
        case 'md':
          blob = await profileService.downloadMarkdown(id)
          break
        case 'docx':
          blob = await profileService.downloadDOCX(id)
          break
        default:
          throw new ProfileError(`Unsupported format: ${format}`, 'VALIDATION_ERROR')
      }

      // Create download link
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `profile_${id}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      const errorMessage = axiosError.response?.data?.message || `Failed to download ${format.toUpperCase()}`

      throw new ProfileError(
        errorMessage,
        'DOWNLOAD_FAILED',
        err
      )
    }
  }

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
  async function setFilters(newFilters: Partial<FilterParams>): Promise<void> {
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
  async function clearFilters(): Promise<void> {
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
  async function goToPage(page: number): Promise<void> {
    if (page < 1 || page > pagination.value.total_pages) {
      throw new ProfileError('Invalid page number', 'VALIDATION_ERROR')
    }

    pagination.value.page = page
    await loadProfiles()
  }

  /**
   * Go to next page
   */
  async function nextPage(): Promise<void> {
    if (!pagination.value.has_next) {
      throw new ProfileError('No next page available', 'VALIDATION_ERROR')
    }

    await goToPage(pagination.value.page + 1)
  }

  /**
   * Go to previous page
   */
  async function previousPage(): Promise<void> {
    if (!pagination.value.has_prev) {
      throw new ProfileError('No previous page available', 'VALIDATION_ERROR')
    }

    await goToPage(pagination.value.page - 1)
  }

  /**
   * Clear any error messages
   */
  function clearError(): void {
    error.value = null
  }

  /**
   * Reset current profile
   * Used when navigating away from detail view
   */
  function clearCurrentProfile(): void {
    currentProfile.value = null
  }

  /**
   * Load unified data (positions + profiles + tasks)
   * Combines data from catalog, profiles, and generation tasks
   * This is the main method for unified interface
   *
   * @example
   * ```typescript
   * await loadUnifiedData()
   * console.log(filteredPositions.value) // All positions with status
   * ```
   */
  async function loadUnifiedData(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      // 1. Load catalog positions (ensures data is loaded)
      await catalogStore.loadSearchableItems()
      const catalogItems = catalogStore.searchableItems

      // 2. Get active generation tasks
      const activeTasks = generatorStore.activeTasks

      // 3. Merge data into unified structure
      unifiedPositions.value = catalogItems.map(item => {
        // Find active task for this position
        const taskEntry = Array.from(activeTasks.entries()).find(
          ([_, task]) => task.position_id === item.position_id
        )
        const task = taskEntry?.[1]

        // Determine status
        const status = determinePositionStatus(item, task)

        // Compute available actions
        const actions = computeActions(status)

        return {
          // Position metadata from catalog
          position_id: item.position_id,
          position_name: item.position_name,
          business_unit_id: item.business_unit_id,
          business_unit_name: item.business_unit_name,
          department_name: item.business_unit_name,
          department_path: item.department_path,

          // Status
          status,

          // Profile data (if exists)
          profile_id: item.profile_id,
          quality_score: undefined, // TODO(backend): Add quality_score to /api/organization/positions response (Week 6)
          created_at: undefined, // TODO(backend): Add created_at to /api/organization/positions response (Week 6)

          // Task data (if generating)
          task_id: task?.task_id,
          progress: task?.progress,
          current_step: task?.current_step,
          estimated_duration: task?.estimated_duration,

          // Actions
          actions
        }
      })
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to load unified data'

      throw new ProfileError(
        error.value,
        'LOAD_FAILED',
        err
      )
    } finally {
      loading.value = false
    }
  }

  /**
   * Determine position status from catalog and task data
   *
   * @param item - Catalog position item with profile_exists flag
   * @param task - Optional generation task data
   * @returns Position status: 'generated', 'not_generated', or 'generating'
   *
   * @example
   * ```typescript
   * const status = determinePositionStatus(catalogItem, activeTask)
   * if (status === 'generating') {
   *   // Show progress indicator
   * }
   * ```
   */
  function determinePositionStatus(
    item: any,
    task?: any
  ): 'generated' | 'not_generated' | 'generating' {
    // Check if currently generating
    if (task && (task.status === 'queued' || task.status === 'processing')) {
      return 'generating'
    }

    // Check if profile exists
    if (item.profile_exists) {
      return 'generated'
    }

    return 'not_generated'
  }

  /**
   * Compute available actions based on position status
   *
   * @param status - Current position status
   * @returns Object with boolean flags for each available action
   *
   * @example
   * ```typescript
   * const actions = computeActions('generated')
   * // { canView: true, canGenerate: false, canDownload: true, ... }
   * ```
   */
  function computeActions(status: 'generated' | 'not_generated' | 'generating'): PositionActions {
    return {
      canView: status === 'generated',
      canGenerate: status === 'not_generated',
      canDownload: status === 'generated',
      canEdit: status === 'generated',
      canCancel: status === 'generating',
      canRegenerate: status === 'generated'
    }
  }

  /**
   * Bulk generate profiles for selected positions
   * Filters out positions that are already generated or generating
   * and starts generation tasks for remaining positions
   *
   * @param positionIds - Array of position IDs to generate profiles for
   * @returns Promise resolving to array of created task IDs
   * @throws {ProfileError} If generation fails
   *
   * @example
   * ```typescript
   * const selectedIds = ['pos_1', 'pos_2', 'pos_3']
   * const taskIds = await bulkGenerate(selectedIds)
   * console.log(`Started ${taskIds.length} generation tasks`)
   * ```
   */
  async function bulkGenerate(positionIds: string[]): Promise<string[]> {
    // Filter to get only not_generated positions
    const positions = unifiedPositions.value
      .filter(p => positionIds.includes(p.position_id) && p.status === 'not_generated')
      .map(p => ({
        position_id: p.position_id,
        position_name: p.position_name,
        business_unit_id: p.business_unit_id,
        business_unit_name: p.business_unit_name,
        department_id: p.department_id,
        department_name: p.department_name,
        department_path: p.department_path,
        profile_exists: false
      }))

    if (positions.length === 0) {
      return []
    }

    try {
      const taskIds = await generatorStore.startBulkGeneration(positions)

      // Reload unified data to reflect new generation tasks
      await loadUnifiedData()

      return taskIds
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to start bulk generation'
      throw new ProfileError(error.value, 'BULK_GENERATE_FAILED', err)
    }
  }

  /**
   * Bulk cancel generation tasks for selected positions
   * Filters positions to find those currently generating
   * and cancels their tasks in parallel
   *
   * @param positionIds - Array of position IDs whose generation tasks should be cancelled
   * @returns Promise that resolves when all cancellations complete
   *
   * @example
   * ```typescript
   * const selectedIds = ['pos_1', 'pos_2', 'pos_3']
   * await bulkCancel(selectedIds)
   * console.log('All generation tasks cancelled')
   * ```
   */
  async function bulkCancel(positionIds: string[]): Promise<void> {
    // Filter to get only generating positions
    const generatingPositions = unifiedPositions.value.filter(
      p => positionIds.includes(p.position_id) && p.status === 'generating' && p.task_id
    )

    if (generatingPositions.length === 0) {
      return
    }

    // Cancel all tasks in parallel
    const cancelPromises = generatingPositions.map(p => {
      if (p.task_id) {
        return generatorStore.cancelTask(p.task_id).catch(err => {
          logger.error(`Failed to cancel task ${p.task_id}`, err)
        })
      }
      return Promise.resolve()
    })

    await Promise.all(cancelPromises)

    // Reload unified data to reflect cancelled tasks
    await loadUnifiedData()
  }

  /**
   * Reset all state to defaults
   */
  function reset(): void {
    profiles.value = []
    currentProfile.value = null
    unifiedPositions.value = []
    loading.value = false
    error.value = null
    pagination.value = {
      page: DEFAULT_PAGE,
      limit: DEFAULT_PAGE_SIZE,
      total: 0,
      total_pages: 0,
      has_next: false,
      has_prev: false
    }
    filters.value = {
      department: undefined,
      position: undefined,
      search: undefined,
      status: undefined
    }
    unifiedFilters.value = {
      search: '',
      department: null,
      status: 'all'
    }
  }

  return {
    // Legacy state (for backward compatibility)
    profiles,
    currentProfile,
    loading,
    error,
    pagination,
    filters,

    // Unified state
    unifiedPositions,
    viewMode,
    unifiedFilters,

    // Legacy computed
    totalProfiles,
    currentPage,
    hasMore,
    hasPrevious,
    profilesCount,
    hasActiveFilters,

    // Unified computed
    filteredPositions,
    statistics,
    departments,

    // Legacy actions
    loadProfiles,
    loadProfile,
    updateProfile,
    deleteProfile,
    downloadProfile,
    setFilters,
    clearFilters,
    goToPage,
    nextPage,
    previousPage,
    clearError,
    clearCurrentProfile,

    // Unified actions
    loadUnifiedData,
    bulkGenerate,
    bulkCancel,

    reset
  }
})

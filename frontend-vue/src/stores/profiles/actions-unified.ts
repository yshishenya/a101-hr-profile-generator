/**
 * Unified view logic for profiles store
 * Combines catalog positions, profiles, and generation tasks
 */

import type { AxiosError } from 'axios'
import { useCatalogStore } from '@/stores/catalog'
import type { SearchableItem } from '@/stores/catalog'
import { useGeneratorStore } from '@/stores/generator'
import type { GenerationTask } from '@/stores/generator'
import type { PositionActions } from '@/types/unified'
import { logger } from '@/utils/logger'
import { ProfileError } from './types'
import { unifiedPositions, loading, error } from './state'

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
export async function loadUnifiedData(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const catalogStore = useCatalogStore()
    const generatorStore = useGeneratorStore()

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
export function determinePositionStatus(
  item: SearchableItem,
  task?: GenerationTask
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
export function computeActions(status: 'generated' | 'not_generated' | 'generating'): PositionActions {
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
export async function bulkGenerate(positionIds: string[]): Promise<string[]> {
  const generatorStore = useGeneratorStore()

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
export async function bulkCancel(positionIds: string[]): Promise<void> {
  const generatorStore = useGeneratorStore()

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

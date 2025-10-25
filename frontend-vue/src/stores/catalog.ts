/**
 * Catalog store
 * Manages position catalog data with in-memory caching
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import catalogService from '@/services/catalog.service'
import type { Position } from '@/types/profile'

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const positions = ref<Position[]>([])
  const isLoaded = ref<boolean>(false)
  const loading = ref<boolean>(false)

  // Computed
  const positionsCount = computed(() => positions.value.length)

  /**
   * Load positions from backend
   * Only loads once - subsequent calls use cached data
   */
  async function loadPositions(): Promise<void> {
    // Skip if already loaded
    if (isLoaded.value) {
      return
    }

    // Skip if currently loading
    if (loading.value) {
      return
    }

    loading.value = true

    try {
      const data = await catalogService.getPositions()
      positions.value = data
      isLoaded.value = true
    } catch (err) {
      if (import.meta.env.DEV) {
        console.error('Failed to load positions:', err)
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Search positions by query string
   * Performs client-side filtering on cached positions
   * @param query - Search query (case-insensitive)
   * @returns Filtered positions matching the query
   */
  function searchPositions(query: string): Position[] {
    if (!query || query.trim() === '') {
      return positions.value
    }

    const lowerQuery = query.toLowerCase().trim()

    return positions.value.filter(position => {
      // Search in position name
      if (position.name.toLowerCase().includes(lowerQuery)) {
        return true
      }

      // Search in department name
      if (position.department.toLowerCase().includes(lowerQuery)) {
        return true
      }

      // Search in full path
      if (position.full_path.toLowerCase().includes(lowerQuery)) {
        return true
      }

      return false
    })
  }

  /**
   * Get positions by department
   * @param department - Department name
   * @returns Positions in the specified department
   */
  function getPositionsByDepartment(department: string): Position[] {
    return positions.value.filter(
      position => position.department === department
    )
  }

  /**
   * Get unique departments from positions
   * @returns Array of unique department names
   */
  function getDepartments(): string[] {
    const departments = new Set(
      positions.value.map(position => position.department)
    )
    return Array.from(departments).sort()
  }

  /**
   * Force reload positions from backend
   * Clears cache and loads fresh data
   */
  async function reloadPositions(): Promise<void> {
    isLoaded.value = false
    await loadPositions()
  }

  return {
    // State
    positions,
    isLoaded,
    loading,

    // Computed
    positionsCount,

    // Actions
    loadPositions,
    searchPositions,
    getPositionsByDepartment,
    getDepartments,
    reloadPositions,
  }
})

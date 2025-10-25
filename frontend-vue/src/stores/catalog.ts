/**
 * Catalog store
 * Manages organization catalog data with localStorage caching
 * Supports search items, organization tree, and departments
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import api from '@/services/api'

// Constants
const CACHE_KEY = 'org_catalog_cache'
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000 // 24 hours

// Types
export interface SearchableItem {
  position_id: string
  position_name: string
  business_unit_id: string
  business_unit_name: string
  department_id?: string
  department_name?: string
  department_path: string
  profile_exists: boolean
  profile_id?: number
}

export interface Department {
  id: string
  name: string
  type: string
}

export interface OrganizationNode {
  id: string
  name: string
  type: 'division' | 'block' | 'department' | 'unit'
  children?: OrganizationNode[]
  positions?: SearchableItem[]
  profile_count?: number
  total_positions?: number
}

interface OrganizationStructureResponse {
  id: string
  name: string
  type?: string
  children?: OrganizationStructureResponse[]
}

class CatalogError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly originalError?: unknown
  ) {
    super(message)
    this.name = 'CatalogError'
  }
}

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const searchableItems: Ref<SearchableItem[]> = ref([])
  const departments: Ref<Department[]> = ref([])
  const organizationTree: Ref<OrganizationNode[]> = ref([])
  const isLoading = ref(false)
  const error: Ref<string | null> = ref(null)
  const lastUpdated: Ref<Date | null> = ref(null)

  // Computed
  const totalPositions = computed(() => searchableItems.value.length)

  const positionsWithProfiles = computed(() => {
    return searchableItems.value.filter(item => item.profile_exists).length
  })

  const coveragePercentage = computed(() => {
    if (totalPositions.value === 0) return 0
    return Math.round((positionsWithProfiles.value / totalPositions.value) * 100)
  })

  const departmentList = computed(() => {
    return departments.value.map(dept => ({
      value: dept.id,
      title: dept.name
    }))
  })

  // Actions
  /**
   * Load searchable positions from API with optional cache bypass
   * Uses localStorage caching with 24-hour TTL to reduce API calls
   *
   * @param forceRefresh - If true, bypasses localStorage cache and fetches fresh data
   * @throws CatalogError if API call fails
   *
   * @example
   * ```typescript
   * // Load from cache or API
   * await loadSearchableItems()
   *
   * // Force fresh load
   * await loadSearchableItems(true)
   * ```
   */
  async function loadSearchableItems(forceRefresh = false): Promise<void> {
    // Check cache first
    if (!forceRefresh) {
      const cached = loadFromCache()
      if (cached) {
        searchableItems.value = cached.items
        lastUpdated.value = new Date(cached.timestamp)
        return
      }
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/api/organization/search-items')
      const items: SearchableItem[] = response.data.data.items

      searchableItems.value = items
      lastUpdated.value = new Date()

      // Cache the results
      saveToCache(items)
    } catch (err: unknown) {
      const errorMessage = (err as any).response?.data?.detail ||
                          'Failed to load organization data'
      error.value = errorMessage

      if (import.meta.env.DEV) {
        console.error('Failed to load searchable items:', err)
      }

      throw new CatalogError(errorMessage, 'API_ERROR', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load department list from API
   *
   * @throws CatalogError if API call fails
   */
  async function loadDepartments(): Promise<void> {
    try {
      const response = await api.get('/api/catalog/departments')
      departments.value = response.data.data.departments
    } catch (err: unknown) {
      if (import.meta.env.DEV) {
        console.error('Failed to load departments:', err)
      }

      throw new CatalogError(
        'Failed to load departments',
        'API_ERROR',
        err
      )
    }
  }

  /**
   * Load organization tree structure from API
   * Falls back to building tree from searchable items if API fails
   *
   * @throws CatalogError if both API and fallback fail
   */
  async function loadOrganizationTree(): Promise<void> {
    try {
      // Load structure.json from backend
      const response = await api.get('/api/organization/structure')
      const structure: OrganizationStructureResponse = response.data.data

      // Transform structure into tree format with profile counts
      organizationTree.value = transformToTree(structure)
    } catch (err: unknown) {
      if (import.meta.env.DEV) {
        console.error('Failed to load organization tree:', err)
      }

      // Fallback: build tree from searchable items
      organizationTree.value = buildTreeFromItems()
    }
  }

  /**
   * Transform backend organization structure into tree with profile counts
   *
   * @param structure - Raw organization structure from API
   * @returns Transformed organization tree nodes
   */
  function transformToTree(structure: OrganizationStructureResponse): OrganizationNode[] {
    // Recursive function to transform backend structure
    function transformNode(node: OrganizationStructureResponse): OrganizationNode {
      const positions = searchableItems.value.filter(
        item => item.business_unit_id === node.id
      )

      const transformed: OrganizationNode = {
        id: node.id,
        name: node.name,
        type: (node.type as OrganizationNode['type']) || 'unit',
        positions,
        profile_count: positions.filter(p => p.profile_exists).length,
        total_positions: positions.length
      }

      if (node.children && node.children.length > 0) {
        transformed.children = node.children.map(transformNode)

        // Aggregate counts from children
        transformed.children.forEach(child => {
          transformed.profile_count! += child.profile_count || 0
          transformed.total_positions! += child.total_positions || 0
        })
      }

      return transformed
    }

    return structure.children?.map(transformNode) || []
  }

  /**
   * Build organization tree from department paths (fallback method)
   * Used when API structure endpoint is unavailable
   *
   * @returns Organization tree built from searchable items
   */
  function buildTreeFromItems(): OrganizationNode[] {
    // Fallback method: build tree from department paths
    const nodeMap = new Map<string, OrganizationNode>()
    const rootNodes: OrganizationNode[] = []

    searchableItems.value.forEach(item => {
      const pathParts = item.department_path.split(' → ')
      let currentPath = ''

      pathParts.forEach((part, index) => {
        const parentPath = currentPath
        currentPath = currentPath ? `${currentPath} → ${part}` : part

        if (!nodeMap.has(currentPath)) {
          const node: OrganizationNode = {
            id: currentPath,
            name: part,
            type: index === 0 ? 'division' : index === 1 ? 'block' : index === 2 ? 'department' : 'unit',
            children: [],
            positions: [],
            profile_count: 0,
            total_positions: 0
          }

          nodeMap.set(currentPath, node)

          if (parentPath) {
            const parent = nodeMap.get(parentPath)
            parent?.children?.push(node)
          } else {
            rootNodes.push(node)
          }
        }

        // Add position to the leaf node
        if (index === pathParts.length - 1) {
          const node = nodeMap.get(currentPath)!
          node.positions!.push(item)
          node.total_positions!++
          if (item.profile_exists) {
            node.profile_count!++
          }
        }
      })
    })

    // Propagate counts up the tree
    function propagateCounts(node: OrganizationNode): void {
      if (node.children && node.children.length > 0) {
        node.children.forEach(propagateCounts)
        node.profile_count = node.children.reduce(
          (sum, child) => sum + (child.profile_count || 0),
          node.profile_count || 0
        )
        node.total_positions = node.children.reduce(
          (sum, child) => sum + (child.total_positions || 0),
          node.total_positions || 0
        )
      }
    }

    rootNodes.forEach(propagateCounts)
    return rootNodes
  }

  /**
   * Find a position by its unique ID
   *
   * @param positionId - Unique position identifier
   * @returns Position if found, undefined otherwise
   */
  function getPositionById(positionId: string): SearchableItem | undefined {
    return searchableItems.value.find(item => item.position_id === positionId)
  }

  /**
   * Get all positions belonging to a specific business unit
   *
   * @param businessUnitId - Business unit identifier
   * @returns Array of positions in the business unit
   */
  function getPositionsByBusinessUnit(businessUnitId: string): SearchableItem[] {
    return searchableItems.value.filter(item => item.business_unit_id === businessUnitId)
  }

  /**
   * Get all positions that don't have generated profiles yet
   *
   * @returns Array of positions without profiles
   */
  function getPositionsWithoutProfiles(): SearchableItem[] {
    return searchableItems.value.filter(item => !item.profile_exists)
  }

  /**
   * Force refresh of cached data
   * Reloads searchable items and organization tree from API
   *
   * @throws CatalogError if refresh fails
   */
  async function refreshCache(): Promise<void> {
    await loadSearchableItems(true)
    await loadOrganizationTree()
  }

  /**
   * Save searchable items to localStorage cache
   *
   * @param items - Array of searchable items to cache
   */
  function saveToCache(items: SearchableItem[]): void {
    try {
      const cacheData = {
        items,
        timestamp: Date.now()
      }
      localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
    } catch (err) {
      if (import.meta.env.DEV) {
        console.warn('Failed to save to cache:', err)
      }
    }
  }

  /**
   * Load searchable items from localStorage cache
   * Returns null if cache is expired or invalid
   *
   * @returns Cached data or null if cache miss
   */
  function loadFromCache(): { items: SearchableItem[], timestamp: number } | null {
    try {
      const cached = localStorage.getItem(CACHE_KEY)
      if (!cached) return null

      const cacheData = JSON.parse(cached)
      const age = Date.now() - cacheData.timestamp

      if (age > CACHE_DURATION_MS) {
        localStorage.removeItem(CACHE_KEY)
        return null
      }

      return cacheData
    } catch (err) {
      if (import.meta.env.DEV) {
        console.warn('Failed to load from cache:', err)
      }
      return null
    }
  }

  /**
   * Clear cached organization data from localStorage
   */
  function clearCache(): void {
    localStorage.removeItem(CACHE_KEY)
  }

  return {
    // State
    searchableItems,
    departments,
    organizationTree,
    isLoading,
    error,
    lastUpdated,

    // Computed
    totalPositions,
    positionsWithProfiles,
    coveragePercentage,
    departmentList,

    // Actions
    loadSearchableItems,
    loadDepartments,
    loadOrganizationTree,
    getPositionById,
    getPositionsByBusinessUnit,
    getPositionsWithoutProfiles,
    refreshCache,
    clearCache
  }
})

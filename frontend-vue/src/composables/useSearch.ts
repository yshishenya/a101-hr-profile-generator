/**
 * Composable for managing tree search functionality
 * Handles search state, navigation, filtering, and highlighting
 */

import { ref, computed, watch } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import type { OrganizationNode } from '@/stores/catalog'
import { logger } from '@/utils/logger'

export interface SearchFilters {
  withProfile: boolean      // Show only positions with profiles
  withoutProfile: boolean   // Show only positions without profiles
  exactMatch: boolean       // Exact match instead of contains
}

export interface SearchResult {
  nodeId: string           // ID of the found node
  nodeName: string         // Name of the found node
  nodeType: string         // Type: 'position' or organizational
  path: string[]           // Path from root to this node (IDs)
  pathNames: string[]      // Path from root to this node (names)
  profileExists?: boolean  // For positions only
  profileId?: number       // For positions only
}

// Constants
const MIN_SEARCH_LENGTH = 2

/**
 * Composable return type
 */
export interface UseSearchReturn {
  // State
  searchQuery: Ref<string>
  searchResults: Ref<SearchResult[]>
  currentResultIndex: Ref<number>
  filters: Ref<SearchFilters>
  // Computed
  hasResults: ComputedRef<boolean>
  totalResults: ComputedRef<number>
  isSearching: ComputedRef<boolean>
  currentResult: ComputedRef<SearchResult | null>
  navigationLabel: ComputedRef<string>
  // Methods
  performSearch: () => void
  goToNextResult: () => void
  goToPreviousResult: () => void
  clearSearch: () => void
  getPathToNode: (nodeId: string) => string[]
  highlightText: (text: string, query: string) => string
}

export function useSearch(treeData: Ref<OrganizationNode[]>): UseSearchReturn {
  // State
  const searchQuery = ref('')
  const searchResults = ref<SearchResult[]>([])
  const currentResultIndex = ref(0)
  const filters = ref<SearchFilters>({
    withProfile: false,
    withoutProfile: false,
    exactMatch: false
  })

  // Computed
  const hasResults = computed(() => searchResults.value.length > 0)
  const totalResults = computed(() => searchResults.value.length)
  const isSearching = computed(() => searchQuery.value.length >= MIN_SEARCH_LENGTH)

  const currentResult = computed((): SearchResult | null => {
    if (hasResults.value && currentResultIndex.value >= 0 && currentResultIndex.value < searchResults.value.length) {
      return searchResults.value[currentResultIndex.value] ?? null
    }
    return null
  })

  const navigationLabel = computed(() => {
    if (!hasResults.value) return '0/0'
    return `${currentResultIndex.value + 1}/${totalResults.value}`
  })

  // Watch for query or filter changes
  watch([searchQuery, filters], () => {
    if (isSearching.value) {
      performSearch()
    } else {
      clearSearch()
    }
  }, { deep: true })

  // Methods
  /**
   * Performs search across organization tree with current query and filters
   * Handles validation, error boundaries, and result collection
   */
  function performSearch(): void {
    try {
      const query = searchQuery.value.trim().toLowerCase()
      if (query.length < MIN_SEARCH_LENGTH) {
        clearSearch()
        return
      }

      // Check if tree data is valid
      if (!treeData.value || treeData.value.length === 0) {
        logger.warn('Search attempted with empty tree data')
        clearSearch()
        return
      }

      const results: SearchResult[] = []
      collectSearchResults(treeData.value, query, [], [], results)

      // Apply filters
      searchResults.value = applyFilters(results)

      // Reset to first result
      currentResultIndex.value = 0
    } catch (error: unknown) {
      logger.error('Search failed', error)
      clearSearch()
    }
  }

  /**
   * Recursively collects search results from organization tree
   * Searches both organizational nodes and position nodes
   *
   * @param nodes - Array of organization nodes to search
   * @param query - Search query string (lowercase)
   * @param currentPath - Current path IDs from root to current node
   * @param currentPathNames - Current path names from root to current node
   * @param results - Accumulator array for search results
   */
  function collectSearchResults(
    nodes: OrganizationNode[],
    query: string,
    currentPath: string[],
    currentPathNames: string[],
    results: SearchResult[]
  ): void {
    for (const node of nodes) {
      const nodePath = [...currentPath, node.id]
      const nodePathNames = [...currentPathNames, node.name]

      // Check if node name matches
      const nodeMatches = matchesQuery(node.name, query)

      // Check positions in this node
      if (node.positions) {
        for (const position of node.positions) {
          const positionMatches = matchesQuery(position.position_name, query)

          if (positionMatches || nodeMatches) {
            results.push({
              nodeId: position.position_id,
              nodeName: position.position_name,
              nodeType: 'position',
              path: [...nodePath, position.position_id],
              pathNames: [...nodePathNames, position.position_name],
              profileExists: position.profile_exists,
              profileId: position.profile_id
            })
          }
        }
      }

      // Recursively search children
      if (node.children) {
        collectSearchResults(node.children, query, nodePath, nodePathNames, results)
      }
    }
  }

  /**
   * Checks if text matches search query based on current filters
   * Supports both exact match and partial match (contains)
   *
   * @param text - Text to search in
   * @param query - Search query
   * @returns True if text matches query
   */
  function matchesQuery(text: string, query: string): boolean {
    const lowerText = text.toLowerCase()
    const lowerQuery = query.toLowerCase()

    if (filters.value.exactMatch) {
      return lowerText === lowerQuery
    }

    return lowerText.includes(lowerQuery)
  }

  /**
   * Applies active filters to search results
   * Filters by profile existence (withProfile/withoutProfile)
   *
   * @param results - Unfiltered search results
   * @returns Filtered search results
   */
  function applyFilters(results: SearchResult[]): SearchResult[] {
    return results.filter(result => {
      // Filter by profile existence
      if (filters.value.withProfile && !filters.value.withoutProfile) {
        return result.profileExists === true
      }
      if (filters.value.withoutProfile && !filters.value.withProfile) {
        return result.profileExists === false
      }

      return true
    })
  }

  /**
   * Navigates to next search result with wraparound to first
   * Loops back to first result when reaching the end
   */
  function goToNextResult(): void {
    if (currentResultIndex.value < searchResults.value.length - 1) {
      currentResultIndex.value++
    } else {
      // Loop to first
      currentResultIndex.value = 0
    }
  }

  /**
   * Navigates to previous search result with wraparound to last
   * Loops back to last result when at the beginning
   */
  function goToPreviousResult(): void {
    if (currentResultIndex.value > 0) {
      currentResultIndex.value--
    } else {
      // Loop to last
      currentResultIndex.value = searchResults.value.length - 1
    }
  }

  /**
   * Clears search state
   * Resets query, results, and current index to initial values
   */
  function clearSearch(): void {
    searchQuery.value = ''
    searchResults.value = []
    currentResultIndex.value = 0
  }

  /**
   * Gets path (array of IDs) from root to specified node
   *
   * @param nodeId - ID of target node
   * @returns Array of node IDs from root to target, or empty array if not found
   */
  function getPathToNode(nodeId: string): string[] {
    const result = searchResults.value.find(r => r.nodeId === nodeId)
    return result ? result.path : []
  }

  /**
   * Highlights search query in text with HTML mark tags
   * Respects exactMatch filter for highlighting behavior
   *
   * @param text - Text to highlight in
   * @param query - Search query to highlight
   * @returns Text with HTML mark tags around matches
   */
  function highlightText(text: string, query: string): string {
    if (!query || query.length < MIN_SEARCH_LENGTH) return text

    const lowerText = text.toLowerCase()
    const lowerQuery = query.toLowerCase()

    if (filters.value.exactMatch) {
      if (lowerText === lowerQuery) {
        return `<mark class="search-highlight">${text}</mark>`
      }
      return text
    }

    // Case-insensitive highlighting
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi')
    return text.replace(regex, '<mark class="search-highlight">$1</mark>')
  }

  /**
   * Escapes special regex characters in string for safe regex use
   *
   * @param string - String to escape
   * @returns Escaped string safe for RegExp constructor
   */
  function escapeRegExp(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  return {
    // State
    searchQuery,
    searchResults,
    currentResultIndex,
    filters,

    // Computed
    hasResults,
    totalResults,
    isSearching,
    currentResult,
    navigationLabel,

    // Methods
    performSearch,
    goToNextResult,
    goToPreviousResult,
    clearSearch,
    getPathToNode,
    highlightText
  }
}

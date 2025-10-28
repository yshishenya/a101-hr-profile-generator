/**
 * Unit tests for useSearch composable
 * Tests search functionality, navigation, filters, and highlighting
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { useSearch } from '../useSearch'
import type { OrganizationNode } from '@/stores/catalog'

describe('useSearch', () => {
  // Test data
  const createTestTree = (): OrganizationNode[] => [
    {
      id: 'dept1',
      name: 'Engineering Department',
      level: 1,
      parent_id: null,
      business_unit_id: 'bu1',
      positions: [
        {
          position_id: 'pos1',
          position_name: 'Senior Engineer',
          profile_exists: true,
          profile_id: 101
        },
        {
          position_id: 'pos2',
          position_name: 'Junior Engineer',
          profile_exists: false,
          profile_id: undefined
        }
      ],
      children: [
        {
          id: 'team1',
          name: 'Backend Team',
          level: 2,
          parent_id: 'dept1',
          business_unit_id: 'bu1',
          positions: [
            {
              position_id: 'pos3',
              position_name: 'Backend Developer',
              profile_exists: true,
              profile_id: 103
            }
          ],
          children: []
        }
      ]
    },
    {
      id: 'dept2',
      name: 'Marketing Department',
      level: 1,
      parent_id: null,
      business_unit_id: 'bu2',
      positions: [
        {
          position_id: 'pos4',
          position_name: 'Marketing Manager',
          profile_exists: false,
          profile_id: undefined
        }
      ],
      children: []
    }
  ]

  let treeData: ReturnType<typeof ref<OrganizationNode[]>>
  let search: ReturnType<typeof useSearch>

  beforeEach(() => {
    treeData = ref(createTestTree())
    search = useSearch(treeData)
  })

  describe('performSearch', () => {
    it('should find positions by exact name match', async () => {
      search.searchQuery.value = 'Senior Engineer'
      await nextTick()

      expect(search.hasResults.value).toBe(true)
      expect(search.totalResults.value).toBe(1)
      expect(search.searchResults.value[0].nodeName).toBe('Senior Engineer')
    })

    it('should find positions by partial name match (case-insensitive)', async () => {
      search.searchQuery.value = 'engineer'
      await nextTick()

      expect(search.hasResults.value).toBe(true)
      expect(search.totalResults.value).toBe(2)

      const names = search.searchResults.value.map(r => r.nodeName)
      expect(names).toContain('Senior Engineer')
      expect(names).toContain('Junior Engineer')
    })

    it('should handle empty search query', () => {
      search.searchQuery.value = '   '

      expect(search.hasResults.value).toBe(false)
      expect(search.totalResults.value).toBe(0)
    })

    it('should handle search query < 2 characters', () => {
      search.searchQuery.value = 'S'

      expect(search.hasResults.value).toBe(false)
      expect(search.totalResults.value).toBe(0)
      expect(search.isSearching.value).toBe(false)
    })

    it('should apply withProfile filter correctly', async () => {
      search.searchQuery.value = 'engineer'
      search.filters.value.withProfile = true
      search.filters.value.withoutProfile = false
      await nextTick()

      expect(search.hasResults.value).toBe(true)
      expect(search.totalResults.value).toBe(1)
      expect(search.searchResults.value[0].nodeName).toBe('Senior Engineer')
      expect(search.searchResults.value[0].profileExists).toBe(true)
    })

    it('should apply withoutProfile filter correctly', async () => {
      search.searchQuery.value = 'engineer'
      search.filters.value.withProfile = false
      search.filters.value.withoutProfile = true
      await nextTick()

      expect(search.hasResults.value).toBe(true)
      expect(search.totalResults.value).toBe(1)
      expect(search.searchResults.value[0].nodeName).toBe('Junior Engineer')
      expect(search.searchResults.value[0].profileExists).toBe(false)
    })

    it('should apply exactMatch filter correctly', () => {
      search.searchQuery.value = 'engineer'
      search.filters.value.exactMatch = true

      // Should not find 'Senior Engineer' or 'Junior Engineer' with exact match
      expect(search.hasResults.value).toBe(false)
      expect(search.totalResults.value).toBe(0)
    })

    it('should handle empty tree data gracefully', () => {
      treeData.value = []
      search.searchQuery.value = 'test'

      expect(search.hasResults.value).toBe(false)
      expect(search.totalResults.value).toBe(0)
    })

    it('should handle null tree data gracefully', () => {
      treeData.value = null as unknown as OrganizationNode[]
      search.searchQuery.value = 'test'

      expect(search.hasResults.value).toBe(false)
      expect(search.totalResults.value).toBe(0)
    })

    it('should find positions in nested children', async () => {
      search.searchQuery.value = 'backend'
      await nextTick()

      expect(search.hasResults.value).toBe(true)
      expect(search.totalResults.value).toBe(1)
      expect(search.searchResults.value[0].nodeName).toBe('Backend Developer')
      expect(search.searchResults.value[0].pathNames).toContain('Backend Team')
    })

    it('should reset to first result after new search', async () => {
      search.searchQuery.value = 'engineer'
      await nextTick()
      search.goToNextResult()
      expect(search.currentResultIndex.value).toBe(1)

      // New search should reset index
      search.searchQuery.value = 'backend'
      await nextTick()
      expect(search.currentResultIndex.value).toBe(0)
    })
  })

  describe('navigation', () => {
    beforeEach(async () => {
      search.searchQuery.value = 'engineer'
      await nextTick()
    })

    it('should navigate to next result', () => {
      expect(search.currentResultIndex.value).toBe(0)

      search.goToNextResult()
      expect(search.currentResultIndex.value).toBe(1)
    })

    it('should wrap to first result when at end', () => {
      search.goToNextResult() // Move to index 1
      search.goToNextResult() // Should wrap to 0

      expect(search.currentResultIndex.value).toBe(0)
    })

    it('should navigate to previous result', () => {
      search.goToNextResult() // Move to index 1
      search.goToPreviousResult() // Back to index 0

      expect(search.currentResultIndex.value).toBe(0)
    })

    it('should wrap to last result when at beginning', () => {
      expect(search.currentResultIndex.value).toBe(0)

      search.goToPreviousResult() // Should wrap to last
      expect(search.currentResultIndex.value).toBe(1)
    })

    it('should provide correct navigation label', () => {
      expect(search.navigationLabel.value).toBe('1/2')

      search.goToNextResult()
      expect(search.navigationLabel.value).toBe('2/2')

      search.goToNextResult() // Wrap to first
      expect(search.navigationLabel.value).toBe('1/2')
    })

    it('should show 0/0 when no results', () => {
      search.clearSearch()
      expect(search.navigationLabel.value).toBe('0/0')
    })
  })

  describe('highlightText', () => {
    it('should highlight partial matches', () => {
      const result = search.highlightText('Senior Engineer', 'engineer')
      expect(result).toContain('<mark class="search-highlight">')
      expect(result).toContain('Engineer</mark>')
    })

    it('should highlight exact matches when exactMatch filter is on', () => {
      search.filters.value.exactMatch = true
      const result = search.highlightText('engineer', 'engineer')
      expect(result).toBe('<mark class="search-highlight">engineer</mark>')
    })

    it('should not highlight when exactMatch filter is on and text does not match', () => {
      search.filters.value.exactMatch = true
      const result = search.highlightText('Senior Engineer', 'engineer')
      expect(result).toBe('Senior Engineer')
      expect(result).not.toContain('<mark')
    })

    it('should handle case-insensitive matching', () => {
      const result1 = search.highlightText('Senior Engineer', 'ENGINEER')
      expect(result1).toContain('<mark class="search-highlight">Engineer</mark>')

      const result2 = search.highlightText('SENIOR ENGINEER', 'engineer')
      expect(result2).toContain('<mark class="search-highlight">ENGINEER</mark>')
    })

    it('should escape regex special characters', () => {
      const result = search.highlightText('Test (special)', '(special)')
      expect(result).toContain('<mark class="search-highlight">(special)</mark>')
    })

    it('should return original text when query is too short', () => {
      const result = search.highlightText('Test text', 'T')
      expect(result).toBe('Test text')
      expect(result).not.toContain('<mark')
    })

    it('should highlight multiple occurrences', () => {
      const result = search.highlightText('Engineer Engineer', 'engineer')
      const matches = (result.match(/<mark/g) || []).length
      expect(matches).toBe(2)
    })
  })

  describe('filters', () => {
    beforeEach(async () => {
      search.searchQuery.value = 'ma' // Should match 'manager' and 'marketing'
      await nextTick()
    })

    it('should filter positions with profiles', async () => {
      search.filters.value.withProfile = true
      search.filters.value.withoutProfile = false
      await nextTick()

      const withProfiles = search.searchResults.value.filter(r => r.profileExists === true)
      expect(search.searchResults.value.length).toBe(withProfiles.length)
    })

    it('should filter positions without profiles', () => {
      search.filters.value.withProfile = false
      search.filters.value.withoutProfile = true

      const withoutProfiles = search.searchResults.value.filter(r => r.profileExists === false)
      expect(search.searchResults.value.length).toBe(withoutProfiles.length)
    })

    it('should show all positions when both filters are false', () => {
      search.filters.value.withProfile = false
      search.filters.value.withoutProfile = false

      expect(search.searchResults.value.length).toBeGreaterThan(0)
    })

    it('should show all positions when both filters are true', () => {
      search.filters.value.withProfile = true
      search.filters.value.withoutProfile = true

      expect(search.searchResults.value.length).toBeGreaterThan(0)
    })

    it('should combine exactMatch with profile filters', () => {
      search.searchQuery.value = 'marketing manager'
      search.filters.value.exactMatch = true
      search.filters.value.withoutProfile = true

      expect(search.hasResults.value).toBe(true)
      expect(search.searchResults.value[0].nodeName).toBe('Marketing Manager')
      expect(search.searchResults.value[0].profileExists).toBe(false)
    })
  })

  describe('getPathToNode', () => {
    beforeEach(async () => {
      search.searchQuery.value = 'engineer'
      await nextTick()
    })

    it('should return path for found node', () => {
      const path = search.getPathToNode('pos1')
      expect(path).toContain('dept1')
      expect(path).toContain('pos1')
    })

    it('should return empty array for unknown node', () => {
      const path = search.getPathToNode('unknown')
      expect(path).toEqual([])
    })
  })

  describe('clearSearch', () => {
    it('should reset all search state', () => {
      search.searchQuery.value = 'test'
      search.goToNextResult()

      search.clearSearch()

      expect(search.searchQuery.value).toBe('')
      expect(search.searchResults.value).toEqual([])
      expect(search.currentResultIndex.value).toBe(0)
      expect(search.hasResults.value).toBe(false)
    })
  })

  describe('computed properties', () => {
    it('should compute hasResults correctly', async () => {
      expect(search.hasResults.value).toBe(false)

      search.searchQuery.value = 'engineer'
      await nextTick()
      expect(search.hasResults.value).toBe(true)
    })

    it('should compute totalResults correctly', async () => {
      expect(search.totalResults.value).toBe(0)

      search.searchQuery.value = 'engineer'
      await nextTick()
      expect(search.totalResults.value).toBe(2)
    })

    it('should compute isSearching correctly', () => {
      expect(search.isSearching.value).toBe(false)

      search.searchQuery.value = 'en'
      expect(search.isSearching.value).toBe(true)

      search.searchQuery.value = 'e'
      expect(search.isSearching.value).toBe(false)
    })

    it('should compute currentResult correctly', async () => {
      expect(search.currentResult.value).toBeNull()

      search.searchQuery.value = 'engineer'
      await nextTick()
      expect(search.currentResult.value).not.toBeNull()
      expect(search.currentResult.value?.nodeName).toBe('Senior Engineer')

      search.goToNextResult()
      expect(search.currentResult.value?.nodeName).toBe('Junior Engineer')
    })
  })

  describe('watcher behavior', () => {
    it('should trigger search when query changes', async () => {
      search.searchQuery.value = 'en'
      await nextTick()
      expect(search.hasResults.value).toBe(true)

      search.searchQuery.value = 'backend'
      await nextTick()
      expect(search.totalResults.value).toBe(1)
    })

    it('should trigger search when filters change', async () => {
      search.searchQuery.value = 'engineer'
      await nextTick()
      const initialCount = search.totalResults.value

      search.filters.value.withProfile = true
      await nextTick()
      expect(search.totalResults.value).toBeLessThan(initialCount)
    })

    it('should clear search when query becomes too short', async () => {
      search.searchQuery.value = 'engineer'
      await nextTick()
      expect(search.hasResults.value).toBe(true)

      search.searchQuery.value = 'e'
      await nextTick()
      expect(search.hasResults.value).toBe(false)
    })
  })

  describe('search result structure', () => {
    beforeEach(async () => {
      search.searchQuery.value = 'backend'
      await nextTick()
    })

    it('should include correct result properties', () => {
      const result = search.searchResults.value[0]

      expect(result).toHaveProperty('nodeId')
      expect(result).toHaveProperty('nodeName')
      expect(result).toHaveProperty('nodeType')
      expect(result).toHaveProperty('path')
      expect(result).toHaveProperty('pathNames')
      expect(result).toHaveProperty('profileExists')
    })

    it('should have correct path structure', () => {
      const result = search.searchResults.value[0]

      expect(Array.isArray(result.path)).toBe(true)
      expect(Array.isArray(result.pathNames)).toBe(true)
      expect(result.path.length).toBeGreaterThan(0)
      expect(result.pathNames.length).toBe(result.path.length)
    })

    it('should mark type as position', () => {
      const result = search.searchResults.value[0]
      expect(result.nodeType).toBe('position')
    })
  })
})

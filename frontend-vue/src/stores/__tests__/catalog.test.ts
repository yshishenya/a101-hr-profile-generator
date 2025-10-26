/**
 * Unit tests for catalog store
 * Tests state management, caching, API calls, and tree building
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCatalogStore } from '../catalog'
import type { SearchableItem, Department } from '../catalog'
import api from '@/services/api'

// Mock dependencies
vi.mock('@/services/api')
vi.mock('@/utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('catalogStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with empty state', () => {
      const store = useCatalogStore()

      expect(store.searchableItems).toEqual([])
      expect(store.departments).toEqual([])
      expect(store.organizationTree).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.lastUpdated).toBe(null)
    })
  })

  describe('Computed Properties', () => {
    it('should compute totalPositions correctly', () => {
      const store = useCatalogStore()

      store.searchableItems = createMockPositions(5)

      expect(store.totalPositions).toBe(5)
    })

    it('should compute positionsWithProfiles correctly', () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true),
        createMockPosition('2', false),
        createMockPosition('3', true)
      ]

      expect(store.positionsWithProfiles).toBe(2)
    })

    it('should compute coveragePercentage correctly', () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true),
        createMockPosition('2', false),
        createMockPosition('3', true),
        createMockPosition('4', true)
      ]

      expect(store.coveragePercentage).toBe(75)
    })

    it('should return 0 for coveragePercentage when no positions', () => {
      const store = useCatalogStore()

      expect(store.coveragePercentage).toBe(0)
    })

    it('should compute departmentList correctly', () => {
      const store = useCatalogStore()

      store.departments = [
        { id: 'dept1', name: 'Department 1', type: 'department' },
        { id: 'dept2', name: 'Department 2', type: 'department' }
      ]

      expect(store.departmentList).toEqual([
        { value: 'dept1', title: 'Department 1' },
        { value: 'dept2', title: 'Department 2' }
      ])
    })
  })

  describe('loadSearchableItems', () => {
    it('should load positions from API successfully', async () => {
      const store = useCatalogStore()
      const mockPositions = createMockPositions(3)

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            items: mockPositions,
            total_count: 3
          }
        }
      })

      await store.loadSearchableItems()

      expect(store.searchableItems).toEqual(mockPositions)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.lastUpdated).toBeInstanceOf(Date)
      expect(api.get).toHaveBeenCalledWith('/api/organization/positions')
    })

    it('should cache positions to localStorage', async () => {
      const store = useCatalogStore()
      const mockPositions = createMockPositions(2)

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            items: mockPositions,
            total_count: 2
          }
        }
      })

      await store.loadSearchableItems()

      const cached = JSON.parse(localStorageMock.getItem('org_positions_cache')!)
      expect(cached.items).toEqual(mockPositions)
      expect(cached.timestamp).toBeDefined()
    })

    it('should load from cache if available and not expired', async () => {
      const store = useCatalogStore()
      const mockPositions = createMockPositions(2)

      // Set cache
      localStorageMock.setItem('org_positions_cache', JSON.stringify({
        items: mockPositions,
        timestamp: Date.now()
      }))

      await store.loadSearchableItems()

      expect(store.searchableItems).toEqual(mockPositions)
      expect(api.get).not.toHaveBeenCalled()
    })

    it('should bypass cache when forceRefresh is true', async () => {
      const store = useCatalogStore()
      const cachedPositions = createMockPositions(1)
      const freshPositions = createMockPositions(3)

      // Set cache
      localStorageMock.setItem('org_positions_cache', JSON.stringify({
        items: cachedPositions,
        timestamp: Date.now()
      }))

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            items: freshPositions,
            total_count: 3
          }
        }
      })

      await store.loadSearchableItems(true)

      expect(store.searchableItems).toEqual(freshPositions)
      expect(api.get).toHaveBeenCalled()
    })

    it('should ignore expired cache', async () => {
      const store = useCatalogStore()
      const mockPositions = createMockPositions(2)

      // Set expired cache (25 hours ago)
      localStorageMock.setItem('org_positions_cache', JSON.stringify({
        items: createMockPositions(1),
        timestamp: Date.now() - (25 * 60 * 60 * 1000)
      }))

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            items: mockPositions,
            total_count: 2
          }
        }
      })

      await store.loadSearchableItems()

      expect(store.searchableItems).toEqual(mockPositions)
      expect(api.get).toHaveBeenCalled()
    })

    it('should handle API errors', async () => {
      const store = useCatalogStore()

      vi.mocked(api.get).mockRejectedValue({
        response: {
          data: {
            detail: 'API Error'
          }
        }
      })

      await expect(store.loadSearchableItems()).rejects.toThrow('API Error')
      expect(store.error).toBe('API Error')
      expect(store.isLoading).toBe(false)
    })

    it('should handle network errors', async () => {
      const store = useCatalogStore()

      vi.mocked(api.get).mockRejectedValue(new Error('Network Error'))

      await expect(store.loadSearchableItems()).rejects.toThrow('Network Error')
      expect(store.error).toBe('Network Error')
    })
  })

  describe('loadDepartments', () => {
    it('should load departments from API successfully', async () => {
      const store = useCatalogStore()
      const mockDepartments: Department[] = [
        { id: 'dept1', name: 'Department 1', type: 'department' },
        { id: 'dept2', name: 'Department 2', type: 'department' }
      ]

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            departments: mockDepartments
          }
        }
      })

      await store.loadDepartments()

      expect(store.departments).toEqual(mockDepartments)
      expect(api.get).toHaveBeenCalledWith('/api/catalog/departments')
    })

    it('should handle API errors', async () => {
      const store = useCatalogStore()

      vi.mocked(api.get).mockRejectedValue(new Error('API Error'))

      await expect(store.loadDepartments()).rejects.toThrow('Failed to load departments')
    })
  })

  describe('loadOrganizationTree', () => {
    it('should build tree from searchable items', async () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true, 'Division A → Block B → Department C'),
        createMockPosition('2', false, 'Division A → Block B → Department C'),
        createMockPosition('3', true, 'Division A → Block B → Department D')
      ]

      await store.loadOrganizationTree()

      expect(store.organizationTree.length).toBeGreaterThan(0)
      expect(store.organizationTree[0].name).toBe('Division A')
      expect(store.organizationTree[0].type).toBe('division')
    })

    it('should calculate profile counts correctly', async () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true, 'Division A → Block B → Department C'),
        createMockPosition('2', false, 'Division A → Block B → Department C'),
        createMockPosition('3', true, 'Division A → Block B → Department D')
      ]

      await store.loadOrganizationTree()

      const divisionNode = store.organizationTree[0]
      expect(divisionNode.total_positions).toBe(3)
      expect(divisionNode.profile_count).toBe(2)
    })

    it('should handle deep hierarchy correctly', async () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true, 'Division A → Block B → Department C → Unit D → SubUnit E')
      ]

      await store.loadOrganizationTree()

      expect(store.organizationTree.length).toBe(1)
      expect(store.organizationTree[0].children).toBeDefined()
      expect(store.organizationTree[0].children!.length).toBeGreaterThan(0)
    })
  })

  describe('Getter Methods', () => {
    it('should get position by ID', () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true),
        createMockPosition('2', false)
      ]

      const position = store.getPositionById('1')

      expect(position).toBeDefined()
      expect(position?.position_id).toBe('1')
    })

    it('should return undefined for non-existent position ID', () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true)
      ]

      const position = store.getPositionById('999')

      expect(position).toBeUndefined()
    })

    it('should get positions by business unit', () => {
      const store = useCatalogStore()

      store.searchableItems = [
        { ...createMockPosition('1', true), business_unit_id: 'bu1' },
        { ...createMockPosition('2', false), business_unit_id: 'bu1' },
        { ...createMockPosition('3', true), business_unit_id: 'bu2' }
      ]

      const positions = store.getPositionsByBusinessUnit('bu1')

      expect(positions.length).toBe(2)
      expect(positions[0].business_unit_id).toBe('bu1')
    })

    it('should get positions without profiles', () => {
      const store = useCatalogStore()

      store.searchableItems = [
        createMockPosition('1', true),
        createMockPosition('2', false),
        createMockPosition('3', false)
      ]

      const positions = store.getPositionsWithoutProfiles()

      expect(positions.length).toBe(2)
      expect(positions.every(p => !p.profile_exists)).toBe(true)
    })
  })

  describe('Cache Management', () => {
    it('should clear cache', () => {
      const store = useCatalogStore()

      localStorageMock.setItem('org_positions_cache', JSON.stringify({
        items: createMockPositions(2),
        timestamp: Date.now()
      }))

      store.clearCache()

      expect(localStorageMock.getItem('org_positions_cache')).toBe(null)
    })

    it('should refresh cache', async () => {
      const store = useCatalogStore()
      const mockPositions = createMockPositions(3)

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            items: mockPositions,
            total_count: 3
          }
        }
      })

      await store.refreshCache()

      expect(store.searchableItems).toEqual(mockPositions)
      expect(store.organizationTree.length).toBeGreaterThan(0)
      expect(api.get).toHaveBeenCalled()
    })

    it('should handle corrupt cache data gracefully', async () => {
      const store = useCatalogStore()
      const mockPositions = createMockPositions(2)

      // Set corrupt cache
      localStorageMock.setItem('org_positions_cache', 'invalid json')

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: {
            items: mockPositions,
            total_count: 2
          }
        }
      })

      await store.loadSearchableItems()

      expect(store.searchableItems).toEqual(mockPositions)
      expect(api.get).toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    it('should set loading state during API call', async () => {
      const store = useCatalogStore()

      let loadingDuringCall = false

      vi.mocked(api.get).mockImplementation(async () => {
        loadingDuringCall = store.isLoading
        return {
          data: {
            data: {
              items: [],
              total_count: 0
            }
          }
        }
      })

      await store.loadSearchableItems()

      expect(loadingDuringCall).toBe(true)
      expect(store.isLoading).toBe(false)
    })
  })
})

// Helper functions
function createMockPosition(
  id: string,
  profileExists: boolean,
  departmentPath: string = 'Division → Block → Department'
): SearchableItem {
  return {
    position_id: id,
    position_name: `Position ${id}`,
    business_unit_id: `bu${id}`,
    business_unit_name: `Business Unit ${id}`,
    department_id: `dept${id}`,
    department_name: `Department ${id}`,
    department_path: departmentPath,
    profile_exists: profileExists,
    profile_id: profileExists ? parseInt(id) : undefined
  }
}

function createMockPositions(count: number): SearchableItem[] {
  return Array.from({ length: count }, (_, i) =>
    createMockPosition(`${i + 1}`, i % 2 === 0)
  )
}

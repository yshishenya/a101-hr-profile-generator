/**
 * Unit tests for OrganizationTree component
 * Tests tree selection functionality with type safety
 */

import { describe, it, expect } from 'vitest'
import type { SearchableItem } from '@/stores/catalog'

// Mock TreeItem type (matches the internal interface)
interface TreeItem {
  id: string
  name: string
  type: 'division' | 'block' | 'department' | 'unit'
  positions?: SearchableItem[]
  profile_count?: number
  total_positions?: number
  children?: TreeItem[]
}

// Helper function to create mock SearchableItem
function createMockPosition(id: string, name: string): SearchableItem {
  return {
    position_id: id,
    position_name: name,
    business_unit_id: 'bu-1',
    business_unit_name: 'Test BU',
    department_path: 'Test → Path',
    profile_exists: false
  }
}

// Helper function to create mock TreeItem
function createMockTreeItem(
  id: string,
  type: TreeItem['type'],
  directPositions: number = 0,
  children: TreeItem[] = []
): TreeItem {
  const positions = Array.from({ length: directPositions }, (_, i) =>
    createMockPosition(`pos-${id}-${i}`, `Position ${i}`)
  )

  // Calculate total positions recursively
  const childrenTotal = children.reduce((sum, child) => sum + (child.total_positions || 0), 0)
  const total_positions = directPositions + childrenTotal

  return {
    id,
    name: `Node ${id}`,
    type,
    positions: directPositions > 0 ? positions : undefined,
    profile_count: 0,
    total_positions,
    children: children.length > 0 ? children : undefined
  }
}

/**
 * Simulate collectAllPositionIdsRecursive function
 * (copied from component for testing)
 */
function collectAllPositionIdsRecursive(node: TreeItem): string[] {
  const ids: string[] = []

  if (node.positions && Array.isArray(node.positions)) {
    ids.push(...node.positions.map((p: SearchableItem) => p.position_id))
  }

  if (node.children && Array.isArray(node.children)) {
    for (const child of node.children) {
      ids.push(...collectAllPositionIdsRecursive(child))
    }
  }

  return ids
}

describe('OrganizationTree - collectAllPositionIdsRecursive', () => {
  it('should return empty array for node without positions', () => {
    const node = createMockTreeItem('node-1', 'unit', 0, [])
    const result = collectAllPositionIdsRecursive(node)

    expect(result).toEqual([])
    expect(result).toHaveLength(0)
  })

  it('should return direct positions for leaf node', () => {
    const node = createMockTreeItem('node-1', 'unit', 3, [])
    const result = collectAllPositionIdsRecursive(node)

    expect(result).toHaveLength(3)
    expect(result).toContain('pos-node-1-0')
    expect(result).toContain('pos-node-1-1')
    expect(result).toContain('pos-node-1-2')
  })

  it('should return all nested positions for deep hierarchy', () => {
    // Create 3-level hierarchy
    const grandchild = createMockTreeItem('grandchild', 'unit', 2, [])
    const child = createMockTreeItem('child', 'department', 3, [grandchild])
    const parent = createMockTreeItem('parent', 'block', 5, [child])

    const result = collectAllPositionIdsRecursive(parent)

    // Should have 5 + 3 + 2 = 10 positions
    expect(result).toHaveLength(10)

    // Check parent positions
    expect(result).toContain('pos-parent-0')
    expect(result).toContain('pos-parent-4')

    // Check child positions
    expect(result).toContain('pos-child-0')
    expect(result).toContain('pos-child-2')

    // Check grandchild positions
    expect(result).toContain('pos-grandchild-0')
    expect(result).toContain('pos-grandchild-1')
  })

  it('should handle 6-level deep hierarchy', () => {
    // Create 6-level hierarchy (max depth in actual data)
    const level6 = createMockTreeItem('l6', 'unit', 1, [])
    const level5 = createMockTreeItem('l5', 'unit', 1, [level6])
    const level4 = createMockTreeItem('l4', 'unit', 1, [level5])
    const level3 = createMockTreeItem('l3', 'department', 1, [level4])
    const level2 = createMockTreeItem('l2', 'block', 1, [level3])
    const level1 = createMockTreeItem('l1', 'division', 1, [level2])

    const result = collectAllPositionIdsRecursive(level1)

    // Should have 6 positions (1 per level)
    expect(result).toHaveLength(6)
    expect(result).toContain('pos-l1-0')
    expect(result).toContain('pos-l6-0')
  })

  it('should handle undefined children gracefully', () => {
    const node: TreeItem = {
      id: 'node-1',
      name: 'Test Node',
      type: 'unit',
      positions: [createMockPosition('pos-1', 'Position 1')],
      total_positions: 1
      // children is undefined
    }

    const result = collectAllPositionIdsRecursive(node)

    expect(result).toHaveLength(1)
    expect(result).toContain('pos-1')
  })

  it('should handle multiple children branches', () => {
    // Create tree with 2 branches
    const branch1 = createMockTreeItem('branch1', 'department', 2, [])
    const branch2 = createMockTreeItem('branch2', 'department', 3, [])
    const root = createMockTreeItem('root', 'division', 5, [branch1, branch2])

    const result = collectAllPositionIdsRecursive(root)

    // Should have 5 + 2 + 3 = 10 positions
    expect(result).toHaveLength(10)
  })

  it('should not duplicate position IDs', () => {
    const node = createMockTreeItem('node-1', 'unit', 5, [])
    const result = collectAllPositionIdsRecursive(node)

    // Check for uniqueness
    const uniqueIds = new Set(result)
    expect(uniqueIds.size).toBe(result.length)
  })
})

describe('OrganizationTree - Selection Logic', () => {
  describe('Direct selection', () => {
    it('should only select direct positions', () => {
      const child = createMockTreeItem('child', 'unit', 3, [])
      const parent = createMockTreeItem('parent', 'department', 5, [child])

      // Direct positions should only include parent's 5 positions
      expect(parent.positions).toHaveLength(5)
      expect(parent.positions?.map(p => p.position_id)).toEqual([
        'pos-parent-0',
        'pos-parent-1',
        'pos-parent-2',
        'pos-parent-3',
        'pos-parent-4'
      ])
    })

    it('should handle node without positions', () => {
      const node = createMockTreeItem('node-1', 'block', 0, [])
      expect(node.positions).toBeUndefined()
    })
  })

  describe('Recursive selection', () => {
    it('should select all positions including nested', () => {
      const child = createMockTreeItem('child', 'unit', 3, [])
      const parent = createMockTreeItem('parent', 'department', 5, [child])

      const allIds = collectAllPositionIdsRecursive(parent)

      // Should have 5 + 3 = 8 positions
      expect(allIds).toHaveLength(8)
      expect(parent.total_positions).toBe(8)
    })

    it('should match total_positions count', () => {
      const grandchild = createMockTreeItem('grandchild', 'unit', 2, [])
      const child = createMockTreeItem('child', 'department', 3, [grandchild])
      const parent = createMockTreeItem('parent', 'block', 5, [child])

      const allIds = collectAllPositionIdsRecursive(parent)

      expect(allIds.length).toBe(parent.total_positions)
      expect(parent.total_positions).toBe(10) // 5 + 3 + 2
    })
  })

  describe('Edge cases', () => {
    it('should handle empty tree', () => {
      const emptyNode = createMockTreeItem('empty', 'unit', 0, [])
      const result = collectAllPositionIdsRecursive(emptyNode)

      expect(result).toEqual([])
    })

    it('should handle single position', () => {
      const node = createMockTreeItem('node-1', 'unit', 1, [])
      const result = collectAllPositionIdsRecursive(node)

      expect(result).toHaveLength(1)
    })

    it('should handle node with only nested positions (no direct)', () => {
      const child = createMockTreeItem('child', 'unit', 5, [])
      const parent = createMockTreeItem('parent', 'department', 0, [child])

      expect(parent.positions).toBeUndefined()
      expect(parent.total_positions).toBe(5)

      const allIds = collectAllPositionIdsRecursive(parent)
      expect(allIds).toHaveLength(5)
    })
  })
})

describe('OrganizationTree - TreeItem type safety', () => {
  it('should enforce valid node types', () => {
    const validTypes: TreeItem['type'][] = ['division', 'block', 'department', 'unit']

    validTypes.forEach(type => {
      const node = createMockTreeItem('test', type, 1, [])
      expect(node.type).toBe(type)
    })
  })

  it('should have correct total_positions calculation', () => {
    const leaf1 = createMockTreeItem('leaf1', 'unit', 5, [])
    const leaf2 = createMockTreeItem('leaf2', 'unit', 3, [])
    const parent = createMockTreeItem('parent', 'department', 2, [leaf1, leaf2])

    expect(parent.total_positions).toBe(10) // 2 + 5 + 3
  })
})

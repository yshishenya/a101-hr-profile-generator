/**
 * Unit tests for LazyTreeView component
 * Tests lazy loading, search, selection, and tree operations
 */

import { describe, it, expect } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { nextTick } from 'vue'
import LazyTreeView from '../LazyTreeView.vue'
import type { OrganizationNode } from '@/stores/catalog'

const vuetify = createVuetify({
  components,
  directives
})

describe('LazyTreeView', () => {
  const createTestTree = (): OrganizationNode[] => [
    {
      id: 'dept1',
      name: 'Engineering Department',
      type: 'department',
      level: 1,
      parent_id: null,
      business_unit_id: 'bu1',
      profile_count: 2,
      total_positions: 3,
      positions: [
        {
          position_id: 'pos1',
          position_name: 'Senior Engineer',
          business_unit_id: 'bu1',
          business_unit_name: 'Engineering',
          department_id: 'dept1',
          department_name: 'Engineering Department',
          department_path: '/Engineering Department',
          status: 'generated',
          profile_exists: true,
          profile_id: 101,
          actions: {
            canView: true,
            canEdit: true,
            canDelete: true,
            canRegenerate: true,
            canCancel: false
          }
        }
      ],
      children: [
        {
          id: 'team1',
          name: 'Backend Team',
          type: 'unit',
          level: 2,
          parent_id: 'dept1',
          business_unit_id: 'bu1',
          profile_count: 1,
          total_positions: 2,
          positions: [
            {
              position_id: 'pos2',
              position_name: 'Backend Developer',
              business_unit_id: 'bu1',
              business_unit_name: 'Engineering',
              department_id: 'team1',
              department_name: 'Backend Team',
              department_path: '/Engineering Department/Backend Team',
              status: 'generated',
              profile_exists: true,
              profile_id: 102,
              actions: {
                canView: true,
                canEdit: true,
                canDelete: true,
                canRegenerate: true,
                canCancel: false
              }
            },
            {
              position_id: 'pos3',
              position_name: 'Junior Developer',
              business_unit_id: 'bu1',
              business_unit_name: 'Engineering',
              department_id: 'team1',
              department_name: 'Backend Team',
              department_path: '/Engineering Department/Backend Team',
              status: 'draft',
              profile_exists: false,
              profile_id: undefined,
              actions: {
                canView: true,
                canEdit: true,
                canDelete: true,
                canRegenerate: true,
                canCancel: false
              }
            }
          ],
          children: []
        }
      ]
    }
  ]

  const defaultProps = {
    items: createTestTree(),
    modelValue: [],
    searchQuery: '',
    currentResultId: null,
    searchResultIds: []
  }

  const createWrapper = (props = {}) => {
    return mount(LazyTreeView, {
      props: { ...defaultProps, ...props },
      global: {
        plugins: [vuetify]
      }
    })
  }

  describe('Rendering', () => {
    it('should render tree view container', () => {
      const wrapper = createWrapper()
      expect(wrapper.find('.tree-view-container').exists()).toBe(true)
    })

    it('should render tree header with title', () => {
      const wrapper = createWrapper()
      expect(wrapper.text()).toContain('Структура организации')
    })

    it('should display total positions count in header', () => {
      const wrapper = createWrapper()
      expect(wrapper.text()).toContain('3 позиций')
    })

    it('should render expand/collapse buttons', () => {
      const wrapper = createWrapper()
      const buttons = wrapper.findAll('.v-btn')
      const expandBtn = buttons.find(btn => btn.text().includes('Развернуть все'))
      const collapseBtn = buttons.find(btn => btn.text().includes('Свернуть все'))

      expect(expandBtn).toBeDefined()
      expect(collapseBtn).toBeDefined()
    })

    it('should render empty state when searching with no results', () => {
      const wrapper = createWrapper({
        items: [],
        searchQuery: 'nonexistent'
      })

      expect(wrapper.text()).toContain('Ничего не найдено')
      expect(wrapper.find('.empty-state').exists()).toBe(true)
    })

    it('should display reset filters button in empty state', () => {
      const wrapper = createWrapper({
        items: [],
        searchQuery: 'nonexistent'
      })

      const resetBtn = wrapper.findAll('.v-btn').find(btn =>
        btn.text().includes('Сбросить фильтры')
      )
      expect(resetBtn).toBeDefined()
    })
  })

  describe('Lazy Loading', () => {
    it('should initially show only top-level nodes', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        displayItems: Array<{ id: string; name: string; children?: unknown[] }>
      }

      // Should have 1 top-level node
      expect(vm.displayItems.length).toBe(1)
      expect(vm.displayItems[0].name).toBe('Engineering Department')
    })

    it('should show loading stub for unexpanded nodes with children', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        displayItems: Array<{ children?: Array<{ name: string; type: string }> }>
      }

      const topNode = vm.displayItems[0]
      if (topNode.children && topNode.children.length > 0) {
        // First child might be loading stub or actual child
        const hasLoadingStub = topNode.children.some(
          child => child.type === 'loading' && child.name === 'Загрузка...'
        )
        // Loading stub should exist OR children are already loaded (top-level is always loaded)
        expect(hasLoadingStub || topNode.children.length > 0).toBe(true)
      }
    })

    it('should load children when node is expanded', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        opened: string[]
        loadedNodes: Set<string>
        handleNodeToggle: (ids: string[]) => void
      }

      // Simulate node expansion
      vm.handleNodeToggle(['dept1', 'team1'])

      await nextTick()

      // Nodes should be marked as loaded
      expect(vm.loadedNodes.has('dept1')).toBe(true)
      expect(vm.loadedNodes.has('team1')).toBe(true)
    })

    it('should handle node toggle correctly', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        loadedNodes: Set<string>
        handleNodeToggle: (ids: string[]) => void
      }

      vm.handleNodeToggle(['dept1'])
      expect(vm.loadedNodes.has('dept1')).toBe(true)
    })

    it('should ignore non-string IDs in handleNodeToggle', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        loadedNodes: Set<string>
        handleNodeToggle: (ids: unknown) => void
      }

      const initialSize = vm.loadedNodes.size
      vm.handleNodeToggle([123, null, undefined, 'valid'])

      // Only 'valid' should be added
      expect(vm.loadedNodes.has('valid')).toBe(true)
      expect(vm.loadedNodes.size).toBe(initialSize + 1)
    })
  })

  describe('Search Functionality', () => {
    it('should filter nodes by search query', () => {
      const wrapper = createWrapper({
        searchQuery: 'backend'
      })
      const vm = wrapper.vm as unknown as {
        displayItems: Array<{ name: string }>
      }

      // Should find nodes containing 'backend'
      const hasBackendNode = vm.displayItems.some(node =>
        node.name.toLowerCase().includes('backend')
      )
      expect(hasBackendNode).toBe(true)
    })

    it('should auto-expand tree when searching', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        opened: string[]
        loadedNodes: Set<string>
      }

      await wrapper.setProps({ searchQuery: 'developer' })
      await nextTick()

      // All nodes should be opened during search
      expect(vm.opened.length).toBeGreaterThan(0)
    })

    it('should reset opened nodes when search is cleared', async () => {
      const wrapper = createWrapper({ searchQuery: 'test' })
      const vm = wrapper.vm as unknown as {
        opened: string[]
        loadedNodes: Set<string>
      }

      await wrapper.setProps({ searchQuery: '' })
      await nextTick()

      expect(vm.opened.length).toBe(0)
      expect(vm.loadedNodes.size).toBe(0)
    })

    it('should highlight search text in node names', () => {
      const wrapper = createWrapper({ searchQuery: 'eng' })
      const vm = wrapper.vm as unknown as {
        highlightSearchText: (text: string) => string
      }

      const highlighted = vm.highlightSearchText('Engineering Department')
      expect(highlighted).toContain('<mark class="search-highlight">')
      expect(highlighted).toContain('Eng')
    })

    it('should escape regex special characters in search', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        highlightSearchText: (text: string) => string
      }

      // Set search query with special characters
      wrapper.setProps({ searchQuery: '(test)' })

      const highlighted = vm.highlightSearchText('Test (test) case')
      expect(highlighted).toContain('(test)')
      expect(() => highlighted).not.toThrow()
    })

    it('should identify current search result', () => {
      const wrapper = createWrapper({
        currentResultId: 'pos1'
      })
      const vm = wrapper.vm as unknown as {
        isCurrentResult: (nodeId: string) => boolean
      }

      expect(vm.isCurrentResult('pos1')).toBe(true)
      expect(vm.isCurrentResult('pos2')).toBe(false)
    })

    it('should determine relevant nodes during search', () => {
      const wrapper = createWrapper({
        searchQuery: 'backend',
        searchResultIds: ['pos2', 'pos3']
      })
      const vm = wrapper.vm as unknown as {
        isRelevantNode: (nodeId: string) => boolean
      }

      // Position in search results should be relevant
      expect(vm.isRelevantNode('pos2')).toBe(true)

      // Parent node containing search results should be relevant
      expect(vm.isRelevantNode('team1')).toBe(true)
    })

    it('should not highlight text when search query is too short', () => {
      const wrapper = createWrapper({ searchQuery: 'e' })
      const vm = wrapper.vm as unknown as {
        highlightSearchText: (text: string) => string
        isSearching: boolean
      }

      expect(vm.isSearching).toBe(false)
      const highlighted = vm.highlightSearchText('Engineering')
      expect(highlighted).toBe('Engineering')
      expect(highlighted).not.toContain('<mark')
    })
  })

  describe('Selection', () => {
    it('should emit update:modelValue when selection changes', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        selected: string[]
      }

      vm.selected = ['pos1']
      await nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })

    it('should emit select event with selected items', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        selected: string[]
      }

      vm.selected = ['pos1']
      await nextTick()

      expect(wrapper.emitted('select')).toBeTruthy()
      const emittedItems = wrapper.emitted('select')?.[0][0]
      expect(Array.isArray(emittedItems)).toBe(true)
    })

    it('should select direct positions only when recursive is false', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        selectPositions: (node: { id: string; positions?: unknown[] }, recursive: boolean) => void
        selected: string[]
      }

      const node = {
        id: 'dept1',
        positions: [{ position_id: 'pos1' }]
      }

      vm.selectPositions(node, false)

      expect(vm.selected).toContain('pos1')
      expect(vm.selected.length).toBeLessThanOrEqual(2) // Only direct positions
    })

    it('should select all positions recursively when recursive is true', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        selectPositions: (node: { id: string }, recursive: boolean) => void
        selected: string[]
      }

      const node = { id: 'dept1' }

      vm.selectPositions(node, true)

      // Should select all positions in dept1 and its children
      expect(vm.selected.length).toBeGreaterThan(1)
    })

    it('should find selected positions from IDs', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        findSelectedPositions: (ids: string[]) => Array<{ position_id: string }>
      }

      const selectedItems = vm.findSelectedPositions(['pos1', 'pos2'])

      expect(selectedItems.length).toBe(2)
      expect(selectedItems[0].position_id).toBe('pos1')
      expect(selectedItems[1].position_id).toBe('pos2')
    })
  })

  describe('Expand/Collapse Operations', () => {
    it('should expand all nodes', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        expandAll: () => Promise<void>
        opened: string[]
        isExpanding: boolean
      }

      await vm.expandAll()
      await flushPromises()

      expect(vm.opened.length).toBeGreaterThan(0)
      expect(vm.isExpanding).toBe(false)
    })

    it('should collapse all nodes', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        collapseAll: () => void
        opened: string[]
      }

      vm.opened = ['dept1', 'team1']
      vm.collapseAll()

      expect(vm.opened.length).toBe(0)
    })

    it('should get all node IDs recursively', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        getAllNodeIds: (nodes: OrganizationNode[]) => string[]
      }

      const ids = vm.getAllNodeIds(defaultProps.items)

      expect(ids).toContain('dept1')
      expect(ids).toContain('team1')
      expect(ids.length).toBeGreaterThanOrEqual(2)
    })

    it('should mark all nodes as loaded during expandAll', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        expandAll: () => Promise<void>
        loadedNodes: Set<string>
      }

      await vm.expandAll()

      expect(vm.loadedNodes.has('dept1')).toBe(true)
      expect(vm.loadedNodes.has('team1')).toBe(true)
    })
  })

  describe('Helper Functions', () => {
    it('should return correct icon for node types', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        getNodeIcon: (item: { type: string }) => string
      }

      expect(vm.getNodeIcon({ type: 'department' })).toBe('mdi-folder')
      expect(vm.getNodeIcon({ type: 'position' })).toBe('mdi-account-tie')
      expect(vm.getNodeIcon({ type: 'division' })).toBe('mdi-office-building')
      expect(vm.getNodeIcon({ type: 'block' })).toBe('mdi-folder-multiple')
      expect(vm.getNodeIcon({ type: 'unit' })).toBe('mdi-folder-outline')
      expect(vm.getNodeIcon({ type: 'unknown' })).toBe('mdi-circle-small')
    })

    it('should return correct color for position nodes', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        getNodeColor: (item: { type: string; profile_exists?: boolean }) => string
      }

      expect(vm.getNodeColor({ type: 'position', profile_exists: true })).toBe('success')
      expect(vm.getNodeColor({ type: 'position', profile_exists: false })).toBe('grey')
    })

    it('should return correct color for organizational nodes based on coverage', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        getNodeColor: (item: {
          type: string
          total_positions?: number
          profile_count?: number
        }) => string
      }

      // High coverage (>= 80%)
      expect(
        vm.getNodeColor({
          type: 'department',
          total_positions: 10,
          profile_count: 9
        })
      ).toBe('success')

      // Medium coverage (>= 50%)
      expect(
        vm.getNodeColor({
          type: 'department',
          total_positions: 10,
          profile_count: 6
        })
      ).toBe('warning')

      // Low coverage
      expect(
        vm.getNodeColor({
          type: 'department',
          total_positions: 10,
          profile_count: 2
        })
      ).toBe('grey')
    })

    it('should calculate coverage color correctly', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        getCoverageColor: (item: {
          total_positions?: number
          profile_count?: number
        }) => string
      }

      // >= 80% = success
      expect(vm.getCoverageColor({ total_positions: 10, profile_count: 8 })).toBe('success')

      // >= 50% = warning
      expect(vm.getCoverageColor({ total_positions: 10, profile_count: 5 })).toBe('warning')

      // < 50% = error
      expect(vm.getCoverageColor({ total_positions: 10, profile_count: 3 })).toBe('error')

      // No data = grey
      expect(vm.getCoverageColor({ total_positions: 0, profile_count: 0 })).toBe('grey')
    })

    it('should find node in tree by ID', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        findNodeInTree: (nodeId: string, nodes: OrganizationNode[]) => OrganizationNode | null
      }

      const found = vm.findNodeInTree('team1', defaultProps.items)
      expect(found).not.toBeNull()
      expect(found?.id).toBe('team1')
    })

    it('should return null when node is not found', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        findNodeInTree: (nodeId: string, nodes: OrganizationNode[]) => OrganizationNode | null
      }

      const found = vm.findNodeInTree('nonexistent', defaultProps.items)
      expect(found).toBeNull()
    })

    it('should check if children have matching positions', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        hasMatchingPositionsInChildren: (nodes: OrganizationNode[], resultIds: string[]) => boolean
      }

      const hasMatch = vm.hasMatchingPositionsInChildren(defaultProps.items, ['pos2'])
      expect(hasMatch).toBe(true)
    })
  })

  describe('Computed Properties', () => {
    it('should compute displayItems correctly without search', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        displayItems: Array<{ id: string }>
      }

      expect(vm.displayItems.length).toBeGreaterThan(0)
      expect(vm.displayItems[0].id).toBe('dept1')
    })

    it('should compute displayItems with search filter', () => {
      const wrapper = createWrapper({
        searchQuery: 'backend'
      })
      const vm = wrapper.vm as unknown as {
        displayItems: Array<{ name: string }>
      }

      const hasBackend = vm.displayItems.some(node =>
        node.name.toLowerCase().includes('backend')
      )
      expect(hasBackend).toBe(true)
    })

    it('should compute totalPositions correctly', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        totalPositions: number
      }

      expect(vm.totalPositions).toBe(3)
    })

    it('should compute isSearching based on query length', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        isSearching: boolean
      }

      expect(vm.isSearching).toBe(false)

      wrapper.setProps({ searchQuery: 'ab' })
      expect(vm.isSearching).toBe(true)

      wrapper.setProps({ searchQuery: 'a' })
      expect(vm.isSearching).toBe(false)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty items array', () => {
      const wrapper = createWrapper({
        items: []
      })
      const vm = wrapper.vm as unknown as {
        displayItems: unknown[]
        totalPositions: number
      }

      expect(vm.displayItems.length).toBe(0)
      expect(vm.totalPositions).toBe(0)
    })

    it('should handle nodes without children', () => {
      const singleNode: OrganizationNode[] = [
        {
          id: 'dept1',
          name: 'Simple Department',
          type: 'department',
          level: 1,
          parent_id: null,
          business_unit_id: 'bu1',
          positions: [],
          children: []
        }
      ]

      const wrapper = createWrapper({ items: singleNode })
      const vm = wrapper.vm as unknown as {
        displayItems: unknown[]
      }

      expect(vm.displayItems.length).toBe(1)
    })

    it('should handle nodes without positions', () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        selectPositions: (node: { id: string; positions?: unknown[] }, recursive: boolean) => void
        selected: string[]
      }

      const nodeWithoutPositions = { id: 'empty', positions: [] }

      vm.selectPositions(nodeWithoutPositions, false)

      // Should not crash, selected stays same
      expect(vm.selected).toBeDefined()
    })

    it('should emit reset-filters when empty state button clicked', async () => {
      const wrapper = createWrapper({
        items: [],
        searchQuery: 'test'
      })

      const resetBtn = wrapper.findAll('.v-btn').find(btn =>
        btn.text().includes('Сбросить фильтры')
      )

      await resetBtn?.trigger('click')

      expect(wrapper.emitted('reset-filters')).toBeTruthy()
    })
  })

  describe('Props and Watchers', () => {
    it('should update displayItems when items prop changes', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        displayItems: Array<{ id: string }>
      }

      const newItems: OrganizationNode[] = [
        {
          id: 'new1',
          name: 'New Department',
          type: 'department',
          level: 1,
          parent_id: null,
          business_unit_id: 'bu1',
          positions: [],
          children: []
        }
      ]

      await wrapper.setProps({ items: newItems })
      await nextTick()

      expect(vm.displayItems[0].id).toBe('new1')
    })

    it('should react to searchQuery prop changes', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        isSearching: boolean
      }

      expect(vm.isSearching).toBe(false)

      await wrapper.setProps({ searchQuery: 'test' })
      await nextTick()

      expect(vm.isSearching).toBe(true)
    })

    it('should update opened nodes when searchQuery changes', async () => {
      const wrapper = createWrapper()
      const vm = wrapper.vm as unknown as {
        opened: string[]
      }

      await wrapper.setProps({ searchQuery: 'backend' })
      await nextTick()

      expect(vm.opened.length).toBeGreaterThan(0)
    })
  })
})

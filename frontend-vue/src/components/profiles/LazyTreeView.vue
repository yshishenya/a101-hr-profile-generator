<template>
  <v-card flat class="tree-view-container">
    <!-- Tree Header -->
    <div class="tree-header px-4 py-3 d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon class="mr-2">mdi-file-tree</v-icon>
        <span class="text-subtitle-1 font-weight-medium">Структура организации</span>
        <v-chip v-if="totalPositions > 0" size="small" class="ml-2" variant="tonal">
          {{ totalPositions }} позиций
        </v-chip>
      </div>

      <!-- Tree Controls -->
      <div class="d-flex gap-2">
        <v-btn
          size="small"
          variant="text"
          prepend-icon="mdi-chevron-down"
          :loading="isExpanding"
          @click="expandAll"
        >
          Развернуть все
        </v-btn>
        <v-btn
          size="small"
          variant="text"
          prepend-icon="mdi-chevron-up"
          @click="collapseAll"
        >
          Свернуть все
        </v-btn>
      </div>
    </div>

    <v-divider />

    <!-- Tree Content with INSTANT loading -->
    <div class="tree-content" style="height: calc(100vh - 400px); overflow-y: auto;">
      <!-- Empty State: No Search Results -->
      <div v-if="isSearching && displayItems.length === 0" class="empty-state pa-8 text-center">
        <v-icon size="64" color="grey-lighten-1" class="mb-4">
          mdi-text-search
        </v-icon>
        <h3 class="text-h6 mb-2">Ничего не найдено</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">
          По запросу <strong>"{{ searchQuery }}"</strong> не найдено ни одной позиции.
        </p>
        <p class="text-body-2 text-medium-emphasis mb-4">
          Попробуйте изменить запрос или сбросить фильтры.
        </p>
        <v-btn
          variant="outlined"
          color="primary"
          prepend-icon="mdi-filter-off"
          @click="$emit('reset-filters')"
        >
          Сбросить фильтры
        </v-btn>
      </div>

      <!-- Show only TOP LEVEL nodes initially - children load on expand -->
      <v-treeview
        v-else-if="displayItems.length > 0"
        ref="treeRef"
        v-model:activated="activated"
        v-model:selected="selected"
        v-model:opened="opened"
        :items="displayItems"
        item-value="id"
        item-title="name"
        :selectable="true"
        :activatable="false"
        density="compact"
        color="primary"
        @update:opened="handleNodeToggle"
      >
        <template #prepend="{ item }">
          <v-icon :color="getNodeColor(item)" size="small">
            {{ getNodeIcon(item) }}
          </v-icon>
        </template>

        <template #title="{ item }">
          <div
            class="d-flex align-center tree-node-title"
            :class="{
              'search-highlight-active': isCurrentResult(item.id),
              'tree-node-dimmed': isSearching && !isRelevantNode(item.id)
            }"
          >
            <!-- Highlighted name -->
            <span
              class="text-body-2"
              v-html="highlightSearchText(item.name)"
            />

            <!-- Coverage badge (only for organizational nodes) -->
            <v-chip
              v-if="item.type !== 'position' && item.total_positions && item.total_positions > 0"
              size="x-small"
              class="ml-2"
              :color="getCoverageColor(item)"
              variant="flat"
            >
              {{ item.profile_count || 0 }}/{{ item.total_positions }}
            </v-chip>

            <!-- Profile status badge (only for positions) -->
            <v-chip
              v-if="item.type === 'position'"
              size="x-small"
              class="ml-2"
              :color="item.profile_exists ? 'success' : 'grey'"
              variant="flat"
            >
              {{ item.profile_exists ? 'Есть профиль' : 'Нет профиля' }}
            </v-chip>
          </div>
        </template>

        <template #append="{ item }">
          <!-- Selection buttons -->
          <div v-if="item.positions && item.positions.length > 0" class="d-flex gap-1">
            <v-btn
              size="x-small"
              variant="outlined"
              @click.stop="selectPositions(item, false)"
            >
              {{ item.positions.length }}
            </v-btn>
          </div>
          <div v-if="item.total_positions && item.total_positions > 0" class="d-flex gap-1">
            <v-btn
              size="x-small"
              variant="tonal"
              @click.stop="selectPositions(item, true)"
            >
              Всё {{ item.total_positions }}
            </v-btn>
          </div>
        </template>
      </v-treeview>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { OrganizationNode, SearchableItem } from '@/stores/catalog'

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  searchQuery: '',
  currentResultId: null,
  searchResultIds: () => []
})
// Emits
const emit = defineEmits<{
  'update:modelValue': [value: SearchableItem[]]
  'select': [items: SearchableItem[]]
  'reset-filters': []
}>()
// Constants
const MIN_SEARCH_LENGTH = 2
const EXPAND_DELAY_MS = 50

// Types
/**
 * Tree node format compatible with v-treeview
 */
interface TreeNode {
  id: string
  name: string
  type: string
  positions?: SearchableItem[]
  profile_count?: number
  total_positions?: number
  profile_exists?: boolean
  profile_id?: number
  position_data?: SearchableItem
  children?: TreeNode[]
}

// Props
interface Props {
  items: OrganizationNode[]
  modelValue?: SearchableItem[]
  searchQuery?: string
  currentResultId?: string | null
  searchResultIds?: string[]
}

// Refs
const treeRef = ref()
const activated = ref<string[]>([])
const selected = ref<string[]>([])
const opened = ref<string[]>([])
const isExpanding = ref(false)
const loadedNodes = ref<Set<string>>(new Set())

// Computed - Process items with lazy loading
const displayItems = computed(() => {
  if (props.searchQuery) {
    // When searching, show all results (filtered)
    return filterNodes(props.items, props.searchQuery)
  }

  // Initial load: show only TOP LEVEL with children stubs
  return props.items.map(node => createLazyNode(node, true))
})

const totalPositions = computed(() => {
  return countPositions(props.items)
})

const isSearching = computed(() => {
  return props.searchQuery && props.searchQuery.length >= MIN_SEARCH_LENGTH
})

// Watch for selection changes
watch(selected, (newValue) => {
  const selectedItems = findSelectedPositions(newValue)
  emit('update:modelValue', selectedItems)
  emit('select', selectedItems)
})

// Watch for search query changes - auto-expand tree
watch(() => props.searchQuery, (newQuery) => {
  if (newQuery && newQuery.length >= MIN_SEARCH_LENGTH) {
    // Auto-expand all nodes when searching
    const allIds = getAllNodeIds(props.items)
    opened.value = allIds

    // Mark all nodes as loaded
    allIds.forEach(id => loadedNodes.value.add(id))
  } else {
    // Reset when search is cleared
    opened.value = []
    loadedNodes.value.clear()
  }
})

// Methods
/**
 * Creates lazy-loaded tree node with children stubs
 * Children are only loaded when node is expanded for better performance
 *
 * @param node - Organization node to convert
 * @param isTopLevel - Whether this is a top-level node (always loaded)
 * @returns Tree node object compatible with v-treeview
 */
function createLazyNode(node: OrganizationNode, isTopLevel = false): TreeNode {
  const hasChildren = node.children && node.children.length > 0
  const hasPositions = node.positions && node.positions.length > 0
  const isLoaded = loadedNodes.value.has(node.id) || isTopLevel

  // Build children array
  let children: TreeNode[] | undefined = undefined

  if (isLoaded || opened.value.includes(node.id)) {
    // Node is expanded - show actual children
    children = []

    // Add organizational children (departments, units, etc.)
    if (hasChildren) {
      children.push(...node.children!.map(child => createLazyNode(child)))
    }

    // Add positions as leaf nodes
    if (hasPositions) {
      const positionNodes = node.positions!.map(position => ({
        id: position.position_id,
        name: position.position_name,
        type: 'position',
        profile_exists: position.profile_exists,
        profile_id: position.profile_id,
        position_data: position, // Keep original position data for selection
        children: undefined // Positions are leaf nodes
      }))
      children.push(...positionNodes)
    }
  } else if (hasChildren || hasPositions) {
    // Node not expanded yet - show loading stub
    children = [{ id: `${node.id}-loading`, name: 'Загрузка...', type: 'loading' }]
  }

  return {
    id: node.id,
    name: node.name,
    type: node.type,
    positions: node.positions,
    profile_count: node.profile_count,
    total_positions: node.total_positions,
    children
  }
}

/**
 * Handles node expand/collapse events from v-treeview
 * Marks newly opened nodes as loaded to trigger children rendering
 *
 * @param openedIds - Array of opened node IDs from v-treeview
 */
function handleNodeToggle(openedIds: unknown): void {
  // Mark newly opened nodes as loaded
  const ids = Array.isArray(openedIds) ? openedIds : []
  for (const id of ids) {
    if (typeof id === 'string' && !loadedNodes.value.has(id)) {
      loadedNodes.value.add(id)
    }
  }
}

/**
 * Recursively filters organization tree by search query
 * Returns only nodes and positions matching the query
 * Positions are converted to leaf nodes for tree rendering
 *
 * @param nodes - Organization nodes to filter
 * @param query - Search query (case-insensitive)
 * @returns Filtered tree nodes array
 */
function filterNodes(nodes: OrganizationNode[], query: string): TreeNode[] {
  const lowerQuery = query.toLowerCase().trim()

  return nodes.reduce<TreeNode[]>((acc, node) => {
    const nameMatches = node.name.toLowerCase().includes(lowerQuery)
    const matchingPositions = node.positions?.filter(pos =>
      pos.position_name.toLowerCase().includes(lowerQuery) ||
      pos.department_name?.toLowerCase().includes(lowerQuery)
    )
    const filteredChildren = node.children ? filterNodes(node.children, query) : []

    if (nameMatches || (matchingPositions && matchingPositions.length > 0) || filteredChildren.length > 0) {
      // Build children array with positions as nodes
      const children: TreeNode[] = []

      // Add filtered organizational children
      if (filteredChildren.length > 0) {
        children.push(...filteredChildren)
      } else if (node.children) {
        // If no filtered children but node has children, recursively filter them
        const allChildrenFiltered = filterNodes(node.children, query)
        children.push(...allChildrenFiltered)
      }

      // Add matching positions as leaf nodes
      const positions = nameMatches ? node.positions : matchingPositions
      if (positions && positions.length > 0) {
        const positionNodes = positions.map(position => ({
          id: position.position_id,
          name: position.position_name,
          type: 'position',
          profile_exists: position.profile_exists,
          profile_id: position.profile_id,
          position_data: position,
          children: undefined
        }))
        children.push(...positionNodes)
      }

      acc.push({
        id: node.id,
        name: node.name,
        type: node.type,
        positions: node.positions,
        profile_count: node.profile_count,
        total_positions: node.total_positions,
        children: children.length > 0 ? children : undefined
      })
    }

    return acc
  }, [])
}

function countPositions(nodes: OrganizationNode[]): number {
  let count = 0

  function traverse(items: OrganizationNode[]): void {
    for (const node of items) {
      if (node.positions) {
        count += node.positions.length
      }
      if (node.children) {
        traverse(node.children)
      }
    }
  }

  traverse(nodes)
  return count
}

function findSelectedPositions(selectedIds: string[]): SearchableItem[] {
  const items: SearchableItem[] = []
  const selectedSet = new Set(selectedIds)

  function traverse(nodes: OrganizationNode[]): void {
    for (const node of nodes) {
      // Check positions in this node
      if (node.positions) {
        for (const position of node.positions) {
          if (selectedSet.has(position.position_id)) {
            items.push(position)
          }
        }
      }
      // Traverse children
      if (node.children) {
        traverse(node.children)
      }
    }
  }

  traverse(props.items)
  return items
}

function selectPositions(node: TreeNode, recursive: boolean): void {
  const positionIds: string[] = []

  if (recursive) {
    // Select all positions recursively
    function collectIds(n: OrganizationNode): void {
      if (n.positions) {
        positionIds.push(...n.positions.map(p => p.position_id))
      }
      if (n.children) {
        n.children.forEach(collectIds)
      }
    }

    // Find original node from props.items using findNodeInTree
    const originalNode = findNodeInTree(node.id, props.items)
    if (originalNode) {
      collectIds(originalNode)
    }
  } else {
    // Select only direct positions
    if (node.positions) {
      positionIds.push(...node.positions.map((p: SearchableItem) => p.position_id))
    }
  }

  // Add to selection
  selected.value = [...new Set([...selected.value, ...positionIds])]
}

function getAllNodeIds(nodes: OrganizationNode[]): string[] {
  const ids: string[] = []
  for (const node of nodes) {
    ids.push(node.id)
    if (node.children) {
      ids.push(...getAllNodeIds(node.children))
    }
  }
  return ids
}

async function expandAll(): Promise<void> {
  isExpanding.value = true

  // Mark all nodes as loaded
  function markAllLoaded(nodes: OrganizationNode[]): void {
    for (const node of nodes) {
      loadedNodes.value.add(node.id)
      if (node.children) {
        markAllLoaded(node.children)
      }
    }
  }

  markAllLoaded(props.items)

  // Wait for Vue to update
  await new Promise(resolve => setTimeout(resolve, EXPAND_DELAY_MS))

  // Expand all nodes
  opened.value = getAllNodeIds(props.items)

  isExpanding.value = false
}

function collapseAll(): void {
  opened.value = []
}

function getNodeIcon(item: TreeNode): string {
  switch (item.type) {
    case 'division':
      return 'mdi-office-building'
    case 'block':
      return 'mdi-folder-multiple'
    case 'department':
      return 'mdi-folder'
    case 'unit':
      return 'mdi-folder-outline'
    case 'position':
      return 'mdi-account-tie'
    default:
      return 'mdi-circle-small'
  }
}

function getNodeColor(item: TreeNode): string {
  // For position nodes, color based on profile existence
  if (item.type === 'position') {
    return item.profile_exists ? 'success' : 'grey'
  }

  // For organizational nodes, color based on coverage
  if (item.total_positions && item.profile_count) {
    const coverage = item.profile_count / item.total_positions
    if (coverage >= 0.8) return 'success'
    if (coverage >= 0.5) return 'warning'
  }
  return 'grey'
}

function getCoverageColor(item: TreeNode): string {
  if (item.total_positions && item.profile_count) {
    const coverage = item.profile_count / item.total_positions
    if (coverage >= 0.8) return 'success'
    if (coverage >= 0.5) return 'warning'
    return 'error'
  }
  return 'grey'
}

// Search-related methods
/**
 * Highlights search query in text with HTML mark tags
 * Escapes regex special characters for safe rendering
 *
 * @param text - Text to highlight
 * @returns Text with highlighted search query
 */
function highlightSearchText(text: string): string {
  if (!isSearching.value) return text

  const query = props.searchQuery!.trim()
  if (query.length < MIN_SEARCH_LENGTH) return text

  // Escape special regex characters
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escapedQuery})`, 'gi')

  return text.replace(regex, '<mark class="search-highlight">$1</mark>')
}

/**
 * Checks if node is the current active search result
 *
 * @param nodeId - ID of node to check
 * @returns True if this node is current result
 */
function isCurrentResult(nodeId: string): boolean {
  return props.currentResultId === nodeId
}

/**
 * Determines if node should be visible (not dimmed) during search
 * Node is relevant if it matches search or contains matching descendants
 *
 * @param nodeId - ID of node to check
 * @returns True if node is relevant to current search
 */
function isRelevantNode(nodeId: string): boolean {
  // If not searching, all nodes are relevant
  if (!isSearching.value) return true

  // Node is relevant if it's in search results or is a parent/ancestor of a result
  if (!props.searchResultIds || props.searchResultIds.length === 0) return true

  // Check if this node is a search result (for position nodes)
  if (props.searchResultIds.includes(nodeId)) return true

  // For organizational nodes, check if any positions in this node or its descendants match
  // Find the node in the tree
  const node = findNodeInTree(nodeId, props.items)
  if (!node) return false

  // Check if this node has any matching positions
  if (node.positions) {
    const hasMatchingPosition = node.positions.some(pos =>
      props.searchResultIds.includes(pos.position_id)
    )
    if (hasMatchingPosition) return true
  }

  // Check recursively in children
  if (node.children) {
    return hasMatchingPositionsInChildren(node.children, props.searchResultIds)
  }

  return false
}

/**
 * Recursively searches for node by ID in organization tree
 *
 * @param nodeId - ID of node to find
 * @param nodes - Organization nodes to search in
 * @returns Found node or null if not found
 */
function findNodeInTree(nodeId: string, nodes: OrganizationNode[]): OrganizationNode | null {
  for (const node of nodes) {
    if (node.id === nodeId) return node
    if (node.children) {
      const found = findNodeInTree(nodeId, node.children)
      if (found) return found
    }
  }
  return null
}

/**
 * Recursively checks if any positions in node tree match search result IDs
 *
 * @param nodes - Organization nodes to check
 * @param resultIds - Array of search result position IDs
 * @returns True if any descendant positions match
 */
function hasMatchingPositionsInChildren(nodes: OrganizationNode[], resultIds: string[]): boolean {
  for (const node of nodes) {
    // Check positions in this node
    if (node.positions) {
      const hasMatch = node.positions.some(pos => resultIds.includes(pos.position_id))
      if (hasMatch) return true
    }
    // Check children recursively
    if (node.children) {
      if (hasMatchingPositionsInChildren(node.children, resultIds)) return true
    }
  }
  return false
}

// Expose methods
defineExpose({
  expandAll,
  collapseAll
})
</script>

<style scoped>
.tree-view-container {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  height: 100%;
}

.tree-header {
  background: rgba(var(--v-theme-surface), 0.5);
}

.tree-content {
  position: relative;
  min-height: 400px;
}

.empty-state {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.gap-1 {
  gap: 4px;
}

.gap-2 {
  gap: 8px;
}

/* Search highlighting styles */
:deep(.search-highlight) {
  background-color: rgba(255, 213, 79, 0.3);
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 500;
}

.tree-node-title.search-highlight-active {
  background-color: rgba(25, 118, 210, 0.15);
  border: 1px solid rgba(25, 118, 210, 0.4);
  border-radius: 4px;
  padding: 2px 4px;
  margin: -2px -4px;
}

.tree-node-dimmed {
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.tree-node-dimmed:hover {
  opacity: 0.85;
}
</style>

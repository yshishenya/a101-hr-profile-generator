<template>
  <div>
    <!-- Tree view -->
    <v-treeview
      v-model:activated="activated"
      v-model:selected="selected"
      v-model:opened="opened"
      :items="treeItems"
      item-value="id"
      item-title="name"
      :selectable="selectable"
      :activatable="activatable"
      density="compact"
      color="primary"
    >
      <template #prepend="{ item }">
        <v-icon :color="getNodeColor(item)" size="small">
          {{ getNodeIcon(item) }}
        </v-icon>
      </template>

      <template #title="{ item }">
        <div class="d-flex align-center">
          <span class="text-body-2">{{ item.name }}</span>

          <!-- Coverage badge -->
          <v-chip
            v-if="item.total_positions && item.total_positions > 0"
            size="x-small"
            class="ml-2"
            :color="getCoverageColor(item)"
            variant="flat"
          >
            {{ item.profile_count || 0 }}/{{ item.total_positions }}
          </v-chip>

          <!-- Type badge -->
          <v-chip
            size="x-small"
            class="ml-2"
            variant="outlined"
            color="grey"
          >
            {{ item.type }}
          </v-chip>
        </div>
      </template>

      <template #append="{ item }">
        <!-- Actions for nodes with positions -->
        <div v-if="selectable" class="d-flex align-center ga-1">
          <!-- Direct positions buttons (3 breakpoints) -->
          <template v-if="item.positions && item.positions.length > 0">
            <TreeSelectionButton
              v-for="breakpoint in breakpoints"
              :key="`direct-${breakpoint}`"
              mode="direct"
              :breakpoint="breakpoint"
              :count="item.positions.length"
              @click="selectDirectPositions(item)"
            />
          </template>

          <!-- All nested positions buttons (3 breakpoints) -->
          <template v-if="item.total_positions && item.total_positions > 0">
            <TreeSelectionButton
              v-for="breakpoint in breakpoints"
              :key="`all-${breakpoint}`"
              mode="all"
              :breakpoint="breakpoint"
              :count="item.total_positions"
              @click="selectAllNestedPositions(item)"
            />
          </template>
        </div>

        <!-- Generate button for non-selectable mode -->
        <div v-else-if="item.positions && item.positions.length > 0">
          <v-btn
            size="x-small"
            variant="text"
            color="primary"
            @click.stop="$emit('generate-node', item)"
          >
            Generate ({{ item.positions.length }})
          </v-btn>
        </div>
      </template>
    </v-treeview>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { OrganizationNode, SearchableItem } from '@/stores/catalog'
import type { Breakpoint } from '@/constants/treeSelection'
import TreeSelectionButton from './TreeSelectionButton.vue'

// Constants
const breakpoints: Breakpoint[] = ['desktop', 'tablet', 'mobile']

// Props
interface Props {
  items: OrganizationNode[]
  modelValue?: SearchableItem[]
  selectable?: boolean
  activatable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  selectable: true,
  activatable: true
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: SearchableItem[]]
  'select': [items: SearchableItem[]]
  'activate': [item: OrganizationNode]
  'generate-node': [node: OrganizationNode]
}>()

// State
const activated = ref<string[]>([])
const selected = ref<string[]>([])
const opened = ref<string[]>([])

// Computed
const treeItems = computed(() => {
  return transformToTreeviewFormat(props.items)
})

// Watch for external modelValue changes
// BUGFIX-10: Added equality check to prevent infinite reactive loop
watch(() => props.modelValue, (newValue) => {
  const newIds = newValue.map(item => item.position_id)

  // Only update if the selection actually changed
  // This prevents infinite loop: modelValue change → selected change → emit update:modelValue → modelValue change...
  const hasChanged = newIds.length !== selected.value.length ||
                     newIds.some(id => !selected.value.includes(id))

  if (hasChanged) {
    selected.value = newIds
  }
}, { deep: true })

// Watch for selection changes
// BUGFIX-10: Only emit when selection actually changes (not on initial mount)
watch(selected, (newValue, oldValue) => {
  // Skip if values haven't actually changed (prevents unnecessary emissions)
  if (oldValue && newValue.length === oldValue.length &&
      newValue.every(id => oldValue.includes(id))) {
    return
  }

  const selectedItems = findSelectedItems(newValue)
  emit('update:modelValue', selectedItems)
  emit('select', selectedItems)
})

// Watch for activation changes
watch(activated, (newValue) => {
  if (newValue.length > 0) {
    const node = findNodeById(newValue[0], props.items)
    if (node) {
      emit('activate', node)
    }
  }
})


// Types
interface TreeItem {
  id: string
  name: string
  type: 'division' | 'block' | 'department' | 'unit'
  positions?: SearchableItem[]
  profile_count?: number
  total_positions?: number
  children?: TreeItem[]
}

// Methods
function transformToTreeviewFormat(nodes: OrganizationNode[]): TreeItem[] {
  return nodes.map(node => ({
    id: node.id,
    name: node.name,
    type: node.type,
    positions: node.positions,
    profile_count: node.profile_count,
    total_positions: node.total_positions,
    children: node.children ? transformToTreeviewFormat(node.children) : []
  }))
}

function findSelectedItems(selectedIds: string[]): SearchableItem[] {
  const items: SearchableItem[] = []

  function traverse(nodes: OrganizationNode[]): void {
    for (const node of nodes) {
      // Check if any positions in this node are selected
      if (node.positions) {
        for (const position of node.positions) {
          if (selectedIds.includes(position.position_id)) {
            items.push(position)
          }
        }
      }

      // Recursively check children
      if (node.children) {
        traverse(node.children)
      }
    }
  }

  traverse(props.items)
  return items
}

function findNodeById(id: string, nodes: OrganizationNode[]): OrganizationNode | null {
  for (const node of nodes) {
    if (node.id === id) {
      return node
    }

    if (node.children) {
      const found = findNodeById(id, node.children)
      if (found) return found
    }
  }

  return null
}

/**
 * Recursively collect all position IDs from a node and its children
 * @param node - Organization tree node
 * @returns Array of all position IDs (direct + nested)
 */
function collectAllPositionIdsRecursive(node: TreeItem): string[] {
  const ids: string[] = []

  // Add direct positions from current node
  if (node.positions && Array.isArray(node.positions)) {
    ids.push(...node.positions.map((p: SearchableItem) => p.position_id))
  }

  // Recursively collect from children
  if (node.children && Array.isArray(node.children)) {
    for (const child of node.children) {
      ids.push(...collectAllPositionIdsRecursive(child))
    }
  }

  return ids
}

/**
 * Select only direct positions under this node (non-recursive)
 * Toggle behavior: if all selected → deselect, otherwise select all
 */
function selectDirectPositions(node: TreeItem): void {
  if (!node.positions) return

  const positionIds = node.positions.map((p: SearchableItem) => p.position_id)

  // Toggle: if all selected, deselect; otherwise select all
  const allSelected = positionIds.every((id: string) => selected.value.includes(id))

  if (allSelected) {
    selected.value = selected.value.filter(id => !positionIds.includes(id))
  } else {
    selected.value = [...new Set([...selected.value, ...positionIds])]
  }
}

/**
 * Select ALL positions recursively (direct + nested children)
 * Toggle behavior: if all selected → deselect, otherwise select all
 */
function selectAllNestedPositions(node: TreeItem): void {
  const allPositionIds = collectAllPositionIdsRecursive(node)

  if (allPositionIds.length === 0) return

  const allSelected = allPositionIds.every((id: string) => selected.value.includes(id))

  if (allSelected) {
    // Deselect all nested positions
    selected.value = selected.value.filter(id => !allPositionIds.includes(id))
  } else {
    // Select all nested positions
    selected.value = [...new Set([...selected.value, ...allPositionIds])]
  }
}

function getNodeIcon(item: TreeItem): string {
  switch (item.type) {
    case 'division':
      return 'mdi-office-building'
    case 'block':
      return 'mdi-layers'
    case 'department':
      return 'mdi-account-group'
    case 'unit':
      return 'mdi-folder'
    default:
      return 'mdi-circle-small'
  }
}

function getNodeColor(item: TreeItem): string {
  if (!item.total_positions || item.total_positions === 0) {
    return 'grey'
  }

  const coverage = (item.profile_count || 0) / item.total_positions
  if (coverage >= 0.8) return 'success'
  if (coverage >= 0.5) return 'warning'
  return 'error'
}

function getCoverageColor(item: TreeItem): string {
  if (!item.total_positions || item.total_positions === 0) {
    return 'grey'
  }

  const coverage = (item.profile_count || 0) / item.total_positions
  if (coverage >= 0.8) return 'success'
  if (coverage >= 0.5) return 'warning'
  return 'error'
}

// Tree expansion helpers
function getAllNodeIds(nodes: OrganizationNode[]): string[] {
  const ids: string[] = []

  function traverse(nodeList: OrganizationNode[]): void {
    for (const node of nodeList) {
      ids.push(node.id)
      if (node.children && node.children.length > 0) {
        traverse(node.children)
      }
    }
  }

  traverse(nodes)
  return ids
}

function expandAll(): void {
  opened.value = getAllNodeIds(props.items)
}

function collapseAll(): void {
  opened.value = []
}

// Expose methods to parent component
defineExpose({
  expandAll,
  collapseAll
})
</script>

<style scoped>
:deep(.v-treeview-node__root) {
  min-height: 40px;
}

:deep(.v-treeview-node__label) {
  flex: 1;
}
</style>

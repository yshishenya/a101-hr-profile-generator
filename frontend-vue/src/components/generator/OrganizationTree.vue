<template>
  <div>
    <!-- Tree view -->
    <v-treeview
      v-model:activated="activated"
      v-model:selected="selected"
      :items="treeItems"
      item-value="id"
      item-title="name"
      :selectable="selectable"
      :activatable="activatable"
      :open-all="openAll"
      density="compact"
      color="primary"
      return-object
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
        <div v-if="item.positions && item.positions.length > 0" class="d-flex align-center">
          <v-btn
            v-if="selectable"
            size="x-small"
            variant="text"
            @click.stop="selectAllPositions(item)"
          >
            Select All ({{ item.positions.length }})
          </v-btn>

          <v-btn
            v-else
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

// Props
interface Props {
  items: OrganizationNode[]
  modelValue?: SearchableItem[]
  selectable?: boolean
  activatable?: boolean
  openAll?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  selectable: true,
  activatable: true,
  openAll: false
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

// Computed
const treeItems = computed(() => {
  return transformToTreeviewFormat(props.items)
})

// Watch for external modelValue changes
watch(() => props.modelValue, (newValue) => {
  selected.value = newValue.map(item => item.position_id)
})

// Watch for selection changes
watch(selected, (newValue) => {
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

// Methods
function transformToTreeviewFormat(nodes: OrganizationNode[]): any[] {
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

function selectAllPositions(node: any): void {
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

function getNodeIcon(item: any): string {
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

function getNodeColor(item: any): string {
  if (!item.total_positions || item.total_positions === 0) {
    return 'grey'
  }

  const coverage = (item.profile_count || 0) / item.total_positions
  if (coverage >= 0.8) return 'success'
  if (coverage >= 0.5) return 'warning'
  return 'error'
}

function getCoverageColor(item: any): string {
  if (!item.total_positions || item.total_positions === 0) {
    return 'grey'
  }

  const coverage = (item.profile_count || 0) / item.total_positions
  if (coverage >= 0.8) return 'success'
  if (coverage >= 0.5) return 'warning'
  return 'error'
}
</script>

<style scoped>
:deep(.v-treeview-node__root) {
  min-height: 40px;
}

:deep(.v-treeview-node__label) {
  flex: 1;
}
</style>

<template>
  <v-card flat class="tree-view-container">
    <!-- Tree Header -->
    <div class="tree-header px-4 py-3 d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon class="mr-2">mdi-file-tree</v-icon>
        <span class="text-subtitle-1 font-weight-medium">Структура организации</span>
      </div>

      <!-- Tree Controls -->
      <div class="d-flex gap-2">
        <v-btn
          size="small"
          variant="text"
          prepend-icon="mdi-chevron-down"
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

    <!-- Tree Content with Virtual Scrolling -->
    <div class="tree-content" style="height: calc(100vh - 400px); overflow-y: auto;">
      <OrganizationTree
        ref="treeRef"
        v-model="selectedPositions"
        :items="highlightedItems"
        :selectable="true"
        :activatable="false"
        @select="handleSelection"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!items || items.length === 0" class="empty-state pa-8 text-center">
      <v-icon size="64" color="grey-lighten-2">mdi-file-tree</v-icon>
      <div class="text-h6 mt-4 text-medium-emphasis">Нет данных</div>
      <div class="text-body-2 text-medium-emphasis mt-2">
        Структура организации не загружена
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { OrganizationNode, SearchableItem } from '@/stores/catalog'
import OrganizationTree from './OrganizationTree.vue'

// Props
interface Props {
  items: OrganizationNode[]
  modelValue?: SearchableItem[]
  searchQuery?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  searchQuery: ''
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: SearchableItem[]]
  'select': [items: SearchableItem[]]
}>()

// Refs
const treeRef = ref<InstanceType<typeof OrganizationTree> | null>(null)
const selectedPositions = ref<SearchableItem[]>(props.modelValue)

// Computed - Filter and highlight search results
const highlightedItems = computed(() => {
  if (!props.searchQuery || !props.searchQuery.trim()) {
    return props.items
  }

  const query = props.searchQuery.toLowerCase().trim()

  // Recursively filter tree nodes that match search
  function filterNodes(nodes: OrganizationNode[]): OrganizationNode[] {
    return nodes.reduce<OrganizationNode[]>((acc, node) => {
      // Check if node name matches
      const nameMatches = node.name.toLowerCase().includes(query)

      // Check if any positions match
      const matchingPositions = node.positions?.filter(pos =>
        pos.position_name.toLowerCase().includes(query) ||
        pos.department_name?.toLowerCase().includes(query)
      )

      // Check if any children match
      const filteredChildren = node.children ? filterNodes(node.children) : []

      // Include node if it or its children match
      if (nameMatches || (matchingPositions && matchingPositions.length > 0) || filteredChildren.length > 0) {
        acc.push({
          ...node,
          // Include all matching positions or all if node matches
          positions: nameMatches ? node.positions : matchingPositions,
          // Include filtered children
          children: filteredChildren.length > 0 ? filteredChildren : node.children
        })
      }

      return acc
    }, [])
  }

  return filterNodes(props.items)
})

// Methods
function expandAll(): void {
  treeRef.value?.expandAll()
}

function collapseAll(): void {
  treeRef.value?.collapseAll()
}

function handleSelection(items: SearchableItem[]): void {
  selectedPositions.value = items
  emit('update:modelValue', items)
  emit('select', items)
}

// Expose methods for parent component
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
}

.empty-state {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.gap-2 {
  gap: 8px;
}
</style>

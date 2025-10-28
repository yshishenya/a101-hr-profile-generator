<template>
  <v-card flat class="tree-view-container">
    <!-- Tree Header -->
    <div class="tree-header px-4 py-3 d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon class="mr-2">mdi-file-tree</v-icon>
        <span class="text-subtitle-1 font-weight-medium">Структура организации</span>
        <v-chip v-if="filteredItemsCount > 0" size="small" class="ml-2" variant="tonal">
          {{ filteredItemsCount }} позиций
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

    <!-- Tree Content -->
    <div class="tree-content" style="height: calc(100vh - 400px); overflow-y: auto;">
      <!-- Vuetify v-treeview automatically optimizes rendering - only renders expanded nodes -->
      <OrganizationTree
        v-if="optimizedItems.length > 0"
        ref="treeRef"
        v-model="selectedPositions"
        :items="optimizedItems"
        :selectable="true"
        :activatable="false"
        @select="handleSelection"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!loading && optimizedItems.length === 0" class="empty-state pa-8 text-center">
      <v-icon size="64" color="grey-lighten-2">mdi-file-tree</v-icon>
      <div class="text-h6 mt-4 text-medium-emphasis">
        {{ searchQuery ? 'Ничего не найдено' : 'Нет данных' }}
      </div>
      <div class="text-body-2 text-medium-emphasis mt-2">
        {{ searchQuery ? 'Попробуйте изменить поисковый запрос' : 'Структура организации не загружена' }}
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { OrganizationNode, SearchableItem } from '@/stores/catalog'
import OrganizationTree from './OrganizationTree.vue'

// Constants
// NOTE: We load ALL nodes but Vuetify v-treeview only renders visible (expanded) ones
// This is more natural UX than "Load More" button

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
const loading = ref(false)
const isExpanding = ref(false)

// Computed - Filter search results first
const filteredItems = computed(() => {
  if (!props.searchQuery || !props.searchQuery.trim()) {
    return props.items
  }

  const query = props.searchQuery.toLowerCase().trim()

  // Recursively filter tree nodes
  function filterNodes(nodes: OrganizationNode[]): OrganizationNode[] {
    return nodes.reduce<OrganizationNode[]>((acc, node) => {
      const nameMatches = node.name.toLowerCase().includes(query)
      const matchingPositions = node.positions?.filter(pos =>
        pos.position_name.toLowerCase().includes(query) ||
        pos.department_name?.toLowerCase().includes(query)
      )
      const filteredChildren = node.children ? filterNodes(node.children) : []

      if (nameMatches || (matchingPositions && matchingPositions.length > 0) || filteredChildren.length > 0) {
        acc.push({
          ...node,
          positions: nameMatches ? node.positions : matchingPositions,
          children: filteredChildren.length > 0 ? filteredChildren : node.children
        })
      }

      return acc
    }, [])
  }

  return filterNodes(props.items)
})

// Computed - Optimized items (show all, Vuetify only renders expanded ones)
const optimizedItems = computed(() => {
  // Always show all nodes
  // Vuetify v-treeview is smart - it only renders expanded nodes
  // So performance is good even with 1487 positions
  return filteredItems.value
})

// Computed - Statistics
const filteredItemsCount = computed(() => countPositions(filteredItems.value))

// Methods
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

async function expandAll(): Promise<void> {
  isExpanding.value = true

  // Wait a bit to show loading indicator
  await new Promise(resolve => setTimeout(resolve, 50))

  // Expand tree (all nodes already loaded)
  treeRef.value?.expandAll()

  isExpanding.value = false
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
  min-height: 400px;
}

.loading-state,
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

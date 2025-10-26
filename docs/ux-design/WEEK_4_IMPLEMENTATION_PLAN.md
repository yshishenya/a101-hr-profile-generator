# Week 4 Implementation Plan - Generator Page

**Date**: 2025-10-25
**Updated Scope**: Quick Search + Browse Tree (both tabs together!)
**Status**: Ready to implement

---

## 📋 Decisions Made

1. ✅ **Quick Search tab**: Primary interface for fast generation
2. ✅ **Browse Tree tab**: Implement TOGETHER with search (not Week 5!)
3. ✅ **Bulk orchestration**: Client-side with async task management
4. ✅ **Downloads**: Use existing endpoints (no ZIP needed for Week 4)
5. ✅ **Editor**: Full content editor planned for Week 7
6. ✅ **Tree**: Deliver both search methods in Week 4

---

## 🎯 Week 4 Deliverables

### UI Components (7 components)

#### 1. `GeneratorView.vue` - Main Page
```vue
<template>
  <v-container fluid>
    <h1>Generate Profile</h1>

    <!-- Tab Navigation -->
    <v-tabs v-model="activeTab">
      <v-tab value="search">🔍 Quick Search</v-tab>
      <v-tab value="tree">🌳 Browse Tree</v-tab>
    </v-tabs>

    <!-- Tab Content -->
    <v-window v-model="activeTab">
      <!-- Quick Search Tab -->
      <v-window-item value="search">
        <QuickSearchTab />
      </v-window-item>

      <!-- Browse Tree Tab -->
      <v-window-item value="tree">
        <BrowseTreeTab />
      </v-window-item>
    </v-window>

    <!-- Shared: Generation Modal/Panel -->
    <GenerationModal v-if="generationActive" />
  </v-container>
</template>
```

**Features**:
- Two tabs for different selection methods
- Shared state between tabs
- Responsive layout
- Help tooltips

---

#### 2. `QuickSearchTab.vue` - Search Interface
```vue
<template>
  <v-row>
    <v-col cols="12" md="8">
      <!-- Search Component -->
      <PositionSearchAutocomplete
        v-model="selectedPosition"
        :filters="filters"
      />

      <!-- Filters -->
      <v-row class="mt-4">
        <v-col cols="12" md="4">
          <v-select
            v-model="filters.department"
            :items="departments"
            label="Department"
            clearable
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="filters.status"
            :items="statusOptions"
            label="Profile Status"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-checkbox
            v-model="filters.ungenerated_only"
            label="Show only ungenerated"
          />
        </v-col>
      </v-row>

      <!-- Results List -->
      <PositionResultsList
        v-if="searchResults.length"
        :results="searchResults"
        @select="handlePositionSelect"
      />
    </v-col>

    <v-col cols="12" md="4">
      <!-- Generation Form (shown when position selected) -->
      <GenerationForm
        v-if="selectedPosition"
        :position="selectedPosition"
        @generate="handleGenerate"
      />
    </v-col>
  </v-row>
</template>
```

**Features**:
- Smart autocomplete search
- Filter controls
- Results preview
- Generation form on selection

---

#### 3. `BrowseTreeTab.vue` - Tree Interface
```vue
<template>
  <v-row>
    <v-col cols="12" md="8">
      <!-- Tree Controls -->
      <v-toolbar density="compact" color="transparent">
        <v-text-field
          v-model="treeSearch"
          prepend-inner-icon="mdi-magnify"
          label="Search in tree..."
          hide-details
          clearable
        />
        <v-spacer />
        <v-btn @click="expandAll">Expand All</v-btn>
        <v-btn @click="collapseAll">Collapse All</v-btn>
      </v-toolbar>

      <!-- Organization Tree -->
      <OrganizationTree
        v-model:selected="selectedPositions"
        v-model:expanded="expandedNodes"
        :search="treeSearch"
        :show-completion="true"
        selectable
      />

      <!-- Bulk Actions Panel (when multiple selected) -->
      <BulkActionsPanel
        v-if="selectedPositions.length > 1"
        :positions="selectedPositions"
        @generate="handleBulkGenerate"
      />
    </v-col>

    <v-col cols="12" md="4">
      <!-- Single Selection Form -->
      <GenerationForm
        v-if="selectedPositions.length === 1"
        :position="selectedPositions[0]"
        @generate="handleGenerate"
      />

      <!-- Multi-Selection Summary -->
      <MultiSelectionSummary
        v-else-if="selectedPositions.length > 1"
        :positions="selectedPositions"
      />
    </v-col>
  </v-row>
</template>
```

**Features**:
- Hierarchical tree view
- Progress indicators per node
- Multi-select support
- Bulk actions panel
- Search within tree

---

#### 4. `PositionSearchAutocomplete.vue` - Reusable Search
```vue
<template>
  <v-autocomplete
    v-model="internalValue"
    :items="filteredResults"
    :loading="loading"
    :search="searchQuery"
    @update:search="handleSearch"
    item-title="display_name"
    item-value="full_path"
    placeholder="Search by position name, department..."
    prepend-inner-icon="mdi-magnify"
    clearable
    auto-select-first
    no-filter
    return-object
  >
    <!-- Custom item template -->
    <template #item="{ props, item }">
      <v-list-item v-bind="props">
        <template #prepend>
          <v-avatar :color="item.raw.profile_exists ? 'success' : 'grey'">
            <v-icon>
              {{ item.raw.profile_exists ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
          </v-avatar>
        </template>

        <v-list-item-title>
          <span v-html="highlightMatch(item.raw.position_name)"></span>
        </v-list-item-title>

        <v-list-item-subtitle>
          <v-icon size="small">mdi-folder-outline</v-icon>
          {{ item.raw.department_path }}
        </v-list-item-subtitle>

        <template #append>
          <v-chip
            :color="item.raw.profile_exists ? 'success' : 'grey'"
            size="small"
            variant="flat"
          >
            {{ item.raw.profile_exists ? 'Generated' : 'New' }}
          </v-chip>
        </template>
      </v-list-item>
    </template>

    <!-- No results template -->
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No positions found. Try different search terms.
        </v-list-item-title>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCatalogStore } from '@/stores/catalog'
import { useDebounceFn } from '@vueuse/core'
import Fuse from 'fuse.js'

const catalogStore = useCatalogStore()
const searchQuery = ref('')
const loading = ref(false)

// Fuzzy search with Fuse.js
const fuse = computed(() => new Fuse(
  catalogStore.searchableItems,
  {
    keys: ['position_name', 'department_path', 'hierarchy'],
    threshold: 0.3,
    includeScore: true
  }
))

const filteredResults = computed(() => {
  if (!searchQuery.value) return []

  const results = fuse.value.search(searchQuery.value, { limit: 50 })
  return results.map(r => r.item)
})

const handleSearch = useDebounceFn((query: string) => {
  searchQuery.value = query
}, 300)

const highlightMatch = (text: string) => {
  if (!searchQuery.value) return text
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}
</script>
```

**Features**:
- Fuzzy search (Fuse.js)
- 300ms debounce
- Highlighted matches
- Status indicators
- Department breadcrumbs
- Max 50 results

---

#### 5. `OrganizationTree.vue` - Tree Component
```vue
<template>
  <v-card elevation="0" class="mt-4">
    <v-treeview
      v-model:selected="internalSelected"
      v-model:opened="internalExpanded"
      :items="treeItems"
      :search="search"
      item-value="id"
      item-title="name"
      activatable
      selectable
      return-object
      open-on-click
    >
      <!-- Prepend: Progress Circle -->
      <template #prepend="{ item }">
        <v-progress-circular
          v-if="item.type === 'department'"
          :model-value="item.completion_percentage"
          :size="32"
          :width="3"
          :color="getCompletionColor(item.completion_percentage)"
        >
          <span class="text-caption">
            {{ Math.round(item.completion_percentage) }}%
          </span>
        </v-progress-circular>

        <v-icon v-else :color="item.profile_exists ? 'success' : 'grey'">
          {{ item.profile_exists ? 'mdi-check-circle' : 'mdi-circle-outline' }}
        </v-icon>
      </template>

      <!-- Title: Custom rendering with counts -->
      <template #title="{ item }">
        <div class="d-flex align-center">
          <span>{{ item.name }}</span>
          <v-chip
            v-if="item.type === 'department'"
            size="x-small"
            class="ml-2"
            variant="flat"
          >
            {{ item.profiles_count }}/{{ item.positions_count }}
          </v-chip>
        </div>
      </template>

      <!-- Append: Actions -->
      <template #append="{ item }">
        <v-btn
          v-if="item.type === 'position' && !item.profile_exists"
          icon="mdi-plus"
          size="x-small"
          variant="text"
          @click.stop="handleQuickGenerate(item)"
        />
      </template>
    </v-treeview>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCatalogStore } from '@/stores/catalog'

interface Props {
  selected?: any[]
  expanded?: string[]
  search?: string
  showCompletion?: boolean
  selectable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: () => [],
  expanded: () => [],
  search: '',
  showCompletion: true,
  selectable: false
})

const emit = defineEmits(['update:selected', 'update:expanded'])

const catalogStore = useCatalogStore()
const internalSelected = ref(props.selected)
const internalExpanded = ref(props.expanded)

// Transform organization data to tree format
const treeItems = computed(() => {
  return catalogStore.organizationTree // Pre-transformed in store
})

const getCompletionColor = (percentage: number) => {
  if (percentage === 0) return 'grey'
  if (percentage < 25) return 'error'
  if (percentage < 50) return 'warning'
  if (percentage < 75) return 'info'
  return 'success'
}

watch(internalSelected, (val) => emit('update:selected', val))
watch(internalExpanded, (val) => emit('update:expanded', val))
</script>
```

**Features**:
- Lazy loading children
- Progress circles per node
- Counts: [generated/total]
- Multi-select checkboxes
- Search highlighting
- Quick generate button

---

#### 6. `GenerationForm.vue` - Generation Configuration
```vue
<template>
  <v-card elevation="2" class="sticky-form">
    <v-card-title>Generate Profile</v-card-title>

    <v-card-text>
      <!-- Selected Position Info -->
      <v-alert
        v-if="position"
        type="info"
        variant="tonal"
        class="mb-4"
      >
        <div class="text-subtitle-2">{{ position.position_name }}</div>
        <div class="text-caption">{{ position.department_path }}</div>
      </v-alert>

      <!-- Form Fields -->
      <v-text-field
        v-model="formData.employee_name"
        label="Employee Name (Optional)"
        placeholder="Иванов Иван Иванович"
        hint="Leave empty for generic profile"
        persistent-hint
      />

      <v-slider
        v-model="formData.temperature"
        label="AI Creativity"
        :min="0"
        :max="1"
        :step="0.1"
        thumb-label
        class="mt-4"
      >
        <template #append>
          <v-text-field
            v-model="formData.temperature"
            type="number"
            style="width: 80px"
            density="compact"
            hide-details
          />
        </template>
      </v-slider>

      <v-alert type="info" variant="tonal" class="mt-4">
        <div class="text-caption">
          <strong>Temperature Guide:</strong><br>
          0.0-0.2: Very consistent, formal<br>
          0.3-0.5: Balanced creativity<br>
          0.6-1.0: More creative, varied
        </div>
      </v-alert>

      <v-checkbox
        v-model="formData.save_result"
        label="Save to database"
        hint="Recommended: keep enabled"
        persistent-hint
      />
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn
        color="primary"
        size="large"
        :loading="generating"
        @click="handleGenerate"
      >
        <v-icon start>mdi-creation</v-icon>
        Generate Profile
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

interface Props {
  position: any
}

const props = defineProps<Props>()
const emit = defineEmits(['generate'])

const generating = ref(false)
const formData = reactive({
  employee_name: '',
  temperature: 0.1,
  save_result: true
})

const handleGenerate = () => {
  emit('generate', {
    department: props.position.department_name,
    position: props.position.position_name,
    employee_name: formData.employee_name || undefined,
    temperature: formData.temperature,
    save_result: formData.save_result
  })
}
</script>

<style scoped>
.sticky-form {
  position: sticky;
  top: 80px;
}
</style>
```

**Features**:
- Pre-filled from selection
- Temperature slider with guide
- Optional employee name
- Save toggle
- Sticky positioning
- Visual feedback

---

#### 7. `GenerationProgressTracker.vue` - Real-time Progress
```vue
<template>
  <v-dialog v-model="dialog" persistent max-width="600">
    <v-card>
      <v-card-title>
        <v-icon :color="statusColor">{{ statusIcon }}</v-icon>
        {{ statusText }}
      </v-card-title>

      <v-card-text>
        <!-- Progress Bar -->
        <v-progress-linear
          :model-value="progress"
          :color="statusColor"
          :indeterminate="status === 'processing' && !progress"
          height="8"
          rounded
          class="mb-4"
        />

        <!-- Current Step -->
        <div v-if="currentStep" class="text-subtitle-2 mb-2">
          {{ currentStep }}
        </div>

        <!-- Time Info -->
        <div class="d-flex justify-space-between text-caption text-medium-emphasis">
          <span>Elapsed: {{ elapsedTime }}s</span>
          <span v-if="estimatedDuration">
            Estimated: ~{{ estimatedDuration }}s
          </span>
        </div>

        <!-- Error Message -->
        <v-alert
          v-if="status === 'failed'"
          type="error"
          variant="tonal"
          class="mt-4"
        >
          {{ errorMessage }}
        </v-alert>

        <!-- Success Preview -->
        <v-card
          v-if="status === 'completed' && result"
          elevation="0"
          variant="tonal"
          color="success"
          class="mt-4"
        >
          <v-card-text>
            <div class="d-flex align-center mb-2">
              <v-icon color="success">mdi-check-circle</v-icon>
              <span class="ml-2 font-weight-bold">Profile Generated!</span>
            </div>

            <div class="text-caption">
              Quality Scores:
              <v-chip size="small" class="ml-2">
                Validation: {{ result.validation_score }}%
              </v-chip>
              <v-chip size="small" class="ml-2">
                Completeness: {{ result.completeness_score }}%
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-card-text>

      <v-card-actions>
        <v-btn
          v-if="status === 'processing'"
          color="error"
          variant="text"
          @click="handleCancel"
        >
          Cancel
        </v-btn>
        <v-spacer />
        <v-btn
          v-if="status === 'completed'"
          color="primary"
          @click="handleViewProfile"
        >
          View Profile
        </v-btn>
        <v-btn
          v-if="status === 'completed'"
          color="primary"
          variant="text"
          @click="handleDownload"
        >
          <v-icon start>mdi-download</v-icon>
          Download
        </v-btn>
        <v-btn
          v-if="status === 'completed' || status === 'failed'"
          @click="handleClose"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useGeneratorStore } from '@/stores/generator'

interface Props {
  taskId: string
  autoPoll?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoPoll: true
})

const emit = defineEmits(['complete', 'error', 'cancel', 'close'])

const generatorStore = useGeneratorStore()
const dialog = ref(true)
const elapsedTime = ref(0)
const pollInterval = ref<number | null>(null)

const task = computed(() => generatorStore.getTask(props.taskId))
const status = computed(() => task.value?.status || 'queued')
const progress = computed(() => task.value?.progress || 0)
const currentStep = computed(() => task.value?.current_step)
const estimatedDuration = computed(() => task.value?.estimated_duration)
const errorMessage = computed(() => task.value?.error_message)
const result = computed(() => task.value?.result)

const statusColor = computed(() => {
  switch (status.value) {
    case 'completed': return 'success'
    case 'failed': return 'error'
    case 'processing': return 'primary'
    default: return 'grey'
  }
})

const statusIcon = computed(() => {
  switch (status.value) {
    case 'completed': return 'mdi-check-circle'
    case 'failed': return 'mdi-alert-circle'
    case 'processing': return 'mdi-cog'
    case 'cancelled': return 'mdi-cancel'
    default: return 'mdi-clock-outline'
  }
})

const statusText = computed(() => {
  switch (status.value) {
    case 'completed': return 'Generation Complete!'
    case 'failed': return 'Generation Failed'
    case 'processing': return 'Generating Profile...'
    case 'cancelled': return 'Generation Cancelled'
    default: return 'Queued for Generation'
  }
})

// Auto-poll task status
if (props.autoPoll) {
  pollInterval.value = window.setInterval(async () => {
    if (status.value === 'processing' || status.value === 'queued') {
      await generatorStore.pollTaskStatus(props.taskId)
      elapsedTime.value++
    } else {
      // Stop polling when completed/failed
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
        pollInterval.value = null
      }
    }
  }, 2000) // Poll every 2 seconds
}

// Emit events based on status
watch(status, (newStatus) => {
  if (newStatus === 'completed') {
    emit('complete', result.value)
  } else if (newStatus === 'failed') {
    emit('error', errorMessage.value)
  }
})

const handleCancel = async () => {
  await generatorStore.cancelTask(props.taskId)
  emit('cancel')
}

const handleViewProfile = () => {
  // Navigate to profile detail
  emit('close')
}

const handleDownload = () => {
  // Trigger download
}

const handleClose = () => {
  dialog.value = false
  emit('close')
}

onUnmounted(() => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
  }
})
</script>
```

**Features**:
- Real-time status polling (2s interval)
- Progress bar with steps
- Elapsed/estimated time
- Cancel support
- Success preview with quality scores
- Error handling
- Action buttons (view, download)

---

### State Management (Pinia Stores)

#### `stores/generator.ts`
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

interface GenerationTask {
  task_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress?: number
  current_step?: string
  estimated_duration?: number
  error_message?: string
  result?: any
  created_at: Date
}

export const useGeneratorStore = defineStore('generator', () => {
  // State
  const activeTasks = ref<Map<string, GenerationTask>>(new Map())
  const selectedPosition = ref<any>(null)
  const generating = ref(false)

  // Getters
  const getTask = (taskId: string) => activeTasks.value.get(taskId)

  const activeTasksList = computed(() =>
    Array.from(activeTasks.value.values())
      .filter(t => t.status === 'processing' || t.status === 'queued')
  )

  // Actions
  async function startGeneration(request: {
    department: string
    position: string
    employee_name?: string
    temperature?: number
    save_result?: boolean
  }) {
    try {
      generating.value = true

      const response = await api.post('/api/generation/start', request)
      const { task_id, estimated_duration } = response.data

      // Add to active tasks
      activeTasks.value.set(task_id, {
        task_id,
        status: 'queued',
        estimated_duration,
        created_at: new Date()
      })

      return task_id
    } catch (error) {
      console.error('Failed to start generation:', error)
      throw error
    } finally {
      generating.value = false
    }
  }

  async function pollTaskStatus(taskId: string) {
    try {
      const response = await api.get(`/api/generation/${taskId}/status`)
      const taskData = response.data.task

      // Update task in store
      activeTasks.value.set(taskId, {
        ...activeTasks.value.get(taskId),
        ...taskData
      })

      // If completed, fetch result
      if (taskData.status === 'completed') {
        const resultResponse = await api.get(`/api/generation/${taskId}/result`)
        activeTasks.value.set(taskId, {
          ...activeTasks.value.get(taskId)!,
          result: resultResponse.data
        })
      }

      return taskData
    } catch (error) {
      console.error('Failed to poll task status:', error)
      throw error
    }
  }

  async function cancelTask(taskId: string) {
    try {
      await api.delete(`/api/generation/${taskId}`)

      const task = activeTasks.value.get(taskId)
      if (task) {
        task.status = 'cancelled'
      }
    } catch (error) {
      console.error('Failed to cancel task:', error)
      throw error
    }
  }

  function clearCompletedTasks() {
    for (const [taskId, task] of activeTasks.value.entries()) {
      if (task.status === 'completed' || task.status === 'failed') {
        activeTasks.value.delete(taskId)
      }
    }
  }

  return {
    // State
    activeTasks,
    selectedPosition,
    generating,

    // Getters
    getTask,
    activeTasksList,

    // Actions
    startGeneration,
    pollTaskStatus,
    cancelTask,
    clearCompletedTasks
  }
})
```

---

#### `stores/catalog.ts`
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const searchableItems = ref<any[]>([])
  const organizationTree = ref<any[]>([])
  const departments = ref<any[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  // Getters
  const totalPositions = computed(() => searchableItems.value.length)

  const departmentsList = computed(() =>
    departments.value.map(d => ({
      title: d.display_name,
      value: d.name
    }))
  )

  // Actions
  async function loadSearchableItems() {
    if (loaded.value) return

    try {
      loading.value = true
      const response = await api.get('/api/organization/search-items')

      searchableItems.value = response.data.data.items
      loaded.value = true

      // Cache in localStorage
      localStorage.setItem('org_cache', JSON.stringify({
        items: searchableItems.value,
        timestamp: Date.now()
      }))
    } catch (error) {
      console.error('Failed to load searchable items:', error)

      // Try loading from cache
      const cache = localStorage.getItem('org_cache')
      if (cache) {
        const parsed = JSON.parse(cache)
        searchableItems.value = parsed.items
        loaded.value = true
      }
    } finally {
      loading.value = false
    }
  }

  async function loadOrganizationTree() {
    // TODO: Transform searchableItems into tree structure
    // or call dedicated tree endpoint
  }

  async function loadDepartments() {
    try {
      const response = await api.get('/api/catalog/departments')
      departments.value = response.data.data.departments
    } catch (error) {
      console.error('Failed to load departments:', error)
    }
  }

  function forceRefresh() {
    loaded.value = false
    localStorage.removeItem('org_cache')
    return loadSearchableItems()
  }

  return {
    // State
    searchableItems,
    organizationTree,
    departments,
    loaded,
    loading,

    // Getters
    totalPositions,
    departmentsList,

    // Actions
    loadSearchableItems,
    loadOrganizationTree,
    loadDepartments,
    forceRefresh
  }
})
```

---

## 📦 Dependencies to Install

```bash
npm install --save fuse.js  # Fuzzy search
npm install --save @vueuse/core  # Utilities (debounce, etc)
```

---

## 🧪 Testing Checklist

### Quick Search Tab
- [ ] Search autocomplete works with fuzzy matching
- [ ] Results show status badges correctly
- [ ] Filters apply correctly (department, status)
- [ ] Position selection pre-fills form
- [ ] Generation starts successfully
- [ ] Progress tracker updates in real-time
- [ ] Error handling works

### Browse Tree Tab
- [ ] Tree loads organization structure
- [ ] Progress circles show correct percentages
- [ ] Single selection works
- [ ] Multi-selection works
- [ ] Quick generate button works
- [ ] Search within tree works
- [ ] Expand/collapse all works

### Generation Flow
- [ ] Form validation works
- [ ] Temperature slider works
- [ ] API request is correct
- [ ] Task polling works (2s interval)
- [ ] Progress updates correctly
- [ ] Completion shows result
- [ ] Cancel works
- [ ] Download buttons work

### State Management
- [ ] Selected position syncs between tabs
- [ ] Active tasks persist
- [ ] Store updates trigger UI updates
- [ ] Cache works (localStorage)
- [ ] Force refresh clears cache

---

## 🚀 Implementation Order

### Day 1: Foundation
1. ✅ Install dependencies (fuse.js, @vueuse/core)
2. ✅ Create Pinia stores (generator, catalog)
3. ✅ Create GeneratorView.vue with tabs
4. ✅ Add route for /generator

### Day 2: Quick Search
1. ✅ Build PositionSearchAutocomplete.vue
2. ✅ Build QuickSearchTab.vue
3. ✅ Integrate with catalog store
4. ✅ Test search functionality

### Day 3: Tree Navigation
1. ✅ Build OrganizationTree.vue
2. ✅ Build BrowseTreeTab.vue
3. ✅ Transform data for tree structure
4. ✅ Test tree navigation

### Day 4: Generation Flow
1. ✅ Build GenerationForm.vue
2. ✅ Build GenerationProgressTracker.vue
3. ✅ Integrate with generation API
4. ✅ Test end-to-end generation

### Day 5: Polish & Testing
1. ✅ Add loading states
2. ✅ Add error handling
3. ✅ Add help tooltips
4. ✅ Full integration testing
5. ✅ Commit and document

---

## 📊 Success Metrics

- Search returns results in < 200ms
- Tree loads in < 1s
- Generation completes in 15-30s
- 0% error rate on happy path
- 100% of features working

---

**Status**: Ready to implement!
**Next**: Start with Day 1 - Foundation setup


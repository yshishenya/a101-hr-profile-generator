# Unified Profiles Interface - Component Specification

**Date**: 2025-10-26
**Based on**: PROFILES_UX_ANALYSIS.md
**Decision**: Unified single-page interface for positions & profiles

---

## 🎯 Component Architecture

### Page Structure

```
/profiles (Unified Positions & Profiles Page)
├── StatsOverview.vue
├── FilterBar.vue
│   ├── SearchInput.vue
│   ├── DepartmentFilter.vue
│   ├── StatusFilter.vue
│   └── ViewModeToggle.vue
├── BulkActionsBar.vue (conditional - when items selected)
├── PositionsTable.vue (default view)
│   ├── PositionRow.vue
│   │   └── RowActions.vue (context-aware)
│   └── TablePagination.vue
├── PositionsTree.vue (alternative view)
│   └── TreeNode.vue
│       └── NodeActions.vue (context-aware)
├── ProfileViewerModal.vue
│   ├── ProfileContent.vue
│   └── ProfileActions.vue
└── GenerationProgressPanel.vue (floating)
    └── TaskProgressCard.vue
```

---

## 📦 Component Specifications

### 1. StatsOverview.vue

**Purpose**: High-level organizational metrics

```vue
<template>
  <BaseCard class="mb-6">
    <v-card-text>
      <v-row align="center">
        <!-- Total Positions -->
        <v-col cols="12" md="3">
          <div class="text-h3 font-weight-bold">{{ totalPositions }}</div>
          <div class="text-caption text-medium-emphasis">Total Positions</div>
        </v-col>

        <!-- Generated Count -->
        <v-col cols="12" md="3">
          <div class="text-h3 font-weight-bold text-success">{{ generatedCount }}</div>
          <div class="text-caption text-medium-emphasis">Generated Profiles</div>
        </v-col>

        <!-- Coverage Progress -->
        <v-col cols="12" md="4">
          <v-progress-linear
            :model-value="coveragePercentage"
            :color="getCoverageColor(coveragePercentage)"
            height="24"
            rounded
          >
            <strong>{{ coveragePercentage }}% Complete</strong>
          </v-progress-linear>
        </v-col>

        <!-- In Progress Indicator -->
        <v-col cols="12" md="2">
          <v-chip
            v-if="inProgressCount > 0"
            color="warning"
            variant="flat"
          >
            <v-icon start>mdi-cog</v-icon>
            {{ inProgressCount }} generating
          </v-chip>
          <div v-else class="text-caption text-medium-emphasis">
            Last updated: {{ lastUpdated }}
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  totalPositions: number
  generatedCount: number
  inProgressCount: number
  lastUpdated: string
}

const props = defineProps<Props>()

const coveragePercentage = computed(() => {
  if (props.totalPositions === 0) return 0
  return Math.round((props.generatedCount / props.totalPositions) * 100)
})

function getCoverageColor(percentage: number): string {
  if (percentage < 25) return 'error'
  if (percentage < 50) return 'warning'
  if (percentage < 75) return 'info'
  return 'success'
}
</script>
```

---

### 2. FilterBar.vue

**Purpose**: Search and filter controls

```vue
<template>
  <BaseCard class="mb-4">
    <v-card-text>
      <v-row align="center">
        <!-- Search Input -->
        <v-col cols="12" md="4">
          <v-text-field
            v-model="internalFilters.search"
            prepend-inner-icon="mdi-magnify"
            label="Search positions..."
            placeholder="Аналитик, Developer, Менеджер..."
            hide-details
            clearable
            @update:model-value="debouncedSearch"
          />
        </v-col>

        <!-- Department Filter -->
        <v-col cols="12" md="3">
          <v-select
            v-model="internalFilters.department"
            :items="departments"
            label="Department"
            prepend-inner-icon="mdi-domain"
            hide-details
            clearable
          />
        </v-col>

        <!-- Status Filter -->
        <v-col cols="12" md="2">
          <v-select
            v-model="internalFilters.status"
            :items="statusOptions"
            label="Status"
            prepend-inner-icon="mdi-filter"
            hide-details
          />
        </v-col>

        <!-- View Mode Toggle -->
        <v-col cols="12" md="2">
          <v-btn-toggle
            v-model="viewMode"
            mandatory
            divided
            density="comfortable"
          >
            <v-btn value="table">
              <v-icon>mdi-table</v-icon>
              <span class="d-none d-md-inline ml-2">Table</span>
            </v-btn>
            <v-btn value="tree">
              <v-icon>mdi-file-tree</v-icon>
              <span class="d-none d-md-inline ml-2">Tree</span>
            </v-btn>
          </v-btn-toggle>
        </v-col>

        <!-- Clear Filters -->
        <v-col cols="12" md="1">
          <v-btn
            v-if="hasActiveFilters"
            icon="mdi-filter-remove"
            variant="text"
            color="error"
            @click="clearFilters"
          >
            <v-icon>mdi-filter-remove</v-icon>
            <v-tooltip activator="parent">Clear all filters</v-tooltip>
          </v-btn>
        </v-col>
      </v-row>

      <!-- Active Filters Chips -->
      <v-row v-if="hasActiveFilters" class="mt-2">
        <v-col>
          <v-chip
            v-if="internalFilters.search"
            closable
            @click:close="internalFilters.search = ''"
          >
            Search: "{{ internalFilters.search }}"
          </v-chip>
          <v-chip
            v-if="internalFilters.department"
            closable
            @click:close="internalFilters.department = null"
          >
            Dept: {{ internalFilters.department }}
          </v-chip>
          <v-chip
            v-if="internalFilters.status !== 'all'"
            closable
            @click:close="internalFilters.status = 'all'"
          >
            Status: {{ statusLabels[internalFilters.status] }}
          </v-chip>
        </v-col>
      </v-row>
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'

interface Filters {
  search: string
  department: string | null
  status: string
}

interface Props {
  filters: Filters
  departments: string[]
  viewMode: 'table' | 'tree'
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:filters': [filters: Filters]
  'update:viewMode': [mode: 'table' | 'tree']
}>()

const internalFilters = ref<Filters>({ ...props.filters })
const viewMode = computed({
  get: () => props.viewMode,
  set: (val) => emit('update:viewMode', val)
})

const statusOptions = [
  { title: 'All statuses', value: 'all' },
  { title: 'Generated', value: 'generated' },
  { title: 'Not generated', value: 'not_generated' },
  { title: 'Generating', value: 'generating' }
]

const statusLabels: Record<string, string> = {
  all: 'All',
  generated: 'Generated',
  not_generated: 'Not generated',
  generating: 'Generating'
}

const hasActiveFilters = computed(() => {
  return !!(
    internalFilters.value.search ||
    internalFilters.value.department ||
    internalFilters.value.status !== 'all'
  )
})

const debouncedSearch = useDebounceFn(() => {
  emit('update:filters', internalFilters.value)
}, 300)

// Watch non-search filters (immediate update)
watch(
  () => [internalFilters.value.department, internalFilters.value.status],
  () => {
    emit('update:filters', internalFilters.value)
  }
)

function clearFilters() {
  internalFilters.value = {
    search: '',
    department: null,
    status: 'all'
  }
  emit('update:filters', internalFilters.value)
}
</script>
```

---

### 3. PositionsTable.vue

**Purpose**: Main data table with status-aware row actions

```vue
<template>
  <BaseCard>
    <v-data-table
      v-model="selectedRows"
      :headers="headers"
      :items="positions"
      :loading="loading"
      :items-per-page="20"
      show-select
      item-value="position_id"
    >
      <!-- Status Column -->
      <template #item.status="{ item }">
        <StatusBadge :status="item.status" :progress="item.progress" />
      </template>

      <!-- Quality Score Column -->
      <template #item.quality="{ item }">
        <v-chip
          v-if="item.quality_score"
          :color="getQualityColor(item.quality_score)"
          size="small"
          variant="flat"
        >
          {{ item.quality_score }}%
        </v-chip>
        <span v-else class="text-medium-emphasis">—</span>
      </template>

      <!-- Created Date Column -->
      <template #item.created_at="{ item }">
        <span v-if="item.created_at">{{ formatDate(item.created_at) }}</span>
        <span v-else class="text-medium-emphasis">—</span>
      </template>

      <!-- Actions Column (Context-Aware) -->
      <template #item.actions="{ item }">
        <RowActions
          :position="item"
          @view="emit('view', item)"
          @generate="emit('generate', item)"
          @download="emit('download', item)"
          @cancel="emit('cancel', item)"
        />
      </template>

      <!-- Empty State -->
      <template #no-data>
        <v-empty-state
          icon="mdi-inbox"
          title="No positions found"
          text="Try adjusting your filters or search terms"
        >
          <template #actions>
            <v-btn color="primary" @click="emit('clear-filters')">
              Clear Filters
            </v-btn>
          </template>
        </v-empty-state>
      </template>

      <!-- Loading State -->
      <template #loading>
        <v-skeleton-loader type="table-row@5" />
      </template>
    </v-data-table>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { UnifiedPosition } from '@/types/unified'

interface Props {
  positions: UnifiedPosition[]
  loading: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  view: [position: UnifiedPosition]
  generate: [position: UnifiedPosition]
  download: [position: UnifiedPosition]
  cancel: [position: UnifiedPosition]
  'clear-filters': []
}>()

const selectedRows = ref<string[]>([])

const headers = [
  { title: 'Position', key: 'position_name', sortable: true },
  { title: 'Department', key: 'department_name', sortable: true },
  { title: 'Status', key: 'status', sortable: true, width: 120 },
  { title: 'Quality', key: 'quality', sortable: true, width: 100 },
  { title: 'Created', key: 'created_at', sortable: true, width: 120 },
  { title: 'Actions', key: 'actions', sortable: false, width: 200 }
]

function getQualityColor(score: number): string {
  if (score >= 90) return 'success'
  if (score >= 75) return 'info'
  if (score >= 60) return 'warning'
  return 'error'
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>
```

---

### 4. RowActions.vue

**Purpose**: Context-aware action buttons for each position

```vue
<template>
  <div class="d-flex ga-1">
    <!-- Generated Profile: View + Download -->
    <template v-if="position.status === 'generated'">
      <v-btn
        icon="mdi-eye"
        size="small"
        variant="text"
        color="primary"
        @click="emit('view')"
      >
        <v-icon>mdi-eye</v-icon>
        <v-tooltip activator="parent">View profile</v-tooltip>
      </v-btn>

      <v-menu>
        <template #activator="{ props: menuProps }">
          <v-btn
            icon="mdi-download"
            size="small"
            variant="text"
            v-bind="menuProps"
          >
            <v-icon>mdi-download</v-icon>
            <v-tooltip activator="parent">Download</v-tooltip>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="downloadAs('json')">
            <v-list-item-title>JSON</v-list-item-title>
          </v-list-item>
          <v-list-item @click="downloadAs('md')">
            <v-list-item-title>Markdown</v-list-item-title>
          </v-list-item>
          <v-list-item @click="downloadAs('docx')">
            <v-list-item-title>DOCX</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>

      <v-btn
        icon="mdi-refresh"
        size="small"
        variant="text"
        @click="confirmRegenerate"
      >
        <v-icon>mdi-refresh</v-icon>
        <v-tooltip activator="parent">Regenerate</v-tooltip>
      </v-btn>
    </template>

    <!-- Not Generated: Generate Button -->
    <template v-else-if="position.status === 'not_generated'">
      <v-btn
        color="primary"
        size="small"
        @click="emit('generate')"
      >
        <v-icon start>mdi-creation</v-icon>
        Generate
      </v-btn>
    </template>

    <!-- Generating: Progress + Cancel -->
    <template v-else-if="position.status === 'generating'">
      <v-chip color="warning" size="small">
        <v-icon start>mdi-cog</v-icon>
        {{ position.progress || 0 }}%
      </v-chip>
      <v-btn
        icon="mdi-close"
        size="small"
        variant="text"
        color="error"
        @click="emit('cancel')"
      >
        <v-icon>mdi-close</v-icon>
        <v-tooltip activator="parent">Cancel</v-tooltip>
      </v-btn>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { UnifiedPosition } from '@/types/unified'

interface Props {
  position: UnifiedPosition
}

const props = defineProps<Props>()
const emit = defineEmits<{
  view: []
  generate: []
  download: [format: string]
  cancel: []
}>()

function downloadAs(format: string) {
  emit('download', format)
}

function confirmRegenerate() {
  if (confirm('Are you sure you want to regenerate this profile? This will create a new version.')) {
    emit('generate')
  }
}
</script>
```

---

### 5. ProfileViewerModal.vue

**Purpose**: Quick profile preview without page navigation

```vue
<template>
  <v-dialog
    v-model="internalShow"
    max-width="1200"
    scrollable
  >
    <v-card v-if="profile">
      <!-- Header -->
      <v-card-title class="d-flex align-center">
        <span class="text-h5">{{ profile.profile.position_title }}</span>
        <v-spacer />
        <StatusBadge
          :status="'generated'"
          :quality="profile.validation_score"
        />
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="internalShow = false"
        />
      </v-card-title>

      <v-divider />

      <!-- Content Tabs -->
      <v-card-text class="pa-0">
        <v-tabs v-model="activeTab">
          <v-tab value="content">Content</v-tab>
          <v-tab value="metadata">Metadata</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <v-window-item value="content">
            <ProfileContent :profile="profile.profile" />
          </v-window-item>

          <v-window-item value="metadata">
            <ProfileMetadata :metadata="profile.metadata" />
          </v-window-item>
        </v-window>
      </v-card-text>

      <v-divider />

      <!-- Actions -->
      <v-card-actions>
        <v-btn
          prepend-icon="mdi-download"
          variant="text"
        >
          Download
          <v-menu activator="parent">
            <v-list>
              <v-list-item @click="download('json')">JSON</v-list-item>
              <v-list-item @click="download('md')">Markdown</v-list-item>
              <v-list-item @click="download('docx')">DOCX</v-list-item>
            </v-list>
          </v-menu>
        </v-btn>

        <v-btn
          prepend-icon="mdi-pencil"
          variant="text"
          @click="emit('edit', profile)"
        >
          Edit
        </v-btn>

        <v-btn
          prepend-icon="mdi-refresh"
          variant="text"
          @click="emit('regenerate', profile)"
        >
          Regenerate
        </v-btn>

        <v-spacer />

        <v-btn
          color="primary"
          @click="internalShow = false"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProfileDetail } from '@/types/profile'

interface Props {
  show: boolean
  profile: ProfileDetail | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:show': [show: boolean]
  download: [format: string, profile: ProfileDetail]
  edit: [profile: ProfileDetail]
  regenerate: [profile: ProfileDetail]
}>()

const internalShow = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

const activeTab = ref('content')

function download(format: string) {
  if (props.profile) {
    emit('download', format, props.profile)
  }
}
</script>
```

---

## 🔄 Data Flow

### Loading Unified Data

```typescript
// In ProfilesView.vue
async function loadUnifiedData() {
  loading.value = true

  try {
    // 1. Load ALL positions from catalog (with profile_exists flag)
    const catalogData = await catalogStore.loadPositions()

    // 2. Load active generation tasks
    const activeTasks = generatorStore.activeTasks

    // 3. Merge data into unified structure
    positions.value = catalogData.items.map(pos => ({
      // Position metadata
      position_id: pos.position_id,
      position_name: pos.position_name,
      department_name: pos.business_unit_name,
      department_path: pos.department_path,

      // Status (derived from multiple sources)
      status: determineStatus(pos, activeTasks),

      // Profile data (if exists)
      profile_id: pos.profile_id,
      quality_score: pos.validation_score,
      created_at: pos.created_at,

      // Task data (if generating)
      task_id: findTaskId(pos, activeTasks),
      progress: findProgress(pos, activeTasks)
    }))
  } finally {
    loading.value = false
  }
}

function determineStatus(
  position: SearchableItem,
  tasks: Map<string, GenerationTask>
): 'generated' | 'not_generated' | 'generating' {
  // Check if currently generating
  const hasActiveTask = Array.from(tasks.values()).some(
    task => task.position_id === position.position_id &&
           (task.status === 'queued' || task.status === 'processing')
  )

  if (hasActiveTask) return 'generating'
  if (position.profile_exists) return 'generated'
  return 'not_generated'
}
```

---

## 🎨 Status Badge Component

```vue
<!-- StatusBadge.vue -->
<template>
  <v-chip
    :color="statusConfig.color"
    :variant="statusConfig.variant"
    size="small"
  >
    <v-icon v-if="statusConfig.icon" start>{{ statusConfig.icon }}</v-icon>
    <span>{{ statusConfig.label }}</span>
    <span v-if="progress !== undefined" class="ml-1">({{ progress }}%)</span>
  </v-chip>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'generated' | 'not_generated' | 'generating'
  progress?: number
  quality?: number
}

const props = defineProps<Props>()

const statusConfig = computed(() => {
  switch (props.status) {
    case 'generated':
      return {
        color: 'success',
        variant: 'flat',
        icon: 'mdi-check-circle',
        label: props.quality ? `Generated (${props.quality}%)` : 'Generated'
      }
    case 'generating':
      return {
        color: 'warning',
        variant: 'flat',
        icon: 'mdi-cog',
        label: 'Generating'
      }
    case 'not_generated':
      return {
        color: 'grey',
        variant: 'outlined',
        icon: 'mdi-circle-outline',
        label: 'Not generated'
      }
  }
})
</script>
```

---

## 📊 Type Definitions

```typescript
// src/types/unified.ts

/**
 * Unified position with profile status
 * Combines data from catalog and profiles
 */
export interface UnifiedPosition {
  // Position metadata (from catalog)
  position_id: string
  position_name: string
  department_id?: string
  department_name: string
  department_path: string

  // Status (derived)
  status: 'generated' | 'not_generated' | 'generating'

  // Profile data (if generated)
  profile_id?: string
  quality_score?: number
  completeness_score?: number
  created_at?: string
  created_by?: string

  // Task data (if generating)
  task_id?: string
  progress?: number
  current_step?: string

  // Actions available
  actions: {
    canView: boolean
    canGenerate: boolean
    canDownload: boolean
    canEdit: boolean
    canCancel: boolean
  }
}
```

---

## ✅ Implementation Checklist

### Phase 1: Core Components (Days 1-2)
- [ ] Create `UnifiedPosition` type
- [ ] Create `StatsOverview.vue`
- [ ] Create `FilterBar.vue`
- [ ] Create `StatusBadge.vue`
- [ ] Update `ProfilesStore` for unified data

### Phase 2: Table View (Days 3-4)
- [ ] Create `PositionsTable.vue`
- [ ] Create `RowActions.vue`
- [ ] Implement filtering logic
- [ ] Implement pagination
- [ ] Add loading/empty states

### Phase 3: Profile Viewer (Day 5)
- [ ] Create `ProfileViewerModal.vue`
- [ ] Create `ProfileContent.vue`
- [ ] Create `ProfileMetadata.vue`
- [ ] Implement download actions

### Phase 4: Integration (Day 6)
- [ ] Create main `ProfilesView.vue`
- [ ] Integrate with generator store
- [ ] Real-time status updates
- [ ] Handle generation from table

### Phase 5: Tree View (Day 7 - Optional)
- [ ] Create `PositionsTree.vue`
- [ ] Adapt existing `OrganizationTree.vue`
- [ ] Toggle between table/tree views

---

**DECISION**: Proceed with Unified Interface implementation

**Next Step**: Build core components starting with `UnifiedPosition` type and `StatsOverview`

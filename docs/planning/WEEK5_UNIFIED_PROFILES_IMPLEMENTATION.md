# Week 5: Unified Profiles Interface - Implementation Plan

**Date**: 2025-10-26
**Status**: READY TO IMPLEMENT
**Estimated Time**: 7 days
**Branch**: `feature/profiles-list-management`

---

## 📋 Executive Summary

Based on comprehensive UX analysis, we're implementing a **Unified Interface** that combines profile viewing and generation into a single page `/profiles`.

### Key Decisions:

1. ✅ **Unified Interface** (scored 47/50 vs alternatives 31-35/50)
2. ✅ **Hybrid Versioning** (version badge + timeline modal)
3. ✅ **Context-aware actions** (View/Generate/Download based on status)
4. ✅ **Real-time updates** (generation progress inline)
5. ✅ **Two view modes** (Table + Tree)

---

## 🎯 Goals

### User Experience Goals:
- **Single Source of Truth**: All positions visible on one page
- **Prevent Duplicates**: Always show generation status
- **Fast Workflow**: Inline actions, no context switching
- **Clear Overview**: Department-level statistics
- **Version Management**: Full audit trail with comparison

### Technical Goals:
- **Type Safety**: 100% typed components
- **Performance**: <1s initial load, <200ms filter updates
- **Code Quality**: DRY, reusable components
- **Maintainability**: Clear component hierarchy

---

## 🗺️ Implementation Roadmap

### Day 1-2: Foundation & Types
```
✅ UX Analysis completed
✅ Component specifications created
→ Type definitions
→ Core components (StatsOverview, FilterBar)
→ Data layer (unified data loading)
```

### Day 3-4: Table View
```
→ PositionsTable component
→ RowActions (context-aware)
→ StatusBadge
→ Pagination & sorting
```

### Day 5: Profile Viewer
```
→ ProfileViewerModal
→ ProfileContent display
→ Download actions
```

### Day 6: Versioning
```
→ ProfileVersionsPanel
→ Version timeline
→ Version switching
→ Backend version endpoints
```

### Day 7: Tree View & Polish
```
→ PositionsTree component
→ View mode toggle
→ Final integration & testing
```

---

## 📦 Component Architecture

```
/profiles (Main Page)
├── StatsOverview.vue ⭐ Day 1
│   └── Coverage progress, counts
├── FilterBar.vue ⭐ Day 1-2
│   ├── SearchInput
│   ├── DepartmentFilter
│   ├── StatusFilter
│   └── ViewModeToggle
├── PositionsTable.vue ⭐ Day 3-4
│   ├── StatusBadge
│   ├── RowActions (context-aware)
│   └── Pagination
├── PositionsTree.vue ⭐ Day 7
│   └── TreeNode (reuse from generator)
├── ProfileViewerModal.vue ⭐ Day 5
│   ├── ProfileContent
│   ├── ProfileMetadata
│   └── ProfileVersionsPanel ⭐ Day 6
│       └── VersionTimeline
└── GenerationProgressPanel.vue
    └── TaskProgressCard
```

---

## 📝 Detailed Implementation Steps

### Day 1: Type Definitions & Data Layer

#### 1.1 Create UnifiedPosition Type

```typescript
// src/types/unified.ts
export interface UnifiedPosition {
  // Position metadata
  position_id: string
  position_name: string
  department_id?: string
  department_name: string
  department_path: string
  business_unit_id: string
  business_unit_name: string

  // Status (derived from multiple sources)
  status: 'generated' | 'not_generated' | 'generating'

  // Profile data (if generated)
  profile_id?: string
  current_version?: number
  version_count?: number
  quality_score?: number
  completeness_score?: number
  created_at?: string
  created_by?: string

  // Task data (if generating)
  task_id?: string
  progress?: number
  current_step?: string
  estimated_duration?: number

  // Actions available (computed)
  actions: {
    canView: boolean
    canGenerate: boolean
    canDownload: boolean
    canEdit: boolean
    canCancel: boolean
  }
}

export interface ProfileVersion {
  version_number: number
  created_at: string
  created_by: string
  type: 'generated' | 'regenerated' | 'edited'
  quality_score: number
  completeness_score: number
  changes_summary?: string[]
  is_current: boolean
}

export type ViewMode = 'table' | 'tree'

export interface ProfileFilters {
  search: string
  department: string | null
  status: 'all' | 'generated' | 'not_generated' | 'generating'
}
```

#### 1.2 Update ProfilesStore for Unified Data

```typescript
// src/stores/profiles.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UnifiedPosition, ProfileVersion } from '@/types/unified'
import { useCatalogStore } from './catalog'
import { useGeneratorStore } from './generator'

export const useProfilesStore = defineStore('profiles', () => {
  const catalogStore = useCatalogStore()
  const generatorStore = useGeneratorStore()

  // State
  const positions = ref<UnifiedPosition[]>([])
  const loading = ref(false)
  const viewMode = ref<ViewMode>('table')
  const filters = ref<ProfileFilters>({
    search: '',
    department: null,
    status: 'all'
  })

  // Computed
  const filteredPositions = computed(() => {
    let result = positions.value

    // Search filter
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      result = result.filter(p =>
        p.position_name.toLowerCase().includes(search) ||
        p.department_name.toLowerCase().includes(search)
      )
    }

    // Department filter
    if (filters.value.department) {
      result = result.filter(p =>
        p.department_name === filters.value.department
      )
    }

    // Status filter
    if (filters.value.status !== 'all') {
      result = result.filter(p => p.status === filters.value.status)
    }

    return result
  })

  const totalPositions = computed(() => positions.value.length)
  const generatedCount = computed(() =>
    positions.value.filter(p => p.status === 'generated').length
  )
  const generatingCount = computed(() =>
    positions.value.filter(p => p.status === 'generating').length
  )
  const coveragePercentage = computed(() => {
    if (totalPositions.value === 0) return 0
    return Math.round((generatedCount.value / totalPositions.value) * 100)
  })

  // Actions
  async function loadUnifiedData() {
    loading.value = true
    try {
      // 1. Load catalog positions (with profile_exists flag)
      await catalogStore.loadSearchableItems()
      const catalogItems = catalogStore.searchableItems

      // 2. Get active generation tasks
      const activeTasks = generatorStore.activeTasks

      // 3. Merge into unified structure
      positions.value = catalogItems.map(item => {
        const taskEntry = Array.from(activeTasks.value.entries()).find(
          ([_, task]) => task.position_id === item.position_id
        )
        const task = taskEntry?.[1]

        const status = determineStatus(item, task)

        return {
          // Position metadata
          position_id: item.position_id,
          position_name: item.position_name,
          business_unit_id: item.business_unit_id,
          business_unit_name: item.business_unit_name,
          department_name: item.business_unit_name,
          department_path: item.department_path,

          // Status
          status,

          // Profile data
          profile_id: item.profile_id,
          quality_score: item.profile_exists ? 85 : undefined, // TODO: Get from API
          created_at: item.profile_exists ? new Date().toISOString() : undefined,

          // Task data
          task_id: task?.task_id,
          progress: task?.progress,
          current_step: task?.current_step,

          // Actions
          actions: {
            canView: status === 'generated',
            canGenerate: status === 'not_generated',
            canDownload: status === 'generated',
            canEdit: status === 'generated',
            canCancel: status === 'generating'
          }
        }
      })
    } finally {
      loading.value = false
    }
  }

  function determineStatus(
    item: any,
    task?: any
  ): 'generated' | 'not_generated' | 'generating' {
    if (task && (task.status === 'queued' || task.status === 'processing')) {
      return 'generating'
    }
    if (item.profile_exists) {
      return 'generated'
    }
    return 'not_generated'
  }

  return {
    // State
    positions,
    loading,
    viewMode,
    filters,

    // Computed
    filteredPositions,
    totalPositions,
    generatedCount,
    generatingCount,
    coveragePercentage,

    // Actions
    loadUnifiedData
  }
})
```

#### 1.3 Build StatsOverview Component

```vue
<!-- src/components/profiles/StatsOverview.vue -->
<template>
  <BaseCard class="mb-6">
    <v-card-text>
      <v-row align="center">
        <!-- Total Positions -->
        <v-col cols="12" sm="6" md="3">
          <div class="text-h4 font-weight-bold">{{ totalPositions }}</div>
          <div class="text-body-2 text-medium-emphasis">Total Positions</div>
        </v-col>

        <!-- Generated Count -->
        <v-col cols="12" sm="6" md="3">
          <div class="text-h4 font-weight-bold text-success">
            {{ generatedCount }}
          </div>
          <div class="text-body-2 text-medium-emphasis">Generated Profiles</div>
        </v-col>

        <!-- Coverage Progress -->
        <v-col cols="12" md="4">
          <div class="text-body-2 text-medium-emphasis mb-2">
            Coverage: {{ coveragePercentage }}%
          </div>
          <v-progress-linear
            :model-value="coveragePercentage"
            :color="getCoverageColor(coveragePercentage)"
            height="24"
            rounded
          >
            <template #default>
              <strong>{{ coveragePercentage }}%</strong>
            </template>
          </v-progress-linear>
        </v-col>

        <!-- In Progress / Last Updated -->
        <v-col cols="12" md="2" class="text-right">
          <v-chip
            v-if="generatingCount > 0"
            color="warning"
            variant="flat"
            prepend-icon="mdi-cog"
          >
            {{ generatingCount }} generating
          </v-chip>
          <div v-else class="text-caption text-medium-emphasis">
            <v-icon size="small">mdi-clock-outline</v-icon>
            {{ lastUpdated }}
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'

interface Props {
  totalPositions: number
  generatedCount: number
  generatingCount: number
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

### Day 2: FilterBar Component

```vue
<!-- src/components/profiles/FilterBar.vue -->
<template>
  <BaseCard class="mb-4">
    <v-card-text>
      <v-row align="center">
        <!-- Search -->
        <v-col cols="12" md="4">
          <v-text-field
            :model-value="filters.search"
            prepend-inner-icon="mdi-magnify"
            label="Search positions..."
            placeholder="Аналитик, Developer, Менеджер..."
            hide-details
            clearable
            @update:model-value="handleSearchChange"
          />
        </v-col>

        <!-- Department Filter -->
        <v-col cols="12" sm="6" md="3">
          <v-select
            :model-value="filters.department"
            :items="departments"
            label="Department"
            prepend-inner-icon="mdi-domain"
            hide-details
            clearable
            @update:model-value="emit('update:filters', { ...filters, department: $event })"
          />
        </v-col>

        <!-- Status Filter -->
        <v-col cols="12" sm="6" md="2">
          <v-select
            :model-value="filters.status"
            :items="statusOptions"
            label="Status"
            prepend-inner-icon="mdi-filter"
            hide-details
            @update:model-value="emit('update:filters', { ...filters, status: $event })"
          />
        </v-col>

        <!-- View Mode Toggle -->
        <v-col cols="12" md="2">
          <v-btn-toggle
            :model-value="viewMode"
            mandatory
            divided
            density="comfortable"
            @update:model-value="emit('update:viewMode', $event)"
          >
            <v-btn value="table">
              <v-icon>mdi-table</v-icon>
              <span class="d-none d-lg-inline ml-1">Table</span>
            </v-btn>
            <v-btn value="tree">
              <v-icon>mdi-file-tree</v-icon>
              <span class="d-none d-lg-inline ml-1">Tree</span>
            </v-btn>
          </v-btn-toggle>
        </v-col>

        <!-- Clear Filters -->
        <v-col cols="12" md="1" class="text-right">
          <v-btn
            v-if="hasActiveFilters"
            icon
            variant="text"
            color="error"
            @click="clearFilters"
          >
            <v-icon>mdi-filter-remove</v-icon>
            <v-tooltip activator="parent">Clear filters</v-tooltip>
          </v-btn>
        </v-col>
      </v-row>

      <!-- Active Filters Chips -->
      <v-row v-if="hasActiveFilters" class="mt-2">
        <v-col>
          <v-chip
            v-if="filters.search"
            closable
            size="small"
            @click:close="emit('update:filters', { ...filters, search: '' })"
          >
            Search: "{{ filters.search }}"
          </v-chip>
          <v-chip
            v-if="filters.department"
            closable
            size="small"
            class="ml-2"
            @click:close="emit('update:filters', { ...filters, department: null })"
          >
            Dept: {{ filters.department }}
          </v-chip>
          <v-chip
            v-if="filters.status !== 'all'"
            closable
            size="small"
            class="ml-2"
            @click:close="emit('update:filters', { ...filters, status: 'all' })"
          >
            Status: {{ statusLabels[filters.status] }}
          </v-chip>
        </v-col>
      </v-row>
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import type { ProfileFilters, ViewMode } from '@/types/unified'
import BaseCard from '@/components/common/BaseCard.vue'

interface Props {
  filters: ProfileFilters
  departments: string[]
  viewMode: ViewMode
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:filters': [filters: ProfileFilters]
  'update:viewMode': [mode: ViewMode]
}>()

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
    props.filters.search ||
    props.filters.department ||
    props.filters.status !== 'all'
  )
})

const handleSearchChange = useDebounceFn((value: string) => {
  emit('update:filters', { ...props.filters, search: value })
}, 300)

function clearFilters() {
  emit('update:filters', {
    search: '',
    department: null,
    status: 'all'
  })
}
</script>
```

---

## 🔄 Testing Strategy

### Unit Tests
```typescript
// tests/unit/stores/profiles.spec.ts
describe('ProfilesStore', () => {
  it('should determine status correctly', () => {
    // Test status logic
  })

  it('should filter positions by search', () => {
    // Test filtering
  })

  it('should calculate coverage percentage', () => {
    // Test computed
  })
})

// tests/unit/components/StatsOverview.spec.ts
describe('StatsOverview', () => {
  it('should display correct statistics', () => {
    // Test rendering
  })

  it('should show correct coverage color', () => {
    // Test color logic
  })
})
```

### Integration Tests
```typescript
// tests/integration/unified-profiles.spec.ts
describe('Unified Profiles Page', () => {
  it('should load all positions on mount', async () => {
    // Test data loading
  })

  it('should filter positions when search typed', async () => {
    // Test filtering
  })

  it('should generate profile when clicking Generate', async () => {
    // Test generation flow
  })
})
```

---

## 📊 Success Metrics

### Performance
- [ ] Initial load: <1s
- [ ] Filter update: <200ms
- [ ] Profile modal open: <300ms
- [ ] Generation start: <500ms

### UX
- [ ] 0 duplicate generations (status always visible)
- [ ] 2 clicks to generate (search → generate)
- [ ] 2 clicks to view (search → view)
- [ ] Real-time progress updates

### Code Quality
- [ ] 100% TypeScript typed
- [ ] 0 `any` types in components
- [ ] <300 lines per component
- [ ] DRY principles followed

---

## 🚀 Next Actions

### Immediate (Today):
1. ✅ Create `unified.ts` types file
2. ✅ Update `ProfilesStore` for unified data
3. ✅ Build `StatsOverview` component
4. ⏳ Build `FilterBar` component

### Tomorrow:
1. ⏳ Build `StatusBadge` component
2. ⏳ Build `PositionsTable` component
3. ⏳ Build `RowActions` component

### This Week:
- Complete all Day 1-7 tasks
- Full testing
- Commit to branch

---

**Status**: 🟢 Ready to implement
**Risk**: 🟢 Low (well-planned)
**Confidence**: 🟢 High (UX validated)

Let's start building! 🚀

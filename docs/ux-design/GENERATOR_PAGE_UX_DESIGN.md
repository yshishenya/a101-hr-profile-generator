# Profile Generator Page - UX Design Document

**Date**: 2025-10-25
**Version**: 1.0
**Status**: Proposal for Week 4 Implementation

---

## 📊 Data Analysis

### Organization Structure
- **Total Business Units**: 567 (fixed from previous 510 due to name duplicates)
- **Hierarchy Levels**: 4-5 levels deep
  - Level 1: Блоки (Blocks) - ~10 items
  - Level 2: Департаменты (Departments) - ~50 items
  - Level 3: Управления (Divisions) - ~150 items
  - Level 4-5: Отделы/Группы (Departments/Groups) - ~350 items
- **Total Positions**: 1,487 unique positions
- **Profiles Generated**: 13 (0.9% completion)

### User Personas & Use Cases

#### Persona 1: HR Manager (Frequent User)
**Goal**: Generate profiles for specific positions quickly
**Pain Points**:
- Needs to find exact position name
- May not remember full hierarchy path
- Wants to see if profile already exists

**Use Case**: "I need to create a profile for 'Руководитель группы анализа данных' but I don't remember which department it's in"

#### Persona 2: Department Head (Occasional User)
**Goal**: Generate profiles for all positions in their department
**Pain Points**:
- Knows department but not all positions
- Wants to see completion status
- Needs to generate multiple profiles at once

**Use Case**: "I want to generate profiles for all positions in my 'Департамент информационных технологий'"

#### Persona 3: System Administrator (Power User)
**Goal**: Bulk generation and system management
**Pain Points**:
- Needs efficient bulk operations
- Wants to track generation progress
- Needs to find gaps in coverage

**Use Case**: "I need to generate 50 profiles for the entire Security Block"

---

## 🎨 UX Approaches - Comparison

### Approach 1: Quick Search Only (Fastest)
```
┌────────────────────────────────────────┐
│  Generate Profile                      │
├────────────────────────────────────────┤
│                                        │
│  Search Position:                      │
│  ┌──────────────────────────────────┐ │
│  │ Руководитель...          🔍      │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ↓ Autocomplete Results (live)        │
│  ┌──────────────────────────────────┐ │
│  │ ● Руководитель группы данных     │ │
│  │   📁 ДИТ → Группа анализа        │ │
│  │   ✓ Profile exists               │ │
│  │                                  │ │
│  │ ○ Руководитель управления        │ │
│  │   📁 ДИТ → Управление разработки │ │
│  │   ○ No profile yet               │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

**Pros**:
- ✅ Fast for known positions
- ✅ Simple, clean interface
- ✅ Works great with fuzzy search

**Cons**:
- ❌ Hard to explore/discover
- ❌ No context for decision making
- ❌ Difficult for bulk selection

**Best for**: Persona 1 (HR Manager)

---

### Approach 2: Tree Navigation Only (Most Context)
```
┌────────────────────────────────────────────────────┐
│  Generate Profile - Browse Organization Tree       │
├────────────────────────────────────────────────────┤
│                                                    │
│  Organization Structure:                           │
│  ┌────────────────────────────────────────────┐  │
│  │ ▼ Блок информационных технологий (25/50)  │  │
│  │   ▼ Департамент ИТ (15/30)                │  │
│  │     ► Управление разработки (0/10)        │  │
│  │     ▼ Группа анализа данных (3/5)         │  │
│  │       ☐ Аналитик данных (junior)          │  │
│  │       ☑ Аналитик данных (middle) ✓        │  │
│  │       ☑ Руководитель группы ✓             │  │
│  │       ☐ Data Scientist                     │  │
│  │       ☐ ML Engineer                        │  │
│  └────────────────────────────────────────────┘  │
│                                                    │
│  Selected: 2 positions                             │
│  [ Generate Profiles ]                             │
└────────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Full context and exploration
- ✅ See completion status per unit
- ✅ Easy multi-select
- ✅ Understand hierarchy

**Cons**:
- ❌ Slow for specific searches
- ❌ Many clicks to find deep items
- ❌ Overwhelming for large trees

**Best for**: Persona 2 (Department Head)

---

### Approach 3: Hybrid (Recommended) ⭐

```
┌──────────────────────────────────────────────────────────┐
│  Generate Profile                                [?] Help │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [🔍 Quick Search]  [🌳 Browse Tree]  [⚡ Bulk Actions] │ Tabs
│                                                          │
│  ┌─ QUICK SEARCH ──────────────────────────────────────┐│
│  │                                                      ││
│  │  Find Position:                                      ││
│  │  ┌────────────────────────────────────────────────┐ ││
│  │  │ Руководитель...                          🔍    │ ││
│  │  └────────────────────────────────────────────────┘ ││
│  │                                                      ││
│  │  Filters: [All Depts ▼] [All Levels ▼] [☑ No Profile]│
│  │                                                      ││
│  │  ↓ Results (5):                                     ││
│  │  ┌────────────────────────────────────────────────┐ ││
│  │  │ ● Руководитель группы анализа данных           │ ││
│  │  │   📁 ДИТ → Группа анализа данных               │ ││
│  │  │   ✓ Generated  👁 View  ↻ Regenerate           │ ││
│  │  │                                                │ ││
│  │  │ ○ Руководитель управления разработки           │ ││
│  │  │   📁 ДИТ → Управление разработки               │ ││
│  │  │   ○ New  [+ Generate]                          │ ││
│  │  │                                                │ ││
│  │  │ ○ Руководитель отдела инфраструктуры          │ ││
│  │  │   📁 ДИТ → Отдел инфраструктуры                │ ││
│  │  │   ○ New  [+ Generate]                          │ ││
│  │  └────────────────────────────────────────────────┘ ││
│  │                                                      ││
│  │  [Generate Selected (0)]  [Select All Ungenerated]  ││
│  └──────────────────────────────────────────────────────┘│
│                                                          │
│  💡 Tip: Use filters to find ungenerated profiles faster │
└──────────────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Best of both worlds
- ✅ Fast search OR exploration
- ✅ Progressive disclosure
- ✅ Supports all user types

**Cons**:
- ⚠️ Slightly more complex UI
- ⚠️ Need good tab UX

**Best for**: All personas

---

## 🎯 Recommended Approach: Hybrid with Progressive Enhancement

### Phase 1 (Week 4 MVP):
Focus on **Quick Search Tab** only:
- Smart autocomplete search
- Filters (department, status)
- Single generation
- Inline result display

### Phase 2 (Week 5):
Add **Browse Tree Tab**:
- Collapsible tree view
- Multi-select
- Completion indicators

### Phase 3 (Week 6):
Add **Bulk Actions Tab**:
- Department-wide generation
- CSV upload
- Batch progress tracking

---

## 🔍 Quick Search Tab - Detailed Design

### Search Component Features

#### 1. Smart Autocomplete
```typescript
interface SearchResult {
  id: string
  position_name: string
  department_path: string
  hierarchy: string[]
  profile_exists: boolean
  profile_id?: number
  match_score: number  // For ranking
}
```

**Search Algorithm**:
- Fuzzy matching on position name
- Search in department names
- Keyword highlights
- Ranking by:
  1. Exact match
  2. Starts with
  3. Contains
  4. Department match

#### 2. Filters
- **Department**: Dropdown with autocomplete (567 items)
- **Profile Status**:
  - ● All
  - ○ Not Generated
  - ✓ Generated
- **Position Level**:
  - All Levels
  - Руководитель/Директор
  - Специалист
  - Менеджер

#### 3. Results Display
Each result card shows:
```
┌─────────────────────────────────────────────┐
│ ○ Position Name                        [+]  │ ← Checkbox + Action
│   📁 Full Hierarchy Path                    │ ← Context
│   ● Status Badge  👁 View  ↻ Regenerate     │ ← Actions
│   📊 Last generated: 2 days ago             │ ← Metadata
└─────────────────────────────────────────────┘
```

Status Badges:
- `✅ Generated` (green) - Has profile
- `🔄 In Progress` (blue) - Generating now
- `❌ Failed` (red) - Generation failed
- `○ New` (gray) - No profile yet

---

## 🌳 Browse Tree Tab - Detailed Design

### Tree Component Features

#### 1. Tree Structure
```
▼ Блок информационных технологий         [13/50] ████░░░░░░ 26%
  ▼ Департамент ИТ                       [10/30] ███░░░░░░░ 33%
    ► Управление разработки               [0/10] ░░░░░░░░░░  0%
    ▼ Группа анализа данных               [3/5]  ██████░░░░ 60%
      ☐ Аналитик данных (junior)          [New]
      ☑ Аналитик данных (middle)          [✓]
      ☑ Руководитель группы               [✓]
      ☐ Data Scientist                    [New]
      ☐ ML Engineer                       [New]
```

#### 2. Node Types
- **Collapsible Groups**: ▼/► indicators
- **Checkboxes**: Select positions
- **Progress Bars**: Visual completion
- **Counters**: [generated/total]

#### 3. Bulk Actions
- **Select All in Unit**: One-click select department
- **Generate Selected**: Batch generation
- **Expand All / Collapse All**: Navigation
- **Jump to Position**: Quick scroll

---

## 🎨 UI Components Specification

### 1. Search Autocomplete
**Component**: Vuetify `v-autocomplete`
```vue
<v-autocomplete
  v-model="selectedPosition"
  :items="searchResults"
  :loading="searching"
  :search-input.sync="searchQuery"
  item-title="display_name"
  item-value="full_path"
  placeholder="Search by position name..."
  prepend-inner-icon="mdi-magnify"
  clearable
  auto-select-first
  no-filter
>
  <template #item="{ props, item }">
    <v-list-item v-bind="props">
      <template #prepend>
        <v-icon :color="item.profile_exists ? 'success' : 'grey'">
          {{ item.profile_exists ? 'mdi-check-circle' : 'mdi-circle-outline' }}
        </v-icon>
      </template>
      <v-list-item-title>{{ item.position_name }}</v-list-item-title>
      <v-list-item-subtitle>
        <v-icon size="small">mdi-folder-outline</v-icon>
        {{ item.department_path }}
      </v-list-item-subtitle>
    </v-list-item>
  </template>
</v-autocomplete>
```

### 2. Results Card
**Component**: Custom `PositionCard.vue`
```vue
<v-card variant="outlined" class="mb-2">
  <v-card-text>
    <div class="d-flex align-center">
      <v-checkbox v-model="selected" hide-details class="flex-grow-0" />
      <div class="flex-grow-1 ml-2">
        <div class="text-subtitle-1 font-weight-medium">
          {{ position.name }}
        </div>
        <div class="text-caption text-medium-emphasis">
          <v-icon size="small">mdi-folder-outline</v-icon>
          {{ position.hierarchy_path }}
        </div>
      </div>
      <v-chip :color="statusColor" size="small" variant="flat">
        {{ statusText }}
      </v-chip>
      <v-btn-group variant="text" density="compact">
        <v-btn icon="mdi-eye" v-if="profile_exists" />
        <v-btn icon="mdi-refresh" v-if="profile_exists" />
        <v-btn icon="mdi-plus" v-else color="primary" />
      </v-btn-group>
    </div>
  </v-card-text>
</v-card>
```

### 3. Tree View
**Component**: Vuetify `v-treeview` with custom templates
```vue
<v-treeview
  :items="organizationTree"
  :open="openNodes"
  item-value="id"
  item-title="name"
  activatable
  selectable
  return-object
>
  <template #prepend="{ item }">
    <v-progress-circular
      :model-value="item.completion_percentage"
      :size="24"
      :width="2"
      color="primary"
    />
  </template>
  <template #append="{ item }">
    <v-chip size="x-small" variant="flat">
      {{ item.generated }}/{{ item.total }}
    </v-chip>
  </template>
</v-treeview>
```

---

## 🚀 Implementation Priority

### Week 4 (Current): Quick Search MVP
**Must Have**:
- ✅ Search autocomplete with API integration
- ✅ Results list with status indicators
- ✅ Single position generation
- ✅ Loading states
- ✅ Error handling

**Nice to Have**:
- ⭐ Filters (department, status)
- ⭐ Recent searches history
- ⭐ Keyboard shortcuts (Ctrl+K)

### Week 5: Enhanced Search + Tree Navigation
- Tree view component
- Multi-select
- Bulk generation preview

### Week 6: Bulk Operations
- Department-level generation
- Progress tracking
- Queue management

---

## 📐 Wireframe Flow

### User Journey: Quick Generation

```
1. Open Generator Page
   ↓
2. Type position name in search
   "Руководитель..."
   ↓
3. See autocomplete results (live)
   5 matches found
   ↓
4. Click on desired position
   "Руководитель группы анализа данных"
   ↓
5. Review position details
   Department: ДИТ → Группа анализа
   Status: ○ Not generated
   ↓
6. Click [Generate Profile]
   ↓
7. See progress indicator
   "Generating... 10s elapsed"
   ↓
8. View result inline
   ✅ Profile generated successfully!
   [View Profile] [Download] [Generate Another]
```

---

## 🎯 Success Metrics

### UX Metrics:
- **Time to First Generation**: < 30 seconds
- **Search Result Relevance**: > 90% in top 3
- **Error Rate**: < 5%
- **User Satisfaction**: > 4/5

### Technical Metrics:
- **Search Response Time**: < 200ms
- **Generation Success Rate**: > 95%
- **API Availability**: > 99.5%

---

## 🔧 Technical Considerations

### Search Optimization:
1. **Client-side caching**: Cache full org structure (567 items ~100KB)
2. **Debounced search**: 300ms delay
3. **Fuzzy matching**: Fuse.js library
4. **Result limiting**: Max 50 results

### Tree Optimization:
1. **Virtualization**: Only render visible nodes
2. **Lazy loading**: Load children on expand
3. **State persistence**: Remember open nodes

### Performance Targets:
- Initial load: < 2s
- Search response: < 200ms
- Tree expand: < 100ms
- Generation start: < 500ms

---

## 🎨 Visual Design Language

### Colors:
- **Primary**: Blue (#1976D2) - Actions, links
- **Success**: Green (#4CAF50) - Generated profiles
- **Warning**: Orange (#FF9800) - In progress
- **Error**: Red (#F44336) - Failed
- **Gray**: #757575 - Not generated

### Typography:
- **Page Title**: text-h4, font-weight-bold
- **Section Title**: text-h6, font-weight-medium
- **Position Name**: text-subtitle-1, font-weight-medium
- **Path**: text-caption, text-medium-emphasis

### Spacing:
- Card padding: 16px
- Section margin: 24px
- Item gap: 8px

---

## 📝 Next Steps

1. **Week 4 Implementation**:
   - [ ] Create `GeneratorView.vue` with tabs
   - [ ] Implement Quick Search tab
   - [ ] Integrate with `/api/organization/search-items`
   - [ ] Add generation trigger
   - [ ] Show inline results

2. **Week 5 Enhancement**:
   - [ ] Add Browse Tree tab
   - [ ] Implement tree component
   - [ ] Multi-select functionality

3. **Week 6 Bulk Operations**:
   - [ ] Bulk Actions tab
   - [ ] Queue management
   - [ ] Progress tracking

---

**Decision**: Start with **Hybrid Approach, Quick Search MVP** for Week 4
**Rationale**: Delivers immediate value, supports iterative enhancement, fits user personas


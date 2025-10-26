# Complete UX Analysis - Profile Generation System

**Date**: 2025-10-25
**Version**: 2.0 - Comprehensive Analysis
**Focus**: All user scenarios from single profile to bulk operations

---

## 🎯 Executive Summary

This document provides a complete UX analysis covering:
- **7 Primary User Scenarios**: From search to bulk download
- **21 API Endpoints**: Complete backend capability mapping
- **3 User Personas**: HR Manager, Department Head, System Admin
- **4 UI Modules**: Generator, Profiles Library, Editor, Downloads

---

## 📊 Available API Endpoints Inventory

### 1. Authentication (`/api/auth/`)
```
POST   /api/auth/login          # Get JWT token
POST   /api/auth/logout         # Logout
POST   /api/auth/refresh        # Refresh token
GET    /api/auth/me             # Current user info
GET    /api/auth/validate       # Validate token
```

### 2. Dashboard (`/api/dashboard/`)
```
GET    /api/dashboard/stats           # Full statistics
GET    /api/dashboard/stats/minimal   # Lightweight stats
GET    /api/dashboard/stats/activity  # Recent activity
```

### 3. Organization & Catalog (`/api/organization/`, `/api/catalog/`)
```
GET    /api/organization/search-items           # All 567 searchable items
GET    /api/organization/structure/{path}       # Full org tree with highlight

GET    /api/catalog/departments                 # All departments list
GET    /api/catalog/departments/{dept_name}     # Department details
GET    /api/catalog/positions/{department}      # Positions for dept
GET    /api/catalog/search                      # Search departments
GET    /api/catalog/search/positions            # Search positions
```

### 4. Profile Generation (`/api/generation/`)
```
POST   /api/generation/start              # Start async generation (returns task_id)
GET    /api/generation/{task_id}/status   # Poll task status
GET    /api/generation/{task_id}/result   # Get result when completed
DELETE /api/generation/{task_id}          # Cancel task
GET    /api/generation/tasks/active       # List all active tasks
```

### 5. Profile Management (`/api/profiles/`)
```
GET    /api/profiles/                           # List with pagination, filters, search
GET    /api/profiles/{profile_id}               # Get full profile
PUT    /api/profiles/{profile_id}               # Update metadata (NOT content yet!)
DELETE /api/profiles/{profile_id}               # Delete profile

GET    /api/profiles/{profile_id}/download/json   # Download JSON
GET    /api/profiles/{profile_id}/download/md     # Download Markdown
GET    /api/profiles/{profile_id}/download/docx   # Download Word
```

**⚠️ Current Limitations**:
- ❌ No XLSX export yet (Week 7)
- ❌ No bulk download/ZIP (Week 8)
- ❌ No inline content editing (Week 7)
- ❌ No bulk generation endpoint (use frontend orchestration)

---

## 👥 User Personas & Goals

### Persona 1: Elena - HR Manager (Daily User)
**Profile**: 32 years old, HR specialist, moderate IT skills
**Goals**:
- Generate 1-5 profiles per day for specific positions
- Find existing profiles quickly
- Download profiles for hiring managers
- Check profile quality scores

**Pain Points**:
- Doesn't remember exact department hierarchies
- Needs fast search
- Downloads same profile in different formats
- Wants to see if profile already exists before regenerating

**Primary Scenarios**: #1, #2, #3, #6

---

### Persona 2: Viktor - Department Head (Weekly User)
**Profile**: 45 years old, IT Director, power user
**Goals**:
- Generate profiles for all 30 positions in IT department
- Track completion percentage for his departments
- Bulk download profiles for department documentation
- Review and approve profiles before distribution

**Pain Points**:
- Needs overview of which positions have profiles
- Wants bulk operations (generate 10-20 at once)
- Needs to navigate department hierarchy
- Wants completion reports

**Primary Scenarios**: #4, #5, #7

---

### Persona 3: Maria - System Administrator (Occasional User)
**Profile**: 28 years old, HRIS admin, technical expert
**Goals**:
- Complete profile coverage for entire organization
- Monitor generation quality and errors
- Bulk regenerate profiles after template updates
- Export data for analytics

**Pain Points**:
- Needs to see gaps in coverage (1,487 positions → 13 profiles)
- Wants batch operations at block/department level
- Needs error tracking and retry mechanisms
- Requires data export for reports

**Primary Scenarios**: #4, #5, #7, #8 (future)

---

## 🎬 Complete User Scenarios

### Scenario 1: Quick Profile Generation (Single)
**User**: Elena (HR Manager)
**Frequency**: Daily (3-5 times per day)
**Goal**: Generate profile for "Руководитель группы анализа данных"

```
Flow:
1. Open Generator page
2. Type "Руководитель группы" in search
   ↓ API: GET /api/organization/search-items
3. See autocomplete results (5 matches)
   - Displays: Position name + Department path + Status
   - Highlights: ○ Not generated | ✓ Generated
4. Select "Руководитель группы анализа данных"
5. Review pre-filled form:
   - Department: auto-filled from selection
   - Position: auto-filled
   - Employee Name: optional input
   - Temperature: default 0.1 (can adjust)
6. Click [Generate Profile]
   ↓ API: POST /api/generation/start
   ← Returns: task_id, estimated_duration: 15-25s
7. See real-time progress (auto-polling every 2s):
   ↓ API: GET /api/generation/{task_id}/status
   - "Инициализация генератора..." (5%)
   - "Загрузка данных организации..." (20%)
   - "Анализ KPI департамента..." (40%)
   - "Генерация контента с AI..." (60%)
   - "Валидация результата..." (80%)
   - "Сохранение профиля..." (95%)
8. Generation completes (18s actual)
   ↓ API: GET /api/generation/{task_id}/result
9. See inline result preview:
   - ✅ Success indicator
   - Quality scores: Validation 95%, Completeness 87%
   - Quick preview of main sections
   - Action buttons: [View Full] [Download ▼] [Generate Another]
10. Click [Download ▼]
    - Options: JSON | Markdown | DOCX
    ↓ API: GET /api/profiles/{profile_id}/download/md
11. File downloads automatically
12. Done! (Total time: ~30 seconds including selection)
```

**Key UX Elements**:
- ⚡ Fast: Autocomplete for quick selection
- 📊 Transparent: Real-time progress with steps
- ✅ Validation: Quality scores shown immediately
- 🎯 Focused: Single-task flow, no distractions
- 🔄 Efficient: "Generate Another" for batch work

---

### Scenario 2: Search Existing Profiles
**User**: Elena (HR Manager)
**Frequency**: Daily (10-15 times per day)
**Goal**: Find profile for "Data Analyst" to send to hiring manager

```
Flow:
1. Navigate to "Profiles" page (tab/menu item)
2. See profiles library:
   - Table view with columns:
     [Position] [Department] [Created] [Quality] [Status] [Actions]
   - Pagination: Page 1 of 1 (13 profiles total)
   - Filters bar:
     • Search: [___________] 🔍
     • Department: [All Departments ▼]
     • Status: [All ▼ | Generated | In Progress | Failed]
     • Sort: [Newest ▼]
3. Type "analyst" in search field (300ms debounce)
   ↓ API: GET /api/profiles/?search=analyst&page=1&limit=20
4. Results filtered instantly (3 matches):
   - "Аналитик данных" - Группа анализа данных - 2 days ago
   - "Старший аналитик" - Департамент аналитики - 5 days ago
   - "Business Analyst" - Бизнес-анализ - 1 week ago
5. Click on "Аналитик данных" row
   ↓ API: GET /api/profiles/{profile_id}
6. Profile modal/page opens:
   - Header: Position name, department breadcrumb
   - Tabs:
     • Overview: Key info, quality scores
     • Full Profile: Complete content (expandable sections)
     • Metadata: Generation info, tokens, model, trace_id
     • History: Changes, versions (future)
   - Actions toolbar:
     [Edit] [Download ▼] [Regenerate] [Share] [Delete]
7. Click [Download ▼]
   - Quick download: MD (default) | JSON | DOCX
   ↓ API: GET /api/profiles/{profile_id}/download/md
8. File downloads, modal stays open
9. Close modal or continue browsing
```

**Key UX Elements**:
- 🔍 Powerful search: Full-text across all fields
- 🎨 Rich filters: Department, status, date range
- 👁 Quick preview: Modal for fast review
- 📥 Fast download: One-click from modal
- 🔄 Stay in context: No page refresh needed

---

### Scenario 3: Regenerate Outdated Profile
**User**: Elena (HR Manager)
**Frequency**: Weekly
**Goal**: Update profile after template/KPI changes

```
Flow:
1. Open Profiles library
2. Filter by department: "Группа анализа данных"
   ↓ API: GET /api/profiles/?department=Группа анализа данных
3. See profile with indicators:
   - "Аналитик данных"
   - 🟡 Warning badge: "Template updated 2 days ago"
   - Quality: 85% (was 95% before template update)
4. Click [Regenerate] button
5. Confirmation modal:
   ┌─────────────────────────────────────┐
   │ Regenerate Profile?                 │
   ├─────────────────────────────────────┤
   │ Current profile: Аналитик данных    │
   │ Created: 2 weeks ago                │
   │ Quality: 85%                        │
   │                                     │
   │ ⚠️ This will:                       │
   │ • Create new version with latest    │
   │   template and KPIs                 │
   │ • Keep old version in history       │
   │ • Update quality scores             │
   │                                     │
   │ Employee name (optional):           │
   │ [___________________________]       │
   │                                     │
   │ Temperature: [0.1 ▼]                │
   │                                     │
   │ [Cancel]  [Regenerate Profile]      │
   └─────────────────────────────────────┘
6. Click [Regenerate Profile]
   ↓ API: POST /api/generation/start (same department/position)
7. See progress in place (profile row shows progress bar)
8. Completion notification:
   "✅ Profile regenerated! Quality: 95% (+10%)"
9. Auto-refresh profile view
   ↓ API: GET /api/profiles/{new_profile_id}
10. Compare old vs new (side-by-side view - future feature)
```

**Key UX Elements**:
- 🔔 Proactive: Warnings for outdated profiles
- 📜 Versioning: Keep history (future)
- 🎯 Context-aware: Pre-fill from existing
- 📊 Comparison: Show quality improvements
- ⚡ In-place: No navigation needed

---

### Scenario 4: Bulk Generation - Department Level
**User**: Viktor (Department Head)
**Frequency**: Monthly
**Goal**: Generate profiles for all 30 positions in IT department

```
Flow:
1. Open Generator page
2. Switch to [🌳 Browse Tree] tab
3. See organization tree with completion indicators:
   ▼ Блок информационных технологий     [13/50] ████░░░░░░ 26%
     ▼ Департамент ИТ                   [10/30] ███░░░░░░░ 33%
       ► Управление разработки           [0/10] ░░░░░░░░░░  0%  ← Viktor's dept
       ▼ Группа анализа данных           [3/5]  ██████░░░░ 60%
4. Expand "Управление разработки" node
5. See all 10 positions with checkboxes:
   ☐ Руководитель управления разработки    [○ New]
   ☐ Архитектор программного обеспечения   [○ New]
   ☐ Team Lead (Backend)                   [○ New]
   ☐ Senior Backend Developer              [○ New]
   ☐ Backend Developer                     [○ New]
   ☐ Senior Frontend Developer             [○ New]
   ☐ Frontend Developer                    [○ New]
   ☐ QA Engineer                          [○ New]
   ☐ DevOps Engineer                      [○ New]
   ☐ Intern Developer                     [○ New]
6. Click [Select All Ungenerated] button (selects all 10)
7. Review selection panel:
   ┌──────────────────────────────────────┐
   │ Selected: 10 positions               │
   │ Estimated time: 3-5 minutes          │
   │ Estimated cost: ~$0.15               │
   │                                      │
   │ Options:                             │
   │ Temperature: [0.1 ▼]                 │
   │ Save to database: [✓]               │
   │ Auto-download: [✓ All as ZIP]       │
   │                                      │
   │ [Clear Selection] [Generate All →]  │
   └──────────────────────────────────────┘
8. Click [Generate All →]
9. Frontend creates 10 tasks (with rate limiting: 5 concurrent max)
   Loop: For each position:
     ↓ API: POST /api/generation/start
     ← task_id
10. Bulk progress view:
   ┌───────────────────────────────────────────┐
   │ Generating 10 profiles...                 │
   │ ████████░░░░░░░░░░░░░░░░░░░░░░ 4/10 (40%)│
   │                                           │
   │ ✅ Руководитель управления (22s)          │
   │ ✅ Архитектор ПО (18s)                    │
   │ ✅ Team Lead Backend (25s)                │
   │ 🔄 Senior Backend Dev... (15s)            │
   │ 🔄 Backend Developer... (8s)              │
   │ ⏳ Senior Frontend Dev... queued          │
   │ ⏳ Frontend Developer... queued           │
   │ ⏳ QA Engineer... queued                  │
   │ ⏳ DevOps Engineer... queued              │
   │ ⏳ Intern Developer... queued             │
   │                                           │
   │ [Pause] [Cancel Remaining]                │
   └───────────────────────────────────────────┘
11. Auto-poll all tasks (2s interval):
    Loop: For each active task_id:
      ↓ API: GET /api/generation/{task_id}/status
12. All complete (4m 15s total):
    ┌───────────────────────────────────────────┐
    │ ✅ Generation Complete!                    │
    │ ██████████████████████████████ 10/10 (100%)│
    │                                           │
    │ Success: 10 | Failed: 0                   │
    │ Total time: 4m 15s                        │
    │ Average quality: 93%                      │
    │                                           │
    │ [Download All (ZIP)] [View Profiles]      │
    └───────────────────────────────────────────┘
13. Click [Download All (ZIP)]
    - Frontend generates ZIP client-side (JSZip)
    - For each profile_id:
      ↓ API: GET /api/profiles/{id}/download/md
    - Combines into single ZIP: "IT_Development_Profiles.zip"
14. ZIP downloads automatically
15. Tree view auto-updates:
    ► Управление разработки  [10/10] ██████████ 100% ✅
```

**Key UX Elements**:
- 🌳 Visual hierarchy: See completion at all levels
- ☑️ Bulk selection: One click for whole department
- 📊 Progress tracking: Individual + aggregate
- 💰 Cost estimation: Show before starting
- ⚡ Rate limiting: Avoid API overload (5 concurrent)
- 📦 Auto-download: ZIP all results
- 🔄 State persistence: Remember tree expansion

---

### Scenario 5: Find Coverage Gaps
**User**: Maria (System Administrator)
**Frequency**: Weekly
**Goal**: Identify departments with low profile coverage

```
Flow:
1. Open Dashboard
2. See top-level stats:
   - Total Positions: 1,487
   - Profiles Generated: 13
   - Completion: 0.9%
   - ⚠️ Warning: Very low coverage!
3. Click on "Completion: 0.9%" card
4. Navigate to "Coverage Report" view:
   ┌──────────────────────────────────────────────┐
   │ Profile Coverage by Department               │
   ├──────────────────────────────────────────────┤
   │ Filters: [Show: All ▼] [Min positions: 5 ▼] │
   │                                              │
   │ [Chart View] [Table View] ← Active          │
   │                                              │
   │ Department              Positions  Generated │
   │ ───────────────────────────────────────────  │
   │ ▼ Блок ИТ (26%)            50        13      │
   │   └ ДИТ (33%)              30        10      │
   │   └ Управление разработки   10         0 ❌   │
   │   └ Группа анализа (60%)     5         3      │
   │                                              │
   │ ▼ Блок безопасности (0%)   15         0 ❌   │
   │   └ Служба безопасности     14         0 ❌   │
   │                                              │
   │ ▼ HR Блок (0%)            125         0 ❌   │
   │   └ Департамент HR          50         0 ❌   │
   │   └ Рекрутинг               25         0 ❌   │
   │                                              │
   │ Sort: [Coverage ▼]                           │
   │ [Export CSV] [Generate Missing] [View Tree]  │
   └──────────────────────────────────────────────┘
5. Filter "Show: No Coverage Only"
   - Shows 554 departments with 0 profiles
6. Select multiple departments (checkbox):
   ☑ Управление разработки (10 positions)
   ☑ Служба безопасности (14 positions)
   ☑ Департамент HR (50 positions)
7. Click [Generate Missing]
8. Bulk generation wizard:
   ┌──────────────────────────────────────────┐
   │ Step 1: Review Selection                 │
   │ ─────────────────────────────────────────│
   │ Selected: 3 departments                  │
   │ Total positions: 74                      │
   │                                          │
   │ Breakdown:                               │
   │ • Управление разработки: 10 positions    │
   │ • Служба безопасности: 14 positions      │
   │ • Департамент HR: 50 positions           │
   │                                          │
   │ Estimated time: 10-15 minutes            │
   │ Estimated cost: ~$1.20                   │
   │                                          │
   │ [Back] [Next: Configure →]               │
   └──────────────────────────────────────────┘
9. Configure settings
10. Start batch generation (similar to Scenario 4)
11. Report updates automatically with progress
```

**Key UX Elements**:
- 📊 Dashboard integration: Quick access
- 🎯 Filterable report: Find gaps easily
- 📈 Visual indicators: Color-coded coverage
- 🔢 Sortable columns: By coverage, size, name
- ☑️ Multi-select: Batch operations
- 📤 Export: CSV for analysis
- 🔄 Live updates: Auto-refresh during generation

---

### Scenario 6: Download in Multiple Formats
**User**: Elena (HR Manager)
**Frequency**: Daily
**Goal**: Send profile to hiring manager in their preferred format

```
Flow:
1. Search and open profile (Scenario 2)
2. In profile view, see download section:
   ┌────────────────────────────────────┐
   │ Downloads                          │
   ├────────────────────────────────────┤
   │ Available formats:                 │
   │                                    │
   │ [📄 JSON]   - Machine-readable     │
   │ [📝 Markdown] - Text editor        │
   │ [📘 DOCX]   - Microsoft Word       │
   │ [🚫 XLSX]   - Not available yet    │ ← Week 7
   │                                    │
   │ Recent downloads:                  │
   │ • DOCX - 2 days ago                │
   │ • MD - 1 week ago                  │
   └────────────────────────────────────┘
3. Click [📘 DOCX]
   ↓ API: GET /api/profiles/{profile_id}/download/docx
4. File downloads immediately: "Аналитик_данных_profile.docx"
5. Manager requests JSON for API integration
6. Click [📄 JSON]
   ↓ API: GET /api/profiles/{profile_id}/download/json
7. JSON downloads: "Аналитик_данных_profile.json"
8. Track download count in metadata (future analytics)
```

**Key UX Elements**:
- 🎨 Visual format selector: Icons + descriptions
- 📊 Format guidance: Show use cases
- 📜 Download history: Track what was shared
- ⚡ One-click: Direct download, no modals
- 🔔 Future: Email sharing, URL links

---

### Scenario 7: Bulk Download for Documentation
**User**: Viktor (Department Head)
**Frequency**: Monthly
**Goal**: Download all IT department profiles for documentation package

```
Flow:
1. Open Profiles library
2. Filter by department: "Департамент ИТ"
   ↓ API: GET /api/profiles/?department=Департамент ИТ
3. See 10 results
4. Click [Select All] (checkbox in header)
5. Bulk actions bar appears:
   ┌────────────────────────────────────────┐
   │ 10 selected                            │
   │ [Clear] [Download All ▼] [Delete]     │
   └────────────────────────────────────────┘
6. Click [Download All ▼]
7. Format selection modal:
   ┌────────────────────────────────────────┐
   │ Bulk Download Options                  │
   ├────────────────────────────────────────┤
   │ Format:                                │
   │ ○ JSON (all in one file)               │
   │ ● Markdown (separate files in ZIP)    │
   │ ○ DOCX (separate files in ZIP)        │
   │ ○ Mixed (choose per profile) ← future │
   │                                        │
   │ File naming:                           │
   │ ● [Position]_[Department].md           │
   │ ○ [Department]_[Position].md           │
   │ ○ Custom template: [___________]       │
   │                                        │
   │ Include:                               │
   │ ☑ Metadata file (CSV)                  │
   │ ☑ README with summary                  │
   │ ☐ Source JSON files                    │
   │                                        │
   │ [Cancel] [Generate ZIP]                │
   └────────────────────────────────────────┘
8. Click [Generate ZIP]
9. Progress modal:
   "Preparing download... 7/10 files"
10. ZIP generates client-side:
    - For each profile:
      ↓ API: GET /api/profiles/{id}/download/md
    - Create ZIP structure:
      ```
      IT_Department_Profiles.zip
      ├── README.md
      ├── profiles_metadata.csv
      ├── Руководитель_ИТ.md
      ├── Архитектор_ПО.md
      ├── Team_Lead_Backend.md
      └── ... (7 more)
      ```
11. ZIP downloads: "IT_Department_Profiles_2025-10-25.zip"
12. Success notification with file size: "10.2 MB downloaded"
```

**Key UX Elements**:
- ☑️ Bulk selection: Multi-select from table
- 🎨 Format choice: Per download decision
- 📝 Naming templates: Consistent file names
- 📦 Metadata included: CSV summary for spreadsheets
- 📄 README: Auto-generated documentation
- ⏱ Progress: Show preparation status

---

## 🗺 UX Information Architecture

### Navigation Structure

```
App Layout
├── Dashboard (Week 3) ✅
│   ├── Stats cards
│   ├── Quick actions
│   └── Recent activity
│
├── Generator (Week 4) ← CURRENT
│   ├── Tab: 🔍 Quick Search
│   │   ├── Search autocomplete
│   │   ├── Filters
│   │   ├── Results list
│   │   └── Generation form
│   ├── Tab: 🌳 Browse Tree (Week 5)
│   │   ├── Organization tree
│   │   ├── Multi-select
│   │   └── Bulk actions
│   └── Tab: ⚡ Bulk Actions (Week 6)
│       ├── Department selector
│       ├── Position picker
│       └── Batch generation
│
├── Profiles Library (Week 5)
│   ├── Search & Filters
│   ├── Table/Grid view toggle
│   ├── Profile modal/detail
│   │   ├── Tab: Overview
│   │   ├── Tab: Full Profile
│   │   ├── Tab: Metadata
│   │   └── Tab: History (future)
│   └── Bulk operations
│
├── Coverage Report (Week 6)
│   ├── Department breakdown
│   ├── Gap analysis
│   ├── Chart visualizations
│   └── Export tools
│
└── Settings (Week 8)
    ├── User preferences
    ├── Generation defaults
    └── Export templates
```

---

## 🎨 UI Component Library

### Reusable Components Needed

#### 1. PositionSearchAutocomplete
```vue
<PositionSearchAutocomplete
  v-model="selectedPosition"
  :filters="{ has_profile: false }"
  :show-department-path="true"
  :show-status-badge="true"
  @select="handlePositionSelect"
/>
```

**Features**:
- Fuzzy search (Fuse.js)
- 300ms debounce
- Keyboard navigation
- Status indicators
- Department breadcrumbs

---

#### 2. OrganizationTree
```vue
<OrganizationTree
  :items="organizationData"
  :selectable="true"
  :show-completion="true"
  v-model:selected="selectedPositions"
  @node-expand="handleExpand"
/>
```

**Features**:
- Lazy loading
- Progress bars per node
- Multi-select checkboxes
- [generated/total] counters
- Expand/collapse all

---

#### 3. GenerationProgressTracker
```vue
<GenerationProgressTracker
  :task-id="taskId"
  :auto-poll="true"
  @complete="handleComplete"
  @error="handleError"
/>
```

**Features**:
- Real-time polling (2s interval)
- Step-by-step progress
- Time elapsed/estimated
- Cancellation support
- Error recovery

---

#### 4. ProfileCard
```vue
<ProfileCard
  :profile="profileData"
  :actions="['view', 'download', 'regenerate', 'delete']"
  :show-quality-scores="true"
  @action="handleAction"
/>
```

**Features**:
- Compact/expanded views
- Quality badge
- Action buttons
- Status indicators
- Metadata tooltip

---

#### 5. BulkOperationPanel
```vue
<BulkOperationPanel
  :selected-count="selectedPositions.length"
  :estimated-time="estimatedTime"
  :estimated-cost="estimatedCost"
  @generate="handleBulkGenerate"
  @clear="clearSelection"
/>
```

**Features**:
- Selection summary
- Cost/time estimation
- Batch configuration
- Progress tracking
- Cancel support

---

#### 6. DownloadMenu
```vue
<DownloadMenu
  :profile-id="profileId"
  :formats="['json', 'md', 'docx']"
  :show-history="true"
  @download="handleDownload"
/>
```

**Features**:
- Format selector
- Download history
- One-click download
- Progress indicator
- Error handling

---

## 📊 State Management Architecture

### Pinia Stores

#### 1. `useGeneratorStore`
```typescript
{
  // Search state
  searchQuery: string
  searchResults: SearchResult[]
  searching: boolean

  // Selection state
  selectedPosition: Position | null
  selectedPositions: Position[]  // For bulk

  // Generation state
  activeTasks: Map<string, TaskStatus>

  // Actions
  searchPositions(query: string)
  startGeneration(request: GenerationRequest)
  pollTaskStatus(taskId: string)
  cancelTask(taskId: string)
}
```

#### 2. `useProfilesStore`
```typescript
{
  // Profiles list
  profiles: Profile[]
  pagination: PaginationMeta
  filters: ProfileFilters

  // Current profile
  currentProfile: Profile | null

  // Actions
  fetchProfiles(params: FilterParams)
  getProfile(id: string)
  updateProfile(id: string, data: Partial<Profile>)
  deleteProfile(id: string)
  downloadProfile(id: string, format: 'json'|'md'|'docx')
}
```

#### 3. `useCatalogStore`
```typescript
{
  // Organization data
  organizationTree: OrgNode[]
  searchableItems: SearchableItem[]
  departments: Department[]

  // Cache state
  loaded: boolean
  lastUpdated: Date

  // Actions
  loadOrganization()
  searchItems(query: string)
  getDepartmentPositions(dept: string)
}
```

---

## ⚡ Performance Optimization Strategy

### 1. Data Loading
- **Initial load**: Cache full org structure (~100KB) in localStorage
- **TTL**: 24 hours before refresh
- **Invalidation**: Manual refresh button
- **Prefetch**: Load on login, not on page visit

### 2. Search Performance
- **Client-side search**: Fuse.js on cached data
- **Debounce**: 300ms delay
- **Result limiting**: Max 50 results
- **Highlighting**: Mark matching terms

### 3. Polling Optimization
- **Active tasks**: Poll every 2s
- **Completed tasks**: Stop polling
- **Batch polling**: Single request for multiple tasks (if backend supports)
- **Exponential backoff**: On errors

### 4. Download Optimization
- **Streaming**: Use blob URLs
- **Parallel**: 3 concurrent downloads max
- **Progress**: Track individual file progress
- **Error recovery**: Retry failed downloads

---

## 🎯 Phased Implementation Plan

### Week 4: Quick Search MVP (Starting Now)
**Must Have**:
- ✅ Search autocomplete component
- ✅ Single generation flow
- ✅ Progress tracking
- ✅ Result preview
- ✅ Download (JSON, MD, DOCX)

**API Endpoints Used**:
- GET /api/organization/search-items
- POST /api/generation/start
- GET /api/generation/{id}/status
- GET /api/generation/{id}/result
- GET /api/profiles/{id}/download/*

**Deliverables**:
- `GeneratorView.vue` (Quick Search tab)
- `PositionSearchAutocomplete.vue`
- `GenerationProgressTracker.vue`
- `useGeneratorStore.ts`

---

### Week 5: Profiles Library + Tree Navigation
**Must Have**:
- ✅ Profiles list with table view
- ✅ Search & filters
- ✅ Profile detail modal
- ✅ Browse Tree tab in Generator

**API Endpoints Used**:
- GET /api/profiles/ (with pagination)
- GET /api/profiles/{id}
- DELETE /api/profiles/{id}

**Deliverables**:
- `ProfilesView.vue`
- `ProfileDetailModal.vue`
- `OrganizationTree.vue`
- `useProfilesStore.ts`

---

### Week 6: Bulk Operations
**Must Have**:
- ✅ Multi-select in tree
- ✅ Bulk generation orchestration
- ✅ Progress tracking for batches
- ✅ Bulk download (client-side ZIP)

**Frontend Orchestration**:
- Loop with rate limiting (5 concurrent)
- Individual task tracking
- Aggregate progress
- Error handling per task

**Deliverables**:
- `BulkOperationPanel.vue`
- `BulkProgressTracker.vue`
- JSZip integration for downloads

---

### Week 7: Editing + XLSX (Backend Changes Needed)
**Backend TODO**:
- 🔧 Extend PUT /api/profiles/{id} for content editing
- 🔧 Add GET /api/profiles/{id}/download/xlsx

**Frontend**:
- ✅ Inline editor component
- ✅ XLSX export integration

---

### Week 8: Polish + Bulk Download Endpoint
**Backend TODO** (optional):
- 🔧 POST /api/profiles/download/bulk (server-side ZIP)

**Frontend**:
- ✅ Coverage report view
- ✅ Advanced filters
- ✅ Settings page
- ✅ Error boundary improvements

---

## ✅ Success Metrics

### Performance
- Initial load: < 2s
- Search response: < 200ms
- Generation time: 15-30s (API dependent)
- Download initiation: < 500ms

### UX Quality
- Time to first generation: < 30s (from app open)
- Search relevance: > 90% correct in top 3
- Error rate: < 5%
- User satisfaction: > 4/5

### Business Metrics
- Daily active users: Track growth
- Profiles generated per day: > 50
- Completion rate: Improve from 0.9% to 10% in month 1
- Download rate: > 80% of profiles downloaded

---

## 🚨 Edge Cases & Error Handling

### Error Scenarios

#### 1. API Failures
- **Network timeout**: Retry with exponential backoff
- **401 Unauthorized**: Redirect to login
- **429 Rate limit**: Show queue position, retry after delay
- **500 Server error**: Show friendly message, enable manual retry

#### 2. Generation Failures
- **LLM timeout**: Allow retry with different temperature
- **Validation failure**: Show validation errors, allow editing
- **Partial completion**: Save progress, allow resume

#### 3. Data Issues
- **Missing department**: Show warning, allow manual input
- **Duplicate positions**: Ask user to clarify
- **No KPIs found**: Generate without KPIs, mark as incomplete

#### 4. User Errors
- **Empty selection**: Disable generate button
- **Too many selected**: Warn about cost/time, add confirmation
- **Network offline**: Queue tasks, sync when online

---

## 📱 Mobile/Tablet Considerations

### Responsive Breakpoints
- **Desktop**: > 1200px (full features)
- **Tablet**: 768-1199px (adapted layout)
- **Mobile**: < 768px (limited to essential features)

### Mobile-First Features (Week 8)
- Search-only mode (no tree navigation)
- Single generation workflow
- View profiles (read-only)
- Download profiles

**Not on Mobile**:
- Tree navigation
- Bulk operations
- Inline editing

---

## 🎓 User Onboarding

### First-Time User Experience

#### Tour Steps:
1. **Welcome**: "Let's generate your first profile!"
2. **Search**: "Type any position name to get started"
3. **Select**: "Choose from autocomplete results"
4. **Generate**: "Click to start AI generation"
5. **Download**: "Get your profile in any format"
6. **Next Steps**: "Explore tree view for bulk operations"

#### Help Resources:
- Tooltips on hover
- Contextual help (?icons)
- Video tutorials (embedded)
- FAQ page
- Support chat (future)

---

## 🔐 Security & Permissions (Future)

### Role-Based Access (Not in MVP)
- **Viewer**: Read profiles only
- **HR**: Generate + download
- **Admin**: Full access + deletion

### Audit Log
- Track who generated what
- Download history
- Edit history
- Deletion logs

---

## 📝 Next Steps & Decisions Needed

### Questions for User:

1. **Week 4 Priority**: Confirm Quick Search tab as starting point?
2. **Bulk Strategy**: Client-side orchestration OK for Week 6?
3. **Downloads**: Is client-side ZIP acceptable? Or need backend endpoint?
4. **Editing**: Week 7 feature - what level of editing? (metadata only vs full content)
5. **Mobile**: Should we scope mobile for Week 8 or defer to later?

### Ready to Start Implementation

I have complete specifications for:
- Component architecture
- State management
- API integration
- User flows

Ready to code! 🚀


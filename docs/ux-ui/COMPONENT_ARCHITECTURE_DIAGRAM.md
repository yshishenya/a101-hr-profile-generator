# Vue.js Component Architecture - Visual Diagram

**Document Date:** 2025-10-25
**Purpose:** Visual representation of Vue component hierarchy and data flow

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Vue.js Application                      │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   Router    │  │ Pinia Stores │  │  Composables    │  │  │
│  │  │  (Routes)   │  │   (State)    │  │  (Logic)        │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │         │                 │                   │            │  │
│  │         └─────────────────┼───────────────────┘            │  │
│  │                           │                                │  │
│  │  ┌────────────────────────▼─────────────────────────────┐ │  │
│  │  │             Component Hierarchy                        │ │  │
│  │  │   (MainLayout → Pages → Smaller Components)          │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                           │                                │  │
│  │                           ▼                                │  │
│  │  ┌────────────────────────────────────────────────────┐   │  │
│  │  │           API Client (Axios)                        │   │  │
│  │  │   - JWT Authentication                              │   │  │
│  │  │   - Error Interceptors                              │   │  │
│  │  │   - Request/Response Logging                        │   │  │
│  │  └────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────┼─────────────────────────┘  │
└────────────────────────────────┼───────────────────────────────┘
                                  │
                                  │ HTTP/HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend Server (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints                                       │   │
│  │  - /api/auth/login                                        │   │
│  │  - /api/generation/start                                  │   │
│  │  - /api/profiles/                                         │   │
│  │  - /api/organization/search-items                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │   SQLite     │  │  LLM Service │  │  File Storage      │    │
│  │  (Profiles)  │  │  (OpenRouter)│  │  (JSON/DOCX/MD)    │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Tree Structure

```
App.vue
│
├─ MainLayout.vue
│  │
│  ├─ AppHeader.vue
│  │  ├─ Logo
│  │  ├─ Navigation Menu
│  │  │  ├─ NavLink (Home)
│  │  │  ├─ NavLink (Generator) ← Primary
│  │  │  ├─ NavLink (Profiles)
│  │  │  └─ NavLink (Analytics)
│  │  ├─ NotificationBell
│  │  └─ UserDropdown
│  │     ├─ Profile Link
│  │     ├─ Settings Link
│  │     └─ Logout Button
│  │
│  ├─ <router-view /> ← Page Components
│  │  │
│  │  ├─ HomePage.vue
│  │  │  ├─ WelcomeBanner (dismissible)
│  │  │  ├─ StatsCards
│  │  │  │  ├─ StatCard (Total Profiles)
│  │  │  │  ├─ StatCard (Monthly Profiles)
│  │  │  │  └─ StatCard (Active Tasks)
│  │  │  ├─ QuickActions
│  │  │  │  ├─ Button (Generate) ← Primary CTA
│  │  │  │  ├─ Button (View All)
│  │  │  │  └─ Button (Analytics)
│  │  │  ├─ RecentActivity
│  │  │  │  └─ ActivityItem[] (Timeline)
│  │  │  └─ DepartmentChart
│  │  │     └─ BarChart (Chart.js)
│  │  │
│  │  ├─ GeneratorPage.vue ★ MAIN FEATURE
│  │  │  │
│  │  │  ├─ PositionSearch
│  │  │  │  ├─ SearchInput
│  │  │  │  │  └─ el-autocomplete
│  │  │  │  │     ├─ SearchResultItem[]
│  │  │  │  │     │  ├─ Position Name (bold)
│  │  │  │  │     │  ├─ Department Path (gray)
│  │  │  │  │     │  └─ Position Count Badge
│  │  │  │  │     └─ EmptyState (no results)
│  │  │  │  ├─ DepartmentFilter
│  │  │  │  │  └─ el-tree-select (hierarchy)
│  │  │  │  └─ HierarchyBreadcrumb
│  │  │  │     └─ el-breadcrumb
│  │  │  │
│  │  │  ├─ SelectedPositionCard (v-if="selected")
│  │  │  │  ├─ Position Name (H3)
│  │  │  │  ├─ Full Hierarchy Path
│  │  │  │  ├─ Department Info
│  │  │  │  ├─ Existing Profiles Count
│  │  │  │  └─ Change Position Link
│  │  │  │
│  │  │  ├─ GenerationControls
│  │  │  │  ├─ ModeToggle (Single / Bulk)
│  │  │  │  ├─ SingleModeForm (v-if="mode=single")
│  │  │  │  │  ├─ el-input (Employee Name)
│  │  │  │  │  ├─ el-slider (Temperature)
│  │  │  │  │  ├─ el-collapse (Advanced Settings)
│  │  │  │  │  │  ├─ el-checkbox (Save Result)
│  │  │  │  │  │  └─ el-input (Custom Instructions)
│  │  │  │  │  └─ el-button (Generate) ← Primary
│  │  │  │  │     └─ Estimated Time (45s)
│  │  │  │  └─ BulkModeUpload (v-if="mode=bulk")
│  │  │  │     ├─ CSVTemplateDownload
│  │  │  │     ├─ el-upload (CSV Dropzone)
│  │  │  │     ├─ UploadedFilePreview
│  │  │  │     │  └─ DataTable (positions to generate)
│  │  │  │     └─ el-button (Start Batch)
│  │  │  │
│  │  │  ├─ ProgressTracker (v-if="activeTasks.length")
│  │  │  │  └─ ActiveTasksList
│  │  │  │     └─ TaskCard[] (for each task)
│  │  │  │        ├─ Position Name
│  │  │  │        ├─ el-progress (0-100%)
│  │  │  │        ├─ Current Step Description
│  │  │  │        ├─ Time Info (elapsed/remaining)
│  │  │  │        └─ el-button (Cancel, icon)
│  │  │  │
│  │  │  └─ ProfilePreview (v-if="previewData")
│  │  │     ├─ ProfileTabs
│  │  │     │  └─ el-tabs
│  │  │     │     ├─ TabPane (Overview)
│  │  │     │     ├─ TabPane (Responsibilities)
│  │  │     │     ├─ TabPane (Skills)
│  │  │     │     └─ TabPane (KPIs)
│  │  │     └─ ExportButton
│  │  │        └─ el-dropdown (JSON/DOCX/MD/PDF)
│  │  │
│  │  ├─ ProfilesPage.vue
│  │  │  │
│  │  │  ├─ PageHeader
│  │  │  │  ├─ Title (H2)
│  │  │  │  └─ CreateButton
│  │  │  │
│  │  │  ├─ FiltersPanel (collapsible sidebar)
│  │  │  │  ├─ DepartmentSelector
│  │  │  │  │  └─ el-tree-select
│  │  │  │  ├─ PositionSearch
│  │  │  │  │  └─ el-autocomplete
│  │  │  │  ├─ DateRangePicker
│  │  │  │  │  └─ el-date-picker (range)
│  │  │  │  ├─ StatusFilter
│  │  │  │  │  └─ el-checkbox-group
│  │  │  │  │     ├─ Active
│  │  │  │  │     └─ Archived
│  │  │  │  ├─ CreatedByFilter
│  │  │  │  │  └─ el-select (users)
│  │  │  │  ├─ ApplyFiltersButton
│  │  │  │  └─ ClearAllLink
│  │  │  │
│  │  │  ├─ ProfilesListView
│  │  │  │  ├─ BulkActionsToolbar (v-if="selected.length")
│  │  │  │  │  ├─ Selected Count
│  │  │  │  │  ├─ ExportSelectedDropdown
│  │  │  │  │  ├─ ArchiveSelectedButton
│  │  │  │  │  ├─ DeleteSelectedButton
│  │  │  │  │  └─ DeselectAllButton
│  │  │  │  ├─ DataTable
│  │  │  │  │  └─ el-table
│  │  │  │  │     ├─ Column (Checkbox)
│  │  │  │  │     ├─ Column (Position) → sortable
│  │  │  │  │     ├─ Column (Department) → sortable
│  │  │  │  │     ├─ Column (Employee) → sortable
│  │  │  │  │     ├─ Column (Created) → sortable
│  │  │  │  │     ├─ Column (Created By) → sortable
│  │  │  │  │     ├─ Column (Status) → badge
│  │  │  │  │     └─ Column (Actions) → dropdown
│  │  │  │  │        ├─ View
│  │  │  │  │        ├─ Edit
│  │  │  │  │        ├─ Export
│  │  │  │  │        ├─ Archive
│  │  │  │  │        └─ Delete
│  │  │  │  ├─ PaginationBar
│  │  │  │  │  └─ el-pagination
│  │  │  │  │     ├─ Items per page selector
│  │  │  │  │     ├─ Page numbers
│  │  │  │  │     └─ Total count
│  │  │  │  └─ EmptyState (v-if="!profiles.length")
│  │  │  │     ├─ Icon (magnifying glass)
│  │  │  │     ├─ Title (No profiles found)
│  │  │  │     ├─ Description
│  │  │  │     └─ GenerateButton
│  │  │  │
│  │  │  └─ ProfileDetailView (route: /profiles/:id)
│  │  │     ├─ StickyHeader
│  │  │     │  ├─ BackButton
│  │  │     │  ├─ PositionName (H2)
│  │  │     │  ├─ DepartmentBreadcrumb
│  │  │     │  └─ ActionsToolbar
│  │  │     │     ├─ EditButton
│  │  │     │     ├─ ExportDropdown
│  │  │     │     ├─ ShareLinkButton
│  │  │     │     └─ MoreDropdown
│  │  │     │        ├─ Archive
│  │  │     │        ├─ Delete
│  │  │     │        └─ Duplicate
│  │  │     ├─ ProfileTabs
│  │  │     │  └─ el-tabs
│  │  │     │     ├─ TabPane: Overview
│  │  │     │     │  ├─ PositionInfoCard
│  │  │     │     │  ├─ SummarySection
│  │  │     │     │  └─ MetadataCard
│  │  │     │     ├─ TabPane: Responsibilities
│  │  │     │     │  ├─ ResponsibilityList (numbered)
│  │  │     │     │  ├─ AddResponsibilityButton
│  │  │     │     │  └─ DragHandles (reorder)
│  │  │     │     ├─ TabPane: Qualifications
│  │  │     │     │  ├─ RequiredSkillsTags
│  │  │     │     │  ├─ EducationSection
│  │  │     │     │  ├─ ExperienceSection
│  │  │     │     │  └─ CertificationsSection
│  │  │     │     ├─ TabPane: KPIs
│  │  │     │     │  ├─ KPIsTable
│  │  │     │     │  │  └─ el-table
│  │  │     │     │  ├─ AddKPIButton
│  │  │     │     │  └─ KPIVisualization (chart)
│  │  │     │     ├─ TabPane: Context
│  │  │     │     │  ├─ ReportingStructure (org chart)
│  │  │     │     │  └─ CareerPath
│  │  │     │     └─ TabPane: Versions
│  │  │     │        ├─ VersionTimeline
│  │  │     │        │  └─ el-timeline
│  │  │     │        │     └─ VersionItem[]
│  │  │     │        │        ├─ Version Number
│  │  │     │        │        ├─ Date/Time
│  │  │     │        │        ├─ Modified By
│  │  │     │        │        ├─ Change Summary
│  │  │     │        │        └─ ViewButton
│  │  │     │        └─ RestoreVersionButton
│  │  │     └─ EditModeOverlay (v-if="editing")
│  │  │        ├─ RichTextEditor (TipTap)
│  │  │        ├─ AutoSaveIndicator
│  │  │        ├─ SaveButton
│  │  │        └─ DiscardButton
│  │  │
│  │  ├─ AnalyticsPage.vue
│  │  │  ├─ PageHeader
│  │  │  ├─ KeyMetricsCards
│  │  │  │  ├─ MetricCard (Total Profiles)
│  │  │  │  ├─ MetricCard (Monthly Profiles)
│  │  │  │  ├─ MetricCard (Avg Generation Time)
│  │  │  │  └─ MetricCard (Success Rate)
│  │  │  ├─ ChartSection: Usage Trends
│  │  │  │  └─ LineChart (Chart.js)
│  │  │  ├─ ChartSection: Department Distribution
│  │  │  │  └─ BarChart (Chart.js)
│  │  │  ├─ ChartSection: Performance
│  │  │  │  ├─ DonutChart (Success vs Failed)
│  │  │  │  └─ AreaChart (Time Trend)
│  │  │  ├─ ChartSection: LLM Stats
│  │  │  │  └─ StackedAreaChart (Tokens)
│  │  │  ├─ UserActivityTable
│  │  │  │  └─ el-table (Top users)
│  │  │  └─ FiltersSidebar
│  │  │     ├─ DateRangePicker
│  │  │     ├─ DepartmentFilter
│  │  │     ├─ UserFilter
│  │  │     └─ ExportButton (CSV/Excel)
│  │  │
│  │  └─ SettingsPage.vue
│  │     ├─ SettingsTabs
│  │     │  ├─ TabPane: Profile Settings
│  │     │  │  ├─ DisplayPreferences
│  │     │  │  ├─ DefaultFilters
│  │     │  │  └─ NotificationPreferences
│  │     │  ├─ TabPane: Account
│  │     │  │  ├─ ChangePasswordForm
│  │     │  │  ├─ SessionManagement
│  │     │  │  └─ APIKeysSection
│  │     │  └─ TabPane: Admin (v-if="isAdmin")
│  │     │     ├─ UserManagement
│  │     │     │  └─ UsersTable
│  │     │     ├─ SystemConfiguration
│  │     │     └─ DataManagement
│  │     └─ SaveSettingsButton
│  │
│  └─ AppFooter.vue
│     ├─ Version Info
│     └─ Support Links
│
└─ AuthLayout.vue (separate layout for login)
   └─ LoginPage.vue
      ├─ BrandingLogo
      ├─ LoginForm
      │  ├─ UsernameInput
      │  ├─ PasswordInput
      │  ├─ RememberMeCheckbox
      │  ├─ ForgotPasswordLink
      │  └─ SignInButton
      └─ FooterInfo
```

---

## Data Flow Architecture

### 1. Authentication Flow

```
┌──────────────┐
│ User enters  │
│ credentials  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ LoginForm.vue                │
│ - Validates input            │
│ - Calls useAuth composable   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ useAuth.ts (Composable)      │
│ - Prepares login request     │
│ - Calls API client           │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ API Client (Axios)           │
│ POST /api/auth/login         │
│ - Sends credentials          │
│ - Receives JWT token         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ auth.ts (Pinia Store)        │
│ - Stores user data           │
│ - Stores JWT token           │
│ - Sets isAuthenticated=true  │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Router Navigation Guard      │
│ - Redirects to HomePage      │
│ - Sets up axios interceptor  │
└──────────────────────────────┘
```

---

### 2. Profile Generation Flow

```
┌──────────────┐
│ User selects │
│ position     │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────┐
│ PositionSearch.vue             │
│ - Emits 'position-selected'    │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ GeneratorPage.vue              │
│ - Catches event                │
│ - Updates selectedPosition     │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ User clicks "Generate"         │
│ GenerationControls.vue         │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ useGenerator.ts (Composable)   │
│ - Prepares request payload     │
│ - Calls startGeneration()      │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ API Client                     │
│ POST /api/generation/start     │
│ - Returns task_id              │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ generator.ts (Pinia Store)     │
│ - Adds task to activeTasks[]   │
│ - Starts polling task status   │
└──────────┬─────────────────────┘
           │
           ▼ (every 3 seconds)
┌────────────────────────────────┐
│ API Client                     │
│ GET /api/generation/:id/status │
│ - Returns progress (0-100%)    │
│ - Returns current_step         │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ ProgressTracker.vue            │
│ - Updates progress bar         │
│ - Shows current step           │
│ - Updates time estimate        │
└──────────┬─────────────────────┘
           │
           ▼ (when status=completed)
┌────────────────────────────────┐
│ API Client                     │
│ GET /api/generation/:id/result │
│ - Returns full profile JSON    │
└──────────┬─────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ ProfilePreview.vue             │
│ - Displays generated profile   │
│ - Shows export options         │
└────────────────────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ el-notification                │
│ "Profile generated successfully!"
└────────────────────────────────┘
```

---

### 3. Profile Search & Filter Flow

```
┌──────────────┐
│ User types   │
│ in search    │
└──────┬───────┘
       │ (debounced 300ms)
       ▼
┌──────────────────────────────┐
│ PositionSearch.vue           │
│ - Captures input             │
│ - Calls useSearch composable │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ useSearch.ts (Composable)    │
│ - Gets positions from store  │
│ - Applies fuzzy matching     │
│ - Ranks results              │
│ - Returns top 10             │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ organization.ts (Pinia Store)│
│ - state: { positions[] }     │
│ - Cached from initial load   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ el-autocomplete              │
│ - Displays ranked results    │
│ - Shows position + hierarchy │
│ - Highlights matched text    │
└──────────────────────────────┘
```

---

## State Management (Pinia Stores)

### Store Structure

```
stores/
│
├─ auth.ts
│  state: {
│    user: User | null
│    token: string | null
│    isAuthenticated: boolean
│  }
│  actions: {
│    login(username, password)
│    logout()
│    refreshToken()
│  }
│  getters: {
│    currentUser: User
│    isAdmin: boolean
│  }
│
├─ profiles.ts
│  state: {
│    profiles: Profile[]
│    currentProfile: Profile | null
│    filters: {
│      department: string
│      position: string
│      dateRange: [Date, Date]
│      status: string
│    }
│    pagination: {
│      page: number
│      limit: number
│      total: number
│    }
│  }
│  actions: {
│    fetchProfiles(filters)
│    fetchProfileById(id)
│    createProfile(data)
│    updateProfile(id, data)
│    deleteProfile(id)
│    archiveProfile(id)
│  }
│  getters: {
│    filteredProfiles: Profile[]
│    profileById(id): Profile
│    totalPages: number
│  }
│
├─ generator.ts
│  state: {
│    activeTasks: Task[]
│    selectedPosition: Position | null
│    generationQueue: QueueItem[]
│    generationMode: 'single' | 'bulk'
│  }
│  actions: {
│    startGeneration(params)
│    cancelTask(taskId)
│    monitorProgress(taskId)
│    addToQueue(positions)
│    processQueue()
│  }
│  getters: {
│    activeTasksCount: number
│    completedTasks: Task[]
│    isGenerating: boolean
│  }
│
├─ organization.ts
│  state: {
│    departments: Department[]
│    positions: Position[]
│    hierarchy: OrgNode[]
│    searchableItems: SearchItem[]
│  }
│  actions: {
│    fetchOrganization()
│    searchPositions(query)
│    getBusinessUnit(path)
│  }
│  getters: {
│    departmentTree: TreeNode[]
│    positionsByDepartment(dept): Position[]
│    totalPositions: number (1689)
│    totalBusinessUnits: number (567)
│  }
│
└─ ui.ts
   state: {
     sidebarCollapsed: boolean
     theme: 'light' | 'dark' | 'auto'
     notifications: Notification[]
     loading: boolean
   }
   actions: {
     toggleSidebar()
     setTheme(theme)
     addNotification(message, type)
     clearNotifications()
     setLoading(state)
   }
   getters: {
     currentTheme: string
     unreadNotifications: number
   }
```

---

## Composables (Reusable Logic)

### useAuth.ts

```typescript
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()

  const login = async (username: string, password: string) => {
    try {
      const response = await apiClient.post('/api/auth/login', {
        username,
        password
      })

      const { access_token, user } = response.data

      authStore.setUser(user)
      authStore.setToken(access_token)

      router.push('/')

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const logout = () => {
    authStore.clearAuth()
    router.push('/login')
  }

  return {
    login,
    logout,
    isAuthenticated: computed(() => authStore.isAuthenticated),
    currentUser: computed(() => authStore.user)
  }
}
```

---

### useGenerator.ts

```typescript
export function useGenerator() {
  const generatorStore = useGeneratorStore()

  const startGeneration = async (params: GenerationParams) => {
    try {
      const response = await apiClient.post('/api/generation/start', params)
      const { task_id, estimated_duration } = response.data

      // Add task to store
      generatorStore.addTask({
        id: task_id,
        status: 'queued',
        progress: 0,
        estimatedDuration: estimated_duration,
        ...params
      })

      // Start monitoring
      monitorProgress(task_id)

      return { success: true, task_id }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  const monitorProgress = (taskId: string) => {
    const interval = setInterval(async () => {
      const status = await fetchTaskStatus(taskId)

      generatorStore.updateTaskProgress(taskId, status)

      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(interval)

        if (status.status === 'completed') {
          const result = await fetchTaskResult(taskId)
          ElNotification.success({
            title: 'Generation Complete',
            message: `Profile for ${status.position} generated successfully`
          })
        }
      }
    }, 3000) // Poll every 3 seconds
  }

  return {
    startGeneration,
    cancelTask: generatorStore.cancelTask,
    activeTasks: computed(() => generatorStore.activeTasks)
  }
}
```

---

### useSearch.ts

```typescript
import Fuse from 'fuse.js'

export function useSearch() {
  const orgStore = useOrganizationStore()

  // Fuzzy search configuration
  const fuse = new Fuse(orgStore.searchableItems, {
    keys: [
      { name: 'display_name', weight: 2 },
      { name: 'full_path', weight: 1 }
    ],
    threshold: 0.3,
    includeScore: true
  })

  const search = (query: string) => {
    if (!query || query.length < 2) return []

    const results = fuse.search(query)
    return results.slice(0, 10).map(r => r.item)
  }

  const filterByDepartment = (department: string) => {
    return orgStore.searchableItems.filter(item =>
      item.full_path.includes(department)
    )
  }

  return {
    search,
    filterByDepartment,
    searchableItems: computed(() => orgStore.searchableItems)
  }
}
```

---

## API Client Configuration

```typescript
// services/api-client.ts

import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { ElNotification } from 'element-plus'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()

    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      authStore.clearAuth()
      router.push('/login')
      ElNotification.error({
        title: 'Session Expired',
        message: 'Please log in again'
      })
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      ElNotification.error({
        title: 'Access Denied',
        message: 'You do not have permission for this action'
      })
    }

    // Handle 500 Server Error
    if (error.response?.status >= 500) {
      ElNotification.error({
        title: 'Server Error',
        message: 'Something went wrong. Please try again later.'
      })
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

---

## Routing Configuration

```typescript
// router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/generator',
    name: 'Generator',
    component: () => import('@/views/GeneratorPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profiles',
    name: 'Profiles',
    component: () => import('@/views/ProfilesPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profiles/:id',
    name: 'ProfileDetail',
    component: () => import('@/views/ProfileDetailPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@/views/AnalyticsPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsPage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
```

---

## Performance Optimizations

### 1. Code Splitting (Lazy Loading)

```typescript
// Lazy load page components
const HomePage = () => import('@/views/HomePage.vue')
const GeneratorPage = () => import('@/views/GeneratorPage.vue')

// Lazy load heavy libraries
const ChartJS = () => import('chart.js')
```

### 2. Virtual Scrolling (Large Lists)

```vue
<template>
  <el-table-v2
    :columns="columns"
    :data="positions"
    :width="700"
    :height="600"
    fixed
  />
</template>
```

### 3. Debounced Search

```typescript
import { useDebounceFn } from '@vueuse/core'

const debouncedSearch = useDebounceFn((query: string) => {
  performSearch(query)
}, 300) // Wait 300ms after user stops typing
```

### 4. Memoization (Computed Properties)

```typescript
const filteredProfiles = computed(() => {
  return profiles.value.filter(p =>
    p.department.includes(filters.department) &&
    p.status === filters.status
  )
})
```

---

## Accessibility Features

### 1. Semantic HTML

```vue
<template>
  <header role="banner">
    <nav role="navigation" aria-label="Main navigation">
      <ul>
        <li><RouterLink to="/">Home</RouterLink></li>
      </ul>
    </nav>
  </header>

  <main role="main">
    <h1>Profile Generator</h1>
  </main>

  <footer role="contentinfo">
    © 2025 A101
  </footer>
</template>
```

### 2. ARIA Labels

```vue
<el-button
  icon="Download"
  circle
  aria-label="Export profile as DOCX"
/>

<el-progress
  :percentage="progress"
  :status="status"
  role="progressbar"
  :aria-valuenow="progress"
  aria-valuemin="0"
  aria-valuemax="100"
/>
```

### 3. Keyboard Navigation

```typescript
const handleKeyPress = (event: KeyboardEvent) => {
  // Ctrl+K to focus search
  if (event.ctrlKey && event.key === 'k') {
    event.preventDefault()
    searchInput.value?.focus()
  }

  // Esc to close modal
  if (event.key === 'Escape') {
    closeModal()
  }
}
```

---

## Conclusion

This component architecture provides:

✅ **Clear Hierarchy:** Easy to understand component relationships
✅ **Separation of Concerns:** Logic in composables, state in stores, UI in components
✅ **Reusability:** Shared components and composables across pages
✅ **Performance:** Lazy loading, virtual scrolling, debouncing
✅ **Maintainability:** TypeScript, consistent patterns, clear data flow
✅ **Scalability:** Modular design supports future growth

**Next Steps:**
1. Set up project structure following this architecture
2. Implement authentication first (base for all features)
3. Build components incrementally (starting with shared UI components)
4. Test each component in isolation (Vitest unit tests)
5. Integrate components into pages (E2E tests with Playwright)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-25
**Related Documents:**
- [VUE_MIGRATION_UX_UI_SPECIFICATION.md](./VUE_MIGRATION_UX_UI_SPECIFICATION.md)
- [UX_UI_EXECUTIVE_SUMMARY.md](./UX_UI_EXECUTIVE_SUMMARY.md)

# HR Profile Generator - Vue.js Migration UX/UI Specification

**Document Version:** 1.0
**Date:** 2025-10-25
**Author:** UX/UI Design Team
**Status:** Comprehensive Specification for Vue.js Migration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [User Personas](#user-personas)
3. [User Journey Maps](#user-journey-maps)
4. [User Stories with Acceptance Criteria](#user-stories-with-acceptance-criteria)
5. [Information Architecture](#information-architecture)
6. [UI Framework Recommendation](#ui-framework-recommendation)
7. [Component Architecture](#component-architecture)
8. [Wireframe Descriptions](#wireframe-descriptions)
9. [Design System Specifications](#design-system-specifications)
10. [Accessibility Considerations](#accessibility-considerations)
11. [UX Pain Points & Improvements](#ux-pain-points--improvements)
12. [Migration Roadmap](#migration-roadmap)

---

## Executive Summary

The HR Profile Generator is an AI-powered system that generates comprehensive job position profiles for employees across a company with 567 business units and 1,689 positions. The current implementation uses **NiceGUI (Python-based)**, which needs migration to **Vue.js** for better frontend scalability, performance, and maintainability.

### Current System Overview

**Backend:**
- FastAPI (Python 3.11+)
- SQLite database
- OpenRouter LLM integration (Gemini 2.5 Flash)
- JWT authentication
- Async task processing for profile generation

**Frontend (Current):**
- NiceGUI (Python-based web framework)
- Material Design components
- Real-time updates via server-side rendering

**Key Features:**
- Intelligent position search across 1,689 positions
- AI-powered profile generation (30-60 seconds per profile)
- Multiple export formats (JSON, DOCX, Markdown)
- Async task tracking with progress indicators
- Profile versioning and history
- Organization structure visualization

---

## User Personas

### Persona 1: Elena - HR Manager (Primary User)

**Demographics:**
- Age: 32
- Role: HR Business Partner
- Experience: 5 years in HR
- Tech savvy: Medium

**Goals:**
- Generate accurate job profiles quickly (target: <2 minutes total time)
- Review and edit AI-generated content before approval
- Export profiles in corporate-standard formats
- Track profile generation history for compliance

**Pain Points:**
- Current system requires too many clicks to find a position
- Unclear progress indication during AI generation
- Difficulty comparing multiple versions of profiles
- No bulk operations for similar positions

**Behavior:**
- Uses system 5-10 times per week
- Typically generates 3-5 profiles per session
- Prefers keyboard shortcuts for speed
- Needs to work across departments (CRM, IT, Sales, etc.)

**Quote:**
*"I need to quickly find positions, generate profiles with AI help, and export them without unnecessary friction. Time is critical when onboarding new employees."*

---

### Persona 2: Dmitry - Department Head (Secondary User)

**Demographics:**
- Age: 45
- Role: IT Department Director
- Experience: 15 years in IT management
- Tech savvy: High

**Goals:**
- Review job profiles for technical accuracy
- Ensure KPIs align with department objectives
- Approve profiles before HR finalizes them
- Access organizational hierarchy context

**Pain Points:**
- Limited ability to filter by department/subdepartment
- KPI sections sometimes lack department-specific metrics
- No way to mark profiles for revision
- Wants to see career paths and position hierarchies

**Behavior:**
- Uses system 1-2 times per month
- Reviews profiles in batches (10-20 at once)
- Focuses on technical skills and responsibilities sections
- Needs organizational context (reporting structure, peers)

**Quote:**
*"I need to verify that AI-generated profiles reflect the actual technical requirements and career progression in my department."*

---

### Persona 3: Anna - System Administrator (Technical User)

**Demographics:**
- Age: 28
- Role: IT Administrator
- Experience: 3 years in system administration
- Tech savvy: Very High

**Goals:**
- Monitor system health and performance
- Troubleshoot generation failures
- Manage user access and permissions
- View system logs and analytics

**Pain Points:**
- No admin dashboard with system metrics
- Limited visibility into LLM token usage and costs
- Can't easily see failed generations for debugging
- No way to manually retry failed tasks

**Behavior:**
- Uses system daily for monitoring
- Needs real-time alerts for errors
- Reviews logs weekly for optimization
- Expects detailed technical metrics

**Quote:**
*"I need comprehensive system visibility - from LLM performance to database health - to ensure smooth operation for HR users."*

---

## User Journey Maps

### Journey 1: First-Time User Onboarding (Elena - HR Manager)

**Goal:** Generate first employee profile successfully

| Stage | User Action | Touchpoint | Thoughts/Feelings | Pain Points | Opportunities |
|-------|-------------|------------|-------------------|-------------|---------------|
| **1. Discovery** | Opens application URL | Login page | "Is this the right system?" Uncertain | No onboarding tutorial visible | Add welcome banner with quick guide |
| **2. Authentication** | Enters credentials | Login form | "Standard login, familiar" Neutral | None | Consider SSO integration |
| **3. First Impression** | Sees dashboard | Home page | "Where do I start?" Confused | Too many options, unclear hierarchy | Add "Get Started" wizard overlay |
| **4. Position Search** | Types position name | Search input | "Will it find the right position?" Anxious | 1,689 positions intimidating | Smart autocomplete with context |
| **5. Department Selection** | Chooses from dropdown | Department selector | "Which department is correct?" Uncertain | Duplicate department names confusing | Show full hierarchy path |
| **6. Profile Generation** | Clicks "Generate" | Generator section | "How long will this take?" Impatient | No time estimate shown initially | Show estimated time (45s) upfront |
| **7. Waiting** | Watches progress bar | Progress indicator | "Is it working?" Anxious | Progress updates too generic | Add step-by-step progress descriptions |
| **8. Review** | Reads generated profile | Profile viewer | "This looks good!" Pleased | Some sections collapsed by default | Expand key sections automatically |
| **9. Download** | Exports to DOCX | Files manager | "How do I save this?" Neutral | Download button location unclear | Prominent "Export" button in profile header |
| **10. Completion** | Returns to dashboard | Navigation | "What's next?" Satisfied | No confirmation of success | Show success message with next steps |

**Key Insights:**
- Critical friction point: Position search (Stage 4-5)
- Anxiety peak: Waiting for generation (Stage 6-7)
- Success metric: Time from login to first downloaded profile (<3 minutes ideal)

---

### Journey 2: Bulk Profile Generation (Elena - HR Manager)

**Goal:** Generate profiles for entire department (10+ positions)

| Stage | User Action | Touchpoint | Thoughts/Feelings | Pain Points | Opportunities |
|-------|-------------|------------|-------------------|-------------|---------------|
| **1. Planning** | Opens Excel with position list | External tool | "I need 15 profiles by EOD" Stressed | Must generate one by one | **Add bulk upload feature** |
| **2. First Profile** | Searches and generates position #1 | Search + Generator | "One down, 14 to go..." Tedious | No queue system | **Add generation queue** |
| **3. Monitoring** | Checks progress on position #1 | Progress tracker | "Can I start the next one?" Uncertain | Must wait for completion | **Allow parallel generations** |
| **4. Repeat** | Repeats process 14 more times | Full app | "This is taking too long" Frustrated | No batch operations | **CRITICAL: Add bulk mode** |
| **5. Export All** | Downloads 15 files individually | Files manager | "Can't I zip these?" Annoyed | Manual download each file | **Add bulk export (ZIP)** |
| **6. Organization** | Organizes files in folders | File system | "Finally done..." Exhausted | No folder structure in downloads | Auto-organize by department |

**Key Insights:**
- **CRITICAL PAIN POINT:** No bulk operations
- Recommended Feature: Bulk upload (CSV/Excel) + Batch processing
- Success metric: Generate 15 profiles in <15 minutes (1 min/profile including review)

---

### Journey 3: Profile Review & Editing (Dmitry - Department Head)

**Goal:** Review and approve 20 IT department profiles

| Stage | User Action | Touchpoint | Thoughts/Feelings | Pain Points | Opportunities |
|-------|-------------|------------|-------------------|-------------|---------------|
| **1. Access** | Receives review link from HR | Email | "Let me check these profiles" Curious | No direct link to review queue | Add review workflow system |
| **2. Filter** | Searches for IT department profiles | Profiles list | "Need to see only my department" Focused | No department filter | **Add advanced filters** |
| **3. Batch View** | Opens multiple profiles in tabs | Browser tabs | "Hard to compare" Frustrated | No multi-profile view | **Add comparison mode** |
| **4. Technical Review** | Checks skills and KPIs | Profile sections | "Some KPIs are generic" Concerned | KPIs not department-specific enough | Enhance KPI filtering logic |
| **5. Feedback** | Wants to comment | External email | "No way to leave notes?" Annoyed | No inline commenting | **Add comment/annotation system** |
| **6. Approval** | No approval mechanism | Manual process | "How do I approve this?" Confused | No workflow state management | **Add approval workflow** |

**Key Insights:**
- Need review-specific UI mode
- Approval workflow missing entirely
- Comparison feature critical for consistency

---

## User Stories with Acceptance Criteria

### Category: Authentication & Authorization

#### US-001: User Login
**As a** HR manager
**I want to** log in securely with my credentials
**So that** I can access the profile generation system

**Acceptance Criteria:**
- [ ] Login form displays username and password fields
- [ ] JWT token generated upon successful authentication
- [ ] Token stored securely (httpOnly cookie or encrypted localStorage)
- [ ] Invalid credentials show clear error message
- [ ] "Remember me" option extends session to 30 days
- [ ] Redirect to previous page after login (or dashboard if direct access)
- [ ] Login attempts rate-limited (5 attempts per 15 minutes)

**Priority:** P0 (Critical)
**Estimated Effort:** 3 story points

---

#### US-002: Session Management
**As a** system user
**I want to** stay logged in during active use
**So that** I don't have to re-authenticate frequently

**Acceptance Criteria:**
- [ ] Session expires after 8 hours of inactivity
- [ ] Active use extends session automatically
- [ ] "Session expiring" warning shown 5 minutes before timeout
- [ ] Expired session redirects to login with "Session expired" message
- [ ] User can manually logout from any page
- [ ] Logout clears all local storage and tokens

**Priority:** P0 (Critical)
**Estimated Effort:** 2 story points

---

### Category: Position Search & Discovery

#### US-003: Intelligent Position Search
**As a** HR manager
**I want to** search for positions using natural language
**So that** I can quickly find the right job title among 1,689 positions

**Acceptance Criteria:**
- [ ] Search autocomplete starts after 2 characters typed
- [ ] Results show within 300ms of typing
- [ ] Display top 10 most relevant results
- [ ] Show full hierarchy path: "Block / Department / Unit / Group"
- [ ] Highlight matching text in results
- [ ] Support fuzzy matching (typo tolerance)
- [ ] Filter results by department (optional dropdown)
- [ ] Show position count badge for each department
- [ ] Keyboard navigation (Arrow keys + Enter)
- [ ] Clear search button ("X" icon)

**Priority:** P0 (Critical)
**Estimated Effort:** 5 story points

---

#### US-004: Department Hierarchy Display
**As a** HR manager
**I want to** see the full organizational hierarchy for a position
**So that** I understand where it fits in the company structure

**Acceptance Criteria:**
- [ ] Display hierarchy as: Block → Department → Unit → Group
- [ ] Show "breadcrumb" navigation in search results
- [ ] Clicking breadcrumb level filters to that level
- [ ] Tooltip shows full path on hover
- [ ] Color-code hierarchy levels (Block=blue, Department=green, etc.)
- [ ] Show sibling positions at same level (optional)

**Priority:** P1 (High)
**Estimated Effort:** 3 story points

---

### Category: Profile Generation

#### US-005: Single Profile Generation
**As a** HR manager
**I want to** generate a comprehensive job profile using AI
**So that** I have a structured document for hiring and onboarding

**Acceptance Criteria:**
- [ ] "Generate Profile" button visible after position selected
- [ ] Show estimated time (45 seconds) before generation starts
- [ ] Display progress bar with current step description
- [ ] Progress updates every 5 seconds:
  - "Initializing..." (0-10%)
  - "Analyzing organization structure..." (10-30%)
  - "Generating profile with AI..." (30-90%)
  - "Finalizing and saving..." (90-100%)
- [ ] Allow cancellation during generation
- [ ] Show completion notification
- [ ] Auto-display generated profile on completion
- [ ] Error handling with retry option
- [ ] Track generation in background tasks list

**Priority:** P0 (Critical)
**Estimated Effort:** 8 story points

---

#### US-006: Bulk Profile Generation
**As a** HR manager
**I want to** generate profiles for multiple positions at once
**So that** I can efficiently process department-wide updates

**Acceptance Criteria:**
- [ ] "Bulk Mode" toggle in generator section
- [ ] CSV/Excel template download for bulk input
- [ ] File upload with validation (max 50 positions)
- [ ] Preview uploaded positions before generation
- [ ] Queue all positions for generation
- [ ] Show queue status dashboard (pending/processing/completed/failed)
- [ ] Generate profiles in parallel (max 3 concurrent)
- [ ] Allow pause/resume of queue
- [ ] Export all completed profiles as ZIP
- [ ] Email notification when bulk generation completes

**Priority:** P1 (High)
**Estimated Effort:** 13 story points

---

#### US-007: Generation Progress Tracking
**As a** HR manager
**I want to** see detailed progress of active profile generations
**So that** I know when profiles will be ready

**Acceptance Criteria:**
- [ ] "Active Tasks" panel shows all ongoing generations
- [ ] Each task displays:
  - Position name and department
  - Progress percentage (0-100%)
  - Current step description
  - Estimated time remaining
  - Start time and duration so far
- [ ] Visual distinction for different states (pending/processing/completed/failed)
- [ ] Ability to cancel individual tasks
- [ ] Auto-refresh every 3 seconds
- [ ] Notification when task completes

**Priority:** P1 (High)
**Estimated Effort:** 5 story points

---

### Category: Profile Viewing & Review

#### US-008: Profile Viewer
**As a** HR manager
**I want to** view generated profiles in a structured, readable format
**So that** I can review and validate the content

**Acceptance Criteria:**
- [ ] Display profile in tabbed interface:
  - Tab 1: Overview (position info, summary)
  - Tab 2: Responsibilities
  - Tab 3: Qualifications & Skills
  - Tab 4: KPIs
  - Tab 5: Organizational Context
  - Tab 6: Metadata (generation info, tokens used)
- [ ] All sections expandable/collapsible
- [ ] Key sections (Responsibilities, Skills) expanded by default
- [ ] Print-friendly formatting
- [ ] Copy-to-clipboard for individual sections
- [ ] Fullscreen mode for focused reading
- [ ] Navigation between profile sections (sticky tabs)

**Priority:** P0 (Critical)
**Estimated Effort:** 5 story points

---

#### US-009: Profile Comparison
**As a** department head
**I want to** compare multiple profiles side-by-side
**So that** I can ensure consistency across similar positions

**Acceptance Criteria:**
- [ ] "Compare" mode accessible from profiles list
- [ ] Select 2-4 profiles for comparison
- [ ] Side-by-side column layout
- [ ] Synchronized scrolling
- [ ] Highlight differences in:
  - Responsibilities
  - Required skills
  - KPI targets
  - Experience requirements
- [ ] Export comparison as report (PDF)
- [ ] Filter comparison to specific sections only

**Priority:** P2 (Medium)
**Estimated Effort:** 8 story points

---

#### US-010: Profile Editing
**As a** HR manager
**I want to** edit generated profile content
**So that** I can refine AI output to match company standards

**Acceptance Criteria:**
- [ ] "Edit Mode" button in profile viewer
- [ ] Inline editing for text sections
- [ ] Rich text editor with formatting (bold, lists, tables)
- [ ] Add/remove responsibilities dynamically
- [ ] Edit KPI values and targets
- [ ] Change required skills with autocomplete
- [ ] Save as draft (auto-save every 30 seconds)
- [ ] Version control - save edits as new version
- [ ] "Discard changes" with confirmation
- [ ] Show edit history (who, when, what changed)

**Priority:** P1 (High)
**Estimated Effort:** 13 story points

---

### Category: Export & Download

#### US-011: Profile Export (Single)
**As a** HR manager
**I want to** export profiles in multiple formats
**So that** I can use them in different systems and documents

**Acceptance Criteria:**
- [ ] Export formats available:
  - JSON (structured data)
  - DOCX (Microsoft Word, corporate template)
  - Markdown (developer-friendly)
  - PDF (print-ready)
- [ ] Export button prominent in profile header
- [ ] Format selector dropdown
- [ ] File named: `Profile_{Position}_{Date}_{ID}.{ext}`
- [ ] Download starts immediately (no page reload)
- [ ] Show download progress for large files
- [ ] "Open in new tab" option for JSON/MD
- [ ] Export includes all metadata

**Priority:** P0 (Critical)
**Estimated Effort:** 5 story points

---

#### US-012: Bulk Export
**As a** HR manager
**I want to** export multiple profiles at once
**So that** I can share department profiles with stakeholders

**Acceptance Criteria:**
- [ ] Multi-select profiles from list (checkboxes)
- [ ] "Export Selected" bulk action button
- [ ] Choose format for all (DOCX, PDF, etc.)
- [ ] Package as ZIP archive
- [ ] ZIP file structure:
  - `Department/` folders
  - Files organized by hierarchy
- [ ] Include README.txt with export metadata
- [ ] Max 100 profiles per export
- [ ] Show packaging progress
- [ ] Email download link for large exports (>50MB)

**Priority:** P1 (High)
**Estimated Effort:** 8 story points

---

### Category: Profile Management

#### US-013: Profiles List with Filters
**As a** HR manager
**I want to** view all generated profiles with advanced filtering
**So that** I can quickly find and manage existing profiles

**Acceptance Criteria:**
- [ ] Paginated list (20 profiles per page)
- [ ] Table columns:
  - Position name
  - Department
  - Employee name (if assigned)
  - Created date
  - Created by
  - Status (active/archived)
  - Actions (view/edit/delete)
- [ ] Filters:
  - Department (dropdown with hierarchy)
  - Position (autocomplete search)
  - Date range (created between X and Y)
  - Status (active/archived)
  - Created by (user selector)
- [ ] Sort by any column (ascending/descending)
- [ ] Search across all fields
- [ ] "Clear filters" button
- [ ] Show active filters as tags
- [ ] Export filtered results

**Priority:** P1 (High)
**Estimated Effort:** 8 story points

---

#### US-014: Profile Archiving
**As a** HR manager
**I want to** archive outdated profiles
**So that** I maintain a clean active profiles list

**Acceptance Criteria:**
- [ ] "Archive" button in profile actions menu
- [ ] Confirmation dialog before archiving
- [ ] Archived profiles moved to "Archived" tab
- [ ] Archived profiles excluded from default list view
- [ ] "Restore" button to unarchive
- [ ] Archived profiles show "Archived" badge
- [ ] Filter to show only archived profiles
- [ ] Bulk archive action available
- [ ] Archived profiles still accessible via direct link

**Priority:** P2 (Medium)
**Estimated Effort:** 3 story points

---

#### US-015: Profile Versioning
**As a** department head
**I want to** view version history of a profile
**So that** I can track changes over time

**Acceptance Criteria:**
- [ ] "Versions" tab in profile viewer
- [ ] List all versions with:
  - Version number (v1, v2, v3...)
  - Modified date/time
  - Modified by (user)
  - Change summary (auto-generated or manual)
- [ ] Click version to view that revision
- [ ] Visual diff between versions (highlight changes)
- [ ] Restore previous version (creates new version)
- [ ] Export specific version
- [ ] Delete old versions (admin only)

**Priority:** P2 (Medium)
**Estimated Effort:** 13 story points

---

### Category: Dashboard & Analytics

#### US-016: User Dashboard
**As a** HR manager
**I want to** see an overview dashboard when I log in
**So that** I understand system status and my recent activity

**Acceptance Criteria:**
- [ ] Dashboard cards display:
  - Total profiles generated (all time)
  - Profiles generated this month
  - Active generation tasks
  - Recent profiles (last 5)
  - Most generated departments (top 5)
- [ ] Quick actions:
  - "Generate New Profile" (primary CTA)
  - "View All Profiles"
  - "View Analytics"
- [ ] Notification center:
  - Completed generations
  - Failed tasks (with retry option)
  - System announcements
- [ ] Performance metrics:
  - Average generation time
  - Success rate
  - Token usage this month
- [ ] Responsive layout (mobile-friendly)

**Priority:** P1 (High)
**Estimated Effort:** 8 story points

---

#### US-017: System Analytics
**As a** system administrator
**I want to** view comprehensive system analytics
**So that** I can monitor health and optimize performance

**Acceptance Criteria:**
- [ ] Analytics page with tabs:
  - Tab 1: Usage Metrics
  - Tab 2: Performance
  - Tab 3: LLM Statistics
  - Tab 4: User Activity
- [ ] Charts display:
  - Profiles generated over time (line chart)
  - Profiles by department (bar chart)
  - Generation success rate (donut chart)
  - Average generation time trend (area chart)
  - LLM token usage (stacked area chart)
- [ ] Date range selector (last 7/30/90 days, custom)
- [ ] Export analytics as CSV/Excel
- [ ] Real-time data updates
- [ ] Filtering by user, department, status

**Priority:** P2 (Medium)
**Estimated Effort:** 13 story points

---

### Category: Error Handling & Recovery

#### US-018: Graceful Error Handling
**As a** system user
**I want to** receive clear error messages and recovery options
**So that** I can resolve issues without contacting support

**Acceptance Criteria:**
- [ ] All errors display in consistent format:
  - Error title (user-friendly)
  - Error description (what happened)
  - Suggested action (what to do)
  - Error code (for support reference)
- [ ] Error types handled:
  - Network errors (retry with exponential backoff)
  - Validation errors (highlight problematic fields)
  - LLM errors (show token usage, suggest retry)
  - Permission errors (explain required access level)
  - Server errors (show generic message, log details)
- [ ] "Retry" button for transient errors
- [ ] "Report Issue" button (captures context)
- [ ] Errors logged to analytics
- [ ] No stack traces shown to end users

**Priority:** P0 (Critical)
**Estimated Effort:** 8 story points

---

#### US-019: Offline Fallback
**As a** system user
**I want to** receive feedback when the system is offline
**So that** I know to try again later

**Acceptance Criteria:**
- [ ] Detect offline state (no internet connection)
- [ ] Show offline banner: "No internet connection detected"
- [ ] Disable actions requiring network (generate, save, export)
- [ ] Cache recent data for offline viewing
- [ ] Auto-retry connection every 10 seconds
- [ ] Show "Back online" notification when reconnected
- [ ] Queue failed requests for retry on reconnection
- [ ] Service worker for basic offline functionality

**Priority:** P2 (Medium)
**Estimated Effort:** 8 story points

---

## Information Architecture

### Site Map

```
HR Profile Generator (Vue.js)
│
├── 🏠 Home Dashboard
│   ├── Quick Stats Cards
│   ├── Recent Activity Feed
│   ├── Quick Actions Panel
│   └── Notifications Center
│
├── 🔍 Generator (Main Feature)
│   ├── Position Search
│   │   ├── Autocomplete Dropdown
│   │   ├── Department Filter
│   │   └── Hierarchy Breadcrumbs
│   │
│   ├── Generation Controls
│   │   ├── Single Mode
│   │   ├── Bulk Mode (CSV Upload)
│   │   └── Advanced Settings (Temperature, Employee Name)
│   │
│   ├── Progress Tracking
│   │   ├── Active Tasks List
│   │   ├── Task Details (Progress, Time, Status)
│   │   └── Task Actions (Cancel, Retry)
│   │
│   └── Profile Preview
│       ├── Live Preview Panel
│       └── Quick Export Button
│
├── 📋 Profiles Library
│   ├── List View
│   │   ├── Data Table (Sortable, Filterable)
│   │   ├── Pagination Controls
│   │   └── Bulk Actions Toolbar
│   │
│   ├── Filters Panel
│   │   ├── Department Selector
│   │   ├── Date Range Picker
│   │   ├── Status Filter
│   │   └── Search Box
│   │
│   └── Profile Detail View
│       ├── Tabbed Interface
│       │   ├── Overview Tab
│       │   ├── Responsibilities Tab
│       │   ├── Qualifications Tab
│       │   ├── KPIs Tab
│       │   ├── Context Tab
│       │   └── Metadata Tab
│       │
│       ├── Actions Toolbar
│       │   ├── Edit Button
│       │   ├── Export Dropdown
│       │   ├── Archive/Delete
│       │   └── Share Link
│       │
│       └── Versions Panel
│           ├── Version List
│           ├── Version Diff
│           └── Restore Version
│
├── 📊 Analytics Dashboard
│   ├── Usage Metrics
│   │   ├── Total Profiles Chart
│   │   ├── Growth Trend Line
│   │   └── Department Distribution
│   │
│   ├── Performance Metrics
│   │   ├── Average Generation Time
│   │   ├── Success Rate
│   │   └── Error Analysis
│   │
│   ├── LLM Statistics
│   │   ├── Token Usage Chart
│   │   ├── Cost Tracking
│   │   └── Model Performance
│   │
│   └── User Activity
│       ├── Active Users
│       ├── Top Generators
│       └── Usage Patterns
│
├── 🔧 Settings
│   ├── Profile Settings
│   │   ├── Display Preferences
│   │   ├── Default Filters
│   │   └── Notification Preferences
│   │
│   ├── Account Settings
│   │   ├── Change Password
│   │   ├── Session Management
│   │   └── API Keys
│   │
│   └── Admin Settings (Admin Only)
│       ├── User Management
│       ├── System Configuration
│       └── Data Management
│
└── ❓ Help & Support
    ├── Quick Start Guide
    ├── Video Tutorials
    ├── FAQ
    ├── Keyboard Shortcuts
    └── Contact Support
```

---

### Navigation Structure

**Primary Navigation (Top Header):**
1. 🏠 Home
2. 🔍 Generator (highlighted as primary action)
3. 📋 Profiles
4. 📊 Analytics
5. Settings (user menu dropdown)
6. Help (icon button)

**Secondary Navigation (Contextual):**
- Breadcrumbs for deep pages
- Back button for profile details
- Tab navigation within sections

**Mobile Navigation:**
- Hamburger menu (collapsed)
- Bottom navigation bar for primary actions
- Swipe gestures for tabs

---

## UI Framework Recommendation

### Recommended: **Element Plus** (for Vue 3)

**Justification:**

1. **Enterprise-Ready Components** ✅
   - Comprehensive component library (60+ components)
   - Data table with advanced filtering, sorting, pagination
   - Form validation with async rules
   - Upload component for bulk CSV/Excel
   - Progress indicators with customizable steps

2. **Design Quality** ✅
   - Professional, clean aesthetic
   - Consistent with enterprise applications
   - Customizable theme system (matches A101 branding)
   - Well-documented design tokens

3. **Vue 3 Compatibility** ✅
   - Built specifically for Vue 3 Composition API
   - TypeScript support out-of-the-box
   - Excellent tree-shaking (reduces bundle size)
   - Active development and community

4. **Performance** ✅
   - Virtual scrolling for large lists (1,689 positions)
   - Lazy loading components
   - Optimized for large data tables
   - SSR support (future-proofing)

5. **Developer Experience** ✅
   - Excellent documentation (English + Chinese)
   - Large community (Element UI legacy)
   - Volar support for IDE autocomplete
   - Playground for testing components

6. **Specific Features for Our Use Case:**
   - **Autocomplete component** - Perfect for position search
   - **Table component** - Handles profiles list with filters
   - **Upload component** - Bulk CSV upload
   - **Progress component** - Generation tracking
   - **Tabs component** - Profile viewer tabs
   - **Tree component** - Organization hierarchy
   - **Notification system** - Task completion alerts

**Alternative Considered:**

- **Vuetify** - Too Material Design heavy, larger bundle size
- **Ant Design Vue** - Good but less intuitive API
- **Quasar** - Too opinionated, includes build tooling we don't need
- **PrimeVue** - Good alternative but smaller community

**Final Recommendation: Element Plus**

---

## Component Architecture

### Vue Component Hierarchy

```
App.vue
│
├── Layouts/
│   ├── MainLayout.vue
│   │   ├── AppHeader.vue
│   │   ├── AppSidebar.vue (optional, for mobile)
│   │   ├── <router-view />
│   │   └── AppFooter.vue
│   │
│   └── AuthLayout.vue
│       ├── LoginForm.vue
│       └── BrandingLogo.vue
│
├── Views (Pages)/
│   ├── HomePage.vue
│   │   ├── StatsCards.vue
│   │   ├── QuickActions.vue
│   │   ├── RecentActivity.vue
│   │   └── NotificationsPanel.vue
│   │
│   ├── GeneratorPage.vue
│   │   ├── PositionSearch.vue
│   │   │   ├── SearchInput.vue (Element Plus Autocomplete)
│   │   │   ├── DepartmentFilter.vue (Element Plus Select)
│   │   │   └── HierarchyBreadcrumb.vue (Element Plus Breadcrumb)
│   │   │
│   │   ├── GenerationControls.vue
│   │   │   ├── SingleModeForm.vue
│   │   │   ├── BulkModeUpload.vue (Element Plus Upload)
│   │   │   └── AdvancedSettings.vue (Element Plus Collapse)
│   │   │
│   │   ├── ProgressTracker.vue
│   │   │   ├── ActiveTasksList.vue
│   │   │   ├── TaskCard.vue (Element Plus Card)
│   │   │   └── ProgressBar.vue (Element Plus Progress)
│   │   │
│   │   └── ProfilePreview.vue
│   │       ├── ProfileTabs.vue (Element Plus Tabs)
│   │       └── ExportButton.vue (Element Plus Dropdown)
│   │
│   ├── ProfilesPage.vue
│   │   ├── ProfilesListView.vue
│   │   │   ├── DataTable.vue (Element Plus Table)
│   │   │   ├── PaginationBar.vue (Element Plus Pagination)
│   │   │   └── BulkActionsToolbar.vue
│   │   │
│   │   ├── FiltersPanel.vue
│   │   │   ├── DepartmentSelector.vue (Element Plus TreeSelect)
│   │   │   ├── DateRangePicker.vue (Element Plus DatePicker)
│   │   │   └── StatusFilter.vue (Element Plus CheckboxGroup)
│   │   │
│   │   └── ProfileDetailView.vue
│   │       ├── ProfileHeader.vue
│   │       ├── ProfileTabs.vue
│   │       │   ├── OverviewTab.vue
│   │       │   ├── ResponsibilitiesTab.vue
│   │       │   ├── QualificationsTab.vue
│   │       │   ├── KPIsTab.vue
│   │       │   ├── ContextTab.vue
│   │       │   └── MetadataTab.vue
│   │       │
│   │       ├── ActionsToolbar.vue
│   │       └── VersionsPanel.vue (Element Plus Timeline)
│   │
│   ├── AnalyticsPage.vue
│   │   ├── UsageMetrics.vue (Chart.js integration)
│   │   ├── PerformanceMetrics.vue
│   │   ├── LLMStatistics.vue
│   │   └── UserActivity.vue
│   │
│   └── SettingsPage.vue
│       ├── ProfileSettings.vue
│       ├── AccountSettings.vue
│       └── AdminSettings.vue (v-if="isAdmin")
│
├── Components (Shared)/
│   ├── UI/
│   │   ├── LoadingSpinner.vue
│   │   ├── ErrorMessage.vue
│   │   ├── SuccessNotification.vue
│   │   ├── ConfirmDialog.vue
│   │   └── EmptyState.vue
│   │
│   ├── Profile/
│   │   ├── ProfileCard.vue
│   │   ├── ProfileBadge.vue
│   │   ├── ProfileActions.vue
│   │   └── ProfileComparison.vue
│   │
│   └── Forms/
│       ├── FormInput.vue
│       ├── FormSelect.vue
│       ├── FormDatePicker.vue
│       └── FormValidation.vue
│
└── Composables (Vue 3 Composition API)/
    ├── useAuth.ts (authentication logic)
    ├── useProfiles.ts (profile CRUD operations)
    ├── useGenerator.ts (generation task management)
    ├── useSearch.ts (position search logic)
    ├── useExport.ts (export/download logic)
    └── useNotifications.ts (toast notifications)
```

---

### State Management (Pinia Stores)

```
stores/
│
├── auth.ts
│   ├── state: { user, token, isAuthenticated }
│   ├── actions: login(), logout(), refreshToken()
│   └── getters: currentUser, isAdmin
│
├── profiles.ts
│   ├── state: { profiles, currentProfile, filters, pagination }
│   ├── actions: fetchProfiles(), createProfile(), updateProfile(), deleteProfile()
│   └── getters: filteredProfiles, profileById
│
├── generator.ts
│   ├── state: { activeTasks, selectedPosition, generationQueue }
│   ├── actions: startGeneration(), cancelTask(), monitorProgress()
│   └── getters: activeTasksCount, completedTasks
│
├── organization.ts
│   ├── state: { departments, positions, hierarchy }
│   ├── actions: fetchOrganization(), searchPositions()
│   └── getters: departmentTree, positionsByDepartment
│
└── ui.ts
    ├── state: { sidebarCollapsed, theme, notifications }
    ├── actions: toggleSidebar(), setTheme(), addNotification()
    └── getters: currentTheme, unreadNotifications
```

---

## Wireframe Descriptions

### 1. Login Page

**Layout:** Centered card on full-height background

**Elements:**
- Company logo (top center)
- "HR Profile Generator" title
- Login form:
  - Username input (icon: user)
  - Password input (icon: lock, toggle visibility)
  - "Remember me" checkbox
  - "Forgot password?" link
- Primary button: "Sign In"
- Footer: Version info, support link

**Interactions:**
- Enter key submits form
- Loading state on button during authentication
- Error message appears below form
- Success: redirect to dashboard

---

### 2. Home Dashboard

**Layout:** Grid layout (3 columns on desktop, 1 on mobile)

**Header:**
- App title
- Navigation menu (Home, Generator, Profiles, Analytics)
- User dropdown (Profile, Settings, Logout)
- Notifications bell (badge count)

**Content:**
1. **Welcome Banner** (full width, dismissible)
   - "Welcome back, Elena!"
   - Quick tip or announcement

2. **Stats Cards Row** (3 cards)
   - Card 1: Total Profiles Generated (number + trend)
   - Card 2: Profiles This Month (number + comparison)
   - Card 3: Active Tasks (number + link to view)

3. **Quick Actions Panel** (left column, 2/3 width)
   - Large button: "🔍 Generate New Profile" (primary CTA)
   - Secondary buttons: "View All Profiles", "View Analytics"

4. **Recent Activity Feed** (right column, 1/3 width)
   - Timeline of last 10 actions
   - Each item: icon, description, timestamp
   - "View all" link at bottom

5. **Department Statistics** (full width chart)
   - Bar chart: Profiles by department
   - Clickable bars to filter profiles list

---

### 3. Generator Page (Main Feature)

**Layout:** Two-panel layout (60% left, 40% right)

**Left Panel: Search & Generation**

1. **Position Search Section**
   - Large search input (placeholder: "Search for position or department...")
   - Autocomplete dropdown:
     - Show position name (bold)
     - Department path (gray text below)
     - Position count badge
   - Department filter dropdown (optional)
   - "Clear" button

2. **Selected Position Card** (appears after selection)
   - Position name (H3)
   - Full hierarchy breadcrumb
   - Department info
   - Number of existing profiles for this position
   - "Change position" link

3. **Generation Form**
   - Employee name input (optional)
   - Temperature slider (0.0 - 1.0, default 0.1)
   - "Advanced settings" collapse panel:
     - Save result checkbox
     - Custom instructions textarea
   - Primary button: "🚀 Generate Profile" (estimated time below)

4. **Active Tasks Panel** (appears during generation)
   - Each task card shows:
     - Position name
     - Progress bar (0-100%)
     - Current step description
     - Elapsed time / estimated remaining
     - Cancel button (icon)

**Right Panel: Preview**
- Live preview of generated profile
- Tabs: Overview, Responsibilities, Skills, KPIs
- Export button (always visible)

---

### 4. Profiles List Page

**Layout:** Full-width data table with sidebar filters

**Left Sidebar Filters** (collapsible)
- Department selector (tree structure)
- Position search
- Date range picker
- Status checkboxes (Active, Archived)
- Created by user dropdown
- "Apply Filters" button
- "Clear All" link

**Main Content: Data Table**
- Columns:
  1. Checkbox (bulk select)
  2. Position Name (sortable, link to detail)
  3. Department (sortable, truncated with tooltip)
  4. Employee Name (sortable, "—" if empty)
  5. Created Date (sortable, relative time: "2 days ago")
  6. Created By (sortable, user avatar + name)
  7. Status (badge: Active/Archived)
  8. Actions (dropdown: View, Edit, Export, Archive, Delete)

- **Bulk Actions Toolbar** (appears when items selected)
  - "X items selected"
  - Export Selected (dropdown: JSON, DOCX, PDF, ZIP)
  - Archive Selected
  - Delete Selected
  - Deselect All

- **Pagination** (bottom)
  - Items per page selector (10, 20, 50, 100)
  - Page numbers
  - Total count: "Showing 1-20 of 156 profiles"

- **Empty State** (when no results)
  - Icon: magnifying glass
  - "No profiles found"
  - "Try adjusting your filters or generate a new profile"
  - "Generate Profile" button

---

### 5. Profile Detail Page

**Layout:** Full-width with sticky header and tabbed content

**Sticky Header:**
- Back button ("← Back to Profiles")
- Position name (H2)
- Department breadcrumb
- Actions toolbar (right):
  - Edit button
  - Export dropdown (JSON, DOCX, MD, PDF)
  - Share link button
  - More dropdown (Archive, Delete, Duplicate)

**Tabbed Content:**

**Tab 1: Overview**
- Position Information Card
  - Title, Department, Employee Name
  - Employment Type, Reporting To
  - Status badge
- Summary Section
  - AI-generated summary (2-3 sentences)
- Metadata Card
  - Created: date + user
  - Last Modified: date + user
  - Generation Time: X seconds
  - Tokens Used: X
  - Model: Gemini 2.5 Flash

**Tab 2: Responsibilities**
- Numbered list of responsibilities
- Each item editable (in edit mode)
- Add responsibility button
- Drag-to-reorder handles

**Tab 3: Qualifications & Skills**
- Required Skills (tags, color-coded by category)
  - Technical Skills (blue)
  - Soft Skills (green)
  - Tools/Software (orange)
- Education Requirements
- Experience Requirements (years)
- Certifications (if applicable)

**Tab 4: KPIs**
- Table of KPIs:
  - KPI Name
  - Target Value
  - Measurement Frequency
  - Category
- Add KPI button
- KPI visualization (chart if numeric values)

**Tab 5: Organizational Context**
- Reporting Structure (org chart)
  - Reports to (above)
  - Peers (same level)
  - Subordinates (below)
- Career Path
  - Previous positions (path to this role)
  - Next positions (growth opportunities)

**Tab 6: Versions**
- Timeline of all versions
- Each version shows:
  - Version number (v1, v2, v3)
  - Date/Time
  - Modified by user
  - Change summary
  - "View" button → opens version diff modal
- "Restore Version" button (creates new version)

---

### 6. Analytics Dashboard

**Layout:** Grid of charts and metrics

**Top Row: Key Metrics Cards** (4 cards)
1. Total Profiles Generated (all time)
2. Profiles This Month (vs last month)
3. Average Generation Time (seconds)
4. Success Rate (percentage)

**Chart Row 1: Usage Trends**
- Line chart: Profiles generated over time
  - X-axis: Date (daily/weekly/monthly)
  - Y-axis: Count
  - Filter: Last 7/30/90 days, custom range

**Chart Row 2: Department Distribution**
- Horizontal bar chart: Profiles by department
  - Sorted by count (descending)
  - Top 10 departments
  - Clickable to filter profiles list

**Chart Row 3: Performance Metrics**
- Left: Donut chart - Success vs Failed generations
- Right: Area chart - Average generation time trend

**Chart Row 4: LLM Statistics**
- Stacked area chart: Token usage over time
  - Input tokens (blue)
  - Output tokens (green)
  - Total cost estimate (secondary Y-axis)

**Bottom Row: User Activity**
- Table: Top 10 users by profiles generated
  - User avatar + name
  - Profile count
  - Last active date

**Filters Panel** (sticky sidebar)
- Date range picker
- Department filter
- User filter
- "Export Analytics" button (CSV/Excel)

---

## Design System Specifications

### Color Palette

**Primary Colors (A101 Brand):**
```scss
$primary-blue: #0052CC;       // Main brand color
$primary-blue-dark: #003D99;  // Hover states
$primary-blue-light: #4C9AFF;  // Accents

$secondary-green: #00875A;     // Success states
$secondary-orange: #FF8B00;    // Warnings
$secondary-red: #DE350B;       // Errors/Destructive actions
```

**Neutral Palette:**
```scss
$neutral-900: #172B4D;  // Headings, primary text
$neutral-800: #253858;  // Body text
$neutral-600: #5E6C84;  // Secondary text
$neutral-400: #8993A4;  // Disabled text, placeholders
$neutral-200: #DFE1E6;  // Borders, dividers
$neutral-100: #F4F5F7;  // Background subtle
$neutral-50:  #FAFBFC;  // Background cards
$white:       #FFFFFF;  // Background main
```

**Semantic Colors:**
```scss
$success:      #00875A;  // Success messages, positive trends
$success-bg:   #E3FCEF;  // Success alert background

$warning:      #FF8B00;  // Warnings, attention needed
$warning-bg:   #FFFAE6;  // Warning alert background

$error:        #DE350B;  // Errors, validation issues
$error-bg:     #FFEBE6;  // Error alert background

$info:         #0065FF;  // Info messages, tips
$info-bg:      #DEEBFF;  // Info alert background
```

**Usage:**
- Primary Blue: Main CTA buttons, links, active states
- Neutral 900: Headings (H1-H6)
- Neutral 800: Body text
- Success Green: Generation completed, profile saved
- Warning Orange: Pending tasks, generation in progress
- Error Red: Failed generations, validation errors

---

### Typography

**Font Family:**
```scss
$font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-family-mono: 'JetBrains Mono', 'Courier New', monospace; // For code, IDs
```

**Type Scale:**
```scss
// Headings
$h1: 32px / 40px; font-weight: 700; // Page titles
$h2: 24px / 32px; font-weight: 600; // Section headers
$h3: 20px / 28px; font-weight: 600; // Card titles
$h4: 16px / 24px; font-weight: 600; // Subsection headers
$h5: 14px / 20px; font-weight: 600; // Small headers
$h6: 12px / 16px; font-weight: 600; // Overlines, labels

// Body
$body-large:  16px / 24px; font-weight: 400; // Main content
$body-medium: 14px / 20px; font-weight: 400; // Secondary content
$body-small:  12px / 16px; font-weight: 400; // Captions, metadata

// Specialized
$button:      14px / 20px; font-weight: 500; // Button text
$label:       12px / 16px; font-weight: 500; // Form labels, tags
$code:        13px / 20px; font-weight: 400; font-family: $font-family-mono;
```

**Usage Guidelines:**
- Maximum line length: 75 characters for optimal readability
- Headings: Use sentence case (not ALL CAPS)
- Links: Underline on hover, color change immediately
- Form labels: Always above input fields, not placeholders
- Error messages: Display below input with icon

---

### Spacing System

**8px Grid System:**
```scss
$space-xs:   4px;   // Tight spacing (icon padding)
$space-sm:   8px;   // Small spacing (button padding)
$space-md:   16px;  // Medium spacing (card padding)
$space-lg:   24px;  // Large spacing (section margins)
$space-xl:   32px;  // Extra large (page margins)
$space-2xl:  48px;  // Huge spacing (hero sections)
$space-3xl:  64px;  // Massive spacing (page breaks)
```

**Component Spacing:**
- **Cards:** `padding: $space-md` (16px)
- **Buttons:** `padding: $space-sm $space-md` (8px 16px)
- **Form inputs:** `padding: $space-sm` (8px)
- **Sections:** `margin-bottom: $space-lg` (24px)
- **Page margins:** `padding: $space-xl` (32px desktop), `$space-md` (16px mobile)

**Responsive Breakpoints:**
```scss
$breakpoint-xs: 0px;      // Mobile portrait
$breakpoint-sm: 640px;    // Mobile landscape
$breakpoint-md: 768px;    // Tablet
$breakpoint-lg: 1024px;   // Laptop
$breakpoint-xl: 1280px;   // Desktop
$breakpoint-2xl: 1536px;  // Large desktop
```

---

### Component Styles

**Buttons:**

```scss
// Primary Button
.btn-primary {
  background: $primary-blue;
  color: $white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: $primary-blue-dark;
  }

  &:disabled {
    background: $neutral-400;
    cursor: not-allowed;
  }
}

// Secondary Button
.btn-secondary {
  background: $white;
  color: $primary-blue;
  border: 1px solid $primary-blue;
  // ... same as primary
}

// Sizes
.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-md { padding: 8px 16px; font-size: 14px; } // Default
.btn-lg { padding: 12px 24px; font-size: 16px; }
```

**Cards:**

```scss
.card {
  background: $white;
  border: 1px solid $neutral-200;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.card-header {
  border-bottom: 1px solid $neutral-200;
  padding-bottom: 12px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: $neutral-900;
}
```

**Form Inputs:**

```scss
.input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid $neutral-200;
  border-radius: 4px;
  font-size: 14px;
  color: $neutral-900;
  background: $white;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: $primary-blue;
    box-shadow: 0 0 0 3px rgba(0, 82, 204, 0.1);
  }

  &:disabled {
    background: $neutral-100;
    color: $neutral-400;
    cursor: not-allowed;
  }

  &.error {
    border-color: $error;

    &:focus {
      box-shadow: 0 0 0 3px rgba(222, 53, 11, 0.1);
    }
  }
}

.input-label {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  font-weight: 500;
  color: $neutral-800;
}

.input-error {
  margin-top: 4px;
  font-size: 12px;
  color: $error;
  display: flex;
  align-items: center;
  gap: 4px;
}
```

**Badges/Tags:**

```scss
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;

  &.badge-success {
    background: $success-bg;
    color: $success;
  }

  &.badge-warning {
    background: $warning-bg;
    color: $warning;
  }

  &.badge-error {
    background: $error-bg;
    color: $error;
  }

  &.badge-info {
    background: $info-bg;
    color: $info;
  }
}
```

---

### Icons

**Icon Library:** [Element Plus Icons](https://element-plus.org/en-US/component/icon.html)

**Size Scale:**
```scss
$icon-xs:  12px;  // Inline with text
$icon-sm:  16px;  // Buttons, badges
$icon-md:  20px;  // Default
$icon-lg:  24px;  // Headers
$icon-xl:  32px;  // Feature icons
$icon-2xl: 48px;  // Hero icons, empty states
```

**Common Icons:**
- 🔍 Search: `<el-icon><Search /></el-icon>`
- ✏️ Edit: `<el-icon><Edit /></el-icon>`
- 📥 Download: `<el-icon><Download /></el-icon>`
- 🗑️ Delete: `<el-icon><Delete /></el-icon>`
- ➕ Add: `<el-icon><Plus /></el-icon>`
- ✅ Success: `<el-icon><SuccessFilled /></el-icon>`
- ❌ Error: `<el-icon><CircleCloseFilled /></el-icon>`
- ⚠️ Warning: `<el-icon><WarningFilled /></el-icon>`
- ℹ️ Info: `<el-icon><InfoFilled /></el-icon>`

---

## Accessibility Considerations

### WCAG 2.1 Level AA Compliance

**1. Color Contrast**
- All text meets WCAG AA contrast ratios:
  - Normal text (< 18px): 4.5:1 minimum
  - Large text (≥ 18px): 3:1 minimum
  - UI components and graphics: 3:1 minimum
- Never rely on color alone to convey information
- Use icons + text for all status indicators

**2. Keyboard Navigation**
- All interactive elements keyboard accessible:
  - `Tab` to navigate forward
  - `Shift+Tab` to navigate backward
  - `Enter` to activate buttons/links
  - `Space` to toggle checkboxes
  - `Esc` to close modals/dropdowns
- Focus indicators clearly visible (3px blue outline)
- Logical tab order matching visual layout
- Skip navigation link for screen readers

**3. Screen Reader Support**
- Semantic HTML (`<nav>`, `<main>`, `<article>`, etc.)
- ARIA labels for icon-only buttons:
  ```html
  <button aria-label="Export profile as DOCX">
    <el-icon><Download /></el-icon>
  </button>
  ```
- ARIA live regions for dynamic content:
  ```html
  <div role="status" aria-live="polite" aria-atomic="true">
    Profile generation in progress...
  </div>
  ```
- Form validation announcements:
  ```html
  <div role="alert" aria-live="assertive">
    Error: Department field is required
  </div>
  ```

**4. Form Accessibility**
- All inputs have associated `<label>` elements
- Error messages linked via `aria-describedby`
- Required fields marked with `aria-required="true"`
- Placeholder text NOT used as labels
- Fieldsets for grouped inputs (radio buttons, checkboxes)

**5. Alternative Text**
- All images have meaningful `alt` attributes
- Decorative images: `alt=""` or `aria-hidden="true"`
- Icons with semantic meaning include accessible text:
  ```html
  <el-icon aria-label="Success"><SuccessFilled /></el-icon>
  ```

**6. Responsive and Zoom**
- Support up to 200% zoom without horizontal scrolling
- Text resizable without loss of functionality
- Touch targets minimum 44x44px (mobile)
- Responsive breakpoints for all devices

**7. Motion and Animation**
- Respect `prefers-reduced-motion` media query:
  ```scss
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```
- Avoid auto-playing animations
- Provide pause/stop controls for carousels

**8. Language and Reading Level**
- HTML `lang` attribute set: `<html lang="ru">`
- Clear, concise language (avoid jargon)
- Error messages actionable and helpful
- Consistent terminology throughout

**9. Testing Tools**
- Automated: axe DevTools, Lighthouse
- Manual: NVDA, JAWS screen readers
- Keyboard-only navigation testing
- Color blindness simulators

---

## UX Pain Points & Improvements

### Current System Pain Points (NiceGUI)

| Pain Point | Impact | Proposed Vue.js Solution |
|------------|--------|--------------------------|
| **1. Slow position search** (1.5s load time for 4,376 positions) | High | Client-side filtering with virtual scrolling (< 300ms) |
| **2. No bulk operations** (must generate one profile at a time) | Critical | CSV upload + batch queue with parallel processing |
| **3. Generic progress updates** ("Processing...") | Medium | Step-by-step progress descriptions with time estimates |
| **4. No profile comparison** (can't compare side-by-side) | Medium | Split-view comparison mode with difference highlighting |
| **5. Unclear hierarchy** (duplicate department names confusing) | High | Full path breadcrumbs (Block/Dept/Unit/Group) |
| **6. No mobile support** (desktop-only layout) | Medium | Responsive design with mobile-first approach |
| **7. Limited export options** (manual downloads) | Medium | Bulk export as ZIP, email large files |
| **8. No inline editing** (must regenerate to change content) | High | Rich text editor with version control |
| **9. No approval workflow** (no review/approve states) | Low | Add status workflow (Draft/Review/Approved) |
| **10. Poor error recovery** (generic error messages) | High | Detailed error messages with retry/recovery options |

---

### Specific UX Improvements

**Improvement 1: Smart Position Search**

**Current:** Simple autocomplete, shows all 4,376 positions, slow

**Improved:**
- **Fuzzy matching:** Tolerates typos ("analitik" finds "аналитик")
- **Smart ranking:** Prioritizes:
  1. Exact matches
  2. Partial matches at start of word
  3. Department relevance (frequently used departments first)
  4. Recent history (positions user searched before)
- **Contextual suggestions:** Show related positions ("People who searched for 'Аналитик BI' also searched for...")
- **Category filters:** Quick filters by department family (IT, Sales, HR)
- **Keyboard shortcuts:** `Ctrl+K` to focus search from anywhere

---

**Improvement 2: Bulk Profile Generation**

**Current:** Generate one profile at a time (15 profiles = 45 minutes)

**Improved:**
- **CSV Upload:** Template with columns: Department, Position, Employee Name
- **Batch Queue:** Queue up to 50 profiles
- **Parallel Processing:** Generate 3 profiles simultaneously
- **Smart Scheduling:** Prioritize by department to optimize LLM context
- **Progress Dashboard:** Real-time overview of all queued tasks
- **Batch Export:** Download all completed profiles as ZIP
- **Email Notification:** Send download link when batch completes

**Impact:** 15 profiles in ~15 minutes (1 min/profile including overhead)

---

**Improvement 3: Enhanced Progress Tracking**

**Current:** Generic "Processing..." with percentage

**Improved:**
- **Detailed Steps:**
  1. "Analyzing organizational structure..." (0-10%)
  2. "Loading company context (567 business units)..." (10-20%)
  3. "Generating responsibilities section..." (20-40%)
  4. "Creating skills matrix..." (40-60%)
  5. "Calculating KPIs..." (60-80%)
  6. "Formatting and validating..." (80-95%)
  7. "Saving to database..." (95-100%)
- **Time Estimates:** "~30 seconds remaining"
- **Cancellation:** Clear "Cancel" button with confirmation
- **Background Tasks:** Continue generation if user navigates away
- **Desktop Notifications:** Browser notification when complete

---

**Improvement 4: Profile Comparison Mode**

**Current:** No comparison capability

**Improved:**
- **Split-view Layout:** 2-4 profiles side-by-side
- **Synchronized Scrolling:** Scroll all profiles together
- **Difference Highlighting:**
  - Green: Content in A but not B
  - Red: Content in B but not A
  - Yellow: Modified content
- **Section-level Comparison:** Compare only specific sections (e.g., just KPIs)
- **Export Comparison:** Generate PDF comparison report
- **Use Cases:**
  - Compare versions of same profile
  - Compare similar positions across departments
  - Ensure consistency in role definitions

---

**Improvement 5: Inline Profile Editing**

**Current:** Must regenerate profile to change content

**Improved:**
- **Edit Mode Toggle:** Switch between View and Edit modes
- **Rich Text Editor:** Quill.js or TipTap for formatting
- **Section-level Editing:** Edit each section independently
- **Auto-save Drafts:** Save every 30 seconds to prevent data loss
- **Version Control:** Each edit creates new version (v1, v2, v3...)
- **Change History:** Track who changed what and when
- **Restore Previous:** Revert to any previous version
- **Merge Conflicts:** Handle concurrent edits by multiple users

---

**Improvement 6: Approval Workflow**

**Current:** No formal approval process

**Improved:**
- **Profile States:**
  - Draft (editable by creator)
  - Pending Review (assigned to department head)
  - Approved (locked, official)
  - Archived (old versions)
- **Assignment:** HR assigns profiles to department heads for review
- **Comments:** Reviewers can leave inline comments
- **Rejection:** Send back to HR with required changes
- **Approval:** Department head approves → profile locked
- **Notifications:** Email alerts for state changes
- **Audit Log:** Track all state transitions

---

## Migration Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Goal:** Set up Vue.js project and core infrastructure

**Tasks:**
1. **Project Setup**
   - Initialize Vue 3 project with Vite
   - Install Element Plus, Pinia, Vue Router
   - Configure TypeScript
   - Set up ESLint, Prettier, Husky

2. **Backend API Integration**
   - Create API client service (Axios)
   - Implement JWT authentication
   - Set up API error handling
   - Configure CORS for local development

3. **Core Layout Components**
   - MainLayout (header, sidebar, footer)
   - AuthLayout (login page)
   - Route guards for authentication

4. **State Management**
   - Pinia store for auth (login, logout, token refresh)
   - Pinia store for UI (theme, notifications)

**Deliverables:**
- ✅ Functional login page
- ✅ Authenticated dashboard shell
- ✅ Route protection working
- ✅ API client connecting to FastAPI backend

**Success Metrics:**
- Login works with existing backend
- Token refresh automatic
- All routes protected

---

### Phase 2: Search & Discovery (Weeks 5-8)

**Goal:** Implement intelligent position search

**Tasks:**
1. **Organization Data Loading**
   - Fetch 567 business units from `/api/organization/search-items`
   - Cache data in Pinia store
   - Implement client-side search with Fuse.js (fuzzy matching)

2. **Search Component**
   - Element Plus Autocomplete
   - Custom result template (position + department path)
   - Keyboard navigation
   - Search history (localStorage)

3. **Department Filter**
   - Tree-select component for hierarchy
   - Breadcrumb navigation
   - Filter search results by department

4. **Search Performance**
   - Virtual scrolling for large result sets
   - Debounced search input (300ms)
   - Lazy loading of department tree

**Deliverables:**
- ✅ Fast position search (< 300ms response)
- ✅ Fuzzy matching works
- ✅ Department hierarchy visible
- ✅ Search history persisted

**Success Metrics:**
- Search returns results in < 300ms
- Users find positions with < 3 characters typed
- Zero confusion about department names

---

### Phase 3: Profile Generation (Weeks 9-12)

**Goal:** Core feature - generate profiles with progress tracking

**Tasks:**
1. **Single Profile Generation**
   - Generation form (department, position, employee name)
   - Advanced settings (temperature, custom instructions)
   - Start generation API call (`POST /api/generation/start`)

2. **Progress Tracking**
   - Poll task status (`GET /api/generation/{task_id}/status`)
   - Real-time progress bar updates
   - Step descriptions and time estimates
   - Cancel generation (`DELETE /api/generation/{task_id}`)

3. **Active Tasks Panel**
   - List all active generation tasks
   - Task cards with progress and actions
   - Auto-refresh every 3 seconds
   - Notifications on completion

4. **Result Handling**
   - Fetch completed profile (`GET /api/generation/{task_id}/result`)
   - Display profile in preview panel
   - Error handling and retry logic

**Deliverables:**
- ✅ Generate profile works end-to-end
- ✅ Progress updates real-time
- ✅ Task cancellation functional
- ✅ Errors handled gracefully

**Success Metrics:**
- 95% generation success rate
- Progress updates every 5 seconds
- Clear error messages for failures

---

### Phase 4: Profile Viewing (Weeks 13-16)

**Goal:** Rich profile viewer with tabs and export

**Tasks:**
1. **Profile Viewer Component**
   - Tabbed interface (Overview, Responsibilities, Skills, KPIs, Context, Metadata)
   - Collapsible sections
   - Print-friendly CSS
   - Copy-to-clipboard for sections

2. **Profile Actions**
   - Export dropdown (JSON, DOCX, MD, PDF)
   - Download API integration (`GET /api/profiles/{id}/download/{format}`)
   - Share link generation
   - Archive/Delete actions

3. **Profile Detail Page**
   - Fetch profile by ID (`GET /api/profiles/{id}`)
   - Sticky header with actions
   - Back navigation
   - Loading states and skeletons

4. **Profile List**
   - Data table with pagination (`GET /api/profiles/`)
   - Sortable columns
   - Basic filters (department, position, date range)
   - Clickable rows to detail page

**Deliverables:**
- ✅ Profile viewer displays all sections
- ✅ Export to all formats works
- ✅ Profiles list with pagination
- ✅ Detail page navigation smooth

**Success Metrics:**
- Profile loads in < 1 second
- All export formats generate correctly
- Table handles 1000+ profiles smoothly

---

### Phase 5: Advanced Features (Weeks 17-20)

**Goal:** Bulk operations, editing, comparison

**Tasks:**
1. **Bulk Generation**
   - CSV template download
   - File upload validation (Element Plus Upload)
   - Queue management (Pinia store)
   - Parallel generation (max 3)
   - Bulk export as ZIP

2. **Profile Editing**
   - Edit mode toggle
   - Rich text editor (TipTap)
   - Auto-save drafts
   - Version control (save edits as new version)
   - Discard changes confirmation

3. **Profile Comparison**
   - Multi-select from profiles list
   - Split-view layout (2-4 columns)
   - Synchronized scrolling
   - Difference highlighting
   - Export comparison report

4. **Advanced Filters**
   - Date range picker
   - Status filter (active/archived)
   - Created by user filter
   - Save filter presets

**Deliverables:**
- ✅ Bulk upload and generation working
- ✅ Inline editing with versions
- ✅ Comparison mode functional
- ✅ Advanced filters applied

**Success Metrics:**
- 50 profiles generated in < 30 minutes
- Editing auto-saves every 30s
- Comparison highlights differences accurately

---

### Phase 6: Analytics & Admin (Weeks 21-24)

**Goal:** Dashboard analytics and admin features

**Tasks:**
1. **Analytics Dashboard**
   - Key metrics cards (total profiles, monthly count, success rate)
   - Charts (Chart.js or ECharts):
     - Profiles generated over time (line chart)
     - Profiles by department (bar chart)
     - Success vs failed (donut chart)
     - Token usage (stacked area chart)
   - Date range filtering
   - Export analytics (CSV)

2. **User Activity Tracking**
   - Top users by profile count
   - Recent activity feed
   - Usage patterns analysis

3. **Admin Features**
   - User management (create, edit, deactivate users)
   - System configuration (LLM settings, rate limits)
   - Data management (bulk delete, cleanup)

4. **Notifications System**
   - Element Plus Notification component
   - Toast messages for actions
   - Email notifications for long tasks
   - Browser push notifications (optional)

**Deliverables:**
- ✅ Analytics dashboard with charts
- ✅ User activity tracking
- ✅ Admin panel functional
- ✅ Notification system working

**Success Metrics:**
- Charts render in < 2 seconds
- Analytics update in real-time
- Admin can manage users easily

---

### Phase 7: Polish & Launch (Weeks 25-28)

**Goal:** Production-ready application

**Tasks:**
1. **Performance Optimization**
   - Code splitting (lazy load routes)
   - Bundle size optimization (< 500KB gzipped)
   - Image optimization (WebP format)
   - Cache API responses (service worker)

2. **Accessibility Audit**
   - Run axe DevTools
   - Test with screen readers (NVDA, JAWS)
   - Keyboard navigation testing
   - Fix all WCAG AA issues

3. **Responsive Design**
   - Mobile layouts for all pages
   - Touch-friendly controls (44x44px minimum)
   - Hamburger menu for mobile nav
   - Test on iOS and Android

4. **Testing**
   - Unit tests (Vitest) - 80% coverage
   - E2E tests (Playwright) - critical paths
   - Integration tests (API + UI)
   - Load testing (100 concurrent users)

5. **Documentation**
   - User guide (screenshots + videos)
   - Admin guide (system management)
   - Developer docs (API, components)
   - Deployment guide (Docker, Nginx)

6. **Deployment**
   - Build production bundle
   - Configure Nginx reverse proxy
   - Set up SSL certificates
   - Deploy to production server
   - Smoke testing in production

**Deliverables:**
- ✅ Production-ready build
- ✅ Accessibility compliant (WCAG AA)
- ✅ Mobile responsive
- ✅ Test coverage > 80%
- ✅ Documentation complete
- ✅ Deployed and monitored

**Success Metrics:**
- Lighthouse score > 90 (Performance, Accessibility, Best Practices)
- Zero critical bugs in production
- < 1 second page load time
- Mobile usability score 100/100

---

## Conclusion

This comprehensive UX/UI specification provides a complete blueprint for migrating the HR Profile Generator from NiceGUI to Vue.js. The migration will deliver:

**Key Benefits:**
1. **Better Performance:** Client-side rendering, virtual scrolling, optimized bundle
2. **Enhanced UX:** Bulk operations, inline editing, comparison mode, smart search
3. **Scalability:** Modern architecture supports future growth (10,000+ profiles)
4. **Maintainability:** Component-based architecture, TypeScript, comprehensive testing
5. **Accessibility:** WCAG AA compliant, keyboard navigation, screen reader support
6. **Mobile Support:** Responsive design for tablets and phones

**Success Metrics Post-Migration:**
- **User Satisfaction:** Task completion time reduced by 60%
- **Performance:** Page load time < 1 second (from 3-5 seconds)
- **Adoption:** Mobile users can now access system (0% → 30%)
- **Efficiency:** Bulk generation enables 50 profiles in 30 minutes (vs 2.5 hours)
- **Quality:** Profile editing with versions improves content accuracy by 40%

**Next Steps:**
1. Review and approve this specification
2. Set up development environment
3. Begin Phase 1 (Foundation) implementation
4. Schedule weekly progress reviews
5. Conduct user testing after Phase 3

**Document Status:** Ready for stakeholder review and approval

---

**Author:** UX/UI Design Team
**Contact:** ux-team@a101.com
**Version:** 1.0
**Last Updated:** 2025-10-25

# Frontend Design & UX/UI Mockups
## A101 HR Profile Generator

*Created: September 8, 2025*
*System Analysis: Complete backend API analysis with real data understanding*

---

## Executive Summary

Основываясь на детальном анализе backend API и организационной структуры компании А101, проектируем современный веб-интерфейс для генерации профилей должностей. Система должна обрабатывать сложную многоуровневую иерархию (до 6 уровней глубины) и поддерживать полный цикл работы с профилями: от выбора должности до генерации и управления версиями.

---

## 1. Main Application Layout

### 1.1 Overall Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     HEADER                                  │
│ [🏢 A101 HR] [Home] [Profiles] [History]     [👤 Admin ▼] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    MAIN CONTENT AREA                        │
│                  (Dynamic Pages Below)                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    STATUS BAR                               │
│ [System Status] [Active Tasks] [Last Update: 20:43]        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Header Components
- **Logo & Brand**: "A101 HR Profile Generator" 
- **Navigation**: Home, Profiles, History
- **User Menu**: Avatar, username, logout
- **Status Indicators**: System health, active generation tasks

---

## 2. Page 1: Department Selection (Home)

### 2.1 UX Flow
**Goal**: Navigate the complex organizational hierarchy (Блок → Департамент → Управление → Отдел)

### 2.2 Layout Design

```
┌─────────────────────────────────────────────────────────────┐
│ 🏢 Генерация профилей должностей                            │
│                                                             │
│ ┌─────────────────┐ ┌───────────────────────────────────────┐ │
│ │   SEARCH & FILTER   │ │          DEPARTMENT TREE          │ │
│ │ 🔍 [Search dept...] │ │                                   │ │
│ │                     │ │ 📁 Блок безопасности (9)         │ │
│ │ Фильтры:            │ │ 📁 Блок бизнес-директора (156)   │ │
│ │ ☐ Есть профили      │ │   📁 Коммерческий департамент     │ │
│ │ ☐ Нет профилей      │ │   📁 Департамент по связям с      │ │
│ │ ☐ В процессе        │ │      общественностью (7)         │ │
│ │                     │ │ 📁 Блок директора по правовому    │ │
│ │ Сортировка:          │ │    обеспечению (87)              │ │
│ │ • По алфавиту       │ │ 📁 Блок директора по развитию     │ │
│ │ • По кол-ву долж.   │ │ 📁 Блок исполнительного           │ │
│ │ • По активности     │ │    директора (423)               │ │
│ └─────────────────┘ └───────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Tree View Interactions
- **Expandable nodes**: Click to expand/collapse
- **Path breadcrumbs**: Show current location in hierarchy
- **Count badges**: Show number of positions in each unit
- **Status indicators**: 
  - 🟢 All positions have profiles
  - 🟡 Some positions have profiles  
  - 🔴 No profiles generated
  - ⚙️ Generation in progress

### 2.4 Department Selection Logic
1. User clicks on department node
2. If has children → expand/collapse
3. If leaf node (final department) → navigate to positions page
4. Show full path in breadcrumbs: "Блок → Департамент → Управление"

---

## 3. Page 2: Positions List

### 3.1 UX Goal
Show all positions within selected department with clear status indicators

### 3.2 Layout Design

```
┌─────────────────────────────────────────────────────────────┐
│ 🏠 Home > Блок исполнительного директора > Архитектурный отдел │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                 DEPARTMENT INFO                         │ │
│ │ 📋 Архитектурный отдел                                  │ │
│ │ 📍 Path: Блок исп. директора/Дирекция проектного...    │ │
│ │ 👥 12 positions • 3 with profiles • 2 in progress      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                  POSITIONS LIST                         │ │
│ │                                                         │ │
│ │ 🟢 Главный архитектор                     [View Profile] │ │
│ │    Level 2 • Management • 2 versions                   │ │
│ │    Last updated: 15 Aug 2025                           │ │
│ │                                                         │ │
│ │ 🟡 Ведущий архитектор                    [View Profile] │ │
│ │    Level 3 • Technical • 1 version                     │ │
│ │    Generated: 10 Aug 2025                              │ │
│ │                                                         │ │
│ │ ⚙️ Архитектор                           [⏱️ Generating...] │ │
│ │    Level 4 • Technical • In progress (45%)             │ │
│ │    Started: 2 min ago                                  │ │
│ │                                                         │ │
│ │ 🔴 Младший архитектор                    [Generate Now] │ │
│ │    Level 5 • Specialist • No profile                  │ │
│ │                                                         │ │
│ │ 🔴 Стажёр архитектор                     [Generate Now] │ │
│ │    Level 5 • Junior • No profile                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Position Status States

#### 3.3.1 🟢 Has Profile(s) - Green
- **Visual**: Green circle icon
- **Info**: Shows version count, last update
- **Actions**: [View Profile] button
- **Additional**: If multiple versions → show version selector

#### 3.3.2 🟡 Has Some Profiles - Yellow  
- **Visual**: Yellow circle icon
- **Info**: Shows existing versions
- **Actions**: [View Profile] + [Generate New Version]

#### 3.3.3 ⚙️ In Progress - Blue
- **Visual**: Spinner icon
- **Info**: Progress percentage, time elapsed
- **Actions**: [Cancel Generation] (if allowed)
- **Real-time updates**: Progress bar, status changes

#### 3.3.4 🔴 No Profile - Red
- **Visual**: Red circle icon
- **Info**: "No profile generated"
- **Actions**: [Generate Now] button

---

## 4. Page 3: Profile View & Management

### 4.1 UX Goal
Display profile content, manage versions, enable editing and new generation

### 4.2 Layout Design

```
┌─────────────────────────────────────────────────────────────┐
│ 🏠 Home > Архитектурный отдел > Главный архитектор          │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                 PROFILE HEADER                          │ │
│ │ 👤 Главный архитектор                                    │ │
│ │ 🏢 Архитектурный отдел                                   │ │
│ │                                                         │ │
│ │ Version: [v2.1 ▼] [v2.1] [v2.0] [v1.0]                │ │
│ │ Created: 15 Aug 2025 by Admin                          │ │
│ │ Status: ✅ Completed • Score: 94%                       │ │
│ │                                                         │ │
│ │ [📝 Edit] [🎯 Generate New] [📄 Export] [🗑️ Delete]      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                  PROFILE CONTENT                        │ │
│ │                                                         │ │
│ │ ## Общая информация                                     │ │
│ │                                                         │ │
│ │ **Название должности:** Главный архитектор               │ │
│ │ **Департамент:** Архитектурный отдел                    │ │
│ │ **Уровень:** 2 (Senior Management)                     │ │
│ │ **Категория:** Management                               │ │
│ │                                                         │ │
│ │ ## Основные обязанности                                 │ │
│ │                                                         │ │
│ │ 1. Руководство архитектурными проектами...             │ │
│ │ 2. Координация работы команды архитекторов...          │ │
│ │ 3. Контроль качества проектной документации...         │ │
│ │                                                         │ │
│ │ ## Требования к кандидату                               │ │
│ │ ...                                                     │ │
│ │                                                         │ │
│ │ [Continue scrolling - full markdown content]           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                   METADATA PANEL                        │ │
│ │ 📊 Generation Metrics:                                  │ │
│ │ • Duration: 47 seconds                                  │ │
│ │ • Tokens used: 3,247                                   │ │
│ │ • Validation score: 94%                                 │ │
│ │ • Completeness: 97%                                     │ │
│ │                                                         │ │
│ │ 🏷️ Tags: Management, Senior, Architecture               │ │
│ │ 🔗 Langfuse trace: [View Details]                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Version Management
- **Version selector**: Dropdown with all versions
- **Visual diff**: Compare versions (future enhancement)
- **Version info**: Creation date, author, changes summary

### 4.4 Action Buttons

#### 4.4.1 📝 Edit Profile
- Opens inline editor or modal
- Allows modification of profile text
- Saves as new version or overwrites current

#### 4.4.2 🎯 Generate New Version
- Triggers new AI generation
- Uses same position data
- Creates new version automatically

#### 4.4.3 📄 Export Options
- JSON format
- Markdown format  
- Word document
- PDF report

---

## 5. Page 4: Generation Process

### 5.1 UX Goal
Provide clear feedback during asynchronous generation process

### 5.2 Generation Dialog

```
┌─────────────────────────────────────────────────────────────┐
│                     Generate Profile                        │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 👤 Position: Младший архитектор                         │ │
│ │ 🏢 Department: Архитектурный отдел                      │ │
│ │ 📍 Full path: Блок исп. дир. > Дирекция > ... > Арх.отдел │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    OPTIONS                              │ │
│ │                                                         │ │
│ │ Employee Name (optional):                               │ │
│ │ [________________________]                              │ │
│ │                                                         │ │
│ │ AI Temperature: [━━━━━━●━━━] 0.1 (More consistent)      │ │
│ │                                                         │ │
│ │ ☑️ Save result to database                              │ │
│ │ ☑️ Send notification when complete                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Cancel] [Generate Profile]                                 │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Progress Modal

```
┌─────────────────────────────────────────────────────────────┐
│                Generating Profile...                        │
│                                                             │
│ ⚙️ Current step: Генерация профиля через LLM               │ │
│                                                             │
│ Progress: [████████████████████████░░░░░] 75%              │
│                                                             │
│ ⏱️ Elapsed: 35 seconds                                     │
│ 🎯 Estimated: ~45 seconds total                            │
│                                                             │
│ Task ID: f47ac10b-58cc-4372-a567-0e02b2c3d479             │
│                                                             │
│ [Run in Background] [Cancel Generation]                     │
└─────────────────────────────────────────────────────────────┘
```

### 5.4 Real-time Updates
- **Progress bar**: Updates every 2-3 seconds
- **Step indicator**: Shows current processing stage
- **Time tracking**: Elapsed and estimated remaining
- **Background option**: User can continue using app

---

## 6. Page 5: Profiles Dashboard

### 6.1 UX Goal
Overview of all generated profiles with management capabilities

### 6.2 Layout Design

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 All Profiles Dashboard                                   │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              SEARCH & FILTERS                           │ │
│ │ 🔍 [Search profiles...]                                 │ │
│ │                                                         │ │
│ │ Department: [All ▼]  Status: [All ▼]  Level: [All ▼]   │ │
│ │ Created: [Last 30 days ▼]  Sort: [Newest first ▼]      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                  PROFILES TABLE                         │ │
│ │                                                         │ │
│ │ Position               Dept         Status    Created    │ │
│ │ ─────────────────────────────────────────────────────── │ │
│ │ 👤 Главный архитектор   Арх. отдел   ✅ v2.1   15 Aug   │ │
│ │ 👤 Ведущий архитектор   Арх. отдел   ✅ v1.0   10 Aug   │ │  
│ │ 👤 Senior Developer     IT Dept      ✅ v1.2   08 Aug   │ │
│ │ 👤 Project Manager      PMO          ⚙️ v1.0   Today    │ │
│ │ 👤 UX Designer          Design       ❌ Draft  07 Aug   │ │
│ │                                                         │ │
│ │ [< Previous] Page 1 of 5 [Next >]                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    QUICK STATS                          │ │
│ │ 📈 Total Profiles: 127                                  │ │
│ │ ✅ Completed: 89    ⚙️ In Progress: 5    ❌ Draft: 33   │ │
│ │ 📅 Generated this month: 23                             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Advanced Features
- **Bulk operations**: Select multiple profiles for batch export/delete
- **Advanced search**: Full-text search in profile content
- **Export options**: CSV list, ZIP archive of all profiles
- **Analytics**: Usage statistics, generation trends

---

## 7. Responsive Design Considerations

### 7.1 Mobile/Tablet Adaptations

#### Department Tree (Mobile)
- Convert to accordion/list view
- Swipe gestures for navigation
- Sticky search bar

#### Positions List (Mobile)
- Card-based layout instead of table
- Simplified status indicators
- Touch-friendly buttons

#### Profile View (Mobile)  
- Collapsible sections
- Bottom action sheet for buttons
- Optimized markdown rendering

### 7.2 Accessibility Requirements
- **Keyboard navigation**: Full app usable without mouse
- **Screen readers**: Proper ARIA labels and structure
- **Color blind support**: Icons + color coding
- **High contrast**: Support for accessibility themes

---

## 8. Technical Implementation Notes

### 8.1 State Management
- **Department selection**: URL-based routing
- **Real-time updates**: WebSocket for generation progress
- **Cache strategy**: Department/position data cached locally

### 8.2 Performance Optimizations
- **Virtual scrolling**: For large position lists
- **Lazy loading**: Department tree expansion
- **Progressive enhancement**: Core functionality works without JS

### 8.3 API Integration Points
```javascript
// Key API calls mapped to UI actions
GET /api/catalog/departments → Department Tree
GET /api/catalog/positions/{dept} → Positions List  
GET /api/profiles/{id} → Profile View
POST /api/generation/start → Generate Profile
GET /api/generation/{task_id}/status → Progress Updates
```

---

## 9. Error Handling & Edge Cases

### 9.1 Network Issues
- **Offline mode**: Show cached data with sync indicators
- **Retry mechanisms**: Auto-retry failed API calls
- **Error boundaries**: Graceful fallbacks for component errors

### 9.2 Generation Failures
- **Clear error messages**: Explain what went wrong
- **Retry options**: Allow user to retry generation
- **Partial results**: Show partial profiles if possible

### 9.3 Data Inconsistencies  
- **Stale data warnings**: Show when local data might be outdated
- **Conflict resolution**: Handle concurrent edits
- **Validation feedback**: Real-time validation of user inputs

---

## 10. Success Metrics & KPIs

### 10.1 User Experience Metrics
- **Time to first profile**: From login to viewing first profile
- **Generation success rate**: % of successful AI generations  
- **User task completion**: % of users who complete full workflow

### 10.2 System Performance
- **API response times**: All calls under 2s
- **Generation time**: Average AI generation under 60s
- **UI responsiveness**: No blocking operations over 100ms

### 10.3 Business Value
- **Profile coverage**: % of company positions with profiles
- **Profile quality**: Validation scores, user feedback
- **Usage adoption**: Active users, profiles generated per month

---

## Conclusion

This comprehensive UI/UX design addresses the complex organizational hierarchy of A101 while maintaining simplicity and usability. The design emphasizes clear visual status indicators, efficient navigation patterns, and robust error handling - critical for a system managing such detailed organizational data.

The phased approach allows for iterative development, starting with core profile generation functionality and expanding to advanced features like version comparison and analytics dashboards.

**Key Design Principles Applied:**
- **Hierarchy First**: UI structure mirrors organizational complexity
- **Status Clarity**: Always clear what state each position is in
- **Progressive Disclosure**: Show details when needed, hide complexity
- **Async-Aware**: Built for long-running AI generation processes
- **Mobile-Ready**: Responsive design from the start

This design foundation supports the technical implementation while ensuring excellent user experience for HR professionals managing hundreds of job profiles across A101's complex organizational structure.
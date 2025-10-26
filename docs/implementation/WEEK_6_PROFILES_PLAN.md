# Week 6: Profiles List Management - Implementation Plan

**Date**: 2025-10-26
**Status**: Planning
**Priority**: HIGH
**Dependencies**: Week 1-5 complete ✅

---

## 🎯 Goals

Implement comprehensive profile management UI with CRUD operations, advanced filtering, versioning, and bulk operations.

---

## 📊 Current State (After Week 5)

### ✅ Existing Components
- **UnifiedProfilesView** - Main view with statistics
- **PositionsTable** - Table with position/profile data
- **FilterBar** - Basic filtering UI
- **BulkActionsBar** - Bulk operation buttons
- **ProfileViewerModal** - View profile content
- **ProfileContent** - Display profile sections
- **ProfileMetadata** - Display metadata (date, version, etc.)
- **StatusBadge** - Show generation status

### ✅ Existing Features
- ✅ View list of positions with generation status
- ✅ Filter by status, department, search query
- ✅ Select multiple positions for bulk operations
- ✅ Bulk generate profiles
- ✅ Bulk cancel generation tasks
- ✅ View profile content in modal
- ✅ Download profile (JSON)
- ✅ Real-time statistics (total, generated, coverage, in progress)
- ✅ Polling for active generation tasks

### ⚠️ Missing Features (Week 6 Scope)
- ❌ **CRUD Operations**:
  - Create new profile manually
  - Edit existing profile
  - Delete profile
  - Regenerate profile

- ❌ **Advanced Filtering**:
  - Filter by date range (created, updated)
  - Filter by multiple departments
  - Filter by generation quality/score
  - Save filter presets

- ❌ **Versioning**:
  - View version history
  - Compare versions (diff view)
  - Restore previous version
  - Version metadata (author, timestamp, reason)

- ❌ **Enhanced Bulk Operations**:
  - Bulk download (ZIP archive)
  - Bulk export (DOCX, MD, XLSX)
  - Bulk tag/categorize
  - Bulk quality check

- ❌ **Export Enhancements**:
  - Download as DOCX
  - Download as Markdown
  - Download as XLSX
  - Bulk download multiple profiles

---

## 📋 Week 6 Tasks Breakdown

### Phase 1: CRUD Operations (Days 1-2)

#### Task 1.1: Edit Profile Modal
**Priority**: HIGH
**Estimated time**: 4 hours

**Requirements**:
- Create `ProfileEditModal.vue` component
- Form fields for all profile sections:
  - Basic info (position, department)
  - Responsibilities (list editor)
  - Competencies (nested editor)
  - Requirements (categorized editor)
  - Skills (tags/chips editor)
- Validation rules
- Save/Cancel actions
- Error handling

**API Endpoints** (check if exist):
- `PUT /api/profiles/{id}` - Update profile

**Files to create**:
- `frontend-vue/src/components/profiles/ProfileEditModal.vue`
- `frontend-vue/src/types/profile.ts` - Update types

#### Task 1.2: Create Profile Modal
**Priority**: MEDIUM
**Estimated time**: 3 hours

**Requirements**:
- Create `ProfileCreateModal.vue` component
- Similar form to edit modal
- Position/department selection
- Manual profile creation (no AI generation)
- Template selection (optional)

**API Endpoints**:
- `POST /api/profiles` - Create profile

**Files to create**:
- `frontend-vue/src/components/profiles/ProfileCreateModal.vue`

#### Task 1.3: Delete Profile Confirmation
**Priority**: MEDIUM
**Estimated time**: 2 hours

**Requirements**:
- Create `ConfirmDeleteDialog.vue` component
- Show profile details before delete
- Confirmation checkbox or double confirmation
- Bulk delete support

**API Endpoints**:
- `DELETE /api/profiles/{id}` - Delete profile

**Files to create**:
- `frontend-vue/src/components/common/ConfirmDeleteDialog.vue`

#### Task 1.4: Regenerate Profile Action
**Priority**: HIGH
**Estimated time**: 2 hours

**Requirements**:
- Add "Regenerate" button to PositionsTable
- Confirmation dialog with reason input
- Keep old version in history
- Trigger generation with same parameters

**Implementation**:
- Reuse existing generation logic from generator store
- Add version note/reason field

---

### Phase 2: Advanced Filtering (Days 3-4)

#### Task 2.1: Enhanced FilterBar
**Priority**: HIGH
**Estimated time**: 4 hours

**Requirements**:
- **Date Range Picker**:
  - Created date range
  - Updated date range
  - Use Vuetify v-date-picker or vue3-datepicker
- **Department Multi-Select**:
  - Checkbox list or autocomplete
  - Show count per department
- **Quality Score Filter**:
  - Slider or range input
  - If quality scores available
- **Clear All Filters** button

**Files to modify**:
- `frontend-vue/src/components/profiles/FilterBar.vue`
- `frontend-vue/src/stores/profiles.ts` - Update filtering logic

#### Task 2.2: Filter Presets
**Priority**: MEDIUM
**Estimated time**: 3 hours

**Requirements**:
- Save current filter state as preset
- Preset name input
- List of saved presets
- Quick apply preset
- Delete preset
- Store in localStorage

**Files to create**:
- `frontend-vue/src/components/profiles/FilterPresets.vue`
- `frontend-vue/src/utils/filterPresets.ts` - Preset management

#### Task 2.3: Advanced Search
**Priority**: MEDIUM
**Estimated time**: 3 hours

**Requirements**:
- Search in profile content (competencies, responsibilities)
- Search operators: AND, OR, NOT, quotes
- Search history
- Search suggestions

**Implementation**:
- Use existing Fuse.js for fuzzy search
- Extend search fields

---

### Phase 3: Versioning (Days 5-6)

#### Task 3.1: Version History Modal
**Priority**: HIGH
**Estimated time**: 5 hours

**Requirements**:
- Create `VersionHistoryModal.vue` component
- Timeline view of versions
- Version metadata:
  - Version number
  - Created timestamp
  - Author (if available)
  - Reason/notes
  - Quality score (if available)
- Actions per version:
  - View version
  - Compare with current
  - Restore version
  - Delete version

**API Endpoints** (need to check/create):
- `GET /api/profiles/{id}/versions` - List versions
- `GET /api/profiles/{id}/versions/{version}` - Get specific version
- `POST /api/profiles/{id}/versions/{version}/restore` - Restore version
- `DELETE /api/profiles/{id}/versions/{version}` - Delete version

**Files to create**:
- `frontend-vue/src/components/profiles/VersionHistoryModal.vue`
- `frontend-vue/src/types/version.ts` - Version types

#### Task 3.2: Version Comparison (Diff View)
**Priority**: MEDIUM
**Estimated time**: 4 hours

**Requirements**:
- Side-by-side comparison of two versions
- Highlight differences (additions, deletions, modifications)
- Use diff library (e.g., `diff` or `fast-diff`)
- Collapsible sections
- Visual indicators (colors, icons)

**Files to create**:
- `frontend-vue/src/components/profiles/VersionCompareModal.vue`
- `frontend-vue/src/utils/diffHelper.ts` - Diff utilities

#### Task 3.3: Version Restoration
**Priority**: HIGH
**Estimated time**: 2 hours

**Requirements**:
- Confirmation dialog before restore
- Show what will be restored
- Create new version (don't overwrite current)
- Notification after success

**Implementation**:
- Reuse ProfileEditModal logic
- Add version metadata

---

### Phase 4: Enhanced Bulk Operations (Day 7)

#### Task 4.1: Bulk Download (ZIP)
**Priority**: HIGH
**Estimated time**: 3 hours

**Requirements**:
- Download selected profiles as ZIP archive
- Multiple formats in one ZIP (JSON, MD, DOCX)
- Progress indicator for large batches
- Use JSZip library

**API Endpoints**:
- `POST /api/profiles/bulk/download` - Bulk download request
- Or handle client-side with multiple API calls

**Files to modify**:
- `frontend-vue/src/stores/profiles.ts` - Add bulkDownload action
- `frontend-vue/src/components/profiles/BulkActionsBar.vue` - Add button

#### Task 4.2: Bulk Export Formats
**Priority**: MEDIUM
**Estimated time**: 3 hours

**Requirements**:
- Export format selector (JSON, MD, DOCX, XLSX)
- Generate files for all selected profiles
- Pack into ZIP if multiple files
- Show progress

**Files to modify**:
- `frontend-vue/src/stores/profiles.ts` - Add bulkExport action

#### Task 4.3: Bulk Quality Check
**Priority**: LOW
**Estimated time**: 2 hours

**Requirements**:
- Run quality checks on selected profiles
- Show results in dialog
- Highlight issues
- Suggest regeneration for low-quality profiles

**API Endpoints** (if available):
- `POST /api/profiles/bulk/quality-check`

---

### Phase 5: Export Enhancements (Day 7-8)

#### Task 5.1: DOCX Export
**Priority**: HIGH
**Estimated time**: 4 hours

**Requirements**:
- Convert profile to DOCX format
- Use existing backend endpoint or docx.js library
- Proper formatting (headings, lists, tables)
- Company branding/logo (optional)

**API Endpoints**:
- `GET /api/profiles/{id}/export/docx` - Export as DOCX

**Files to modify**:
- `frontend-vue/src/services/profile.service.ts` - Add exportDocx method
- `frontend-vue/src/stores/profiles.ts` - Add downloadDocx action

#### Task 5.2: Markdown Export
**Priority**: MEDIUM
**Estimated time**: 2 hours

**Requirements**:
- Convert profile to Markdown format
- Proper Markdown syntax
- Code blocks for structured data

**API Endpoints**:
- `GET /api/profiles/{id}/export/md` - Export as Markdown

#### Task 5.3: XLSX Export
**Priority**: MEDIUM
**Estimated time**: 3 hours

**Requirements**:
- Export profile as Excel spreadsheet
- Multiple sheets (overview, competencies, requirements)
- Formatted tables
- Use xlsx library or backend endpoint

**API Endpoints**:
- `GET /api/profiles/{id}/export/xlsx` - Export as XLSX

---

## 🗂️ File Structure (New Files)

```
frontend-vue/
├── src/
│   ├── components/
│   │   ├── profiles/
│   │   │   ├── ProfileEditModal.vue          # NEW - Edit profile
│   │   │   ├── ProfileCreateModal.vue        # NEW - Create profile
│   │   │   ├── VersionHistoryModal.vue       # NEW - Version history
│   │   │   ├── VersionCompareModal.vue       # NEW - Compare versions
│   │   │   ├── FilterBar.vue                 # MODIFY - Enhanced filters
│   │   │   ├── BulkActionsBar.vue            # MODIFY - More actions
│   │   │   ├── PositionsTable.vue            # MODIFY - Add actions
│   │   ├── common/
│   │   │   ├── ConfirmDeleteDialog.vue       # NEW - Delete confirmation
│   │   │   ├── FilterPresets.vue             # NEW - Filter presets
│   ├── types/
│   │   ├── version.ts                        # NEW - Version types
│   │   ├── profile.ts                        # MODIFY - Update types
│   ├── stores/
│   │   ├── profiles/
│   │   │   ├── actions-crud.ts               # MODIFY - CRUD operations
│   │   │   ├── actions-export.ts             # MODIFY - Export formats
│   │   │   ├── actions-versions.ts           # NEW - Version management
│   │   │   ├── actions-filters.ts            # MODIFY - Enhanced filters
│   ├── utils/
│   │   ├── diffHelper.ts                     # NEW - Diff utilities
│   │   ├── filterPresets.ts                  # NEW - Preset management
│   │   ├── exportHelper.ts                   # NEW - Export utilities
│   ├── views/
│   │   ├── UnifiedProfilesView.vue           # MODIFY - Integrate modals
```

---

## 🔗 Backend API Requirements

**Endpoints to check/implement**:

1. **CRUD**:
   - `PUT /api/profiles/{id}` - Update profile
   - `POST /api/profiles` - Create profile
   - `DELETE /api/profiles/{id}` - Delete profile

2. **Versioning**:
   - `GET /api/profiles/{id}/versions` - List versions
   - `GET /api/profiles/{id}/versions/{version}` - Get version
   - `POST /api/profiles/{id}/versions/{version}/restore` - Restore
   - `DELETE /api/profiles/{id}/versions/{version}` - Delete version

3. **Export**:
   - `GET /api/profiles/{id}/export/docx` - DOCX export
   - `GET /api/profiles/{id}/export/md` - Markdown export
   - `GET /api/profiles/{id}/export/xlsx` - XLSX export

4. **Bulk Operations**:
   - `POST /api/profiles/bulk/download` - Bulk download
   - `POST /api/profiles/bulk/export` - Bulk export
   - `POST /api/profiles/bulk/quality-check` - Quality check

---

## 📊 Testing Requirements

### Unit Tests
- ProfileEditModal component
- ProfileCreateModal component
- VersionHistoryModal component
- CRUD actions in profiles store
- Version management actions
- Export utilities
- Diff helpers

### Integration Tests
- Complete CRUD flow
- Version history flow
- Bulk operations
- Export flow

### E2E Tests
- User creates profile manually
- User edits existing profile
- User views version history
- User compares two versions
- User restores previous version
- User downloads multiple profiles

---

## 🎨 UX/UI Considerations

1. **Modals**:
   - Use consistent modal sizes (max-width: 800px for forms, 1200px for comparisons)
   - Smooth transitions
   - Keyboard navigation (Esc to close, Tab for fields)

2. **Forms**:
   - Inline validation
   - Auto-save draft (localStorage)
   - Field-level error messages
   - Required field indicators

3. **Bulk Operations**:
   - Progress indicators
   - Cancelable operations
   - Batch size limits (e.g., 50 profiles max)
   - Clear feedback messages

4. **Versioning**:
   - Visual timeline
   - Clear version numbering (v1, v2, v3)
   - Highlight current version
   - Show diff summary (X changes)

5. **Responsive Design**:
   - Mobile-friendly modals
   - Touch-friendly buttons
   - Collapsible sections on small screens

---

## 🚀 Implementation Order (Recommended)

### Day 1-2: CRUD Operations
1. ProfileEditModal (4h)
2. ConfirmDeleteDialog (2h)
3. Regenerate action (2h)
4. ProfileCreateModal (3h)

### Day 3-4: Advanced Filtering
5. Enhanced FilterBar (4h)
6. Filter Presets (3h)
7. Advanced Search (3h)

### Day 5-6: Versioning
8. VersionHistoryModal (5h)
9. Version Restoration (2h)
10. VersionCompareModal (4h)

### Day 7-8: Bulk & Export
11. Bulk Download ZIP (3h)
12. DOCX Export (4h)
13. Bulk Export Formats (3h)
14. Markdown/XLSX Export (5h)

**Total estimated time**: ~47 hours (~6-7 working days)

---

## ✅ Definition of Done

Week 6 is complete when:

- ✅ Users can create profiles manually
- ✅ Users can edit existing profiles
- ✅ Users can delete profiles with confirmation
- ✅ Users can regenerate profiles
- ✅ Advanced filtering works (date range, multi-select departments)
- ✅ Users can save and apply filter presets
- ✅ Users can view version history of profiles
- ✅ Users can compare two versions
- ✅ Users can restore previous versions
- ✅ Users can download profiles in multiple formats (DOCX, MD, XLSX)
- ✅ Users can bulk download multiple profiles as ZIP
- ✅ All unit tests passing
- ✅ Integration tests for critical flows
- ✅ Documentation updated
- ✅ Code review completed

---

## 📚 Dependencies

**NPM Packages** (may need to install):
- `jszip` - ✅ Already installed (for ZIP creation)
- `file-saver` - ✅ Already installed (for file downloads)
- `diff` or `fast-diff` - For version comparison
- `docx` (optional) - If client-side DOCX generation needed
- `xlsx` (optional) - If client-side XLSX generation needed
- Vue3 date picker component (research options)

---

## 🎯 Success Metrics

- **User Efficiency**: Time to manage profiles reduced by 50%
- **Feature Adoption**: 80% of users use advanced filtering within first week
- **Version Management**: 60% of regenerated profiles use version history
- **Export Usage**: 70% of downloads use non-JSON formats (DOCX/MD/XLSX)
- **Bulk Operations**: 40% of downloads are bulk downloads
- **Error Rate**: <5% error rate on CRUD operations
- **Performance**: All operations complete within 2 seconds (excluding generation)

---

**Created**: 2025-10-26
**Next Review**: After Phase 1 completion
**Owner**: Frontend Team

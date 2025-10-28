# Documentation Cleanup Plan

**Date**: 2025-10-28
**Status**: IN PROGRESS
**Goal**: Organize 208 documentation files, remove outdated content, ensure accuracy

---

## 📊 Current State

- **Total files**: 208 in `docs/`, 21 in `.memory_bank/`
- **Problem**: Many outdated planning docs, completed analysis reports, redundant files
- **Impact**: Hard to find current information, confusion about project state

---

## 🎯 Cleanup Actions

### Phase 1: Root Level Cleanup (PRIORITY 1)

**Files to move to archive** (6 Vue planning docs from Oct 25):
```
docs/VUE_MIGRATION_EXECUTIVE_DECISION.md        → docs/archive/planning/vue-migration/
docs/VUE_MVP_IMPLEMENTATION_PLAN.md             → docs/archive/planning/vue-migration/
docs/VUE_MVP_SIMPLIFIED_PLAN.md                 → docs/archive/planning/vue-migration/
docs/VUE_STYLING_STRATEGY.md                    → docs/archive/planning/vue-migration/
docs/VUE_WEEK_1_2_DETAILED_PLAN.md              → docs/archive/planning/vue-migration/
docs/ASYNC_OPENAI_MIGRATION.md                  → docs/archive/planning/
```

**Reason**: These planning docs are now historical - Week 6 is complete, Week 5 fully done.
**Keep**: `docs/README.md` - main index (update it)

---

### Phase 2: Analysis Directory Cleanup (PRIORITY 2)

**Current**: 52 files in `docs/analysis/`
**Action**: Move completed/historical analysis to `docs/archive/analysis/quality/`

**Files to archive** (prompt quality analysis - COMPLETED work):
```
docs/analysis/PROMPT_ENGINEERING_ANALYSIS.md
docs/analysis/PROMPT_QUALITY_FIXES_PROPOSAL.md
docs/analysis/PROMPT_IMPROVEMENTS_CHECKLIST.md
docs/analysis/llm_quality_analysis.md
docs/analysis/prompt_analysis_report.md
docs/analysis/SCHEMA_FIX_*.md (3 files)
docs/analysis/KPI_MAPPING_*.md (5 files)
docs/analysis/100_PERCENT_KPI_COVERAGE_IMPLEMENTATION.md
docs/analysis/HIERARCHICAL_KPI_IMPLEMENTATION_SUMMARY.md
docs/analysis/HR_EXPERT_QUALITY_ASSESSMENT.md
docs/analysis/CRITICAL_*.md (5 files)
docs/analysis/EXECUTIVE_SUMMARY.md
docs/analysis/FINAL_SUMMARY.md
docs/analysis/MULTI_EXPERT_SYNTHESIS.md
... (most files from Q1 2025 prompt optimization)
```

**Keep in docs/analysis/** (current/reference):
- V55_TEST_SUCCESS_REPORT.md (recent)
- ROOT_CAUSE_ANALYSIS_v48_vs_v52.md (recent)
- README.md (if exists)

---

### Phase 3: Implementation Directory Cleanup (PRIORITY 2)

**Current**: 25 files in `docs/implementation/`
**Action**: Move completed implementation reports to archive

**Files to archive**:
```
docs/implementation/P0_*.md (4 files - completed prompt work)
docs/implementation/P1_*.md (2 files)
docs/implementation/PROMPT_*.md (3 files - completed)
docs/implementation/SCHEMA_*.md (2 files - completed)
docs/implementation/BASECARD_REFACTORING.md (completed)
docs/implementation/BUG_08_*.md (completed)
docs/implementation/BUG_09_*.md (completed)
docs/implementation/DESIGN_CONSISTENCY_FIXES.md (completed)
docs/implementation/CODE_REVIEW_FIXES_*.md (3 files - completed)
docs/implementation/STATS_UNIFICATION_SUMMARY.md (completed)
docs/implementation/FRONTEND_API_UNIFICATION_REPORT.md (completed)
```

**Keep in docs/implementation/** (active):
- WEEK_6_PROFILES_PLAN.md (current plan)
- WEEK_6_PHASE_2_SUMMARY.md (current)
- FILTERBAR_SIMPLIFICATION.md (recent Week 6)
- FILTERBAR_UX_IMPROVEMENTS.md (recent Week 6)
- AGENT_WORK_PLAN.md (if current)
- IMPLEMENTATION_CHECKLIST.md (reference)
- JSDOC_ENHANCEMENT_EXAMPLES.md (reference)

---

### Phase 4: Testing Directory Cleanup (PRIORITY 2)

**Current**: 25 files in `docs/testing/`
**Action**: Move test reports to archive, keep guides

**Files to archive** (test reports):
```
docs/testing/V55_QUALITY_*.md (3 files)
docs/testing/P0_*.md (4 files)
docs/testing/P1_*.md (4 files)
docs/testing/FINAL_TESTING_RESULTS.md
docs/testing/EXECUTIVE_SUMMARY.md
docs/testing/QUALITY_ANALYSIS_SUMMARY.md
docs/testing/SEMANTIC_*.md (2 files)
docs/testing/RECOMMENDATIONS_BY_PROFILE.md
```

**Keep in docs/testing/** (guides and current):
- README.md (testing guide)
- TEST_IMPLEMENTATION_GUIDE.md
- TEST_SCENARIOS_COMPREHENSIVE.md
- VISUAL_TESTING_GUIDE.md
- BASECARD_TEST_PLAN.md (reference)
- BASERESPONSE_TEST_UPDATES.md (recent)

---

### Phase 5: Memory Bank Verification (PRIORITY 1)

**Files to verify/update**:
- `.memory_bank/tech_stack.md` - verify all dependencies are listed
- `.memory_bank/current_tasks.md` - ✅ JUST UPDATED
- `.memory_bank/product_brief.md` - verify accuracy
- `.memory_bank/architecture/component_library.md` - verify all components listed
- `.memory_bank/architecture/frontend_architecture.md` - verify accuracy
- `.memory_bank/guides/frontend_coding_standards.md` - verify rules match project

---

### Phase 6: Create Documentation Index (PRIORITY 3)

**Action**: Create comprehensive index of CURRENT documentation

**File to create**: `docs/CURRENT_DOCUMENTATION_INDEX.md`

**Sections**:
1. Active Plans (Week 6+)
2. Implementation Guides (current)
3. Testing Guides
4. API Documentation
5. Architecture Documentation
6. Company Data (KPI, org structure, IT systems)
7. Archive (historical work)

---

## 📋 Execution Order

1. ✅ Create this cleanup plan
2. ⏳ **Phase 1**: Move root Vue planning docs to archive
3. ⏳ **Phase 5**: Verify Memory Bank accuracy
4. ⏳ **Phase 2-4**: Clean up analysis/implementation/testing
5. ⏳ **Phase 6**: Create documentation index
6. ⏳ Update `docs/README.md` to reflect new structure

---

## 📈 Success Metrics

- **Before**: 208 files, unclear which are current
- **After**: ~50-60 current files, 150+ archived, clear index
- **Result**: Easy to find current documentation, historical work preserved

---

## 🚨 Important Rules

1. **NEVER delete** - only move to archive
2. **Preserve history** - all work has value for reference
3. **Update indexes** - keep README files current
4. **Single source of truth** - Memory Bank is authoritative for current state

---

**Last Updated**: 2025-10-28
**Next Review**: After Week 7 completion

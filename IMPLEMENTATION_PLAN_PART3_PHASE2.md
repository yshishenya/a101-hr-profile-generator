# IMPLEMENTATION PLAN - PART 3: PHASE 2 BACKEND FILTERING
## Weeks 2-3: Position-Aware KPI Filtering

**Goal:** Improve quality from 6.0/10 (after Phase 1) to 8.0/10 (+33% additional improvement)
**Timeline:** 5-7 days (Weeks 2-3)
**Risk Level:** MEDIUM (code changes, moderate refactoring)

---

## PHASE 2 OVERVIEW

### What We're Building

**Backend KPI Filtering System:**
- Parse KPI files (YAML frontmatter + markdown table)
- Match user's position to KPI file columns (fuzzy matching)
- Filter KPIs where position weight > 0%
- Rebuild clean markdown with only 3-5 relevant KPIs
- Integrate with DataLoader

### Expected Results After Phase 2

| Metric | After Phase 1 | After Phase 2 | Improvement |
|--------|---------------|---------------|-------------|
| Overall Quality | 6.0/10 | **8.0/10** | +33% |
| KPI Accuracy | 85% | **95%+** | +12% |
| KPI Count | 4-6 | **3-5** | Optimal |
| Token Usage (KPI) | 2-4K | **200-500** | -80% |

**Why Backend Filtering?**
- Prompt guidance (Phase 1) improved from 60% → 85%
- But LLM still sees ALL 34 KPIs → can still make mistakes
- Backend filtering GUARANTEES only relevant KPIs reach LLM → 95%+ accuracy

---

## ARCHITECTURE OVERVIEW

### Current Data Flow (After Phase 1)

```
Excel KPI File (34 rows × 5 positions)
    ↓
KPIMapper.load_kpi_content(department)
    ↓
Returns: ALL 34 KPI rows (2-4K tokens)
    ↓
DataLoader adds to {{kpi_data}}
    ↓
Langfuse Prompt v27 (with KPI selection rules)
    ↓
LLM tries to filter (85% accuracy)
    ↓
Result: 4-6 KPIs (some errors remain)
```

### NEW Data Flow (Phase 2)

```
Excel KPI File (34 rows × 5 positions)
    ↓
KPIMapper.load_kpi_content_for_position(dept, position)
    ↓
  ├─> Parse YAML frontmatter (positions_map)
  ├─> Match position to column (fuzzy 80%+ confidence)
  ├─> Filter rows where weight > 0%
  └─> Rebuild markdown (only relevant KPIs)
    ↓
Returns: 3-5 filtered KPI rows (200-500 tokens, -80%)
    ↓
DataLoader adds to {{kpi_data}}
    ↓
Langfuse Prompt v27 receives ONLY relevant KPIs
    ↓
LLM sees clean data (95%+ accuracy)
    ↓
Result: 3-5 KPIs (all correct!)
```

**Key Benefit:** LLM no longer confused by irrelevant KPIs!

---

## IMPLEMENTATION DETAILS

### Complete Technical Specification

**Full implementation details are in:**
→ [KPI_FILTERING_IMPLEMENTATION_SPEC.md](KPI_FILTERING_IMPLEMENTATION_SPEC.md)

**Summary of changes:**

**File:** `/home/yan/A101/HR/backend/core/data_mapper.py`

**New Methods (add ~300 lines):**
1. `_parse_kpi_file()` - Parse YAML + markdown table
2. `_parse_markdown_table()` - Extract KPI rows with weights
3. `_match_position_to_column()` - Fuzzy position matching (thefuzz)
4. `_filter_kpis_by_position()` - Filter by weight > 0%
5. `_rebuild_kpi_markdown()` - Create clean markdown output
6. `load_kpi_content_for_position()` - Main method (replaces old one)

**File:** `/home/yan/A101/HR/backend/core/data_loader.py`

**Modify Line 69:**
```python
# OLD (Phase 1):
kpi_content = self.kpi_mapper.load_kpi_content(department)

# NEW (Phase 2):
try:
    kpi_content = self.kpi_mapper.load_kpi_content_for_position(
        department=department,
        position=position
    )
    logger.info(f"Using position-filtered KPI content for {position}")
except Exception as e:
    logger.warning(f"Filtering failed, using full content: {e}")
    kpi_content = self.kpi_mapper.load_kpi_content(department)  # Fallback
```

**Dependencies:**
```txt
PyYAML>=6.0  # Already present
thefuzz>=0.20.0  # NEW - fuzzy string matching
python-Levenshtein>=0.21.0  # NEW - speeds up thefuzz
```

---

## WEEK-BY-WEEK TIMELINE

### Week 2: Core Development (5 days)

**Day 1-2: Parsing & Position Matching**
- Implement `_parse_kpi_file()` with YAML frontmatter parsing
- Implement `_parse_markdown_table()` with regex
- Handle multi-line cells, Cyrillic text, dash "-" for zero values
- Implement `_match_position_to_column()` with fuzzy matching
- **Deliverable:** Can parse all 9 KPI files + match positions

**Day 3: Filtering Logic**
- Implement `_filter_kpis_by_position()`
- Include corporate KPIs logic
- Weight threshold checking (> 0%)
- Logging for transparency
- **Deliverable:** Can filter KPIs for any position

**Day 4: Markdown Rebuild & Integration**
- Implement `_rebuild_kpi_markdown()`
- Implement main `load_kpi_content_for_position()`
- Add error handling + fallback logic
- Modify data_loader.py line 69
- **Deliverable:** End-to-end filtering works

**Day 5: Unit Testing**
- Write unit tests (test_kpi_mapper_filtering.py)
- Test parsing, matching, filtering, rebuild
- Test with real KPI files
- Test error cases
- **Deliverable:** 90%+ test coverage

### Week 3: Testing & Refinement (2-3 days)

**Day 6: Integration Testing**
- Write integration tests (test_profile_generation_with_filtering.py)
- Test complete profile generation flow
- Test all 9 KPI files
- Validate token reduction
- **Deliverable:** Integration tests passing

**Day 7: End-to-End Validation**
- Generate 10 test profiles (various departments/positions)
- Compare KPI accuracy before/after
- Measure token savings
- Performance benchmarking
- Bug fixes
- **Deliverable:** Production-ready code

**Day 8 (Buffer):**
- Address any issues from testing
- Code review
- Documentation updates
- Prepare for Phase 3
- **Deliverable:** Week 3 complete

---

## CODE EXAMPLES

### Example: Parsing KPI File

**Input:** `KPI_ДИТ.md`
```markdown
---
department: ДИТ
positions_map:
  Директор по информационным технологиям: Сложеникин Алексей Вячеславович
  Руководитель отдела: Нор Евгений Алексеевич
---

| КПЭ | Целевое значение | Директор | Рук. отдела |
|-----|------------------|----------|-------------|
| SLA | 99% | 10% | - |
| NPS | 4.5 | 10% | - |
| Спринты | 80% | - | 15% |
```

**Output after `_parse_kpi_file()`:**
```python
frontmatter = {
    'department': 'ДИТ',
    'positions_map': {
        'Директор по информационным технологиям': 'Сложеникин Алексей Вячеславович',
        'Руководитель отдела': 'Нор Евгений Алексеевич'
    }
}

table_rows = [
    {
        'kpi_name': 'SLA',
        'target': '99%',
        'positions': {
            'Сложеникин Алексей Вячеславович': 0.1,
            'Нор Евгений Алексеевич': 0.0
        }
    },
    {
        'kpi_name': 'NPS',
        'target': '4.5',
        'positions': {
            'Сложеникин Алексей Вячеславович': 0.1,
            'Нор Евгений Алексеевич': 0.0
        }
    },
    {
        'kpi_name': 'Спринты',
        'target': '80%',
        'positions': {
            'Сложеникин Алексей Вячеславович': 0.0,
            'Нор Евгений Алексеевич': 0.15
        }
    }
]
```

### Example: Position Matching

**Input:** User requests profile for `"Директор ИТ"`

**Fuzzy Matching Process:**
```python
positions_map = {
    'Директор по информационным технологиям': 'Сложеникин А.В.',
    'Руководитель отдела': 'Нор Е.А.'
}

# fuzz.ratio("директор ит", "директор по информационным технологиям") = 62%
# fuzz.ratio("директор ит", "руководитель отдела") = 28%

# Best match: 62% < 80% threshold
# Falls back to partial matching or returns best match if > 75%
```

**Result:** Matches to "Директор по информационным технологиям" (confidence 85% with partial_ratio)

### Example: Filtering

**Input:** Position = "Директор по информационным технологиям"

**Filtering Logic:**
```python
# From table_rows above:
# SLA: weight = 0.1 (10%) ✅ INCLUDE
# NPS: weight = 0.1 (10%) ✅ INCLUDE
# Спринты: weight = 0.0 ❌ EXCLUDE
```

**Output after `_filter_kpis_by_position()`:**
```python
filtered_rows = [
    {'kpi_name': 'SLA', 'target': '99%', ...},
    {'kpi_name': 'NPS', 'target': '4.5', ...}
]
# 2 KPIs instead of 3 (33% reduction)
```

### Example: Rebuilt Markdown

**Output after `_rebuild_kpi_markdown()`:**
```markdown
# KPI для позиции: Директор по информационным технологиям

**Департамент:** ДИТ
**Количество KPI:** 2

| № | КПЭ | Целевое значение | Вес | Методика |
|---|-----|------------------|-----|----------|
| 1 | SLA | 99% | 10% | См. KPI файл |
| 2 | NPS | 4.5 | 10% | См. KPI файл |
```

**Token Count:**
- Original: ~2000 tokens (34 KPIs)
- Filtered: ~300 tokens (2 KPIs)
- **Reduction: 85%**

---

## TESTING STRATEGY

### Unit Tests (Day 5)

**File:** `tests/unit/test_kpi_mapper_filtering.py`

**Test Cases:**
1. ✅ `test_parse_kpi_file_structure()` - YAML + table parsing
2. ✅ `test_position_matching_exact()` - Direct position name match
3. ✅ `test_position_matching_fuzzy()` - Abbreviated name matching
4. ✅ `test_kpi_filtering_by_weight()` - Filters 0% weight KPIs
5. ✅ `test_markdown_rebuild()` - Clean output format
6. ✅ `test_load_kpi_for_position_real_file()` - Integration with real files
7. ✅ `test_fallback_on_position_not_found()` - Error handling

**Run:**
```bash
pytest tests/unit/test_kpi_mapper_filtering.py -v
```

**Expected:** 100% tests passing

### Integration Tests (Day 6)

**File:** `tests/integration/test_profile_generation_with_filtering.py`

**Test Cases:**
1. ✅ `test_director_profile_kpi_accuracy()` - 3-5 KPIs expected
2. ✅ `test_profile_validation_score()` - 7.0/10+ validation
3. ✅ `test_no_generic_terms()` - Zero "например" phrases
4. ✅ `test_all_9_kpi_files()` - Works for all departments

**Run:**
```bash
pytest tests/integration/test_profile_generation_with_filtering.py -v --asyncio-mode=auto
```

**Expected:** 100% tests passing

### End-to-End Validation (Day 7)

**Manual Test Plan:**

**Test Case 1: CIO Profile (High Complexity)**
- Department: "ДИТ"
- Position: "Директор по информационным технологиям"
- **Expected:**
  - 4 KPIs (matching Excel exactly)
  - No KPIs with 0% weight
  - Token reduction 80%+
  - Filtering logs show correct match

**Test Case 2: Middle Manager (Medium Complexity)**
- Department: "ДРР"
- Position: "Руководитель управления"
- **Challenge:** Multiple "Руководитель управления" in file
- **Expected:**
  - Correct column selected (fuzzy match with unit name)
  - 3-5 relevant KPIs
  - No cross-contamination from other managers

**Test Case 3: Junior (Edge Case)**
- Department: "ДИТ"
- Position: "Программист"
- **Expected:**
  - 2-4 KPIs (junior positions have fewer)
  - Falls back gracefully if not in KPI file
  - Validation still passes

---

## PERFORMANCE OPTIMIZATION

### Caching Strategy (Optional Enhancement)

**Problem:** Parsing same KPI file multiple times is wasteful

**Solution:** Add caching to KPIMapper

```python
class KPIMapper:
    def __init__(self):
        self._parse_cache = {}  # Cache parsed KPI files

    def _get_cached_parse(self, kpi_path: Path):
        cache_key = str(kpi_path)
        if cache_key not in self._parse_cache:
            with open(kpi_path) as f:
                content = f.read()
            self._parse_cache[cache_key] = self._parse_kpi_file(content)
        return self._parse_cache[cache_key]
```

**Impact:**
- First request: ~50ms parsing
- Cached requests: ~1ms (50x faster)
- Memory: ~100KB per cached file (acceptable)

### Performance Benchmark

**Expected Overhead:**

| Operation | Time | Impact |
|-----------|------|--------|
| Parse YAML | ~5-10ms | One-time per file |
| Parse markdown table | ~20-50ms | One-time per file |
| Fuzzy position matching | ~5-10ms | Per request |
| Filter KPIs | ~5-10ms | Per request |
| Rebuild markdown | ~5-10ms | Per request |
| **Total (uncached)** | **~40-90ms** | Acceptable |
| **Total (cached)** | **~15-30ms** | Excellent |

**Current generation time:** 8-12 seconds
**Added overhead:** ~0.05 seconds (<1% increase)

**Verdict:** ✅ Performance impact negligible

---

## RISK MANAGEMENT

### Risk #1: Parsing Fails for Complex Tables

**Probability:** MEDIUM
**Impact:** HIGH

**Mitigation:**
- Robust regex with multiple patterns
- Fallback to unfiltered content (system keeps working)
- Try-catch around all parsing operations
- Extensive testing with all 9 KPI files

**Contingency:**
- If parsing fails → log error + use unfiltered (Phase 1 quality maintained)
- Fix parser offline, re-deploy

### Risk #2: Position Matching Accuracy < 90%

**Probability:** MEDIUM
**Impact:** MEDIUM

**Mitigation:**
- Fuzzy matching threshold = 80% (tunable)
- Can add manual synonym dictionary
- Logging shows confidence score
- Test with 50+ position name variations

**Contingency:**
- Lower threshold to 75%
- Add position aliases to config
- Manual review of low-confidence matches

### Risk #3: Performance Degradation

**Probability:** LOW
**Impact:** LOW

**Mitigation:**
- Benchmark before deployment
- Implement caching if needed
- Monitor Langfuse traces for latency

**Contingency:**
- Optimize parsing (use pandas instead of regex)
- Cache parsed KPI files
- Parallel processing for multiple profiles

---

## PHASE 2 SUCCESS CRITERIA

### Quantitative Targets

| Metric | After Phase 1 | Phase 2 Target | Measurement |
|--------|---------------|----------------|-------------|
| Overall Quality | 6.0/10 | **8.0/10** | Validation rubric |
| KPI Accuracy | 85% | **95%+** | Manual review |
| KPI Count | 4-6 | **3-5** | Automated count |
| Token Usage (KPI) | 2-4K | **200-500** | Langfuse traces |
| Parsing Success | N/A | **95%+** | Error logs |
| Position Match Accuracy | N/A | **90%+** | Match confidence logs |

### Acceptance Criteria

**Technical:**
- ✅ All 9 KPI files parse correctly
- ✅ Position matching ≥90% accuracy
- ✅ KPI filtering works for all departments
- ✅ 95%+ unit test coverage
- ✅ Integration tests passing
- ✅ Performance overhead <100ms

**Quality:**
- ✅ Generate 10 test profiles → all have 3-5 KPIs
- ✅ Manual review: 95% of KPIs are correct
- ✅ No profiles with 7+ KPIs (was common before)
- ✅ Token usage reduced 60-80%

**Operational:**
- ✅ Fallback to unfiltered works
- ✅ Error logging comprehensive
- ✅ Documentation updated
- ✅ Code review approved

---

## ROLLBACK PLAN

**If Phase 2 has critical issues:**

**Option 1: Feature Flag Disable**
```python
# In data_loader.py
USE_KPI_FILTERING = os.getenv('ENABLE_KPI_FILTERING', 'false') == 'true'

if USE_KPI_FILTERING:
    kpi_content = self.kpi_mapper.load_kpi_content_for_position(...)
else:
    kpi_content = self.kpi_mapper.load_kpi_content(department)  # Old way
```

**Option 2: Code Revert**
```bash
git revert <phase-2-commit-hash>
docker-compose restart
```

**Impact of Rollback:**
- System reverts to Phase 1 quality (6.0/10)
- Phase 1 improvements retained
- Zero downtime

**Decision Criteria for Rollback:**
- >10% parsing failures
- >20% wrong position matches
- Performance degradation >200ms
- Client reports worse quality than Phase 1

---

## DELIVERABLES

### Code Files

1. **Modified:** `/home/yan/A101/HR/backend/core/data_mapper.py`
   - +300 lines (6 new methods)

2. **Modified:** `/home/yan/A101/HR/backend/core/data_loader.py`
   - +10 lines (modify line 69 + fallback)

3. **New:** `/home/yan/A101/HR/tests/unit/test_kpi_mapper_filtering.py`
   - ~150 lines (unit tests)

4. **New:** `/home/yan/A101/HR/tests/integration/test_profile_generation_with_filtering.py`
   - ~100 lines (integration tests)

5. **Modified:** `/home/yan/A101/HR/requirements.txt`
   - +2 lines (thefuzz, python-Levenshtein)

### Documentation

6. **Updated:** `/home/yan/A101/HR/docs/SYSTEM_ARCHITECTURE.md`
   - Add KPI filtering architecture section

7. **Updated:** `/home/yan/A101/HR/docs/API_REFERENCE.md`
   - Document new internal methods (if applicable)

8. **Updated:** `/home/yan/A101/HR/README.md`
   - Update with Phase 2 features

---

## NEXT: PART 4 - PHASE 3 & SUMMARY

Continue to [IMPLEMENTATION_PLAN_PART4_PHASE3.md](IMPLEMENTATION_PLAN_PART4_PHASE3.md) for:
- Phase 3: Validation & Deployment (Week 4)
- Client review process
- Production deployment plan
- Success metrics & monitoring
- Final recommendations

---

**Status:** ✅ Part 3 (Phase 2) Complete
**Effort Estimate:** 5-7 days (Weeks 2-3)
**Expected Quality:** 6.0/10 → 8.0/10 (+33%)
**Risk Level:** MEDIUM (mitigated with fallbacks)

Captain, Phase 2 backend filtering план готов! Detailed spec уже существует в KPI_FILTERING_IMPLEMENTATION_SPEC.md. Продолжаем? 🫡

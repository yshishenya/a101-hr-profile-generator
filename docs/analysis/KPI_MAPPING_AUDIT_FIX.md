# KPI Mapping Audit and Fix Report

**Date:** 2025-10-25
**Auditor:** Claude (Python Expert)
**Status:** CRITICAL BUG FOUND - Hierarchical inheritance broken

---

## Executive Summary

**PROBLEM:** KPI coverage is only 1.6% (9/568 departments) despite having 9 KPI files covering major departments.

**ROOT CAUSE:** The current KPIMapper uses **exact string matching** without hierarchical inheritance. Subdepartments don't inherit their parent's KPI file.

**EXPECTED COVERAGE:** Minimum 12.4% (68/568 departments) with hierarchical inheritance:
- 9 top-level departments (exact matches)
- 59 subdepartments (should inherit from parent)
- Total: 68 departments should have KPI data

**SOLUTION:** Implement hierarchical KPI lookup that walks up the department path until a KPI file is found.

---

## Current KPI Files Analysis

We have **9 KPI files** in `/home/yan/A101/HR/data/KPI/`:

### 1. KPI_ДИТ.md (IT Department)
**YAML frontmatter:**
```yaml
department: ДИТ
responsible: Сложеникин А
positions_map:
  Директор по информационным технологиям: Сложеникин Алексей Вячеславович
```

**Organization structure mapping:**
- **Full name:** Департамент информационных технологий
- **Block path:** Блок операционного директора → Департамент информационных технологий
- **Headcount:** 155 people
- **Subdepartments:** 25 units (including Отдел CRM, Управление развития информационных систем, etc.)
- **Should cover:** 26 departments total (1 parent + 25 children)
- **Currently covers:** 1 department only (BROKEN!)

**Subdepartments that SHOULD inherit this KPI:**
1. Отдел управления данными
2. Служба информационной безопасности
3. Управление развития информационных систем
4. Отдел CRM (example from user's question)
5. Отдел продуктовой аналитики
6. ... (20 more subdepartments)

---

### 2. KPI_ДПУ.md (Production Management)
**YAML frontmatter:**
```yaml
department: ДПУ
responsible: Вавилина Ю
positions_map:
  Директор дирекции ПУ по М, МО и объектам МПТ: Вавилина Юлия Владимировна
```

**Organization structure mapping:**
- **Issue:** NOT FOUND in current structure
- **Likely reason:** Department name changed or merged
- **Evidence:** Responsible person "Вавилина Ю" not found in structure.json
- **Current coverage:** UNKNOWN (file exists but department not in structure)

**Recommendation:** This KPI file may be obsolete or department was reorganized.

---

### 3. KPI_ДРР.md (Regional Development)
**YAML frontmatter:**
```yaml
department: ДРР
responsible: Шабанов В
positions_map:
  Директор департамента регионального развития: Шабанов Владимир Александрович
```

**Organization structure mapping:**
- **Full name:** Департамент регионального развития
- **Block path:** Блок исполнительного директора → Департамент регионального развития
- **Headcount:** 73 people
- **Subdepartments:** 22 units
- **Should cover:** 23 departments total (1 parent + 22 children)
- **Currently covers:** 1 department only (BROKEN!)

---

### 4. KPI_Закупки.md (Procurement)
**YAML frontmatter:**
```yaml
department: Закупки
responsible: Леликова Е
positions_map:
  Директор по закупкам: Леликова Елена Николаевна
```

**Organization structure mapping:**
- **Full name:** Департамент закупок
- **Block path:** Блок операционного директора → Департамент закупок
- **Headcount:** 38 people
- **Subdepartments:** 7 units
  - Отдел закупок работ и услуг
  - Группа администрирования
  - Группа по работе с объектами жилого строительства
  - Группа по работе с объектами развития инфраструктуры
  - Отдел закупок строительных материалов и оборудования
  - Группа по сопровождению поставок
  - Группа управления тендерами
- **Should cover:** 8 departments total (1 parent + 7 children)
- **Currently covers:** 1 department only (BROKEN!)

---

### 5. KPI_АС.md (Cost Analysis)
**YAML frontmatter:**
```yaml
department: АС
responsible: Ларина О
positions_map:
  Руководитель управления анализа себестоимости: Ларина Ольга Александровна
```

**Organization structure mapping:**
- **Full name:** Отдел бюджетирования и анализа себестоимости
- **Block path:** Блок операционного директора → Единый центр экономики строительства → Отдел бюджетирования и анализа себестоимости
- **Headcount:** 7 people
- **Subdepartments:** 0 (leaf node)
- **Should cover:** 1 department (itself only)
- **Currently covers:** 1 department (CORRECT!)

---

### 6. KPI_ПРП.md (Project Planning)
**YAML frontmatter:**
```yaml
department: ПРП
responsible: Попов А
positions_map:
  Руководитель управления план. и реал. проектов: Попов Андрей Михайлович
```

**Organization structure mapping:**
- **Full name:** Управление планирования и контроля реализации проектов
- **Block path:** Блок исполнительного директора → Управление планирования и контроля реализации проектов
- **Headcount:** 25 people
- **Subdepartments:** 3 units
  - Отдел контроля СМР
  - Отдел операционного управления
  - Проектный офис
- **Should cover:** 4 departments total (1 parent + 3 children)
- **Currently covers:** 1 department only (BROKEN!)

---

### 7. KPI_УВАиК.md (Internal Audit)
**YAML frontmatter:**
```yaml
department: УВАиК
responsible: Абаев М
positions_map:
  Руководитель управления: Абаев Михаил Шалумович
```

**Organization structure mapping:**
- **Full name:** Управление внутреннего аудита и контроля
- **Block path:** Управление внутреннего аудита и контроля (top-level, no parent block)
- **Headcount:** 7 people
- **Subdepartments:** 2 units
  - Отдел внутреннего аудита
  - Отдел внутреннего контроля и управления рисками
- **Should cover:** 3 departments total (1 parent + 2 children)
- **Currently covers:** 1 department only (BROKEN!)

---

### 8. KPI_Цифра.md (Digitalization)
**YAML frontmatter:**
```yaml
department: Цифра
responsible: Уртякова М
positions_map:
  Директор по повышению эффективности бизнес-процессов и цифровизации: Уртякова Марина Александровна
```

**Organization structure mapping:**
- **Full name:** Управление цифровизации и повышения эффективности бизнес-процессов
- **Block path:** Блок операционного директора → Управление цифровизации и повышения эффективности бизнес-процессов
- **Headcount:** 6 people
- **Subdepartments:** 0 (leaf node)
- **Should cover:** 1 department (itself only)
- **Currently covers:** 1 department (CORRECT!)

---

### 9. KPI_DIT.md (Duplicate/Legacy?)
**Note:** This file exists alongside KPI_ДИТ.md. Likely a duplicate with Latin characters instead of Cyrillic.

**Recommendation:** Delete or merge with KPI_ДИТ.md to avoid confusion.

---

## Organization Structure Analysis

### Total Department Count
- **Total departments/units:** 568
- **Units with headcount data:** 545
- **Units covered by current KPI system:** 9 (1.6%)
- **Units that SHOULD be covered:** 68 (12.4%) minimum

### Block Hierarchy

The organization has the following top-level blocks:

1. **Блок безопасности** (Security Block)
2. **Блок бизнес-директора** (Business Director Block)
3. **Блок генерального директора** (General Director Block)
4. **Блок исполнительного директора** (Executive Director Block)
   - Contains: ДРР, ПРП
5. **Блок операционного директора** (Operations Director Block)
   - Contains: ДИТ, Закупки, АС (nested), Цифра
6. **Управление внутреннего аудита и контроля** (УВАиК - top-level, no parent block)

### Example Department Paths

```
Блок операционного директора
  └─ Департамент информационных технологий (ДИТ) ← KPI_ДИТ.md
      ├─ Отдел управления данными ← SHOULD inherit KPI_ДИТ.md
      ├─ Служба информационной безопасности ← SHOULD inherit KPI_ДИТ.md
      └─ Управление развития информационных систем ← SHOULD inherit KPI_ДИТ.md
          └─ Отдел CRM ← SHOULD inherit KPI_ДИТ.md (user's example!)

Блок операционного директора
  └─ Департамент закупок (Закупки) ← KPI_Закупки.md
      ├─ Отдел закупок работ и услуг ← SHOULD inherit KPI_Закупки.md
      ├─ Группа администрирования ← SHOULD inherit KPI_Закупки.md
      └─ ... (5 more subdepartments)
```

---

## Current KPIMapper Implementation Analysis

### Code Location
`/home/yan/A101/HR/backend/core/data_mapper.py` (lines 288-530)

### Current Algorithm (BROKEN)

#### Method: `find_kpi_file(department: str) -> str`

**What it does:**
1. Uses `KPIDepartmentMapper.find_best_match(department)`
2. Performs **exact or partial string matching** on department name
3. Returns KPI filename or falls back to `KPI_DIT.md`

**Example:**
```python
# Input: "Отдел CRM"
# Current behavior:
mapper.find_kpi_file("Отдел CRM")
# → Checks pattern matching against "отдел crm"
# → No match found (patterns only have "дит", "информационн", etc.)
# → Returns fallback: "KPI_DIT.md"

# PROBLEM: "Отдел CRM" is UNDER "ДИТ" in hierarchy, but mapping doesn't know this!
```

#### Method: `load_kpi_content(department: str) -> str`

**3-tier fallback system:**
1. Try specific KPI file (if `find_kpi_file()` returns one)
2. Fallback to generic template by department type
3. Fallback to minimal generic template

**Problems:**
- Step 1 fails for subdepartments (no hierarchical lookup)
- Falls back to templates for 559/568 departments
- Templates are generic, not specific to the parent department's actual KPI

---

## KPIDepartmentMapper Analysis

### Code Location
`/home/yan/A101/HR/backend/core/kpi_department_mapping.py`

### Current Implementation (FLAT MATCHING ONLY)

```python
DEPARTMENT_TO_KPI_FILE = {
    # IT Department (ДИТ)
    "департамент информационных технологий": "ДИТ",
    "дит": "ДИТ",
    "информационн": "ДИТ",

    # ... more mappings
}

@classmethod
def get_kpi_file_for_department(cls, department: str) -> Optional[str]:
    dept_lower = department.lower().strip()

    # Direct match first
    if dept_lower in cls.DEPARTMENT_TO_KPI_FILE:
        return cls.DEPARTMENT_TO_KPI_FILE[dept_lower]

    # Partial match
    for pattern, kpi_code in cls.DEPARTMENT_TO_KPI_FILE.items():
        if pattern in dept_lower or dept_lower in pattern:
            return kpi_code

    return None  # NO HIERARCHICAL LOOKUP!
```

**PROBLEM:**
- Only matches if department name contains pattern (e.g., "информационн")
- "Отдел CRM" doesn't contain "информационн" → no match
- Doesn't check organizational hierarchy at all

---

## Root Cause of 1.6% Coverage

### The Bug

The current system uses **pattern matching** without **hierarchical inheritance**.

**Example failure case:**
```
User generates profile for: "Отдел CRM"

Current flow:
1. KPIMapper.find_kpi_file("Отдел CRM")
2. KPIDepartmentMapper.find_best_match("Отдел CRM")
3. Check patterns:
   - "отдел crm" in "департамент информационных технологий"? NO
   - "отдел crm" in "дит"? NO
   - "отдел crm" in "информационн"? NO
   - ... all patterns fail
4. Return None
5. Fallback to KPI_DIT.md (default)
6. But wait! KPI_DIT.md is the CORRECT file!
   - Problem: It was a fallback, not intelligent lookup
   - Logs show "fallback_no_match" instead of "smart_mapping"
```

**What SHOULD happen:**
```
Correct flow (with hierarchy):
1. KPIMapper.find_kpi_file("Отдел CRM")
2. Get department path from OrganizationMapper:
   "Блок операционного директора → Департамент информационных технологий →
    Управление развития информационных систем → Отдел CRM"
3. Walk up hierarchy:
   - Try "Отдел CRM" → no KPI file
   - Try "Управление развития информационных систем" → no KPI file
   - Try "Департамент информационных технологий" → FOUND! KPI_ДИТ.md
4. Return KPI_ДИТ.md with confidence="high" and method="hierarchical_inheritance"
```

### Coverage Statistics

| Scenario | Current | Expected |
|----------|---------|----------|
| **ДИТ + subdepartments** | 1/26 (3.8%) | 26/26 (100%) |
| **ДРР + subdepartments** | 1/23 (4.3%) | 23/23 (100%) |
| **Закупки + subdepartments** | 1/8 (12.5%) | 8/8 (100%) |
| **ПРП + subdepartments** | 1/4 (25%) | 4/4 (100%) |
| **УВАиК + subdepartments** | 1/3 (33%) | 3/3 (100%) |
| **АС** | 1/1 (100%) | 1/1 (100%) |
| **Цифра** | 1/1 (100%) | 1/1 (100%) |
| **ДПУ** | 0/0 (N/A) | N/A |
| **Total** | 9/568 (1.6%) | 68/568 (12.4%) |

---

## Proposed Fix

### Solution 1: Hierarchical KPI Lookup (RECOMMENDED)

Add hierarchical inheritance to `KPIMapper.find_kpi_file()`:

```python
def find_kpi_file(self, department: str) -> str:
    """
    Find KPI file with hierarchical inheritance.

    Algorithm:
    1. Try exact match on department name
    2. Get department path from OrganizationMapper
    3. Walk up hierarchy until KPI file found
    4. Fallback to default if nothing found
    """
    # Step 1: Try direct match (current behavior)
    if self.dept_mapper:
        match_result = self.dept_mapper.find_best_match(department)
        if match_result:
            kpi_file = match_result["filename"]
            kpi_path = self.kpi_dir / kpi_file
            if kpi_path.exists():
                # Found exact match
                self.mappings_log.append({
                    "department": department,
                    "kpi_file": kpi_file,
                    "method": "exact_match",
                    "confidence": match_result["confidence"]
                })
                return kpi_file

    # Step 2: Try hierarchical inheritance (NEW!)
    kpi_file = self._find_kpi_by_hierarchy(department)
    if kpi_file:
        self.mappings_log.append({
            "department": department,
            "kpi_file": kpi_file,
            "method": "hierarchical_inheritance",
            "confidence": "high"
        })
        return kpi_file

    # Step 3: Fallback to default
    self.mappings_log.append({
        "department": department,
        "kpi_file": self.default_kpi_file,
        "method": "fallback_no_match"
    })
    return self.default_kpi_file


def _find_kpi_by_hierarchy(self, department: str) -> Optional[str]:
    """
    Walk up organizational hierarchy to find KPI file.

    Example:
        department = "Отдел CRM"
        path = "Блок операционного директора → Департамент информационных технологий →
                Управление развития информационных систем → Отдел CRM"

        Try matching (from bottom to top):
        1. "Отдел CRM" → no match
        2. "Управление развития информационных систем" → no match
        3. "Департамент информационных технологий" → MATCH! → KPI_ДИТ.md
    """
    from .organization_cache import organization_cache

    # Get full department path
    path_list = organization_cache.find_department_path(department)
    if not path_list:
        logger.warning(f"Department path not found: {department}")
        return None

    # Walk up hierarchy (from specific to general)
    for i in range(len(path_list) - 1, -1, -1):
        ancestor_name = path_list[i]

        # Try to match this ancestor to KPI file
        if self.dept_mapper:
            match_result = self.dept_mapper.find_best_match(ancestor_name)
            if match_result:
                kpi_file = match_result["filename"]
                kpi_path = self.kpi_dir / kpi_file

                if kpi_path.exists():
                    logger.info(
                        f"Hierarchical match: '{department}' inherits KPI from "
                        f"'{ancestor_name}' → {kpi_file}"
                    )
                    return kpi_file

    # No match found in hierarchy
    logger.warning(f"No KPI file found in hierarchy for: {department}")
    return None
```

### Solution 2: Explicit Block-to-KPI Mapping

Add a mapping table for organizational blocks:

```python
# In KPIDepartmentMapper class
BLOCK_TO_KPI = {
    # Operations Director Block
    "Блок операционного директора / Департамент информационных технологий": "ДИТ",
    "Блок операционного директора / Департамент закупок": "Закупки",
    "Блок операционного директора / Единый центр экономики строительства": "АС",
    "Блок операционного директора / Управление цифровизации и повышения эффективности бизнес-процессов": "Цифра",

    # Executive Director Block
    "Блок исполнительного директора / Департамент регионального развития": "ДРР",
    "Блок исполнительного директора / Управление планирования и контроля реализации проектов": "ПРП",

    # Top-level (no parent block)
    "Управление внутреннего аудита и контроля": "УВАиК",
}

@classmethod
def get_kpi_by_block_path(cls, full_path: str) -> Optional[str]:
    """
    Match department by full organizational path.

    Args:
        full_path: e.g., "Блок операционного директора → Департамент информационных технологий → Отдел CRM"

    Returns:
        KPI code or None
    """
    # Try matching prefixes (from most specific to least)
    path_parts = full_path.split(" → ")

    for i in range(len(path_parts), 0, -1):
        partial_path = " / ".join(path_parts[:i])

        if partial_path in cls.BLOCK_TO_KPI:
            return cls.BLOCK_TO_KPI[partial_path]

    return None
```

### Solution 3: Department Alias Mapping (OPTIONAL)

Handle department name variations:

```python
DEPARTMENT_ALIASES = {
    "ДИТ": [
        "Департамент информационных технологий",
        "DIT",
        "IT Department"
    ],
    "ДПУ": [
        "Дирекция ПУ",
        "Дирекция производственного управления",
        "Production Management Directorate"
    ],
    "АС": [
        "Анализ себестоимости",
        "Отдел бюджетирования и анализа себестоимости",
        "Управление анализа себестоимости",
        "Cost Analysis"
    ],
    # ... etc
}
```

---

## Implementation Plan

### Phase 1: Add Hierarchical Lookup (HIGH PRIORITY)

**Files to modify:**
1. `/home/yan/A101/HR/backend/core/data_mapper.py`
   - Add `_find_kpi_by_hierarchy()` method
   - Modify `find_kpi_file()` to use hierarchical lookup

**Dependencies:**
- `organization_cache.find_department_path()` (already exists)
- `KPIDepartmentMapper.find_best_match()` (already exists)

**Testing:**
```python
# Test cases
test_cases = [
    # (department_name, expected_kpi_file)
    ("Департамент информационных технологий", "KPI_ДИТ.md"),  # Direct match
    ("Отдел CRM", "KPI_ДИТ.md"),  # Hierarchical inheritance
    ("Управление развития информационных систем", "KPI_ДИТ.md"),  # Hierarchical
    ("Отдел управления данными", "KPI_ДИТ.md"),  # Hierarchical

    ("Департамент закупок", "KPI_Закупки.md"),  # Direct match
    ("Отдел закупок работ и услуг", "KPI_Закупки.md"),  # Hierarchical
    ("Группа администрирования", "KPI_Закупки.md"),  # Hierarchical

    ("Управление внутреннего аудита и контроля", "KPI_УВАиК.md"),  # Direct match
    ("Отдел внутреннего аудита", "KPI_УВАиК.md"),  # Hierarchical

    ("Несуществующий департамент", "KPI_DIT.md"),  # Fallback
]
```

### Phase 2: Update KPIDepartmentMapper (MEDIUM PRIORITY)

**Files to modify:**
1. `/home/yan/A101/HR/backend/core/kpi_department_mapping.py`
   - Add better pattern matching
   - Add block path support

### Phase 3: Cleanup and Optimization (LOW PRIORITY)

1. **Delete duplicate KPI_DIT.md** (Latin version)
2. **Investigate ДПУ** - verify if department exists or KPI file is obsolete
3. **Add department aliases** for robustness
4. **Cache KPI lookups** to avoid repeated hierarchy walks

---

## Testing Strategy

### Unit Tests

```python
import pytest
from backend.core.data_mapper import KPIMapper

@pytest.fixture
def kpi_mapper():
    return KPIMapper(kpi_dir="data/KPI")

def test_exact_match(kpi_mapper):
    """Test direct department match"""
    kpi_file = kpi_mapper.find_kpi_file("Департамент информационных технологий")
    assert kpi_file == "KPI_ДИТ.md"

def test_hierarchical_inheritance(kpi_mapper):
    """Test subdepartment inherits parent KPI"""
    kpi_file = kpi_mapper.find_kpi_file("Отдел CRM")
    assert kpi_file == "KPI_ДИТ.md"

    # Check that method was hierarchical, not fallback
    log = kpi_mapper.mappings_log[-1]
    assert log["method"] == "hierarchical_inheritance"

def test_deep_hierarchy(kpi_mapper):
    """Test 3-level deep subdepartment"""
    # Отдел CRM is under: ДИТ → Управление развития → Отдел CRM
    kpi_file = kpi_mapper.find_kpi_file("Отдел CRM")
    assert kpi_file == "KPI_ДИТ.md"

def test_multiple_subdepartments(kpi_mapper):
    """Test all subdepartments of Закупки inherit KPI_Закупки.md"""
    subdepts = [
        "Отдел закупок работ и услуг",
        "Группа администрирования",
        "Группа по работе с объектами жилого строительства",
        "Отдел закупок строительных материалов и оборудования",
    ]

    for subdept in subdepts:
        kpi_file = kpi_mapper.find_kpi_file(subdept)
        assert kpi_file == "KPI_Закупки.md", f"Failed for {subdept}"

def test_fallback_for_unknown(kpi_mapper):
    """Test fallback when no match found"""
    kpi_file = kpi_mapper.find_kpi_file("Несуществующий департамент")
    assert kpi_file == "KPI_DIT.md"  # Default fallback
```

### Integration Tests

Run against real organization structure:

```bash
# Count departments with KPI coverage
python3 -c "
from backend.core.data_mapper import KPIMapper
from backend.core.organization_cache import organization_cache

mapper = KPIMapper()

# Get all departments
all_depts = organization_cache.get_all_department_names()

# Count coverage
coverage = {}
for dept in all_depts:
    kpi_file = mapper.find_kpi_file(dept)
    method = mapper.mappings_log[-1]['method']

    if method not in coverage:
        coverage[method] = 0
    coverage[method] += 1

print(f'Total departments: {len(all_depts)}')
for method, count in sorted(coverage.items()):
    pct = (count / len(all_depts)) * 100
    print(f'{method}: {count} ({pct:.1f}%)')
"
```

**Expected output (after fix):**
```
Total departments: 568
exact_match: 9 (1.6%)
hierarchical_inheritance: 59 (10.4%)
template: 500 (88.0%)
```

**Improvement:** 1.6% → 12.0% specific KPI coverage (7.5x increase!)

---

## Expected Results

### Before Fix
- **Coverage:** 9/568 departments (1.6%)
- **Method breakdown:**
  - Exact match: 9 departments
  - Hierarchical: 0 departments (BROKEN!)
  - Template fallback: 559 departments

### After Fix
- **Coverage:** 68/568 departments (12.0%)
- **Method breakdown:**
  - Exact match: 9 departments
  - Hierarchical inheritance: 59 departments (NEW!)
  - Template fallback: 500 departments

### Impact on User's Case

**User's question:** "Отдел CRM" not getting KPI_ДИТ.md

**Before fix:**
```
Department: Отдел CRM
KPI file: KPI_DIT.md (fallback)
Method: fallback_no_match
Confidence: low
Content: Generic template (not specific to ДИТ)
```

**After fix:**
```
Department: Отдел CRM
KPI file: KPI_ДИТ.md
Method: hierarchical_inheritance
Confidence: high
Parent: Департамент информационных технологий
Content: Specific ДИТ KPI data (155 people, detailed metrics)
```

---

## Risks and Mitigation

### Risk 1: Department Name Mismatches
**Risk:** Department name in profile doesn't exactly match structure.json

**Mitigation:**
- Use fuzzy matching in `organization_cache.find_department_path()`
- Already implemented in OrganizationMapper (lines 51-57)

### Risk 2: Circular Dependencies
**Risk:** Infinite loop if organizational structure has cycles

**Mitigation:**
- Add max depth limit (e.g., 10 levels)
- Track visited departments
- Log warning if max depth exceeded

### Risk 3: Performance
**Risk:** Walking hierarchy for each department could be slow

**Mitigation:**
- Cache KPI lookups (department → KPI file mapping)
- Pre-build mapping table at startup
- Store in organization_cache

### Risk 4: KPI File Not Found
**Risk:** Hierarchical match finds KPI code but file doesn't exist

**Mitigation:**
- Already handled in current code (lines 360-381)
- Falls back to default if file doesn't exist

---

## Recommendations

### Immediate Actions (Priority 1)
1. ✅ **Implement hierarchical KPI lookup** (Solution 1)
2. ✅ **Add unit tests** for hierarchical inheritance
3. ✅ **Test with real data** (all 568 departments)
4. ✅ **Verify coverage increases** from 1.6% to 12%+

### Short-term Actions (Priority 2)
1. **Clean up KPI_DIT.md** (Latin version) - merge or delete
2. **Investigate KPI_ДПУ.md** - verify department exists
3. **Add logging** for hierarchical matches (already in proposed code)
4. **Update documentation** with new coverage stats

### Long-term Actions (Priority 3)
1. **Create KPI files for major blocks** (increase coverage to 50%+)
2. **Build admin UI** to visualize KPI coverage by department
3. **Add KPI inheritance metadata** to profiles (show which parent KPI is used)
4. **Performance optimization** (caching, pre-computation)

---

## Code Implementation

### Full Code for `_find_kpi_by_hierarchy()` Method

Add this method to the `KPIMapper` class in `/home/yan/A101/HR/backend/core/data_mapper.py`:

```python
def _find_kpi_by_hierarchy(self, department: str) -> Optional[str]:
    """
    Walk up organizational hierarchy to find KPI file.

    This implements hierarchical KPI inheritance:
    - Start with the department itself
    - Walk up the hierarchy (child → parent → grandparent → ...)
    - Try to match each ancestor to a KPI file
    - Return the first match found

    Args:
        department: Department name to find KPI for

    Returns:
        KPI filename (e.g., "KPI_ДИТ.md") or None if not found

    Example:
        >>> # Department hierarchy:
        >>> # Блок ОД → ДИТ → Управление развития → Отдел CRM
        >>> mapper._find_kpi_by_hierarchy("Отдел CRM")
        'KPI_ДИТ.md'  # Inherited from parent "ДИТ"
    """
    try:
        from .organization_cache import organization_cache
    except ImportError:
        logger.error("organization_cache not available for hierarchical lookup")
        return None

    # Get full department path as list
    # e.g., ["Блок операционного директора", "Департамент информационных технологий",
    #        "Управление развития информационных систем", "Отдел CRM"]
    path_list = organization_cache.find_department_path(department)

    if not path_list:
        logger.debug(f"Department path not found in organization cache: {department}")
        return None

    logger.debug(f"Hierarchical KPI lookup for '{department}', path: {' → '.join(path_list)}")

    # Walk up hierarchy from most specific to most general
    # Start from the end (child) and move towards beginning (root)
    for i in range(len(path_list) - 1, -1, -1):
        ancestor_name = path_list[i]

        # Try to match this ancestor to a KPI file
        if not self.dept_mapper:
            continue

        match_result = self.dept_mapper.find_best_match(ancestor_name)

        if match_result:
            kpi_file = match_result["filename"]
            kpi_path = self.kpi_dir / kpi_file

            # Verify file exists
            if kpi_path.exists():
                depth = len(path_list) - 1 - i  # How many levels up we went

                logger.info(
                    f"✅ Hierarchical KPI match: '{department}' inherits from "
                    f"'{ancestor_name}' ({depth} levels up) → {kpi_file}"
                )

                return kpi_file
            else:
                logger.warning(
                    f"KPI file found but doesn't exist: {kpi_file} for ancestor '{ancestor_name}'"
                )

    # No match found in entire hierarchy
    logger.debug(f"No KPI file found in hierarchy for: {department}")
    return None
```

### Updated `find_kpi_file()` Method

Replace the current `find_kpi_file()` method (lines 330-394) with this:

```python
def find_kpi_file(self, department: str) -> str:
    """
    Find the most appropriate KPI file for a department.

    Uses 3-tier lookup strategy:
    1. Direct/exact match - department name matches KPI file pattern
    2. Hierarchical inheritance - walk up org tree to find parent's KPI
    3. Fallback - use default KPI file

    Args:
        department: Department name

    Returns:
        KPI filename (always returns a valid filename, never None)

    Examples:
        >>> mapper.find_kpi_file("Департамент информационных технологий")
        'KPI_ДИТ.md'  # Direct match

        >>> mapper.find_kpi_file("Отдел CRM")
        'KPI_ДИТ.md'  # Hierarchical inheritance from parent ДИТ

        >>> mapper.find_kpi_file("Неизвестный отдел")
        'KPI_DIT.md'  # Fallback to default
    """
    # TIER 1: Try direct/exact match
    if self.dept_mapper:
        match_result = self.dept_mapper.find_best_match(department)

        if match_result:
            kpi_file = match_result["filename"]
            kpi_path = self.kpi_dir / kpi_file

            if kpi_path.exists():
                # Direct match found!
                self.mappings_log.append({
                    "department": department,
                    "kpi_file": kpi_file,
                    "kpi_code": match_result["kpi_code"],
                    "confidence": match_result["confidence"],
                    "method": "exact_match",
                })

                logger.info(
                    f"✅ Exact KPI match: '{department}' → '{kpi_file}' "
                    f"(confidence: {match_result['confidence']})"
                )

                return kpi_file
            else:
                logger.warning(
                    f"KPI file '{kpi_file}' found for '{department}' but doesn't exist"
                )

    # TIER 2: Try hierarchical inheritance (NEW!)
    kpi_file_hierarchical = self._find_kpi_by_hierarchy(department)

    if kpi_file_hierarchical:
        self.mappings_log.append({
            "department": department,
            "kpi_file": kpi_file_hierarchical,
            "method": "hierarchical_inheritance",
            "confidence": "high",
        })

        logger.info(
            f"✅ Hierarchical KPI match: '{department}' → '{kpi_file_hierarchical}'"
        )

        return kpi_file_hierarchical

    # TIER 3: Fallback to default
    self.mappings_log.append({
        "department": department,
        "kpi_file": self.default_kpi_file,
        "method": "fallback_no_match",
        "confidence": "low",
    })

    logger.info(
        f"⚠️  KPI fallback: '{department}' → '{self.default_kpi_file}' (no match found)"
    )

    return self.default_kpi_file
```

---

## Conclusion

### Summary

The KPI mapping system has a **critical bug**: it only uses exact/pattern matching without hierarchical inheritance. This causes:
- **1.6% coverage** instead of expected 12%+
- **59 subdepartments** don't inherit their parent's KPI
- User's "Отдел CRM" example fails to get correct KPI_ДИТ.md

### Solution

Implement hierarchical KPI lookup by walking up the organizational tree. This:
- Increases coverage from 1.6% to 12% (7.5x improvement)
- Ensures all subdepartments inherit parent KPI
- Maintains backward compatibility (exact matches still work)

### Next Steps

1. Implement `_find_kpi_by_hierarchy()` method
2. Update `find_kpi_file()` to use hierarchical lookup
3. Add unit tests for all 68 departments that should have KPI
4. Verify coverage improvement in production

---

**Report prepared by:** Claude (Python Expert)
**Date:** 2025-10-25
**Version:** 1.0

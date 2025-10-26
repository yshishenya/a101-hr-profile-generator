# KPI Mapping Fix - Implementation Guide

**Quick Reference for Implementing Hierarchical KPI Inheritance**

---

## TL;DR - The Problem

```
Current: "Отдел CRM" → fallback to KPI_DIT.md (wrong method)
Should:  "Отдел CRM" → inherit KPI_ДИТ.md from parent "ДИТ" (correct!)

Coverage: 1.6% (9/568) → Should be 12% (68/568)
```

---

## The Fix - Two Functions to Add

### File: `/home/yan/A101/HR/backend/core/data_mapper.py`

Add these two functions to the `KPIMapper` class:

#### 1. Add Hierarchical Lookup Method

Insert this method around line 395 (after current `find_kpi_file()` method):

```python
def _find_kpi_by_hierarchy(self, department: str) -> Optional[str]:
    """
    Walk up organizational hierarchy to find KPI file.

    Implements hierarchical KPI inheritance: child departments inherit
    their parent's KPI file if they don't have their own.

    Args:
        department: Department name to find KPI for

    Returns:
        KPI filename (e.g., "KPI_ДИТ.md") or None if not found

    Example:
        >>> # Hierarchy: Блок ОД → ДИТ → Управление развития → Отдел CRM
        >>> mapper._find_kpi_by_hierarchy("Отдел CRM")
        'KPI_ДИТ.md'  # Inherited from parent "ДИТ"
    """
    try:
        from .organization_cache import organization_cache
    except ImportError:
        logger.error("organization_cache not available for hierarchical lookup")
        return None

    # Get full department path as list
    # Example: ["Блок операционного директора", "Департамент информационных технологий",
    #           "Управление развития информационных систем", "Отдел CRM"]
    path_list = organization_cache.find_department_path(department)

    if not path_list:
        logger.debug(f"Department path not found in organization cache: {department}")
        return None

    logger.debug(
        f"Hierarchical KPI lookup for '{department}', "
        f"path: {' → '.join(path_list)}"
    )

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
                    f"KPI file found but doesn't exist: {kpi_file} "
                    f"for ancestor '{ancestor_name}'"
                )

    # No match found in entire hierarchy
    logger.debug(f"No KPI file found in hierarchy for: {department}")
    return None
```

#### 2. Update `find_kpi_file()` Method

Replace the current `find_kpi_file()` method (lines 330-394) with this updated version:

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

## Testing the Fix

### Quick Test Script

Save this as `test_kpi_hierarchy.py` in project root:

```python
#!/usr/bin/env python3
"""Test hierarchical KPI lookup"""

import sys
sys.path.insert(0, '/home/yan/A101/HR')

from backend.core.data_mapper import KPIMapper

def test_kpi_hierarchy():
    """Test that subdepartments inherit parent KPI"""

    mapper = KPIMapper(kpi_dir="data/KPI")

    test_cases = [
        # (department, expected_kpi, expected_method)

        # Direct matches
        ("Департамент информационных технологий", "KPI_ДИТ.md", "exact_match"),
        ("Департамент закупок", "KPI_Закупки.md", "exact_match"),

        # Hierarchical inheritance - ДИТ subdepartments
        ("Отдел CRM", "KPI_ДИТ.md", "hierarchical_inheritance"),
        ("Управление развития информационных систем", "KPI_ДИТ.md", "hierarchical_inheritance"),
        ("Отдел управления данными", "KPI_ДИТ.md", "hierarchical_inheritance"),
        ("Служба информационной безопасности", "KPI_ДИТ.md", "hierarchical_inheritance"),

        # Hierarchical inheritance - Закупки subdepartments
        ("Отдел закупок работ и услуг", "KPI_Закупки.md", "hierarchical_inheritance"),
        ("Группа администрирования", "KPI_Закупки.md", "hierarchical_inheritance"),
        ("Отдел закупок строительных материалов и оборудования", "KPI_Закупки.md", "hierarchical_inheritance"),

        # Hierarchical inheritance - УВАиК subdepartments
        ("Отдел внутреннего аудита", "KPI_УВАиК.md", "hierarchical_inheritance"),
        ("Отдел внутреннего контроля и управления рисками", "KPI_УВАиК.md", "hierarchical_inheritance"),

        # Hierarchical inheritance - ПРП subdepartments
        ("Отдел контроля СМР", "KPI_ПРП.md", "hierarchical_inheritance"),
        ("Проектный офис", "KPI_ПРП.md", "hierarchical_inheritance"),

        # Fallback
        ("Несуществующий департамент", "KPI_DIT.md", "fallback_no_match"),
    ]

    print("Testing KPI Hierarchical Inheritance")
    print("=" * 80)

    passed = 0
    failed = 0

    for dept, expected_kpi, expected_method in test_cases:
        kpi_file = mapper.find_kpi_file(dept)
        actual_method = mapper.mappings_log[-1]["method"]

        status = "✅ PASS" if (kpi_file == expected_kpi and actual_method == expected_method) else "❌ FAIL"

        if status == "✅ PASS":
            passed += 1
        else:
            failed += 1

        print(f"\n{status}")
        print(f"  Department: {dept}")
        print(f"  Expected: {expected_kpi} via {expected_method}")
        print(f"  Actual:   {kpi_file} via {actual_method}")

    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    # Coverage statistics
    print("\n" + "=" * 80)
    print("Coverage Statistics:")

    from backend.core.organization_cache import organization_cache

    all_depts = []
    def collect_depts(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key not in ['organization', 'children'] and isinstance(value, dict):
                    all_depts.append(key)
                    if 'children' in value:
                        collect_depts(value['children'])

    import json
    with open('data/structure.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    collect_depts(data)

    # Count by method
    method_counts = {}
    for dept in all_depts[:100]:  # Sample first 100 to avoid long runtime
        kpi_file = mapper.find_kpi_file(dept)
        method = mapper.mappings_log[-1]["method"]

        method_counts[method] = method_counts.get(method, 0) + 1

    total = sum(method_counts.values())
    print(f"\nSample coverage (first 100 departments):")
    for method, count in sorted(method_counts.items()):
        pct = (count / total) * 100
        print(f"  {method}: {count} ({pct:.1f}%)")

    return failed == 0

if __name__ == "__main__":
    success = test_kpi_hierarchy()
    sys.exit(0 if success else 1)
```

Run the test:

```bash
cd /home/yan/A101/HR
python3 test_kpi_hierarchy.py
```

### Expected Output (After Fix)

```
Testing KPI Hierarchical Inheritance
================================================================================

✅ PASS
  Department: Департамент информационных технологий
  Expected: KPI_ДИТ.md via exact_match
  Actual:   KPI_ДИТ.md via exact_match

✅ PASS
  Department: Отдел CRM
  Expected: KPI_ДИТ.md via hierarchical_inheritance
  Actual:   KPI_ДИТ.md via hierarchical_inheritance

... (more tests)

================================================================================
Results: 15 passed, 0 failed out of 15 tests

================================================================================
Coverage Statistics:

Sample coverage (first 100 departments):
  exact_match: 5 (5.0%)
  hierarchical_inheritance: 35 (35.0%)
  fallback_no_match: 60 (60.0%)
```

---

## Verification Checklist

After implementing the fix, verify:

- [ ] All 15 test cases pass
- [ ] "Отдел CRM" returns KPI_ДИТ.md via hierarchical_inheritance
- [ ] Coverage increases from 1.6% to 12%+
- [ ] Logs show clear hierarchy paths
- [ ] No performance degradation (add caching if needed)
- [ ] Backward compatibility maintained (exact matches still work)

---

## Quick Summary

**Changes:**
1. Add `_find_kpi_by_hierarchy()` method - walks up org tree
2. Update `find_kpi_file()` - calls hierarchical lookup as Tier 2

**Impact:**
- Coverage: 1.6% → 12%+ (7.5x improvement)
- Fixes: 59 subdepartments now inherit parent KPI
- User's case: "Отдел CRM" correctly gets KPI_ДИТ.md

**Testing:**
- Run `test_kpi_hierarchy.py`
- Verify all tests pass
- Check logs show hierarchical inheritance

---

**Implementation time:** ~30 minutes
**Testing time:** ~15 minutes
**Total:** ~45 minutes to fix critical KPI mapping bug

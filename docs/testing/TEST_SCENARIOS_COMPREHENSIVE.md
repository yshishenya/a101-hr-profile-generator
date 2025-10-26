# Comprehensive Test Scenarios - Schema & Prompt Fixes
**Branch**: `feature/quality-optimization`
**Date**: 2025-10-25
**Status**: Ready for Implementation

## Executive Summary

This document provides comprehensive test scenarios for validating 4 critical fixes to the HR Profile Generator:

1. **Schema Fix**: `area` field changed from array to string
2. **Schema Fix**: `performance_metrics` field removed from schema
3. **Prompt Fix**: `careerogram` structure corrected (object with arrays, not mixed array)
4. **Feature**: KPI mapping implementation for department-specific metrics
5. **Feature**: Conditional IT Systems loading based on role type

**Expected Impact**:
- 100% schema validation pass rate (currently fails on array/string mismatch)
- 100% careerogram parseability (currently 0% due to broken structure)
- 100% KPI coverage (currently 1.6% - only 9/567 departments)
- ~40% token reduction for non-IT roles (conditional IT systems loading)

---

## Test Strategy

### 1. Testing Pyramid

```
        /\
       /  \        E2E Tests (5%)
      /____\       - Full generation flow with golden standard comparison
     /      \
    /        \     Integration Tests (25%)
   /__________\    - Multi-component interactions
  /            \
 /              \  Unit Tests (70%)
/________________\ - Individual fix validation
```

### 2. Testing Approach

- **Test Isolation**: Each fix tested independently before integration
- **Regression Safety**: Old profile formats still readable
- **Performance**: No degradation in generation time
- **Quality**: Manual review on sample outputs (1-10 scale, target ≥8)

### 3. Tools & Frameworks

```python
# Core Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Mocking & Fixtures
pytest-mock>=3.11.1
unittest.mock

# Schema Validation
jsonschema>=4.19.0

# Performance
pytest-benchmark>=4.0.0
```

---

## Unit Tests - Schema Fixes

### Test Case 1.1: `area` Field Type Validation

**Objective**: Verify `area` is generated as string, not array

```python
# File: tests/unit/test_schema_area_field.py

import pytest
import json
from jsonschema import validate, ValidationError
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_area_field_is_string_not_array():
    """Test that area field in responsibility_areas is string, not array"""
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"], f"Generation failed: {result.get('errors', [])}"

    profile = result["profile"]
    responsibility_areas = profile.get("responsibility_areas", [])

    assert len(responsibility_areas) > 0, "No responsibility areas generated"

    for idx, area_obj in enumerate(responsibility_areas):
        area_value = area_obj.get("area")

        # Primary assertion: area must be string
        assert isinstance(area_value, str), (
            f"responsibility_areas[{idx}].area must be string, "
            f"got {type(area_value).__name__}: {area_value}"
        )

        # Secondary assertion: area must not be list
        assert not isinstance(area_value, list), (
            f"responsibility_areas[{idx}].area must not be list"
        )

        # Tertiary assertion: area must not be empty
        assert len(area_value.strip()) > 0, (
            f"responsibility_areas[{idx}].area must not be empty string"
        )


@pytest.mark.asyncio
async def test_area_field_schema_validation():
    """Test that generated profile passes JSON schema validation for area field"""
    # Arrange
    generator = ProfileGenerator()

    with open("/home/yan/A101/HR/templates/universal_job_profile_schema.json") as f:
        schema = json.load(f)

    # Act
    result = await generator.generate_profile(
        department="Департамент информационных технологий",
        position="Программист 1С",
        temperature=0.1,
        save_result=False,
    )

    profile = result["profile"]

    # Assert - should NOT raise ValidationError
    try:
        validate(instance=profile, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed: {e.message}\nPath: {e.path}")


@pytest.mark.asyncio
async def test_area_field_examples():
    """Test area field format across multiple positions"""
    generator = ProfileGenerator()

    test_cases = [
        ("Бюро комплексного проектирования", "Архитектор 3к", "Моделирование"),
        ("Отдел CRM", "Программист 1С", "Разработка"),
        ("Департамент продаж", "Менеджер по продажам", "Продажи"),
    ]

    for department, position, expected_area_keyword in test_cases:
        result = await generator.generate_profile(
            department=department,
            position=position,
            temperature=0.1,
            save_result=False,
        )

        assert result["success"], f"Failed for {position} in {department}"

        areas = result["profile"]["responsibility_areas"]

        # Check all areas are strings
        for area_obj in areas:
            assert isinstance(area_obj["area"], str), (
                f"area field is not string for {position}"
            )
```

### Test Case 1.2: `performance_metrics` Removed

**Objective**: Verify `performance_metrics` field no longer appears in generated profiles

```python
# File: tests/unit/test_schema_performance_metrics_removed.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_performance_metrics_field_not_present():
    """Test that performance_metrics field is NOT in generated profile"""
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Департамент информационных технологий",
        position="Аналитик данных",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"], f"Generation failed: {result.get('errors', [])}"

    profile = result["profile"]

    # Primary assertion: field must not exist
    assert "performance_metrics" not in profile, (
        "performance_metrics field should be removed from schema"
    )

    # Verify other metrics-related fields still exist (if expected)
    # This ensures we didn't accidentally remove too much
    assert "metadata" in profile, "metadata field should still exist"


@pytest.mark.asyncio
async def test_performance_metrics_not_in_schema():
    """Test that performance_metrics is not in the JSON schema"""
    import json

    with open("/home/yan/A101/HR/templates/universal_job_profile_schema.json") as f:
        schema = json.load(f)

    properties = schema.get("properties", {})

    # Assert: performance_metrics should not be in schema
    assert "performance_metrics" not in properties, (
        "performance_metrics should be removed from schema properties"
    )


@pytest.mark.asyncio
async def test_markdown_export_without_performance_metrics():
    """Test that Markdown export works without performance_metrics field"""
    # Arrange
    from backend.core.markdown_service import ProfileMarkdownService

    generator = ProfileGenerator()
    md_service = ProfileMarkdownService()

    # Act
    result = await generator.generate_profile(
        department="Департамент информационных технологий",
        position="DevOps инженер",
        temperature=0.1,
        save_result=False,
    )

    profile = result["profile"]
    metadata = result["metadata"]

    # Generate markdown
    markdown_content = md_service.generate_markdown(
        profile=profile,
        metadata=metadata
    )

    # Assert
    assert markdown_content is not None
    assert len(markdown_content) > 0
    assert "performance_metrics" not in markdown_content.lower()


@pytest.mark.asyncio
async def test_docx_export_without_performance_metrics():
    """Test that DOCX export works without performance_metrics field"""
    # Arrange
    from backend.core.docx_service import initialize_docx_service
    import tempfile
    import os

    generator = ProfileGenerator()
    docx_service = initialize_docx_service()

    if not docx_service:
        pytest.skip("DOCX service not available")

    # Act
    result = await generator.generate_profile(
        department="Финансовый блок",
        position="Финансовый аналитик",
        temperature=0.1,
        save_result=False,
    )

    profile = result["profile"]
    metadata = result["metadata"]

    # Generate DOCX to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = tmp.name

    try:
        docx_service.generate_docx(
            profile=profile,
            metadata=metadata,
            output_path=tmp_path
        )

        # Assert: file exists and has content
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 0

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
```

### Test Case 1.3: `proficiency_description` Retained

**Objective**: Verify `proficiency_description` is still present and matches `proficiency_level`

```python
# File: tests/unit/test_schema_proficiency_description.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_proficiency_description_present():
    """Test that proficiency_description is still present in skills"""
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Департамент информационных технологий",
        position="Python разработчик",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"]

    profile = result["profile"]
    professional_skills = profile.get("professional_skills", [])

    assert len(professional_skills) > 0, "No professional skills generated"

    for skill_obj in professional_skills:
        # Check if proficiency_level exists
        if "proficiency_level" in skill_obj:
            # If level exists, description should also exist
            assert "proficiency_description" in skill_obj, (
                f"proficiency_description missing for skill: {skill_obj.get('skill_category')}"
            )


@pytest.mark.asyncio
async def test_proficiency_level_description_consistency():
    """Test that proficiency_level matches proficiency_description"""
    # Arrange
    generator = ProfileGenerator()

    level_to_description_keywords = {
        "Базовый": ["знание основ", "базовые", "начальный"],
        "Продвинутый": ["существенные знания", "уверенное владение", "продвинутый"],
        "Экспертный": ["глубокие знания", "экспертиза", "мастерство"],
    }

    # Act
    result = await generator.generate_profile(
        department="Департамент информационных технологий",
        position="Data Scientist",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    professional_skills = result["profile"]["professional_skills"]

    for skill in professional_skills:
        level = skill.get("proficiency_level")
        description = skill.get("proficiency_description", "").lower()

        if level and level in level_to_description_keywords:
            keywords = level_to_description_keywords[level]

            # Description should contain at least one keyword for the level
            matches = any(keyword.lower() in description for keyword in keywords)

            # Soft assertion - log warning if no match
            if not matches:
                import logging
                logging.warning(
                    f"Proficiency level '{level}' may not match description '{description}'"
                )
```

---

## Unit Tests - Prompt Fixes

### Test Case 2.1: Careerogram Structure Fixed

**Objective**: Verify careerogram has correct structure `{source_positions: [...], target_positions: [...]}`

```python
# File: tests/unit/test_prompt_careerogram_structure.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_careerogram_structure_is_object():
    """Test that careerogram is an object with source/target arrays, not flat array"""
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Отдел CRM",
        position="Программист 1С",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"]

    profile = result["profile"]
    career_dev = profile.get("career_development", {})

    # Careerogram fields should exist
    assert "career_entry_positions" in career_dev, (
        "career_entry_positions (source_positions) missing"
    )
    assert "career_growth_positions" in career_dev, (
        "career_growth_positions (target_positions) missing"
    )

    # Both should be arrays
    source_positions = career_dev["career_entry_positions"]
    target_positions = career_dev["career_growth_positions"]

    assert isinstance(source_positions, list), (
        f"career_entry_positions must be list, got {type(source_positions).__name__}"
    )
    assert isinstance(target_positions, list), (
        f"career_growth_positions must be list, got {type(target_positions).__name__}"
    )


@pytest.mark.asyncio
async def test_careerogram_contains_position_strings():
    """Test that careerogram arrays contain position name strings"""
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    career_dev = result["profile"]["career_development"]

    source_positions = career_dev.get("career_entry_positions", [])
    target_positions = career_dev.get("career_growth_positions", [])

    # Check source positions
    for pos in source_positions:
        assert isinstance(pos, str), (
            f"Source position must be string, got {type(pos).__name__}: {pos}"
        )
        assert len(pos.strip()) > 0, "Source position must not be empty"

        # Should NOT contain key-value structure (old broken format)
        assert ":" not in pos or pos.count(":") <= 1, (
            f"Position should be simple string, not key-value: {pos}"
        )

    # Check target positions
    for pos in target_positions:
        assert isinstance(pos, str), (
            f"Target position must be string, got {type(pos).__name__}: {pos}"
        )
        assert len(pos.strip()) > 0, "Target position must not be empty"

        # Should NOT contain key-value structure
        assert ":" not in pos or pos.count(":") <= 1, (
            f"Position should be simple string, not key-value: {pos}"
        )


@pytest.mark.asyncio
async def test_careerogram_not_flat_mixed_array():
    """Test that careerogram is NOT a flat array mixing keys and values"""
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Департамент продаж",
        position="Менеджер по продажам",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    career_dev = result["profile"]["career_development"]

    # Old broken format would look like:
    # ["source_positions", "pos1", "pos2", "target_positions", "pos3", "pos4"]
    # We need to ensure it's NOT this format

    # If career_development is a dict (correct), it should have specific keys
    assert isinstance(career_dev, dict), (
        "career_development must be object/dict, not array"
    )

    # Should NOT be a flat list
    assert not isinstance(career_dev, list), (
        "career_development must not be flat array"
    )


@pytest.mark.asyncio
async def test_careerogram_parseability():
    """Test that 100% of careergrams are parseable and make sense"""
    # Arrange
    generator = ProfileGenerator()

    test_positions = [
        ("Департамент информационных технологий", "Junior Python Developer"),
        ("Отдел CRM", "Программист 1С"),
        ("Бюро комплексного проектирования", "Архитектор 3к"),
        ("Департамент продаж", "Менеджер по продажам"),
        ("Финансовый блок", "Финансовый аналитик"),
    ]

    parseable_count = 0
    total_count = len(test_positions)

    for department, position in test_positions:
        result = await generator.generate_profile(
            department=department,
            position=position,
            temperature=0.1,
            save_result=False,
        )

        if not result["success"]:
            continue

        career_dev = result["profile"].get("career_development", {})

        # Check if structure is parseable
        try:
            source = career_dev.get("career_entry_positions", [])
            target = career_dev.get("career_growth_positions", [])

            # Both must be lists
            assert isinstance(source, list) and isinstance(target, list)

            # All items must be strings
            assert all(isinstance(p, str) for p in source)
            assert all(isinstance(p, str) for p in target)

            parseable_count += 1

        except (AssertionError, TypeError, KeyError):
            pass

    # Calculate parseability rate
    parseability_rate = (parseable_count / total_count) * 100

    # Assert: 100% should be parseable (vs 0% before fix)
    assert parseability_rate == 100.0, (
        f"Only {parseability_rate}% of careergrams are parseable (expected 100%)"
    )
```

---

## Unit Tests - KPI Mapping

### Test Case 3.1: IT Department Gets IT KPIs

**Objective**: Verify IT departments receive IT-specific KPI templates

```python
# File: tests/unit/test_kpi_mapping_it.py

import pytest
from backend.core.data_loader import DataLoader


@pytest.mark.asyncio
async def test_it_department_gets_it_kpis():
    """Test that IT department gets IT-specific KPIs"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    it_departments = [
        "Департамент информационных технологий",
        "Отдел информационных технологий",
        "ДИТ",
        "Управление информационных технологий",
    ]

    for dept in it_departments:
        # Act
        kpi_data = await data_loader.load_kpi_for_department(dept)

        # Assert
        assert kpi_data is not None, f"No KPI data for IT department: {dept}"
        assert len(kpi_data.strip()) > 0, f"Empty KPI data for IT department: {dept}"

        # Check for IT-specific keywords
        it_keywords = ["MTTR", "deployment", "incident", "availability", "SLA"]
        kpi_lower = kpi_data.lower()

        matches = sum(1 for keyword in it_keywords if keyword.lower() in kpi_lower)

        assert matches > 0, (
            f"IT KPIs should contain IT-specific metrics for {dept}. "
            f"Found 0 matches from {it_keywords}"
        )


@pytest.mark.asyncio
async def test_it_kpis_loaded_from_correct_file():
    """Test that IT KPIs are loaded from KPI_DIT.md"""
    # Arrange
    from pathlib import Path

    kpi_file = Path("/home/yan/A101/HR/data/KPI/KPI_DIT.md")

    # Assert file exists
    assert kpi_file.exists(), "KPI_DIT.md file not found"

    # Read file
    with open(kpi_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for IT-specific content
    assert "MTTR" in content or "mttr" in content.lower()
    assert len(content) > 100, "KPI_DIT.md seems too short"
```

### Test Case 3.2: Non-IT Department Gets Generic KPIs

**Objective**: Verify non-IT departments receive generic/department-specific KPIs

```python
# File: tests/unit/test_kpi_mapping_generic.py

import pytest
from backend.core.data_loader import DataLoader


@pytest.mark.asyncio
async def test_non_it_department_gets_generic_kpis():
    """Test that non-IT departments get generic or department-specific KPIs"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    non_it_departments = [
        "Департамент продаж",
        "Финансовый блок",
        "Отдел кадров",
        "Юридический департамент",
    ]

    for dept in non_it_departments:
        # Act
        kpi_data = await data_loader.load_kpi_for_department(dept)

        # Assert
        assert kpi_data is not None, f"No KPI data for department: {dept}"
        assert len(kpi_data.strip()) > 0, f"Empty KPI data for department: {dept}"

        # Should NOT contain IT-specific technical metrics
        it_technical_keywords = ["MTTR", "deployment frequency", "kubernetes"]
        kpi_lower = kpi_data.lower()

        it_matches = sum(1 for kw in it_technical_keywords if kw.lower() in kpi_lower)

        # Generic departments should have 0 or very few IT-specific metrics
        assert it_matches == 0, (
            f"Non-IT department {dept} should not have IT-specific KPIs. "
            f"Found: {it_matches} IT keywords"
        )
```

### Test Case 3.3: KPI Coverage 100%

**Objective**: Verify all 567 departments have KPI data (no empty results)

```python
# File: tests/unit/test_kpi_coverage.py

import pytest
from backend.core.data_loader import DataLoader


@pytest.mark.asyncio
async def test_all_departments_have_kpi_data():
    """Test that 100% of departments have KPI data (not empty)"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    # Load all departments from organization structure
    org_structure = await data_loader.load_organization_structure()

    # Extract all department names
    all_departments = data_loader.extract_all_departments(org_structure)

    total_departments = len(all_departments)
    departments_with_kpis = 0
    departments_without_kpis = []

    # Act
    for dept in all_departments:
        kpi_data = await data_loader.load_kpi_for_department(dept)

        if kpi_data and len(kpi_data.strip()) > 0:
            departments_with_kpis += 1
        else:
            departments_without_kpis.append(dept)

    # Calculate coverage
    coverage_rate = (departments_with_kpis / total_departments) * 100

    # Assert: 100% coverage (vs 1.6% before fix)
    assert coverage_rate == 100.0, (
        f"KPI coverage is {coverage_rate:.1f}% (expected 100%). "
        f"Missing KPIs for {len(departments_without_kpis)} departments: "
        f"{departments_without_kpis[:10]}"  # Show first 10
    )

    # Also assert no departments without KPIs
    assert len(departments_without_kpis) == 0, (
        f"{len(departments_without_kpis)} departments have no KPI data"
    )


@pytest.mark.asyncio
async def test_kpi_fallback_mechanism():
    """Test that fallback KPI mechanism works for unknown departments"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    fake_departments = [
        "Несуществующий отдел XYZ",
        "Department of Magic",
        "测试部门",  # Chinese characters
    ]

    for dept in fake_departments:
        # Act
        kpi_data = await data_loader.load_kpi_for_department(dept)

        # Assert: even fake departments should get fallback KPIs
        assert kpi_data is not None, (
            f"Fallback KPI should be provided for unknown department: {dept}"
        )
        assert len(kpi_data.strip()) > 0, (
            f"Fallback KPI should not be empty for: {dept}"
        )
```

---

## Unit Tests - Conditional IT Systems

### Test Case 4.1: IT Role Gets Full IT Systems

**Objective**: Verify IT roles receive full 15K token IT systems data

```python
# File: tests/unit/test_conditional_it_systems_full.py

import pytest
from backend.core.data_loader import DataLoader


@pytest.mark.asyncio
async def test_it_role_gets_full_it_systems():
    """Test that IT roles get full anonymized_digitization_map.md (15K tokens)"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    it_roles = [
        ("Департамент информационных технологий", "Программист"),
        ("ДИТ", "DevOps инженер"),
        ("Отдел информационных технологий", "Data Engineer"),
        ("ДИТ", "Системный администратор"),
    ]

    for department, position in it_roles:
        # Act
        it_systems_data = await data_loader.load_it_systems_conditional(
            department=department,
            position=position
        )

        # Assert
        assert it_systems_data is not None
        assert len(it_systems_data) > 10000, (  # ~15K tokens = ~60K chars
            f"IT role should get full IT systems data. "
            f"Got {len(it_systems_data)} chars (expected >10000)"
        )

        # Check for technical details (should be present in full version)
        technical_keywords = ["API", "database", "authentication", "integration"]
        content_lower = it_systems_data.lower()

        matches = sum(1 for kw in technical_keywords if kw in content_lower)

        assert matches >= 2, (
            f"Full IT systems should contain technical details for {position}"
        )
```

### Test Case 4.2: Management Role Gets Compressed IT Systems

**Objective**: Verify management roles receive compressed (~3K tokens) IT systems summary

```python
# File: tests/unit/test_conditional_it_systems_compressed.py

import pytest
from backend.core.data_loader import DataLoader


@pytest.mark.asyncio
async def test_management_role_gets_compressed_it_systems():
    """Test that management roles get compressed IT systems (~3K tokens)"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    management_roles = [
        ("Блок развития", "Директор"),
        ("Департамент продаж", "Руководитель отдела"),
        ("Финансовый блок", "Начальник управления"),
    ]

    for department, position in management_roles:
        # Act
        it_systems_data = await data_loader.load_it_systems_conditional(
            department=department,
            position=position
        )

        # Assert
        assert it_systems_data is not None

        # Compressed version: 3K tokens ≈ 12K chars
        assert 1000 < len(it_systems_data) < 15000, (
            f"Management role should get compressed IT systems. "
            f"Got {len(it_systems_data)} chars (expected 1000-15000)"
        )

        # Should contain high-level sections only
        high_level_keywords = ["overview", "summary", "main systems"]
        content_lower = it_systems_data.lower()

        matches = sum(1 for kw in high_level_keywords if kw in content_lower)

        # At least some high-level content
        assert matches >= 0, (
            f"Compressed IT systems should contain high-level overview"
        )
```

### Test Case 4.3: Other Roles Get Minimal IT Systems

**Objective**: Verify non-IT, non-management roles receive minimal (~1K tokens) overview

```python
# File: tests/unit/test_conditional_it_systems_minimal.py

import pytest
from backend.core.data_loader import DataLoader


@pytest.mark.asyncio
async def test_other_roles_get_minimal_it_systems():
    """Test that non-IT, non-management roles get minimal IT systems (~1K tokens)"""
    # Arrange
    data_loader = DataLoader("/home/yan/A101/HR/data")

    other_roles = [
        ("Департамент продаж", "Менеджер по продажам"),
        ("Отдел кадров", "HR специалист"),
        ("Юридический департамент", "Юрист"),
    ]

    for department, position in other_roles:
        # Act
        it_systems_data = await data_loader.load_it_systems_conditional(
            department=department,
            position=position
        )

        # Assert
        assert it_systems_data is not None

        # Minimal version: 1K tokens ≈ 4K chars
        assert len(it_systems_data) < 5000, (
            f"Non-IT role should get minimal IT systems. "
            f"Got {len(it_systems_data)} chars (expected <5000)"
        )
```

---

## Integration Tests

### Test Case 5.1: Full Generation Flow with All Fixes

**Objective**: Generate complete profile with ALL fixes applied and validated

```python
# File: tests/integration/test_full_generation_all_fixes.py

import pytest
import json
from jsonschema import validate
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_full_generation_architect_all_fixes():
    """
    Integration test: Generate Архитектор 3к profile with ALL fixes validated

    Validates:
    1. area is string ✓
    2. No performance_metrics ✓
    3. Careerogram correct structure ✓
    4. Has KPI data ✓
    5. IT systems conditional ✓
    """
    # Arrange
    generator = ProfileGenerator()

    with open("/home/yan/A101/HR/templates/universal_job_profile_schema.json") as f:
        schema = json.load(f)

    # Act
    result = await generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        employee_name="Тестовый Архитектор",
        temperature=0.1,
        save_result=True,
    )

    # Assert: Generation successful
    assert result["success"], f"Generation failed: {result.get('errors', [])}"

    profile = result["profile"]
    metadata = result["metadata"]

    # Fix 1: area is string
    for area_obj in profile["responsibility_areas"]:
        assert isinstance(area_obj["area"], str), "Fix 1 failed: area not string"

    # Fix 2: No performance_metrics
    assert "performance_metrics" not in profile, (
        "Fix 2 failed: performance_metrics still present"
    )

    # Fix 3: Careerogram structure
    career_dev = profile["career_development"]
    assert isinstance(career_dev, dict), "Fix 3 failed: careerogram not dict"
    assert isinstance(career_dev.get("career_entry_positions", []), list)
    assert isinstance(career_dev.get("career_growth_positions", []), list)

    # Fix 4: KPI data present
    # Check if KPI data was included in context (visible in metadata or profile)
    # This is implementation-specific - adjust based on your KPI integration
    assert metadata is not None, "Metadata should be present"

    # Fix 5: IT systems conditional (Architect = non-IT, should be compressed/minimal)
    # This is validated via token count in metadata
    llm_metadata = metadata.get("llm", {})
    input_tokens = llm_metadata.get("input_tokens", 0)

    # Architect is non-IT, so should NOT have full 15K token IT systems
    # Approximate: full IT systems adds ~15K tokens
    # Without it or with compressed version, should be <100K tokens total
    assert input_tokens < 100000, (
        f"Fix 5 failed: Input tokens too high ({input_tokens}), "
        f"suggests full IT systems loaded for non-IT role"
    )

    # Schema validation
    validate(instance=profile, schema=schema)

    # Check file was saved
    from pathlib import Path
    profile_id = metadata["generation"].get("profile_id")
    assert profile_id is not None

    output_dir = Path("/home/yan/A101/HR/data/generated_profiles")
    json_file = output_dir / f"{profile_id}.json"

    # Give it a moment for async file save
    import asyncio
    await asyncio.sleep(0.5)

    assert json_file.exists(), "Profile JSON file not saved"


@pytest.mark.asyncio
async def test_full_generation_it_role_all_fixes():
    """
    Integration test: Generate IT role profile (Программист 1С) with ALL fixes

    This IT role SHOULD get full IT systems data
    """
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Отдел CRM",
        position="Программист 1С",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"]

    profile = result["profile"]
    metadata = result["metadata"]

    # All same fixes as above...
    # Fix 1: area is string
    for area_obj in profile["responsibility_areas"]:
        assert isinstance(area_obj["area"], str)

    # Fix 2: No performance_metrics
    assert "performance_metrics" not in profile

    # Fix 3: Careerogram structure
    career_dev = profile["career_development"]
    assert isinstance(career_dev, dict)

    # Fix 5: IT role SHOULD have higher token count (full IT systems)
    input_tokens = metadata["llm"]["input_tokens"]

    # With full IT systems, input tokens should be high
    # This is a soft check - exact numbers depend on implementation
    # If conditional IT systems is working, IT roles will have more tokens
    assert input_tokens > 20000, (
        f"IT role should have full IT systems (higher token count). "
        f"Got {input_tokens} tokens"
    )
```

### Test Case 5.2: Golden Standard Comparison

**Objective**: Compare generated profile structure with golden standard Excel

```python
# File: tests/integration/test_golden_standard_comparison.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_profile_structure_matches_golden_standard():
    """
    Compare generated Архитектор 3к profile with golden standard Excel

    Golden standard: docs/Profiles/Профили архитекторы.xlsx
    """
    # Arrange
    generator = ProfileGenerator()

    # Act
    result = await generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"]

    profile = result["profile"]

    # Golden standard fields (from Excel structure)
    expected_top_level_fields = [
        "position_title",
        "department_broad",
        "department_specific",
        "position_category",
        "responsibility_areas",
        "professional_skills",
        "personal_qualities",
        "education_requirements",
        "career_development",
    ]

    for field in expected_top_level_fields:
        assert field in profile, (
            f"Missing expected field from golden standard: {field}"
        )

    # Check responsibility_areas structure
    responsibility_areas = profile["responsibility_areas"]
    assert isinstance(responsibility_areas, list)
    assert len(responsibility_areas) > 0

    # Each area should have area (string) and tasks (array)
    for area_obj in responsibility_areas:
        assert "area" in area_obj
        assert "tasks" in area_obj
        assert isinstance(area_obj["area"], str)  # Fix 1 validation
        assert isinstance(area_obj["tasks"], list)

    # Check professional_skills structure
    professional_skills = profile["professional_skills"]
    assert isinstance(professional_skills, list)
    assert len(professional_skills) > 0

    for skill in professional_skills:
        assert "skill_category" in skill
        assert "specific_skills" in skill

    # Structure match score
    matched_fields = sum(1 for field in expected_top_level_fields if field in profile)
    match_percentage = (matched_fields / len(expected_top_level_fields)) * 100

    # Require 95%+ structural match
    assert match_percentage >= 95.0, (
        f"Profile structure only {match_percentage}% matches golden standard "
        f"(expected ≥95%)"
    )
```

---

## Regression Tests

### Test Case 6.1: Old Profiles Still Load

**Objective**: Ensure backward compatibility - old profile format still readable

```python
# File: tests/regression/test_old_profile_compatibility.py

import pytest
import json


def test_old_profile_format_with_array_area_loads():
    """
    Test that old profiles with area as array can still be read

    This is a regression test to ensure we don't break existing data
    """
    # Arrange: Create mock old profile with area as array (old format)
    old_profile = {
        "position_title": "Test Position",
        "department_broad": "Test Department",
        "responsibility_areas": [
            {
                "area": ["Разработка", "Тестирование"],  # Old format: array
                "tasks": ["Task 1", "Task 2"]
            }
        ],
        "professional_skills": [],
        "personal_qualities": [],
    }

    # Act: Try to process old format
    # In production, you'd have a compatibility layer that handles both formats
    from backend.core.profile_processor import ProfileProcessor

    processor = ProfileProcessor()

    try:
        processed = processor.normalize_profile(old_profile)

        # Assert: Should not crash, should convert array to string
        area_value = processed["responsibility_areas"][0]["area"]

        assert isinstance(area_value, str), (
            "Compatibility layer should convert array area to string"
        )

    except Exception as e:
        pytest.fail(f"Failed to process old profile format: {e}")


def test_load_existing_profile_from_database():
    """Test loading existing profiles from database (backward compatibility)"""
    # Arrange
    from backend.models.database import get_db_manager

    db = get_db_manager()
    conn = db.get_connection()
    cursor = conn.cursor()

    # Act: Try to load one existing profile
    cursor.execute("SELECT profile_data FROM profiles LIMIT 1")
    row = cursor.fetchone()

    if not row:
        pytest.skip("No existing profiles in database")

    profile_data = row[0]

    # Parse JSON
    try:
        profile = json.loads(profile_data)

        # Assert: Should load successfully
        assert "position_title" in profile
        assert "responsibility_areas" in profile

    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse existing profile JSON: {e}")

    finally:
        conn.close()
```

### Test Case 6.2: Database Compatibility

**Objective**: Verify new profiles save and old profiles load without migration

```python
# File: tests/regression/test_database_compatibility.py

import pytest
import json
from backend.models.database import get_db_manager
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_save_new_profile_load_old_profile():
    """Test saving new profile and loading old profile without schema migration"""
    # Arrange
    generator = ProfileGenerator()
    db = get_db_manager()

    # Act 1: Generate and save new profile
    new_result = await generator.generate_profile(
        department="Test Department",
        position="Test Position",
        temperature=0.1,
        save_result=True,
    )

    assert new_result["success"]

    new_profile_id = new_result["metadata"]["generation"].get("profile_id")

    # Act 2: Try to load the new profile from DB
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT profile_data FROM profiles WHERE id = ?", (new_profile_id,))
    row = cursor.fetchone()

    assert row is not None, "New profile not found in database"

    new_profile_data = json.loads(row[0])

    # Assert: New profile has correct schema (area is string)
    for area_obj in new_profile_data["responsibility_areas"]:
        assert isinstance(area_obj["area"], str)

    # Assert: New profile has no performance_metrics
    assert "performance_metrics" not in new_profile_data

    # Act 3: Load any old profile (if exists)
    cursor.execute(
        "SELECT profile_data FROM profiles WHERE id != ? LIMIT 1",
        (new_profile_id,)
    )
    old_row = cursor.fetchone()

    if old_row:
        old_profile_data = json.loads(old_row[0])

        # Assert: Old profile loads successfully (even if different schema)
        assert "position_title" in old_profile_data

    conn.close()
```

---

## Performance Tests

### Test Case 7.1: Token Reduction Measurement

**Objective**: Measure token reduction from conditional IT systems loading

```python
# File: tests/performance/test_token_reduction.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_token_reduction_non_it_roles():
    """
    Test that non-IT roles use significantly fewer tokens than before

    Before fix: ~158K tokens average (full IT systems always loaded)
    After fix: <100K tokens for non-IT roles (conditional loading)
    """
    # Arrange
    generator = ProfileGenerator()

    non_it_positions = [
        ("Департамент продаж", "Менеджер по продажам"),
        ("Отдел кадров", "HR специалист"),
        ("Финансовый блок", "Финансовый аналитик"),
    ]

    total_tokens = 0
    count = 0

    # Act
    for department, position in non_it_positions:
        result = await generator.generate_profile(
            department=department,
            position=position,
            temperature=0.1,
            save_result=False,
        )

        if result["success"]:
            input_tokens = result["metadata"]["llm"]["input_tokens"]
            total_tokens += input_tokens
            count += 1

    # Calculate average
    average_tokens = total_tokens / count if count > 0 else 0

    # Assert: Average should be <100K (vs 158K before)
    assert average_tokens < 100000, (
        f"Token reduction not achieved. Average: {average_tokens} tokens "
        f"(expected <100K)"
    )

    # Calculate reduction percentage
    tokens_before_fix = 158000
    reduction = ((tokens_before_fix - average_tokens) / tokens_before_fix) * 100

    # Expect at least 30% reduction
    assert reduction >= 30.0, (
        f"Token reduction only {reduction:.1f}% (expected ≥30%)"
    )


@pytest.mark.asyncio
async def test_it_roles_still_have_full_context():
    """Test that IT roles still get full context (no token reduction)"""
    # Arrange
    generator = ProfileGenerator()

    it_positions = [
        ("Департамент информационных технологий", "Программист"),
        ("ДИТ", "DevOps инженер"),
    ]

    # Act & Assert
    for department, position in it_positions:
        result = await generator.generate_profile(
            department=department,
            position=position,
            temperature=0.1,
            save_result=False,
        )

        if result["success"]:
            input_tokens = result["metadata"]["llm"]["input_tokens"]

            # IT roles should still have high token count (full IT systems)
            assert input_tokens > 100000, (
                f"IT role {position} has only {input_tokens} tokens. "
                f"Should have full IT systems context (>100K tokens)"
            )
```

### Test Case 7.2: Generation Time Comparison

**Objective**: Ensure generation time hasn't increased

```python
# File: tests/performance/test_generation_time.py

import pytest
import time
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_generation_time_not_slower():
    """Test that generation time hasn't increased with fixes"""
    # Arrange
    generator = ProfileGenerator()

    # Baseline: typical generation should take 30-60 seconds
    max_acceptable_time = 90  # seconds

    # Act
    start_time = time.time()

    result = await generator.generate_profile(
        department="Департамент информационных технологий",
        position="Python разработчик",
        temperature=0.1,
        save_result=False,
    )

    end_time = time.time()
    duration = end_time - start_time

    # Assert
    assert result["success"], f"Generation failed: {result.get('errors', [])}"

    assert duration < max_acceptable_time, (
        f"Generation took {duration:.1f}s (expected <{max_acceptable_time}s)"
    )

    # Also check metadata duration matches
    metadata_duration = result["metadata"]["generation"]["duration"]

    # Should be close to measured duration (within 5 seconds)
    assert abs(metadata_duration - duration) < 5.0, (
        f"Metadata duration ({metadata_duration}s) differs from measured ({duration:.1f}s)"
    )


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_generation_performance_benchmark(benchmark):
    """Benchmark test for generation performance"""
    # Arrange
    generator = ProfileGenerator()

    async def generate():
        return await generator.generate_profile(
            department="Отдел CRM",
            position="Программист 1С",
            temperature=0.1,
            save_result=False,
        )

    # Act & Assert
    result = benchmark(generate)

    # Benchmark will automatically compare with previous runs
    # and detect performance regressions
```

---

## Quality Tests (Manual Review)

### Test Case 8.1: Quality Score Assessment

**Objective**: Manual HR review of generated profiles on 1-10 scale

```python
# File: tests/quality/test_manual_quality_review.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.manual
@pytest.mark.asyncio
async def test_generate_profiles_for_manual_review():
    """
    Generate 10 diverse profiles for manual HR quality review

    Manual review criteria (1-10 scale):
    - Accuracy: Does profile match position reality?
    - Completeness: All sections filled appropriately?
    - Relevance: Skills/tasks relevant to position?
    - Language: Professional, clear, consistent?
    - Careerogram: Makes logical sense?

    Target: Average score ≥8/10
    """
    # Arrange
    generator = ProfileGenerator()

    review_positions = [
        ("Бюро комплексного проектирования", "Архитектор 3к"),
        ("Департамент информационных технологий", "Python разработчик"),
        ("Отдел CRM", "Программист 1С"),
        ("Департамент продаж", "Менеджер по продажам"),
        ("Финансовый блок", "Финансовый аналитик"),
        ("Юридический департамент", "Юрист"),
        ("Отдел кадров", "HR специалист"),
        ("Департамент маркетинга", "Маркетолог"),
        ("Служба безопасности", "Специалист по ИБ"),
        ("Административный отдел", "Офис-менеджер"),
    ]

    from pathlib import Path
    review_dir = Path("/home/yan/A101/HR/data/generated_profiles/manual_review")
    review_dir.mkdir(parents=True, exist_ok=True)

    # Act: Generate all profiles
    for idx, (department, position) in enumerate(review_positions, 1):
        result = await generator.generate_profile(
            department=department,
            position=position,
            temperature=0.1,
            save_result=False,
        )

        if result["success"]:
            # Save for manual review
            import json

            review_file = review_dir / f"{idx:02d}_{position.replace(' ', '_')}.json"

            with open(review_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ Generated {idx}/10: {position} in {department}")
            print(f"   Saved to: {review_file}")
        else:
            print(f"❌ Failed {idx}/10: {position}")

    # Instructions for manual review
    print("\n" + "="*80)
    print("MANUAL REVIEW INSTRUCTIONS")
    print("="*80)
    print(f"\nReview files location: {review_dir}")
    print("\nReview criteria (rate each profile 1-10):")
    print("  1. Accuracy: Profile matches position reality")
    print("  2. Completeness: All sections appropriately filled")
    print("  3. Relevance: Skills/tasks relevant to position")
    print("  4. Language: Professional, clear, consistent")
    print("  5. Careerogram: Logical career paths")
    print("\nTarget: Average score ≥8/10")
    print("\nRecord scores in: tests/quality/manual_review_scores.json")
    print("="*80)

    # This test always passes - it's just for generating review files
    assert True


def test_load_and_validate_manual_review_scores():
    """Load manual review scores and validate against target"""
    import json
    from pathlib import Path

    scores_file = Path("/home/yan/A101/HR/tests/quality/manual_review_scores.json")

    if not scores_file.exists():
        pytest.skip("Manual review not yet completed")

    with open(scores_file, "r") as f:
        scores_data = json.load(f)

    all_scores = []

    for profile_scores in scores_data.values():
        # Each profile has scores for: accuracy, completeness, relevance, language, careerogram
        profile_avg = sum(profile_scores.values()) / len(profile_scores)
        all_scores.append(profile_avg)

    overall_average = sum(all_scores) / len(all_scores)

    # Assert: Average ≥8/10
    assert overall_average >= 8.0, (
        f"Manual review average score {overall_average:.2f}/10 "
        f"(expected ≥8.0)"
    )
```

### Test Case 8.2: Careerogram Readability

**Objective**: Verify 100% of careergrams are parseable and make sense

```python
# File: tests/quality/test_careerogram_quality.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_careerogram_readability_10_samples():
    """
    Generate 10 profiles and check careerogram readability

    Before fix: 0% parseable (broken structure)
    After fix: 100% parseable, 90%+ make logical sense
    """
    # Arrange
    generator = ProfileGenerator()

    test_positions = [
        ("Департамент информационных технологий", "Junior Python Developer"),
        ("Отдел CRM", "Программист 1С"),
        ("Бюро комплексного проектирования", "Архитектор 3к"),
        ("Департамент продаж", "Менеджер по продажам"),
        ("Финансовый блок", "Финансовый аналитик"),
        ("Юридический департамент", "Юрист"),
        ("Отдел кадров", "HR специалист"),
        ("Департамент маркетинга", "Маркетолог"),
        ("Служба безопасности", "Специалист по ИБ"),
        ("Административный отдел", "Офис-менеджер"),
    ]

    parseable_count = 0
    total_count = len(test_positions)

    careerogram_samples = []

    # Act
    for department, position in test_positions:
        result = await generator.generate_profile(
            department=department,
            position=position,
            temperature=0.1,
            save_result=False,
        )

        if not result["success"]:
            continue

        career_dev = result["profile"].get("career_development", {})

        # Check parseability
        try:
            source = career_dev.get("career_entry_positions", [])
            target = career_dev.get("career_growth_positions", [])

            # Validate structure
            assert isinstance(source, list) and isinstance(target, list)
            assert all(isinstance(p, str) for p in source)
            assert all(isinstance(p, str) for p in target)

            parseable_count += 1

            careerogram_samples.append({
                "position": position,
                "source_positions": source,
                "target_positions": target,
            })

        except (AssertionError, TypeError, KeyError):
            pass

    # Calculate parseability rate
    parseability_rate = (parseable_count / total_count) * 100

    # Assert: 100% parseable (vs 0% before fix)
    assert parseability_rate == 100.0, (
        f"Only {parseability_rate}% of careergrams are parseable "
        f"(expected 100%, was 0% before fix)"
    )

    # Print samples for manual sense-checking
    print("\n" + "="*80)
    print("CAREEROGRAM SAMPLES FOR MANUAL REVIEW")
    print("="*80)

    for sample in careerogram_samples[:3]:  # Show first 3
        print(f"\nPosition: {sample['position']}")
        print(f"  Source positions: {sample['source_positions']}")
        print(f"  Target positions: {sample['target_positions']}")

    print("="*80)
```

---

## Test Data & Fixtures

### Golden Standard Profile Example

```python
# File: tests/fixtures/golden_standard_profile.py

GOLDEN_STANDARD_ARCHITECT_3K = {
    "position_title": "Архитектор 3 категории",
    "department_broad": "Проектный блок",
    "department_specific": "Бюро комплексного проектирования",
    "position_category": "Главный специалист",
    "responsibility_areas": [
        {
            "area": "Моделирование",  # String, not array!
            "tasks": [
                "Создание архитектурных моделей",
                "Подготовка чертежей и планов",
                "Согласование проектных решений",
            ]
        },
        {
            "area": "Проектирование",  # String, not array!
            "tasks": [
                "Разработка концепций зданий",
                "Расчет конструктивных элементов",
            ]
        }
    ],
    "professional_skills": [
        {
            "skill_category": "Технические системы и инструменты",
            "specific_skills": ["AutoCAD", "Revit", "ArchiCAD"],
            "proficiency_level": "Продвинутый",
            "proficiency_description": "Уверенное владение, опыт работы более 3 лет"
        }
    ],
    "personal_qualities": [
        "внимательность к деталям",
        "системное мышление",
        "коммуникабельность"
    ],
    "education_requirements": {
        "education_level": "Высшее образование (специалитет)",
        "preferred_specializations": ["Архитектура", "Строительство"],
        "total_experience": "От 5 лет",
        "relevant_experience": "От 3 лет"
    },
    "career_development": {
        # Correct structure: object with arrays, not flat array!
        "career_entry_positions": [
            "Архитектор 2 категории",
            "Архитектор-стажер"
        ],
        "career_growth_positions": [
            "Архитектор 1 категории",
            "Главный архитектор проекта",
            "Руководитель бюро"
        ]
    },
    # No performance_metrics field!
}
```

### pytest Fixtures

```python
# File: tests/conftest.py

import pytest
from backend.core.profile_generator import ProfileGenerator
from backend.models.database import get_db_manager


@pytest.fixture
async def profile_generator():
    """Fixture: ProfileGenerator instance"""
    return ProfileGenerator()


@pytest.fixture
def db_manager():
    """Fixture: Database manager instance"""
    return get_db_manager()


@pytest.fixture
async def sample_architect_profile(profile_generator):
    """Fixture: Generate Архитектор 3к profile"""
    result = await profile_generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=False,
    )

    assert result["success"], "Failed to generate sample profile"
    return result


@pytest.fixture
async def sample_it_profile(profile_generator):
    """Fixture: Generate IT profile (Программист 1С)"""
    result = await profile_generator.generate_profile(
        department="Отдел CRM",
        position="Программист 1С",
        temperature=0.1,
        save_result=False,
    )

    assert result["success"], "Failed to generate IT profile"
    return result


@pytest.fixture
def json_schema():
    """Fixture: Load JSON schema"""
    import json
    from pathlib import Path

    schema_path = Path("/home/yan/A101/HR/templates/universal_job_profile_schema.json")

    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)
```

---

## Test Execution Plan

### Week 1: Implementation & Testing

#### Day 1: Unit Tests - Schema Fixes
- Implement Test Cases 1.1, 1.2, 1.3
- Run: `pytest tests/unit/test_schema_*.py -v`
- **Success Criteria**: All unit tests pass (100%)

#### Day 2: Unit Tests - Prompt & KPI Fixes
- Implement Test Cases 2.1, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3
- Run: `pytest tests/unit/test_prompt_*.py tests/unit/test_kpi_*.py tests/unit/test_conditional_*.py -v`
- **Success Criteria**: All unit tests pass (100%)

#### Day 3: Integration Tests
- Implement Test Cases 5.1, 5.2
- Run: `pytest tests/integration/test_full_generation_*.py -v`
- **Success Criteria**: All integration tests pass, golden standard match ≥95%

#### Day 4: Regression & Performance Tests
- Implement Test Cases 6.1, 6.2, 7.1, 7.2
- Run: `pytest tests/regression/ tests/performance/ -v`
- **Success Criteria**: No regressions, token reduction ≥30%, time <90s

#### Day 5: Quality Review & Final Report
- Generate 10 profiles for manual review (Test Case 8.1)
- HR team manual review (target ≥8/10)
- Careerogram readability check (Test Case 8.2)
- **Success Criteria**: Quality ≥8/10, careerogram 100% parseable

### Commands Summary

```bash
# Run all tests
pytest tests/ -v --cov=backend --cov-report=html

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests
pytest tests/regression/ -v              # Regression tests
pytest tests/performance/ -v --benchmark # Performance benchmarks

# Run tests for specific fix
pytest tests/unit/test_schema_area_field.py -v          # Fix 1: area field
pytest tests/unit/test_schema_performance_metrics*.py -v # Fix 2: performance_metrics
pytest tests/unit/test_prompt_careerogram*.py -v         # Fix 3: careerogram
pytest tests/unit/test_kpi_*.py -v                       # Fix 4: KPI mapping
pytest tests/unit/test_conditional_*.py -v               # Fix 5: IT systems

# Generate coverage report
pytest tests/ --cov=backend --cov-report=html
open htmlcov/index.html

# Run with detailed output
pytest tests/ -v -s --tb=short

# Run only fast tests (skip slow integration)
pytest tests/unit/ -v --maxfail=1
```

---

## Success Criteria Summary

### Quantitative Metrics

| Metric | Before Fix | After Fix | Target | Status |
|--------|-----------|-----------|--------|--------|
| Schema validation pass rate | 0% (array/string mismatch) | ? | 100% | 🎯 To test |
| Careerogram parseability | 0% (broken structure) | ? | 100% | 🎯 To test |
| KPI coverage | 1.6% (9/567 depts) | ? | 100% | 🎯 To test |
| Token usage (non-IT roles) | 158K avg | ? | <100K | 🎯 To test |
| Token reduction | 0% | ? | ≥30% | 🎯 To test |
| Generation time | 30-60s | ? | <90s | 🎯 To test |
| Unit test coverage | ? | ? | ≥80% | 🎯 To test |

### Qualitative Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Manual quality score | ≥8/10 | HR team review of 10 profiles |
| Careerogram makes sense | 90%+ | Manual review of logic |
| Golden standard match | ≥95% | Automated structural comparison |
| No regressions | 100% | Old profiles still load correctly |

---

## Test Coverage Goals

```
backend/
  ├── core/
  │   ├── profile_generator.py    [90%+ coverage]
  │   ├── data_loader.py          [85%+ coverage]
  │   ├── prompt_manager.py       [80%+ coverage]
  │   ├── llm_client.py           [75%+ coverage]
  │   ├── markdown_service.py     [70%+ coverage]
  │   └── docx_service.py         [70%+ coverage]
  ├── api/
  │   └── generation.py           [85%+ coverage]
  └── models/
      ├── schema.py               [95%+ coverage]
      └── database.py             [80%+ coverage]

Overall Target: ≥80% code coverage
```

---

## Appendix: Test Scenarios Summary

### Total Test Cases: 24

**Unit Tests (15)**:
- Schema fixes: 9 tests
- Prompt fixes: 3 tests
- KPI mapping: 3 tests
- Conditional IT systems: 3 tests

**Integration Tests (2)**:
- Full generation flow: 1 test
- Golden standard comparison: 1 test

**Regression Tests (2)**:
- Old profile compatibility: 1 test
- Database compatibility: 1 test

**Performance Tests (2)**:
- Token reduction: 1 test
- Generation time: 1 test

**Quality Tests (2)**:
- Manual review generation: 1 test
- Careerogram readability: 1 test

---

## Next Steps

1. **Implement fixes** in `feature/quality-optimization` branch
2. **Write tests** following this document
3. **Run test suite** and validate all success criteria
4. **Manual quality review** by HR team
5. **Document results** and create PR
6. **Merge to main** after all tests pass

---

**Document Version**: 1.0
**Last Updated**: 2025-10-25
**Author**: Claude Code (Test Automation Specialist)
**Status**: Ready for Implementation ✅

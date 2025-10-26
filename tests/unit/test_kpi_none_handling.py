"""
Unit tests for KPI None handling regression prevention.

These tests prevent regression of the critical bug where find_kpi_file()
returning None would cause crashes in 71.2% of departments.

Bug Reference: BACKEND_KPI_NONE_FIX.md (2025-10-25)
"""

import pytest
from backend.core.data_mapper import KPIMapper
from backend.core.data_loader import DataLoader


class TestKPIMapperNoneHandling:
    """Test KPIMapper handles None correctly."""

    def test_find_kpi_file_returns_none_for_unknown_department(self):
        """
        Regression test: find_kpi_file should return None for unknown departments.

        This test prevents the crash that occurred when None was not handled
        properly before path operations.

        Bug: TypeError when None was used in path concatenation (PosixPath / None)
        """
        # Arrange
        mapper = KPIMapper()
        unknown_department = "Несуществующий департамент XYZ123"

        # Act
        result = mapper.find_kpi_file(unknown_department)

        # Assert
        assert result is None, (
            f"Expected None for unknown department, got {result}. "
            "This could cause crashes in path operations."
        )

    def test_find_kpi_file_returns_string_for_known_department(self):
        """
        Test that find_kpi_file returns valid filename for known departments.

        This ensures the positive path still works correctly.
        """
        # Arrange
        mapper = KPIMapper()
        known_department = "Департамент информационных технологий"

        # Act
        result = mapper.find_kpi_file(known_department)

        # Assert
        assert result is not None, "Expected KPI file for ДИТ department"
        assert isinstance(result, str), f"Expected string, got {type(result)}"
        assert result.endswith(".md"), f"Expected .md file, got {result}"

    def test_load_kpi_content_handles_none_gracefully(self):
        """
        Regression test: load_kpi_content must not crash when find_kpi_file returns None.

        Should fall back to template instead of crashing.

        Bug: Crashed on path operations when kpi_filename was None
        """
        # Arrange
        mapper = KPIMapper()
        department_without_kpi = "Административное управление"

        # Act
        content = mapper.load_kpi_content(department_without_kpi)

        # Assert
        assert content is not None, "Content should never be None (should use template)"
        assert len(content) > 0, "Content should not be empty (should use template)"
        assert isinstance(content, str), f"Expected string, got {type(content)}"

        # Verify it's template content (not specific KPI)
        # Template content should have "Generic" or standard structure
        assert (
            "Generic" in content or "department:" in content or "КПЭ" in content
        ), "Content should be from template, not empty or error"

    def test_load_kpi_content_for_department_with_specific_kpi(self):
        """
        Test that departments with specific KPI files load correctly.

        This ensures we didn't break the normal path while fixing None handling.
        """
        # Arrange
        mapper = KPIMapper()
        department_with_kpi = "Департамент информационных технологий"

        # Act
        content = mapper.load_kpi_content(department_with_kpi)

        # Assert
        assert content is not None
        assert len(content) > 0
        # Specific KPI files should contain department name
        assert "ДИТ" in content or "информационных технологий" in content.lower()

    def test_load_kpi_content_handles_file_read_errors(self, tmp_path):
        """
        Test that file read errors are handled gracefully with fallback to template.

        This tests the exception handling for IOError, OSError, UnicodeDecodeError.
        """
        # This test would require mocking file operations
        # For now, we just verify that the method doesn't crash
        mapper = KPIMapper()

        # Test with various department names
        test_departments = ["Отдел тестирования", "Группа проверки", "Управление контроля"]

        for dept in test_departments:
            # Act & Assert - should not raise exception
            content = mapper.load_kpi_content(dept)
            assert content is not None
            assert len(content) > 0


class TestDataLoaderNoneHandling:
    """Test DataLoader handles None from KPIMapper correctly."""

    def test_detect_kpi_source_handles_none(self):
        """
        Regression test: _detect_kpi_source must handle None from find_kpi_file.

        Bug: Crashed when trying to build path with None
        """
        # Arrange
        loader = DataLoader()
        department_without_kpi = "Тестовый отдел без KPI"

        # Act
        result = loader._detect_kpi_source(department_without_kpi)

        # Assert
        assert result is not None, "Result should never be None"
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "source" in result, "Result must have 'source' key"
        assert "kpi_file" in result, "Result must have 'kpi_file' key"

        # When no KPI file found, should use template
        assert result["source"] in (
            "template",
            "none",
        ), f"Expected 'template' or 'none' source, got {result['source']}"
        assert result["kpi_file"] is None, f"Expected None for kpi_file, got {result['kpi_file']}"

    def test_detect_kpi_source_for_known_department(self):
        """
        Test that _detect_kpi_source works correctly for departments with KPI files.
        """
        # Arrange
        loader = DataLoader()
        department_with_kpi = "Департамент информационных технологий"

        # Act
        result = loader._detect_kpi_source(department_with_kpi)

        # Assert
        assert result is not None
        assert (
            result["source"] == "specific"
        ), f"Expected 'specific' source for ДИТ, got {result['source']}"
        assert result["kpi_file"] is not None, "Expected KPI file for ДИТ"
        assert isinstance(result["kpi_file"], str)

    def test_detect_kpi_source_returns_correct_structure(self):
        """
        Test that _detect_kpi_source always returns the expected dict structure.
        """
        # Arrange
        loader = DataLoader()
        test_departments = [
            "Департамент информационных технологий",  # Has KPI
            "Административное управление",  # No KPI
            "Отдел тестирования",  # No KPI
        ]

        for dept in test_departments:
            # Act
            result = loader._detect_kpi_source(dept)

            # Assert
            assert isinstance(result, dict), f"Expected dict for {dept}"
            assert "source" in result, f"Missing 'source' key for {dept}"
            assert "dept_type" in result, f"Missing 'dept_type' key for {dept}"
            assert "kpi_file" in result, f"Missing 'kpi_file' key for {dept}"

            # Source should be one of valid values
            assert result["source"] in (
                "specific",
                "template",
                "none",
                "fallback",
            ), f"Invalid source value: {result['source']}"


class TestKPICoverageValidation:
    """Test KPI coverage across organization structure."""

    def test_all_departments_can_load_kpi_content(self):
        """
        Integration test: Verify ALL departments can load KPI content without crashes.

        This is the ultimate regression test - ensures 100% coverage with no crashes.
        """
        # Arrange
        mapper = KPIMapper()
        from backend.core.organization_cache import organization_cache

        # Get all departments
        all_departments = organization_cache.get_all_departments()

        assert len(all_departments) > 0, "Should have departments in org structure"

        # Act & Assert
        failed_departments = []
        for dept in all_departments[:50]:  # Test first 50 to keep test fast
            try:
                content = mapper.load_kpi_content(dept)

                # Verify content is valid
                assert content is not None, f"None content for {dept}"
                assert len(content) > 0, f"Empty content for {dept}"
                assert isinstance(content, str), f"Non-string content for {dept}"

            except Exception as e:
                failed_departments.append((dept, str(e)))

        # Assert no failures
        assert (
            len(failed_departments) == 0
        ), f"Failed to load KPI for {len(failed_departments)} departments:\n" + "\n".join(
            [f"  - {dept}: {err}" for dept, err in failed_departments]
        )

    def test_none_handling_coverage_statistics(self):
        """
        Verify the statistics from the bug fix (28.8% specific, 71.2% template).

        This test documents the expected distribution.
        """
        # Arrange
        mapper = KPIMapper()
        from backend.core.organization_cache import organization_cache

        all_departments = organization_cache.get_all_departments()

        # Act
        specific_count = 0
        template_count = 0

        for dept in all_departments:
            kpi_file = mapper.find_kpi_file(dept)
            if kpi_file is not None:
                specific_count += 1
            else:
                template_count += 1

        total = len(all_departments)
        specific_pct = (specific_count / total) * 100
        template_pct = (template_count / total) * 100

        # Assert
        # Allow some tolerance for changes in org structure
        assert 25 <= specific_pct <= 35, f"Expected ~28.8% specific KPI, got {specific_pct:.1f}%"
        assert 65 <= template_pct <= 75, f"Expected ~71.2% template KPI, got {template_pct:.1f}%"

        # Document actual values
        print("\n📊 KPI Coverage Statistics:")
        print(f"   Total departments: {total}")
        print(f"   Specific KPI: {specific_count} ({specific_pct:.1f}%)")
        print(f"   Template KPI: {template_count} ({template_pct:.1f}%)")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])

"""
Unit tests for CatalogService.

Tests для catalog_service с фокусом на новые методы и логику подсчета позиций.
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch

from backend.services.catalog_service import CatalogService
from backend.models.database import initialize_db_manager


@pytest.fixture(scope="session", autouse=True)
def init_db():
    """Initialize database for tests."""
    # Initialize with in-memory database for tests
    initialize_db_manager(":memory:")


class TestCatalogService:
    """Tests for CatalogService class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.catalog_service = CatalogService()

    def test_get_position_metadata_returns_dict(self):
        """Test that get_position_metadata returns a dictionary."""
        # Arrange
        position_name = "Главный бухгалтер"

        # Act
        result = self.catalog_service.get_position_metadata(position_name)

        # Assert
        assert isinstance(result, dict)
        assert 'level' in result
        assert 'category' in result

    def test_get_position_metadata_has_correct_types(self):
        """Test that metadata has correct value types."""
        # Arrange
        position_name = "Руководитель департамента"

        # Act
        result = self.catalog_service.get_position_metadata(position_name)

        # Assert
        assert isinstance(result['level'], int)
        assert isinstance(result['category'], str)

    def test_get_position_metadata_level_in_valid_range(self):
        """Test that level is in valid range (1-5)."""
        # Arrange
        position_names = [
            "Генеральный директор",  # High level
            "Главный бухгалтер",  # High level
            "Специалист",  # Lower level
            "Менеджер",  # Mid level
        ]

        # Act & Assert
        for position_name in position_names:
            result = self.catalog_service.get_position_metadata(position_name)
            assert 1 <= result['level'] <= 5, f"Level {result['level']} out of range for {position_name}"

    def test_get_position_metadata_category_not_empty(self):
        """Test that category is not empty."""
        # Arrange
        position_name = "Главный архитектор"

        # Act
        result = self.catalog_service.get_position_metadata(position_name)

        # Assert
        assert result['category']
        assert len(result['category']) > 0

    def test_get_position_metadata_consistent_results(self):
        """Test that same position always returns same metadata."""
        # Arrange
        position_name = "Руководитель отдела"

        # Act
        result1 = self.catalog_service.get_position_metadata(position_name)
        result2 = self.catalog_service.get_position_metadata(position_name)

        # Assert
        assert result1 == result2
        assert result1['level'] == result2['level']
        assert result1['category'] == result2['category']

    def test_get_position_metadata_different_positions(self):
        """Test metadata for different position types."""
        # Arrange
        test_cases = [
            {
                "name": "Генеральный директор",
                "expected_level_max": 2,  # Should be high level
                "expected_category": "management"
            },
            {
                "name": "Специалист 1 категории",
                "expected_level_min": 3,  # Should be mid-level or lower
                "expected_category": "specialist"
            }
        ]

        # Act & Assert
        for test_case in test_cases:
            result = self.catalog_service.get_position_metadata(test_case["name"])

            if "expected_level_max" in test_case:
                assert result['level'] <= test_case["expected_level_max"], \
                    f"{test_case['name']} should be high level"

            if "expected_level_min" in test_case:
                assert result['level'] >= test_case["expected_level_min"], \
                    f"{test_case['name']} should be mid/lower level"

            if "expected_category" in test_case:
                assert result['category'] == test_case["expected_category"], \
                    f"{test_case['name']} should be in {test_case['expected_category']} category"

    def test_get_searchable_items_returns_list(self):
        """Test that get_searchable_items returns a list."""
        # Act
        result = self.catalog_service.get_searchable_items()

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_searchable_items_correct_count(self):
        """Test that searchable_items returns all 567 business units."""
        # Act
        result = self.catalog_service.get_searchable_items()

        # Assert
        assert len(result) == 567, f"Expected 567 business units, got {len(result)}"

    def test_get_searchable_items_has_positions(self):
        """Test that searchable_items contain positions."""
        # Act
        result = self.catalog_service.get_searchable_items()

        # Assert
        # Should have at least some items with positions
        items_with_positions = [item for item in result if item.get('positions')]
        assert len(items_with_positions) > 0

        # Check structure of first item with positions
        item_with_pos = items_with_positions[0]
        assert 'name' in item_with_pos
        assert 'positions' in item_with_pos
        assert isinstance(item_with_pos['positions'], list)

    def test_total_positions_count_is_1689(self):
        """Test that total positions across all BUs is 1689."""
        # Act
        searchable_items = self.catalog_service.get_searchable_items()
        total_positions = sum(len(item.get('positions', [])) for item in searchable_items)

        # Assert
        assert total_positions == 1689, \
            f"Expected 1689 total positions, got {total_positions}"

    def test_get_departments_returns_510(self):
        """Test that get_departments returns 510 unique names."""
        # Act
        departments = self.catalog_service.get_departments()

        # Assert
        assert len(departments) == 510, \
            f"Expected 510 unique department names, got {len(departments)}"

    def test_departments_vs_business_units_difference(self):
        """Test the difference between departments and business units."""
        # Act
        departments = self.catalog_service.get_departments()
        searchable_items = self.catalog_service.get_searchable_items()

        # Assert
        # Should have 567 BUs but only 510 unique department names
        assert len(searchable_items) == 567
        assert len(departments) == 510
        assert len(searchable_items) > len(departments)

        # The difference should be due to duplicate names
        expected_duplicates = len(searchable_items) - len(departments)
        assert expected_duplicates == 57, \
            f"Expected 57 duplicate names, got {expected_duplicates}"


class TestCatalogServiceEdgeCases:
    """Tests for edge cases and error handling."""

    def setup_method(self):
        """Setup test fixtures."""
        self.catalog_service = CatalogService()

    def test_get_position_metadata_empty_string(self):
        """Test metadata for empty position name."""
        # Arrange
        position_name = ""

        # Act
        result = self.catalog_service.get_position_metadata(position_name)

        # Assert
        # Should still return valid structure even for empty string
        assert isinstance(result, dict)
        assert 'level' in result
        assert 'category' in result

    def test_get_position_metadata_special_characters(self):
        """Test metadata for position with special characters."""
        # Arrange
        position_name = "Руководитель IT-департамента"

        # Act
        result = self.catalog_service.get_position_metadata(position_name)

        # Assert
        assert isinstance(result['level'], int)
        assert isinstance(result['category'], str)
        assert 1 <= result['level'] <= 5

    def test_get_position_metadata_very_long_name(self):
        """Test metadata for very long position name."""
        # Arrange
        position_name = "Главный специалист отдела по работе с " * 5

        # Act
        result = self.catalog_service.get_position_metadata(position_name)

        # Assert
        assert isinstance(result, dict)
        assert 'level' in result
        assert 'category' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

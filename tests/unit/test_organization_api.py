"""
Unit tests for Organization API endpoints (BUG-09 fix).

These tests verify the /api/organization/positions endpoint correctly
flattens business units into positions and calculates statistics.

Bug Reference: BUG-09 - Fix incorrect statistics on Profile Generator page
Date: 2025-10-26
"""

import pytest
import sqlite3
from typing import Dict, Any, List, Tuple
from unittest.mock import Mock, MagicMock, patch

# Import functions to test
from backend.api.organization import (
    _build_profile_mapping,
    _flatten_business_units_to_positions,
    _calculate_position_statistics
)


class TestBuildProfileMapping:
    """Test _build_profile_mapping helper function."""

    def test_builds_correct_mapping_from_profiles(self):
        """
        Test that profile mapping is built correctly from database rows.

        The mapping should use (department, position) tuple as key
        and profile_id as value for O(1) lookups.
        """
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'department': 'ДИТ', 'position': 'Программист'},
            {'id': 2, 'department': 'ДИТ', 'position': 'Аналитик'},
            {'id': 3, 'department': 'HR', 'position': 'Менеджер'}
        ]

        # Act
        result = _build_profile_mapping(mock_cursor)

        # Assert
        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) == 3, "Should have 3 profile mappings"
        assert result[('ДИТ', 'Программист')] == 1
        assert result[('ДИТ', 'Аналитик')] == 2
        assert result[('HR', 'Менеджер')] == 3

    def test_handles_empty_profiles(self):
        """
        Test that empty profile list returns empty mapping.

        This happens when no profiles have been created yet.
        """
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []

        # Act
        result = _build_profile_mapping(mock_cursor)

        # Assert
        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) == 0, "Should be empty for no profiles"

    def test_handles_duplicate_department_position_pairs(self):
        """
        Test that duplicate (department, position) pairs use last profile_id.

        This shouldn't happen in production, but we handle it gracefully.
        """
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'department': 'ДИТ', 'position': 'Программист'},
            {'id': 2, 'department': 'ДИТ', 'position': 'Программист'},  # Duplicate
        ]

        # Act
        result = _build_profile_mapping(mock_cursor)

        # Assert
        assert len(result) == 1, "Duplicate keys should be overwritten"
        assert result[('ДИТ', 'Программист')] == 2, "Should use last profile_id"


class TestFlattenBusinessUnitsToPositions:
    """Test _flatten_business_units_to_positions helper function."""

    def test_flattens_business_units_correctly(self):
        """
        Test that business units are flattened into individual positions.

        Each business unit has a list of position names (strings).
        Should create one position dict for each position string.
        """
        # Arrange
        search_items = [
            {
                'name': 'ДИТ',
                'hierarchy': 'Блок ОД → ДИТ',
                'full_path': 'Блок ОД/ДИТ',
                'positions': ['Программист', 'Аналитик']
            }
        ]
        profile_map = {('ДИТ', 'Программист'): 42}

        # Act
        result = _flatten_business_units_to_positions(search_items, profile_map)

        # Assert
        assert len(result) == 2, "Should create 2 positions from 2 position names"

        # Check first position (with profile)
        programmer = result[0]
        assert programmer['position_name'] == 'Программист'
        assert programmer['business_unit_name'] == 'ДИТ'
        assert programmer['profile_exists'] is True
        assert programmer['profile_id'] == 42

        # Check second position (without profile)
        analyst = result[1]
        assert analyst['position_name'] == 'Аналитик'
        assert analyst['profile_exists'] is False
        assert analyst['profile_id'] is None

    def test_generates_unique_position_ids(self):
        """
        Test that each position gets a unique ID from path + name.

        Position ID is used for frontend tracking and should be unique.
        """
        # Arrange
        search_items = [
            {
                'name': 'ДИТ',
                'hierarchy': 'Блок ОД → ДИТ',
                'full_path': 'Блок ОД/ДИТ',
                'positions': ['Программист', 'Программист']  # Duplicate names
            }
        ]
        profile_map = {}

        # Act
        result = _flatten_business_units_to_positions(search_items, profile_map)

        # Assert
        assert len(result) == 2, "Should create 2 positions even with duplicate names"
        # Both should have same generated ID (based on full_path + position_name)
        assert result[0]['position_id'] == result[1]['position_id']
        assert 'Блок_ОД_ДИТ_Программист' in result[0]['position_id']

    def test_handles_multiple_business_units(self):
        """
        Test flattening multiple business units into one position list.

        Real scenario: 567 business units -> ~1689 positions.
        """
        # Arrange
        search_items = [
            {
                'name': 'ДИТ',
                'hierarchy': 'Блок ОД → ДИТ',
                'full_path': 'Блок ОД/ДИТ',
                'positions': ['Программист']
            },
            {
                'name': 'HR',
                'hierarchy': 'Блок ГД → HR',
                'full_path': 'Блок ГД/HR',
                'positions': ['Менеджер', 'Специалист']
            }
        ]
        profile_map = {}

        # Act
        result = _flatten_business_units_to_positions(search_items, profile_map)

        # Assert
        assert len(result) == 3, "Should have 1 + 2 = 3 total positions"
        business_units = {p['business_unit_name'] for p in result}
        assert business_units == {'ДИТ', 'HR'}

    def test_handles_empty_business_units(self):
        """
        Test that empty business unit list returns empty position list.
        """
        # Arrange
        search_items = []
        profile_map = {}

        # Act
        result = _flatten_business_units_to_positions(search_items, profile_map)

        # Assert
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 0, "Should be empty for no business units"

    def test_handles_business_unit_with_no_positions(self):
        """
        Test that business units with empty positions list are handled.

        Some business units might have no positions defined.
        """
        # Arrange
        search_items = [
            {
                'name': 'Empty Department',
                'hierarchy': 'Test',
                'full_path': 'Test/Empty',
                'positions': []  # No positions
            }
        ]
        profile_map = {}

        # Act
        result = _flatten_business_units_to_positions(search_items, profile_map)

        # Assert
        assert len(result) == 0, "Should return no positions for empty positions list"


class TestCalculatePositionStatistics:
    """Test _calculate_position_statistics helper function."""

    def test_calculates_statistics_correctly(self):
        """
        Test that statistics are calculated correctly from position list.

        Should return total_count, positions_with_profiles, coverage_percentage.
        """
        # Arrange
        positions = [
            {'profile_exists': True},
            {'profile_exists': False},
            {'profile_exists': True},
            {'profile_exists': False},
        ]

        # Act
        result = _calculate_position_statistics(positions)

        # Assert
        assert result['total_count'] == 4
        assert result['positions_with_profiles'] == 2
        assert result['coverage_percentage'] == 50.0

    def test_calculates_coverage_with_rounding(self):
        """
        Test that coverage percentage is rounded to 1 decimal place.

        Example: 2/3 = 66.666... should be rounded to 66.7
        """
        # Arrange
        positions = [
            {'profile_exists': True},
            {'profile_exists': True},
            {'profile_exists': False},
        ]

        # Act
        result = _calculate_position_statistics(positions)

        # Assert
        assert result['coverage_percentage'] == 66.7, "Should round to 1 decimal"

    def test_handles_zero_positions(self):
        """
        Test that division by zero is avoided for empty position list.

        Should return 0% coverage instead of throwing error.
        """
        # Arrange
        positions = []

        # Act
        result = _calculate_position_statistics(positions)

        # Assert
        assert result['total_count'] == 0
        assert result['positions_with_profiles'] == 0
        assert result['coverage_percentage'] == 0

    def test_handles_all_positions_with_profiles(self):
        """
        Test 100% coverage calculation.

        All positions have profiles created.
        """
        # Arrange
        positions = [
            {'profile_exists': True},
            {'profile_exists': True},
            {'profile_exists': True},
        ]

        # Act
        result = _calculate_position_statistics(positions)

        # Assert
        assert result['total_count'] == 3
        assert result['positions_with_profiles'] == 3
        assert result['coverage_percentage'] == 100.0

    def test_handles_no_positions_with_profiles(self):
        """
        Test 0% coverage calculation.

        No profiles have been created yet.
        """
        # Arrange
        positions = [
            {'profile_exists': False},
            {'profile_exists': False},
        ]

        # Act
        result = _calculate_position_statistics(positions)

        # Assert
        assert result['total_count'] == 2
        assert result['positions_with_profiles'] == 0
        assert result['coverage_percentage'] == 0.0


class TestGetAllPositionsEndpoint:
    """Integration tests for the full /positions endpoint."""

    @pytest.mark.asyncio
    async def test_endpoint_returns_correct_structure(self):
        """
        Test that endpoint response has correct structure.

        Response should match the documented API schema.
        """
        # This would require full FastAPI test client setup
        # Placeholder for future integration test
        pass

    @pytest.mark.asyncio
    async def test_endpoint_handles_errors_gracefully(self):
        """
        Test that endpoint handles various error conditions.

        Should return 500 with appropriate error message.
        """
        # This would require full FastAPI test client setup
        # Placeholder for future integration test
        pass

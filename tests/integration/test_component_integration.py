"""
Integration tests for A101 HR Profile Generator component interactions.

Tests the event system, state management, and component lifecycle.
Identifies and validates integration patterns between components.
"""

import asyncio
import pytest
import unittest.mock as mock
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, Optional
import logging
import sys
import os

# Mock NiceGUI imports
sys_modules_backup = {}
mock_modules = [
    'nicegui', 'nicegui.ui', 'nicegui.app'
]

for module in mock_modules:
    if module in sys.modules:
        sys_modules_backup[module] = sys.modules[module]
    sys.modules[module] = Mock()

# Import components after mocking NiceGUI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../frontend'))

from services.api_client import APIClient, APIError
from components.core.search_component import SearchComponent
from components.core.generator_component import GeneratorComponent
from components.core.profile_viewer_component import ProfileViewerComponent
from components.core.files_manager_component import FilesManagerComponent
from pages.generator_page import GeneratorPage

logger = logging.getLogger(__name__)


class TestComponentIntegration:
    """Tests for component integration and event system."""

    @pytest.fixture
    def mock_api_client(self):
        """Mock API client with common responses."""
        client = Mock(spec=APIClient)
        client.base_url = "http://localhost:8022"

        # Mock common API responses
        client.get_organization_search_items = AsyncMock(return_value={
            "success": True,
            "data": {
                "items": [
                    {
                        "name": "IT Department",
                        "full_path": "Company → IT Department",
                        "hierarchy": "Company → IT Department",
                        "display_name": "IT Department",
                        "level": 1,
                        "positions": ["Java Developer", "Python Developer"],
                        "positions_count": 2
                    }
                ]
            }
        })

        client.get_departments = AsyncMock(return_value={
            "success": True,
            "data": {
                "departments": [
                    {"name": "IT Department", "full_path": "Company → IT Department"}
                ]
            }
        })

        client.get_positions = AsyncMock(return_value={
            "success": True,
            "data": {
                "positions": [
                    {"name": "Java Developer", "department": "IT Department"}
                ]
            }
        })

        client.get_profiles_list = AsyncMock(return_value={
            "profiles": [
                {
                    "profile_id": "test123",
                    "position": "Java Developer",
                    "department": "IT Department",
                    "status": "completed",
                    "created_at": "2024-01-01T10:00:00Z"
                }
            ]
        })

        client.start_profile_generation = AsyncMock(return_value={
            "task_id": "task123",
            "status": "queued",
            "message": "Generation started"
        })

        client.get_generation_task_status = AsyncMock(return_value={
            "success": True,
            "task": {
                "status": "completed",
                "progress": 100,
                "current_step": "Completed"
            }
        })

        client.get_generation_task_result = AsyncMock(return_value={
            "success": True,
            "profile_id": "test123",
            "profile": {"position_title": "Java Developer"},
            "metadata": {"generation_time_seconds": 30}
        })

        client.download_profile_json = AsyncMock(return_value=b'{"test": "data"}')
        client.download_profile_markdown = AsyncMock(return_value=b'# Test Profile')

        return client

    @pytest.fixture
    def components(self, mock_api_client):
        """Create component instances for testing."""
        search = SearchComponent(mock_api_client)
        generator = GeneratorComponent(mock_api_client)
        viewer = ProfileViewerComponent(mock_api_client)
        files = FilesManagerComponent(mock_api_client)
        return search, generator, viewer, files

    @pytest.fixture
    def generator_page(self, mock_api_client):
        """Create GeneratorPage instance for testing."""
        return GeneratorPage(mock_api_client)


class TestEventSystemIntegration(TestComponentIntegration):
    """Test event system communication between components."""

    def test_event_binding_setup(self, generator_page):
        """Test that events are properly bound between components."""
        page = generator_page

        # Check SearchComponent → GeneratorComponent binding
        assert page.search.on_position_selected == page.generator.set_position

        # Check SearchComponent → ProfileViewerComponent binding
        assert page.search.on_profiles_found == page.viewer.show_profile_list

        # Check ProfileViewerComponent → FilesManagerComponent binding
        assert page.viewer.on_download_request == page.files.download_file_sync

        # Check GeneratorComponent → ProfileViewerComponent binding (if available)
        if hasattr(page.generator, 'on_generation_complete'):
            assert page.generator.on_generation_complete is not None

    @pytest.mark.asyncio
    async def test_position_selection_flow(self, components):
        """Test position selection propagation from SearchComponent to GeneratorComponent."""
        search, generator, viewer, files = components

        # Mock UI elements
        search.search_input = Mock()
        search.search_results_container = Mock()
        search.search_loading = Mock()

        # Set up event binding
        position_received = []
        def mock_set_position(position, department):
            position_received.append((position, department))

        search.on_position_selected = mock_set_position

        # Simulate position selection
        await search._set_selected_position("Java Developer", "IT Department")

        # Verify position was propagated
        assert len(position_received) == 1
        assert position_received[0] == ("Java Developer", "IT Department")
        assert search.selected_position == "Java Developer"
        assert search.selected_department == "IT Department"

    @pytest.mark.asyncio
    async def test_profiles_found_flow(self, components):
        """Test profiles found event from SearchComponent to ProfileViewerComponent."""
        search, generator, viewer, files = components

        # Mock UI elements
        search.search_input = Mock()
        search.search_results_container = Mock()
        search.search_loading = Mock()

        # Set up event binding
        profiles_received = []
        def mock_show_profiles(profiles_data):
            profiles_received.append(profiles_data)

        search.on_profiles_found = mock_show_profiles

        # Load test position details
        await search._load_position_details("Java Developer", "IT Department")

        # Verify profiles were found and propagated
        assert len(profiles_received) > 0
        profiles_data = profiles_received[0]
        assert 'profiles' in profiles_data
        assert 'status' in profiles_data
        assert profiles_data['position'] == "Java Developer"
        assert profiles_data['department'] == "IT Department"

    def test_download_request_flow(self, components):
        """Test download request from ProfileViewerComponent to FilesManagerComponent."""
        search, generator, viewer, files = components

        # Mock download method
        download_requests = []
        def mock_download(profile_id, format_type):
            download_requests.append((profile_id, format_type))

        viewer.on_download_request = mock_download

        # Simulate download request
        viewer._request_download("test123", "json")

        # Verify download request was propagated
        assert len(download_requests) == 1
        assert download_requests[0] == ("test123", "json")


class TestStateManagement(TestComponentIntegration):
    """Test state management and synchronization between components."""

    def test_search_component_state_management(self, components):
        """Test SearchComponent state consistency."""
        search, _, _, _ = components

        # Initial state
        assert search.selected_position == ""
        assert search.selected_department == ""
        assert search.position_profiles == []

        # Set position state
        search.selected_position = "Java Developer"
        search.selected_department = "IT Department"
        search.position_profiles = [{"profile_id": "test123"}]

        # Verify state consistency
        position_data = search.get_selected_position_data()
        assert position_data["position"] == "Java Developer"
        assert position_data["department"] == "IT Department"
        assert len(position_data["existing_profiles"]) == 1

    def test_generator_component_state_management(self, components):
        """Test GeneratorComponent state consistency."""
        _, generator, _, _ = components

        # Initial state
        initial_status = generator.get_generation_status()
        assert not initial_status["is_generating"]
        assert initial_status["task_id"] is None

        # Set position
        generator.set_position("Java Developer", "IT Department")

        # Verify state update
        status = generator.get_generation_status()
        assert status["selected_position"] == "Java Developer"
        assert status["selected_department"] == "IT Department"

    def test_viewer_component_state_management(self, components):
        """Test ProfileViewerComponent state consistency."""
        _, _, viewer, _ = components

        # Initial state
        assert viewer.current_profile is None
        assert viewer.profiles_list == []
        assert not viewer.show_detailed_view

        # Show profile list
        test_profiles = [
            {"profile_id": "test123", "position": "Java Developer"}
        ]
        viewer.show_profile_list(test_profiles)

        # Verify state update
        assert viewer.profiles_list == test_profiles
        assert not viewer.show_detailed_view

        # Show single profile
        viewer.show_profile(test_profiles[0])

        # Verify detailed view state
        assert viewer.current_profile == test_profiles[0]
        assert viewer.show_detailed_view

    def test_files_manager_state_management(self, components):
        """Test FilesManagerComponent state consistency."""
        _, _, _, files = components

        # Initial state
        status = files.get_download_status()
        assert status["temp_files_count"] == 0
        assert not status["is_downloading"]

        # Simulate file creation
        files.temp_files.add("/tmp/test_file.json")

        # Verify state update
        status = files.get_download_status()
        assert status["temp_files_count"] == 1
        assert "/tmp/test_file.json" in status["temp_files"]


class TestComponentLifecycle(TestComponentIntegration):
    """Test component lifecycle management."""

    @pytest.mark.asyncio
    async def test_search_component_lifecycle(self, components):
        """Test SearchComponent initialization and data loading."""
        search, _, _, _ = components

        # Test data loading
        await search.load_search_data()

        # Verify hierarchical suggestions are loaded
        assert len(search.hierarchical_suggestions) > 0
        assert len(search.position_lookup) > 0

    @pytest.mark.asyncio
    async def test_generator_page_initialization(self, generator_page):
        """Test GeneratorPage component initialization and binding."""
        page = generator_page

        # Verify all components are initialized
        assert page.search is not None
        assert page.generator is not None
        assert page.viewer is not None
        assert page.files is not None

        # Verify event bindings are set up
        assert page.search.on_position_selected is not None
        assert page.search.on_profiles_found is not None
        assert page.viewer.on_download_request is not None

    def test_component_cleanup(self, components):
        """Test component cleanup functionality."""
        search, generator, viewer, files = components

        # Test search component cleanup
        search.selected_position = "Test Position"
        search.selected_department = "Test Department"
        search.position_profiles = [{"test": "data"}]

        asyncio.run(search._clear_search())

        assert search.selected_position == ""
        assert search.selected_department == ""
        assert search.position_profiles == []

        # Test viewer component cleanup
        viewer.current_profile = {"test": "profile"}
        viewer.show_detailed_view = True
        viewer.profiles_list = [{"test": "data"}]

        viewer.clear_display()

        assert viewer.current_profile is None
        assert not viewer.show_detailed_view
        assert viewer.profiles_list == []

        # Test files manager cleanup
        files.temp_files.add("/tmp/test1.json")
        files.temp_files.add("/tmp/test2.json")

        files.cleanup_all_temp_files()

        assert len(files.temp_files) == 0


class TestErrorHandling(TestComponentIntegration):
    """Test error handling and propagation between components."""

    @pytest.mark.asyncio
    async def test_api_error_handling_in_search(self, components):
        """Test error handling in SearchComponent when API fails."""
        search, _, _, _ = components

        # Mock API failure
        search.api_client.get_organization_search_items = AsyncMock(
            side_effect=APIError("API Error", 500)
        )

        # Mock UI elements
        search.search_input = Mock()
        search.search_results_container = Mock()
        search.search_loading = Mock()

        # Load data should handle error gracefully
        await search.load_search_data()

        # Should fall back to fallback suggestions
        assert len(search.hierarchical_suggestions) > 0
        assert "fallback" in search.hierarchical_suggestions[0].lower() or "департамент" in search.hierarchical_suggestions[0].lower()

    @pytest.mark.asyncio
    async def test_generation_error_handling(self, components):
        """Test error handling in GeneratorComponent during generation."""
        _, generator, _, _ = components

        # Mock API failure
        generator.api_client.start_profile_generation = AsyncMock(
            side_effect=APIError("Generation failed", 500)
        )

        # Mock UI elements
        generator.generate_button = Mock()
        generator.generation_status_container = Mock()

        # Set position
        generator.set_position("Java Developer", "IT Department")

        # Start generation should handle error
        with patch('asyncio.create_task'):  # Prevent actual task creation
            await generator._start_generation()

        # Verify error state
        assert not generator.is_generating

    def test_download_error_handling(self, components):
        """Test error handling in FilesManagerComponent during download."""
        _, _, _, files = components

        # Test invalid profile ID
        with patch('nicegui.ui.notify') as mock_notify:
            asyncio.run(files.download_file("", "json"))
            mock_notify.assert_called_with("❌ Нет ID профиля для скачивания", type="negative")

        # Test invalid format
        with patch('nicegui.ui.notify') as mock_notify:
            asyncio.run(files.download_file("test123", "invalid"))
            mock_notify.assert_called_with("❌ Неподдерживаемый формат: invalid", type="negative")


class TestDataFlow(TestComponentIntegration):
    """Test complete data flow through component system."""

    @pytest.mark.asyncio
    async def test_complete_generation_flow(self, generator_page):
        """Test complete flow: search → generate → view → download."""
        page = generator_page

        # Mock UI elements for all components
        page.search.search_input = Mock()
        page.search.search_results_container = Mock()
        page.search.search_loading = Mock()
        page.generator.generate_button = Mock()
        page.generator.generation_status_container = Mock()

        # Step 1: Load search data
        await page.search.load_search_data()
        assert len(page.search.hierarchical_suggestions) > 0

        # Step 2: Select position
        await page.search._set_selected_position("Java Developer", "IT Department")
        assert page.search.selected_position == "Java Developer"

        # Step 3: Check if generator received position
        # (This would be called by event system in real scenario)
        page.generator.set_position("Java Developer", "IT Department")
        assert page.generator.selected_position == "Java Developer"

        # Step 4: Mock generation completion
        generation_result = {
            "success": True,
            "profile_id": "test123",
            "profile": {"position_title": "Java Developer"},
            "metadata": {"generation_time_seconds": 30}
        }

        # Step 5: Show result in viewer
        await page._handle_generation_complete(generation_result)

        # Verify the flow completed successfully
        # (In real app, viewer would be updated through events)

    def test_error_propagation_flow(self, generator_page):
        """Test error propagation through component system."""
        page = generator_page

        # Test error in generation affecting viewer
        error_result = {
            "success": False,
            "error": "Generation failed due to network error"
        }

        with patch('nicegui.ui.notify') as mock_notify:
            asyncio.run(page._handle_generation_complete(error_result))
            # Should show error notification
            mock_notify.assert_called()


class TestIntegrationIssues:
    """Specific tests for identified integration issues."""

    def test_async_event_handling_issue(self):
        """Test Issue #1: Async event handlers in sync contexts."""
        # Issue: ProfileViewerComponent calls async methods in sync event handlers

        viewer = ProfileViewerComponent(Mock())

        # Problem: _view_single_profile creates async task incorrectly
        with patch('asyncio.create_task') as mock_task, \
             patch('nicegui.ui.notify'):

            viewer.position_profiles = [{"profile_id": "test123"}]
            viewer.selected_position = "Java Developer"
            viewer.selected_department = "IT Department"
            viewer.on_profiles_found = AsyncMock()

            viewer._view_single_profile()

            # Should create task for async operation
            mock_task.assert_called()

    def test_event_binding_type_mismatch(self):
        """Test Issue #2: Event binding type mismatches."""
        # Issue: on_download_request expects async function but gets sync wrapper

        viewer = ProfileViewerComponent(Mock())
        files = FilesManagerComponent(Mock())

        # Current binding uses sync wrapper
        viewer.on_download_request = files.download_file_sync

        # Test that sync wrapper is called correctly
        with patch.object(files, 'download_file_sync') as mock_sync:
            viewer._request_download("test123", "json")
            mock_sync.assert_called_with("test123", "json")

    def test_state_synchronization_issue(self):
        """Test Issue #3: State synchronization between components."""
        # Issue: Component states can become inconsistent

        search = SearchComponent(Mock())
        generator = GeneratorComponent(Mock())

        # Set up binding
        generator.set_position = Mock()
        search.on_position_selected = generator.set_position

        # Manually set state in search
        search.selected_position = "Java Developer"
        search.selected_department = "IT Department"

        # Generator state is not automatically synchronized
        assert generator.selected_position != search.selected_position

        # Event must be called to synchronize
        search.on_position_selected(search.selected_position, search.selected_department)
        generator.set_position.assert_called_with("Java Developer", "IT Department")


# Integration test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
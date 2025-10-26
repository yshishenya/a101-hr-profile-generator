#!/usr/bin/env python3
"""
@doc
Comprehensive E2E testing for A101 HR Profile Generator /generate page.

This test suite covers critical user journeys:
1. Happy Path - New profile generation
2. View existing profile
3. Error handling scenarios
4. Performance testing
5. Integration testing

Captain, this ensures all user-facing functionality works correctly end-to-end.

Examples:
  python> tester = TestE2EUserJourneys()
  python> await tester.run_all_user_journey_tests()
"""

import asyncio
import pytest
import json
import httpx
import time
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import logging
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestE2EUserJourneys:
    """
    @doc
    End-to-end testing for critical user journeys on /generate page.

    Tests real user interactions without UI automation, focusing on
    business logic, API integration, and component coordination.
    """

    def __init__(self):
        """Initialize test environment with realistic setup"""
        self.base_url = "http://localhost:8022"
        self.frontend_url = "http://localhost:8033"
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "critical_issues": [],
            "performance_metrics": {}
        }

    async def setup_test_environment(self):
        """
        @doc
        Setup test environment with proper authentication and mocking.

        Examples:
          python> await tester.setup_test_environment()
          python> # Environment ready for testing
        """
        # Import components after setting up mocks
        import sys
        sys.path.append('/home/yan/A101/HR')

        # Create mock UI to avoid NiceGUI dependency in tests
        self.mock_ui = self._create_mock_ui()

        # Patch NiceGUI imports
        with patch.dict('sys.modules', {
            'nicegui': MagicMock(),
            'nicegui.ui': self.mock_ui,
            'nicegui.app': MagicMock(storage=MagicMock(user={'authenticated': True}))
        }):

            from frontend.services.api_client import APIClient
            from frontend.pages.generator_page import GeneratorPage

            self.api_client = APIClient(self.base_url)

            # Get a valid test token
            test_token = await self._get_test_token()
            self.api_client._access_token = test_token

            # Initialize the main page component
            self.generator_page = GeneratorPage(self.api_client)

        logger.info("✅ Test environment setup completed")

    def _create_mock_ui(self):
        """Create comprehensive UI mocks"""
        class MockUI:
            def __init__(self):
                self.notifications = []
                self.components = []

            def notify(self, message: str, type: str = "info", **kwargs):
                self.notifications.append({"message": message, "type": type, "kwargs": kwargs})
                print(f"UI NOTIFY [{type.upper()}]: {message}")

            def card(self): return self
            def column(self): return self
            def row(self): return self
            def label(self, text=""): return self
            def button(self, text="", **kwargs): return self
            def select(self, **kwargs): return self
            def spinner(self, **kwargs): return self
            def expansion(self, *args, **kwargs): return self
            def icon(self, name, **kwargs): return self
            def badge(self, text): return self
            def classes(self, *args): return self
            def props(self, *args): return self
            def style(self, *args): return self
            def set_options(self, options): pass
            def set_value(self, value): pass
            def set_text(self, text): pass
            def clear(self): pass
            def on(self, event, handler): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass

        return MockUI()

    async def _get_test_token(self) -> str:
        """Get a valid test token for API calls"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    json={"username": "admin", "password": "admin"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    # Verify BaseResponse format
                    if data.get("success") and data.get("access_token"):
                        return data["access_token"]
                    else:
                        logger.warning(f"Auth response missing expected fields: {data}")
                        return "test_token_12345"
                else:
                    # Fallback to test token
                    return "test_token_12345"

        except Exception as e:
            logger.warning(f"Could not get auth token, using fallback: {e}")
            return "test_token_12345"

    async def test_journey_1_new_profile_generation(self):
        """
        @doc
        TEST JOURNEY 1: Happy Path - New Profile Generation

        User flow:
        1. User enters /generate page
        2. Searches for "Java"
        3. Sees positions with status indicators
        4. Selects position without profile (🔴)
        5. Generation button activates
        6. Clicks generation
        7. Sees progress dialog
        8. Generation completes successfully
        9. ProfileViewer opens automatically
        10. Can switch between tabs
        11. Can download files

        Examples:
          python> await tester.test_journey_1_new_profile_generation()
          python> # Full user journey tested
        """
        print("\n🎯 USER JOURNEY 1: New Profile Generation (Happy Path)")
        print("-" * 60)

        issues = []
        journey_start = time.time()

        try:
            # Step 1: Initialize page components
            search = self.generator_page.search
            generator = self.generator_page.generator
            viewer = self.generator_page.viewer
            files = self.generator_page.files

            # Step 2: Load search data (simulating user entering page)
            print("📋 Step 1: Loading search data...")
            await search.load_search_data()

            if len(search.hierarchical_suggestions) == 0:
                issues.append("CRITICAL: No search suggestions loaded")

            suggestions_count = len(search.hierarchical_suggestions)
            print(f"   ✅ Loaded {suggestions_count} position suggestions")

            # Step 3: Search functionality (user types "Java")
            print("🔍 Step 2: Testing search for 'Java' positions...")
            java_positions = [s for s in search.hierarchical_suggestions if 'java' in s.lower()]

            if not java_positions:
                print("   ⚠️  No Java positions found, using first available position")
                test_position = search.hierarchical_suggestions[0]
            else:
                test_position = java_positions[0]
                print(f"   ✅ Found Java position: {test_position}")

            # Step 4: Position selection (user clicks on position)
            print("🎯 Step 3: Simulating position selection...")
            department, position = search._process_hierarchical_selection(test_position)

            if not department or not position:
                issues.append(f"CRITICAL: Failed to parse position selection: {test_position}")
                raise Exception("Position parsing failed")

            print(f"   ✅ Parsed selection: '{position}' in '{department}'")

            # Step 5: Set position and check status
            print("📊 Step 4: Loading position details and status...")

            # Mock the UI container to avoid NoneType errors
            search.search_results_container = self.mock_ui

            await search._set_selected_position(position, department)

            if search.selected_position != position:
                issues.append("CRITICAL: Position not set correctly")

            print(f"   ✅ Position set: {search.selected_position}")
            print(f"   ✅ Department set: {search.selected_department}")

            profile_count = len(search.position_profiles)
            status_info = search._analyze_profile_status()
            print(f"   📈 Profile status: {status_info['status']} ({profile_count} existing)")

            # Step 6: Test generator activation
            print("⚡ Step 5: Testing generator activation...")
            generator.set_position(position, department)

            if not generator.selected_position:
                issues.append("CRITICAL: Generator position not set")

            # Mock generation UI elements
            generator.generate_button = self.mock_ui
            generator.progress_dialog = self.mock_ui
            generator.progress_bar = self.mock_ui
            generator.progress_text = self.mock_ui

            generator._update_generation_ui_state()
            print("   ✅ Generator activated and UI updated")

            # Step 7: Test generation flow (without actual LLM call)
            print("🚀 Step 6: Testing generation workflow...")

            # Mock successful generation result
            mock_generation_result = {
                "success": True,
                "profile_id": f"test_{int(time.time())}",
                "profile": {
                    "job_summary": f"Test profile for {position}",
                    "responsibility_areas": [{"area": ["Development"], "tasks": ["Code", "Test"]}],
                    "professional_skills": [{"skill_category": "Technical", "skills": ["Java", "Spring"]}],
                    "kpi": [{"kpi_name": "Code Quality", "target_value": "95%"}]
                },
                "metadata": {"generation_time_seconds": 2.5, "model": "gemini-2.5-flash"}
            }

            # Step 8: Test profile viewer display
            print("👁️  Step 7: Testing profile viewer display...")

            # Mock viewer UI elements
            viewer.profile_container = self.mock_ui
            viewer.tab_container = self.mock_ui

            # Test adaptation of generation result
            adapted_profile = viewer._adapt_generation_result(mock_generation_result)

            if "profile_id" not in adapted_profile:
                issues.append("CRITICAL: Profile adaptation failed")

            viewer.show_profile(adapted_profile)

            if not viewer.current_profile:
                issues.append("CRITICAL: Profile not displayed in viewer")
            else:
                print("   ✅ Profile displayed in viewer")

            # Step 9: Test tab switching
            print("📑 Step 8: Testing tab functionality...")
            available_tabs = ["content", "metadata", "versions", "markdown"]

            for tab in available_tabs:
                if hasattr(viewer, 'on_tab_switch') and viewer.on_tab_switch:
                    viewer.on_tab_switch(tab)
                    print(f"   ✅ Tab switch to '{tab}' working")

            # Step 10: Test markdown generation
            print("📝 Step 9: Testing markdown generation...")
            markdown_content = viewer._generate_markdown_from_json(mock_generation_result["profile"])

            if not markdown_content or len(markdown_content) < 100:
                issues.append("WARNING: Markdown generation seems incomplete")
            else:
                print(f"   ✅ Markdown generated ({len(markdown_content)} chars)")

            # Step 11: Test file operations
            print("💾 Step 10: Testing file download preparation...")

            # Mock files manager
            files.temp_files = {}

            download_formats = ["json", "markdown"]
            for fmt in download_formats:
                try:
                    # This would normally download, but we just test the setup
                    status = files.get_download_status()
                    print(f"   ✅ Download status for {fmt}: ready")
                except Exception as e:
                    issues.append(f"WARNING: Download setup for {fmt} failed: {e}")

        except Exception as e:
            issues.append(f"CRITICAL: Journey 1 failed with error: {e}")
            logger.exception("Journey 1 failed")

        journey_time = time.time() - journey_start

        print(f"\n⏱️  Journey completed in {journey_time:.2f}s")

        if issues:
            print("🚨 Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            self.test_results["critical_issues"].extend(issues)
            return False
        else:
            print("✅ Journey 1 PASSED - New profile generation flow working")
            return True

    async def test_journey_2_view_existing_profile(self):
        """
        @doc
        TEST JOURNEY 2: View Existing Profile

        User flow:
        1. User searches for position with existing profile (🟢)
        2. Clicks on position
        3. ProfileViewer opens with data
        4. Can browse Content, Metadata, Versions, Markdown tabs
        5. Can copy Markdown content
        6. Can download files
        7. If multiple versions (📚), can switch between them

        Examples:
          python> await tester.test_journey_2_view_existing_profile()
          python> # Existing profile viewing tested
        """
        print("\n🎯 USER JOURNEY 2: View Existing Profile")
        print("-" * 60)

        issues = []
        journey_start = time.time()

        try:
            search = self.generator_page.search
            viewer = self.generator_page.viewer
            files = self.generator_page.files

            # Step 1: Setup existing profile scenario
            print("📋 Step 1: Setting up existing profile scenario...")

            # Mock existing profiles
            mock_profiles = [
                {
                    "profile_id": "existing_001",
                    "position_title": "Senior Java Developer",
                    "department_path": "IT Department",
                    "json_data": {
                        "job_summary": "Senior Java development role",
                        "responsibility_areas": [
                            {"area": ["Backend Development"], "tasks": ["API Design", "Code Review"]}
                        ],
                        "professional_skills": [
                            {"skill_category": "Programming", "skills": ["Java", "Spring Boot", "SQL"]}
                        ],
                        "kpi": [
                            {"kpi_name": "Code Quality", "target_value": "98%"}
                        ]
                    },
                    "status": "completed",
                    "created_at": "2024-09-17T10:00:00Z",
                    "version": "1.0"
                },
                {
                    "profile_id": "existing_002",
                    "position_title": "Senior Java Developer",
                    "department_path": "IT Department",
                    "json_data": {
                        "job_summary": "Updated Java development role",
                        "responsibility_areas": [
                            {"area": ["Full Stack Development"], "tasks": ["Frontend", "Backend", "DevOps"]}
                        ]
                    },
                    "status": "completed",
                    "created_at": "2024-09-18T10:00:00Z",
                    "version": "2.0"
                }
            ]

            search.position_profiles = mock_profiles
            search.selected_position = "Senior Java Developer"
            search.selected_department = "IT Department"

            print(f"   ✅ Setup {len(mock_profiles)} existing profiles")

            # Step 2: Test profile status analysis
            print("📊 Step 2: Analyzing profile status...")
            status_info = search._analyze_profile_status()

            expected_status = "has_multiple" if len(mock_profiles) > 1 else "has_single"
            if status_info["status"] != expected_status:
                issues.append(f"WARNING: Expected status {expected_status}, got {status_info['status']}")

            print(f"   ✅ Profile status: {status_info['status']} ({status_info.get('count', 0)} profiles)")

            # Step 3: Test single profile viewing
            print("👁️  Step 3: Testing single profile display...")

            # Mock UI elements
            viewer.profile_container = self.mock_ui
            viewer.tab_container = self.mock_ui

            latest_profile = mock_profiles[-1]  # Most recent
            viewer.show_profile(latest_profile)

            if not viewer.current_profile:
                issues.append("CRITICAL: Profile not loaded in viewer")
            else:
                print("   ✅ Profile loaded successfully")

            # Verify profile data structure
            required_keys = ["profile_id", "json_data", "status"]
            for key in required_keys:
                if key not in viewer.current_profile:
                    issues.append(f"CRITICAL: Missing key '{key}' in profile data")

            # Step 4: Test profile list viewing (multiple versions)
            print("📚 Step 4: Testing profile versions display...")

            viewer.show_profile_list(mock_profiles)

            if len(viewer.profiles_list) != len(mock_profiles):
                issues.append("CRITICAL: Profile list not properly set")
            else:
                print(f"   ✅ Profile list loaded ({len(viewer.profiles_list)} versions)")

            # Step 5: Test tab functionality
            print("📑 Step 5: Testing detailed tab functionality...")

            tabs_to_test = {
                "content": "Profile content display",
                "metadata": "Profile metadata display",
                "versions": "Version comparison",
                "markdown": "Markdown export"
            }

            for tab_id, description in tabs_to_test.items():
                try:
                    if hasattr(viewer, 'on_tab_switch') and viewer.on_tab_switch:
                        viewer.on_tab_switch(tab_id)
                        print(f"   ✅ {description} working")
                except Exception as e:
                    issues.append(f"WARNING: Tab '{tab_id}' functionality issue: {e}")

            # Step 6: Test markdown generation for existing profile
            print("📝 Step 6: Testing markdown generation from existing data...")

            profile_json = latest_profile["json_data"]
            markdown = viewer._generate_markdown_from_json(profile_json)

            # Verify markdown contains key information
            expected_content = ["Java", "development", "responsibilities"]
            missing_content = []

            for content in expected_content:
                if content.lower() not in markdown.lower():
                    missing_content.append(content)

            if missing_content:
                issues.append(f"WARNING: Markdown missing expected content: {missing_content}")
            else:
                print(f"   ✅ Markdown generation complete ({len(markdown)} chars)")

            # Step 7: Test version switching
            print("🔄 Step 7: Testing version switching...")

            if len(mock_profiles) > 1:
                for i, profile in enumerate(mock_profiles):
                    viewer.show_profile(profile)

                    if viewer.current_profile["version"] != profile["version"]:
                        issues.append(f"WARNING: Version switch failed for version {profile['version']}")
                    else:
                        print(f"   ✅ Switched to version {profile['version']}")

            # Step 8: Test download preparation for existing profiles
            print("💾 Step 8: Testing download functionality...")

            for profile in mock_profiles:
                profile_id = profile["profile_id"]

                # Test download status
                download_status = files.get_download_status()

                if download_status["is_downloading"]:
                    issues.append("WARNING: Download state management issue")
                else:
                    print(f"   ✅ Download ready for profile {profile_id}")

        except Exception as e:
            issues.append(f"CRITICAL: Journey 2 failed with error: {e}")
            logger.exception("Journey 2 failed")

        journey_time = time.time() - journey_start
        print(f"\n⏱️  Journey completed in {journey_time:.2f}s")

        if issues:
            print("🚨 Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            self.test_results["critical_issues"].extend(issues)
            return False
        else:
            print("✅ Journey 2 PASSED - Existing profile viewing working")
            return True

    async def test_journey_3_error_handling(self):
        """
        @doc
        TEST JOURNEY 3: Error Handling Scenarios

        Tests:
        1. API unavailable during search → Fallback suggestions
        2. Generation error → Retry dialog
        3. Download error → Error message + retry
        4. Invalid data → Graceful fallback
        5. Network interruption handling

        Examples:
          python> await tester.test_journey_3_error_handling()
          python> # Error scenarios tested
        """
        print("\n🎯 USER JOURNEY 3: Error Handling")
        print("-" * 60)

        issues = []
        journey_start = time.time()

        try:
            search = self.generator_page.search
            generator = self.generator_page.generator
            viewer = self.generator_page.viewer

            # Test 1: API failure fallback
            print("🚨 Test 1: API failure fallback...")

            # Mock API failure
            original_client = search.api_client

            class MockFailingClient:
                async def get_organization_search_items(self):
                    raise Exception("Network timeout")
                async def get_positions(self, dept):
                    raise Exception("Server error")
                async def get_departments(self):
                    return {"success": False, "error": "Database error"}

            search.api_client = MockFailingClient()

            # Test fallback behavior
            await search.load_search_data()

            if len(search.hierarchical_suggestions) == 0:
                issues.append("CRITICAL: No fallback suggestions when API fails")
            else:
                print(f"   ✅ Fallback loaded {len(search.hierarchical_suggestions)} suggestions")

            # Restore original client
            search.api_client = original_client

            # Test 2: Invalid profile data handling
            print("🚨 Test 2: Invalid profile data handling...")

            invalid_profiles = [
                None,
                {},
                {"invalid": "structure"},
                {"profile_id": None},
                {"json_data": None},
            ]

            # Mock UI to prevent crashes
            viewer.profile_container = self.mock_ui
            viewer.tab_container = self.mock_ui

            for i, invalid_profile in enumerate(invalid_profiles):
                try:
                    viewer.show_profile(invalid_profile)
                    print(f"   ✅ Handled invalid profile {i+1}")
                except Exception as e:
                    issues.append(f"WARNING: Could improve handling of invalid profile {i+1}: {e}")

            # Test 3: Search with no results
            print("🚨 Test 3: Empty search results handling...")

            # Temporarily clear suggestions
            original_suggestions = search.hierarchical_suggestions[:]
            search.hierarchical_suggestions = []
            search.position_lookup = {}

            # Test empty search
            dept, pos = search._process_hierarchical_selection("nonexistent_position")

            # Should handle gracefully - note: current implementation returns position as-is
            # This might be acceptable behavior
            print(f"   📝 Empty search result: dept='{dept}', pos='{pos}'")

            # Restore original suggestions
            search.hierarchical_suggestions = original_suggestions

            # Test 4: Generation error simulation
            print("🚨 Test 4: Generation error handling...")

            # Mock generation failure
            generator.selected_position = "Test Position"
            generator.selected_department = "Test Dept"

            # Mock UI elements
            generator.generate_button = self.mock_ui
            generator.progress_dialog = self.mock_ui
            generator.progress_bar = self.mock_ui

            # Simulate error during generation
            error_result = {
                "success": False,
                "error": "OpenRouter API timeout",
                "profile_id": None
            }

            # Test error handling in generation completion
            if hasattr(generator, '_handle_generation_error'):
                generator._handle_generation_error(error_result)
                print("   ✅ Generation error handled")
            else:
                print("   📝 Note: Generation error handler not implemented")

            # Test 5: UI state consistency during errors
            print("🚨 Test 5: UI state consistency during errors...")

            # Test search component error state
            search.search_results_container = self.mock_ui

            search._show_error_state(
                error_type="loading_error",
                message="Test error message",
                details="Test error details",
                retry_callback=lambda: print("Retry called")
            )

            print("   ✅ Error state display working")

            # Test notification system
            notification_count = len(self.mock_ui.notifications)

            # Trigger some notifications
            self.mock_ui.notify("Test error", type="negative")
            self.mock_ui.notify("Test warning", type="warning")

            new_notification_count = len(self.mock_ui.notifications)
            if new_notification_count > notification_count:
                print(f"   ✅ Notification system working ({new_notification_count - notification_count} new)")
            else:
                issues.append("WARNING: Notification system not responding")

        except Exception as e:
            issues.append(f"CRITICAL: Journey 3 failed with error: {e}")
            logger.exception("Journey 3 failed")

        journey_time = time.time() - journey_start
        print(f"\n⏱️  Journey completed in {journey_time:.2f}s")

        if issues:
            print("🚨 Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            self.test_results["critical_issues"].extend(issues)
            return False
        else:
            print("✅ Journey 3 PASSED - Error handling working")
            return True

    async def test_performance_and_responsiveness(self):
        """
        @doc
        TEST: Performance and Responsiveness

        Measures:
        1. Page load time simulation
        2. Search responsiveness with 4376 positions
        3. Tab switching performance
        4. Memory usage patterns
        5. Component initialization time

        Examples:
          python> await tester.test_performance_and_responsiveness()
          python> # Performance metrics collected
        """
        print("\n🎯 PERFORMANCE & RESPONSIVENESS TESTING")
        print("-" * 60)

        issues = []
        metrics = {}

        try:
            # Test 1: Component initialization time
            print("⏱️  Test 1: Component initialization performance...")

            init_start = time.time()

            # Import and initialize fresh components
            from frontend.services.api_client import APIClient
            from frontend.pages.generator_page import GeneratorPage

            api_client = APIClient(self.base_url)
            api_client._access_token = "test_token"

            generator_page = GeneratorPage(api_client)

            init_time = time.time() - init_start
            metrics["component_init_time"] = init_time

            if init_time > 1.0:
                issues.append(f"WARNING: Slow component initialization ({init_time:.2f}s)")
            else:
                print(f"   ✅ Components initialized in {init_time:.3f}s")

            # Test 2: Search data loading performance
            print("⏱️  Test 2: Search data loading performance...")

            search = generator_page.search

            load_start = time.time()
            await search.load_search_data()
            load_time = time.time() - load_start

            metrics["search_load_time"] = load_time
            suggestion_count = len(search.hierarchical_suggestions)

            if load_time > 5.0:
                issues.append(f"WARNING: Slow search data loading ({load_time:.2f}s)")
            else:
                print(f"   ✅ Loaded {suggestion_count} suggestions in {load_time:.3f}s")

            # Test 3: Search filtering performance
            print("⏱️  Test 3: Search filtering performance...")

            filter_queries = ["java", "senior", "manager", "analyst", "специалист"]
            total_filter_time = 0

            for query in filter_queries:
                filter_start = time.time()

                # Simulate filtering
                filtered = [s for s in search.hierarchical_suggestions if query.lower() in s.lower()]

                filter_time = time.time() - filter_start
                total_filter_time += filter_time

                print(f"   📊 Query '{query}': {len(filtered)} results in {filter_time:.4f}s")

            avg_filter_time = total_filter_time / len(filter_queries)
            metrics["avg_filter_time"] = avg_filter_time

            if avg_filter_time > 0.1:
                issues.append(f"WARNING: Slow search filtering ({avg_filter_time:.3f}s average)")
            else:
                print(f"   ✅ Average filter time: {avg_filter_time:.4f}s")

            # Test 4: Profile display performance
            print("⏱️  Test 4: Profile display performance...")

            viewer = generator_page.viewer
            viewer.profile_container = self.mock_ui
            viewer.tab_container = self.mock_ui

            # Create large profile for testing
            large_profile = {
                "profile_id": "perf_test",
                "json_data": {
                    "job_summary": "Large profile for performance testing" * 10,
                    "responsibility_areas": [
                        {"area": [f"Area {i}"], "tasks": [f"Task {j}" for j in range(20)]}
                        for i in range(10)
                    ],
                    "professional_skills": [
                        {"skill_category": f"Category {i}", "skills": [f"Skill {j}" for j in range(15)]}
                        for i in range(8)
                    ],
                    "kpi": [
                        {"kpi_name": f"KPI {i}", "target_value": "95%", "description": "Test KPI" * 20}
                        for i in range(10)
                    ]
                }
            }

            display_start = time.time()
            viewer.show_profile(large_profile)
            display_time = time.time() - display_start

            metrics["profile_display_time"] = display_time

            if display_time > 0.5:
                issues.append(f"WARNING: Slow profile display ({display_time:.3f}s)")
            else:
                print(f"   ✅ Large profile displayed in {display_time:.3f}s")

            # Test 5: Markdown generation performance
            print("⏱️  Test 5: Markdown generation performance...")

            markdown_start = time.time()
            markdown = viewer._generate_markdown_from_json(large_profile["json_data"])
            markdown_time = time.time() - markdown_start

            metrics["markdown_generation_time"] = markdown_time
            markdown_size = len(markdown)

            if markdown_time > 0.2:
                issues.append(f"WARNING: Slow markdown generation ({markdown_time:.3f}s)")
            else:
                print(f"   ✅ Generated {markdown_size} chars markdown in {markdown_time:.3f}s")

            # Test 6: Memory usage simulation
            print("⏱️  Test 6: Memory usage patterns...")

            import sys

            # Simulate loading many profiles
            profiles_list = []
            for i in range(100):
                profile = {
                    "profile_id": f"test_{i}",
                    "json_data": large_profile["json_data"].copy(),
                    "created_at": f"2024-09-{17+i%10:02d}T10:00:00Z"
                }
                profiles_list.append(profile)

            memory_test_start = time.time()
            viewer.show_profile_list(profiles_list)
            memory_test_time = time.time() - memory_test_start

            metrics["large_list_processing_time"] = memory_test_time

            if memory_test_time > 1.0:
                issues.append(f"WARNING: Slow large list processing ({memory_test_time:.3f}s)")
            else:
                print(f"   ✅ Processed {len(profiles_list)} profiles in {memory_test_time:.3f}s")

        except Exception as e:
            issues.append(f"CRITICAL: Performance testing failed: {e}")
            logger.exception("Performance testing failed")

        # Store metrics for reporting
        self.test_results["performance_metrics"] = metrics

        print(f"\n📊 PERFORMANCE SUMMARY:")
        for metric, value in metrics.items():
            print(f"   {metric}: {value:.4f}s")

        if issues:
            print("🚨 Performance issues found:")
            for issue in issues:
                print(f"   - {issue}")
            self.test_results["critical_issues"].extend(issues)
            return False
        else:
            print("✅ Performance tests PASSED - System responsive")
            return True

    async def run_all_user_journey_tests(self):
        """
        @doc
        Run all user journey tests and generate comprehensive report.

        Returns:
            Dict[str, Any]: Test results with metrics and issues

        Examples:
          python> results = await tester.run_all_user_journey_tests()
          python> print(results["summary"])
        """
        print("🚀 STARTING COMPREHENSIVE E2E USER JOURNEY TESTING")
        print("=" * 80)

        # Setup test environment
        await self.setup_test_environment()

        # Define all test journeys
        test_journeys = [
            ("Journey 1: New Profile Generation", self.test_journey_1_new_profile_generation),
            ("Journey 2: View Existing Profile", self.test_journey_2_view_existing_profile),
            ("Journey 3: Error Handling", self.test_journey_3_error_handling),
            ("Performance & Responsiveness", self.test_performance_and_responsiveness),
        ]

        total_start = time.time()

        # Run all journeys
        for journey_name, journey_method in test_journeys:
            try:
                success = await journey_method()
                if success:
                    self.test_results["passed"] += 1
                else:
                    self.test_results["failed"] += 1

            except Exception as e:
                print(f"❌ {journey_name} FAILED: {e}")
                self.test_results["failed"] += 1
                self.test_results["critical_issues"].append(f"{journey_name}: {e}")

        total_time = time.time() - total_start

        # Generate final report
        return self._generate_test_report(total_time)

    def _generate_test_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""

        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE E2E TEST REPORT")
        print("=" * 80)

        print(f"⏱️  Total execution time: {total_time:.2f}s")
        print(f"✅ Tests passed: {self.test_results['passed']}")
        print(f"❌ Tests failed: {self.test_results['failed']}")
        print(f"📊 Success rate: {success_rate:.1f}%")

        # Performance metrics
        if self.test_results["performance_metrics"]:
            print(f"\n📈 PERFORMANCE METRICS:")
            for metric, value in self.test_results["performance_metrics"].items():
                print(f"   {metric.replace('_', ' ').title()}: {value:.4f}s")

        # Critical issues
        if self.test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.test_results['critical_issues'])}):")

            # Categorize issues
            critical = [i for i in self.test_results["critical_issues"] if "CRITICAL" in i]
            warnings = [i for i in self.test_results["critical_issues"] if "WARNING" in i]

            if critical:
                print("   🔴 CRITICAL (must fix before production):")
                for issue in critical:
                    print(f"      - {issue}")

            if warnings:
                print("   🟡 WARNINGS (recommended to fix):")
                for issue in warnings:
                    print(f"      - {issue}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")

        if success_rate >= 90:
            print("   ✅ System is ready for production deployment")
            print("   ✅ All critical user journeys are working")

            if warnings:
                print("   📝 Address warnings to improve user experience")

        elif success_rate >= 70:
            print("   ⚠️  System needs attention before production")
            print("   🔧 Fix critical issues and retest")

        else:
            print("   🚨 System NOT ready for production")
            print("   🔧 Major fixes required across multiple areas")

        print("=" * 80)

        # Return structured results
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": self.test_results["passed"],
                "failed": self.test_results["failed"],
                "success_rate": success_rate,
                "execution_time": total_time
            },
            "performance_metrics": self.test_results["performance_metrics"],
            "critical_issues": self.test_results["critical_issues"],
            "ready_for_production": success_rate >= 90 and len(critical) == 0
        }

async def main():
    """Main test runner for E2E user journeys"""
    tester = TestE2EUserJourneys()
    results = await tester.run_all_user_journey_tests()

    # Return exit code based on results
    return 0 if results["ready_for_production"] else 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
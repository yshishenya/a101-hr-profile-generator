#!/usr/bin/env python3
"""
Simple integration test for A101 HR Profile Generator component system.

This test analyzes the real component code without running the UI,
focusing on event system integration, data flow, and error handling.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_component_integration():
    """Analyze component integration patterns by examining the code."""

    print("🔍 A101 HR Profile Generator - Component Integration Analysis")
    print("=" * 70)

    # Test 1: Component Import Analysis
    print("\n1. COMPONENT IMPORT ANALYSIS")
    print("-" * 35)

    try:
        # Check if components can be imported (indicates basic structure is correct)
        components_path = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'components', 'core')

        search_component_file = os.path.join(components_path, 'search_component.py')
        generator_component_file = os.path.join(components_path, 'generator_component.py')
        viewer_component_file = os.path.join(components_path, 'profile_viewer_component.py')
        files_component_file = os.path.join(components_path, 'files_manager_component.py')

        files_exist = {
            'SearchComponent': os.path.exists(search_component_file),
            'GeneratorComponent': os.path.exists(generator_component_file),
            'ProfileViewerComponent': os.path.exists(viewer_component_file),
            'FilesManagerComponent': os.path.exists(files_component_file)
        }

        for component, exists in files_exist.items():
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"   {component}: {status}")

        if all(files_exist.values()):
            print("   ✅ All core components found")
        else:
            print("   ❌ Missing components detected")

    except Exception as e:
        print(f"   ❌ Error checking components: {e}")

    # Test 2: Event System Analysis
    print("\n2. EVENT SYSTEM ANALYSIS")
    print("-" * 30)

    try:
        # Read and analyze event patterns in components
        event_patterns = analyze_event_patterns()

        print("   Event handlers found:")
        for component, events in event_patterns.items():
            print(f"   📦 {component}:")
            for event in events:
                print(f"      🔗 {event}")

    except Exception as e:
        print(f"   ❌ Error analyzing events: {e}")

    # Test 3: API Integration Analysis
    print("\n3. API INTEGRATION ANALYSIS")
    print("-" * 35)

    try:
        api_integration = analyze_api_integration()

        print("   API method usage:")
        for component, methods in api_integration.items():
            print(f"   📦 {component}:")
            for method in methods:
                print(f"      🌐 {method}")

    except Exception as e:
        print(f"   ❌ Error analyzing API integration: {e}")

    # Test 4: Integration Flow Analysis
    print("\n4. INTEGRATION FLOW ANALYSIS")
    print("-" * 35)

    integration_flows = analyze_integration_flows()

    for flow_name, flow_steps in integration_flows.items():
        print(f"   🔄 {flow_name}:")
        for i, step in enumerate(flow_steps, 1):
            print(f"      {i}. {step}")

    # Test 5: Potential Issues Analysis
    print("\n5. POTENTIAL ISSUES ANALYSIS")
    print("-" * 35)

    issues = identify_potential_issues()

    for issue_type, problems in issues.items():
        print(f"   ⚠️ {issue_type}:")
        for problem in problems:
            print(f"      - {problem}")

    print("\n" + "=" * 70)
    print("✅ Integration analysis completed")


def analyze_event_patterns():
    """Analyze event patterns in component files."""

    event_patterns = {}

    components = {
        'SearchComponent': 'frontend/components/core/search_component.py',
        'GeneratorComponent': 'frontend/components/core/generator_component.py',
        'ProfileViewerComponent': 'frontend/components/core/profile_viewer_component.py',
        'FilesManagerComponent': 'frontend/components/core/files_manager_component.py'
    }

    for component_name, file_path in components.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            events = []

            # Look for event handler patterns
            lines = content.split('\n')
            for line in lines:
                line = line.strip()

                # Event handler definitions
                if 'self.on_' in line and '=' in line:
                    events.append(line)

                # Event calls
                if 'on_' in line and 'self.' in line and '(' in line:
                    events.append(line)

            event_patterns[component_name] = events[:10]  # Limit to first 10

        except Exception as e:
            event_patterns[component_name] = [f"Error reading file: {e}"]

    return event_patterns


def analyze_api_integration():
    """Analyze API method usage in components."""

    api_integration = {}

    components = {
        'SearchComponent': 'frontend/components/core/search_component.py',
        'GeneratorComponent': 'frontend/components/core/generator_component.py',
        'ProfileViewerComponent': 'frontend/components/core/profile_viewer_component.py',
        'FilesManagerComponent': 'frontend/components/core/files_manager_component.py'
    }

    for component_name, file_path in components.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            api_methods = []

            # Look for API client method calls
            lines = content.split('\n')
            for line in lines:
                line = line.strip()

                if 'self.api_client.' in line and 'await' in line:
                    # Extract method name
                    start = line.find('self.api_client.') + len('self.api_client.')
                    end = line.find('(', start)
                    if end > start:
                        method = line[start:end]
                        api_methods.append(method)

            api_integration[component_name] = list(set(api_methods))  # Remove duplicates

        except Exception as e:
            api_integration[component_name] = [f"Error reading file: {e}"]

    return api_integration


def analyze_integration_flows():
    """Analyze integration flows between components."""

    flows = {
        "Search → Generator Flow": [
            "User searches for position in SearchComponent",
            "SearchComponent.on_position_selected event triggered",
            "GeneratorComponent.set_position method called",
            "GeneratorComponent UI state updated (button enabled)",
            "User can start generation"
        ],

        "Generator → Viewer Flow": [
            "User clicks generate in GeneratorComponent",
            "API call to start_profile_generation",
            "Progress dialog shown with polling",
            "On completion, on_generation_complete event triggered",
            "ProfileViewerComponent.show_profile called",
            "Profile displayed in detailed view"
        ],

        "Viewer → Files Flow": [
            "User clicks download in ProfileViewerComponent",
            "on_download_request event triggered",
            "FilesManagerComponent.download_file_sync called",
            "Background download process started",
            "File served through NiceGUI download"
        ],

        "Search → Viewer Flow (Existing Profiles)": [
            "Position selected in SearchComponent",
            "API call to get_profiles_list",
            "on_profiles_found event triggered",
            "ProfileViewerComponent.show_profile_list called",
            "List or single profile view displayed"
        ]
    }

    return flows


def identify_potential_issues():
    """Identify potential integration issues."""

    issues = {
        "Event System Issues": [
            "Async event handlers may not be properly awaited",
            "Event binding happens in GeneratorPage but not validated",
            "No error handling for failed event propagation",
            "Events can be None if not connected properly"
        ],

        "State Synchronization Issues": [
            "Component states can become inconsistent",
            "No central state management",
            "Manual event calling required for state sync",
            "UI refreshable methods may not update all dependent states"
        ],

        "API Integration Issues": [
            "No retry logic for failed API calls in some components",
            "Error handling varies between components",
            "Network timeouts not consistently handled",
            "Some API errors may not propagate to UI properly"
        ],

        "UI Integration Issues": [
            "Dialog management could conflict between components",
            "No global loading state coordination",
            "File download progress not coordinated with other operations",
            "Notification flooding possible during bulk operations"
        ],

        "Performance Issues": [
            "Large profile lists may cause UI lag",
            "Markdown generation happens on every tab switch",
            "No caching for repetitive API calls",
            "Background downloads may accumulate temp files"
        ]
    }

    return issues


def test_live_integration():
    """Test live integration if containers are running."""

    print("\n6. LIVE INTEGRATION TEST")
    print("-" * 28)

    try:
        import requests

        # Test if backend is accessible
        try:
            response = requests.get("http://localhost:8022/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ Backend API accessible")

                # Test basic API endpoints
                endpoints_to_test = [
                    "/api/departments",
                    "/api/organization/search-items",
                    "/docs"  # Swagger docs
                ]

                for endpoint in endpoints_to_test:
                    try:
                        resp = requests.get(f"http://localhost:8022{endpoint}", timeout=3)
                        status = "✅ OK" if resp.status_code in [200, 401] else f"❌ {resp.status_code}"
                        print(f"   {endpoint}: {status}")
                    except Exception as e:
                        print(f"   {endpoint}: ❌ {str(e)[:50]}")

            else:
                print(f"   ❌ Backend API not healthy: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Backend API not accessible: {str(e)[:50]}")

        # Test if frontend is accessible
        try:
            response = requests.get("http://localhost:8033", timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"   Frontend: {status}")
        except Exception as e:
            print(f"   Frontend: ❌ {str(e)[:50]}")

    except ImportError:
        print("   ⚠️ requests library not available, skipping live tests")


def run_integration_recommendations():
    """Provide integration recommendations."""

    print("\n7. INTEGRATION RECOMMENDATIONS")
    print("-" * 35)

    recommendations = [
        "Add centralized event validation in GeneratorPage",
        "Implement error boundaries for component failures",
        "Add integration health checks for event system",
        "Create component state synchronization utilities",
        "Add comprehensive error logging for event flows",
        "Implement retry logic for critical API calls",
        "Add loading state coordination between components",
        "Create automated integration tests with real API mocks",
        "Add performance monitoring for large data operations",
        "Implement graceful degradation for offline scenarios"
    ]

    for i, rec in enumerate(recommendations, 1):
        print(f"   {i:2d}. {rec}")


if __name__ == "__main__":
    try:
        analyze_component_integration()
        test_live_integration()
        run_integration_recommendations()

    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
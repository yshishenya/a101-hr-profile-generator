#!/usr/bin/env python3
"""
Минимальный тест для проверки событийной системы компонентов.
"""

import sys
import os
import asyncio

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'frontend'))

from frontend.services.api_client import APIClient
from frontend.components.core.search_component import SearchComponent
from frontend.components.core.generator_component import GeneratorComponent
from frontend.components.core.profile_viewer_component import ProfileViewerComponent

async def test_component_initialization():
    """Test component initialization and event connections."""
    print("🧪 Testing component initialization and events...")

    # Initialize API client
    api_client = APIClient(base_url="http://localhost:8022")

    # Initialize components
    search = SearchComponent(api_client)
    generator = GeneratorComponent(api_client)
    viewer = ProfileViewerComponent(api_client)

    print(f"✅ Components initialized:")
    print(f"   - SearchComponent: {search}")
    print(f"   - GeneratorComponent: {generator}")
    print(f"   - ProfileViewerComponent: {viewer}")

    # Test event connections
    print(f"\n🔗 Testing event connections...")

    # Check if components have required methods
    if hasattr(generator, 'set_position'):
        print(f"✅ GeneratorComponent.set_position exists")
        search.on_position_selected = generator.set_position
        print(f"✅ Connected search.on_position_selected to generator.set_position")
    else:
        print(f"❌ GeneratorComponent.set_position NOT FOUND!")

    if hasattr(viewer, 'show_profile_list'):
        print(f"✅ ProfileViewerComponent.show_profile_list exists")
        search.on_profiles_found = viewer.show_profile_list
        print(f"✅ Connected search.on_profiles_found to viewer.show_profile_list")
    else:
        print(f"❌ ProfileViewerComponent.show_profile_list NOT FOUND!")

    # Test event callbacks
    print(f"\n🎯 Testing event callbacks...")
    print(f"search.on_position_selected = {search.on_position_selected}")
    print(f"search.on_profiles_found = {search.on_profiles_found}")

    # Simulate position selection event
    if search.on_position_selected:
        print(f"\n🔥 Simulating position selection event...")
        try:
            search.on_position_selected("Директор по информационным технологиям", "Департамент информационных технологий")
            print(f"✅ Position selection event fired successfully!")
        except Exception as e:
            print(f"❌ Position selection event failed: {e}")

    # Simulate profiles found event
    if search.on_profiles_found:
        print(f"\n🔥 Simulating profiles found event...")
        test_profiles_data = {
            "profiles": [{"position": "Test Position", "department": "Test Department"}],
            "status": {"status": "has_single", "action": "view"},
            "position": "Test Position",
            "department": "Test Department"
        }
        try:
            search.on_profiles_found(test_profiles_data)
            print(f"✅ Profiles found event fired successfully!")
        except Exception as e:
            print(f"❌ Profiles found event failed: {e}")

    print(f"\n🏁 Component event system test completed!")

if __name__ == "__main__":
    asyncio.run(test_component_initialization())
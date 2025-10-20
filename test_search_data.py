#!/usr/bin/env python3
"""
Тест загрузки данных поиска и обработки UI событий.
"""

import sys
import os
import asyncio

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'frontend'))

from frontend.services.api_client import APIClient
from frontend.components.core.search_component import SearchComponent

async def test_search_data_loading():
    """Test search data loading and UI event processing."""
    print("🔍 Testing search data loading...")

    # Initialize API client with auth token
    api_client = APIClient(base_url="http://localhost:8022")

    # Set auth token for testing
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsImZ1bGxfbmFtZSI6Ilx1MDQxMFx1MDQzNFx1MDQzY1x1MDQzOFx1MDQzZFx1MDQzOFx1MDQ0MVx1MDQ0Mlx1MDQ0MFx1MDQzMFx1MDQ0Mlx1MDQzZVx1MDQ0MCBcdTA0NDFcdTA0MzhcdTA0NDFcdTA0NDJcdTA0MzVcdTA0M2NcdTA0NGIiLCJleHAiOjE3NTg4MDk3MTEsImlhdCI6MTc1ODcyMzMxMSwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.AQgbzWvnCNlLEKXKQ-jUuWL8aJ16_oITnuAoYUVGLHo"
    api_client.token = token
    api_client.headers = {"Authorization": f"Bearer {token}"}

    # Initialize search component
    search = SearchComponent(api_client)

    print(f"✅ SearchComponent initialized: {search}")

    # Test API call directly
    print(f"\n📡 Testing direct API call...")
    try:
        response = await api_client.get_organization_search_items()
        if response and response.get("success"):
            items_count = len(response["data"]["items"])
            print(f"✅ API call successful: {items_count} items received")
        else:
            print(f"❌ API call failed: {response}")
    except Exception as e:
        print(f"❌ API call error: {e}")

    # Test search data loading
    print(f"\n📥 Testing search data loading through component...")
    try:
        await search._load_hierarchical_suggestions()
        suggestions_count = len(search.hierarchical_suggestions)
        print(f"✅ Search suggestions loaded: {suggestions_count} suggestions")

        # Show first few suggestions
        print(f"📝 First 5 suggestions:")
        for i, suggestion in enumerate(search.hierarchical_suggestions[:5]):
            print(f"   {i+1}. {suggestion}")

    except Exception as e:
        print(f"❌ Search data loading error: {e}")

    # Test position lookup
    print(f"\n🔍 Testing position lookup...")
    lookup_count = len(search.position_lookup)
    print(f"✅ Position lookup populated: {lookup_count} entries")

    # Look for IT director position
    it_director_key = None
    for key, value in search.position_lookup.items():
        if "Директор по информационным технологиям" in value.get("position_name", ""):
            it_director_key = key
            print(f"✅ Found IT Director: '{key}' -> {value}")
            break

    if not it_director_key:
        print(f"❌ IT Director position not found in lookup")

    # Test position selection processing
    print(f"\n⚙️ Testing position selection processing...")
    if it_director_key:
        try:
            department, position = search._process_hierarchical_selection(it_director_key)
            print(f"✅ Position processing successful:")
            print(f"   Department: {department}")
            print(f"   Position: {position}")
        except Exception as e:
            print(f"❌ Position processing error: {e}")

    print(f"\n🏁 Search data loading test completed!")

if __name__ == "__main__":
    asyncio.run(test_search_data_loading())
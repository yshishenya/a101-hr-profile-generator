#!/usr/bin/env python3
"""
Quick API endpoint testing script
"""
import asyncio
import httpx
import json

async def test_api_endpoints():
    print("🔌 Testing API Endpoints")

    # Login to get valid token
    login_data = {"username": "admin", "password": "q4Mrpwty7t9F"}

    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            "http://localhost:8022/api/auth/login",
            json=login_data,
            timeout=10.0
        )

        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return

        data = response.json()
        if not data.get("success"):
            print(f"❌ Login unsuccessful: {data}")
            return

        token = data.get("access_token")
        print(f"✅ Login successful, token length: {len(token)}")

        headers = {"Authorization": f"Bearer {token}"}

        # Test endpoints
        endpoints = [
            "/api/organization/search-items",
            "/api/catalog/departments",
            "/api/profiles/",
            "/api/dashboard/stats/minimal"
        ]

        for endpoint in endpoints:
            try:
                resp = await client.get(f"http://localhost:8022{endpoint}", headers=headers, timeout=10.0)
                print(f"✅ {endpoint}: {resp.status_code}")

                if resp.status_code == 200:
                    result = resp.json()
                    if endpoint == "/api/organization/search-items":
                        items_count = len(result.get("data", {}).get("items", []))
                        print(f"   Search items: {items_count}")
                    elif endpoint == "/api/catalog/departments":
                        dept_count = len(result.get("data", {}).get("departments", []))
                        print(f"   Departments: {dept_count}")
                    elif endpoint == "/api/profiles/":
                        total = result.get("pagination", {}).get("total", 0)
                        print(f"   Total profiles: {total}")
                    elif endpoint == "/api/dashboard/stats/minimal":
                        pos_count = result.get("data", {}).get("positions_count", 0)
                        print(f"   Positions: {pos_count}")

            except Exception as e:
                print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
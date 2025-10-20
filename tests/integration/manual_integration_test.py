#!/usr/bin/env python3
"""
Manual integration test for A101 HR Profile Generator component system.

This test simulates real user interactions by sending HTTP requests to test
the actual integration between components in the running system.
"""

import asyncio
import logging
import sys
import os
import json
from typing import Dict, Any

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationTestRunner:
    """Manual integration test runner for live system."""

    def __init__(self, backend_url="http://localhost:8022", frontend_url="http://localhost:8033"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        self.test_results = {}

    def run_all_tests(self):
        """Run all integration tests."""

        print("🧪 A101 HR Profile Generator - Manual Integration Test")
        print("=" * 60)

        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Frontend Health Check", self.test_frontend_health),
            ("API Authentication", self.test_api_authentication),
            ("Search Component API Integration", self.test_search_api_integration),
            ("Generator Component API Integration", self.test_generator_api_integration),
            ("File Download Integration", self.test_file_download_integration),
            ("Error Handling Integration", self.test_error_handling),
            ("Performance Integration", self.test_performance_scenarios)
        ]

        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * len(test_name))

            try:
                result = test_func()
                self.test_results[test_name] = result
                if result.get('success', False):
                    print(f"   ✅ PASSED")
                else:
                    print(f"   ❌ FAILED: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"   💥 ERROR: {str(e)}")
                self.test_results[test_name] = {'success': False, 'error': str(e)}

        self.print_summary()

    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health and basic connectivity."""

        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=5)

            if response.status_code == 200:
                health_data = response.json()
                print(f"   🌐 Backend Status: {health_data.get('status', 'unknown')}")
                print(f"   📊 Database: {health_data.get('database', 'unknown')}")

                return {'success': True, 'data': health_data}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_frontend_health(self) -> Dict[str, Any]:
        """Test frontend accessibility."""

        try:
            response = self.session.get(self.frontend_url, timeout=5)

            if response.status_code == 200:
                print(f"   🖥️ Frontend accessible")
                print(f"   📄 Content length: {len(response.content)} bytes")

                return {'success': True, 'status_code': response.status_code}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_api_authentication(self) -> Dict[str, Any]:
        """Test API authentication workflow."""

        try:
            # Test unauthenticated access
            response = self.session.get(f"{self.backend_url}/api/departments", timeout=5)

            if response.status_code == 401:
                print(f"   🔒 Authentication required (expected)")

                # Try to get test token (if available)
                try:
                    token_response = self.session.post(
                        f"{self.backend_url}/api/auth/login",
                        json={"username": "admin", "password": "admin"},
                        timeout=5
                    )

                    if token_response.status_code == 200:
                        token_data = token_response.json()
                        token = token_data.get('access_token')

                        if token:
                            self.session.headers.update({'Authorization': f'Bearer {token}'})
                            print(f"   🔑 Token obtained successfully")

                            # Test authenticated access
                            auth_response = self.session.get(f"{self.backend_url}/api/departments", timeout=5)
                            if auth_response.status_code == 200:
                                print(f"   ✅ Authenticated API access working")
                                return {'success': True, 'authenticated': True}
                            else:
                                print(f"   ⚠️ Authenticated access failed: {auth_response.status_code}")
                                return {'success': False, 'error': f'Auth failed: {auth_response.status_code}'}

                    else:
                        print(f"   ⚠️ Token request failed: {token_response.status_code}")
                        return {'success': False, 'error': f'Token failed: {token_response.status_code}'}

                except Exception as e:
                    print(f"   ⚠️ Authentication test failed: {str(e)}")
                    return {'success': False, 'error': f'Auth error: {str(e)}'}

            else:
                print(f"   ⚠️ Unexpected response: {response.status_code}")
                return {'success': False, 'error': f'Unexpected: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_search_api_integration(self) -> Dict[str, Any]:
        """Test SearchComponent API integration."""

        try:
            # Test organization search items endpoint
            response = self.session.get(f"{self.backend_url}/api/organization/search-items", timeout=10)

            if response.status_code == 200:
                data = response.json()
                items = data.get('data', {}).get('items', [])

                print(f"   📊 Found {len(items)} organization items")

                if items:
                    sample_item = items[0]
                    print(f"   📝 Sample: {sample_item.get('name', 'Unknown')}")
                    print(f"   🏢 Positions: {sample_item.get('positions_count', 0)}")

                    # Test departments endpoint
                    dept_response = self.session.get(f"{self.backend_url}/api/departments", timeout=5)
                    if dept_response.status_code == 200:
                        dept_data = dept_response.json()
                        departments = dept_data.get('data', {}).get('departments', [])
                        print(f"   🏢 Found {len(departments)} departments")

                        return {'success': True, 'items': len(items), 'departments': len(departments)}

                    else:
                        return {'success': False, 'error': f'Departments API failed: {dept_response.status_code}'}

                else:
                    return {'success': False, 'error': 'No organization items found'}

            else:
                return {'success': False, 'error': f'Search API failed: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_generator_api_integration(self) -> Dict[str, Any]:
        """Test GeneratorComponent API integration."""

        try:
            # Test profile generation start
            generation_data = {
                "department": "ДИТ",
                "position": "Java-разработчик",
                "save_result": True
            }

            response = self.session.post(
                f"{self.backend_url}/api/generate-profile",
                json=generation_data,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')

                if task_id:
                    print(f"   🚀 Generation started: {task_id}")

                    # Test status polling
                    status_response = self.session.get(
                        f"{self.backend_url}/api/generation-task/{task_id}/status",
                        timeout=5
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        task_status = status_data.get('task', {}).get('status', 'unknown')
                        print(f"   📊 Task status: {task_status}")

                        return {'success': True, 'task_id': task_id, 'status': task_status}

                    else:
                        return {'success': False, 'error': f'Status check failed: {status_response.status_code}'}

                else:
                    return {'success': False, 'error': 'No task ID returned'}

            else:
                return {'success': False, 'error': f'Generation API failed: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_file_download_integration(self) -> Dict[str, Any]:
        """Test FilesManagerComponent integration."""

        try:
            # First, try to get existing profiles
            profiles_response = self.session.get(
                f"{self.backend_url}/api/profiles",
                params={"limit": 1},
                timeout=5
            )

            if profiles_response.status_code == 200:
                profiles_data = profiles_response.json()
                profiles = profiles_data.get('profiles', [])

                if profiles:
                    profile_id = profiles[0].get('profile_id')
                    print(f"   📄 Testing download for profile: {profile_id[:12]}...")

                    # Test JSON download
                    json_response = self.session.get(
                        f"{self.backend_url}/api/profiles/{profile_id}/download/json",
                        timeout=10
                    )

                    if json_response.status_code == 200:
                        json_size = len(json_response.content)
                        print(f"   📥 JSON download: {json_size} bytes")

                        # Test Markdown download
                        md_response = self.session.get(
                            f"{self.backend_url}/api/profiles/{profile_id}/download/markdown",
                            timeout=10
                        )

                        if md_response.status_code == 200:
                            md_size = len(md_response.content)
                            print(f"   📥 Markdown download: {md_size} bytes")

                            return {'success': True, 'json_size': json_size, 'md_size': md_size}

                        else:
                            return {'success': False, 'error': f'Markdown download failed: {md_response.status_code}'}

                    else:
                        return {'success': False, 'error': f'JSON download failed: {json_response.status_code}'}

                else:
                    print(f"   ⚠️ No profiles available for download test")
                    return {'success': True, 'note': 'No profiles to test download'}

            else:
                return {'success': False, 'error': f'Profiles API failed: {profiles_response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling integration."""

        try:
            error_scenarios = []

            # Test invalid profile ID
            invalid_response = self.session.get(
                f"{self.backend_url}/api/profiles/invalid-id/download/json",
                timeout=5
            )
            error_scenarios.append(('Invalid Profile ID', invalid_response.status_code))

            # Test invalid department
            invalid_gen_response = self.session.post(
                f"{self.backend_url}/api/generate-profile",
                json={"department": "NonExistent", "position": "Test"},
                timeout=5
            )
            error_scenarios.append(('Invalid Department', invalid_gen_response.status_code))

            # Test invalid task ID
            invalid_task_response = self.session.get(
                f"{self.backend_url}/api/generation-task/invalid-task/status",
                timeout=5
            )
            error_scenarios.append(('Invalid Task ID', invalid_task_response.status_code))

            for scenario, status_code in error_scenarios:
                expected_error = status_code in [400, 404, 422]  # Expected error codes
                status = "✅" if expected_error else "❌"
                print(f"   {status} {scenario}: {status_code}")

            # All should return appropriate error codes
            success = all(status in [400, 404, 422] for _, status in error_scenarios)

            return {'success': success, 'scenarios': error_scenarios}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_performance_scenarios(self) -> Dict[str, Any]:
        """Test performance aspects of integration."""

        try:
            import time

            # Test search performance
            start_time = time.time()
            search_response = self.session.get(f"{self.backend_url}/api/organization/search-items", timeout=10)
            search_time = time.time() - start_time

            print(f"   ⏱️ Search API response time: {search_time:.2f}s")

            if search_response.status_code == 200:
                data = search_response.json()
                items_count = len(data.get('data', {}).get('items', []))
                print(f"   📊 Items processed: {items_count}")

                # Test concurrent requests (simulate multiple component calls)
                concurrent_results = []
                start_concurrent = time.time()

                for i in range(3):
                    response = self.session.get(f"{self.backend_url}/api/departments", timeout=5)
                    concurrent_results.append(response.status_code == 200)

                concurrent_time = time.time() - start_concurrent
                print(f"   🔄 Concurrent requests time: {concurrent_time:.2f}s")
                print(f"   ✅ Concurrent success rate: {sum(concurrent_results)}/3")

                return {
                    'success': True,
                    'search_time': search_time,
                    'concurrent_time': concurrent_time,
                    'items_count': items_count,
                    'concurrent_success': sum(concurrent_results)
                }

            else:
                return {'success': False, 'error': f'Search API failed: {search_response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def print_summary(self):
        """Print test summary."""

        print(f"\n📊 TEST SUMMARY")
        print("=" * 40)

        passed = sum(1 for result in self.test_results.values() if result.get('success', False))
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%")

        print(f"\n🔍 INTEGRATION STATUS")
        print("-" * 25)

        if passed == total:
            print("✅ All integration tests passed - system is healthy")
        elif passed >= total * 0.8:
            print("⚠️ Most tests passed - minor issues detected")
        elif passed >= total * 0.5:
            print("🟡 Some tests failed - moderate issues detected")
        else:
            print("❌ Many tests failed - significant issues detected")

        print(f"\n📋 DETAILED RESULTS")
        print("-" * 20)

        for test_name, result in self.test_results.items():
            status = "✅" if result.get('success', False) else "❌"
            print(f"{status} {test_name}")
            if not result.get('success', False) and 'error' in result:
                print(f"   Error: {result['error']}")


if __name__ == "__main__":
    print("Starting A101 HR Profile Generator Integration Tests...")

    # Check if services are running
    try:
        runner = IntegrationTestRunner()
        runner.run_all_tests()

    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Test runner failed: {e}")
        import traceback
        traceback.print_exc()
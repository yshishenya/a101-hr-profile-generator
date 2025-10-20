#!/usr/bin/env python3
"""
@doc
Test script for validating A101 HR Profile Generator error recovery mechanisms.

This script tests the comprehensive error recovery infrastructure including:
- Circuit Breaker pattern
- Exponential backoff retry
- API health monitoring
- Component state recovery
- Resource cleanup

Run this script to validate that all error recovery mechanisms work correctly.

Examples:
  python> python test_error_recovery.py
  python> # All error recovery tests executed
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Mock dependencies for testing
class MockAPIClient:
    """Mock API client for testing error scenarios"""

    def __init__(self):
        self.call_count = 0
        self.fail_until_call = 0
        self.should_timeout = False

    async def get_departments(self):
        self.call_count += 1

        if self.should_timeout:
            await asyncio.sleep(2)
            raise TimeoutError("Connection timeout")

        if self.call_count <= self.fail_until_call:
            raise ConnectionError(f"API unavailable (call {self.call_count})")

        return {"success": True, "data": {"departments": []}}

    async def health_check(self):
        return await self.get_departments()


# Import after mocking
try:
    from frontend.core.error_recovery import (
        ErrorRecoveryCoordinator,
        CircuitBreaker,
        RetryManager,
        APIHealthMonitor,
        ComponentStateManager,
        ResourceCleanupManager,
        CircuitBreakerConfig,
        RetryConfig,
    )
except ImportError:
    logger.error(
        "Failed to import error recovery modules. Make sure you're in the correct directory."
    )
    sys.exit(1)


class ErrorRecoveryTests:
    """
    @doc
    Comprehensive test suite for error recovery mechanisms.

    Tests all major error recovery patterns and validates
    that they work correctly under various failure scenarios.
    """

    def __init__(self):
        self.mock_api = MockAPIClient()
        self.test_results = {}

    async def run_all_tests(self):
        """
        @doc
        Run all error recovery tests.

        Examples:
          python> tests = ErrorRecoveryTests()
          python> await tests.run_all_tests()
          python> # All tests executed with results
        """
        logger.info("🚀 Starting A101 HR Profile Generator Error Recovery Tests")
        logger.info("=" * 70)

        tests = [
            ("Circuit Breaker Pattern", self.test_circuit_breaker),
            ("Exponential Backoff Retry", self.test_retry_manager),
            ("API Health Monitoring", self.test_health_monitoring),
            ("Component State Management", self.test_state_management),
            ("Resource Cleanup", self.test_resource_cleanup),
            ("Integrated Error Coordination", self.test_error_coordination),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                logger.info(f"🧪 Running: {test_name}")
                result = await test_func()
                self.test_results[test_name] = result

                if result.get("passed", False):
                    logger.info(f"✅ PASSED: {test_name}")
                    passed += 1
                else:
                    logger.error(
                        f"❌ FAILED: {test_name} - {result.get('error', 'Unknown error')}"
                    )

            except Exception as e:
                logger.error(f"💥 ERROR: {test_name} - {str(e)}")
                self.test_results[test_name] = {"passed": False, "error": str(e)}

        # Print summary
        logger.info("=" * 70)
        logger.info(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            logger.info("🎉 All error recovery mechanisms are working correctly!")
            return True
        else:
            logger.warning(
                f"⚠️  {total - passed} tests failed. Review error recovery implementation."
            )
            return False

    async def test_circuit_breaker(self) -> Dict[str, Any]:
        """Test circuit breaker pattern functionality"""
        try:
            # Setup circuit breaker with low thresholds for testing
            circuit_breaker = CircuitBreaker(
                "test_breaker",
                CircuitBreakerConfig(failure_threshold=2, timeout_seconds=1),
            )

            # Test normal operation (should succeed)
            self.mock_api.call_count = 0
            self.mock_api.fail_until_call = 0

            result = await circuit_breaker.call(self.mock_api.get_departments)
            assert result["success"] is True, "Normal operation should succeed"

            # Test failure scenarios
            self.mock_api.fail_until_call = 5  # Fail next 5 calls

            # Generate failures to trip circuit breaker
            failures = 0
            for i in range(3):
                try:
                    await circuit_breaker.call(self.mock_api.get_departments)
                except Exception:
                    failures += 1

            assert failures >= 2, "Should have multiple failures"

            # Circuit should be open now
            stats = circuit_breaker.get_stats()
            assert (
                stats["state"] == "OPEN"
            ), f"Circuit should be OPEN, got {stats['state']}"

            # Wait for timeout and test recovery
            await asyncio.sleep(1.5)  # Wait for timeout
            self.mock_api.fail_until_call = 0  # Stop failing

            # Should transition to HALF_OPEN then CLOSED
            result = await circuit_breaker.call(self.mock_api.get_departments)
            assert result["success"] is True, "Should succeed after recovery"

            stats = circuit_breaker.get_stats()
            assert (
                stats["state"] == "CLOSED"
            ), f"Circuit should be CLOSED after recovery, got {stats['state']}"

            return {
                "passed": True,
                "stats": stats,
                "message": "Circuit breaker correctly handled failures and recovery",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_retry_manager(self) -> Dict[str, Any]:
        """Test exponential backoff retry functionality"""
        try:
            # Setup retry manager with fast retries for testing
            retry_manager = RetryManager(
                RetryConfig(
                    max_retries=3, base_delay=0.1, max_delay=1, backoff_factor=2
                )
            )

            # Test successful retry after failures
            self.mock_api.call_count = 0
            self.mock_api.fail_until_call = 2  # Fail first 2 calls, succeed on 3rd

            start_time = time.time()
            result = await retry_manager.retry(self.mock_api.get_departments)
            end_time = time.time()

            assert result["success"] is True, "Should succeed after retries"
            assert (
                self.mock_api.call_count == 3
            ), f"Should make 3 calls, made {self.mock_api.call_count}"
            assert end_time - start_time >= 0.3, "Should have delays between retries"

            # Test retry exhaustion
            self.mock_api.call_count = 0
            self.mock_api.fail_until_call = 10  # Always fail

            try:
                await retry_manager.retry(self.mock_api.get_departments)
                assert False, "Should raise exception after exhausting retries"
            except Exception:
                pass  # Expected

            assert (
                self.mock_api.call_count == 4
            ), f"Should make 4 total attempts, made {self.mock_api.call_count}"

            stats = retry_manager.get_stats()
            assert stats["total_attempts"] > 0, "Should have attempt statistics"

            return {
                "passed": True,
                "stats": stats,
                "message": "Retry manager correctly handled retries with exponential backoff",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_health_monitoring(self) -> Dict[str, Any]:
        """Test API health monitoring functionality"""
        try:
            # Setup health monitor with fast check interval
            health_monitor = APIHealthMonitor(
                self.mock_api, check_interval=0.5, timeout=1.0
            )

            recovery_triggered = False
            degradation_triggered = False

            def on_recovery():
                nonlocal recovery_triggered
                recovery_triggered = True

            def on_degradation(error_msg):
                nonlocal degradation_triggered
                degradation_triggered = True

            health_monitor.on_recovery = on_recovery
            health_monitor.on_degradation = on_degradation

            # Start monitoring
            await health_monitor.start_monitoring()

            # Initially should be healthy
            self.mock_api.call_count = 0
            self.mock_api.fail_until_call = 0
            await asyncio.sleep(1)  # Wait for health checks

            status = health_monitor.get_health_status()
            assert status["current_status"] in [
                "HEALTHY",
                "DEGRADED",
            ], f"Should be healthy initially, got {status['current_status']}"

            # Simulate API failure
            self.mock_api.fail_until_call = 10  # Start failing
            await asyncio.sleep(2)  # Wait for health checks to detect failure

            status = health_monitor.get_health_status()
            assert (
                status["current_status"] == "UNHEALTHY"
            ), f"Should be unhealthy after failures, got {status['current_status']}"
            assert (
                degradation_triggered
            ), "Degradation callback should have been triggered"

            # Simulate API recovery
            self.mock_api.fail_until_call = 0  # Stop failing
            await asyncio.sleep(1.5)  # Wait for health checks to detect recovery

            status = health_monitor.get_health_status()
            assert recovery_triggered, "Recovery callback should have been triggered"

            # Stop monitoring
            await health_monitor.stop_monitoring()

            return {
                "passed": True,
                "status": status,
                "message": "Health monitoring correctly detected failures and recovery",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_state_management(self) -> Dict[str, Any]:
        """Test component state management functionality"""
        try:
            state_manager = ComponentStateManager(cleanup_interval=1)

            # Start cleanup
            await state_manager.start_cleanup()

            # Save some test state
            test_state = {
                "component_name": "test_component",
                "selected_position": "Developer",
                "query": "python developer",
            }

            state_manager.save_state("test_component", test_state, ttl_seconds=10)

            # Verify state was saved
            stats = state_manager.get_stats()
            assert stats["saves_count"] == 1, "Should have 1 saved state"
            assert stats["current_components"] == 1, "Should have 1 component"

            # Restore state
            restored_state = state_manager.restore_state("test_component")
            assert restored_state is not None, "Should restore saved state"
            assert (
                restored_state["selected_position"] == "Developer"
            ), "Should restore correct data"

            stats = state_manager.get_stats()
            assert stats["restores_count"] == 1, "Should have 1 restore"
            assert stats["successful_restores"] == 1, "Should have 1 successful restore"

            # Test state expiration
            state_manager.save_state(
                "expired_component", {"data": "test"}, ttl_seconds=0.1
            )
            await asyncio.sleep(0.2)  # Wait for expiration

            expired_state = state_manager.restore_state("expired_component")
            assert (
                expired_state is None or expired_state == {}
            ), "Expired state should be empty"

            # Stop cleanup
            await state_manager.stop_cleanup()

            return {
                "passed": True,
                "stats": stats,
                "message": "State management correctly saved, restored, and expired states",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_resource_cleanup(self) -> Dict[str, Any]:
        """Test resource cleanup functionality"""
        try:
            cleanup_manager = ResourceCleanupManager()

            # Create mock resources
            class MockResource:
                def __init__(self, resource_id):
                    self.resource_id = resource_id
                    self.cleaned_up = False

                async def cleanup(self):
                    self.cleaned_up = True

            # Track some resources
            resource1 = MockResource("test_resource_1")
            resource2 = MockResource("test_resource_2")

            cleanup_manager.track_resource(resource1)
            cleanup_manager.track_resource(resource2)

            stats = cleanup_manager.get_stats()
            assert stats["currently_tracked"] == 2, "Should track 2 resources"

            # Cleanup all resources
            cleanup_stats = await cleanup_manager.cleanup_all()
            assert (
                cleanup_stats["successful"] == 2
            ), "Should cleanup 2 resources successfully"
            assert cleanup_stats["failed"] == 0, "Should have no failures"

            # Verify resources were cleaned up
            assert resource1.cleaned_up, "Resource 1 should be cleaned up"
            assert resource2.cleaned_up, "Resource 2 should be cleaned up"

            final_stats = cleanup_manager.get_stats()
            assert (
                final_stats["currently_tracked"] == 0
            ), "Should have no tracked resources after cleanup"

            return {
                "passed": True,
                "stats": final_stats,
                "cleanup_stats": cleanup_stats,
                "message": "Resource cleanup correctly tracked and cleaned up resources",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def test_error_coordination(self) -> Dict[str, Any]:
        """Test integrated error recovery coordination"""
        try:
            # Setup error recovery coordinator
            coordinator = ErrorRecoveryCoordinator(self.mock_api)

            # Start coordinator
            await coordinator.start()

            # Get circuit breaker and retry manager
            circuit_breaker = coordinator.get_circuit_breaker("test_ops")
            retry_manager = coordinator.get_retry_manager("test_retry")

            # Test component error handling
            test_error = Exception("Test component failure")
            recovered = await coordinator.handle_component_error(
                "test_component", test_error, attempt_recovery=True
            )

            # Should handle gracefully (no saved state to recover)
            assert recovered is False, "Should not recover without saved state"

            # Save state and test recovery
            coordinator.state_manager.save_state("test_component", {"test": "data"})

            recovered = await coordinator.handle_component_error(
                "test_component", test_error, attempt_recovery=True
            )

            assert recovered is True, "Should recover with saved state"

            # Get overall statistics
            stats = coordinator.get_overall_stats()
            assert "coordinator" in stats, "Should have coordinator stats"
            assert "health_monitor" in stats, "Should have health monitor stats"

            # Stop coordinator
            await coordinator.stop()

            return {
                "passed": True,
                "stats": stats,
                "message": "Error recovery coordinator successfully orchestrated all recovery mechanisms",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}


async def main():
    """Main test runner"""
    logger.info("A101 HR Profile Generator - Error Recovery Test Suite")
    logger.info("Testing comprehensive error recovery mechanisms...")

    tests = ErrorRecoveryTests()
    success = await tests.run_all_tests()

    if success:
        logger.info("🎉 All error recovery tests passed! System is production-ready.")
        return 0
    else:
        logger.error("❌ Some tests failed. Review the error recovery implementation.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        sys.exit(1)

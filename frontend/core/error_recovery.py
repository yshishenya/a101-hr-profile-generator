"""
@doc
Error Recovery Infrastructure - Comprehensive error recovery mechanisms for A101 HR Profile Generator.

Provides Circuit Breaker pattern, exponential backoff retry, API health monitoring,
component state management, and resource cleanup for production-ready reliability.

Classes:
- CircuitBreaker: Circuit breaker pattern for API failures
- RetryManager: Exponential backoff retry logic
- APIHealthMonitor: Continuous API health monitoring with auto-recovery
- ComponentStateManager: Component state save/restore mechanisms
- ResourceCleanupManager: Resource leak prevention and cleanup
- ErrorRecoveryCoordinator: Central coordinator for all recovery mechanisms

Examples:
  python> circuit_breaker = CircuitBreaker("api_calls", failure_threshold=3)
  python> retry_manager = RetryManager(max_retries=3, base_delay=1, max_delay=60)
  python> health_monitor = APIHealthMonitor(api_client, check_interval=30)
"""

import asyncio
import logging
import time
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Set, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, blocking requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""

    failure_threshold: int = 5
    timeout_seconds: int = 60
    success_threshold: int = 3
    max_failures_window_seconds: int = 300


class CircuitBreaker:
    """
    @doc
    Circuit breaker pattern implementation for API reliability.

    Prevents cascading failures by monitoring API call success/failure rates
    and temporarily blocking calls when failure threshold is exceeded.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Failure threshold exceeded, calls blocked
    - HALF_OPEN: Testing recovery, limited calls allowed

    Examples:
      python> breaker = CircuitBreaker("api_calls", failure_threshold=3, timeout_seconds=60)
      python> result = await breaker.call(async_api_function, arg1, arg2)
      python> print(breaker.get_stats())  # {'state': 'CLOSED', 'failures': 0}
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        @doc
        Initialize circuit breaker with configuration.

        Args:
            name: Unique name for this circuit breaker
            config: Configuration object, uses defaults if None

        Examples:
          python> breaker = CircuitBreaker("search_api", CircuitBreakerConfig(failure_threshold=3))
          python> # Circuit breaker initialized and ready
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # State management
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None

        # Failure tracking within time window
        self.failure_timestamps: List[float] = []

        # Statistics
        self.total_calls = 0
        self.total_successes = 0
        self.total_failures = 0

    async def call(self, func: Callable, *args, **kwargs):
        """
        @doc
        Execute function through circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            CircuitBreakerOpenError: When circuit is open
            Original exception: When func fails and circuit allows

        Examples:
          python> result = await breaker.call(api_client.get_data, param1="value")
          python> # Function executed with circuit breaker protection
        """
        self.total_calls += 1

        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker '{self.name}' moving to HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return False

        return (time.time() - self.last_failure_time) >= self.config.timeout_seconds

    def _on_success(self):
        """Handle successful call"""
        self.total_successes += 1
        self.last_success_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success in closed state
            self.failure_count = max(0, self.failure_count - 1)

    def _on_failure(self):
        """Handle failed call"""
        current_time = time.time()
        self.total_failures += 1
        self.last_failure_time = current_time
        self.failure_count += 1
        self.failure_timestamps.append(current_time)

        # Clean old failures outside window
        cutoff_time = current_time - self.config.max_failures_window_seconds
        self.failure_timestamps = [
            t for t in self.failure_timestamps if t > cutoff_time
        ]

        # Check if should open circuit
        if self.state == CircuitBreakerState.CLOSED:
            if len(self.failure_timestamps) >= self.config.failure_threshold:
                self._trip()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self._trip()

    def _trip(self):
        """Open the circuit breaker"""
        self.state = CircuitBreakerState.OPEN
        logger.warning(f"Circuit breaker '{self.name}' TRIPPED - state: OPEN")

    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.failure_timestamps.clear()
        logger.info(f"Circuit breaker '{self.name}' RESET - state: CLOSED")

    def get_stats(self) -> Dict[str, Any]:
        """
        @doc
        Get circuit breaker statistics.

        Returns:
            Dict with current state and performance stats

        Examples:
          python> stats = breaker.get_stats()
          python> print(stats['state'])  # "CLOSED"
          python> print(stats['success_rate'])  # 0.95
        """
        success_rate = (
            self.total_successes / self.total_calls if self.total_calls > 0 else 0
        )

        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate": round(success_rate, 3),
            "failures_in_window": len(self.failure_timestamps),
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""

    pass


@dataclass
class RetryConfig:
    """Configuration for retry manager"""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True


class RetryManager:
    """
    @doc
    Exponential backoff retry manager with jitter.

    Provides configurable retry logic with exponential backoff,
    maximum delay caps, and optional jitter to prevent thundering herd.

    Features:
    - Exponential backoff with configurable base and max delays
    - Jitter to distribute retry attempts
    - Retry condition callbacks for selective retries
    - Statistics tracking

    Examples:
      python> retry_manager = RetryManager(max_retries=3, base_delay=1, max_delay=30)
      python> result = await retry_manager.retry(api_call_func, arg1, arg2)
      python> print(retry_manager.get_stats())  # {'attempts': 2, 'successes': 1}
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        @doc
        Initialize retry manager with configuration.

        Args:
            config: RetryConfig object, uses defaults if None

        Examples:
          python> manager = RetryManager(RetryConfig(max_retries=5, base_delay=2))
          python> # Retry manager configured for 5 attempts with 2s base delay
        """
        self.config = config or RetryConfig()

        # Statistics
        self.total_attempts = 0
        self.total_successes = 0
        self.total_final_failures = 0

    async def retry(
        self,
        func: Callable,
        *args,
        retry_condition: Optional[Callable[[Exception], bool]] = None,
        **kwargs,
    ):
        """
        @doc
        Execute function with exponential backoff retry.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            retry_condition: Optional function to determine if error should trigger retry
            **kwargs: Keyword arguments for func

        Returns:
            Result of successful func execution

        Raises:
            Last exception if all retries exhausted

        Examples:
          python> result = await retry_manager.retry(api_call, param1="value")
          python> # Function retried with exponential backoff on failures
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            self.total_attempts += 1

            try:
                result = await func(*args, **kwargs)
                self.total_successes += 1

                if attempt > 0:
                    logger.info(f"Function succeeded after {attempt} retries")

                return result

            except Exception as e:
                last_exception = e

                # Check if we should retry this exception
                if retry_condition and not retry_condition(e):
                    logger.debug(f"Retry condition failed for exception: {e}")
                    break

                # Don't sleep after the last attempt
                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_retries + 1} attempts failed")

        self.total_final_failures += 1
        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt with exponential backoff and jitter"""
        delay = min(
            self.config.base_delay * (self.config.backoff_factor**attempt),
            self.config.max_delay,
        )

        if self.config.jitter:
            import random

            # Add ±25% jitter
            jitter_range = delay * 0.25
            delay = delay + random.uniform(-jitter_range, jitter_range)
            delay = max(0.1, delay)  # Ensure minimum delay

        return delay

    def get_stats(self) -> Dict[str, Any]:
        """
        @doc
        Get retry manager statistics.

        Returns:
            Dict with attempt counts and success rates

        Examples:
          python> stats = retry_manager.get_stats()
          python> print(stats['retry_success_rate'])  # 0.85
        """
        retry_success_rate = (
            self.total_successes / self.total_attempts if self.total_attempts > 0 else 0
        )

        return {
            "total_attempts": self.total_attempts,
            "total_successes": self.total_successes,
            "total_final_failures": self.total_final_failures,
            "retry_success_rate": round(retry_success_rate, 3),
            "config": {
                "max_retries": self.config.max_retries,
                "base_delay": self.config.base_delay,
                "max_delay": self.config.max_delay,
                "backoff_factor": self.config.backoff_factor,
                "jitter": self.config.jitter,
            },
        }


class APIHealthStatus(Enum):
    """API health status"""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass
class APIHealthCheck:
    """Result of API health check"""

    status: APIHealthStatus
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class APIHealthMonitor:
    """
    @doc
    Continuous API health monitoring with automatic recovery detection.

    Monitors API health through periodic checks and notifies when service
    recovers from failures, enabling automatic fallback → normal transitions.

    Features:
    - Configurable health check intervals
    - Response time monitoring
    - Automatic recovery detection
    - Health status callbacks for UI updates
    - Statistics and trend tracking

    Examples:
      python> monitor = APIHealthMonitor(api_client, check_interval=30)
      python> monitor.on_recovery = lambda: ui.notify("API recovered!", type="positive")
      python> await monitor.start_monitoring()
    """

    def __init__(
        self,
        api_client,
        check_interval: int = 30,
        timeout: float = 10.0,
        unhealthy_threshold: int = 3,
    ):
        """
        @doc
        Initialize API health monitor.

        Args:
            api_client: API client instance for health checks
            check_interval: Seconds between health checks
            timeout: Timeout for health check requests
            unhealthy_threshold: Consecutive failures before marking unhealthy

        Examples:
          python> monitor = APIHealthMonitor(api_client, check_interval=60, timeout=5)
          python> # Monitor configured for 60s intervals with 5s timeout
        """
        self.api_client = api_client
        self.check_interval = check_interval
        self.timeout = timeout
        self.unhealthy_threshold = unhealthy_threshold

        # State
        self.current_status = APIHealthStatus.UNKNOWN
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

        # Health history
        self.health_checks: List[APIHealthCheck] = []
        self.consecutive_failures = 0
        self.last_healthy_time = None

        # Callbacks
        self.on_health_change: Optional[
            Callable[[APIHealthStatus, APIHealthStatus], None]
        ] = None
        self.on_recovery: Optional[Callable[[], None]] = None
        self.on_degradation: Optional[Callable[[str], None]] = None

    async def start_monitoring(self):
        """
        @doc
        Start continuous API health monitoring.

        Starts background task that performs periodic health checks
        and triggers recovery callbacks when API becomes healthy.

        Examples:
          python> await monitor.start_monitoring()
          python> # Background monitoring started
        """
        if self.is_monitoring:
            logger.warning("Health monitoring already running")
            return

        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Started API health monitoring (interval: {self.check_interval}s)")

    async def stop_monitoring(self):
        """
        @doc
        Stop API health monitoring.

        Cancels background monitoring task and cleans up resources.

        Examples:
          python> await monitor.stop_monitoring()
          python> # Monitoring stopped and resources cleaned up
        """
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None

        logger.info("Stopped API health monitoring")

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                health_check = await self._perform_health_check()
                await self._process_health_check(health_check)

                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _perform_health_check(self) -> APIHealthCheck:
        """Perform single health check"""
        start_time = time.time()

        try:
            # Use health endpoint if available, otherwise try a simple API call
            if hasattr(self.api_client, "health_check"):
                await asyncio.wait_for(
                    self.api_client.health_check(), timeout=self.timeout
                )
            else:
                # Fallback: try to get departments (lightweight call)
                await asyncio.wait_for(
                    self.api_client.get_departments(), timeout=self.timeout
                )

            response_time = (time.time() - start_time) * 1000

            # Determine status based on response time
            if response_time < 1000:  # < 1s
                status = APIHealthStatus.HEALTHY
            elif response_time < 5000:  # < 5s
                status = APIHealthStatus.DEGRADED
            else:
                status = APIHealthStatus.DEGRADED

            return APIHealthCheck(status=status, response_time_ms=response_time)

        except asyncio.TimeoutError:
            return APIHealthCheck(
                status=APIHealthStatus.UNHEALTHY,
                error_message=f"Health check timeout ({self.timeout}s)",
            )
        except Exception as e:
            return APIHealthCheck(
                status=APIHealthStatus.UNHEALTHY, error_message=str(e)
            )

    async def _process_health_check(self, health_check: APIHealthCheck):
        """Process health check result and trigger callbacks"""
        previous_status = self.current_status

        # Add to history (keep last 100 checks)
        self.health_checks.append(health_check)
        if len(self.health_checks) > 100:
            self.health_checks.pop(0)

        # Update consecutive failure count
        if health_check.status == APIHealthStatus.UNHEALTHY:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0
            if health_check.status == APIHealthStatus.HEALTHY:
                self.last_healthy_time = health_check.timestamp

        # Determine current status
        if self.consecutive_failures >= self.unhealthy_threshold:
            self.current_status = APIHealthStatus.UNHEALTHY
        else:
            self.current_status = health_check.status

        # Trigger callbacks if status changed
        if previous_status != self.current_status:
            logger.info(
                f"API health status changed: {previous_status.value} → {self.current_status.value}"
            )

            if self.on_health_change:
                try:
                    self.on_health_change(previous_status, self.current_status)
                except Exception as e:
                    logger.error(f"Error in health change callback: {e}")

            # Recovery detection
            if (
                previous_status
                in [
                    APIHealthStatus.UNHEALTHY,
                    APIHealthStatus.DEGRADED,
                    APIHealthStatus.UNKNOWN,
                ]
                and self.current_status == APIHealthStatus.HEALTHY
            ):
                logger.info("API recovered - triggering recovery callback")
                if self.on_recovery:
                    try:
                        self.on_recovery()
                    except Exception as e:
                        logger.error(f"Error in recovery callback: {e}")

            # Degradation detection
            if previous_status == APIHealthStatus.HEALTHY and self.current_status in [
                APIHealthStatus.DEGRADED,
                APIHealthStatus.UNHEALTHY,
            ]:
                error_msg = (
                    health_check.error_message or f"Status: {self.current_status.value}"
                )
                if self.on_degradation:
                    try:
                        self.on_degradation(error_msg)
                    except Exception as e:
                        logger.error(f"Error in degradation callback: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """
        @doc
        Get current API health status and statistics.

        Returns:
            Dict with current status, response times, and failure stats

        Examples:
          python> status = monitor.get_health_status()
          python> print(status['current_status'])  # "HEALTHY"
          python> print(status['avg_response_time_ms'])  # 245.3
        """
        recent_checks = self.health_checks[-10:] if self.health_checks else []

        response_times = [
            check.response_time_ms
            for check in recent_checks
            if check.response_time_ms is not None
        ]

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else None
        )

        return {
            "current_status": self.current_status.value,
            "is_monitoring": self.is_monitoring,
            "consecutive_failures": self.consecutive_failures,
            "last_healthy_time": self.last_healthy_time,
            "total_checks": len(self.health_checks),
            "recent_checks_count": len(recent_checks),
            "avg_response_time_ms": (
                round(avg_response_time, 1) if avg_response_time else None
            ),
            "check_interval": self.check_interval,
            "unhealthy_threshold": self.unhealthy_threshold,
        }


class ComponentState:
    """
    @doc
    Component state snapshot for recovery.

    Captures component state at a point in time to enable
    rollback to known good states after errors.

    Examples:
      python> state = ComponentState("search_component", {"query": "java", "results": [...]})
      python> print(state.is_expired())  # False
      python> restored_data = state.get_data()  # {"query": "java", "results": [...]}
    """

    def __init__(
        self, component_name: str, state_data: Dict[str, Any], ttl_seconds: int = 300
    ):
        """
        @doc
        Create component state snapshot.

        Args:
            component_name: Name of the component
            state_data: State data to save
            ttl_seconds: Time-to-live for state (default 5 minutes)

        Examples:
          python> state = ComponentState("generator", {"position": "Developer"}, ttl_seconds=600)
          python> # State saved with 10-minute TTL
        """
        self.component_name = component_name
        self.state_data = state_data.copy() if state_data else {}
        self.timestamp = time.time()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if state is expired"""
        return (time.time() - self.timestamp) > self.ttl_seconds

    def get_data(self) -> Dict[str, Any]:
        """Get state data (empty dict if expired)"""
        return self.state_data.copy() if not self.is_expired() else {}


class ComponentStateManager:
    """
    @doc
    Manager for component state save/restore operations.

    Provides centralized state management for components with
    automatic cleanup of expired states and recovery capabilities.

    Features:
    - Automatic state expiration and cleanup
    - Multiple state versions per component
    - State validation and sanitization
    - Recovery statistics tracking

    Examples:
      python> state_manager = ComponentStateManager()
      python> state_manager.save_state("search", {"query": "dev", "results": [...]})
      python> restored = state_manager.restore_state("search")  # Returns saved state or None
    """

    def __init__(self, cleanup_interval: int = 60):
        """
        @doc
        Initialize component state manager.

        Args:
            cleanup_interval: Seconds between expired state cleanup

        Examples:
          python> manager = ComponentStateManager(cleanup_interval=120)
          python> # Manager with 2-minute cleanup interval
        """
        self.states: Dict[str, List[ComponentState]] = {}
        self.cleanup_interval = cleanup_interval
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Statistics
        self.saves_count = 0
        self.restores_count = 0
        self.successful_restores = 0

    async def start_cleanup(self):
        """Start automatic cleanup of expired states"""
        if self.is_running:
            return

        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Started state cleanup (interval: {self.cleanup_interval}s)")

    async def stop_cleanup(self):
        """Stop automatic cleanup"""
        if not self.is_running:
            return

        self.is_running = False

        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None

        logger.info("Stopped state cleanup")

    async def _cleanup_loop(self):
        """Periodic cleanup of expired states"""
        while self.is_running:
            try:
                self._cleanup_expired_states()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in state cleanup loop: {e}")
                await asyncio.sleep(self.cleanup_interval)

    def _cleanup_expired_states(self):
        """Remove expired states"""
        total_cleaned = 0

        for component_name, states_list in list(self.states.items()):
            original_count = len(states_list)
            states_list[:] = [state for state in states_list if not state.is_expired()]
            cleaned = original_count - len(states_list)
            total_cleaned += cleaned

            # Remove empty component entries
            if not states_list:
                del self.states[component_name]

        if total_cleaned > 0:
            logger.debug(f"Cleaned up {total_cleaned} expired component states")

    def save_state(
        self,
        component_name: str,
        state_data: Dict[str, Any],
        ttl_seconds: int = 300,
        max_versions: int = 3,
    ):
        """
        @doc
        Save component state with automatic versioning.

        Args:
            component_name: Name of the component
            state_data: State data to save
            ttl_seconds: Time-to-live for state
            max_versions: Maximum state versions to keep

        Examples:
          python> state_manager.save_state("search", {"query": "python"}, ttl_seconds=600)
          python> # State saved with 10-minute TTL
        """
        if not component_name or not isinstance(state_data, dict):
            logger.warning(f"Invalid state save attempt: {component_name}")
            return

        state = ComponentState(component_name, state_data, ttl_seconds)

        if component_name not in self.states:
            self.states[component_name] = []

        # Add new state to front
        self.states[component_name].insert(0, state)

        # Limit versions
        if len(self.states[component_name]) > max_versions:
            self.states[component_name] = self.states[component_name][:max_versions]

        self.saves_count += 1
        logger.debug(
            f"Saved state for component '{component_name}' (version {len(self.states[component_name])})"
        )

    def restore_state(
        self, component_name: str, version: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        @doc
        Restore component state by name and version.

        Args:
            component_name: Name of the component
            version: Version to restore (0 = latest, 1 = previous, etc.)

        Returns:
            Restored state data or None if not available

        Examples:
          python> state = state_manager.restore_state("search")  # Latest version
          python> prev_state = state_manager.restore_state("search", version=1)  # Previous version
        """
        self.restores_count += 1

        if component_name not in self.states:
            logger.debug(f"No saved states for component '{component_name}'")
            return None

        states_list = self.states[component_name]

        if version >= len(states_list):
            logger.debug(
                f"Version {version} not available for component '{component_name}'"
            )
            return None

        state = states_list[version]
        state_data = state.get_data()

        if state_data:
            self.successful_restores += 1
            logger.info(
                f"Restored state for component '{component_name}' (version {version})"
            )
            return state_data
        else:
            logger.warning(
                f"State for component '{component_name}' version {version} is expired"
            )
            return None

    def clear_states(self, component_name: Optional[str] = None):
        """
        @doc
        Clear saved states.

        Args:
            component_name: Specific component to clear, or None for all

        Examples:
          python> state_manager.clear_states("search")  # Clear search component states
          python> state_manager.clear_states()  # Clear all states
        """
        if component_name:
            if component_name in self.states:
                count = len(self.states[component_name])
                del self.states[component_name]
                logger.info(f"Cleared {count} states for component '{component_name}'")
        else:
            total_count = sum(len(states) for states in self.states.values())
            self.states.clear()
            logger.info(f"Cleared all {total_count} saved states")

    def get_stats(self) -> Dict[str, Any]:
        """
        @doc
        Get state manager statistics.

        Returns:
            Dict with save/restore counts and current state info

        Examples:
          python> stats = state_manager.get_stats()
          python> print(stats['restore_success_rate'])  # 0.87
        """
        total_states = sum(len(states) for states in self.states.values())
        restore_success_rate = (
            self.successful_restores / self.restores_count
            if self.restores_count > 0
            else 0
        )

        return {
            "saves_count": self.saves_count,
            "restores_count": self.restores_count,
            "successful_restores": self.successful_restores,
            "restore_success_rate": round(restore_success_rate, 3),
            "current_components": len(self.states),
            "total_saved_states": total_states,
            "is_running": self.is_running,
            "cleanup_interval": self.cleanup_interval,
        }


class ManagedResource(ABC):
    """
    @doc
    Abstract base class for managed resources.

    Resources that implement this interface can be automatically
    tracked and cleaned up by ResourceCleanupManager.

    Examples:
      python> class TempFile(ManagedResource):
      python>     async def cleanup(self): os.remove(self.path)
    """

    @abstractmethod
    async def cleanup(self):
        """Cleanup resource (close files, cancel tasks, etc.)"""
        pass

    @property
    @abstractmethod
    def resource_id(self) -> str:
        """Unique identifier for this resource"""
        pass


class ResourceCleanupManager:
    """
    @doc
    Manager for automatic resource cleanup and leak prevention.

    Tracks managed resources and ensures they are properly cleaned up
    to prevent memory leaks, file handle exhaustion, and task accumulation.

    Features:
    - Weak reference tracking to avoid circular references
    - Automatic cleanup on process exit
    - Manual cleanup triggers
    - Resource leak detection and reporting

    Examples:
      python> cleanup_manager = ResourceCleanupManager()
      python> cleanup_manager.track_resource(temp_file_resource)
      python> await cleanup_manager.cleanup_all()  # Clean up all tracked resources
    """

    def __init__(self):
        """
        @doc
        Initialize resource cleanup manager.

        Examples:
          python> manager = ResourceCleanupManager()
          python> # Ready to track and cleanup resources
        """
        self.tracked_resources: Set[weakref.ReferenceType] = set()
        self.cleanup_stats = {
            "resources_tracked": 0,
            "successful_cleanups": 0,
            "failed_cleanups": 0,
            "last_cleanup_time": None,
        }

    def track_resource(self, resource: ManagedResource):
        """
        @doc
        Track a resource for automatic cleanup.

        Args:
            resource: Resource implementing ManagedResource interface

        Examples:
          python> manager.track_resource(temp_file)
          python> # Resource tracked for cleanup
        """
        if not isinstance(resource, ManagedResource):
            raise TypeError("Resource must implement ManagedResource interface")

        weak_ref = weakref.ref(resource, self._on_resource_deleted)
        self.tracked_resources.add(weak_ref)
        self.cleanup_stats["resources_tracked"] += 1

        logger.debug(f"Tracking resource: {resource.resource_id}")

    def _on_resource_deleted(self, weak_ref):
        """Callback when tracked resource is garbage collected"""
        self.tracked_resources.discard(weak_ref)

    async def cleanup_all(self) -> Dict[str, int]:
        """
        @doc
        Clean up all tracked resources.

        Returns:
            Dict with cleanup statistics

        Examples:
          python> stats = await manager.cleanup_all()
          python> print(f"Cleaned up {stats['successful']} resources")
        """
        logger.info(
            f"Starting cleanup of {len(self.tracked_resources)} tracked resources"
        )

        successful = 0
        failed = 0

        # Create list from set to avoid modification during iteration
        resources_to_cleanup = list(self.tracked_resources)

        for weak_ref in resources_to_cleanup:
            resource = weak_ref()
            if resource is None:
                # Resource was already garbage collected
                self.tracked_resources.discard(weak_ref)
                continue

            try:
                await resource.cleanup()
                successful += 1
                logger.debug(
                    f"Successfully cleaned up resource: {resource.resource_id}"
                )

            except Exception as e:
                failed += 1
                logger.error(f"Failed to cleanup resource {resource.resource_id}: {e}")

            # Remove from tracking
            self.tracked_resources.discard(weak_ref)

        self.cleanup_stats["successful_cleanups"] += successful
        self.cleanup_stats["failed_cleanups"] += failed
        self.cleanup_stats["last_cleanup_time"] = time.time()

        logger.info(f"Cleanup completed: {successful} successful, {failed} failed")

        return {
            "successful": successful,
            "failed": failed,
            "total_attempted": successful + failed,
        }

    async def cleanup_by_type(self, resource_type: type) -> int:
        """
        @doc
        Clean up resources of specific type.

        Args:
            resource_type: Type of resources to clean up

        Returns:
            Number of resources cleaned up

        Examples:
          python> count = await manager.cleanup_by_type(TempFileResource)
          python> print(f"Cleaned up {count} temp files")
        """
        cleaned_count = 0
        resources_to_cleanup = []

        for weak_ref in list(self.tracked_resources):
            resource = weak_ref()
            if resource is None:
                self.tracked_resources.discard(weak_ref)
                continue

            if isinstance(resource, resource_type):
                resources_to_cleanup.append((weak_ref, resource))

        for weak_ref, resource in resources_to_cleanup:
            try:
                await resource.cleanup()
                cleaned_count += 1
                self.tracked_resources.discard(weak_ref)
                logger.debug(
                    f"Cleaned up {resource_type.__name__}: {resource.resource_id}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to cleanup {resource_type.__name__} {resource.resource_id}: {e}"
                )

        return cleaned_count

    def get_stats(self) -> Dict[str, Any]:
        """
        @doc
        Get resource cleanup statistics.

        Returns:
            Dict with tracking and cleanup stats

        Examples:
          python> stats = manager.get_stats()
          python> print(stats['currently_tracked'])  # 5
        """
        # Clean up dead weak references
        self.tracked_resources = {
            ref for ref in self.tracked_resources if ref() is not None
        }

        return {
            "currently_tracked": len(self.tracked_resources),
            "total_tracked": self.cleanup_stats["resources_tracked"],
            "successful_cleanups": self.cleanup_stats["successful_cleanups"],
            "failed_cleanups": self.cleanup_stats["failed_cleanups"],
            "last_cleanup_time": self.cleanup_stats["last_cleanup_time"],
        }


class ErrorRecoveryCoordinator:
    """
    @doc
    Central coordinator for all error recovery mechanisms.

    Orchestrates circuit breakers, retry managers, health monitoring,
    state management, and resource cleanup for comprehensive error recovery.

    Features:
    - Centralized configuration and management
    - Component integration and event coordination
    - Recovery statistics and reporting
    - Graceful shutdown and cleanup

    Examples:
      python> coordinator = ErrorRecoveryCoordinator(api_client)
      python> await coordinator.start()  # Start all recovery mechanisms
      python> await coordinator.handle_component_error("search", exception)
    """

    def __init__(self, api_client):
        """
        @doc
        Initialize error recovery coordinator.

        Args:
            api_client: API client for health monitoring

        Examples:
          python> coordinator = ErrorRecoveryCoordinator(api_client)
          python> # All recovery mechanisms initialized
        """
        self.api_client = api_client

        # Initialize recovery components
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_managers: Dict[str, RetryManager] = {}
        self.health_monitor = APIHealthMonitor(api_client)
        self.state_manager = ComponentStateManager()
        self.cleanup_manager = ResourceCleanupManager()

        # Configuration
        self.is_started = False
        self.recovery_callbacks: Dict[str, List[Callable]] = {}

        # Statistics
        self.recovery_events = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0

        # Set up health monitor callbacks
        self.health_monitor.on_recovery = self._on_api_recovery
        self.health_monitor.on_degradation = self._on_api_degradation

    async def start(self):
        """
        @doc
        Start all error recovery mechanisms.

        Initializes health monitoring, state management cleanup,
        and other background recovery processes.

        Examples:
          python> await coordinator.start()
          python> # All recovery mechanisms active
        """
        if self.is_started:
            logger.warning("Error recovery coordinator already started")
            return

        # Start health monitoring
        await self.health_monitor.start_monitoring()

        # Start state cleanup
        await self.state_manager.start_cleanup()

        self.is_started = True
        logger.info("Error recovery coordinator started")

    async def stop(self):
        """
        @doc
        Stop all error recovery mechanisms and cleanup resources.

        Performs graceful shutdown of all recovery components
        and cleans up tracked resources.

        Examples:
          python> await coordinator.stop()
          python> # All recovery mechanisms stopped, resources cleaned up
        """
        if not self.is_started:
            return

        logger.info("Stopping error recovery coordinator...")

        # Stop monitoring and cleanup
        await self.health_monitor.stop_monitoring()
        await self.state_manager.stop_cleanup()

        # Cleanup all tracked resources
        await self.cleanup_manager.cleanup_all()

        self.is_started = False
        logger.info("Error recovery coordinator stopped")

    def get_circuit_breaker(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        @doc
        Get or create circuit breaker for component.

        Args:
            name: Circuit breaker name
            config: Configuration, uses defaults if None

        Returns:
            CircuitBreaker instance

        Examples:
          python> breaker = coordinator.get_circuit_breaker("api_calls")
          python> result = await breaker.call(api_function)
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, config)
            logger.debug(f"Created circuit breaker: {name}")

        return self.circuit_breakers[name]

    def get_retry_manager(
        self, name: str, config: Optional[RetryConfig] = None
    ) -> RetryManager:
        """
        @doc
        Get or create retry manager for component.

        Args:
            name: Retry manager name
            config: Configuration, uses defaults if None

        Returns:
            RetryManager instance

        Examples:
          python> retry_manager = coordinator.get_retry_manager("search_retry")
          python> result = await retry_manager.retry(search_function)
        """
        if name not in self.retry_managers:
            self.retry_managers[name] = RetryManager(config)
            logger.debug(f"Created retry manager: {name}")

        return self.retry_managers[name]

    async def handle_component_error(
        self, component_name: str, error: Exception, attempt_recovery: bool = True
    ) -> bool:
        """
        @doc
        Handle component error with automatic recovery attempts.

        Args:
            component_name: Name of the component that failed
            error: The exception that occurred
            attempt_recovery: Whether to attempt automatic recovery

        Returns:
            True if recovery was successful, False otherwise

        Examples:
          python> recovered = await coordinator.handle_component_error("search", exception)
          python> if recovered: print("Component recovered successfully")
        """
        self.recovery_events += 1
        logger.warning(f"Handling error in component '{component_name}': {error}")

        if not attempt_recovery:
            self.failed_recoveries += 1
            return False

        try:
            # Attempt state recovery
            recovered_state = self.state_manager.restore_state(component_name)
            if recovered_state:
                logger.info(f"Restored state for component '{component_name}'")

                # Trigger recovery callbacks
                await self._trigger_recovery_callbacks(component_name, recovered_state)

                self.successful_recoveries += 1
                return True
            else:
                logger.warning(
                    f"No saved state available for component '{component_name}'"
                )
                self.failed_recoveries += 1
                return False

        except Exception as recovery_error:
            logger.error(
                f"Recovery failed for component '{component_name}': {recovery_error}"
            )
            self.failed_recoveries += 1
            return False

    def register_recovery_callback(self, component_name: str, callback: Callable):
        """
        @doc
        Register callback for component recovery events.

        Args:
            component_name: Name of the component
            callback: Function to call on recovery

        Examples:
          python> coordinator.register_recovery_callback("search", search_component.reset_state)
          python> # Callback will be triggered on search component recovery
        """
        if component_name not in self.recovery_callbacks:
            self.recovery_callbacks[component_name] = []

        self.recovery_callbacks[component_name].append(callback)
        logger.debug(f"Registered recovery callback for component '{component_name}'")

    async def _trigger_recovery_callbacks(
        self, component_name: str, recovered_state: Dict[str, Any]
    ):
        """Trigger registered recovery callbacks for component"""
        if component_name not in self.recovery_callbacks:
            return

        for callback in self.recovery_callbacks[component_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(recovered_state)
                else:
                    callback(recovered_state)

            except Exception as e:
                logger.error(f"Error in recovery callback for '{component_name}': {e}")

    def _on_api_recovery(self):
        """Handle API recovery event"""
        logger.info("API recovery detected - notifying components")
        # API recovered - components can transition from fallback to normal mode
        # This will be implemented in component-specific handlers

    def _on_api_degradation(self, error_message: str):
        """Handle API degradation event"""
        logger.warning(f"API degradation detected: {error_message}")
        # API degraded - components should switch to fallback mode if available
        # This will be implemented in component-specific handlers

    def get_overall_stats(self) -> Dict[str, Any]:
        """
        @doc
        Get comprehensive recovery statistics.

        Returns:
            Dict with stats from all recovery components

        Examples:
          python> stats = coordinator.get_overall_stats()
          python> print(stats['recovery_success_rate'])  # 0.92
        """
        recovery_success_rate = (
            self.successful_recoveries / self.recovery_events
            if self.recovery_events > 0
            else 0
        )

        return {
            "coordinator": {
                "is_started": self.is_started,
                "recovery_events": self.recovery_events,
                "successful_recoveries": self.successful_recoveries,
                "failed_recoveries": self.failed_recoveries,
                "recovery_success_rate": round(recovery_success_rate, 3),
            },
            "circuit_breakers": {
                name: breaker.get_stats()
                for name, breaker in self.circuit_breakers.items()
            },
            "retry_managers": {
                name: manager.get_stats()
                for name, manager in self.retry_managers.items()
            },
            "health_monitor": self.health_monitor.get_health_status(),
            "state_manager": self.state_manager.get_stats(),
            "cleanup_manager": self.cleanup_manager.get_stats(),
        }

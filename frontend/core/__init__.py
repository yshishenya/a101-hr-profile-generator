"""
@doc
Core infrastructure modules for A101 HR Profile Generator frontend.

Contains error recovery, state management, and other core utilities.

Examples:
  python> from frontend.core.error_recovery import ErrorRecoveryCoordinator
  python> coordinator = ErrorRecoveryCoordinator(api_client)
"""

from .error_recovery import ErrorRecoveryCoordinator, RetryConfig, CircuitBreakerConfig

__all__ = ["ErrorRecoveryCoordinator", "RetryConfig", "CircuitBreakerConfig"]

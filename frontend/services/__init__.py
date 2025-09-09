"""
Frontend services module.

Содержит API клиенты и сервисные классы для взаимодействия с backend.
"""

from .api_client import APIClient, APIError, handle_api_error

__all__ = ["APIClient", "APIError", "handle_api_error"]

"""
Frontend utils module.

Содержит утилиты и конфигурацию для frontend приложения.
"""

from .config import FrontendConfig, config, get_version, is_production, is_development

__all__ = ['FrontendConfig', 'config', 'get_version', 'is_production', 'is_development']
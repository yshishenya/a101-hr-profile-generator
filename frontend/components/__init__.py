"""
Frontend components module.

Модульная структура компонентов:
- ui/: UI компоненты (авторизация, хедер, статистика)
- core/: Основные бизнес-компоненты (поиск, генерация, просмотр)
"""

# UI компоненты
from .ui.auth_component import AuthComponent
from .ui.header_component import HeaderComponent
from .ui.stats_component import StatsComponent

# Core компоненты
from .core.search_component import SearchComponent
from .core.generator_component import GeneratorComponent
from .core.profile_viewer_component import ProfileViewerComponent
from .core.files_manager_component import FilesManagerComponent

__all__ = [
    # UI
    "AuthComponent",
    "HeaderComponent",
    "StatsComponent",
    # Core
    "SearchComponent",
    "GeneratorComponent",
    "ProfileViewerComponent",
    "FilesManagerComponent",
]

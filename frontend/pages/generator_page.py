"""
@doc
GeneratorPage - Композитная страница генератора профилей.

Собирает вместе модульные компоненты для создания единого пользовательского интерфейса:
- SearchComponent: Поиск и выбор должностей
- GeneratorComponent: Управление генерацией профилей
- ProfileViewerComponent: Отображение сгенерированных профилей
- FilesManagerComponent: Скачивание файлов профилей

Обеспечивает взаимодействие между компонентами через систему событий.

Examples:
  python> generator_page = GeneratorPage(api_client)
  python> await generator_page.render()
"""

import logging
from typing import Dict, Any

from nicegui import ui
from ..services.api_client import APIClient
from ..components.core.search_component import SearchComponent
from ..components.core.generator_component import GeneratorComponent
from ..components.core.profile_viewer_component import ProfileViewerComponent
from ..components.core.files_manager_component import FilesManagerComponent

logger = logging.getLogger(__name__)


class GeneratorPage:
    """
    @doc
    Композитная страница, объединяющая модульные компоненты генератора.
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

        # Инициализация компонентов
        self.search = SearchComponent(api_client)
        self.generator = GeneratorComponent(api_client)
        self.viewer = ProfileViewerComponent(api_client)
        self.files = FilesManagerComponent(api_client)

        # Связывание компонентов через события
        self._connect_components()

    def _connect_components(self):
        """Связывание компонентов через систему событий."""
        self.search.on_position_selected = self.generator.set_position
        self.search.on_profiles_found = self.viewer.show_profile_list
        self.generator.on_generation_complete = self.viewer.show_profile
        self.viewer.on_download_request = self.files.download_file

        logger.info("Generator components connected successfully")

    async def render(self):
        """
        @doc
        Рендеринг всей страницы генератора.

        Создает layout и рендерит все дочерние компоненты.
        """
        # Загружаем начальные данные для поиска
        await self.search.load_search_data()

        with ui.column().classes("w-full gap-6"):
            # 1. Секция поиска
            with ui.card().classes("w-full"):
                with ui.card_section():
                    await self.search.render_search_section()

            # 2. Секция генерации
            with ui.card().classes("w-full"):
                with ui.card_section():
                    await self.generator.render_generator_section()

            # 3. Секция просмотра (изначально пустая)
            with ui.card().classes("w-full"):
                 with ui.card_section():
                    await self.viewer.render_profile_viewer()

            # 4. Секция управления файлами (может быть скрыта или упрощена)
            with ui.card().classes("w-full"):
                 with ui.card_section():
                    await self.files.render_files_section()

    async def reload_search_data(self):
        """Перезагрузка данных для компонента поиска."""
        await self.search.force_reload_data()

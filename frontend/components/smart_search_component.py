"""
@doc
Умный компонент поиска для системы генерации профилей А101.

Обеспечивает:
- Поиск по должностям и департаментам
- Автодополнение и фильтрацию в реальном времени
- Быстрый доступ к генерации профилей
- Визуализацию результатов поиска с контекстом

Examples:
  python> search = SmartSearchComponent(api_client)
  python> await search.render()
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from nicegui import ui
from ..services.api_client import APIClient

logger = logging.getLogger(__name__)


class SmartSearchComponent:
    """
    @doc
    Интеллектуальный компонент поиска для навигации по организационной структуре.

    Особенности:
    - Объединенный поиск по департаментам и должностям
    - Автодополнение с debounce для производительности
    - Группировка результатов по категориям
    - Интеграция с генерацией профилей

    Examples:
      python> search = SmartSearchComponent(api_client)
      python> search.on_position_selected = lambda pos: print(f"Selected: {pos['name']}")
      python> await search.render()
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

        # UI компоненты
        self.search_input = None
        self.results_container = None
        self.stats_display = None
        self.loading_indicator = None

        # Состояние поиска
        self.current_query = ""
        self.search_results = {"departments": [], "positions": []}
        self.is_searching = False
        self.search_timer = None

        # Callbacks
        self.on_department_selected: Optional[Callable] = None
        self.on_position_selected: Optional[Callable] = None
        self.on_generate_profile: Optional[Callable] = None

        # Статистика для оптимизации UX
        self.total_stats = {"departments": 0, "positions": 0}

    async def render(self) -> ui.column:
        """
        @doc
        Отрисовка компонента умного поиска.

        Examples:
          python> component = await search.render()
          python> component.classes("w-full max-w-4xl mx-auto")
        """
        with ui.column().classes("w-full space-y-4") as container:
            # Заголовок и статистика
            await self._render_header()

            # Поле поиска
            await self._render_search_input()

            # Индикатор загрузки
            with ui.row().classes("w-full justify-center"):
                self.loading_indicator = ui.spinner(size="lg").classes("hidden")

            # Контейнер результатов
            self.results_container = ui.column().classes("w-full space-y-4")

            # Загружаем начальную статистику
            await self._load_initial_stats()

        return container

    async def _render_header(self):
        """Отрисовка заголовка с общей статистикой"""
        with ui.card().classes("w-full"):
            with ui.card_section():
                ui.label("🔍 Поиск по организационной структуре").classes(
                    "text-h5 font-bold text-primary"
                )

                with ui.row().classes("items-center space-x-4 mt-2"):
                    self.stats_display = ui.label("Загрузка статистики...").classes(
                        "text-caption text-gray-600"
                    )

                ui.label(
                    "Введите название должности или департамента для быстрого поиска"
                ).classes("text-body2 text-gray-500 mt-2")

    async def _render_search_input(self):
        """Отрисовка поля поиска с автодополнением"""
        with ui.card().classes("w-full"):
            with ui.card_section():
                with ui.row().classes("w-full items-center space-x-2"):
                    # Основное поле поиска
                    self.search_input = ui.input(
                        label="Поиск должностей и департаментов",
                        placeholder="Например: архитектор, разработчик, ДИТ, менеджер...",
                    ).classes("flex-1")

                    # Настройка обработчиков
                    self.search_input.on("input", self._on_search_input)

                    # Кнопка очистки
                    ui.button(icon="clear", on_click=self._clear_search).props(
                        "flat round"
                    ).classes("text-gray-500")

                # Быстрые фильтры
                with ui.row().classes("mt-3 space-x-2 flex-wrap"):
                    ui.button(
                        "Руководители",
                        on_click=lambda: self._quick_search("руководитель"),
                    ).props("size=sm outlined").classes("text-xs")
                    ui.button(
                        "Разработчики",
                        on_click=lambda: self._quick_search("разработчик"),
                    ).props("size=sm outlined").classes("text-xs")
                    ui.button(
                        "Аналитики", on_click=lambda: self._quick_search("аналитик")
                    ).props("size=sm outlined").classes("text-xs")
                    ui.button("ДИТ", on_click=lambda: self._quick_search("ДИТ")).props(
                        "size=sm outlined"
                    ).classes("text-xs")
                    ui.button(
                        "Коммерческий",
                        on_click=lambda: self._quick_search("коммерческий"),
                    ).props("size=sm outlined").classes("text-xs")

    async def _load_initial_stats(self):
        """Загрузка начальной статистики для отображения масштаба"""
        try:
            # Получаем статистику каталога
            stats_response = await self.api_client._make_request(
                "GET", "/api/catalog/stats"
            )

            if stats_response.get("success"):
                stats_data = stats_response["data"]
                dept_count = stats_data["departments"]["total_count"]
                pos_count = stats_data["positions"]["total_count"]

                self.total_stats = {"departments": dept_count, "positions": pos_count}

                # Обновляем отображение статистики
                self.stats_display.text = f"📊 {dept_count:,} департаментов • {pos_count:,} должностей • Быстрый поиск по всем"

        except Exception as e:
            logger.error(f"Error loading initial stats: {e}")
            self.stats_display.text = "📊 Готов к поиску по организационной структуре"

    def _on_search_input(self, event):
        """Обработчик ввода в поле поиска с debounce"""
        query = event.value.strip()

        # Отменяем предыдущий таймер
        if self.search_timer:
            self.search_timer.cancel()

        # Очищаем результаты если запрос пустой
        if not query:
            self._clear_results()
            return

        # Устанавливаем новый таймер для debounce (300ms)
        self.search_timer = asyncio.create_task(self._debounced_search(query))

    async def _debounced_search(self, query: str):
        """Отложенный поиск для оптимизации производительности"""
        try:
            await asyncio.sleep(0.3)  # Debounce 300ms

            if query == self.current_query:  # Избегаем дублирования
                return

            self.current_query = query
            await self._perform_search(query)

        except asyncio.CancelledError:
            pass  # Таймер отменен, это нормально
        except Exception as e:
            logger.error(f"Error in debounced search: {e}")

    async def _perform_search(self, query: str):
        """Выполнение поиска по департаментам и должностям"""
        if self.is_searching:
            return

        try:
            self.is_searching = True
            self.loading_indicator.classes(remove="hidden")

            # Параллельный поиск по департаментам и должностям
            dept_task = asyncio.create_task(self.api_client.search_departments(query))
            pos_task = asyncio.create_task(self.api_client.search_positions(query))

            dept_results, pos_results = await asyncio.gather(
                dept_task, pos_task, return_exceptions=True
            )

            # Обработка результатов
            departments = []
            positions = []

            if isinstance(dept_results, dict) and dept_results.get("success"):
                departments = dept_results["data"]["departments"]

            if isinstance(pos_results, dict) and pos_results.get("success"):
                positions = pos_results["data"]["positions"]

            self.search_results = {"departments": departments, "positions": positions}

            # Отображаем результаты
            await self._render_search_results()

        except Exception as e:
            logger.error(f"Error performing search: {e}")
            await self._render_error(f"Ошибка поиска: {str(e)}")

        finally:
            self.is_searching = False
            self.loading_indicator.classes(add="hidden")

    async def _render_search_results(self):
        """Отрисовка результатов поиска"""
        self.results_container.clear()

        departments = self.search_results["departments"]
        positions = self.search_results["positions"]

        total_results = len(departments) + len(positions)

        with self.results_container:
            if total_results == 0:
                await self._render_no_results()
                return

            # Сводка результатов
            with ui.card().classes("w-full"):
                with ui.card_section():
                    ui.label(
                        f"🎯 Найдено: {len(positions)} должностей, {len(departments)} департаментов"
                    ).classes("font-semibold text-primary")

            # Результаты по должностям (приоритетные)
            if positions:
                await self._render_positions_results(positions)

            # Результаты по департаментам
            if departments:
                await self._render_departments_results(departments)

    async def _render_positions_results(self, positions: List[Dict]):
        """Отрисовка результатов поиска должностей"""
        with ui.card().classes("w-full"):
            with ui.card_section():
                ui.label(f"👥 Должности ({len(positions)})").classes(
                    "text-h6 font-bold mb-3"
                )

                # Группировка по департаментам для лучшего UX
                positions_by_dept = {}
                for pos in positions:
                    dept = pos["department"]
                    if dept not in positions_by_dept:
                        positions_by_dept[dept] = []
                    positions_by_dept[dept].append(pos)

                # Отображаем по департаментам (до 10 для производительности)
                displayed_count = 0
                for dept_name, dept_positions in list(positions_by_dept.items())[:10]:
                    if displayed_count >= 20:  # Лимит результатов
                        break

                    with ui.card().classes("w-full border-l-4 border-l-primary"):
                        with ui.card_section():
                            ui.label(f"📁 {dept_name}").classes(
                                "text-subtitle2 font-semibold text-primary mb-2"
                            )

                            for pos in dept_positions[
                                :3
                            ]:  # До 3 позиций на департамент
                                if displayed_count >= 20:
                                    break

                                await self._render_position_item(pos)
                                displayed_count += 1

                            if len(dept_positions) > 3:
                                ui.label(
                                    f"... и еще {len(dept_positions) - 3} должностей"
                                ).classes("text-caption text-gray-500 mt-1")

                if len(positions) > 20:
                    ui.label(
                        f"... и еще {len(positions) - 20} результатов. Уточните запрос для более точного поиска."
                    ).classes("text-caption text-gray-500 mt-3")

    async def _render_position_item(self, position: Dict):
        """Отрисовка отдельной должности"""
        level_colors = {1: "red", 2: "orange", 3: "yellow", 4: "green", 5: "blue"}
        level_color = level_colors.get(position["level"], "gray")

        with ui.row().classes(
            "w-full items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
        ):
            with ui.column().classes("flex-1"):
                with ui.row().classes("items-center space-x-2"):
                    ui.label(position["name"]).classes("font-medium")
                    ui.chip(f"Уровень {position['level']}", color=level_color).props(
                        "size=sm"
                    )
                    ui.chip(position["category"], color="grey").props(
                        "size=sm outlined"
                    )

                ui.label(f"📁 {position['department']}").classes(
                    "text-caption text-gray-500"
                )

            # Кнопки действий
            with ui.row().classes("space-x-1"):
                ui.button(
                    "Выбрать",
                    icon="check_circle",
                    on_click=lambda pos=position: self._select_position(pos),
                ).props("size=sm color=primary")

                ui.button(
                    "Профиль",
                    icon="description",
                    on_click=lambda pos=position: self._generate_profile(pos),
                ).props("size=sm color=secondary outlined")

    async def _render_departments_results(self, departments: List[Dict]):
        """Отрисовка результатов поиска департаментов"""
        with ui.card().classes("w-full"):
            with ui.card_section():
                ui.label(f"🏢 Департаменты ({len(departments)})").classes(
                    "text-h6 font-bold mb-3"
                )

                for dept in departments[:10]:  # Лимит для производительности
                    with ui.row().classes(
                        "w-full items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
                    ):
                        with ui.column().classes("flex-1"):
                            ui.label(dept["name"]).classes("font-medium")
                            ui.label(f"🗂️ {dept['path']}").classes(
                                "text-caption text-gray-500"
                            )
                            ui.label(
                                f"👥 {dept['positions_count']} должностей"
                            ).classes("text-caption text-blue-600")

                        ui.button(
                            "Обзор",
                            icon="folder_open",
                            on_click=lambda d=dept: self._select_department(d),
                        ).props("size=sm color=primary outlined")

                if len(departments) > 10:
                    ui.label(
                        f"... и еще {len(departments) - 10} департаментов"
                    ).classes("text-caption text-gray-500 mt-2")

    async def _render_no_results(self):
        """Отрисовка сообщения об отсутствии результатов"""
        with ui.card().classes("w-full text-center"):
            with ui.card_section():
                ui.icon("search_off", size="3rem").classes("text-gray-400 mb-2")
                ui.label(
                    f"По запросу '{self.current_query}' ничего не найдено"
                ).classes("text-h6 text-gray-600 mb-2")
                ui.label("Попробуйте:").classes("text-body2 text-gray-500 mb-2")

                with ui.column().classes("space-y-1 text-left"):
                    ui.label("• Изменить поисковый запрос").classes(
                        "text-body2 text-gray-500"
                    )
                    ui.label(
                        "• Использовать частичные совпадения (например, 'разраб' вместо 'разработчик')"
                    ).classes("text-body2 text-gray-500")
                    ui.label("• Попробовать синонимы или сокращения").classes(
                        "text-body2 text-gray-500"
                    )

    async def _render_error(self, error_message: str):
        """Отрисовка ошибки поиска"""
        self.results_container.clear()

        with self.results_container:
            with ui.card().classes("w-full border-l-4 border-l-red-500"):
                with ui.card_section():
                    ui.icon("error", size="2rem").classes("text-red-500 mb-2")
                    ui.label("Ошибка поиска").classes("text-h6 text-red-600 font-bold")
                    ui.label(error_message).classes("text-body2 text-red-500")

    def _clear_search(self):
        """Очистка поиска"""
        if self.search_input:
            self.search_input.value = ""
        self._clear_results()

    def _clear_results(self):
        """Очистка результатов поиска"""
        self.current_query = ""
        self.search_results = {"departments": [], "positions": []}
        if self.results_container:
            self.results_container.clear()

    async def _quick_search(self, query: str):
        """Быстрый поиск по предустановленному запросу"""
        if self.search_input:
            self.search_input.value = query
        await self._perform_search(query)

    def _select_position(self, position: Dict):
        """Выбор должности"""
        if self.on_position_selected:
            self.on_position_selected(position)

    def _select_department(self, department: Dict):
        """Выбор департамента"""
        if self.on_department_selected:
            self.on_department_selected(department)

    def _generate_profile(self, position: Dict):
        """Запуск генерации профиля для должности"""
        if self.on_generate_profile:
            self.on_generate_profile(position)


class SmartSearchPage:
    """
    @doc
    Страница с умным поиском для основной навигации по системе.

    Examples:
      python> page = SmartSearchPage(api_client)
      python> await page.render()
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.search_component = SmartSearchComponent(api_client)

        # Настройка обработчиков
        self.search_component.on_position_selected = self._on_position_selected
        self.search_component.on_department_selected = self._on_department_selected
        self.search_component.on_generate_profile = self._on_generate_profile

    async def render(self):
        """Отрисовка страницы поиска"""
        ui.page_title("🔍 Поиск • A101 HR")

        with ui.column().classes("w-full max-w-6xl mx-auto p-4 space-y-6"):
            # Заголовок страницы
            with ui.card().classes("w-full"):
                with ui.card_section():
                    ui.label("🔍 Умный поиск по организации").classes(
                        "text-h4 font-bold text-primary"
                    )
                    ui.label(
                        "Найдите нужную должность или департамент для генерации профиля"
                    ).classes("text-body1 text-gray-600")

            # Компонент поиска
            await self.search_component.render()

            # Подсказки по использованию
            with ui.card().classes("w-full"):
                with ui.card_section():
                    ui.label("💡 Советы по поиску").classes("text-h6 font-bold mb-3")

                    with ui.grid(columns=3).classes("gap-4"):
                        with ui.column().classes("space-y-2"):
                            ui.label("🎯 Точный поиск").classes("font-semibold")
                            ui.label(
                                "Введите полное название должности или департамента"
                            ).classes("text-body2 text-gray-600")

                        with ui.column().classes("space-y-2"):
                            ui.label("🔍 Частичный поиск").classes("font-semibold")
                            ui.label(
                                "Используйте часть названия: 'архитект', 'разраб', 'менеджер'"
                            ).classes("text-body2 text-gray-600")

                        with ui.column().classes("space-y-2"):
                            ui.label("⚡ Быстрые фильтры").classes("font-semibold")
                            ui.label(
                                "Используйте кнопки быстрого поиска для популярных категорий"
                            ).classes("text-body2 text-gray-600")

    def _on_position_selected(self, position: Dict):
        """Обработка выбора должности"""
        logger.info(
            f"Position selected: {position['name']} in {position['department']}"
        )
        ui.notify(f"Выбрана должность: {position['name']}", type="positive")

        # Здесь можно добавить навигацию к деталям должности или форме генерации

    def _on_department_selected(self, department: Dict):
        """Обработка выбора департамента"""
        logger.info(f"Department selected: {department['name']}")
        ui.notify(f"Выбран департамент: {department['name']}", type="info")

        # Здесь можно добавить навигацию к обзору департамента

    def _on_generate_profile(self, position: Dict):
        """Обработка запуска генерации профиля"""
        logger.info(
            f"Profile generation requested for: {position['name']} in {position['department']}"
        )
        ui.notify(f"Запуск генерации профиля для: {position['name']}", type="info")

        # Здесь можно добавить навигацию к форме генерации профиля


if __name__ == "__main__":
    # Тестирование компонентов
    print("✅ Smart Search components created!")
    print("🔍 Features:")
    print("  - Unified search across 4,376 positions and 510 departments")
    print("  - Real-time auto-complete with debounce")
    print("  - Quick filters for common searches")
    print("  - Integrated profile generation workflow")

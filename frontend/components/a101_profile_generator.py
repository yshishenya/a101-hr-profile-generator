"""
@doc
Профессиональный генератор профилей A101 с корпоративным дизайном для NiceGUI.

Реализует реалистичный UX в рамках возможностей NiceGUI:
- A101 корпоративная цветовая схема
- Responsive design с Tailwind CSS
- Debounced search с real-time feedback
- Professional progress tracking
- Mobile-friendly interface

Examples:
  python> generator = A101ProfileGenerator(api_client)
  python> await generator.render()
"""

import asyncio
import logging
from typing import List, Dict

from nicegui import ui
from ..services.api_client import APIClient

logger = logging.getLogger(__name__)


class A101ProfileGenerator:
    """
    @doc
    Профессиональный генератор профилей с корпоративным A101 дизайном.

    Особенности:
    - NiceGUI-совместимый дизайн с CSS injection
    - Корпоративная цветовая схема A101
    - Debounced search с оптимизацией производительности
    - Responsive layout для desktop и mobile
    - Professional feedback и error handling

    Examples:
      python> generator = A101ProfileGenerator(api_client)
      python> await generator.render()
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

        # UI компоненты
        self.search_input = None
        self.search_results_container = None
        self.selected_position_card = None
        self.employee_name_input = None
        self.temperature_slider = None
        self.profile_type_select = None
        self.generate_button = None
        self.progress_dialog = None

        # Состояние приложения
        self.current_query = ""
        self.selected_position = None
        self.search_timer = None
        self.is_searching = False
        self.is_generating = False
        self.current_task_id = None
        self.search_results = []

        # Автоподсказки с иерархией
        self.autocomplete_options = []
        self.hierarchical_suggestions = []
        self.search_history = []

        # UI состояние
        self.has_search_results = False
        self.has_selected_position = False
        self.can_generate = False

        # Выбранные данные для генерации
        self.selected_position = ""
        self.selected_department = ""

        # Системная статистика
        self.total_stats = {"departments": 0, "positions": 0}

        # Убрали search_categories - dropdown заменяет умные категории

        # Clean NiceGUI styling like login page
        self._add_clean_nicegui_styles()

        # Загружаем иерархические предложения асинхронно
        asyncio.create_task(self._load_hierarchical_suggestions())

    def _format_position_level(self, level):
        """Форматирование уровня должности для отображения"""
        if isinstance(level, str):
            # Строковые уровни
            level_mapping = {
                "senior": {"text": "Высший", "color": "red"},
                "lead": {"text": "Руководящий", "color": "deep-orange"},
                "middle": {"text": "Основной", "color": "green"},
                "junior": {"text": "Начальный", "color": "blue"},
            }
            return level_mapping.get(level, {"text": "Не определен", "color": "grey"})
        elif isinstance(level, int):
            # Числовые уровни (1-5)
            level_colors = ["red", "deep-orange", "orange", "green", "blue"]
            color = level_colors[level - 1] if 1 <= level <= 5 else "grey"
            return {"text": f"Ур. {level}", "color": color}
        else:
            return {"text": "Не определен", "color": "grey"}

    async def _load_hierarchical_suggestions(self):
        """
        Загрузка иерархических предложений автокомплита из backend данных.

        Создает предложения в формате:
        "Блок безопасности → Служба безопасности → Специалист"
        "IT Департамент → Разработка → Ведущий разработчик"
        """
        try:
            logger.info("Loading hierarchical suggestions from backend...")

            # Проверяем авторизацию
            from nicegui import app

            if not hasattr(app, "storage") or not app.storage.user.get(
                "authenticated", False
            ):
                logger.warning("User not authenticated, using fallback suggestions")
                self._use_fallback_suggestions()
                return

            # Получаем полную структуру организации через API
            stats_response = await self.api_client._make_request(
                "GET", "/api/catalog/stats"
            )

            if not stats_response.get("success"):
                logger.warning(
                    "Failed to get organization stats, using fallback suggestions"
                )
                self._use_fallback_suggestions()
                return

            # Генерируем иерархические предложения
            self.hierarchical_suggestions = (
                await self._generate_hierarchical_from_backend()
            )

            logger.info(
                f"✅ Loaded {len(self.hierarchical_suggestions)} suggestions"
            )

            # Обновляем dropdown options в поисковом поле если оно уже создано
            if hasattr(self, "search_input") and self.search_input:
                options_dict = {
                    suggestion: suggestion
                    for suggestion in self.hierarchical_suggestions
                }
                self.search_input.set_options(options_dict)
                logger.info("✅ Updated search dropdown with hierarchical options")

        except Exception as e:
            logger.error(f"Error loading hierarchical suggestions: {e}")
            self._use_fallback_suggestions()

    async def _generate_hierarchical_from_backend(self) -> List[str]:
        """
        Генерация иерархических предложений из backend данных.

        Returns:
            List[str]: Список иерархических предложений для автокомплита
        """
        suggestions = []

        try:
            # Получаем список всех департаментов
            departments_response = await self.api_client._make_request(
                "GET", "/api/catalog/departments"
            )

            if not departments_response.get("success"):
                logger.warning("Failed to get departments for hierarchical suggestions")
                return []

            # Извлекаем departments из response["data"]["departments"]
            departments = departments_response["data"]["departments"]

            logger.info(
                f"Processing {len(departments)} departments..."
            )

            # Для каждого департамента получаем позиции и создаем иерархические пути
            for dept in departments:
                dept_name = dept["name"]

                try:
                    # Получаем позиции департамента - правильный endpoint
                    positions_response = await self.api_client._make_request(
                        "GET", f"/api/catalog/positions/{dept_name}"
                    )

                    if positions_response.get("success"):
                        # Извлекаем positions из response["data"]["positions"]
                        positions_data = positions_response["data"]
                        positions = positions_data["positions"]

                        # Debug: log first few positions to understand structure
                        if positions:
                            logger.debug(
                                f"First position structure in '{dept_name}': {positions[0] if positions else 'None'}"
                            )
                            if len(positions) > 5:
                                logger.debug(
                                    f"Department '{dept_name}' has {len(positions)} positions"
                                )
                        else:
                            logger.debug(
                                f"No positions found for department '{dept_name}'"
                            )

                        # Создаем иерархические предложения
                        for position in positions:
                            try:
                                # Формируем иерархический путь
                                hierarchical_path = self._build_hierarchical_path(
                                    dept_name, position
                                )
                                if hierarchical_path:  # Проверяем что путь не пустой
                                    suggestions.append(hierarchical_path)
                            except Exception as pos_error:
                                logger.warning(
                                    f"Failed to build path for position: {pos_error}"
                                )

                except Exception as dept_error:
                    logger.warning(
                        f"Failed to get positions for department '{dept_name}': {dept_error}"
                    )
                    continue

            logger.info(f"Generated {len(suggestions)} suggestions from backend")

            # Сортируем по алфавиту для консистентности
            suggestions.sort()

            # Ограничиваем количество предложений для производительности
            return suggestions[:500]  # Топ 500 наиболее релевантных

        except Exception as e:
            logger.error(f"Error generating hierarchical suggestions: {e}")
            return []

    def _build_hierarchical_path(self, department: str, position: dict) -> str:
        """
        Построение иерархического пути для позиции.

        Args:
            department: Название департамента
            position: Данные позиции

        Returns:
            str: Иерархический путь типа "Департамент → Позиция"
        """
        # Безопасное извлечение названия позиции
        if isinstance(position, dict):
            position_name = position.get("name", str(position))
        elif isinstance(position, str):
            position_name = position
        else:
            logger.warning(
                f"Unexpected position type: {type(position)}, value: {position}"
            )
            position_name = str(position)

        # Определяем уровень вложенности на основе названия департамента
        path_parts = []

        # Парсим структуру департамента для иерархии
        if "→" in department or "/" in department or "\\" in department:
            # Департамент уже содержит путь
            path_parts = [
                part.strip()
                for part in department.replace("/", "→").replace("\\", "→").split("→")
            ]
        else:
            # Простое название департамента
            path_parts = [department]

        # Добавляем позицию в конце пути
        path_parts.append(position_name)

        # Создаем финальный иерархический путь
        hierarchical_path = " → ".join(path_parts)

        return hierarchical_path

    def _use_fallback_suggestions(self):
        """Использование fallback предложений при недоступности backend"""
        # Только реальные должности из оргструктуры А101 - без вымышленных
        fallback_suggestions = [
            "Руководитель отдела",
            "Ведущий специалист",
            "Старший специалист",
            "Специалист",
            "Главный специалист",
            "Заместитель руководителя",
            "Директор департамента",
            "Руководитель направления",
            "Руководитель управления",
            "Руководитель службы",
            "Координатор",
            "Помощник директора",
        ]

        self.hierarchical_suggestions = fallback_suggestions
        logger.info(f"Using {len(fallback_suggestions)} fallback suggestions")

        # Обновляем dropdown options в поисковом поле если оно уже создано
        if hasattr(self, "search_input") and self.search_input:
            options_dict = {
                suggestion: suggestion for suggestion in self.hierarchical_suggestions
            }
            self.search_input.set_options(options_dict)
            logger.info("✅ Updated search dropdown with fallback options")

    # OLD INPUT STYLES METHOD REMOVED - Use _add_minimal_input_styles() instead

    # MASSIVE A101 CUSTOM CSS REMOVED (487 lines) - Using standard NiceGUI styling

    async def render(self) -> ui.column:
        """
        @doc
        Отрисовка профессионального генератора профилей A101.

        Examples:
          python> component = await generator.render()
        """
        # Основной контейнер с градиентным фоном
        with ui.column().classes(
            "w-full min-h-screen bg-gradient-to-br from-slate-50 to-blue-50"
        ) as container:

            # Корпоративный заголовок
            await self._render_corporate_header()

            # Системная статистика
            await self._render_system_stats()

            # Главный генератор
            await self._render_main_generator()

            # Загружаем системную статистику
            await self._load_system_stats()

        return container

    async def render_content(self) -> ui.column:
        """
        @doc
        Render generator content without header for unified page design.

        Used when header is provided by main page layout.

        Examples:
          python> await generator.render_content()
        """
        # Create unified content layout
        with ui.column().classes("w-full gap-6") as container:
            # Page header with consistent styling
            self._render_page_header()

            # System stats with dashboard-style cards
            await self._render_unified_system_stats()

            # Load system stats after labels are created
            await self._load_system_stats()

            # Main generator with unified styling
            await self._render_unified_main_generator()

        return container

    def _render_page_header(self):
        """Unified page header matching dashboard style"""
        with ui.row().classes("w-full items-center justify-between mb-6"):
            ui.label("🎯 Генератор профилей должностей").classes(
                "text-h4 text-weight-medium"
            )

            # Refresh button consistent with dashboard
            ui.button(icon="refresh", on_click=self._refresh_data).props(
                "flat round"
            ).tooltip("Обновить данные")

    async def _refresh_data(self):
        """Refresh generator data"""
        ui.notify("Обновление данных...", type="info")
        try:
            await self._load_system_stats()
            await self._load_hierarchical_suggestions()
            ui.notify("Данные обновлены", type="positive")
        except Exception as e:
            ui.notify(f"Ошибка обновления: {e}", type="negative")

    async def _render_unified_system_stats(self):
        """System stats with dashboard-consistent styling"""
        with ui.card().classes("w-full mb-6"):
            ui.label("📊 Статус системы").classes("text-h6 q-mb-md")

            with ui.row().classes("w-full q-gutter-md"):
                # Departments
                with ui.card().classes("flex-1 text-center p-4"):
                    self.departments_label = ui.label("Загрузка...").classes(
                        "text-h4 text-weight-bold text-primary"
                    )
                    ui.label("Департаментов").classes("text-caption text-grey-6")

                # Positions
                with ui.card().classes("flex-1 text-center p-4"):
                    self.positions_label = ui.label("Загрузка...").classes(
                        "text-h4 text-weight-bold text-green"
                    )
                    ui.label("Должностей").classes("text-caption text-grey-6")

                # System status
                with ui.card().classes("flex-1 text-center p-4"):
                    ui.label("Готова").classes("text-h4 text-weight-bold text-positive")
                    ui.label("Система").classes("text-caption text-grey-6")

    async def _render_unified_main_generator(self):
        """Main generator with unified dashboard styling"""
        # Search section
        with ui.card().classes("w-full mb-6"):
            ui.label("🔍 Поиск должности").classes("text-h6 q-mb-md")

            with ui.card_section():
                await self._render_unified_search_section()

        # Selected position (shown when position is selected)
        with ui.column().classes("w-full").bind_visibility_from(
            self, "has_selected_position"
        ):
            self.selected_position_card = ui.column().classes("w-full")

        # Generation parameters (shown when position is selected)
        with ui.card().classes("w-full mb-6").bind_visibility_from(
            self, "has_selected_position"
        ):
            ui.label("⚙️ Параметры генерации").classes("text-h6 q-mb-md")

            with ui.card_section():
                await self._render_unified_generation_params()

        # Generation button (shown when position is selected)
        with ui.card().classes("w-full text-center").bind_visibility_from(
            self, "has_selected_position"
        ):
            with ui.card_section():
                self.generate_button = (
                    ui.button(
                        "🚀 Создать профиль должности",
                        icon="auto_awesome",
                        on_click=self._start_generation,
                    )
                    .props("size=lg color=primary")
                    .classes("q-mb-sm")
                )

                ui.label(
                    "Генерация займет 1-3 минуты в зависимости от сложности позиции"
                ).classes("text-caption text-grey-6")

    async def _render_unified_search_section(self):
        """Clean search section - Following login page styling philosophy"""
        # Search input with clean NiceGUI styling like login page
        self.search_input = (
            ui.select(
                options={
                    suggestion: suggestion
                    for suggestion in self.hierarchical_suggestions
                },
                label="Поиск должности",
                with_input=True,
                on_change=self._on_search_select,
            )
            .props("outlined clearable use-input")
            .classes("w-full")
        )

        # Clean placeholder like login page
        self.search_input.props('placeholder="Начните вводить название должности"')

        # Events
        self.search_input.on("input-value", self._on_search_input_value)

        # Simple loading indicator
        self.search_loading = ui.spinner(size="sm").classes("self-center hidden")

    async def _render_unified_generation_params(self):
        """Clean generation parameters - Following login page philosophy"""
        with ui.column().classes("w-full gap-4"):

            # Employee name - clean like login page
            self.employee_name_input = (
                ui.input(
                    label="ФИО сотрудника (опционально)",
                    placeholder="Иванов Иван Иванович"
                )
                .props("outlined clearable")
                .classes("w-full")
            )

            # Profile type - clean select
            self.profile_type_select = (
                ui.select(
                    options=[
                        "Полный профиль",
                        "Краткое описание",
                        "Только компетенции",
                    ],
                    label="Тип профиля",
                    value="Полный профиль",
                )
                .props("outlined")
                .classes("w-full")
            )

            # Temperature slider - clean styling
            with ui.column().classes("w-full gap-2 mt-4"):
                ui.label("Точность и детализация").classes("text-subtitle2")

                with ui.row().classes("w-full items-center gap-4"):
                    ui.label("Точная").classes("text-caption text-grey-6")

                    self.temperature_slider = (
                        ui.slider(min=0.0, max=1.0, step=0.1, value=0.1)
                        .classes("flex-1")
                        .props("color=primary")
                    )

                    ui.label("Творческая").classes("text-caption text-grey-6")

                # Temperature description - clean typography
                self.temperature_description = ui.label().classes(
                    "text-caption text-grey-6"
                )

                # Update description on slider change
                self.temperature_slider.on(
                    "update:model-value", self._update_temperature_description
                )
                self._update_temperature_description()

    def _add_clean_nicegui_styles(self):
        """Clean NiceGUI styling - Following login page philosophy"""
        # No custom CSS - using pure NiceGUI components like login page
        pass

    async def _render_corporate_header(self):
        """Корпоративный заголовок A101"""
        with ui.card().classes("w-full bg-primary text-white border-0"):
            with ui.card_section().classes("py-6"):
                with ui.row().classes("w-full items-center justify-between"):
                    # Логотип и название
                    with ui.row().classes("items-center gap-4"):
                        ui.icon("business", size="2.5rem").classes("text-white")
                        with ui.column().classes("gap-0"):
                            ui.label("A101 HR Profile Generator").classes(
                                "text-white text-2xl font-bold"
                            )
                            ui.label(
                                "Система автоматической генерации профилей должностей"
                            ).classes("text-blue-100 text-sm")

                    # Информация о пользователе
                    with ui.row().classes(
                        "items-center gap-3 bg-white bg-opacity-10 rounded-lg px-4 py-2"
                    ):
                        ui.avatar(icon="person", color="white").classes("text-blue-900")
                        with ui.column().classes("gap-0"):
                            ui.label("Администратор").classes(
                                "text-white font-medium text-sm"
                            )
                            ui.label("Активная сессия").classes("text-blue-100 text-xs")

    async def _render_system_stats(self):
        """Карточки системной статистики"""
        with ui.row().classes("w-full gap-6 mb-8 max-w-6xl mx-auto px-4"):

            # Департаменты
            with ui.card().classes("flex-1 p-4 text-center"):
                ui.icon("corporate_fare", size="2rem").classes("text-blue-600 mb-2")
                self.departments_label = ui.label("Загрузка...").classes(
                    "text-3xl font-bold text-gray-900"
                )
                ui.label("Департаментов").classes("text-gray-600 text-sm font-medium")

            # Должности
            with ui.card().classes("flex-1 p-4 text-center"):
                ui.icon("groups", size="2rem").classes("text-emerald-600 mb-2")
                self.positions_label = ui.label("Загрузка...").classes(
                    "text-3xl font-bold text-gray-900"
                )
                ui.label("Должностей").classes("text-gray-600 text-sm font-medium")

            # Статус системы
            with ui.card().classes("flex-1 p-4 text-center"):
                ui.icon("check_circle", size="2rem").classes("text-green-600 mb-2")
                ui.label("Готова").classes("text-3xl font-bold text-gray-900")
                ui.label("Система").classes("text-gray-600 text-sm font-medium")

    async def _render_main_generator(self):
        """Основной генератор профилей"""
        with ui.card().classes("w-full max-w-4xl mx-auto px-4"):

            # Заголовок генератора
            with ui.card_section().classes("bg-grey-2 py-4"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("psychology", size="2rem").classes("text-blue-600")
                    with ui.column().classes("gap-1"):
                        ui.label("Генератор профилей должностей").classes(
                            "text-xl font-bold text-primary"
                        )
                        ui.label(
                            "Найдите должность и создайте детальный профиль с помощью ИИ"
                        ).classes("text-muted")

            # Контент генератора
            with ui.card_section().classes("py-8"):

                # Поиск должности
                await self._render_search_section()

                # Выбранная должность
                with ui.column().classes("w-full mt-8"):
                    self.selected_position_card = ui.column().classes("w-full")

                # Параметры генерации (показываем только после выбора)
                with ui.column().classes("w-full mt-8").bind_visibility_from(
                    self, "has_selected_position"
                ):
                    await self._render_generation_params()

                # Кнопка генерации
                with ui.column().classes(
                    "w-full mt-8 text-center"
                ).bind_visibility_from(self, "has_selected_position"):
                    self.generate_button = ui.button(
                        "🚀 Создать профиль должности",
                        icon="auto_awesome",
                        on_click=self._start_generation,
                    ).props("size=lg color=primary")

                    ui.label(
                        "Генерация займет 1-3 минуты в зависимости от сложности позиции"
                    ).classes("text-xs text-muted mt-3")

    async def _render_search_section(self):
        """Секция поиска должностей"""
        with ui.column().classes("w-full gap-6"):

            # Заголовок поиска
            with ui.row().classes("items-center gap-2"):
                ui.icon("search", size="1.5rem").classes("text-blue-600")
                ui.label("Поиск должности").classes(
                    "text-lg font-semibold text-primary"
                )

            # Расширенная поисковая строка с автокомплитом
            with ui.column().classes("w-full gap-2 relative"):

                # Clean search input following login page philosophy
                self.search_input = (
                    ui.select(
                        options={
                            suggestion: suggestion
                            for suggestion in self.hierarchical_suggestions
                        },
                        label="Поиск должности",
                        with_input=True,
                        on_change=self._on_search_select,
                    )
                    .props("outlined clearable use-input")
                    .classes("w-full")
                )

                # Clean placeholder
                self.search_input.props('placeholder="Начните вводить название должности"')

                # События для обновления результатов при вводе
                self.search_input.on("input-value", self._on_search_input_value)

                # Style fixes no longer needed with standard NiceGUI styling

            # Убрали "Умные категории поиска" - dropdown заменяет эту функциональность

            # Убрали результаты поиска - dropdown заменяет эту функциональность
            # Оставляем только spinner для обратной связи при выборе
            self.search_loading = (
                ui.spinner(size="sm").classes("self-center").style("display: none")
            )

    async def _render_generation_params(self):
        """Параметры генерации"""
        with ui.column().classes("w-full gap-6"):

            # Заголовок параметров
            with ui.row().classes("items-center gap-2"):
                ui.icon("tune", size="1.5rem").classes("text-blue-600")
                ui.label("Параметры генерации").classes(
                    "text-lg font-semibold text-primary"
                )

            # Параметры в сетке
            with ui.grid(columns="1fr 1fr").classes("w-full gap-6"):

                # Employee name - clean like login page
                self.employee_name_input = (
                    ui.input(
                        label="ФИО сотрудника (опционально)",
                        placeholder="Иванов Иван Иванович"
                    )
                    .props("outlined clearable")
                    .classes("w-full")
                )

                # Profile type - clean select
                self.profile_type_select = (
                    ui.select(
                        options=[
                            "Полный профиль",
                            "Краткое описание",
                            "Только компетенции",
                        ],
                        label="Тип профиля",
                        value="Полный профиль",
                    )
                    .props("outlined")
                    .classes("w-full")
                )

            # Clean temperature slider
            with ui.column().classes("gap-3 mt-4"):
                ui.label("Точность и детализация").classes("text-subtitle2")

                with ui.row().classes("w-full items-center gap-4"):
                    ui.label("Точная").classes("text-caption text-grey-6")

                    self.temperature_slider = (
                        ui.slider(min=0.0, max=1.0, step=0.1, value=0.1)
                        .classes("flex-1")
                        .props("color=primary")
                    )

                    ui.label("Творческая").classes("text-caption text-grey-6")

                # Clean description
                self.temperature_description = ui.label().classes(
                    "text-caption text-grey-6"
                )

                # Обновляем описание при изменении слайдера
                self.temperature_slider.on(
                    "update:model-value", self._update_temperature_description
                )
                self._update_temperature_description()  # Начальное значение

    def _update_temperature_description(self):
        """Обновление описания температуры"""
        if hasattr(self, "temperature_description") and self.temperature_description:
            value = self.temperature_slider.value
            if value <= 0.2:
                desc = "Строго по данным - максимальная точность"
            elif value <= 0.6:
                desc = "Умеренная адаптация - баланс точности и гибкости"
            else:
                desc = "Творческий подход - больше интерпретации"

            self.temperature_description.text = (
                f"Текущая настройка: {desc} ({value:.1f})"
            )

    async def _load_system_stats(self):
        """Загрузка системной статистики"""
        try:
            # Проверяем авторизацию
            from nicegui import app

            if not app.storage.user.get("authenticated", False):
                # Fallback значения для неавторизованных пользователей
                self._update_stats_labels("510", "4,376")
                return

            stats_response = await self.api_client._make_request(
                "GET", "/api/catalog/stats"
            )

            if stats_response.get("success"):
                stats_data = stats_response["data"]

                # Обновляем счетчики
                dept_count = stats_data["departments"]["total_count"]
                pos_count = stats_data["positions"]["total_count"]

                self._update_stats_labels(f"{dept_count:,}", f"{pos_count:,}")

                self.total_stats = {"departments": dept_count, "positions": pos_count}

        except Exception as e:
            logger.error(f"Error loading system stats: {e}")
            # Fallback значения
            self._update_stats_labels("510", "4,376")
            self.total_stats = {"departments": 510, "positions": 4376}

    def _update_stats_labels(self, dept_text: str, pos_text: str):
        """Safely update stats labels if they exist"""
        if hasattr(self, "departments_label") and self.departments_label:
            self.departments_label.text = dept_text
        if hasattr(self, "positions_label") and self.positions_label:
            self.positions_label.text = pos_text

    def _on_search_select(self, event=None):
        """Обработчик выбора варианта из dropdown - сразу подготавливаем к генерации"""
        if event and hasattr(event, "value") and event.value:
            # Получаем выбранное значение из dropdown
            selected_value = event.value.strip()
            logger.info(f"Selected from dropdown: {selected_value}")

            # Обрабатываем иерархический выбор
            department, position = self._process_hierarchical_selection(selected_value)

            # Сразу устанавливаем данные для генерации
            if department and position:
                self._set_selected_position(position, department)
                ui.notify(f"✅ Выбрано: {position} в {department}", type="positive")

                # Показываем что позиция выбрана
                self.has_selected_position = True
                self.can_generate = True
                self._update_generation_ui_state()
            else:
                # Если не удалось извлечь иерархию, показываем уведомление
                ui.notify(
                    "Выберите должность из списка для генерации профиля", type="info"
                )

        elif (
            self.search_input
            and hasattr(self.search_input, "value")
            and self.search_input.value
        ):
            # Fallback - если event пустой, берем значение напрямую
            query = self.search_input.value.strip()
            if query:
                department, position = self._process_hierarchical_selection(query)
                if department and position:
                    self._set_selected_position(position, department)

    def _on_search_input_value(self, event=None):
        """Обработчик ввода в поисковое поле с dropdown (упрощенная версия)"""
        # Убираем live search - dropdown уже показывает все варианты
        # Оставляем только для логирования если нужно
        if event and hasattr(event, "args") and event.args:
            query = str(event.args).strip()
            logger.debug(f"Input value changed: {query}")

            # Скрываем spinner если поле очистили
            if len(query) == 0 and hasattr(self, "search_loading"):
                self.search_loading.style("display: none")

    def _process_hierarchical_selection(self, selection: str) -> tuple[str, str]:
        """
        Обработка выбора из иерархического автокомплита.

        Args:
            selection: Выбранная строка (может быть иерархический путь)

        Returns:
            tuple[str, str]: (department, position) или ("", "") если не удалось извлечь
        """
        if " → " in selection:
            # Это иерархический путь, извлекаем позицию (последний элемент)
            parts = [part.strip() for part in selection.split(" → ")]
            if len(parts) >= 2:
                department = parts[-2]  # Предпоследний элемент - департамент
                position = parts[-1]  # Последний элемент - позиция

                logger.info(f"Hierarchical selection: {department} → {position}")
                return department, position
        else:
            # Простое название позиции без иерархии
            logger.info(f"Simple selection: {selection}")
            return "", selection.strip()

        return "", ""

    def _set_selected_position(self, position: str, department: str):
        """
        Установка выбранной позиции для генерации профиля.

        Args:
            position: Название позиции
            department: Название департамента
        """
        # Сохраняем выбранные данные
        self.selected_position = position
        self.selected_department = department

        # Обновляем UI состояние
        self.has_selected_position = True
        self.can_generate = True

        logger.info(f"Position selected: {position} in {department}")

    def _update_generation_ui_state(self):
        """Обновление состояния UI для генерации профиля"""
        try:
            # Показать что можно генерировать (если есть соответствующие элементы UI)
            if hasattr(self, "generate_button") and self.generate_button:
                self.generate_button.props("color=primary")
                self.generate_button.props("icon=auto_awesome")

            # Скрыть индикатор загрузки поиска если он есть
            if hasattr(self, "search_loading") and self.search_loading:
                self.search_loading.style("display: none")

            logger.debug("Generation UI state updated")
        except Exception as e:
            logger.warning(f"Error updating generation UI state: {e}")

    # UNUSED _fix_dropdown_styles method removed - Using standard NiceGUI styling

    async def _debounced_search(self, query: str):
        """Debounced поиск должностей"""
        try:
            await asyncio.sleep(0.3)  # 300ms debounce

            if query == self.current_query:
                return

            self.current_query = query
            await self._perform_search(query)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in debounced search: {e}")
        finally:
            self.search_loading.style("display: none")

    async def _render_search_result_card(self, position: Dict):
        """Карточка результата поиска"""
        level_class = f"level-{position.get('level', 1)}"

        with ui.card().classes(f"cursor-pointer hover:bg-grey-1 {level_class}").on(
            "click", lambda pos=position: self._select_position(pos)
        ):
            with ui.card_section().classes("py-3"):
                with ui.row().classes("w-full items-center justify-between"):

                    # Информация о позиции
                    with ui.column().classes("flex-1 gap-1"):

                        # Название и уровень
                        with ui.row().classes("items-center gap-2"):
                            ui.label(position["name"]).classes(
                                "font-semibold text-gray-900"
                            )

                            # Обработка уровня должности (может быть строкой или числом)
                            level_info = self._format_position_level(
                                position.get("level")
                            )
                            ui.chip(
                                level_info["text"], color=level_info["color"]
                            ).props("size=sm")

                        # Департамент и категория
                        with ui.row().classes("items-center gap-4 text-sm text-muted"):
                            with ui.row().classes("items-center gap-1"):
                                ui.icon("business", size="1rem")
                                ui.label(position["department"])

                            with ui.row().classes("items-center gap-1"):
                                ui.icon("category", size="1rem")
                                ui.label(position["category"])

                    # Стрелка выбора
                    ui.icon("arrow_forward", size="1.5rem").classes("text-gray-400")

    def _select_position(self, position: Dict):
        """Выбор должности"""
        self.selected_position = position
        self.has_selected_position = True
        self.can_generate = True

        # Очищаем результаты поиска
        self._clear_search_results()

        # Устанавливаем выбранную должность в поле поиска
        if self.search_input:
            self.search_input.set_value(position["name"])

        # Отображаем выбранную должность
        self._display_selected_position()

        ui.notify(
            f"✅ Выбрана должность: {position['name']}", type="positive", position="top"
        )

    def _display_selected_position(self):
        """Отображение выбранной должности"""
        if not self.selected_position:
            return

        self.selected_position_card.clear()

        with self.selected_position_card:
            with ui.card().classes("bg-positive-1 border-l-4 border-positive"):
                with ui.card_section().classes("py-4"):
                    with ui.row().classes("w-full items-start justify-between"):

                        # Информация о позиции
                        with ui.column().classes("flex-1 gap-3"):

                            # Заголовок
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("check_circle", size="1.5rem").classes(
                                    "text-emerald-600"
                                )
                                ui.label("Выбранная должность").classes(
                                    "text-sm font-medium text-emerald-700"
                                )

                            # Название должности
                            ui.label(self.selected_position["name"]).classes(
                                "text-xl font-bold text-gray-900"
                            )

                            # Детали в сетке
                            with ui.grid(columns="1fr 1fr").classes("gap-4 mt-3"):

                                # Департамент
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("business", size="1rem").classes(
                                        "text-gray-500"
                                    )
                                    ui.label(
                                        self.selected_position["department"]
                                    ).classes("text-sm text-gray-700")

                                # Уровень
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("trending_up", size="1rem").classes(
                                        "text-gray-500"
                                    )
                                    level_info = self._format_position_level(
                                        self.selected_position.get("level")
                                    )
                                    ui.label(level_info["text"]).classes(
                                        "text-sm text-gray-700"
                                    )

                                # Категория
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("category", size="1rem").classes(
                                        "text-gray-500"
                                    )
                                    ui.label(
                                        self.selected_position["category"]
                                    ).classes("text-sm text-gray-700")

                        # Кнопка изменения
                        ui.button(
                            "Изменить", icon="edit", on_click=self._clear_selection
                        ).props("size=sm outlined color=primary")

    def _clear_selection(self):
        """Очистка выбранной должности"""
        self.selected_position = None
        self.has_selected_position = False
        self.can_generate = False

        if self.search_input:
            self.search_input.set_value("")

        self._clear_search_results()

    def _clear_search_results(self):
        """Очистка результатов поиска (заглушка - результаты убраны)"""
        self.current_query = ""
        self.search_results = []
        self.has_search_results = False
        # Скрываем spinner загрузки если он есть
        if hasattr(self, "search_loading") and self.search_loading:
            self.search_loading.style("display: none")

    def _show_no_results(self):
        """Отображение отсутствия результатов"""
        with self.search_results_container:
            with ui.card().classes("w-full text-center py-8"):
                with ui.card_section():
                    ui.icon("search_off", size="3rem").classes("text-gray-400 mb-4")
                    ui.label(
                        f"По запросу '{self.current_query}' ничего не найдено"
                    ).classes("text-lg text-gray-600 mb-2")
                    ui.label(
                        "Попробуйте изменить поисковый запрос или воспользуйтесь категориями"
                    ).classes("text-sm text-muted")

    def _show_search_error(self, error_message: str):
        """Отображение ошибки поиска"""
        with self.search_results_container:
            with ui.card().classes("bg-negative-1 border-l-4 border-negative p-4"):
                with ui.card_section():
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("error", size="1.5rem").classes("text-error")
                        ui.label("Ошибка поиска").classes("font-semibold text-error")
                    ui.label(error_message).classes("text-sm text-muted mt-2")

    async def _start_generation(self):
        """Запуск генерации профиля"""
        if not self.selected_position or self.is_generating:
            return

        try:
            self.is_generating = True
            self.generate_button.props(add="loading")

            # Подготовка данных для генерации
            generation_data = {
                "department": self.selected_position["department"],
                "position": self.selected_position["name"],
                "employee_name": (
                    self.employee_name_input.value.strip()
                    if self.employee_name_input.value
                    else None
                ),
                "temperature": self.temperature_slider.value,
                "save_result": True,
            }

            # Запуск генерации через API
            response = await self.api_client.start_profile_generation(**generation_data)

            if response.get("success"):
                self.current_task_id = response["task_id"]
                ui.notify(
                    "🚀 Генерация профиля запущена!", type="positive", position="top"
                )

                # Показываем прогресс
                await self._show_generation_progress()
            else:
                ui.notify("❌ Ошибка запуска генерации", type="negative")

        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            ui.notify(f"❌ Ошибка: {str(e)}", type="negative")
        finally:
            self.is_generating = False
            self.generate_button.props(remove="loading")

    async def _show_generation_progress(self):
        """Отображение прогресса генерации"""
        with ui.dialog() as dialog:
            with ui.card():
                with ui.card_section().classes("py-6 px-8"):

                    # Заголовок
                    with ui.row().classes("items-center gap-3 mb-4"):
                        ui.spinner(size="lg", color="primary")
                        with ui.column().classes("gap-1"):
                            ui.label("Генерация профиля должности").classes(
                                "text-lg font-semibold text-primary"
                            )
                            progress_status = ui.label(
                                "Инициализация процесса..."
                            ).classes("text-sm text-muted")

                    # Прогресс-бар
                    progress_bar = ui.linear_progress(value=0).classes("w-full mb-2")
                    progress_percentage = ui.label("0%").classes(
                        "text-xs text-muted text-right"
                    )

                    # Кнопка отмены
                    with ui.row().classes("justify-center mt-6"):
                        ui.button("Отменить", on_click=dialog.close).props(
                            "outlined color=grey"
                        )

        dialog.open()

        # Отслеживание прогресса
        await self._poll_generation_status(
            dialog, progress_status, progress_bar, progress_percentage
        )

    async def _poll_generation_status(
        self, dialog, status_label, progress_bar, progress_percentage
    ):
        """Опрос статуса генерации"""
        max_attempts = 60  # 5 минут максимум
        attempt = 0

        while (
            attempt < max_attempts and dialog.value
        ):  # Проверяем, что диалог не закрыт
            try:
                status_response = await self.api_client.get_generation_task_status(
                    self.current_task_id
                )

                if not status_response.get("success"):
                    break

                task_data = status_response["task"]
                status = task_data["status"]
                progress = task_data.get("progress", 0)
                current_step = task_data.get("current_step", "Обработка...")

                # Обновляем UI
                status_label.text = current_step
                progress_bar.value = progress / 100.0
                progress_percentage.text = f"{progress}%"

                if status == "completed":
                    dialog.close()
                    await self._show_generation_success()
                    break
                elif status == "failed":
                    dialog.close()
                    error_msg = task_data.get("error_message", "Неизвестная ошибка")
                    await self._show_generation_error(error_msg)
                    break
                elif status == "cancelled":
                    dialog.close()
                    ui.notify("Генерация отменена", type="warning")
                    break

                await asyncio.sleep(5)  # Проверяем каждые 5 секунд
                attempt += 1

            except Exception as e:
                logger.error(f"Error polling generation status: {e}")
                await asyncio.sleep(5)
                attempt += 1

        if attempt >= max_attempts:
            dialog.close()
            await self._show_generation_error("Превышено время ожидания")

    async def _show_generation_success(self):
        """Отображение успешного завершения"""
        with ui.dialog() as dialog:
            with ui.card().classes("text-center p-6"):
                with ui.card_section().classes("text-center py-8"):

                    # Иконка успеха
                    ui.icon("check_circle", size="4rem").classes("text-success mb-4")

                    # Заголовок
                    ui.label("🎉 Профиль успешно создан!").classes(
                        "text-2xl font-bold text-success mb-2"
                    )
                    ui.label("Профиль должности готов для использования").classes(
                        "text-muted mb-6"
                    )

                    # Действия
                    with ui.row().classes("gap-3 justify-center"):
                        ui.button(
                            "Просмотреть профиль",
                            icon="description",
                            on_click=lambda: self._view_profile(dialog),
                        ).props("color=primary")

                        ui.button(
                            "Создать еще один",
                            icon="add_circle_outline",
                            on_click=lambda: self._create_another(dialog),
                        ).props("outlined color=primary")

        dialog.open()
        ui.notify(
            "🎊 Профиль должности готов!",
            type="positive",
            position="center",
            timeout=5000,
        )

    async def _show_generation_error(self, error_message: str):
        """Отображение ошибки генерации"""
        with ui.dialog() as dialog:
            with ui.card().classes("bg-negative-1 border-l-4 border-negative p-4"):
                with ui.card_section().classes("py-6"):

                    # Заголовок ошибки
                    with ui.row().classes("items-center gap-3 mb-4"):
                        ui.icon("error", size="2rem").classes("text-error")
                        ui.label("❌ Ошибка генерации").classes(
                            "text-lg font-bold text-error"
                        )

                    # Сообщение об ошибке
                    ui.label(error_message).classes("text-sm text-muted mb-6")

                    # Действия
                    with ui.row().classes("gap-3"):
                        ui.button(
                            "Попробовать снова",
                            icon="refresh",
                            on_click=lambda: self._retry_generation(dialog),
                        ).props("color=red")

                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

        dialog.open()
        ui.notify(f"❌ {error_message}", type="negative", position="top")

    def _view_profile(self, dialog):
        """Просмотр сгенерированного профиля"""
        dialog.close()
        ui.navigate.to(f"/profiles/{self.current_task_id}")

    def _create_another(self, dialog):
        """Создание еще одного профиля"""
        dialog.close()
        self._reset_generator()

    def _retry_generation(self, dialog):
        """Повтор генерации"""
        dialog.close()
        asyncio.create_task(self._start_generation())

    def _reset_generator(self):
        """Сброс генератора"""
        self._clear_selection()
        self.current_task_id = None

        if self.employee_name_input:
            self.employee_name_input.value = ""
        if self.temperature_slider:
            self.temperature_slider.value = 0.1
        if self.profile_type_select:
            self.profile_type_select.value = "Полный профиль"

        self._update_temperature_description()
        ui.notify("🔄 Генератор сброшен", type="info")


if __name__ == "__main__":
    print("✅ A101 Professional Profile Generator created!")
    print("🎨 Features:")
    print("  - NiceGUI-compatible corporate design")
    print("  - Debounced search with category filters")
    print("  - Professional progress tracking")
    print("  - Responsive mobile-friendly layout")
    print("  - Real-time feedback and error handling")

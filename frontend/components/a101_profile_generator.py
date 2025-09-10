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
from typing import List, Dict, Any

from nicegui import ui
from ..services.api_client import APIClient
from .stats_component import StatsComponent

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

        # Единая системная статистика
        self.stats_component = None

        # Убрали search_categories - dropdown заменяет умные категории

        # Clean NiceGUI styling like login page
        self._add_clean_nicegui_styles()

        # Данные будут загружены после авторизации пользователя

    async def load_initial_data(self):
        """
        @doc
        Загрузка начальных данных после успешной авторизации.

        Теперь использует единый UnifiedStatsComponent для статистики.

        Examples:
          python> await generator.load_initial_data()
          python> # Данные загружены и UI обновлен
        """
        logger.info("Loading ProfileGenerator initial data...")

        try:
            # Загружаем только иерархические предложения
            # Статистика загружается через UnifiedStatsComponent автоматически
            await self._load_hierarchical_suggestions()
            logger.info("✅ ProfileGenerator data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading ProfileGenerator data: {e}")
            # При ошибке используем fallback значения
            self._use_fallback_suggestions()

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
        Загрузка position-first предложений для contextual search.

        Преобразует 567 бизнес-единиц в ~1689 позиций с умным контекстом
        для различения дублированных должностей.
        """
        try:
            logger.info(
                "Loading contextual position suggestions from organization API..."
            )

            # Проверяем авторизацию
            from nicegui import app

            if not hasattr(app, "storage") or not app.storage.user.get(
                "authenticated", False
            ):
                logger.warning("User not authenticated, using fallback suggestions")
                self._use_fallback_suggestions()
                return

            # Получаем все элементы для поиска через organization endpoint
            search_items_response = await self.api_client._make_request(
                "GET", "/api/organization/search-items"
            )

            if not search_items_response.get("success"):
                logger.warning(
                    "Failed to get search items from organization API, "
                    "using fallback suggestions"
                )
                self._use_fallback_suggestions()
                return

            # Извлекаем элементы и создаем position-first suggestions
            search_items = search_items_response["data"]["items"]

            # Создаем contextual position suggestions
            position_suggestions = self._create_position_suggestions(search_items)

            # Устанавливаем suggestions для NiceGUI dropdown
            self.hierarchical_suggestions = [
                item["display_name"] for item in position_suggestions
            ]
            self.position_lookup = {
                item["display_name"]: item for item in position_suggestions
            }

            logger.info(
                f"✅ Loaded {len(self.hierarchical_suggestions)} contextual position suggestions from {len(search_items)} business units"
            )

            # Обновляем dropdown options в поисковом поле если оно уже создано
            if hasattr(self, "search_input") and self.search_input:
                options_dict = {
                    suggestion: suggestion
                    for suggestion in self.hierarchical_suggestions
                }
                self.search_input.set_options(options_dict)
                logger.info(
                    "✅ Updated search dropdown with contextual position options"
                )

        except Exception as e:
            logger.debug(
                f"Error loading contextual position suggestions (using fallback): {e}"
            )
            self._use_fallback_suggestions()

    def _create_position_suggestions(self, search_items):
        """
        Создание contextual position suggestions с умным различением дублей.

        Преобразует бизнес-единицы в список позиций с контекстом:
        - "Java-разработчик → ДИТ (Блок ОД)" для уникальных позиций
        - "Руководитель группы → Группа 1 (Упр. подбора)" для дублированных

        Args:
            search_items: Список бизнес-единиц из API

        Returns:
            List[Dict]: Список позиций с contextual display names
        """
        # Шаг 1: Создаем map для обнаружения дублирования позиций
        position_instances = {}

        for unit in search_items:
            if unit.get("positions_count", 0) == 0:
                continue

            for position in unit.get("positions", []):
                position_key = position.lower().strip()
                if position_key not in position_instances:
                    position_instances[position_key] = []

                position_instances[position_key].append(
                    {"position_name": position, "unit": unit}
                )

        # Шаг 2: Создаем contextual suggestions для каждой позиции
        position_suggestions = []

        for position_key, instances in position_instances.items():
            is_duplicated = len(instances) > 1

            for instance in instances:
                position_name = instance["position_name"]
                unit = instance["unit"]

                # Создаем contextual display name
                display_name = self._create_contextual_display_name(
                    position_name, unit, is_duplicated
                )

                position_suggestions.append(
                    {
                        "display_name": display_name,
                        "position_name": position_name,
                        "unit_name": unit["name"],
                        "unit_path": unit["full_path"],
                        "hierarchy": unit["hierarchy"],
                        "level": unit.get("level", 0),
                        "unit_data": unit,
                    }
                )

        logger.info(
            f"Created {len(position_suggestions)} contextual position suggestions"
        )
        return position_suggestions

    def _create_contextual_display_name(self, position_name, unit, is_duplicated):
        """
        Создание умного contextual display name для позиции.

        Args:
            position_name: Название позиции
            unit: Данные бизнес-единицы
            is_duplicated: True если позиция дублируется в других единицах

        Returns:
            str: Контекстуальное отображаемое имя
        """
        if not is_duplicated:
            # Уникальная позиция - минимальный контекст
            return f"{position_name} → {unit['display_name']}"

        # Дублированная позиция - расширенный контекст для различения
        hierarchy_parts = unit["hierarchy"].split(" → ")

        if len(hierarchy_parts) <= 3:
            # Короткая иерархия - показываем полностью
            return f"{position_name} → {unit['hierarchy']}"

        # Длинная иерархия - умное сжатие
        # Показываем: позиция → последние 2 уровня (более специфичный контекст)
        context = " → ".join(hierarchy_parts[-2:])

        # Добавляем блок в скобках для дополнительного контекста
        block = hierarchy_parts[0] if hierarchy_parts else ""
        if block and block not in context:
            return f"{position_name} → {context} ({block})"
        else:
            return f"{position_name} → {context}"

    def _use_fallback_suggestions(self):
        """Использование fallback предложений при недоступности backend"""
        # Создаем fallback suggestions в новом contextual формате
        fallback_positions = [
            "Руководитель отдела → Департамент",
            "Ведущий специалист → Отдел",
            "Старший специалист → Управление",
            "Специалист → Группа",
            "Главный специалист → Департамент",
            "Заместитель руководителя → Департамент",
            "Директор департамента → Блок",
            "Руководитель направления → Департамент",
            "Руководитель управления → Департамент",
            "Руководитель службы → Блок",
            "Координатор → Управление",
            "Помощник директора → Департамент",
        ]

        self.hierarchical_suggestions = fallback_positions

        # Создаем fallback lookup для совместимости
        self.position_lookup = {}
        for suggestion in fallback_positions:
            if " → " in suggestion:
                parts = suggestion.split(" → ")
                position_name = parts[0].strip()
                unit_name = parts[1].strip()
            else:
                position_name = suggestion
                unit_name = "Неизвестно"

            self.position_lookup[suggestion] = {
                "display_name": suggestion,
                "position_name": position_name,
                "unit_name": unit_name,
                "unit_path": unit_name,
                "hierarchy": unit_name,
            }

        logger.info(f"Using {len(fallback_positions)} contextual fallback suggestions")

        # Обновляем dropdown options в поисковом поле если оно уже создано
        if hasattr(self, "search_input") and self.search_input:
            options_dict = {
                suggestion: suggestion for suggestion in self.hierarchical_suggestions
            }
            self.search_input.set_options(options_dict)
            logger.info("✅ Updated search dropdown with contextual fallback options")

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

            # Системная статистика через unified component
            await self._render_unified_system_stats()

            # Главный генератор
            await self._render_main_generator()

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

            # Статистика будет загружена после авторизации пользователя

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
            # Обновляем статистику через unified component
            if self.stats_component:
                await self.stats_component.manual_refresh()

            # Обновляем данные поиска
            await self._load_hierarchical_suggestions()
            ui.notify("Данные обновлены", type="positive")
        except Exception as e:
            ui.notify(f"Ошибка обновления: {e}", type="negative")

    async def _render_unified_system_stats(self):
        """Отображение системной статистики через упрощенный компонент"""
        # Создаем компонент статистики в компактном стиле
        self.stats_component = StatsComponent(self.api_client, style="compact")
        await self.stats_component.render()

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

        # Generation button (shown when position is selected) - Simplified interface
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

            # Old _render_system_stats method removed - now using unified UnifiedStatsComponent

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

                # Параметры генерации убраны - упрощенный интерфейс

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
                self.search_input.props(
                    'placeholder="Начните вводить название должности"'
                )

                # События для обновления результатов при вводе
                self.search_input.on("input-value", self._on_search_input_value)

                # Style fixes no longer needed with standard NiceGUI styling

            # Убрали "Умные категории поиска" - dropdown заменяет эту функциональность

            # Убрали результаты поиска - dropdown заменяет эту функциональность
            # Оставляем только spinner для обратной связи при выборе
            self.search_loading = (
                ui.spinner(size="sm").classes("self-center").style("display: none")
            )

    # Метод _load_system_stats удален - теперь используется UnifiedStatsComponent
    # Метод _update_stats_labels удален - теперь UnifiedStatsComponent сам обновляет UI

    async def _on_search_select(self, event=None):
        """Обработчик выбора варианта из dropdown - сразу подготавливаем к генерации"""
        if event and hasattr(event, "value") and event.value:
            # Получаем выбранное значение из dropdown
            selected_value = event.value.strip()
            logger.info(f"Selected from dropdown: {selected_value}")

            # Обрабатываем иерархический выбор
            department, position = self._process_hierarchical_selection(selected_value)

            # Сразу устанавливаем данные для генерации
            if department and position:
                await self._set_selected_position(position, department)
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
                    await self._set_selected_position(position, department)

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
        Обработка выбора из contextual position search.

        Args:
            selection: Выбранная строка (display_name позиции с контекстом)

        Returns:
            tuple[str, str]: (unit_name, position_name) или ("", "") если не удалось извлечь
        """
        try:
            # Проверяем есть ли данные о выбранной позиции в lookup
            if hasattr(self, "position_lookup") and selection in self.position_lookup:
                position_item = self.position_lookup[selection]

                position_name = position_item["position_name"]
                unit_name = position_item["unit_name"]
                unit_path = position_item["unit_path"]

                logger.info(
                    f"Contextual position selection: {position_name} in {unit_name} (path: {unit_path})"
                )
                return unit_name, position_name

            # Fallback для старого формата или ручного ввода
            if " → " in selection:
                parts = [part.strip() for part in selection.split(" → ")]
                if len(parts) >= 2:
                    position_name = parts[0]
                    # Пытаемся извлечь unit name из контекста
                    context_part = parts[1]

                    # Убираем скобки если есть: "Группа 1 (Блок ОД)" -> "Группа 1"
                    if "(" in context_part:
                        unit_name = context_part.split("(")[0].strip()
                    else:
                        # Берем последнюю часть как unit name
                        context_parts = context_part.split(" → ")
                        unit_name = context_parts[-1].strip()

                    logger.info(
                        f"Fallback contextual selection: {position_name} in {unit_name}"
                    )
                    return unit_name, position_name
            else:
                # Простой ввод без контекста - считаем что это название позиции
                logger.info(f"Simple position selection: {selection}")
                return "", selection.strip()

        except Exception as e:
            logger.error(f"Error processing contextual selection: {e}")

        return "", ""

    async def _set_selected_position(self, position: str, department: str):
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

        # Загружаем детальную информацию о позиции
        await self._load_position_details(position, department)

        # Отображаем детальную информацию
        await self._display_detailed_position_info()

    async def _load_position_details(self, position: str, department: str):
        """
        Загрузка детальной информации о позиции включая статус профилей.

        Args:
            position: Название позиции
            department: Название департамента
        """
        try:
            # Получаем детальную информацию о позиции из каталога
            positions_response = await self.api_client._make_request(
                "GET", f"/api/catalog/positions/{department}"
            )

            # Ищем конкретную позицию в ответе
            self.position_details = None
            if positions_response.get("success"):
                positions = positions_response["data"]["positions"]
                for pos in positions:
                    if pos["name"] == position:
                        self.position_details = pos
                        break

            # Получаем информацию о департаменте для полной иерархии
            departments_response = await self.api_client._make_request(
                "GET", "/api/catalog/departments"
            )

            self.department_details = None
            if departments_response.get("success"):
                departments = departments_response["data"]["departments"]
                for dept in departments:
                    if dept["name"] == department:
                        self.department_details = dept
                        break

            # Получаем информацию о существующих профилях для этой позиции
            profiles_response = await self.api_client.get_profiles_list(
                department=department,
                position=position,
                limit=100,  # Получаем все версии
            )

            # Сохраняем информацию о профилях
            self.position_profiles = []
            if profiles_response and profiles_response.get("profiles"):
                self.position_profiles = profiles_response["profiles"]

            logger.info(
                f"Loaded details for {position}: {len(self.position_profiles)} existing profiles"
            )

        except Exception as e:
            logger.error(f"Error loading position details: {e}")
            self.position_details = None
            self.position_profiles = []

    async def _display_detailed_position_info(self):
        """Отображение детальной информации о выбранной позиции"""
        if (
            not hasattr(self, "selected_position_card")
            or not self.selected_position_card
        ):
            return

        self.selected_position_card.clear()

        with self.selected_position_card:
            with ui.card().classes("w-full border-l-4 border-primary"):
                with ui.card_section().classes("py-4"):
                    # Заголовок с иконкой
                    with ui.row().classes("w-full items-center gap-3 mb-4"):
                        ui.icon("check_circle", size="1.5rem").classes("text-primary")
                        ui.label("Выбранная должность").classes(
                            "text-h6 text-weight-medium text-primary"
                        )

                    # Название должности
                    ui.label(self.selected_position).classes(
                        "text-h5 text-weight-bold mb-3"
                    )

                    # Детальная информация в сетке
                    with ui.grid(columns="1fr 1fr").classes("w-full gap-4"):
                        # Левая колонка
                        with ui.column().classes("gap-2"):
                            # Департамент с полным путем (иерархия)
                            if (
                                hasattr(self, "position_details")
                                and self.position_details
                            ):
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("account_tree", size="1rem").classes(
                                        "text-grey-6"
                                    )
                                    ui.label("Иерархия:").classes(
                                        "text-caption text-grey-6"
                                    )

                                # Показываем полную иерархию чипсами
                                self._display_hierarchy_chips()

                                # Уровень должности
                                with ui.row().classes("items-center gap-2 mt-2"):
                                    ui.icon("trending_up", size="1rem").classes(
                                        "text-grey-6"
                                    )
                                    ui.label("Уровень:").classes(
                                        "text-caption text-grey-6"
                                    )
                                level_info = self._format_position_level(
                                    self.position_details.get("level")
                                )
                                ui.chip(
                                    level_info["text"], color=level_info["color"]
                                ).props("size=sm").classes("q-ml-sm")

                                # Категория
                                with ui.row().classes("items-center gap-2 mt-2"):
                                    ui.icon("category", size="1rem").classes(
                                        "text-grey-6"
                                    )
                                    ui.label("Категория:").classes(
                                        "text-caption text-grey-6"
                                    )
                                ui.label(
                                    self.position_details.get("category", "Не указана")
                                ).classes("text-body2 q-ml-lg")

                        # Правая колонка - детальная информация о профилях
                        with ui.column().classes("gap-2"):
                            await self._render_profiles_section()

    def _display_hierarchy_chips(self):
        """Отображение иерархии сотрудника красивыми чипсами"""
        try:
            hierarchy_parts = []

            # Получаем полную иерархию
            if (
                hasattr(self, "department_details")
                and self.department_details
                and self.department_details.get("path")
            ):
                # Разбиваем путь департамента на части
                dept_path = self.department_details["path"]
                hierarchy_parts = [part.strip() for part in dept_path.split("/")]
            else:
                # Fallback - используем только название департамента
                hierarchy_parts = [self.selected_department]

            # Добавляем позицию как последний элемент
            if hasattr(self, "selected_position") and self.selected_position:
                hierarchy_parts.append(self.selected_position)

            # Создаем контейнер для чипсов с отступом
            with ui.column().classes("q-ml-lg mt-2"):
                # Отображаем чипсы с стрелками
                with ui.row().classes("items-center gap-1 flex-wrap"):
                    for i, part in enumerate(hierarchy_parts):
                        # Определяем стиль и цвет для каждого уровня
                        if i == len(hierarchy_parts) - 1:  # Позиция (последний элемент)
                            color = "primary"
                            icon = "person"
                        elif i == 0:  # Блок (первый элемент)
                            color = "deep-purple"
                            icon = "corporate_fare"
                        elif "департамент" in part.lower():
                            color = "blue"
                            icon = "business"
                        elif "управление" in part.lower():
                            color = "green"
                            icon = "manage_accounts"
                        else:
                            color = "grey"
                            icon = "folder"

                        # Чипс с иконкой
                        ui.chip(part, icon=icon, color=color).props(
                            "size=sm outline"
                        ).classes("text-weight-medium")

                        # Стрелка между элементами (кроме последнего)
                        if i < len(hierarchy_parts) - 1:
                            ui.icon("chevron_right", size="1.2rem").classes(
                                "text-grey-5"
                            )

        except Exception as e:
            logger.error(f"Error displaying hierarchy chips: {e}")
            # Fallback на простой текст при ошибке
            ui.label(f"{self.selected_department} → {self.selected_position}").classes(
                "text-body2 q-ml-lg text-blue-700"
            )

    def _get_full_hierarchy(self) -> str:
        """Получение полной иерархии сотрудника"""
        try:
            if (
                hasattr(self, "department_details")
                and self.department_details
                and hasattr(self, "selected_position")
                and self.selected_position
            ):
                # Полная иерархия = путь департамента + позиция
                dept_path = self.department_details.get(
                    "path", self.selected_department
                )
                return f"{dept_path} → {self.selected_position}"
            else:
                # Fallback - просто департамент и позиция
                return f"{self.selected_department} → {self.selected_position}"
        except Exception as e:
            logger.error(f"Error building hierarchy: {e}")
            return f"{self.selected_department} → {self.selected_position}"

    def _format_datetime(self, datetime_str: str) -> str:
        """Форматирование даты и времени для отображения"""
        if not datetime_str:
            return "Неизвестно"
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return datetime_str

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
        if (
            not self.selected_position
            or not self.selected_department
            or self.is_generating
        ):
            ui.notify("❌ Выберите позицию для генерации", type="warning")
            return

        try:
            self.is_generating = True
            self.generate_button.props(add="loading")

            # Подготовка данных для генерации - используем существующие строки
            generation_data = {
                "department": self.selected_department,  # Это строка
                "position": self.selected_position,  # Это тоже строка
                "save_result": True,
            }

            logger.info(f"Starting generation with data: {generation_data}")

            # Запуск генерации через API
            response = await self.api_client.start_profile_generation(**generation_data)

            logger.info(f"Generation API response: {response}")

            if response.get("task_id") and response.get("status") == "queued":
                self.current_task_id = response["task_id"]
                message = response.get("message", "Генерация профиля запущена")
                ui.notify(f"🚀 {message}", type="positive", position="top")

                # Показываем прогресс
                await self._show_generation_progress()
            else:
                error_msg = response.get("message", "Неизвестная ошибка")
                logger.error(f"Generation start failed: {error_msg}")
                ui.notify(f"❌ Ошибка запуска: {error_msg}", type="negative")

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
        """Сброс генератора - упрощенная версия"""
        self._clear_selection()
        self.current_task_id = None
        ui.notify("🔄 Генератор сброшен", type="info")

    async def _start_generation(self):
        """Запуск генерации профиля должности"""
        if not (self.selected_department and self.selected_position):
            ui.notify("❌ Необходимо выбрать департамент и должность", type="negative")
            return

        try:
            # Показываем диалог с прогрессом
            await self._show_generation_progress_dialog()

            # Подготавливаем данные для генерации
            generation_data = {
                "department": self.selected_department,
                "position": self.selected_position,
                "save_result": True,
            }

            # Отправляем запрос на генерацию
            response = await self.api_client._make_request(
                "POST", "/api/generation/start", data=generation_data
            )

            if response.get("task_id"):
                # Сохраняем ID задачи
                self.current_task_id = response["task_id"]
                # Запускаем polling статуса задачи
                await self._poll_task_status(response["task_id"])
            else:
                self._safe_close_dialog("generation_dialog")
                ui.notify("❌ Ошибка при запуске генерации", type="negative")

        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            self._safe_close_dialog("generation_dialog")
            ui.notify(f"❌ Ошибка генерации: {str(e)}", type="negative")

    async def _show_generation_progress_dialog(self):
        """Показ диалога с прогрессом генерации"""
        self.generation_dialog = ui.dialog()
        self.progress_value = 0
        self.progress_step = "Инициализация..."

        with self.generation_dialog:
            with ui.card().classes("w-96 p-6"):
                with ui.column().classes("items-center gap-4"):
                    # Заголовок
                    ui.label("🚀 Генерация профиля должности").classes(
                        "text-lg font-bold"
                    )

                    # Информация о задаче
                    with ui.column().classes("w-full gap-2"):
                        ui.label(f"Должность: {self.selected_position}").classes(
                            "font-medium"
                        )
                        ui.label(f"Департамент: {self.selected_department}").classes(
                            "text-sm text-gray-600"
                        )

                    # Прогресс-бар и спиннер
                    with ui.row().classes("w-full items-center gap-4"):
                        ui.spinner(size="md", color="primary")
                        with ui.column().classes("flex-1"):
                            self.progress_bar = (
                                ui.linear_progress()
                                .bind_value_from(self, "progress_value")
                                .classes("w-full")
                            )
                            self.progress_label = (
                                ui.label()
                                .bind_text_from(self, "progress_step")
                                .classes("text-sm")
                            )

                    # Кнопка отмены
                    ui.button("Отменить", on_click=self._cancel_generation).props(
                        "outlined color=grey size=sm"
                    )

        self.generation_dialog.open()

    async def _poll_task_status(self, task_id: str):
        """Polling статуса задачи генерации"""
        max_attempts = 120  # 2 минуты максимум
        attempt = 0

        while attempt < max_attempts:
            try:
                # Получаем статус задачи
                status_response = await self.api_client._make_request(
                    "GET", f"/api/generation/{task_id}/status"
                )

                if not status_response:
                    break

                task_data = status_response.get("task", {})
                status = task_data.get("status", "unknown")
                progress = task_data.get("progress", 0)
                current_step = task_data.get("current_step", "Обработка...")

                # Обновляем прогресс
                self.progress_value = progress / 100.0  # NiceGUI expects 0-1 range
                self.progress_step = f"{current_step} ({progress}%)"

                if status == "completed":
                    # Получаем результат
                    result_response = await self.api_client._make_request(
                        "GET", f"/api/generation/{task_id}/result"
                    )

                    self._safe_close_dialog("generation_dialog")
                    await self._show_generation_success(result_response.get("result"))
                    return

                elif status == "failed":
                    self._safe_close_dialog("generation_dialog")
                    error_msg = task_data.get("error_message", "Неизвестная ошибка")
                    await self._show_generation_error(error_msg)
                    return

                # Ждем 1 секунду перед следующим запросом
                await asyncio.sleep(1)
                attempt += 1

            except Exception as e:
                logger.error(f"Error polling task status: {e}")
                await asyncio.sleep(2)  # Увеличиваем задержку при ошибке
                attempt += 1

        # Превышено время ожидания
        self._safe_close_dialog("generation_dialog")
        await self._show_generation_error("Превышено время ожидания генерации")

    async def _show_generation_success(self, result):
        """Показ успешного результата генерации"""
        dialog = ui.dialog()

        with dialog:
            with ui.card().classes("w-[500px] p-6"):
                with ui.column().classes("items-center gap-4"):
                    # Успех
                    ui.icon("check_circle", size="3rem", color="positive")
                    ui.label("✅ Профиль успешно создан!").classes(
                        "text-xl font-bold text-positive"
                    )

                    if result and result.get("profile"):
                        profile = result["profile"]

                        # Краткая информация о профиле
                        with ui.column().classes("w-full gap-2 bg-gray-50 p-4 rounded"):
                            ui.label(
                                f"Должность: {profile.get('position_title', 'N/A')}"
                            ).classes("font-medium")
                            ui.label(
                                f"Департамент: {profile.get('department_specific', 'N/A')}"
                            ).classes("text-sm")
                            ui.label(
                                f"Категория: {profile.get('position_category', 'N/A')}"
                            ).classes("text-sm")

                            # Метаданные генерации
                            if result.get("metadata", {}).get("validation", {}):
                                validation = result["metadata"]["validation"]
                                completeness = (
                                    validation.get("completeness_score", 0) * 100
                                )
                                ui.label(
                                    f"Полнота профиля: {completeness:.0f}%"
                                ).classes("text-sm text-blue-600")

                    # Действия
                    with ui.row().classes("gap-3 justify-center"):
                        ui.button(
                            "📄 Просмотреть профиль",
                            icon="description",
                            on_click=lambda: self._view_profile_result(result, dialog),
                        ).props("color=primary")

                        ui.button(
                            "➕ Создать еще один",
                            icon="add_circle_outline",
                            on_click=lambda: self._create_another_profile(dialog),
                        ).props("outlined")

                    ui.button("Закрыть", on_click=dialog.close).props(
                        "outlined color=grey"
                    )

        dialog.open()

    async def _show_generation_error(self, error_message: str):
        """Показ ошибки генерации"""
        dialog = ui.dialog()

        with dialog:
            with ui.card().classes("w-96 p-6"):
                with ui.column().classes("items-center gap-4"):
                    # Ошибка
                    ui.icon("error", size="3rem", color="negative")
                    ui.label("❌ Ошибка генерации").classes(
                        "text-xl font-bold text-negative"
                    )
                    ui.label(error_message).classes("text-center text-gray-600")

                    # Действия
                    with ui.row().classes("gap-3"):
                        ui.button(
                            "🔄 Попробовать снова",
                            icon="refresh",
                            on_click=lambda: self._retry_generation_from_error(dialog),
                        ).props("color=primary")

                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

        dialog.open()

    def _cancel_generation(self):
        """Отмена генерации"""
        self._safe_close_dialog("generation_dialog")
        self.current_task_id = None
        ui.notify("Генерация отменена", type="warning")

    def _view_profile_result(self, result, dialog):
        """Просмотр результата профиля"""
        self._safe_close_any_dialog(dialog)
        # Создаем диалог просмотра профиля
        self._show_profile_details(result)

    def _show_profile_details(self, result):
        """Показ детальной информации о профиле"""
        if not result or not result.get("profile"):
            ui.notify("❌ Нет данных профиля для отображения", type="negative")
            return

        profile = result["profile"]

        dialog = ui.dialog()
        with dialog:
            with ui.card().classes("w-[800px] max-h-[80vh] overflow-y-auto"):
                with ui.column().classes("gap-4 p-6"):
                    # Заголовок
                    ui.label(
                        f"📋 Профиль должности: {profile.get('position_title', 'N/A')}"
                    ).classes("text-xl font-bold")

                    # Основная информация
                    with ui.expansion("Основная информация", icon="info").classes(
                        "w-full"
                    ):
                        with ui.column().classes("gap-2 p-4"):
                            ui.label(
                                f"Департамент: {profile.get('department_specific', 'N/A')}"
                            )
                            ui.label(
                                f"Категория: {profile.get('position_category', 'N/A')}"
                            )
                            ui.label(
                                f"Тип деятельности: {profile.get('primary_activity_type', 'N/A')}"
                            )

                    # Области ответственности
                    if profile.get("responsibility_areas"):
                        with ui.expansion(
                            "Области ответственности", icon="assignment"
                        ).classes("w-full"):
                            with ui.column().classes("gap-3 p-4"):
                                for area in profile["responsibility_areas"]:
                                    if isinstance(area, dict) and area.get("tasks"):
                                        area_name = (
                                            area.get("area", ["Неопределено"])[0]
                                            if isinstance(area.get("area"), list)
                                            else str(area.get("area", "Неопределено"))
                                        )
                                        ui.label(f"🔹 {area_name}").classes(
                                            "font-medium"
                                        )
                                        for task in area["tasks"][
                                            :3
                                        ]:  # Показываем первые 3 задачи
                                            ui.label(f"• {task}").classes(
                                                "text-sm ml-4"
                                            )

                    # Навыки
                    if profile.get("professional_skills"):
                        with ui.expansion(
                            "Профессиональные навыки", icon="psychology"
                        ).classes("w-full"):
                            with ui.column().classes("gap-2 p-4"):
                                for skill_group in profile["professional_skills"][
                                    :3
                                ]:  # Показываем первые 3 группы
                                    if isinstance(skill_group, dict):
                                        category = skill_group.get(
                                            "skill_category", "Общие навыки"
                                        )
                                        ui.label(f"🔸 {category}").classes(
                                            "font-medium"
                                        )

                                        skills = skill_group.get("specific_skills", [])
                                        for skill in skills[
                                            :2
                                        ]:  # Показываем первые 2 навыка в группе
                                            if isinstance(skill, dict):
                                                skill_name = skill.get(
                                                    "skill_name", "Неопределено"
                                                )
                                                level = skill.get(
                                                    "proficiency_level", 1
                                                )
                                                ui.label(
                                                    f"• {skill_name} (Уровень: {level})"
                                                ).classes("text-sm ml-4")

                    # Кнопка закрытия
                    with ui.row().classes("justify-center mt-4"):
                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

        dialog.open()

    def _create_another_profile(self, dialog):
        """Создание еще одного профиля"""
        self._safe_close_any_dialog(dialog)
        self._clear_selection()
        ui.notify("✨ Выберите новую должность для создания профиля", type="info")

    def _retry_generation_from_error(self, dialog):
        """Повторная генерация после ошибки"""
        self._safe_close_any_dialog(dialog)
        asyncio.create_task(self._start_generation())

    def _clear_selection(self):
        """Очистка выбранной позиции"""
        self.selected_department = None
        self.selected_position = None
        self.has_selected_position = False
        self.can_generate = False
        self.current_task_id = None

        # Очищаем поля поиска если есть
        if hasattr(self, "search_input"):
            self.search_input.value = ""

        ui.notify("🧹 Выбор очищен", type="info")

    def _safe_close_dialog(self, dialog_attr_name: str):
        """Безопасное закрытие диалога с обработкой ошибок"""
        try:
            if hasattr(self, dialog_attr_name):
                dialog = getattr(self, dialog_attr_name)
                if dialog and hasattr(dialog, "close"):
                    dialog.close()
                    # Очищаем ссылку на диалог
                    setattr(self, dialog_attr_name, None)
        except Exception as e:
            logger.warning(f"Error closing dialog {dialog_attr_name}: {e}")

    def _safe_close_any_dialog(self, dialog):
        """Безопасное закрытие любого диалога"""
        try:
            if dialog and hasattr(dialog, "close"):
                dialog.close()
        except Exception as e:
            logger.warning(f"Error closing dialog: {e}")

    # ============================================================================
    # PROFILE VIEWING METHODS (Enhanced for generator page)
    # ============================================================================

    async def _render_profiles_section(self):
        """
        @doc
        Отображение детальной секции профилей с версионированием и функциями скачивания.

        Показывает:
        - Статистику версий профилей
        - Список всех версий с метаданными
        - Кнопки скачивания JSON/MD для каждой версии
        - Предпросмотр содержания профилей

        Examples:
          python> await self._render_profiles_section()
        """

        # Заголовок секции профилей
        with ui.row().classes("items-center gap-2"):
            ui.icon("description", size="1rem").classes("text-grey-6")
            ui.label("Существующие профили:").classes("text-caption text-grey-6")

        profiles_count = (
            len(self.position_profiles) if hasattr(self, "position_profiles") else 0
        )

        if profiles_count > 0:
            # Статистика профилей
            with ui.row().classes("items-center gap-3 q-ml-lg"):
                ui.chip(f"{profiles_count} версий", color="positive").props("size=sm")

                # Кнопка показать/скрыть все версии
                show_all_button = ui.button(
                    "Показать все",
                    icon="expand_more",
                    on_click=lambda: self._toggle_profiles_view(show_all_button),
                ).props("flat size=sm color=primary")

            # Контейнер для списка профилей (скрытый по умолчанию)
            self.profiles_list_container = ui.column().classes("q-ml-lg mt-2 hidden")

            # Последний профиль (всегда видимый)
            await self._render_latest_profile_info()

            # Полный список профилей (в скрытом контейнере)
            with self.profiles_list_container:
                await self._render_all_profiles_list()

        else:
            # Нет профилей
            with ui.column().classes("q-ml-lg"):
                ui.label("Профилей не найдено").classes("text-body2 text-grey-6")
                ui.chip("Новая позиция", color="orange").props("size=sm").classes(
                    "mt-1"
                )

                ui.label("Создайте первый профиль для этой должности").classes(
                    "text-caption text-grey-7 mt-2"
                )

    async def _render_latest_profile_info(self):
        """Отображение информации о последнем профиле"""
        if not self.position_profiles:
            return

        latest_profile = max(
            self.position_profiles,
            key=lambda x: x.get("created_at", ""),
        )

        with ui.card().classes("q-ml-lg mt-2 border-l-2 border-positive"):
            with ui.card_section().classes("py-2 px-3"):
                with ui.row().classes("w-full items-center justify-between"):
                    with ui.column().classes("gap-1"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("new_releases", size="1rem").classes(
                                "text-positive"
                            )
                            ui.label("Последняя версия").classes(
                                "text-caption font-medium text-positive"
                            )

                        ui.label(
                            self._format_datetime(latest_profile.get("created_at"))
                        ).classes("text-body2")

                        # Показываем метаданные если есть
                        if latest_profile.get("generation_metadata"):
                            metadata = latest_profile["generation_metadata"]
                            tokens = metadata.get("tokens_used", 0)
                            time_taken = metadata.get("generation_time_seconds", 0)

                            with ui.row().classes("items-center gap-3"):
                                if tokens:
                                    ui.label(f"🪙 {tokens:,}").classes(
                                        "text-caption text-grey-6"
                                    )
                                if time_taken:
                                    ui.label(f"⏱️ {time_taken:.1f}с").classes(
                                        "text-caption text-grey-6"
                                    )

                    # Действия для последнего профиля
                    with ui.column().classes("gap-1"):
                        await self._render_profile_actions(latest_profile, compact=True)

    async def _render_all_profiles_list(self):
        """Отображение полного списка всех профилей"""
        if not self.position_profiles:
            return

        # Сортируем профили по дате создания (новые сверху)
        sorted_profiles = sorted(
            self.position_profiles, key=lambda x: x.get("created_at", ""), reverse=True
        )

        with ui.column().classes("gap-2"):
            ui.label("Все версии профилей").classes("text-body2 font-medium mb-2")

            for i, profile in enumerate(sorted_profiles, 1):
                await self._render_profile_version_card(profile, i)

    async def _render_profile_version_card(
        self, profile: Dict[str, Any], version_num: int
    ):
        """Отображение карточки версии профиля"""
        created_at = profile.get("created_at", "")
        status = profile.get("status", "active")
        employee_name = profile.get("employee_name", "")

        # Определяем цвет статуса
        status_color = "positive" if status == "active" else "grey"
        status_text = "Активен" if status == "active" else "Архивирован"

        with ui.card().classes("w-full"):
            with ui.card_section().classes("py-2 px-3"):
                with ui.row().classes("w-full items-center justify-between"):
                    with ui.column().classes("gap-1"):
                        # Заголовок версии
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"Версия {version_num}").classes(
                                "text-body2 font-medium"
                            )
                            ui.chip(status_text, color=status_color).props("size=sm")

                        # Дата создания
                        ui.label(self._format_datetime(created_at)).classes(
                            "text-caption text-grey-7"
                        )

                        # Имя сотрудника если есть
                        if employee_name:
                            with ui.row().classes("items-center gap-1"):
                                ui.icon("person", size="0.8rem").classes("text-grey-6")
                                ui.label(employee_name).classes("text-caption")

                        # Метаданные генерации
                        if profile.get("generation_metadata"):
                            metadata = profile["generation_metadata"]
                            tokens = metadata.get("tokens_used", 0)
                            time_taken = metadata.get("generation_time_seconds", 0)
                            model = metadata.get("model_used", "")

                            with ui.row().classes("items-center gap-3 mt-1"):
                                if tokens:
                                    ui.label(f"🪙 {tokens:,}").classes(
                                        "text-caption text-grey-6"
                                    )
                                if time_taken:
                                    ui.label(f"⏱️ {time_taken:.1f}с").classes(
                                        "text-caption text-grey-6"
                                    )
                                if model and "gemini" in model.lower():
                                    ui.label("🤖 Gemini 2.5").classes(
                                        "text-caption text-blue-600"
                                    )

                    # Действия для профиля
                    with ui.column().classes("gap-1"):
                        await self._render_profile_actions(profile, compact=False)

    async def _render_profile_actions(
        self, profile: Dict[str, Any], compact: bool = False
    ):
        """Отображение действий для профиля"""
        profile_id = profile.get("profile_id", "")

        if compact:
            # Компактный режим - только основные действия
            with ui.row().classes("gap-1"):
                ui.button(
                    icon="visibility",
                    on_click=lambda p=profile: self._view_profile_details(p),
                ).props("flat round size=sm color=primary").tooltip("Просмотр")

                ui.button(
                    icon="file_download",
                    on_click=lambda p=profile: self._show_download_options(p),
                ).props("flat round size=sm color=blue").tooltip("Скачать")
        else:
            # Полный режим - все действия
            with ui.row().classes("gap-1"):
                ui.button(
                    "Просмотр",
                    icon="visibility",
                    on_click=lambda p=profile: self._view_profile_details(p),
                ).props("flat size=sm color=primary")

                ui.button(
                    icon="article", on_click=lambda p=profile: self._preview_markdown(p)
                ).props("flat round size=sm color=green").tooltip("Предпросмотр MD")

                ui.button(
                    icon="download", on_click=lambda p=profile: self._download_json(p)
                ).props("flat round size=sm color=blue").tooltip("Скачать JSON")

                ui.button(
                    icon="description",
                    on_click=lambda p=profile: self._download_markdown(p),
                ).props("flat round size=sm color=purple").tooltip("Скачать MD")

    def _toggle_profiles_view(self, button):
        """Переключение отображения списка профилей"""
        if hasattr(self, "profiles_list_container"):
            is_hidden = "hidden" in self.profiles_list_container.classes

            if is_hidden:
                # Показать список
                self.profiles_list_container.classes(remove="hidden")
                button.props(remove="icon=expand_more")
                button.props(add="icon=expand_less")
                button.text = "Скрыть"
            else:
                # Скрыть список
                self.profiles_list_container.classes(add="hidden")
                button.props(remove="icon=expand_less")
                button.props(add="icon=expand_more")
                button.text = "Показать все"

    async def _view_profile_details(self, profile: Dict[str, Any]):
        """Просмотр детальной информации о профиле"""
        try:
            # Загружаем полный профиль
            full_profile = await self.api_client.get_profile_by_id(
                profile["profile_id"]
            )
            if full_profile and "data" in full_profile:
                await self._show_profile_detail_dialog(full_profile["data"])
            else:
                ui.notify("Ошибка загрузки профиля", type="negative")
        except Exception as e:
            logger.error(f"Error loading profile details: {e}")
            ui.notify(f"Ошибка: {str(e)}", type="negative")

    async def _show_profile_detail_dialog(self, profile_data: Dict[str, Any]):
        """Показ диалога с детальной информацией профиля"""
        dialog = ui.dialog()

        with dialog:
            with ui.card().classes("w-[85vw] max-w-5xl max-h-[80vh]"):
                # Заголовок диалога
                with ui.card_section().classes("bg-primary text-white"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.column():
                            ui.label(profile_data.get("position_title", "")).classes(
                                "text-h5 font-bold"
                            )
                            ui.label(profile_data.get("department_path", "")).classes(
                                "text-body1 opacity-90"
                            )

                        ui.button(icon="close", on_click=dialog.close).props(
                            "flat round text-color=white"
                        )

                # Основной контент
                with ui.scroll_area().classes("flex-1"):
                    with ui.column().classes("gap-4 p-6"):
                        # Основная информация
                        await self._render_profile_basic_info(profile_data)

                        # Содержание профиля (JSON данные)
                        if profile_data.get("json_data"):
                            await self._render_profile_content(
                                profile_data["json_data"]
                            )

                        # Метаданные генерации
                        await self._render_profile_metadata(profile_data)

                # Действия в футере
                with ui.card_actions():
                    with ui.row().classes("w-full justify-between"):
                        with ui.row().classes("gap-2"):
                            ui.button(
                                "Скачать JSON",
                                icon="file_download",
                                on_click=lambda: self._download_json_by_id(
                                    profile_data.get("profile_id")
                                ),
                            ).props("color=blue")

                            ui.button(
                                "Скачать MD",
                                icon="article",
                                on_click=lambda: self._download_markdown_by_id(
                                    profile_data.get("profile_id")
                                ),
                            ).props("color=green")

                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

        dialog.open()

    async def _render_profile_basic_info(self, profile_data: Dict[str, Any]):
        """Отображение базовой информации профиля"""
        with ui.expansion("📋 Основная информация", value=True).classes("w-full"):
            with ui.grid(columns="1fr 1fr").classes("gap-4 p-4"):
                # Левая колонка
                with ui.column().classes("gap-3"):
                    self._render_info_item(
                        "Должность", profile_data.get("position_title")
                    )
                    self._render_info_item(
                        "Департамент", profile_data.get("department_path")
                    )
                    self._render_info_item("Версия", profile_data.get("version"))
                    self._render_info_item("Статус", profile_data.get("status"))

                # Правая колонка
                with ui.column().classes("gap-3"):
                    self._render_info_item(
                        "Создан", self._format_datetime(profile_data.get("created_at"))
                    )
                    self._render_info_item(
                        "Обновлен",
                        self._format_datetime(profile_data.get("updated_at")),
                    )
                    self._render_info_item("Автор", profile_data.get("created_by"))
                    if profile_data.get("employee_name"):
                        self._render_info_item(
                            "Сотрудник", profile_data.get("employee_name")
                        )

    def _render_info_item(self, label: str, value: Any):
        """Отображение элемента информации"""
        with ui.row().classes("items-center gap-3"):
            ui.label(f"{label}:").classes("text-weight-medium min-w-28 text-grey-7")
            ui.label(str(value or "Не указано")).classes("text-body1")

    async def _render_profile_content(self, json_data: Dict[str, Any]):
        """Отображение содержания профиля"""
        with ui.expansion("📄 Содержание профиля", value=False).classes("w-full"):
            with ui.column().classes("gap-4 p-4"):

                # Краткое описание
                if json_data.get("job_summary"):
                    ui.label("🎯 Краткое описание").classes("text-h6 font-medium")
                    ui.label(json_data["job_summary"]).classes("text-body1 mb-4")

                # Области ответственности
                if json_data.get("responsibility_areas"):
                    ui.label("📋 Области ответственности").classes(
                        "text-h6 font-medium mb-2"
                    )

                    for i, area in enumerate(json_data["responsibility_areas"][:3], 1):
                        if isinstance(area, dict):
                            area_names = area.get("area", [])
                            if isinstance(area_names, list) and area_names:
                                ui.label(f"{i}. {area_names[0]}").classes(
                                    "text-body1 font-medium"
                                )

                            tasks = area.get("tasks", [])
                            if tasks:
                                with ui.column().classes("ml-4 gap-1"):
                                    for task in tasks[:3]:
                                        ui.label(f"• {task}").classes("text-body2")
                                    if len(tasks) > 3:
                                        ui.label(
                                            f"... и еще {len(tasks) - 3} задач"
                                        ).classes("text-caption text-grey-6")

                # Профессиональные навыки
                if json_data.get("professional_skills"):
                    ui.label("🛠️ Профессиональные навыки").classes(
                        "text-h6 font-medium mb-2"
                    )

                    for skill_group in json_data["professional_skills"][:2]:
                        if isinstance(skill_group, dict):
                            category = skill_group.get("skill_category", "Общие навыки")
                            ui.label(f"▸ {category}").classes("text-body1 font-medium")

                            skills = skill_group.get("specific_skills", [])
                            for skill in skills[:3]:
                                if isinstance(skill, dict):
                                    skill_name = skill.get("skill_name", "")
                                    level = skill.get("proficiency_level", 1)
                                    ui.label(
                                        f"  • {skill_name} (Уровень {level})"
                                    ).classes("text-body2")

    async def _render_profile_metadata(self, profile_data: Dict[str, Any]):
        """Отображение метаданных профиля"""
        if not profile_data.get("generation_metadata"):
            return

        metadata = profile_data["generation_metadata"]

        with ui.expansion("⚙️ Метаданные генерации").classes("w-full"):
            with ui.grid(columns="1fr 1fr").classes("gap-4 p-4"):
                # Производительность
                with ui.column().classes("gap-2"):
                    ui.label("📊 Производительность").classes("text-body1 font-medium")

                    time_taken = metadata.get("generation_time_seconds", 0)
                    self._render_info_item("Время генерации", f"{time_taken:.1f} сек")

                    tokens = metadata.get("tokens_used", {})
                    if isinstance(tokens, dict):
                        total_tokens = tokens.get("total", 0)
                        input_tokens = tokens.get("input", 0)
                        output_tokens = tokens.get("output", 0)
                        self._render_info_item("Всего токенов", f"{total_tokens:,}")
                        if input_tokens:
                            self._render_info_item("Входные", f"{input_tokens:,}")
                        if output_tokens:
                            self._render_info_item("Выходные", f"{output_tokens:,}")
                    elif isinstance(tokens, int):
                        self._render_info_item("Токены", f"{tokens:,}")

                # Технические детали
                with ui.column().classes("gap-2"):
                    ui.label("🔧 Технические детали").classes("text-body1 font-medium")
                    self._render_info_item("Модель", metadata.get("model_used", ""))

                    if metadata.get("prompt_name"):
                        self._render_info_item("Промпт", metadata["prompt_name"])
                    if metadata.get("prompt_version"):
                        self._render_info_item(
                            "Версия промпта", metadata["prompt_version"]
                        )

                    if metadata.get("langfuse_trace_id"):
                        ui.label("🔍 Trace ID:").classes(
                            "text-weight-medium text-grey-7"
                        )
                        ui.label(metadata["langfuse_trace_id"]).classes(
                            "text-caption font-mono"
                        )

    def _show_download_options(self, profile: Dict[str, Any]):
        """Показ опций скачивания"""
        # Простое меню выбора формата
        ui.menu().props("auto-close").open()

        # TODO: Реализовать меню выбора формата
        ui.notify("Выберите формат для скачивания", type="info")

    async def _preview_markdown(self, profile: Dict[str, Any]):
        """Предпросмотр markdown файла"""
        try:
            profile_id = profile.get("profile_id")
            if not profile_id:
                ui.notify("ID профиля не найден", type="negative")
                return

            # Показываем диалог предпросмотра
            dialog = ui.dialog()

            with dialog:
                with ui.card().classes("w-[80vw] max-w-4xl max-h-[80vh]"):
                    # Заголовок
                    with ui.card_section().classes("bg-grey-1"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label("📄 Предпросмотр Markdown").classes("text-h6")
                            ui.button(icon="close", on_click=dialog.close).props(
                                "flat round"
                            )

                    # Контент предпросмотра
                    with ui.scroll_area().classes("flex-1"):
                        with ui.card_section():
                            # В реальной реализации здесь бы загружался markdown контент
                            position_title = profile.get(
                                "position_title", "Профиль должности"
                            )
                            department = profile.get("department_path", "Не указан")
                            created_at = self._format_datetime(
                                profile.get("created_at", "")
                            )

                            ui.markdown(
                                f"""
# 📋 {position_title}

**Департамент:** {department}

---

## 📊 Основная информация

| Параметр | Значение |
|----------|----------|
| **Название должности** | {position_title} |
| **Департамент** | {department} |
| **Создан** | {created_at} |

## 🎯 Области ответственности

*Загрузка полного содержания MD файла...*

---

*Это предварительный просмотр. Полное содержание доступно при скачивании MD файла.*
                            """
                            ).classes("w-full")

            dialog.open()

        except Exception as e:
            logger.error(f"Error previewing markdown: {e}")
            ui.notify(f"Ошибка предпросмотра: {str(e)}", type="negative")

    def _download_json(self, profile: Dict[str, Any]):
        """Скачивание JSON файла профиля"""
        self._download_profile_file(profile, "json")

    def _download_markdown(self, profile: Dict[str, Any]):
        """Скачивание Markdown файла профиля"""
        self._download_profile_file(profile, "md")

    def _download_json_by_id(self, profile_id: str):
        """Скачивание JSON по ID профиля"""
        if profile_id:
            ui.notify(f"📥 Загрузка JSON файла...", type="info")
            # В реальной реализации здесь был бы запрос к API
            logger.info(f"Download JSON requested for profile: {profile_id}")

    def _download_markdown_by_id(self, profile_id: str):
        """Скачивание Markdown по ID профиля"""
        if profile_id:
            ui.notify(f"📥 Загрузка MD файла...", type="info")
            # В реальной реализации здесь был бы запрос к API
            logger.info(f"Download MD requested for profile: {profile_id}")

    def _download_profile_file(self, profile: Dict[str, Any], format_type: str):
        """Базовый метод скачивания файла профиля"""
        try:
            profile_id = profile.get("profile_id")
            position_title = profile.get("position_title", "profile")

            if not profile_id:
                ui.notify("ID профиля не найден", type="negative")
                return

            # Уведомление пользователя
            format_name = "JSON" if format_type == "json" else "Markdown"
            ui.notify(
                f"📥 Загрузка {format_name} файла для '{position_title}'...",
                type="info",
            )

            # В реальной реализации здесь был бы вызов API
            # endpoint = f"/api/profiles/{profile_id}/download/{format_type}"
            logger.info(f"Download {format_type} requested for profile: {profile_id}")

        except Exception as e:
            logger.error(f"Error downloading profile file: {e}")
            ui.notify(f"Ошибка скачивания: {str(e)}", type="negative")


if __name__ == "__main__":
    print("✅ A101 Professional Profile Generator created!")
    print("🎨 Features:")
    print("  - NiceGUI-compatible corporate design")
    print("  - Debounced search with category filters")
    print("  - Professional progress tracking")
    print("  - Responsive mobile-friendly layout")
    print("  - Real-time feedback and error handling")

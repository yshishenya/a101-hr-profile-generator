"""
@doc
SearchComponent - Компонент поиска должностей для Linney.

Единственная ответственность: поиск и выбор должностей из каталога организации.
Обрабатывает 4,376 позиций с умным контекстом для различения дублированных должностей.

События:
- on_position_selected(position: str, department: str) - позиция выбрана для генерации

Examples:
  python> search = SearchComponent(api_client)
  python> search.on_position_selected = lambda pos, dept: print(f"Selected: {pos} in {dept}")
  python> await search.render_search_section()
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Callable, Optional

from nicegui import ui, app

try:
    # Relative imports для запуска как модуль
    from ...services.api_client import APIClient

    try:
        from ...core.error_recovery import (
            ErrorRecoveryCoordinator,
            RetryConfig,
            CircuitBreakerConfig,
        )
    except ImportError:
        # Error recovery is optional - system can work without it
        ErrorRecoveryCoordinator = None
        RetryConfig = None
        CircuitBreakerConfig = None
except ImportError:
    try:
        # Docker imports с /app в PYTHONPATH
        from frontend.services.api_client import APIClient

        try:
            from frontend.core.error_recovery import (
                ErrorRecoveryCoordinator,
                RetryConfig,
                CircuitBreakerConfig,
            )
        except ImportError:
            # Error recovery is optional - system can work without it
            ErrorRecoveryCoordinator = None
            RetryConfig = None
            CircuitBreakerConfig = None
    except ImportError:
        # Прямые импорты для local development
        import sys
        import os

        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(current_dir, "../..")
        sys.path.append(frontend_dir)
        from services.api_client import APIClient

        try:
            from core.error_recovery import (
                ErrorRecoveryCoordinator,
                RetryConfig,
                CircuitBreakerConfig,
            )
        except ImportError:
            # Error recovery is optional - system can work without it
            ErrorRecoveryCoordinator = None
            RetryConfig = None
            CircuitBreakerConfig = None

logger = logging.getLogger(__name__)


class SearchComponent:
    """
    @doc
    Компонент поиска должностей с контекстуальными подсказками.

    Особенности:
    - Contextual search с умным различением дублированных должностей
    - Загрузка 4,376 позиций из organization API
    - Fallback suggestions при недоступности backend
    - Debounced search с real-time feedback
    - События для интеграции с другими компонентами

    Examples:
      python> search = SearchComponent(api_client)
      python> search.on_position_selected = generator.set_position
      python> container = await search.render_search_section()
    """

    def __init__(
        self,
        api_client,
        error_recovery_coordinator: Optional[ErrorRecoveryCoordinator] = None,
    ):
        """
        @doc
        Инициализация компонента поиска должностей.

        Args:
            api_client: Экземпляр APIClient для взаимодействия с backend

        Examples:
          python> search = SearchComponent(api_client)
          python> # Компонент готов к использованию
        """
        self.api_client = api_client
        self.error_recovery_coordinator = error_recovery_coordinator

        # UI компоненты
        self.search_input = None
        self.search_results_container = None
        self.search_loading = None

        # Состояние поиска
        self.current_query = ""
        self.search_timer = None
        self.is_searching = False
        self.fallback_mode = False
        self.recovery_in_progress = False

        # Данные для поиска
        self.hierarchical_suggestions = []
        self.position_lookup = {}
        self.search_history = []

        # Кеширование для оптимизации
        self._suggestions_cache = None
        self._cache_timestamp = None

        # Выбранные данные
        self.selected_position = ""
        self.selected_department = ""
        self.selected_position_details = None
        self.position_details = None
        self.department_details = None
        self.position_profiles = []

        # Error recovery components (optional)
        self.circuit_breaker = None
        self.retry_manager = None
        if (
            self.error_recovery_coordinator
            and ErrorRecoveryCoordinator is not None
            and CircuitBreakerConfig is not None
        ):
            try:
                self.circuit_breaker = (
                    self.error_recovery_coordinator.get_circuit_breaker(
                        "search_component",
                        CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30),
                    )
                )
                self.retry_manager = self.error_recovery_coordinator.get_retry_manager(
                    "search_retry",
                    RetryConfig(max_retries=2, base_delay=1, max_delay=10),
                )
                # Register recovery callback
                self.error_recovery_coordinator.register_recovery_callback(
                    "search_component", self._on_recovery_callback
                )
                logger.info("Error recovery components initialized successfully")
            except Exception as e:
                logger.warning(
                    f"Error recovery initialization failed: {e}. Component will work in basic mode."
                )
                self.circuit_breaker = None
                self.retry_manager = None

        # События для интеграции с другими компонентами
        self.on_position_selected: Optional[Callable[[str, str], None]] = None
        self.on_profiles_found: Optional[Callable[[list], None]] = None

    async def force_reload_data(self, from_recovery: bool = False):
        """
        @doc
        Принудительная перезагрузка данных для поиска.

        Используется для обновления списка должностей после событий,
        например, после авторизации пользователя.

        Examples:
          python> await search.force_reload_data()
          python> # Данные перезагружены с backend
        """
        logger.info(
            f"Force reloading search data{'(recovery mode)' if from_recovery else ''}..."
        )

        # Save current state before reload
        if self.error_recovery_coordinator and not from_recovery:
            self._save_component_state()

        # Clear fallback mode on successful recovery
        if from_recovery and self.fallback_mode:
            self.fallback_mode = False
            self.recovery_in_progress = False
            self._update_ui_recovery_state()

        await self.load_search_data()

    async def load_search_data(self):
        """
        @doc
        Загрузка данных для поиска должностей.

        Загружает 4,376 позиций из organization API с контекстуальными подсказками.
        При недоступности API использует fallback suggestions.

        Examples:
          python> await search.load_search_data()
          python> # Данные загружены, поиск готов к работе
        """
        # Оптимизация: используем таймер для ленивой загрузки
        if not self.hierarchical_suggestions:
            await self._load_hierarchical_suggestions()

    async def render_search_section(self) -> ui.column:
        """
        @doc
        Рендеринг секции поиска должностей с оптимизированной загрузкой.

        Использует progressive loading - сначала показывает UI, затем загружает данные асинхронно.

        Returns:
            ui.column: Контейнер с поисковой секцией

        Examples:
          python> container = await search.render_search_section()
          python> # Поисковая секция отрендерена мгновенно
        """
        with ui.column().classes("w-full gap-4") as search_container:
            # Заголовок секции с легендой статусов
            with ui.row().classes("w-full items-center justify-between"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("search", size="1.5rem").classes("text-primary")
                    ui.label("Поиск должности").classes(
                        "text-h6 text-weight-medium text-primary"
                    )

                # Status legend
                self._render_status_legend()

            # Поисковое поле с dropdown и подсказками
            with ui.row().classes("w-full gap-2"):
                self.search_input = (
                    ui.select(
                        options={},
                        with_input=True,
                        on_change=self._on_search_select,
                        new_value_mode="add-unique",
                    )
                    .classes("flex-1")
                    .props(
                        'use-input hide-selected fill-input input-debounce="300" '
                        'clearable placeholder="Начните вводить название должности..."'
                    )
                    .tooltip(
                        "💡 Введите несколько букв для поиска должности. Система найдет все подходящие варианты с указанием отделов."
                    )
                )
                self.search_input.on("filter", self._on_search_filter)

                # Кнопка очистки с подсказкой
                ui.button("", icon="clear", on_click=self._clear_search).classes(
                    "self-stretch"
                ).props("flat color=grey-6").tooltip("Очистить поиск и начать заново")

            # Подсказка по использованию поиска
            ui.label(
                "💡 Совет: Используйте контекстуальную информацию в скобках для выбора нужного отдела"
            ).classes("text-caption text-blue-600 mt-1")

            # Контейнер для результатов поиска
            self.search_results_container = ui.column().classes("w-full")

            # Индикатор загрузки
            with ui.row().classes("w-full justify-center mt-2"):
                self.search_loading = ui.spinner(size="sm").classes("text-primary")
                self.search_loading.style("display: none")

        return search_container

    def _render_status_legend(self):
        """
        @doc
        Рендеринг легенды статусов профилей.

        Показывает пользователям что означают эмодзи статусов профилей.

        Examples:
          python> search._render_status_legend()
          python> # Отрендерена легенда статусов
        """
        with ui.expansion("📋 Статусы профилей", icon="help").classes("w-auto"):
            with ui.column().classes("gap-2"):
                statuses = [
                    (
                        "🟢",
                        "Готов",
                        "Профиль полностью завершен и готов к использованию",
                        "positive",
                    ),
                    (
                        "🟡",
                        "Черновик",
                        "Профиль создан, но может требовать доработки",
                        "warning",
                    ),
                    (
                        "⚙️",
                        "Создается",
                        "ИИ генерирует профиль, подождите немного",
                        "info",
                    ),
                    (
                        "🔴",
                        "Отсутствует",
                        "Профиль для этой должности еще не создан",
                        "negative",
                    ),
                    (
                        "📚",
                        "Несколько версий",
                        "Доступно несколько вариантов профиля",
                        "primary",
                    ),
                ]

                ui.label("Расшифровка статусов профилей:").classes(
                    "text-subtitle2 font-medium mb-2"
                )

                for emoji, status, description, color in statuses:
                    with ui.row().classes("items-center gap-2 py-1"):
                        ui.label(emoji).classes("text-lg")
                        with ui.column().classes("gap-0"):
                            ui.label(status).classes(
                                f"text-body2 font-medium text-{color}"
                            )
                            ui.label(description).classes("text-caption text-grey-6")

    async def _load_hierarchical_suggestions(self, retry_count: int = 0):
        """Загрузка position-first предложений для contextual search с кешированием"""
        try:
            import time

            # Проверяем кеш (кешируем на 5 минут)
            current_time = time.time()
            if (
                self._suggestions_cache
                and self._cache_timestamp
                and (current_time - self._cache_timestamp) < 300
            ):
                logger.info("Using cached suggestions for better performance")
                self.hierarchical_suggestions = self._suggestions_cache["suggestions"]
                self.position_lookup = self._suggestions_cache["lookup"]

                if hasattr(self, "search_input") and self.search_input:
                    options_dict = {
                        suggestion: suggestion
                        for suggestion in self.hierarchical_suggestions
                    }
                    self.search_input.set_options(options_dict)
                return

            logger.info(
                "Loading contextual position suggestions from organization API..."
            )

            # CRITICAL FIX: If we have a token in APIClient but not authenticated in storage, set it
            if hasattr(app, "storage") and not app.storage.user.get(
                "authenticated", False
            ):
                if (
                    hasattr(self.api_client, "_access_token")
                    and self.api_client._access_token
                ):
                    app.storage.user["authenticated"] = True
                    logger.info("✅ Set authentication status based on APIClient token")

            if not hasattr(app, "storage") or not app.storage.user.get(
                "authenticated", False
            ):
                logger.warning("User not authenticated, using fallback suggestions")
                self._use_fallback_suggestions()
                return

            # Enhanced API call with circuit breaker and retry
            search_items_response = await self._safe_api_call(
                self.api_client.get_organization_search_items
            )

            if not search_items_response or not search_items_response.get("success"):
                error_msg = (
                    search_items_response.get("message", "Unknown error")
                    if search_items_response
                    else "API unavailable"
                )
                logger.warning(f"Failed to get search items: {error_msg}")

                # Handle API failure with recovery
                await self._handle_api_failure(
                    "load_suggestions", error_msg, retry_count
                )
                return

            search_items = search_items_response["data"]["items"]

            position_suggestions = self._create_position_suggestions(search_items)

            self.hierarchical_suggestions = [
                item["display_name"] for item in position_suggestions
            ]
            self.position_lookup = {
                item["display_name"]: item for item in position_suggestions
            }

            # Кешируем результат
            self._suggestions_cache = {
                "suggestions": self.hierarchical_suggestions,
                "lookup": self.position_lookup,
            }
            self._cache_timestamp = current_time

            logger.info(
                f"✅ Loaded {len(self.hierarchical_suggestions)} contextual position suggestions from {len(search_items)} business units"
            )

            if hasattr(self, "search_input") and self.search_input:
                # 🚀 ПРОИЗВОДИТЕЛЬНОСТЬ: Ограничиваем количество опций для быстрого рендеринга
                max_options = 1000  # Показываем максимум 1000 опций вместо 4376
                limited_suggestions = self.hierarchical_suggestions[:max_options]

                options_dict = {
                    suggestion: suggestion for suggestion in limited_suggestions
                }
                self.search_input.set_options(options_dict)
                logger.info(
                    f"✅ Updated search dropdown with {len(limited_suggestions)} contextual position options (performance optimized)"
                )

        except Exception as e:
            logger.error(f"Error loading contextual position suggestions: {e}")

            # Enhanced error handling with recovery
            await self._handle_api_failure(
                "load_suggestions_error", str(e), retry_count
            )

            # Always provide fallback as last resort
            if retry_count >= 2:  # After all retries exhausted
                self._use_fallback_suggestions(error_context=str(e))

    def _create_position_suggestions(self, search_items):
        """
        @doc
        Создание contextual position suggestions с умным различением дублей.

        Преобразует бизнес-единицы в список позиций с контекстом:
        - "Java-разработчик → ДИТ (Блок ОД)" для уникальных позиций
        - "Руководитель группы → Группа 1 (Упр. подбора)" для дублированных

        Args:
            search_items: Список бизнес-единиц из API

        Returns:
            List[Dict]: Список позиций с contextual display names

        Examples:
          python> suggestions = search._create_position_suggestions(search_items)
          python> print(len(suggestions))  # 4376
        """
        # Шаг 1: Создаем map для обнаружения дублирования позиций (оптимизировано)
        position_instances = {}

        # Фильтруем единицы с позициями заранее для повышения производительности
        units_with_positions = [
            unit for unit in search_items if unit.get("positions_count", 0) > 0
        ]

        for unit in units_with_positions:
            positions = unit.get("positions", [])
            for position in positions:
                position_key = position.lower().strip()
                if position_key not in position_instances:
                    position_instances[position_key] = []

                position_instances[position_key].append(
                    {"position_name": position, "unit": unit}
                )

        # Шаг 2: Создаем contextual suggestions для каждой позиции (оптимизировано)
        position_suggestions = []

        # Используем list comprehension для оптимизации
        for position_key, instances in position_instances.items():
            is_duplicated = len(instances) > 1

            suggestions_batch = []
            for instance in instances:
                position_name = instance["position_name"]
                unit = instance["unit"]

                # Создаем contextual display name
                display_name = self._create_contextual_display_name(
                    position_name, unit, is_duplicated
                )

                suggestions_batch.append(
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

            position_suggestions.extend(suggestions_batch)

        logger.info(
            f"Created {len(position_suggestions)} contextual position suggestions from {len(units_with_positions)} units"
        )
        return position_suggestions

    def _create_contextual_display_name(self, position_name, unit, is_duplicated):
        """
        @doc
        Создание умного contextual display name для позиции.

        Args:
            position_name: Название позиции
            unit: Данные бизнес-единицы
            is_duplicated: True если позиция дублируется в других единицах

        Returns:
            str: Контекстуальное отображаемое имя

        Examples:
          python> name = search._create_contextual_display_name("Java-разработчик", unit, False)
          python> print(name)  # "Java-разработчик → ДИТ"
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

    def _use_fallback_suggestions(self, error_context: str = ""):
        """
        @doc
        Использование fallback предложений при недоступности backend.

        Создает базовые предложения должностей для тестирования.

        Examples:
          python> search._use_fallback_suggestions()
          python> print(len(search.hierarchical_suggestions))  # 12
        """
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
                "level": 0,
            }

        self.fallback_mode = True
        logger.warning(
            f"Using fallback suggestions: {len(fallback_positions)} positions"
            + (f" (due to: {error_context})" if error_context else "")
        )

        # Update UI to show fallback mode
        self._update_ui_fallback_state()

    async def _on_search_filter(self, event: Dict[str, Any]):
        """
        @doc
        Обработчик фильтрации списка при вводе текста.

        NiceGUI 'ui.select' с 'use-input' генерирует событие 'filter',
        которое можно использовать для динамического обновления опций.

        Args:
            event: Событие фильтра с введенным значением.
        """
        if not self.search_input:
            return

        raw_query = event.args

        # NiceGUI может передавать значение как строку или как список
        if isinstance(raw_query, list):
            query = raw_query[0] if raw_query else ""
        else:
            query = raw_query if raw_query else ""

        query = query.lower()

        if not query:
            # Если запрос пустой, показываем несколько последних из истории или ничего
            initial_options = self.search_history[:5]
            self.search_input.set_options({opt: opt for opt in initial_options})
            return

        # Фильтруем предложения
        filtered_suggestions = [
            s for s in self.hierarchical_suggestions if query in s.lower()
        ]

        # Ограничиваем количество для производительности
        options_to_show = filtered_suggestions[:100]

        self.search_input.set_options({opt: opt for opt in options_to_show})

    async def _on_search_select(self, event=None):
        """
        @doc
        Обработчик выбора варианта из dropdown.

        Обрабатывает выбор позиции и вызывает событие on_position_selected.

        Args:
            event: Событие выбора из NiceGUI

        Examples:
          python> await search._on_search_select(event)
          python> # Позиция обработана и событие отправлено
        """
        if event and hasattr(event, "value") and event.value:
            # Получаем выбранное значение из dropdown
            selected_value = event.value.strip()
            logger.info(f"Selected from dropdown: {selected_value}")

            # Добавляем в историю поиска
            if selected_value not in self.search_history:
                self.search_history.insert(0, selected_value)
                self.search_history = self.search_history[:10]  # Храним 10 последних

            # Обрабатываем иерархический выбор
            department, position = self._process_hierarchical_selection(selected_value)

            # Устанавливаем данные для генерации
            if department and position:
                await self._set_selected_position(position, department)
                ui.notify(f"✅ Выбрано: {position} в {department}", type="positive")

                # Вызываем событие для других компонентов
                logger.info(
                    f"🔥 DEBUG: About to call on_position_selected with {position}, {department}"
                )
                logger.info(
                    f"🔥 DEBUG: on_position_selected is: {self.on_position_selected}"
                )
                if self.on_position_selected:
                    logger.info(
                        f"🔥 DEBUG: Calling on_position_selected({position}, {department})"
                    )
                    self.on_position_selected(position, department)
                    logger.info(f"🔥 DEBUG: on_position_selected call completed")
                else:
                    logger.warning(
                        f"🔥 DEBUG: on_position_selected is None, cannot call event"
                    )
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

                    # Вызываем событие для других компонентов
                    logger.info(
                        f"🔥 DEBUG: Fallback - About to call on_position_selected with {position}, {department}"
                    )
                    if self.on_position_selected:
                        logger.info(
                            f"🔥 DEBUG: Fallback - Calling on_position_selected({position}, {department})"
                        )
                        self.on_position_selected(position, department)
                    else:
                        logger.warning(
                            f"🔥 DEBUG: Fallback - on_position_selected is None, cannot call event"
                        )

    def _process_hierarchical_selection(self, selection: str) -> tuple[str, str]:
        """
        @doc
        Обработка выбора из contextual position search.

        Args:
            selection: Выбранная строка (display_name позиции с контекстом)

        Returns:
            tuple[str, str]: (unit_name, position_name) или ("", "") если не удалось извлечь

        Examples:
          python> dept, pos = search._process_hierarchical_selection("Java-разработчик → ДИТ")
          python> print(dept, pos)  # ("ДИТ", "Java-разработчик")
        """
        try:
            if hasattr(self, "position_lookup") and selection in self.position_lookup:
                position_item = self.position_lookup[selection]

                position_name = position_item["position_name"]
                unit_name = position_item["unit_name"]
                unit_path = position_item["unit_path"]

                logger.info(
                    f"Contextual position selection: {position_name} in {unit_name} (path: {unit_path})"
                )
                return unit_name, position_name

            if " → " in selection:
                parts = [part.strip() for part in selection.split(" → ")]
                if len(parts) >= 2:
                    position_name = parts[0]
                    context_part = parts[1]

                    if "(" in context_part:
                        unit_name = context_part.split("(")[0].strip()
                    else:
                        context_parts = context_part.split(" → ")
                        unit_name = context_parts[-1].strip()

                    logger.info(
                        f"Fallback contextual selection: {position_name} in {unit_name}"
                    )
                    return unit_name, position_name
            else:
                logger.info(f"Simple position selection: {selection}")
                return "", selection.strip()

        except Exception as e:
            logger.error(f"Error processing contextual selection: {e}")

        return "", ""

    async def _set_selected_position(self, position: str, department: str):
        """
        @doc
        Установка выбранной позиции.

        Сохраняет выбранные данные и загружает детальную информацию о позиции.

        Args:
            position: Название позиции
            department: Название департамента

        Examples:
          python> await search._set_selected_position("Java-разработчик", "ДИТ")
          python> print(search.selected_position)  # "Java-разработчик"
        """
        # Сохраняем выбранные данные
        self.selected_position = position
        self.selected_department = department

        logger.info(f"Position selected: {position} in {department}")

        # Показываем индикатор загрузки
        self._show_loading_indicator()

        # Загружаем детальную информацию о позиции
        await self._load_position_details(position, department)

        # Отображаем статус карточку после загрузки
        profile_status_info = self._analyze_profile_status()
        self.render_profile_status_card(position, department, profile_status_info)

    async def _load_position_details(
        self, position: str, department: str, retry_count: int = 0
    ):
        """
        @doc
        Загрузка детальной информации о позиции включая статус профилей.

        Args:
            position: Название позиции
            department: Название департамента

        Examples:
          python> await search._load_position_details("Java-разработчик", "ДИТ")
          python> print(len(search.position_profiles))  # Количество существующих профилей
        """
        try:
            # Enhanced API calls with circuit breaker and retry
            positions_response = await self._safe_api_call(
                self.api_client.get_positions, department
            )

            # Ищем конкретную позицию в ответе
            self.position_details = None
            if positions_response and positions_response.get("success"):
                positions = positions_response["data"]["positions"]
                for pos in positions:
                    if pos["name"] == position:
                        self.position_details = pos
                        break

            # Получаем информацию о департаменте для полной иерархии
            departments_response = await self._safe_api_call(
                self.api_client.get_departments
            )

            self.department_details = None
            if departments_response and departments_response.get("success"):
                departments = departments_response["data"]["departments"]
                for dept in departments:
                    if dept["name"] == department:
                        self.department_details = dept
                        break

            # Получаем информацию о существующих профилях для этой позиции
            profiles_response = await self._safe_api_call(
                self.api_client.get_profiles_list,
                department=department,
                position=position,
                limit=100,  # Получаем все версии
            )

            # Сохраняем информацию о профилях
            self.position_profiles = []
            if profiles_response and profiles_response.get("profiles"):
                self.position_profiles = profiles_response["profiles"]

            # Save successful state for recovery
            if self.error_recovery_coordinator:
                self._save_component_state()

            # Вызываем событие с расширенной информацией о статусе
            profile_status_info = self._analyze_profile_status()
            logger.info(
                f"🔥 DEBUG: About to call on_profiles_found with {len(self.position_profiles)} profiles"
            )
            logger.info(f"🔥 DEBUG: on_profiles_found is: {self.on_profiles_found}")
            if self.on_profiles_found:
                logger.info(f"🔥 DEBUG: Calling on_profiles_found with profiles data")
                self.on_profiles_found(
                    {
                        "profiles": self.position_profiles,
                        "status": profile_status_info,
                        "position": position,
                        "department": department,
                    }
                )
                logger.info(f"🔥 DEBUG: on_profiles_found call completed")
            else:
                logger.warning(
                    f"🔥 DEBUG: on_profiles_found is None, cannot call event"
                )

            logger.info(
                f"Loaded details for {position}: {len(self.position_profiles)} existing profiles, status: {profile_status_info['status']}"
            )

        except Exception as e:
            logger.error(f"Error loading position details: {e}")

            # Enhanced error handling with recovery
            await self._handle_api_failure(
                f"load_position_details_{position}", str(e), retry_count
            )

            if retry_count < 2:  # Allow retries
                logger.info(
                    f"Retrying position details load (attempt {retry_count + 1})"
                )
                await asyncio.sleep(1 * (retry_count + 1))  # Progressive delay
                await self._load_position_details(position, department, retry_count + 1)
            else:
                # All retries exhausted
                self.position_details = None
                self.position_profiles = []

                # Show enhanced error state with recovery options
                self._show_error_state(
                    error_type="loading_error",
                    message=f"Не удалось загрузить информацию о профилях для позиции '{position}'",
                    details=str(e),
                    retry_callback=lambda: asyncio.create_task(
                        self._load_position_details(position, department, 0)
                    ),
                )

    def _analyze_profile_status(self) -> Dict[str, Any]:
        """
        @doc
        Анализ статуса профилей для позиции.

        Определяет статус профилей на основе количества и состояния.

        Returns:
            Dict[str, Any]: Информация о статусе профилей

        Examples:
          python> status = search._analyze_profile_status()
          python> print(status['status'])  # "has_multiple", "has_single", "no_profiles"
        """
        profile_count = len(self.position_profiles)

        if profile_count == 0:
            return {
                "status": "no_profiles",
                "icon": "🔴",
                "color": "grey-5",
                "text": "Нет профиля",
                "count": 0,
                "action": "create",
            }
        elif profile_count == 1:
            profile = self.position_profiles[0]
            profile_status = profile.get("status", "unknown")

            if profile_status == "completed":
                return {
                    "status": "has_single",
                    "icon": "🟢",
                    "color": "positive",
                    "text": "Профиль готов",
                    "count": 1,
                    "action": "view",
                }
            elif profile_status == "in_progress":
                return {
                    "status": "generating",
                    "icon": "⚙️",
                    "color": "warning",
                    "text": "Генерируется...",
                    "count": 1,
                    "action": "wait",
                }
            else:
                return {
                    "status": "has_single",
                    "icon": "🟡",
                    "color": "info",
                    "text": "Профиль черновик",
                    "count": 1,
                    "action": "edit",
                }
        else:
            completed_count = sum(
                1 for p in self.position_profiles if p.get("status") == "completed"
            )
            return {
                "status": "has_multiple",
                "icon": "📚",
                "color": "primary",
                "text": f"Несколько версий ({profile_count})",
                "count": profile_count,
                "completed_count": completed_count,
                "action": "list",
            }

    def render_profile_status_card(
        self, position: str, department: str, status_info: Dict[str, Any]
    ):
        """
        @doc
        Рендеринг карточки статуса профиля после выбора позиции.

        Args:
            position: Название позиции
            department: Название департамента
            status_info: Информация о статусе из _analyze_profile_status()

        Examples:
          python> search.render_profile_status_card("Java Developer", "IT", status_info)
          python> # Отрендерена карточка со статусом профиля
        """
        # Очищаем контейнер результатов
        if not self.search_results_container:
            logger.warning(
                "Cannot render profile status card - search_results_container not initialized"
            )
            return

        self.search_results_container.clear()

        with self.search_results_container:
            # Заголовок результатов поиска
            ui.label(f'🔍 Результаты поиска: "{position}"').classes(
                "text-h6 font-medium text-primary mb-4"
            )

            # Карточка статуса профиля с улучшенной видимостью статуса
            with ui.card().classes(
                f"w-full border-l-4 border-{status_info['color']} hover:shadow-lg transition-shadow"
            ):
                with ui.card_section():
                    # Компактный статус-индикатор (убираем переразмеренный badge)
                    with ui.row().classes("w-full items-center gap-3 mb-4"):
                        # Компактный статус с иконкой
                        ui.icon("folder", size="md").classes(
                            f"text-{status_info['color']}"
                        )
                        with ui.column().classes("flex-1"):
                            ui.label(status_info["text"]).classes(
                                f"text-subtitle1 font-medium text-{status_info['color']}"
                            )
                            if status_info["count"] > 1:
                                ui.label(
                                    f"{status_info['count']} версий доступно"
                                ).classes("text-caption text-grey-6")

                    # Информация о позиции (чистый дизайн)
                    with ui.column().classes("w-full gap-2 mb-4"):
                        ui.label(position).classes("text-h6 font-bold text-grey-9")
                        ui.label(department).classes("text-body1 text-grey-6")

                        # Дополнительная информация для множественных профилей
                        if status_info.get("completed_count") is not None:
                            completed = status_info["completed_count"]
                            total = status_info["count"]
                            ui.label(f"Готовых версий: {completed} из {total}").classes(
                                "text-body2 text-grey-6"
                            )

                    # Консолидированные действия (стандартный размер, без избыточных эмодзи)
                    with ui.row().classes("w-full gap-3 mt-4"):
                        if status_info["action"] == "view":
                            # Основное действие
                            ui.button(
                                "Просмотр профиля",
                                icon="visibility",
                                on_click=lambda: self._view_single_profile(),
                            ).props("color=primary").classes("flex-1")

                            # Вторичное действие
                            ui.button(
                                "Скачать",
                                icon="download",
                                on_click=lambda: self._download_profiles(),
                            ).props("outlined").classes("min-w-[100px]")

                        elif status_info["action"] == "list":
                            # Множественные профили
                            ui.button(
                                "Просмотр версий",
                                icon="list",
                                on_click=lambda: self._view_profile_versions(),
                            ).props("color=primary").classes("flex-1")

                            ui.button(
                                "Скачать",
                                icon="download",
                                on_click=lambda: self._download_profiles(),
                            ).props("outlined").classes("min-w-[100px]")

                        elif status_info["action"] == "create":
                            # Создание нового профиля
                            ui.button(
                                "Создать профиль",
                                icon="add",
                                on_click=lambda: self._create_new_profile(),
                            ).props("color=positive").classes("flex-1")

                        elif status_info["action"] == "wait":
                            ui.button(
                                "Генерация...",
                                icon="hourglass_empty",
                                on_click=lambda: self._cancel_generation(),
                            ).props("color=grey outlined").classes(
                                "flex-1"
                            ).set_enabled(
                                False
                            )

    def _view_single_profile(self):
        """Просмотр единственного профиля"""
        if self.position_profiles and len(self.position_profiles) > 0:
            profile = self.position_profiles[0]
            if self.on_profiles_found:
                # Вызываем событие напрямую (синхронная функция)
                self.on_profiles_found(
                    {
                        "profiles": [profile],
                        "status": self._analyze_profile_status(),
                        "position": self.selected_position,
                        "department": self.selected_department,
                        "view_mode": "single",
                    }
                )
                try:
                    ui.notify(
                        f"Открываем профиль: {profile.get('position', 'неизвестная должность')}",
                        type="info",
                    )
                except RuntimeError:
                    # UI notifications are optional when no context available
                    logger.info(
                        f"Opening profile: {profile.get('position', 'unknown position')}"
                    )

    def _view_profile_versions(self):
        """Просмотр списка версий профилей"""
        if self.on_profiles_found and self.position_profiles:
            # Вызываем событие напрямую (синхронная функция)
            self.on_profiles_found(
                {
                    "profiles": self.position_profiles,
                    "status": self._analyze_profile_status(),
                    "position": self.selected_position,
                    "department": self.selected_department,
                    "view_mode": "list",
                }
            )
            try:
                ui.notify(
                    f"Показываем {len(self.position_profiles)} версий профиля",
                    type="info",
                )
            except RuntimeError:
                # UI notifications are optional when no context available
                logger.info(f"Showing {len(self.position_profiles)} profile versions")

    def _create_new_profile(self):
        """Создание нового профиля"""
        if self.on_position_selected:
            self.on_position_selected(self.selected_position, self.selected_department)
            try:
                ui.notify("Запуск генерации нового профиля...", type="info")
            except RuntimeError:
                # UI notifications are optional when no context available
                logger.info("Starting generation of new profile...")

    def _cancel_generation(self):
        """Отмена генерации профиля"""
        try:
            ui.notify("Функция отмены генерации будет реализована", type="warning")
        except RuntimeError:
            # UI notifications are optional when no context available
            logger.warning("Cancel generation function not implemented yet")

    def _download_profiles(self):
        """Скачивание профилей"""
        if not self.position_profiles or len(self.position_profiles) == 0:
            try:
                ui.notify("❌ Нет профилей для скачивания", type="negative")
            except RuntimeError:
                logger.warning("No profiles available for download")
            return

        # Вызываем событие скачивания через callback
        if hasattr(self, 'on_download_request') and self.on_download_request:
            try:
                # Скачиваем первый профиль как JSON по умолчанию
                profile_id = self.position_profiles[0].get('profile_id')
                if profile_id:
                    logger.info(f"Initiating download for profile {profile_id}")
                    self.on_download_request(profile_id, "json")
                    try:
                        ui.notify("📥 Скачивание начато...", type="positive")
                    except RuntimeError:
                        pass
                else:
                    try:
                        ui.notify("❌ Не найден ID профиля", type="negative")
                    except RuntimeError:
                        logger.error("Profile ID not found")
            except Exception as e:
                logger.error(f"Download failed: {e}")
                try:
                    ui.notify(f"❌ Ошибка скачивания: {str(e)}", type="negative")
                except RuntimeError:
                    pass
        else:
            try:
                ui.notify("❌ Сервис скачивания недоступен", type="negative")
            except RuntimeError:
                logger.error("Download service not connected")

    def _show_loading_indicator(self):
        """
        @doc
        Отображение индикатора загрузки в контейнере результатов.

        Examples:
          python> search._show_loading_indicator()
          python> # Показан спиннер загрузки
        """
        if not self.search_results_container:
            logger.warning(
                "Cannot show loading indicator - search_results_container not initialized"
            )
            return

        self.search_results_container.clear()

        with self.search_results_container:
            with ui.row().classes("w-full justify-center items-center gap-3 p-8"):
                ui.spinner(size="lg").classes("text-primary")
                ui.label("Загрузка информации о профилях...").classes(
                    "text-body1 text-grey-6"
                )

    def _show_error_state(
        self,
        error_type: str = "generic",
        message: str = "",
        details: str = "",
        retry_callback=None,
    ):
        """
        @doc
        Отображение состояния ошибки в контейнере результатов.

        Args:
            error_type: Тип ошибки для определения иконки и цвета
            message: Основное сообщение об ошибке
            details: Детали ошибки (техническая информация)
            retry_callback: Функция для повторной попытки

        Examples:
          python> search._show_error_state("loading_error", "Не удалось загрузить данные")
          python> # Показано состояние ошибки с кнопкой повтора
        """
        if not self.search_results_container:
            logger.warning(
                "Cannot show error state - search_results_container not initialized"
            )
            return

        self.search_results_container.clear()

        error_configs = {
            "loading_error": {
                "icon": "🌐",
                "color": "orange",
                "title": "Ошибка загрузки",
                "suggestion": "Проверьте подключение к серверу и попробуйте еще раз",
            },
            "network_error": {
                "icon": "📡",
                "color": "red",
                "title": "Проблема с сетью",
                "suggestion": "Проверьте интернет-соединение",
            },
            "api_error": {
                "icon": "⚠️",
                "color": "orange",
                "title": "Ошибка сервера",
                "suggestion": "Сервер временно недоступен, попробуйте позже",
            },
            "permission_error": {
                "icon": "🔒",
                "color": "red",
                "title": "Нет доступа",
                "suggestion": "У вас нет прав для просмотра этих данных",
            },
        }

        config = error_configs.get(
            error_type,
            {
                "icon": "❌",
                "color": "red",
                "title": "Произошла ошибка",
                "suggestion": "Попробуйте обновить страницу",
            },
        )

        with self.search_results_container:
            with ui.card().classes(f"w-full border-l-4 border-{config['color']}-500"):
                with ui.card_section().classes(f"bg-{config['color']}-50"):
                    # Заголовок ошибки
                    with ui.row().classes("w-full items-center gap-3 mb-3"):
                        ui.label(config["icon"]).classes("text-2xl")
                        ui.label(config["title"]).classes(
                            f"text-h6 font-bold text-{config['color']}-700"
                        )

                    # Основное сообщение
                    if message:
                        ui.label(message).classes("text-body1 mb-2")

                    # Предложение по решению
                    ui.label(config["suggestion"]).classes(
                        "text-body2 text-grey-6 mb-3"
                    )

                    # Технические детали (сворачиваемые)
                    if details:
                        with ui.expansion("🔧 Технические детали", icon="info").classes(
                            "w-full"
                        ):
                            ui.label(details).classes(
                                "text-caption font-mono bg-grey-100 p-2 rounded"
                            )

                    # Кнопки действий
                    with ui.row().classes("w-full gap-2 mt-4"):
                        if retry_callback:
                            ui.button(
                                "Повторить", icon="refresh", on_click=retry_callback
                            ).props(f"color={config['color']}")

                        ui.button(
                            "Очистить", icon="clear", on_click=self._clear_search
                        ).props("outlined")

                        ui.button(
                            "На главную",
                            icon="home",
                            on_click=lambda: ui.navigate.to("/"),
                        ).props("outlined")

    async def _clear_search(self):
        """
        @doc
        Очистка результатов поиска.

        Сбрасывает все выбранные данные и очищает поисковое поле.

        Examples:
          python> search._clear_search()
          python> print(search.selected_position)  # ""
        """
        # Очищаем поисковое поле
        if self.search_input:
            self.search_input.set_value(None)
        else:
            logger.warning("Cannot clear search input - search_input not initialized")

        # Сбрасываем состояние
        self.selected_position = ""
        self.selected_department = ""
        self.position_details = None
        self.department_details = None
        self.position_profiles = []

        # Очищаем контейнер результатов
        if self.search_results_container:
            self.search_results_container.clear()

        # Также нужно очистить viewer, если он подписан на события
        if self.on_profiles_found:
            self.on_profiles_found([])  # Отправляем пустой список

        # Скрываем индикатор загрузки
        if self.search_loading:
            self.search_loading.style("display: none")

        logger.info("Search cleared")

    # === Error Recovery Methods ===

    async def _safe_api_call(self, api_func, *args, **kwargs):
        """
        @doc
        Execute API call with circuit breaker and retry protection.

        Args:
            api_func: API function to call
            *args: Positional arguments for api_func
            **kwargs: Keyword arguments for api_func

        Returns:
            API response or None if all recovery attempts fail

        Examples:
          python> response = await search._safe_api_call(api_client.get_departments)
          python> # API call with circuit breaker and retry protection
        """
        if not self.circuit_breaker or not self.retry_manager:
            # Fallback to direct call if no recovery infrastructure
            try:
                return await api_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Direct API call failed: {e}")
                return None

        try:
            # Use circuit breaker with retry manager
            return await self.circuit_breaker.call(
                self.retry_manager.retry,
                api_func,
                *args,
                retry_condition=self._should_retry_api_error,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Safe API call failed after all recovery attempts: {e}")
            return None

    def _should_retry_api_error(self, error: Exception) -> bool:
        """
        @doc
        Determine if API error should trigger retry.

        Args:
            error: Exception from API call

        Returns:
            True if should retry, False otherwise

        Examples:
          python> should_retry = search._should_retry_api_error(ConnectionError())
          python> print(should_retry)  # True
        """
        error_str = str(error).lower()

        # Retry on network and temporary server errors
        retry_conditions = [
            "timeout",
            "connection",
            "network",
            "temporary",
            "502",
            "503",
            "504",
            "service unavailable",
            "rate limit",
            "too many requests",
        ]

        should_retry = any(condition in error_str for condition in retry_conditions)

        if should_retry:
            logger.debug(f"API error is retryable: {error}")
        else:
            logger.debug(f"API error is not retryable: {error}")

        return should_retry

    async def _handle_api_failure(
        self, operation: str, error_message: str, retry_count: int = 0
    ):
        """
        @doc
        Handle API failure with recovery coordination.

        Args:
            operation: Name of the failed operation
            error_message: Error message from the failure
            retry_count: Current retry attempt

        Examples:
          python> await search._handle_api_failure("load_suggestions", "Connection timeout", 1)
          python> # Failure handled with recovery coordination
        """
        if self.error_recovery_coordinator:
            # Report error to coordinator for component-wide recovery
            try:
                error = Exception(f"{operation}: {error_message}")
                recovered = (
                    await self.error_recovery_coordinator.handle_component_error(
                        "search_component", error, attempt_recovery=True
                    )
                )

                if recovered:
                    logger.info(
                        f"Component recovery successful for operation: {operation}"
                    )
                    return
            except Exception as recovery_error:
                logger.error(f"Error recovery coordination failed: {recovery_error}")

        # Fallback to local recovery if coordinator unavailable
        await self._attempt_local_recovery(operation, retry_count)

    async def _attempt_local_recovery(self, operation: str, retry_count: int):
        """
        @doc
        Attempt local recovery without coordinator.

        Args:
            operation: Name of the failed operation
            retry_count: Current retry attempt

        Examples:
          python> await search._attempt_local_recovery("load_suggestions", 2)
          python> # Local recovery attempted
        """
        if retry_count < 2:
            # Try to reload data after delay
            delay = min(5 * (retry_count + 1), 30)  # Progressive delay up to 30s
            logger.info(f"Attempting local recovery for '{operation}' in {delay}s...")

            await asyncio.sleep(delay)

            if operation.startswith("load_suggestions"):
                await self._load_hierarchical_suggestions(retry_count + 1)
            elif operation.startswith("load_position_details"):
                # Extract position and department from current state
                if self.selected_position and self.selected_department:
                    await self._load_position_details(
                        self.selected_position,
                        self.selected_department,
                        retry_count + 1,
                    )
        else:
            # All local recovery attempts exhausted - enter fallback mode
            if not self.fallback_mode:
                logger.warning(
                    f"Entering fallback mode after failed recovery for: {operation}"
                )
                self.fallback_mode = True
                self._update_ui_fallback_state()

    def _save_component_state(self):
        """
        @doc
        Save current component state for recovery.

        Captures current search state to enable rollback on errors.

        Examples:
          python> search._save_component_state()
          python> # Current state saved for recovery
        """
        if not self.error_recovery_coordinator:
            return

        state_data = {
            "selected_position": self.selected_position,
            "selected_department": self.selected_department,
            "current_query": self.current_query,
            "hierarchical_suggestions": self.hierarchical_suggestions[
                :100
            ],  # Limit size
            "position_lookup": dict(list(self.position_lookup.items())[:100]),
            "search_history": self.search_history.copy(),
            "position_profiles": self.position_profiles.copy(),
            "fallback_mode": self.fallback_mode,
            "timestamp": time.time(),
        }

        try:
            self.error_recovery_coordinator.state_manager.save_state(
                "search_component", state_data, ttl_seconds=600  # 10 minute TTL
            )
            logger.debug("Component state saved for recovery")
        except Exception as e:
            logger.error(f"Failed to save component state: {e}")

    async def _on_recovery_callback(self, recovered_state: Dict[str, Any]):
        """
        @doc
        Handle state recovery from error recovery coordinator.

        Args:
            recovered_state: Previously saved state data

        Examples:
          python> await search._on_recovery_callback({"selected_position": "Developer"})
          python> # State recovered from coordinator
        """
        try:
            logger.info("Recovering search component state...")

            # Restore state data
            self.selected_position = recovered_state.get("selected_position", "")
            self.selected_department = recovered_state.get("selected_department", "")
            self.current_query = recovered_state.get("current_query", "")

            suggestions = recovered_state.get("hierarchical_suggestions", [])
            if suggestions:
                self.hierarchical_suggestions = suggestions

            lookup = recovered_state.get("position_lookup", {})
            if lookup:
                self.position_lookup = lookup

            history = recovered_state.get("search_history", [])
            if history:
                self.search_history = history

            profiles = recovered_state.get("position_profiles", [])
            if profiles:
                self.position_profiles = profiles

            # Update UI state
            self.recovery_in_progress = True
            self._update_ui_recovery_state()

            # Try to reload fresh data
            await self.force_reload_data(from_recovery=True)

            ui.notify("🔄 Поиск восстановлен после ошибки", type="positive")
            logger.info("Search component state recovery completed")

        except Exception as e:
            logger.error(f"Error during state recovery: {e}")
            ui.notify("⚠️ Частичное восстановление поиска", type="warning")

    def _update_ui_fallback_state(self):
        """
        @doc
        Update UI to show fallback mode indicator.

        Shows user that component is operating in degraded mode.

        Examples:
          python> search._update_ui_fallback_state()
          python> # UI updated to show fallback mode
        """
        if self.search_input:
            # Add fallback mode indicator
            self.search_input.tooltip(
                "⚠️ Режим ограниченного функционала - используются базовые данные. "
                "API временно недоступен."
            )

        # Show fallback notification
        if not self.recovery_in_progress:
            ui.notify(
                "⚠️ Поиск работает в режиме ограниченного функционала",
                type="warning",
                position="top",
            )

    def _update_ui_recovery_state(self):
        """
        @doc
        Update UI to show recovery in progress.

        Shows user that component is recovering from error.

        Examples:
          python> search._update_ui_recovery_state()
          python> # UI updated to show recovery state
        """
        if self.search_input:
            if self.recovery_in_progress:
                self.search_input.tooltip(
                    "🔄 Восстановление после ошибки - обновление данных..."
                )
            else:
                # Clear recovery state
                self.search_input.tooltip(
                    "💡 Введите несколько букв для поиска должности. "
                    "Система найдет все подходящие варианты с указанием отделов."
                )

    async def reset_component_state(self):
        """
        @doc
        Reset component to clean state.

        Used for manual recovery or when starting fresh.

        Examples:
          python> await search.reset_component_state()
          python> # Component reset to clean state
        """
        logger.info("Resetting search component state")

        # Clear all state
        self.current_query = ""
        self.selected_position = ""
        self.selected_department = ""
        self.position_details = None
        self.department_details = None
        self.position_profiles = []
        self.fallback_mode = False
        self.recovery_in_progress = False

        # Clear UI
        if self.search_input:
            self.search_input.set_value(None)
        else:
            logger.warning("Cannot reset search input - search_input not initialized")

        if self.search_results_container:
            self.search_results_container.clear()

        # Clear cache
        self._suggestions_cache = None
        self._cache_timestamp = None

        # Try to reload data
        try:
            await self.load_search_data()
            ui.notify("🔄 Поиск сброшен и перезагружен", type="info")
        except Exception as e:
            logger.error(f"Error reloading data after reset: {e}")
            ui.notify("⚠️ Поиск сброшен, но данные недоступны", type="warning")

    def get_selected_position_data(self) -> Dict[str, Any]:
        """
        @doc
        Получение данных выбранной позиции.

        Returns:
            Dict[str, Any]: Словарь с данными позиции или пустой словарь

        Examples:
          python> data = search.get_selected_position_data()
          python> print(data.get("position"))  # "Java-разработчик"
        """
        if not self.selected_position or not self.selected_department:
            return {}

        return {
            "position": self.selected_position,
            "department": self.selected_department,
            "position_details": self.position_details,
            "department_details": self.department_details,
            "existing_profiles": self.position_profiles,
        }

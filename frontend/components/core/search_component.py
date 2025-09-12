"""
@doc
SearchComponent - Компонент поиска должностей для A101 HR Profile Generator.

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
from typing import List, Dict, Any, Callable, Optional

from nicegui import ui, app

from ...services.api_client import APIClient

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

    def __init__(self, api_client):
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

        # UI компоненты
        self.search_input = None
        self.search_results_container = None
        self.search_loading = None

        # Состояние поиска
        self.current_query = ""
        self.search_timer = None
        self.is_searching = False

        # Данные для поиска
        self.hierarchical_suggestions = []
        self.position_lookup = {}
        self.search_history = []

        # Выбранные данные
        self.selected_position = ""
        self.selected_department = ""
        self.selected_position_details = None
        self.position_details = None
        self.department_details = None
        self.position_profiles = []

        # События для интеграции с другими компонентами
        self.on_position_selected: Optional[Callable[[str, str], None]] = None
        self.on_profiles_found: Optional[Callable[[list], None]] = None

    async def force_reload_data(self):
        """
        @doc
        Принудительная перезагрузка данных для поиска.

        Используется для обновления списка должностей после событий,
        например, после авторизации пользователя.

        Examples:
          python> await search.force_reload_data()
          python> # Данные перезагружены с backend
        """
        logger.info("Force reloading search data...")
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
        await self._load_hierarchical_suggestions()

    async def render_search_section(self) -> ui.column:
        """
        @doc
        Рендеринг секции поиска должностей.

        Returns:
            ui.column: Контейнер с поисковой секцией

        Examples:
          python> container = await search.render_search_section()
          python> # Поисковая секция отрендерена
        """
        with ui.column().classes("w-full gap-4") as search_container:
            # Заголовок секции
            with ui.row().classes("w-full items-center gap-3"):
                ui.icon("search", size="1.5rem").classes("text-primary")
                ui.label("Поиск должности").classes(
                    "text-h6 text-weight-medium text-primary"
                )

            # Поисковое поле с dropdown
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
                )
                self.search_input.on('filter', self._on_search_filter)

                # Кнопка очистки
                ui.button(
                    "", icon="clear", on_click=self._clear_search
                ).classes("self-stretch").props("flat color=grey-6")

            # Контейнер для результатов поиска
            self.search_results_container = ui.column().classes("w-full")

            # Индикатор загрузки
            with ui.row().classes("w-full justify-center mt-2"):
                self.search_loading = ui.spinner(size="sm").classes("text-primary")
                self.search_loading.style("display: none")

        return search_container

    async def _load_hierarchical_suggestions(self):
        """Загрузка position-first предложений для contextual search"""
        try:
            logger.info("Loading contextual position suggestions from organization API...")

            if not hasattr(app, "storage") or not app.storage.user.get("authenticated", False):
                logger.warning("User not authenticated, using fallback suggestions")
                self._use_fallback_suggestions()
                return

            search_items_response = await self.api_client.get_organization_search_items()

            if not search_items_response.get("success"):
                logger.warning("Failed to get search items from organization API, using fallback suggestions")
                self._use_fallback_suggestions()
                return

            search_items = search_items_response["data"]["items"]

            position_suggestions = self._create_position_suggestions(search_items)

            self.hierarchical_suggestions = [
                item["display_name"] for item in position_suggestions
            ]
            self.position_lookup = {
                item["display_name"]: item for item in position_suggestions
            }

            logger.info(f"✅ Loaded {len(self.hierarchical_suggestions)} contextual position suggestions from {len(search_items)} business units")

            if hasattr(self, "search_input") and self.search_input:
                options_dict = {
                    suggestion: suggestion for suggestion in self.hierarchical_suggestions
                }
                self.search_input.set_options(options_dict)
                logger.info("✅ Updated search dropdown with contextual position options")

        except Exception as e:
            logger.debug(f"Error loading contextual position suggestions (using fallback): {e}")
            self._use_fallback_suggestions()

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
        # Шаг 1: Создаем map для обнаружения дублирования позиций
        position_instances = {}

        for unit in search_items:
            if unit.get("positions_count", 0) == 0:
                continue

            for position in unit.get("positions", []):
                position_key = position.lower().strip()
                if position_key not in position_instances:
                    position_instances[position_key] = []

                position_instances[position_key].append({
                    "position_name": position,
                    "unit": unit
                })

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

                position_suggestions.append({
                    "display_name": display_name,
                    "position_name": position_name,
                    "unit_name": unit["name"],
                    "unit_path": unit["full_path"],
                    "hierarchy": unit["hierarchy"],
                    "level": unit.get("level", 0),
                    "unit_data": unit,
                })

        logger.info(f"Created {len(position_suggestions)} contextual position suggestions")
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

    def _use_fallback_suggestions(self):
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

        logger.info(f"Using fallback suggestions: {len(fallback_positions)} positions")

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
                self.search_history = self.search_history[:10] # Храним 10 последних

            # Обрабатываем иерархический выбор
            department, position = self._process_hierarchical_selection(selected_value)

            # Устанавливаем данные для генерации
            if department and position:
                await self._set_selected_position(position, department)
                ui.notify(f"✅ Выбрано: {position} в {department}", type="positive")

                # Вызываем событие для других компонентов
                if self.on_position_selected:
                    self.on_position_selected(position, department)
            else:
                # Если не удалось извлечь иерархию, показываем уведомление
                ui.notify("Выберите должность из списка для генерации профиля", type="info")

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
                    if self.on_position_selected:
                        self.on_position_selected(position, department)

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

                logger.info(f"Contextual position selection: {position_name} in {unit_name} (path: {unit_path})")
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

                    logger.info(f"Fallback contextual selection: {position_name} in {unit_name}")
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

        # Загружаем детальную информацию о позиции
        await self._load_position_details(position, department)

    async def _load_position_details(self, position: str, department: str):
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
            # Получаем детальную информацию о позиции из каталога
            positions_response = await self.api_client.get_positions(department)

            # Ищем конкретную позицию в ответе
            self.position_details = None
            if positions_response.get("success"):
                positions = positions_response["data"]["positions"]
                for pos in positions:
                    if pos["name"] == position:
                        self.position_details = pos
                        break

            # Получаем информацию о департаменте для полной иерархии
            departments_response = await self.api_client.get_departments()

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

            # Вызываем событие, если найдены существующие профили
            if self.on_profiles_found and self.position_profiles:
                await self.on_profiles_found(self.position_profiles)

            logger.info(f"Loaded details for {position}: {len(self.position_profiles)} existing profiles")

        except Exception as e:
            logger.error(f"Error loading position details: {e}")
            self.position_details = None
            self.position_profiles = []

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
            await self.on_profiles_found([]) # Отправляем пустой список

        # Скрываем индикатор загрузки
        if self.search_loading:
            self.search_loading.style("display: none")

        logger.info("Search cleared")

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

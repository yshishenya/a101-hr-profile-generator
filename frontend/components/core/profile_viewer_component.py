"""
@doc
ProfileViewerComponent - Компонент просмотра сгенерированных профилей для A101 HR Profile Generator.

Единственная ответственность: отображение детальной информации о профилях должностей.
Показывает содержимое профилей, метаданные генерации, версии и историю.

События:
- on_download_request(profile_id, format) - запрос на скачивание профиля

Examples:
  python> viewer = ProfileViewerComponent(api_client)
  python> viewer.on_download_request = files_manager.download_file
  python> await viewer.show_profile(profile_data)
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from nicegui import ui

logger = logging.getLogger(__name__)


class ProfileViewerComponent:
    """
    @doc
    Компонент просмотра детальной информации о профилях должностей.

    Особенности:
    - Детальное отображение содержимого профилей JSON
    - Метаданные генерации LLM (токены, время, модель)
    - История версий профилей
    - Форматирование профессиональных навыков и задач
    - События для интеграции со скачиванием файлов

    Examples:
      python> viewer = ProfileViewerComponent(api_client)
      python> viewer.on_download_request = lambda pid, fmt: print(f"Download {pid}")
      python> viewer.show_profile({"profile_id": "123", ...})
    """

    def __init__(self, api_client):
        """
        @doc
        Инициализация компонента просмотра профилей.

        Args:
            api_client: Экземпляр APIClient для взаимодействия с backend

        Examples:
          python> viewer = ProfileViewerComponent(api_client)
          python> # Компонент готов к использованию
        """
        self.api_client = api_client

        # UI компоненты
        self.profile_container = None
        self.profile_dialog = None

        # События для интеграции с другими компонентами
        self.on_download_request: Optional[Callable[[str, str], None]] = None

    async def render_profile_viewer(self) -> ui.column:
        """
        @doc
        Рендеринг контейнера для просмотра профилей.

        Returns:
            ui.column: Контейнер для отображения профилей

        Examples:
          python> container = await viewer.render_profile_viewer()
          python> # Контейнер просмотра профилей готов
        """
        with ui.column().classes("w-full gap-4") as profile_container:
            # Заголовок секции
            with ui.row().classes("w-full items-center gap-3"):
                ui.icon("preview", size="1.5rem").classes("text-primary")
                ui.label("Просмотр профилей").classes(
                    "text-h6 text-weight-medium text-primary"
                )

            # Контейнер для содержимого профилей
            self.profile_container = ui.column().classes("w-full")

        return profile_container

    async def show_profile(self, profile_data: Dict[str, Any]):
        """
        @doc
        Отображение профиля в диалоге.

        Загружает и показывает детальную информацию о профиле.

        Args:
            profile_data: Данные профиля от GeneratorComponent или API

        Examples:
          python> await viewer.show_profile({"profile_id": "123"})
          python> # Показан диалог с детальной информацией профиля
        """
        try:
            # Если это результат генерации, извлекаем нужные данные
            if "task_result" in profile_data:
                result = profile_data["task_result"]
                if result and "profile" in result:
                    profile_id = result.get("profile_id")
                    if profile_id:
                        # Загружаем полный профиль по ID
                        full_profile = await self.api_client.get_profile_by_id(profile_id)
                        if full_profile:
                            await self._show_profile_detail_dialog(full_profile)
                        else:
                            # Показываем данные из результата генерации
                            adapted_data = self._adapt_generation_result(result)
                            await self._show_profile_detail_dialog(adapted_data)
                    else:
                        # Показываем данные из результата генерации напрямую
                        adapted_data = self._adapt_generation_result(result)
                        await self._show_profile_detail_dialog(adapted_data)
                else:
                    ui.notify("❌ Нет данных профиля для отображения", type="negative")
            else:
                # Это уже готовые данные профиля
                await self._show_profile_detail_dialog(profile_data)

        except Exception as e:
            logger.error(f"Error showing profile: {e}")
            ui.notify(f"❌ Ошибка отображения: {str(e)}", type="negative")

    def _adapt_generation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        @doc
        Адаптация результата генерации к формату отображения.

        Args:
            result: Результат генерации профиля

        Returns:
            Dict[str, Any]: Адаптированные данные для отображения

        Examples:
          python> adapted = viewer._adapt_generation_result(generation_result)
          python> print(adapted["position_title"])
        """
        profile = result.get("profile", {})
        metadata = result.get("metadata", {})

        return {
            "profile_id": result.get("profile_id"),
            "position_title": profile.get("position_title", result.get("position", "Неизвестная должность")),
            "department_path": profile.get("department", result.get("department", "Неизвестный департамент")),
            "json_data": profile,
            "metadata": metadata,
            "generation_metadata": metadata,
            "created_at": result.get("created_at"),
            "created_by_username": result.get("created_by_username"),
            "version": result.get("version", "1.0"),
            "status": "completed"
        }

    async def _show_profile_detail_dialog(self, profile_data: Dict[str, Any]):
        """
        @doc
        Показ диалога с детальной информацией профиля.

        Args:
            profile_data: Данные профиля для отображения

        Examples:
          python> await viewer._show_profile_detail_dialog(profile_data)
          python> # Показан детальный диалог профиля
        """
        dialog = ui.dialog()

        with dialog:
            with ui.card().classes("w-[85vw] max-w-5xl max-h-[80vh]"):
                # Заголовок диалога
                with ui.card_section().classes("bg-primary text-white"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.column():
                            ui.label(profile_data.get("position_title", "Профиль должности")).classes(
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
                        self._render_profile_basic_info(profile_data)

                        # Содержание профиля (JSON данные)
                        if profile_data.get("json_data"):
                            self._render_profile_content(profile_data["json_data"])

                        # Метаданные генерации
                        if profile_data.get("generation_metadata") or profile_data.get("metadata"):
                            self._render_profile_metadata(profile_data)

                # Действия в футере
                with ui.card_actions():
                    with ui.row().classes("w-full justify-between"):
                        with ui.row().classes("gap-2"):
                            ui.button(
                                "Скачать JSON",
                                icon="file_download",
                                on_click=lambda: self._request_download(
                                    profile_data.get("profile_id"), "json"
                                ),
                            ).props("color=blue")

                            ui.button(
                                "Скачать MD",
                                icon="article",
                                on_click=lambda: self._request_download(
                                    profile_data.get("profile_id"), "markdown"
                                ),
                            ).props("color=green")

                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

        self.profile_dialog = dialog
        dialog.open()

    def _render_profile_basic_info(self, profile_data: Dict[str, Any]):
        """
        @doc
        Отображение базовой информации профиля.

        Args:
            profile_data: Данные профиля

        Examples:
          python> viewer._render_profile_basic_info(profile_data)
          python> # Отрендерена секция основной информации
        """
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
                        "Обновлен", self._format_datetime(profile_data.get("updated_at"))
                    )
                    self._render_info_item("Автор", profile_data.get("created_by_username"))
                    if profile_data.get("employee_name"):
                        self._render_info_item(
                            "Сотрудник", profile_data.get("employee_name")
                        )

    def _render_info_item(self, label: str, value: Any):
        """
        @doc
        Отображение элемента информации.

        Args:
            label: Название поля
            value: Значение поля

        Examples:
          python> viewer._render_info_item("Должность", "Java-разработчик")
          python> # Отрендерен элемент информации
        """
        with ui.row().classes("items-center gap-3"):
            ui.label(f"{label}:").classes("text-weight-medium min-w-28 text-grey-7")
            ui.label(str(value or "Не указано")).classes("text-body1")

    def _render_profile_content(self, json_data: Dict[str, Any]):
        """
        @doc
        Отображение содержания профиля.

        Показывает краткое описание, области ответственности и навыки.

        Args:
            json_data: JSON данные профиля

        Examples:
          python> viewer._render_profile_content(profile_json)
          python> # Отрендерено содержимое профиля
        """
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

                            skills = skill_group.get("skills", [])
                            if skills:
                                with ui.column().classes("ml-4 gap-1"):
                                    for skill in skills[:4]:
                                        if isinstance(skill, dict):
                                            skill_name = skill.get("skill_name", skill.get("name", str(skill)))
                                        else:
                                            skill_name = str(skill)
                                        ui.label(f"• {skill_name}").classes("text-body2")
                                    if len(skills) > 4:
                                        ui.label(f"... и еще {len(skills) - 4} навыков").classes(
                                            "text-caption text-grey-6"
                                        )

                # KPI и цели
                if json_data.get("kpi"):
                    ui.label("📊 Ключевые показатели (KPI)").classes(
                        "text-h6 font-medium mb-2"
                    )

                    kpi_data = json_data["kpi"]
                    if isinstance(kpi_data, list):
                        for i, kpi in enumerate(kpi_data[:3], 1):
                            if isinstance(kpi, dict):
                                kpi_name = kpi.get("kpi_name", kpi.get("name", f"KPI {i}"))
                                ui.label(f"{i}. {kpi_name}").classes("text-body1")
                            else:
                                ui.label(f"{i}. {str(kpi)}").classes("text-body1")

    def _render_profile_metadata(self, profile_data: Dict[str, Any]):
        """
        @doc
        Отображение метаданных профиля.

        Показывает информацию о генерации: время, токены, модель LLM.

        Args:
            profile_data: Данные профиля с метаданными

        Examples:
          python> viewer._render_profile_metadata(profile_data)
          python> # Отрендерены метаданные генерации
        """
        metadata = profile_data.get("generation_metadata") or profile_data.get("metadata")
        if not metadata:
            return

        with ui.expansion("⚙️ Метаданные генерации").classes("w-full"):
            with ui.grid(columns="1fr 1fr").classes("gap-4 p-4"):
                # Производительность
                with ui.column().classes("gap-2"):
                    ui.label("📊 Производительность").classes("text-body1 font-medium")

                    time_taken = metadata.get("generation_time_seconds", metadata.get("time_taken", 0))
                    self._render_info_item("Время генерации", f"{time_taken:.1f} сек")

                    tokens = metadata.get("tokens_used", metadata.get("tokens", {}))
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
                    self._render_info_item("Модель", metadata.get("model_used", metadata.get("model", "")))

                    if metadata.get("prompt_name"):
                        self._render_info_item("Промпт", metadata["prompt_name"])
                    if metadata.get("prompt_version"):
                        self._render_info_item("Версия промпта", metadata["prompt_version"])

                    if metadata.get("langfuse_trace_id"):
                        ui.label("🔍 Trace ID:").classes("text-weight-medium text-grey-7")
                        ui.label(metadata["langfuse_trace_id"]).classes("text-caption font-mono")

    def _format_datetime(self, datetime_str: str) -> str:
        """
        @doc
        Форматирование даты и времени для отображения.

        Args:
            datetime_str: Строка с датой в ISO формате

        Returns:
            str: Отформатированная дата

        Examples:
          python> formatted = viewer._format_datetime("2024-09-12T15:30:00Z")
          python> print(formatted)  # "12.09.2024 15:30"
        """
        if not datetime_str:
            return "Не указано"

        try:
            # Парсим ISO формат даты
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(datetime_str)

            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception as e:
            logger.debug(f"Error formatting datetime {datetime_str}: {e}")
            return str(datetime_str)

    def _request_download(self, profile_id: str, format_type: str):
        """
        @doc
        Запрос скачивания профиля.

        Вызывает событие для FilesManagerComponent.

        Args:
            profile_id: ID профиля для скачивания
            format_type: Тип файла ("json" или "markdown")

        Examples:
          python> viewer._request_download("profile123", "json")
          python> # Отправлен запрос на скачивание JSON
        """
        if self.on_download_request and profile_id:
            self.on_download_request(profile_id, format_type)
        else:
            ui.notify("❌ Невозможно скачать: нет ID профиля", type="negative")

    async def show_profile_list(self, profiles: list[Dict[str, Any]]):
        """
        @doc
        Отображение списка профилей.

        Args:
            profiles: Список профилей для отображения

        Examples:
          python> await viewer.show_profile_list(profiles_list)
          python> # Показан список профилей с кнопками просмотра
        """
        if not self.profile_container:
            return

        self.profile_container.clear()

        if not profiles:
            with self.profile_container:
                ui.label("Профили не найдены").classes("text-center text-muted")
            return

        with self.profile_container:
            ui.label(f"Найдено профилей: {len(profiles)}").classes("text-h6 mb-4")

            for profile in profiles[:10]:  # Показываем до 10 профилей
                with ui.card().classes("w-full mb-2"):
                    with ui.card_section():
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.column():
                                ui.label(profile.get("position", "Неизвестная должность")).classes(
                                    "text-subtitle1 font-medium"
                                )
                                ui.label(profile.get("department", "")).classes("text-caption")
                                ui.label(
                                    f"Создан: {self._format_datetime(profile.get('created_at'))}"
                                ).classes("text-caption text-grey-6")

                            ui.button(
                                "Просмотр",
                                icon="preview",
                                on_click=lambda p=profile: self.show_profile(p)
                            ).props("color=primary")

    def clear_display(self):
        """
        @doc
        Очистка отображения профилей.

        Examples:
          python> viewer.clear_display()
          python> # Контейнер очищен
        """
        if self.profile_container:
            self.profile_container.clear()

        if self.profile_dialog:
            self.profile_dialog.close()
            self.profile_dialog = None

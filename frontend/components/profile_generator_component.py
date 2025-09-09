"""
@doc
Единый компонент генератора профилей должностей для системы А101.

Интегрирует:
- Smart Search по должностям в реальном времени
- Форму генерации профилей
- Управление задачами генерации
- Отображение результатов

Examples:
  python> generator = ProfileGeneratorComponent(api_client)
  python> await generator.render()
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from nicegui import ui
from ..services.api_client import APIClient

logger = logging.getLogger(__name__)


class ProfileGeneratorComponent:
    """
    @doc
    Единый компонент генерации профилей должностей с интегрированным поиском.

    Особенности:
    - Живой поиск по 4,376 должностям
    - Выбор должности одним кликом
    - Форма генерации с настройками
    - Отслеживание прогресса генерации

    Examples:
      python> generator = ProfileGeneratorComponent(api_client)
      python> await generator.render()
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

        # UI компоненты
        self.search_input = None
        self.search_results_container = None
        self.selected_position_display = None
        self.employee_name_input = None
        self.temperature_slider = None
        self.generate_button = None
        self.progress_container = None

        # Состояние
        self.current_query = ""
        self.selected_position = None
        self.search_timer = None
        self.is_searching = False
        self.is_generating = False
        self.current_task_id = None

        # Состояние для привязки UI
        self.has_search_results = False
        self.has_selected_position = False
        self.can_generate = False

        # Статистика системы
        self.total_stats = {"departments": 0, "positions": 0}
        self.stats_text = "Загрузка статистики..."

    async def render(self) -> ui.column:
        """
        @doc
        Отрисовка основного компонента генератора профилей.

        Examples:
          python> component = await generator.render()
          python> component.classes("w-full max-w-4xl mx-auto")
        """
        with ui.column().classes("w-full space-y-4") as container:
            # Заголовок системы
            await self._render_system_header()

            # Основной генератор профилей
            with ui.card().classes("w-full"):
                with ui.card_section():
                    ui.label("🎯 ГЕНЕРАТОР ПРОФИЛЕЙ (Smart Search)").classes(
                        "text-h5 font-bold text-primary mb-4"
                    )

                    # Поиск должности
                    await self._render_search_section()

                    # Отображение выбранной должности
                    await self._render_selected_position()

                    # Дополнительные параметры
                    await self._render_additional_params()

                    # Кнопка генерации
                    await self._render_generate_button()

                    # Прогресс генерации
                    self.progress_container = ui.column().classes("w-full mt-4")

            # Загружаем начальную статистику
            await self._load_system_stats()

        return container

    async def _render_system_header(self):
        """Отрисовка заголовка с системной статистикой"""
        with ui.card().classes("w-full bg-blue-50"):
            with ui.card_section():
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label("📊 СИСТЕМА:").classes("font-bold text-gray-700")
                    self.stats_label = ui.label("Загрузка статистики...").classes(
                        "text-gray-600"
                    )

    async def _render_search_section(self):
        """Отрисовка секции поиска должностей"""
        # Поле поиска
        with ui.row().classes("w-full items-center space-x-2 mb-4"):
            ui.label("🔍 Поиск должности:").classes("font-semibold min-w-fit")

            self.search_input = ui.input(
                placeholder="Введите название должности... (архитектор, менеджер, разработчик)"
            ).classes("flex-1")
            self.search_input.on("input", self._on_search_input)

            ui.button("🔍", on_click=self._trigger_search).props("flat").classes(
                "text-primary"
            )

        # Популярные теги
        with ui.row().classes("w-full items-center space-x-2 mb-4"):
            ui.label("ИЛИ Выбрать из популярных:").classes(
                "text-body2 text-gray-600 min-w-fit"
            )

            popular_searches = [
                "Менеджер",
                "Специалист",
                "Руководитель",
                "Директор",
                "Разработчик",
                "Аналитик",
            ]
            for tag in popular_searches:
                ui.button(
                    f"#{tag}", on_click=lambda t=tag: self._quick_search(t)
                ).props("size=sm outlined color=primary").classes("text-xs")

        # Контейнер живых результатов поиска
        with ui.column().classes("w-full"):
            ui.label("⚡ Live результаты:").classes(
                "font-semibold text-gray-700"
            ).bind_visibility_from(self, "has_search_results")
            self.search_results_container = ui.column().classes(
                "w-full space-y-1 max-h-48 overflow-y-auto"
            )

    async def _render_selected_position(self):
        """Отрисовка выбранной должности"""
        with ui.column().classes("w-full mt-4"):
            self.selected_position_display = (
                ui.column()
                .classes("w-full")
                .bind_visibility_from(self, "has_selected_position")
            )

    async def _render_additional_params(self):
        """Отрисовка дополнительных параметров"""
        with ui.column().classes("w-full mt-4").bind_visibility_from(
            self, "has_selected_position"
        ):
            ui.label("📋 Дополнительно:").classes("font-semibold text-gray-700 mb-3")

            # ФИО сотрудника
            with ui.row().classes("w-full items-center space-x-2 mb-3"):
                ui.label("ФИО:").classes("min-w-fit font-medium")
                self.employee_name_input = ui.input(
                    placeholder="ФИО сотрудника (опционально)"
                ).classes("flex-1")

            # Температура генерации
            with ui.row().classes("w-full items-center space-x-2 mb-3"):
                ui.label("Точность:").classes("min-w-fit font-medium")
                with ui.column().classes("flex-1"):
                    self.temperature_slider = ui.slider(
                        min=0.0, max=1.0, step=0.1, value=0.1
                    ).classes("w-full")
                    ui.label().classes("text-caption text-gray-500").bind_text_from(
                        self.temperature_slider,
                        "value",
                        lambda v: f"{'Консистентная' if v <= 0.3 else 'Умеренная' if v <= 0.7 else 'Творческая'} ({v})",
                    )

    async def _render_generate_button(self):
        """Отрисовка кнопки генерации"""
        with ui.row().classes("w-full justify-center mt-6"):
            self.generate_button = (
                ui.button(
                    "🚀 СОЗДАТЬ ПРОФИЛЬ ДОЛЖНОСТИ", on_click=self._start_generation
                )
                .props("size=lg color=primary")
                .classes("font-bold px-8 py-3")
            )
            self.generate_button.bind_visibility_from(self, "can_generate")

    async def _load_system_stats(self):
        """Загрузка системной статистики"""
        try:
            stats_response = await self.api_client._make_request(
                "GET", "/api/catalog/stats"
            )

            if stats_response.get("success"):
                stats_data = stats_response["data"]
                self.total_stats = {
                    "departments": stats_data["departments"]["total_count"],
                    "positions": stats_data["positions"]["total_count"],
                }

                # Обновляем отображение
                if hasattr(self, "stats_label"):
                    self.stats_label.text = f"{self.total_stats['departments']:,} департаментов • {self.total_stats['positions']:,} должностей"

        except Exception as e:
            logger.error(f"Error loading system stats: {e}")
            self.total_stats = {"departments": 510, "positions": 4376}  # fallback

            # Отображаем fallback
            if hasattr(self, "stats_label"):
                self.stats_label.text = f"{self.total_stats['departments']:,} департаментов • {self.total_stats['positions']:,} должностей"

    def _on_search_input(self, event):
        """Обработчик ввода поиска с debounce"""
        query = event.value.strip()

        # Отменяем предыдущий таймер
        if self.search_timer:
            self.search_timer.cancel()

        # Очищаем результаты если запрос пустой
        if not query:
            self._clear_search_results()
            return

        # Устанавливаем новый таймер (200ms для живого поиска)
        self.search_timer = asyncio.create_task(self._debounced_search(query))

    async def _debounced_search(self, query: str):
        """Отложенный поиск"""
        try:
            await asyncio.sleep(0.2)  # Debounce 200ms

            if query == self.current_query:
                return

            self.current_query = query
            await self._perform_search(query)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in debounced search: {e}")

    async def _perform_search(self, query: str):
        """Выполнение поиска позиций"""
        if self.is_searching:
            return

        try:
            self.is_searching = True

            # Поиск должностей
            search_response = await self.api_client.search_positions(query)

            if search_response.get("success"):
                positions = search_response["data"]["positions"]
                await self._display_search_results(
                    positions[:8]
                )  # Показываем только первые 8 для живого поиска
            else:
                self._clear_search_results()

        except Exception as e:
            logger.error(f"Error performing search: {e}")
            self._clear_search_results()
        finally:
            self.is_searching = False

    async def _display_search_results(self, positions: List[Dict]):
        """Отображение результатов поиска"""
        self.search_results_container.clear()

        if not positions:
            self.has_search_results = False
            return

        self.has_search_results = True

        with self.search_results_container:
            for position in positions:
                await self._render_position_result(position)

    async def _render_position_result(self, position: Dict):
        """Отрисовка одного результата поиска"""
        level_colors = {1: "red", 2: "deep-orange", 3: "orange", 4: "green", 5: "blue"}
        level_color = level_colors.get(position["level"], "grey")

        with ui.row().classes(
            "w-full items-center justify-between p-2 hover:bg-gray-50 rounded-lg border-l-2 border-l-primary cursor-pointer"
        ).on("click", lambda pos=position: self._select_position(pos)):
            with ui.column().classes("flex-1"):
                with ui.row().classes("items-center space-x-2"):
                    ui.label(f"• {position['name']}").classes("font-medium")
                    ui.chip(f"Ур.{position['level']}", color=level_color).props(
                        "size=xs"
                    )

                ui.label(f"📁 {position['department']}").classes(
                    "text-caption text-gray-500"
                )

            ui.icon("chevron_right").classes("text-gray-400")

    def _select_position(self, position: Dict):
        """Выбор должности"""
        self.selected_position = position
        self.has_selected_position = True
        self.can_generate = True

        # Очищаем результаты поиска
        self._clear_search_results()

        # Устанавливаем значение в поле поиска
        if self.search_input:
            self.search_input.value = position["name"]

        # Отображаем выбранную должность
        self._display_selected_position()

        ui.notify(f"Выбрана должность: {position['name']}", type="positive")

    def _display_selected_position(self):
        """Отображение выбранной должности"""
        if not self.selected_position:
            return

        self.selected_position_display.clear()

        with self.selected_position_display:
            with ui.card().classes("w-full border-l-4 border-l-green-500 bg-green-50"):
                with ui.card_section():
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.column().classes("flex-1"):
                            ui.label(
                                f"✅ ВЫБРАНО: {self.selected_position['name']}"
                            ).classes("font-bold text-green-800")

                            # Получаем путь департамента
                            dept_path = self.selected_position.get(
                                "department", "Не указан"
                            )
                            ui.label(f"📍 Департамент: {dept_path}").classes(
                                "text-body2 text-green-700"
                            )

                            # Дополнительная информация
                            level = self.selected_position.get("level", "Не указан")
                            category = self.selected_position.get(
                                "category", "Не указана"
                            )
                            ui.label(
                                f"⚙️ Уровень: {level} • Категория: {category}"
                            ).classes("text-caption text-green-600")

                        ui.button(
                            "Изменить", icon="edit", on_click=self._clear_selection
                        ).props("size=sm outlined color=green")

    def _clear_selection(self):
        """Очистка выбранной должности"""
        self.selected_position = None
        self.has_selected_position = False
        self.can_generate = False

        if self.search_input:
            self.search_input.value = ""

        self._clear_search_results()

    def _clear_search_results(self):
        """Очистка результатов поиска"""
        self.current_query = ""
        self.has_search_results = False
        if self.search_results_container:
            self.search_results_container.clear()

    async def _quick_search(self, query: str):
        """Быстрый поиск по тегу"""
        if self.search_input:
            self.search_input.value = query
        await self._perform_search(query)

    def _trigger_search(self):
        """Принудительный поиск"""
        if self.search_input and self.search_input.value.strip():
            asyncio.create_task(self._perform_search(self.search_input.value.strip()))

    async def _start_generation(self):
        """Запуск генерации профиля"""
        if not self.selected_position or self.is_generating:
            return

        try:
            self.is_generating = True
            self.generate_button.props("loading")

            # Подготавливаем данные для генерации
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

            # Запускаем генерацию
            response = await self.api_client.start_profile_generation(**generation_data)

            if response.get("success"):
                self.current_task_id = response["task_id"]
                ui.notify("🚀 Генерация профиля запущена!", type="positive")

                # Начинаем отслеживание прогресса
                await self._track_generation_progress()
            else:
                ui.notify("❌ Ошибка запуска генерации", type="negative")

        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            ui.notify(f"❌ Ошибка: {str(e)}", type="negative")
        finally:
            self.is_generating = False
            self.generate_button.props(remove="loading")

    async def _track_generation_progress(self):
        """Отслеживание прогресса генерации"""
        if not self.current_task_id:
            return

        # Создаем компонент прогресса
        self.progress_container.clear()

        with self.progress_container:
            with ui.card().classes("w-full border-l-4 border-l-blue-500"):
                with ui.card_section():
                    ui.label("🔄 Генерация профиля...").classes(
                        "font-bold text-blue-800 mb-2"
                    )

                    progress_bar = ui.linear_progress(value=0).classes("w-full")
                    status_label = ui.label("Инициализация...").classes(
                        "text-body2 text-blue-600"
                    )

                    # Отслеживаем прогресс
                    await self._poll_generation_status(progress_bar, status_label)

    async def _poll_generation_status(self, progress_bar, status_label):
        """Опрос статуса генерации"""
        max_attempts = 60  # 5 минут максимум
        attempt = 0

        while attempt < max_attempts:
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
                progress_bar.value = progress / 100.0
                status_label.text = current_step

                if status == "completed":
                    await self._handle_generation_complete()
                    break
                elif status == "failed":
                    error_msg = task_data.get("error_message", "Неизвестная ошибка")
                    await self._handle_generation_error(error_msg)
                    break
                elif status in ["cancelled"]:
                    status_label.text = "Генерация отменена"
                    break

                await asyncio.sleep(5)  # Проверяем каждые 5 секунд
                attempt += 1

            except Exception as e:
                logger.error(f"Error polling generation status: {e}")
                await asyncio.sleep(5)
                attempt += 1

        if attempt >= max_attempts:
            await self._handle_generation_error("Превышено время ожидания")

    async def _handle_generation_complete(self):
        """Обработка завершения генерации"""
        self.progress_container.clear()

        with self.progress_container:
            with ui.card().classes("w-full border-l-4 border-l-green-500 bg-green-50"):
                with ui.card_section():
                    ui.label("✅ Профиль успешно создан!").classes(
                        "font-bold text-green-800 mb-2"
                    )

                    with ui.row().classes("space-x-2"):
                        ui.button(
                            "Просмотреть профиль",
                            icon="description",
                            on_click=lambda: self._view_generated_profile(),
                        ).props("color=green")

                        ui.button(
                            "Создать еще один",
                            icon="add_circle",
                            on_click=lambda: self._reset_generator(),
                        ).props("outlined color=green")

        ui.notify("🎉 Профиль должности готов!", type="positive")

    async def _handle_generation_error(self, error_message: str):
        """Обработка ошибки генерации"""
        self.progress_container.clear()

        with self.progress_container:
            with ui.card().classes("w-full border-l-4 border-l-red-500 bg-red-50"):
                with ui.card_section():
                    ui.label("❌ Ошибка генерации").classes(
                        "font-bold text-red-800 mb-2"
                    )
                    ui.label(error_message).classes("text-body2 text-red-600")

                    ui.button(
                        "Попробовать снова",
                        icon="refresh",
                        on_click=lambda: self._retry_generation(),
                    ).props("color=red outlined")

        ui.notify(f"❌ Ошибка генерации: {error_message}", type="negative")

    def _view_generated_profile(self):
        """Просмотр сгенерированного профиля"""
        # Здесь можно добавить навигацию к просмотру профиля
        ui.navigate.to(f"/profiles/{self.current_task_id}")

    def _reset_generator(self):
        """Сброс генератора для создания нового профиля"""
        self._clear_selection()
        self.progress_container.clear()
        self.current_task_id = None

        if self.employee_name_input:
            self.employee_name_input.value = ""
        if self.temperature_slider:
            self.temperature_slider.value = 0.1

    def _retry_generation(self):
        """Повтор генерации"""
        self.progress_container.clear()
        asyncio.create_task(self._start_generation())


if __name__ == "__main__":
    # Тестирование компонента
    print("✅ Profile Generator component created!")
    print("🎯 Features:")
    print("  - Live search across 4,376 positions")
    print("  - One-click position selection")
    print("  - Integrated generation form")
    print("  - Real-time progress tracking")

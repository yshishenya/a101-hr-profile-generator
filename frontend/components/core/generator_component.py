"""
@doc
GeneratorComponent - Компонент генерации профилей должностей для A101 HR Profile Generator.

Единственная ответственность: управление процессом генерации профилей LLM.
Обрабатывает запуск генерации, отслеживание прогресса, отображение результатов и ошибок.

События:
- on_generation_complete(profile_data) - генерация успешно завершена
- on_generation_error(error_message) - произошла ошибка генерации

Examples:
  python> generator = GeneratorComponent(api_client)
  python> generator.on_generation_complete = viewer.show_profile
  python> await generator.render_generator_section()
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable

from nicegui import ui

logger = logging.getLogger(__name__)


class GeneratorComponent:
    """
    @doc
    Компонент генерации профилей должностей с LLM.

    Особенности:
    - Асинхронная генерация через OpenRouter API + Gemini 2.5 Flash
    - Real-time отслеживание прогресса генерации
    - Professional UI с прогресс-барами и спиннерами
    - Retry logic при ошибках генерации
    - События для интеграции с другими компонентами

    Examples:
      python> generator = GeneratorComponent(api_client)
      python> generator.on_generation_complete = lambda data: print("Done!")
      python> container = await generator.render_generator_section()
    """

    def __init__(self, api_client):
        """
        @doc
        Инициализация компонента генерации профилей.

        Args:
            api_client: Экземпляр APIClient для взаимодействия с backend

        Examples:
          python> generator = GeneratorComponent(api_client)
          python> # Компонент готов к использованию
        """
        self.api_client = api_client

        # UI компоненты
        self.generate_button = None
        self.progress_dialog = None
        self.generation_status_container = None

        # Состояние генерации
        self.is_generating = False
        self.current_task_id = None
        self.selected_position = ""
        self.selected_department = ""

        # События для интеграции с другими компонентами
        self.on_generation_complete: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_generation_error: Optional[Callable[[str], None]] = None

    def set_position(self, position: str, department: str):
        """
        @doc
        Установка выбранной позиции для генерации.

        Вызывается SearchComponent при выборе должности.

        Args:
            position: Название позиции
            department: Название департамента

        Examples:
          python> generator.set_position("Java-разработчик", "ДИТ")
          python> # Позиция установлена для генерации
        """
        self.selected_position = position
        self.selected_department = department
        
        # Обновляем UI состояние кнопки генерации
        self._update_generation_ui_state()
        
        logger.info(f"Generator received position: {position} in {department}")

    async def render_generator_section(self) -> ui.column:
        """
        @doc
        Рендеринг секции генерации профилей.

        Returns:
            ui.column: Контейнер с секцией генерации

        Examples:
          python> container = await generator.render_generator_section()
          python> # Секция генерации отрендерена
        """
        with ui.column().classes("w-full gap-4") as generator_container:
            # Заголовок секции
            with ui.row().classes("w-full items-center gap-3"):
                ui.icon("auto_awesome", size="1.5rem").classes("text-primary")
                ui.label("Генерация профиля").classes(
                    "text-h6 text-weight-medium text-primary"
                )

            # Кнопка генерации
            self.generate_button = ui.button(
                "🚀 Сгенерировать профиль",
                icon="auto_awesome",
                on_click=self._start_generation,
            ).classes("w-full").props("size=lg color=primary")
            
            # Изначально кнопка отключена до выбора позиции
            self.generate_button.props("disable")

            # Контейнер для статуса генерации
            self.generation_status_container = ui.column().classes("w-full")

        return generator_container

    def _update_generation_ui_state(self):
        """
        @doc
        Обновление состояния UI кнопки генерации.

        Включает/отключает кнопку в зависимости от наличия выбранной позиции.

        Examples:
          python> generator._update_generation_ui_state()
          python> # UI обновлен в соответствии с текущим состоянием
        """
        if self.generate_button:
            has_position = bool(self.selected_position and self.selected_department)
            
            if has_position and not self.is_generating:
                self.generate_button.props(remove="disable")
                self.generate_button.set_text(f"🚀 Сгенерировать профиль: {self.selected_position}")
            else:
                self.generate_button.props(add="disable")
                if self.is_generating:
                    self.generate_button.set_text("⏳ Генерация...")
                else:
                    self.generate_button.set_text("🚀 Сгенерировать профиль")

    async def _start_generation(self):
        """
        @doc
        Запуск генерации профиля должности.

        Отправляет запрос на backend для генерации через LLM и показывает прогресс.

        Examples:
          python> await generator._start_generation()
          python> # Генерация запущена, показан прогресс-диалог
        """
        if (
            not self.selected_position
            or not self.selected_department
            or self.is_generating
        ):
            ui.notify("❌ Выберите позицию для генерации", type="warning")
            return

        try:
            self.is_generating = True
            if self.generate_button:
                self.generate_button.props(add="loading")
            self._update_generation_ui_state()

            # Подготовка данных для генерации
            generation_data = {
                "department": self.selected_department,
                "position": self.selected_position,
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
                await self._show_generation_error(error_msg)

        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            await self._show_generation_error(f"Ошибка запуска: {str(e)}")
        finally:
            self.is_generating = False
            if self.generate_button:
                self.generate_button.props(remove="loading")
            self._update_generation_ui_state()

    async def _show_generation_progress(self):
        """
        @doc
        Отображение прогресса генерации в диалоге.

        Показывает прогресс-бар, статус и кнопку отмены генерации.

        Examples:
          python> await generator._show_generation_progress()
          python> # Показан диалог с прогрессом генерации
        """
        with ui.dialog() as dialog:
            dialog.on('close', self._cancel_generation)
            
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

                    # Информация о позиции
                    with ui.row().classes("w-full mb-4"):
                        ui.label(f"Позиция: {self.selected_position}").classes("text-sm")
                    with ui.row().classes("w-full mb-4"):
                        ui.label(f"Департамент: {self.selected_department}").classes("text-sm")

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

        self.progress_dialog = dialog
        dialog.open()

        # Отслеживание прогресса
        await self._poll_generation_status(
            dialog, progress_status, progress_bar, progress_percentage
        )

    async def _poll_generation_status(
        self, dialog, status_label, progress_bar, progress_percentage
    ):
        """
        @doc
        Опрос статуса генерации каждые 5 секунд.

        Обновляет прогресс-бар и статус до завершения генерации.

        Args:
            dialog: Диалог прогресса
            status_label: Лейбл текущего статуса
            progress_bar: Прогресс-бар
            progress_percentage: Лейбл процентов

        Examples:
          python> await generator._poll_generation_status(dialog, status, bar, pct)
          python> # Статус отслеживается до завершения
        """
        max_attempts = 60  # 5 минут максимум
        attempt = 0

        while attempt < max_attempts and dialog.value:  # Проверяем, что диалог не закрыт
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
        """
        @doc
        Отображение успешного завершения генерации.

        Показывает диалог успеха с действиями для просмотра результата.

        Examples:
          python> await generator._show_generation_success()
          python> # Показан диалог успешной генерации
        """
        # Получаем результат генерации
        result_response = await self.api_client.get_generation_task_result(self.current_task_id)
        
        with ui.dialog() as dialog:
            with ui.card().classes("text-center p-6"):
                with ui.card_section().classes("text-center py-8"):
                    # Иконка успеха
                    ui.icon("check_circle", size="4rem").classes("text-success mb-4")

                    # Заголовок
                    ui.label("🎉 Профиль успешно создан!").classes(
                        "text-2xl font-bold text-success mb-2"
                    )
                    ui.label(f"Профиль должности '{self.selected_position}' готов для использования").classes(
                        "text-muted mb-6"
                    )

                    # Действия
                    with ui.row().classes("gap-3 justify-center"):
                        ui.button(
                            "Просмотреть профиль",
                            icon="description",
                            on_click=lambda: self._view_profile_result(result_response, dialog),
                        ).props("color=primary")

                        ui.button(
                            "Создать еще один",
                            icon="add",
                            on_click=lambda: self._create_another(dialog),
                        ).props("outlined")

        dialog.open()
        
        # Вызываем событие для других компонентов
        if self.on_generation_complete and result_response:
            self.on_generation_complete(result_response)

        ui.notify("✅ Профиль успешно сгенерирован!", type="positive", position="top")

    async def _show_generation_error(self, error_message: str):
        """
        @doc
        Отображение ошибки генерации.

        Показывает диалог ошибки с возможностью повтора генерации.

        Args:
            error_message: Сообщение об ошибке

        Examples:
          python> await generator._show_generation_error("Timeout error")
          python> # Показан диалог ошибки с кнопкой повтора
        """
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
        
        # Вызываем событие для других компонентов
        if self.on_generation_error:
            self.on_generation_error(error_message)

        ui.notify(f"❌ {error_message}", type="negative", position="top")

    def _view_profile_result(self, result, dialog):
        """
        @doc
        Просмотр результата сгенерированного профиля.

        Args:
            result: Данные профиля из API
            dialog: Диалог для закрытия

        Examples:
          python> generator._view_profile_result(result, dialog)
          python> # Результат передан компоненту просмотра
        """
        dialog.close()
        
        # Вызываем событие для компонента просмотра профилей
        if self.on_generation_complete and result:
            self.on_generation_complete(result)

    def _create_another(self, dialog):
        """
        @doc
        Создание еще одного профиля.

        Закрывает диалог успеха и сбрасывает состояние генератора.

        Args:
            dialog: Диалог для закрытия

        Examples:
          python> generator._create_another(dialog)
          python> # Генератор готов к новой генерации
        """
        dialog.close()
        self._reset_generator()

    def _retry_generation(self, dialog):
        """
        @doc
        Повтор генерации после ошибки.

        Args:
            dialog: Диалог ошибки для закрытия

        Examples:
          python> generator._retry_generation(dialog)
          python> # Запущен повтор генерации
        """
        dialog.close()
        asyncio.create_task(self._start_generation())

    def _reset_generator(self):
        """
        @doc
        Сброс состояния генератора.

        Очищает выбранную позицию и статус генерации.

        Examples:
          python> generator._reset_generator()
          python> # Генератор сброшен к начальному состоянию
        """
        self.selected_position = ""
        self.selected_department = ""
        self.current_task_id = None
        self.is_generating = False
        
        # Обновляем UI
        self._update_generation_ui_state()
        
        # Очищаем контейнер статуса
        if self.generation_status_container:
            self.generation_status_container.clear()
        
        ui.notify("🔄 Генератор сброшен", type="info")

    def _cancel_generation(self):
        """
        @doc
        Отмена текущей генерации.

        Закрывает диалог прогресса и отменяет задачу на backend.

        Examples:
          python> generator._cancel_generation()
          python> # Генерация отменена
        """
        if self.progress_dialog:
            self.progress_dialog.close()
            
        if self.current_task_id:
            # Асинхронно отменяем задачу на backend
            asyncio.create_task(self._cancel_backend_task())
            
        self.current_task_id = None
        self.is_generating = False
        self._update_generation_ui_state()
        
        ui.notify("Генерация отменена", type="warning")

    async def _cancel_backend_task(self):
        """
        @doc
        Отмена задачи на backend.

        Отправляет запрос отмены текущей задачи генерации.

        Examples:
          python> await generator._cancel_backend_task()
          python> # Задача отменена на backend
        """
        if self.current_task_id:
            try:
                await self.api_client.cancel_generation_task(self.current_task_id)
                logger.info(f"Cancelled generation task: {self.current_task_id}")
            except Exception as e:
                logger.error(f"Error cancelling generation task: {e}")

    def get_generation_status(self) -> Dict[str, Any]:
        """
        @doc
        Получение текущего статуса генерации.

        Returns:
            Dict[str, Any]: Статус генерации

        Examples:
          python> status = generator.get_generation_status()
          python> print(status["is_generating"])  # True/False
        """
        return {
            "is_generating": self.is_generating,
            "task_id": self.current_task_id,
            "selected_position": self.selected_position,
            "selected_department": self.selected_department,
        }
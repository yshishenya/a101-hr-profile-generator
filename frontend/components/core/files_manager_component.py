"""
@doc
FilesManagerComponent - Компонент управления файлами профилей для A101 HR Profile Generator.

Единственная ответственность: скачивание файлов профилей через чистый API слой.
Убирает прямые HTTP запросы из UI компонентов, обеспечивая правильную архитектуру.

Поддерживаемые форматы:
- JSON (полные данные профиля)
- Markdown (отформатированный документ)

Examples:
  python> files_manager = FilesManagerComponent(api_client)
  python> await files_manager.download_file("profile123", "json")
"""

import asyncio
import logging
import tempfile
import os
import threading
from typing import Dict, Any, Optional

from nicegui import ui

logger = logging.getLogger(__name__)


class FilesManagerComponent:
    """
    @doc
    Компонент управления скачиванием файлов профилей.

    Особенности:
    - Чистая архитектура: UI → Services → API (никаких прямых HTTP запросов)
    - Автоматическая очистка временных файлов
    - Progress indication для пользователя
    - Error handling и retry logic
    - Поддержка JSON и Markdown форматов

    Examples:
      python> files_manager = FilesManagerComponent(api_client)
      python> await files_manager.download_file("profile123", "json")
      python> # Файл скачан через browser download
    """

    def __init__(self, api_client):
        """
        @doc
        Инициализация компонента управления файлами.

        Args:
            api_client: Экземпляр APIClient для взаимодействия с backend

        Examples:
          python> files_manager = FilesManagerComponent(api_client)
          python> # Компонент готов к использованию
        """
        self.api_client = api_client

        # UI компоненты
        self.download_progress_dialog = None

        # Временные файлы для очистки
        self.temp_files = set()

    async def render_files_section(self) -> ui.column:
        """
        @doc
        Рендеринг секции управления файлами.

        Returns:
            ui.column: Контейнер с секцией управления файлами

        Examples:
          python> container = await files_manager.render_files_section()
          python> # Секция управления файлами отрендерена
        """
        with ui.column().classes("w-full gap-4") as files_container:
            # Заголовок секции
            with ui.row().classes("w-full items-center gap-3"):
                ui.icon("folder_open", size="1.5rem").classes("text-primary")
                ui.label("Управление файлами").classes(
                    "text-h6 text-weight-medium text-primary"
                )

            # Информация о поддерживаемых форматах
            with ui.card().classes("w-full"):
                with ui.card_section():
                    ui.label("📋 Поддерживаемые форматы:").classes("text-subtitle2 mb-2")
                    with ui.column().classes("gap-1"):
                        ui.label("• JSON - полные данные профиля для анализа").classes("text-body2")
                        ui.label("• Markdown - отформатированный документ для печати").classes("text-body2")

        return files_container

    async def download_file(self, profile_id: str, format_type: str):
        """
        @doc
        Скачивание файла профиля в указанном формате.

        Args:
            profile_id: ID профиля для скачивания
            format_type: Формат файла ("json" или "markdown")

        Examples:
          python> await files_manager.download_file("profile123", "json")
          python> # JSON файл скачан через browser download
        """
        if not profile_id:
            ui.notify("❌ Нет ID профиля для скачивания", type="negative")
            return

        if format_type not in ["json", "markdown"]:
            ui.notify(f"❌ Неподдерживаемый формат: {format_type}", type="negative")
            return

        try:
            # Показываем прогресс
            self._show_download_progress(profile_id, format_type)

            # Скачиваем через API (чистая архитектура)
            if format_type == "json":
                file_data = await self.api_client.download_profile_json(profile_id)
                file_extension = "json"
                content_type = "application/json"
            else:  # markdown
                file_data = await self.api_client.download_profile_markdown(profile_id)
                file_extension = "md"
                content_type = "text/markdown"

            # Закрываем диалог прогресса
            self._hide_download_progress()

            # Создаем временный файл
            temp_path = await self._create_temp_file(
                file_data, profile_id, file_extension
            )

            # Скачиваем через NiceGUI
            filename = f"profile_{profile_id[:8]}.{file_extension}"
            ui.download(temp_path, filename)

            # Планируем очистку временного файла
            self._schedule_cleanup(temp_path)

            ui.notify(
                f"✅ {format_type.upper()} файл скачан: {filename}",
                type="positive"
            )

            logger.info(f"File download completed: {filename} for profile {profile_id}")

        except Exception as e:
            self._hide_download_progress()
            logger.error(f"Error downloading {format_type} file: {e}")
            ui.notify(
                f"❌ Ошибка скачивания {format_type}: {str(e)}",
                type="negative"
            )

    def _show_download_progress(self, profile_id: str, format_type: str):
        """
        @doc
        Отображение прогресса скачивания.

        Args:
            profile_id: ID скачиваемого профиля
            format_type: Тип файла

        Examples:
          python> files_manager._show_download_progress("profile123", "json")
          python> # Показан диалог прогресса скачивания
        """
        if self.download_progress_dialog:
            return  # Уже показан

        with ui.dialog() as dialog:
            with ui.card():
                with ui.card_section().classes("py-6 px-8 text-center"):
                    ui.spinner(size="lg", color="primary")
                    ui.label(f"📥 Скачивание {format_type.upper()} файла...").classes(
                        "text-lg font-semibold text-primary mt-3"
                    )
                    ui.label(f"Профиль: {profile_id[:12]}...").classes(
                        "text-sm text-muted mt-2"
                    )

        self.download_progress_dialog = dialog
        dialog.open()

    def _hide_download_progress(self):
        """
        @doc
        Скрытие диалога прогресса скачивания.

        Examples:
          python> files_manager._hide_download_progress()
          python> # Диалог прогресса скрыт
        """
        if self.download_progress_dialog:
            self.download_progress_dialog.close()
            self.download_progress_dialog = None

    async def _create_temp_file(self, file_data: bytes, profile_id: str, extension: str) -> str:
        """
        @doc
        Создание временного файла для скачивания.

        Args:
            file_data: Данные файла
            profile_id: ID профиля
            extension: Расширение файла

        Returns:
            str: Путь к временному файлу

        Examples:
          python> path = await files_manager._create_temp_file(data, "123", "json")
          python> print(path)  # "/tmp/tmp123.json"
        """
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=f"_{profile_id[:8]}.{extension}",
                delete=False
            ) as tmp_file:
                tmp_file.write(file_data)
                temp_path = tmp_file.name

            # Добавляем в список для отслеживания
            self.temp_files.add(temp_path)

            logger.info(f"Created temp file: {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"Error creating temp file: {e}")
            raise

    def _schedule_cleanup(self, temp_path: str, delay: int = 60):
        """
        @doc
        Планирование очистки временного файла.

        Args:
            temp_path: Путь к временному файлу
            delay: Задержка в секундах до удаления

        Examples:
          python> files_manager._schedule_cleanup("/tmp/file.json", 30)
          python> # Файл будет удален через 30 секунд
        """
        def cleanup():
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info(f"Cleaned up temp file: {temp_path}")
                
                # Убираем из отслеживания
                self.temp_files.discard(temp_path)
                
            except Exception as e:
                logger.error(f"Error cleaning up temp file {temp_path}: {e}")

        # Планируем удаление через указанную задержку
        threading.Timer(delay, cleanup).start()

    async def download_multiple_files(self, profile_ids: list[str], format_type: str):
        """
        @doc
        Скачивание нескольких файлов профилей.

        Args:
            profile_ids: Список ID профилей
            format_type: Формат файлов

        Examples:
          python> await files_manager.download_multiple_files(["123", "456"], "json")
          python> # Несколько JSON файлов скачано
        """
        if not profile_ids:
            ui.notify("❌ Нет профилей для скачивания", type="negative")
            return

        ui.notify(f"📥 Начинается скачивание {len(profile_ids)} файлов...", type="info")

        success_count = 0
        for i, profile_id in enumerate(profile_ids, 1):
            try:
                ui.notify(f"📥 Скачивание {i}/{len(profile_ids)}: {profile_id[:8]}...", type="info")
                await self.download_file(profile_id, format_type)
                success_count += 1
                
                # Небольшая пауза между скачиваниями
                if i < len(profile_ids):
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error downloading file {profile_id}: {e}")
                ui.notify(f"❌ Ошибка скачивания {profile_id[:8]}: {str(e)}", type="negative")

        # Итоговое уведомление
        if success_count == len(profile_ids):
            ui.notify(f"✅ Все {success_count} файлов успешно скачаны", type="positive")
        else:
            ui.notify(
                f"⚠️ Скачано {success_count} из {len(profile_ids)} файлов",
                type="warning"
            )

    async def preview_markdown(self, profile_id: str):
        """
        @doc
        Предпросмотр Markdown файла профиля.

        Args:
            profile_id: ID профиля для предпросмотра

        Examples:
          python> await files_manager.preview_markdown("profile123")
          python> # Показан диалог с содержимым Markdown
        """
        try:
            ui.notify("📥 Загрузка предпросмотра...", type="info")

            # Скачиваем Markdown через API
            markdown_data = await self.api_client.download_profile_markdown(profile_id)
            markdown_content = markdown_data.decode('utf-8')

            # Показываем в диалоге
            with ui.dialog() as dialog:
                with ui.card().classes("w-[80vw] max-w-4xl max-h-[70vh]"):
                    # Заголовок
                    with ui.card_section().classes("bg-primary text-white"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label(f"📄 Предпросмотр Markdown: {profile_id[:12]}...").classes(
                                "text-h6"
                            )
                            ui.button(icon="close", on_click=dialog.close).props(
                                "flat round text-color=white"
                            )

                    # Содержимое
                    with ui.scroll_area().classes("flex-1 p-6"):
                        # Показываем как код (NiceGUI не рендерит Markdown из строк)
                        ui.code(markdown_content).classes("w-full")

                    # Действия
                    with ui.card_actions():
                        ui.button(
                            "Скачать",
                            icon="download",
                            on_click=lambda: self.download_file(profile_id, "markdown")
                        ).props("color=primary")
                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

            dialog.open()

        except Exception as e:
            logger.error(f"Error previewing markdown: {e}")
            ui.notify(f"❌ Ошибка предпросмотра: {str(e)}", type="negative")

    def cleanup_all_temp_files(self):
        """
        @doc
        Немедленная очистка всех временных файлов.

        Examples:
          python> files_manager.cleanup_all_temp_files()
          python> # Все временные файлы удалены
        """
        cleaned_count = 0
        for temp_path in list(self.temp_files):
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    cleaned_count += 1
                    logger.info(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temp file {temp_path}: {e}")
            finally:
                self.temp_files.discard(temp_path)

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files")

    def get_download_status(self) -> Dict[str, Any]:
        """
        @doc
        Получение статуса компонента скачивания.

        Returns:
            Dict[str, Any]: Статус компонента

        Examples:
          python> status = files_manager.get_download_status()
          python> print(status["temp_files_count"])  # Количество временных файлов
        """
        return {
            "temp_files_count": len(self.temp_files),
            "is_downloading": bool(self.download_progress_dialog),
            "temp_files": list(self.temp_files)
        }
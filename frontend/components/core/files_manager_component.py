"""
@doc
FilesManagerComponent - Компонент управления файлами профилей
для A101 HR Profile Generator.

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
import time
from typing import Dict, Any, Optional

from nicegui import ui

try:
    # Relative imports для запуска как модуль
    try:
        from ...core.error_recovery import (
            ErrorRecoveryCoordinator,
            RetryConfig,
            CircuitBreakerConfig,
            ManagedResource,
        )
    except ImportError:
        # Error recovery is optional - system can work without it
        ErrorRecoveryCoordinator = None
        RetryConfig = None
        CircuitBreakerConfig = None
        ManagedResource = None
except ImportError:
    try:
        # Docker imports с /app в PYTHONPATH
        from frontend.core.error_recovery import (
            ErrorRecoveryCoordinator,
            RetryConfig,
            CircuitBreakerConfig,
            ManagedResource,
        )
    except ImportError:
        # Error recovery is optional - system can work without it
        ErrorRecoveryCoordinator = None
        RetryConfig = None
        CircuitBreakerConfig = None
        ManagedResource = None

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

    def __init__(
        self,
        api_client,
        error_recovery_coordinator: Optional[ErrorRecoveryCoordinator] = None,
    ):
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
        self.error_recovery_coordinator = error_recovery_coordinator

        # UI компоненты
        self.download_progress_dialog = None

        # Временные файлы для очистки
        self.temp_files = set()
        self.managed_resources = set()

        # Download tracking
        self.download_attempts = {}
        self.failed_downloads = set()

        # Error recovery components
        self.circuit_breaker = None
        self.retry_manager = None
        if self.error_recovery_coordinator:
            self.circuit_breaker = self.error_recovery_coordinator.get_circuit_breaker(
                "files_manager_component",
                CircuitBreakerConfig(failure_threshold=2, timeout_seconds=30),
            )
            self.retry_manager = self.error_recovery_coordinator.get_retry_manager(
                "download_retry", RetryConfig(max_retries=2, base_delay=2, max_delay=15)
            )
            # Register recovery callback
            self.error_recovery_coordinator.register_recovery_callback(
                "files_manager_component", self._on_recovery_callback
            )

    def _safe_notify(self, message: str, type_: str = "info"):
        """Safely calls ui.notify() with a fallback to logging."""
        try:
            ui.notify(message, type=type_)
        except RuntimeError:
            # UI недоступен (background task), логируем вместо уведомления
            log_level_map = {
                "positive": logger.info,
                "info": logger.info,
                "warning": logger.warning,
                "negative": logger.error
            }
            log_func = log_level_map.get(type_, logger.info)
            log_func(f"UI Notification: {message}")

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
                    ui.label("📋 Поддерживаемые форматы:").classes(
                        "text-subtitle2 mb-2"
                    )
                    with ui.column().classes("gap-1"):
                        ui.label("• JSON - полные данные профиля для анализа").classes(
                            "text-body2"
                        )
                        ui.label(
                            "• Markdown - отформатированный документ для печати"
                        ).classes("text-body2")

        return files_container

    def download_file(self, profile_id: str, format_type: str):
        """Downloads a profile file in the specified format."""
        if not profile_id:
            logger.warning("No profile ID provided for download")
            self._safe_notify("❌ Не указан ID профиля", "negative")
            return

        if format_type not in ["json", "markdown", "docx"]:
            logger.warning(f"Unsupported format: {format_type}")
            self._safe_notify(f"❌ Неподдерживаемый формат: {format_type}", "negative")
            return

        # Показываем индикатор загрузки
        self._safe_notify("📥 Подготовка файла...", "info")
        logger.info(f"🔍 Starting download: profile_id={profile_id}, format={format_type}")

        # Выполняем синхронно для простоты (файлы небольшие)
        self._download_file_sync(profile_id, format_type)

    def _download_file_sync(self, profile_id: str, format_type: str):
        """def _download_file_sync(self, profile_id: str, format_type: str):
        Synchronously downloads a file by reading it from the filesystem.  This
        function determines the file path based on the provided profile_id  and
        format_type. It reads the file content according to the specified  format
        (json, docx, or markdown) and initiates a download using  ui.download(). If any
        errors occur during file reading or downloading,  appropriate notifications are
        sent, and errors are logged.
        
        Args:
            profile_id: ID профиля для скачивания
            format_type: Формат файла"""
        try:
            # Определяем путь к файлу на основе profile_id
            file_path = self._find_profile_file_sync(profile_id, format_type)

            if not file_path:
                logger.warning(f"Profile file not found: {profile_id} ({format_type})")
                self._safe_notify("❌ Файл профиля не найден", "negative")
                return

            logger.info(f"📁 Found file: {file_path}")

            # Читаем содержимое файла
            try:
                if format_type == "json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    media_type = "application/json"
                    extension = "json"
                elif format_type == "docx":
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    extension = "docx"
                else:  # markdown
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    media_type = "text/markdown"
                    extension = "md"

                logger.info(f"📄 File read successfully: {len(content)} characters/bytes")

            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                self._safe_notify("❌ Ошибка чтения файла", "negative")
                return

            # Генерируем имя файла
            filename = f"profile_{profile_id[:8]}.{extension}"

            # Используем ui.download() для безопасного скачивания
            try:
                if isinstance(content, str):
                    # Для текстовых файлов
                    ui.download(content.encode('utf-8'), filename, media_type=media_type)
                else:
                    # Для бинарных файлов
                    ui.download(content, filename, media_type=media_type)

                logger.info(f"✅ Download initiated: {filename}")
                self._safe_notify(f"✅ Скачивание файла {filename}", "positive")

            except Exception as e:
                logger.error(f"Error initiating ui.download(): {e}")
                self._safe_notify("❌ Ошибка инициализации скачивания", "negative")

        except Exception as e:
            logger.error(f"Error in sync download: {e}")
            self._safe_notify("❌ Произошла ошибка при скачивании", "negative")

    async def _download_file_async(self, profile_id: str, format_type: str):
        """Asynchronously downloads a file by reading it directly from the file system.
        
        This function determines the file path based on the provided profile_id and
        format_type.  It reads the file content according to the specified format,
        handles potential errors during  file reading, and initiates a download using
        ui.download(). Notifications are sent to the user  regarding the success or
        failure of each operation, ensuring a smooth user experience.
        """
        try:
            # Определяем путь к файлу на основе profile_id
            file_path = await self._find_profile_file(profile_id, format_type)

            if not file_path:
                logger.warning(f"Profile file not found: {profile_id} ({format_type})")
                self._safe_notify("❌ Файл профиля не найден", "negative")
                return

            logger.info(f"📁 Found file: {file_path}")

            # Читаем содержимое файла
            try:
                if format_type == "json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    media_type = "application/json"
                    extension = "json"
                elif format_type == "docx":
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    extension = "docx"
                else:  # markdown
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    media_type = "text/markdown"
                    extension = "md"

                logger.info(f"📄 File read successfully: {len(content)} characters/bytes")

            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                self._safe_notify("❌ Ошибка чтения файла", "negative")
                return

            # Генерируем имя файла
            filename = f"profile_{profile_id[:8]}.{extension}"

            # Используем ui.download() для безопасного скачивания
            try:
                if isinstance(content, str):
                    # Для текстовых файлов
                    ui.download(content.encode('utf-8'), filename, media_type=media_type)
                else:
                    # Для бинарных файлов
                    ui.download(content, filename, media_type=media_type)

                logger.info(f"✅ Download initiated: {filename}")
                self._safe_notify(f"✅ Скачивание файла {filename}", "positive")

            except Exception as e:
                logger.error(f"Error initiating ui.download(): {e}")
                self._safe_notify("❌ Ошибка инициализации скачивания", "negative")

        except Exception as e:
            logger.error(f"Error in async download: {e}")
            self._safe_notify("❌ Произошла ошибка при скачивании", "negative")

    async def _find_profile_file(self, profile_id: str, format_type: str) -> Optional[str]:
        """Searches for a profile file in the filesystem by profile_id and format_type.
        
        This function employs two strategies to locate the desired profile file.
        First, it searches for files matching the profile_id in their names using
        various patterns. If no files are found, it attempts to retrieve the last
        selected profile from SearchComponent and performs a fallback search for  any
        file of the specified format type. If successful, it returns the full  path to
        the found file; otherwise, it returns None.
        
        Args:
            profile_id: UUID профиля из базы данных
            format_type: Тип файла для поиска
        """
        import os
        import glob

        # Определяем расширение файла
        extensions = {
            "json": "json",
            "markdown": "md",
            "docx": "docx"
        }
        ext = extensions.get(format_type, format_type)

        logger.info(f"🔍 Searching for profile: {profile_id} ({format_type})")

        # Стратегия 1: Поиск по profile_id в имени файла
        search_patterns = [
            f"generated_profiles/**/*{profile_id}*.{ext}",
            f"generated_profiles/**/*{profile_id[:8]}*.{ext}",
            f"generated_profiles/**/{profile_id}/**/*.{ext}",
            f"generated_profiles/**/{profile_id[:8]}/**/*.{ext}"
        ]

        for pattern in search_patterns:
            try:
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    found_file = matches[0]
                    logger.info(f"📁 Found file by ID pattern {pattern}: {found_file}")
                    if os.path.exists(found_file):
                        return found_file
            except Exception as e:
                logger.warning(f"Error searching with pattern {pattern}: {e}")

        # Стратегия 2: Поиск по текущему профилю из SearchComponent
        try:
            # Пытаемся получить информацию о последнем выбранном профиле
            # из SearchComponent через singleton или общее состояние
            selected_position = getattr(self, '_current_position', None)

            if not selected_position:
                # Пытаемся найти любой файл нужного типа как fallback
                logger.info(f"🔍 Using fallback search for any {ext} files")
                all_files = glob.glob(f"generated_profiles/**/*.{ext}", recursive=True)

                if all_files:
                    # Сортируем по времени модификации (последний созданный)
                    latest_file = max(all_files, key=os.path.getmtime)
                    logger.info(f"📁 Using latest {ext} file: {latest_file}")
                    return latest_file

        except Exception as e:
            logger.warning(f"Error in fallback search: {e}")

        logger.warning(f"No file found for profile_id {profile_id} with extension {ext}")
        return None

    def set_current_position(self, position_name: str):
        """Sets the current position for file searching.
        
        Args:
            position_name: The name of the position for finding corresponding files.
        """
        self._current_position = position_name
        logger.info(f"📋 Set current position: {position_name}")

    def _find_profile_file_sync(self, profile_id: str, format_type: str) -> Optional[str]:
        """
        @doc
        Синхронный поиск файла профиля в файловой системе.

        Args:
            profile_id: UUID профиля из базы данных
            format_type: Тип файла для поиска

        Returns:
            str: Полный путь к файлу или None если не найден
        """
        import os
        import glob

        # Определяем расширение файла
        extensions = {
            "json": "json",
            "markdown": "md",
            "docx": "docx"
        }
        ext = extensions.get(format_type, format_type)

        logger.info(f"🔍 Searching for profile: {profile_id} ({format_type})")
        logger.info(f"🔍 Profile ID parts: full={profile_id}, short={profile_id[:8]}")

        # Стратегия 1: Поиск по profile_id в имени файла (разные варианты)
        search_patterns = [
            f"generated_profiles/**/*{profile_id}*.{ext}",
            f"generated_profiles/**/*{profile_id[:8]}*.{ext}",
            f"generated_profiles/**/{profile_id}/**/*.{ext}",
            f"generated_profiles/**/{profile_id[:8]}/**/*.{ext}",
            # Добавляем поиск по окончанию имени файла (возможно profile_id в конце)
            f"generated_profiles/**/*_{profile_id[:8]}.{ext}",
            f"generated_profiles/**/*_{profile_id}.{ext}"
        ]

        for pattern in search_patterns:
            try:
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    found_file = matches[0]
                    logger.info(f"📁 Found file by ID pattern '{pattern}': {found_file}")
                    if os.path.exists(found_file):
                        return found_file
            except Exception as e:
                logger.warning(f"Error searching with pattern {pattern}: {e}")

        # Стратегия 2: Fallback - найти любой файл нужного типа (последний по времени)
        try:
            logger.info(f"🔍 Using fallback search for any {ext} files")
            all_files = glob.glob(f"generated_profiles/**/*.{ext}", recursive=True)

            if all_files:
                # Сортируем по времени модификации (последний созданный)
                latest_file = max(all_files, key=os.path.getmtime)
                logger.info(f"📁 Using latest {ext} file: {latest_file}")
                logger.info(f"📁 Available files: {[os.path.basename(f) for f in all_files[:5]]}")  # Показываем первые 5
                return latest_file

        except Exception as e:
            logger.warning(f"Error in fallback search: {e}")

        logger.warning(f"No file found for profile_id {profile_id} with extension {ext}")
        return None

    def _download_in_background_safe(self, profile_id: str, format_type: str):

        """Safely downloads a file in a background thread to avoid slot context errors.
        
        Args:
            profile_id: ID профиля для скачивания.
            format_type: Формат файла.
        """
        def run_download():
            """Starts an async download in a separate thread pool."""
            try:
                # Создаем новый event loop для этого thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Запускаем скачивание
                loop.run_until_complete(
                    self._async_download_file(profile_id, format_type)
                )

            except Exception as e:
                logger.error(f"Background download failed: {e}")
            finally:
                loop.close()

        # Запускаем в background thread (НЕ в UI context)
        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()

        logger.info(
            f"Started background download for profile {profile_id} ({format_type})"
        )

    async def _async_download_file(self, profile_id: str, format_type: str):
        """Asynchronously downloads a file without UI notifications."""
        try:
            download_key = f"{profile_id}_{format_type}"
            self.download_attempts[download_key] = (
                self.download_attempts.get(download_key, 0) + 1
            )

            file_data, file_extension = await self._safe_download_file(
                profile_id, format_type
            )

            if not file_data:
                logger.error(f"Failed to download {format_type} file for {profile_id}")
                return

            # Создаем временный файл
            temp_path = await self._create_temp_file(
                file_data, profile_id, file_extension
            )

            # Логируем успешное скачивание
            filename = f"profile_{profile_id[:8]}.{file_extension}"
            logger.info(f"File prepared for download: {filename} at {temp_path}")

            # Планируем очистку временного файла
            self._schedule_cleanup(temp_path)

            logger.info(f"File download completed: {filename} for profile {profile_id}")

        except Exception as e:
            logger.error(f"Error in async download: {e}")

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

    async def _create_temp_file(
        self, file_data: bytes, profile_id: str, extension: str
    ) -> str:
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
                mode="wb", suffix=f"_{profile_id[:8]}.{extension}", delete=False
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
        """Downloads multiple profile files asynchronously.
        
        This function takes a list of profile IDs and a format type to download the
        corresponding files.  It notifies the user about the download progress and
        handles any errors that occur during the  download process. A brief pause is
        introduced between downloads to manage the request rate.  Finally, it provides
        a summary notification indicating the success or failure of the downloads.
        
        Args:
            profile_ids: A list of profile IDs to download.
            format_type: The format of the files to be downloaded.
        """
        if not profile_ids:
            self._safe_notify("❌ Нет профилей для скачивания", "negative")
            return

        self._safe_notify(f"📥 Начинается скачивание {len(profile_ids)} файлов...", "info")

        success_count = 0
        for i, profile_id in enumerate(profile_ids, 1):
            try:
                self._safe_notify(
                    f"📥 Скачивание {i}/{len(profile_ids)}: {profile_id[:8]}...",
                    "info",
                )
                await self.download_file(profile_id, format_type)
                success_count += 1

                # Небольшая пауза между скачиваниями
                if i < len(profile_ids):
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error downloading file {profile_id}: {e}")
                self._safe_notify(
                    f"❌ Ошибка скачивания {profile_id[:8]}: {str(e)}", "negative"
                )

        # Итоговое уведомление
        if success_count == len(profile_ids):
            self._safe_notify(f"✅ Все {success_count} файлов успешно скачаны", "positive")
        else:
            self._safe_notify(
                f"⚠️ Скачано {success_count} из {len(profile_ids)} файлов",
                "warning",
            )

    async def preview_markdown(self, profile_id: str):
        """Displays a preview of the Markdown file for a given profile ID."""
        self._safe_notify("📥 Загрузка предпросмотра...", "info")

        try:
            # Enhanced markdown download with retry protection
            markdown_data, _ = await self._safe_download_file(profile_id, "markdown")

            if not markdown_data:
                await self._handle_download_failure(
                    f"{profile_id}_markdown_preview", "Failed to load markdown preview"
                )
                return

            markdown_content = markdown_data.decode("utf-8")

            # Показываем в диалоге
            with ui.dialog() as dialog:
                with ui.card().classes("w-[80vw] max-w-4xl max-h-[70vh]"):
                    # Заголовок
                    with ui.card_section().classes("bg-primary text-white"):
                        with ui.row().classes("w-full justify-between items-center"):
                            ui.label(
                                f"📄 Предпросмотр Markdown: {profile_id[:12]}..."
                            ).classes("text-h6")
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
                            on_click=lambda: self.download_file(profile_id, "markdown"),
                        ).props("color=primary")
                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

            dialog.open()

        except Exception as e:
            logger.error(f"Error previewing markdown: {e}")
            self._safe_notify(f"❌ Ошибка предпросмотра: {str(e)}", "negative")

    async def cleanup_all_temp_files(self):
        """Clean up all temporary files.
        
        This asynchronous function performs a comprehensive cleanup of all tracked
        temporary files. It iterates through the list of `self.temp_files`, attempting
        to delete each file if it exists, while logging the process. After cleaning  up
        the temporary files, it calls the `_cleanup_managed_resources` method to
        ensure that any associated resources are also cleaned up. Finally, it resets
        the state by clearing `self.download_attempts` and `self.failed_downloads`.
        """
        logger.info("Starting comprehensive temp file cleanup")
        cleaned_count = 0

        # Clean up tracked temp files
        for temp_path in list(self.temp_files):
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    cleaned_count += 1
                    logger.debug(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temp file {temp_path}: {e}")
            finally:
                self.temp_files.discard(temp_path)

        # Clean up managed resources
        await self._cleanup_managed_resources()

        # Reset state
        self.download_attempts.clear()
        self.failed_downloads.clear()

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            self._safe_notify(f"🧹 Очищено {cleaned_count} временных файлов", "info")

    def download_file_sync(self, profile_id: str, format_type: str):
        """
        @doc
        Синхронный wrapper для async download_file метода.

        Создает background task для async операции, совместимо с NiceGUI best practices.
        НЕ создает UI элементы в background task - только выполняет скачивание.

        Args:
            profile_id: ID профиля для скачивания
            format_type: Формат файла ("json" или "markdown")

        Examples:
          python> files_manager.download_file_sync("profile123", "json")
          # Запущено асинхронное скачивание без UI блокировки
        """
        import asyncio
        import threading

        def run_download():
            """Запуск async download в отдельном thread pool."""
            try:
                # Создаем новый event loop для этого thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Запускаем скачивание
                loop.run_until_complete(self.download_file(profile_id, format_type))

            except Exception as e:
                logger.error(f"Background download failed: {e}")
            finally:
                loop.close()

        # Запускаем в background thread (НЕ в UI context)
        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()

        logger.info(
            f"Started background download for profile {profile_id} ({format_type})"
        )

    # === Error Recovery and Resource Management Methods ===

    async def _safe_download_file(self, profile_id: str, format_type: str):
        """Download a file with error recovery and retry protection.
        
        Args:
            profile_id: ID of profile to download.
            format_type: File format ("json", "markdown", "docx").
        
        Returns:
            Tuple of (file_data, file_extension) or (None, None) if failed.
        """
        if not self.circuit_breaker or not self.retry_manager:
            # Fallback to direct call if no recovery infrastructure
            return await self._direct_download_file(profile_id, format_type)

        try:
            # Use circuit breaker with retry manager
            return await self.circuit_breaker.call(
                self.retry_manager.retry,
                self._direct_download_file,
                profile_id,
                format_type,
                retry_condition=self._should_retry_download_error,
            )
        except Exception as e:
            logger.error(f"Safe download failed after all recovery attempts: {e}")
            return None, None

    async def _direct_download_file(self, profile_id: str, format_type: str):
        """Directly downloads a file in the specified format.
        
        This function retrieves a file based on the provided profile_id and
        format_type.  It supports downloading files in JSON, Markdown, and DOCX formats
        by calling  the appropriate methods from the api_client. If an unsupported
        format is  specified, a ValueError is raised. Error handling is implemented to
        log  any issues encountered during the download process.
        
        Args:
            profile_id: ID of profile to download.
            format_type: File format.
        """
        try:
            if format_type == "json":
                file_data = await self.api_client.download_profile_json(profile_id)
                file_extension = "json"
            elif format_type == "markdown":
                file_data = await self.api_client.download_profile_markdown(profile_id)
                file_extension = "md"
            elif format_type == "docx":
                file_data = await self.api_client.download_profile_docx(profile_id)
                file_extension = "docx"
            else:
                raise ValueError(f"Unsupported format: {format_type}")

            return file_data, file_extension

        except Exception as e:
            logger.error(f"Direct download API error: {e}")
            raise

    def _should_retry_download_error(self, error: Exception) -> bool:
        """Determine if download error should trigger retry.
        
        This function evaluates the provided error to decide whether a retry  of the
        download operation is warranted. It first checks against a list  of permanent
        errors that should not trigger a retry. If the error is  not permanent, it then
        assesses if the error falls under conditions  that are typically retryable,
        such as network issues or server errors.
        
        Args:
            error: Exception from download operation
        """
        error_str = str(error).lower()

        # Don't retry certain permanent errors
        permanent_errors = [
            "not found",
            "profile not found",
            "file not found",
            "unauthorized",
            "forbidden",
            "permission denied",
            "invalid profile",
            "invalid format",
            "validation error",
            "400",
            "401",
            "403",
            "404",
        ]

        if any(perm_error in error_str for perm_error in permanent_errors):
            logger.debug(f"Download error is permanent, not retrying: {error}")
            return False

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
            "server error",
            "internal server error",
            "gateway timeout",
        ]

        should_retry = any(condition in error_str for condition in retry_conditions)

        if should_retry:
            logger.debug(f"Download error is retryable: {error}")
        else:
            logger.debug(f"Download error is not retryable: {error}")

        return should_retry

    async def _handle_download_failure(self, download_key: str, error_message: str):
        """Handle download failure and coordinate recovery efforts.
        
        Args:
            download_key: Unique key for the download operation.
            error_message: Error message from the failure.
        """
        self.failed_downloads.add(download_key)
        logger.error(f"Download failure for {download_key}: {error_message}")

        # Report to error recovery coordinator
        if self.error_recovery_coordinator:
            try:
                error = Exception(f"download_failure_{download_key}: {error_message}")
                recovered = (
                    await self.error_recovery_coordinator.handle_component_error(
                        "files_manager_component", error, attempt_recovery=True
                    )
                )

                if recovered:
                    logger.info(
                        f"Files manager recovery successful for: {download_key}"
                    )
                    self._safe_notify(
                        "🔄 Менеджер файлов восстановлен, попробуйте скачать еще раз",
                        "positive",
                    )
                    return
            except Exception as recovery_error:
                logger.error(
                    f"Files manager error recovery coordination failed: {recovery_error}"
                )

        # Show enhanced error dialog with recovery options
        await self._show_download_error_dialog(download_key, error_message)

    async def _show_download_error_dialog(self, download_key: str, error_message: str):
        # Parse download key to extract profile_id and format
        """Show download error dialog with recovery options.
        
        This function displays a dialog to inform the user about a failed download,
        providing a user-friendly error message and suggestions for recovery. It
        parses the download_key to extract the profile_id and format type, and
        retrieves the number of download attempts. The dialog includes technical
        details about the error and offers action buttons for retrying the download,
        trying an alternative format, or resetting the download state.
        
        Args:
            download_key: Key identifying the failed download.
            error_message: Technical error message.
        """
        parts = download_key.split("_")
        if len(parts) >= 2:
            profile_id = parts[0]
            format_type = parts[1]
        else:
            profile_id = download_key
            format_type = "unknown"

        attempts = self.download_attempts.get(download_key, 0)
        friendly_message, suggestion = self._get_user_friendly_download_error(
            error_message
        )

        with ui.dialog() as dialog:
            with ui.card().classes("border-l-4 border-red-500 bg-red-50 min-w-[500px]"):
                with ui.card_section().classes("py-6"):
                    # Enhanced header with attempt info
                    with ui.row().classes("items-center gap-3 mb-4"):
                        ui.icon("file_download_off", size="2rem").classes(
                            "text-red-600"
                        )
                        with ui.column().classes("gap-1"):
                            ui.label("❌ Не удалось скачать файл").classes(
                                "text-lg font-bold text-red-800"
                            )
                            ui.label(
                                f"{format_type.upper()} • {profile_id[:12]}..."
                            ).classes("text-caption text-red-600")

                    # User-friendly error message
                    ui.label(friendly_message).classes("text-body1 text-red-700 mb-3")

                    # Enhanced suggestion with recovery context
                    if suggestion:
                        ui.label(suggestion).classes("text-body2 text-red-600 mb-4")

                    # Show download attempts
                    if attempts > 1:
                        with ui.card().classes(
                            "w-full bg-orange-50 border border-orange-200 mb-4"
                        ):
                            with ui.card_section().classes("py-3"):
                                ui.label(f"🔄 Выполнено попыток: {attempts}").classes(
                                    "text-body2 text-orange-700"
                                )
                                if attempts >= 3:
                                    ui.label(
                                        "Рекомендуется проверить соединение с интернетом"
                                    ).classes("text-caption text-orange-600")

                    # Technical details (expandable)
                    with ui.expansion("🔧 Технические детали", icon="info").classes(
                        "w-full mb-4"
                    ):
                        ui.label(error_message).classes(
                            "text-caption font-mono bg-grey-100 p-2 rounded"
                        )

                        # Show circuit breaker status if available
                        if self.circuit_breaker:
                            stats = self.circuit_breaker.get_stats()
                            ui.label(
                                f"Circuit Breaker: {stats['state']} (failures: {stats['failure_count']})"
                            ).classes("text-caption text-grey-6 mt-2")

                    # Enhanced action buttons
                    with ui.row().classes("gap-3"):
                        if attempts < 5:  # Allow more retries for downloads
                            ui.button(
                                "Повторить попытку",
                                icon="refresh",
                                on_click=lambda: self._retry_download(
                                    dialog, profile_id, format_type
                                ),
                            ).props("color=blue")

                        ui.button(
                            "Попробовать другой формат",
                            icon="file_copy",
                            on_click=lambda: self._try_alternative_format(
                                dialog, profile_id, format_type
                            ),
                        ).props("color=orange outlined")

                        ui.button(
                            "Очистить и сбросить",
                            icon="cleaning_services",
                            on_click=lambda: self._reset_downloads_state(dialog),
                        ).props("color=red outlined")

                        ui.button("Закрыть", on_click=dialog.close).props("outlined")

        dialog.open()

    def _get_user_friendly_download_error(self, error_message: str):
        """
        @doc
        Convert technical download error to user-friendly message.

        Args:
            error_message: Technical error message

        Returns:
            Tuple of (friendly_message, suggestion)

        Examples:
          python> msg, sug = files_manager._get_user_friendly_download_error("Connection timeout")
          python> print(msg)  # "Проблемы с подключением к серверу"
        """
        error_lower = error_message.lower()

        if any(
            keyword in error_lower for keyword in ["timeout", "connection", "network"]
        ):
            return (
                "Проблемы с подключением к серверу",
                "Проверьте интернет-соединение и повторите попытку",
            )
        elif any(keyword in error_lower for keyword in ["not found", "404"]):
            return (
                "Файл профиля не найден",
                "Возможно, профиль еще не был сгенерирован или был удален",
            )
        elif any(keyword in error_lower for keyword in ["unauthorized", "401", "403"]):
            return (
                "Нет прав доступа к файлу",
                "Обратитесь к администратору для получения доступа",
            )
        elif any(keyword in error_lower for keyword in ["rate limit", "too many"]):
            return (
                "Превышен лимит запросов",
                "Подождите несколько минут перед повторной попыткой",
            )
        elif any(
            keyword in error_lower for keyword in ["server error", "500", "502", "503"]
        ):
            return (
                "Временные проблемы на сервере",
                "Сервер временно недоступен, попробуйте позже",
            )
        else:
            return (
                "Произошла техническая ошибка",
                "Попробуйте еще раз или обратитесь к администратору",
            )

    async def _retry_download(self, dialog, profile_id: str, format_type: str):
        """Retry the download process with user feedback.
        
        Args:
            dialog: Error dialog to close.
            profile_id: Profile ID to retry.
            format_type: File format to retry.
        """
        dialog.close()

        # Remove from failed downloads to allow retry
        download_key = f"{profile_id}_{format_type}"
        self.failed_downloads.discard(download_key)

        self._safe_notify(
            f"🔄 Повторная попытка скачивания {format_type.upper()}...", "info"
        )

        # Small delay before retry
        await asyncio.sleep(1)
        await self.download_file(profile_id, format_type)

    async def _try_alternative_format(
        self, dialog, profile_id: str, current_format: str
    ):
        """
        @doc
        Try downloading in alternative format.

        Args:
            dialog: Error dialog to close
            profile_id: Profile ID to download
            current_format: Currently failed format

        Examples:
          python> await files_manager._try_alternative_format(dialog, "123", "json")
          python> # Alternative format download attempted
        """
        dialog.close()

        # Suggest alternative format
        alternative_formats = {
            "json": "markdown",
            "markdown": "json",
            "docx": "markdown",
        }

        alternative = alternative_formats.get(current_format, "json")

        self._safe_notify(
            f"🔄 Попытка скачивания в формате {alternative.upper()}...", "info"
        )
        await asyncio.sleep(1)
        await self.download_file(profile_id, alternative)

    async def _reset_downloads_state(self, dialog):
        """
        @doc
        Reset downloads state and cleanup resources.

        Args:
            dialog: Dialog to close

        Examples:
          python> await files_manager._reset_downloads_state(dialog)
          python> # Downloads state reset and resources cleaned
        """
        dialog.close()

        logger.info("Resetting files manager downloads state")

        # Clean up all resources
        await self.cleanup_all_temp_files()

        # Reset circuit breaker if available
        if self.circuit_breaker:
            self.circuit_breaker._reset()

        self._safe_notify("🧹 Состояние менеджера файлов сброшено", "info")

    async def _cleanup_managed_resources(self):
        """Clean up all managed resources to prevent leaks.
        
        This function cleans up all resources managed by the files manager. It checks
        for an error recovery coordinator and iterates through the managed resources,
        invoking the `cleanup` method on each resource if it exists. The cleanup tasks
        are gathered and awaited to ensure all resources are properly cleaned up before
        clearing the managed resources list. Any exceptions during the cleanup process
        are logged for debugging purposes.
        """
        logger.debug("Cleaning up files manager managed resources")

        try:
            # Clean up managed resources through coordinator
            if self.error_recovery_coordinator and self.managed_resources:
                cleanup_tasks = []
                for resource in list(self.managed_resources):
                    if hasattr(resource, "cleanup"):
                        cleanup_tasks.append(resource.cleanup())

                if cleanup_tasks:
                    await asyncio.gather(*cleanup_tasks, return_exceptions=True)

                self.managed_resources.clear()

            logger.debug("Files manager resource cleanup completed")

        except Exception as e:
            logger.error(f"Error during files manager resource cleanup: {e}")

    def _save_component_state(self):
        """Save the current component state for recovery."""
        if not self.error_recovery_coordinator:
            return

        state_data = {
            "temp_files_count": len(self.temp_files),
            "download_attempts": dict(self.download_attempts),
            "failed_downloads": list(self.failed_downloads),
            "is_downloading": bool(self.download_progress_dialog),
            "timestamp": time.time(),
        }

        try:
            self.error_recovery_coordinator.state_manager.save_state(
                "files_manager_component", state_data, ttl_seconds=600  # 10 minute TTL
            )
            logger.debug("Files manager component state saved for recovery")
        except Exception as e:
            logger.error(f"Failed to save files manager component state: {e}")

    async def _on_recovery_callback(self, recovered_state: dict):
        """Handle state recovery for the files manager component.
        
        Args:
            recovered_state (dict): Previously saved state data.
        """
        try:
            logger.info("Recovering files manager component state...")

            # Clean up current resources first
            await self._cleanup_managed_resources()

            # Clear current state
            self.download_attempts.clear()
            self.failed_downloads.clear()

            self._safe_notify("🔄 Менеджер файлов восстановлен после ошибки", "positive")
            logger.info("Files manager component state recovery completed")

        except Exception as e:
            logger.error(f"Error during files manager state recovery: {e}")
            self._safe_notify("⚠️ Частичное восстановление менеджера файлов", "warning")

    def track_resource(self, resource):
        """Track a resource for automatic cleanup.
        
        Args:
            resource: Resource to track (should implement cleanup method).
        """
        if hasattr(resource, "cleanup"):
            self.managed_resources.add(resource)

            # Also register with coordinator if available
            if self.error_recovery_coordinator and isinstance(
                resource, ManagedResource
            ):
                self.error_recovery_coordinator.cleanup_manager.track_resource(resource)

            logger.debug(
                f"Tracking resource: {getattr(resource, 'resource_id', 'unknown')}"
            )
        else:
            logger.warning("Resource does not implement cleanup method")

    async def reset_component_state(self):
        """Reset the component to a clean state."""
        logger.info("Resetting files manager component state")

        # Clean up all resources
        await self.cleanup_all_temp_files()

        # Close any open dialogs
        if self.download_progress_dialog:
            self.download_progress_dialog.close()
            self.download_progress_dialog = None

        # Reset circuit breaker if available
        if self.circuit_breaker:
            self.circuit_breaker._reset()

        self._safe_notify("🔄 Менеджер файлов сброшен", "info")

    def get_download_status(self) -> Dict[str, Any]:
        """Retrieve the download status of the component."""
        return {
            "temp_files_count": len(self.temp_files),
            "is_downloading": bool(self.download_progress_dialog),
            "temp_files": list(self.temp_files),
            "managed_resources_count": len(self.managed_resources),
            "download_attempts": dict(self.download_attempts),
            "failed_downloads": list(self.failed_downloads),
            "circuit_breaker_stats": (
                self.circuit_breaker.get_stats() if self.circuit_breaker else None
            ),
        }

"""
@doc
GeneratorPage - Композитная страница генератора профилей.

Собирает вместе модульные компоненты для создания единого пользовательского интерфейса:
- SearchComponent: Поиск и выбор должностей
- GeneratorComponent: Управление генерацией профилей
- ProfileViewerComponent: Отображение сгенерированных профилей
- FilesManagerComponent: Скачивание файлов профилей

Обеспечивает взаимодействие между компонентами через систему событий.

Examples:
  python> generator_page = GeneratorPage(api_client)
  python> await generator_page.render()
"""

import asyncio
import logging
from typing import Dict, Any

from nicegui import ui, app

try:
    from ..core.error_recovery import ErrorRecoveryCoordinator
except ImportError:
    try:
        from frontend.core.error_recovery import ErrorRecoveryCoordinator
    except ImportError:
        # Error recovery is optional - system can work without it
        ErrorRecoveryCoordinator = None

try:
    # Relative imports для запуска как модуль
    from ..services.api_client import APIClient
    from ..components.core.search_component import SearchComponent
    from ..components.core.generator_component import GeneratorComponent
    from ..components.core.profile_viewer_component import ProfileViewerComponent
    from ..components.core.files_manager_component import FilesManagerComponent
except ImportError:
    # Absolute imports для прямого запуска
    from services.api_client import APIClient
    from components.core.search_component import SearchComponent
    from components.core.generator_component import GeneratorComponent
    from components.core.profile_viewer_component import ProfileViewerComponent
    from components.core.files_manager_component import FilesManagerComponent

logger = logging.getLogger(__name__)


class GeneratorPage:
    """
    @doc
    Композитная страница, объединяющая модульные компоненты генератора.
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

        # Initialize error recovery coordinator (optional)
        self.error_recovery_coordinator = None
        if ErrorRecoveryCoordinator is not None:
            try:
                self.error_recovery_coordinator = ErrorRecoveryCoordinator(api_client)
                logger.info("Error recovery coordinator initialized successfully")
            except Exception as e:
                logger.warning(
                    f"Error recovery coordinator initialization failed: {e}. Running in basic mode."
                )
                self.error_recovery_coordinator = None
        else:
            logger.info("Error recovery not available - running in basic mode")

        self.recovery_active = False

        # Инициализация компонентов с error recovery (если доступно)
        self.search = SearchComponent(api_client, self.error_recovery_coordinator)
        self.generator = GeneratorComponent(api_client, self.error_recovery_coordinator)
        self.viewer = ProfileViewerComponent(
            api_client, self.error_recovery_coordinator
        )
        self.files = FilesManagerComponent(api_client, self.error_recovery_coordinator)

        # Связывание компонентов через события
        self._connect_components()

    def _connect_components(self):
        """Связывание компонентов через расширенную систему событий."""
        # Основные события (без изменений для backward compatibility)
        logger.info(
            f"🔥 DEBUG: Connecting search.on_position_selected to generator.set_position"
        )
        self.search.on_position_selected = self.generator.set_position
        logger.info(
            f"🔥 DEBUG: Connected search.on_position_selected = {self.search.on_position_selected}"
        )

        logger.info(
            f"🔥 DEBUG: Connecting search.on_profiles_found to viewer.show_profile_list"
        )
        self.search.on_profiles_found = self.viewer.show_profile_list
        logger.info(
            f"🔥 DEBUG: Connected search.on_profiles_found = {self.search.on_profiles_found}"
        )

        # Интеграция ProfileViewerComponent с другими компонентами
        self.viewer.on_download_request = (
            self.files.download_file
        )  # Новый синхронный метод

        # Интеграция SearchComponent с FilesManagerComponent для скачивания
        self.search.on_download_request = self.files.download_file

        # Новые события для расширенной функциональности
        if hasattr(self.viewer, "on_tab_switch"):
            self.viewer.on_tab_switch = self._handle_tab_switch

        # Обработка генерации профилей
        if hasattr(self.generator, "on_generation_complete"):
            self.generator.on_generation_complete = self._handle_generation_complete

        # Enhanced error recovery event connections
        self._setup_recovery_monitoring()

        logger.info(
            "Generator components connected successfully with enhanced events and error recovery"
        )

    def _render_compact_welcome_banner(self):
        """
        @doc
        Рендеринг компактного приветственного баннера с возможностью закрытия.

        Показывает краткую информацию и предоставляет доступ к подробному гиду.
        Использует минимум экранного пространства (~3% вместо 20%).

        Examples:
          python> page._render_compact_welcome_banner()
          python> # Компактный баннер отрендерен
        """
        # Check if banner was dismissed
        welcome_dismissed = app.storage.user.get("welcome_dismissed", False)

        if not welcome_dismissed:
            # Компактный баннер с использованием ui.card (имитация ui.banner)
            with ui.card().classes(
                "w-full bg-blue-50 border-l-4 border-blue-500 mb-2"
            ) as banner:
                with ui.row().classes("w-full items-center justify-between p-2"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("info", size="1.2rem").classes("text-blue-600")
                        ui.label(
                            "Добро пожаловать в A101 HR Profile Generator! Создавайте профили должностей с помощью ИИ"
                        ).classes("text-body1 text-blue-800")

                    with ui.row().classes("items-center gap-1"):
                        ui.button(
                            "Быстрый гид",
                            icon="help",
                            on_click=self._show_detailed_guide,
                        ).props("flat dense size=sm color=primary")
                        ui.button(
                            icon="close",
                            on_click=lambda: self._dismiss_welcome_banner(banner),
                        ).props("flat dense size=sm")

    def _dismiss_welcome_banner(self, banner):
        """
        @doc
        Закрытие приветственного баннера с сохранением состояния.

        Args:
            banner: UI компонент баннера для удаления

        Examples:
          python> page._dismiss_welcome_banner(banner_component)
          python> # Баннер закрыт и состояние сохранено
        """
        app.storage.user["welcome_dismissed"] = True
        banner.delete()
        logger.info("Welcome banner dismissed by user")

    def _show_detailed_guide(self):
        """
        @doc
        Показ детального гида по использованию генератора в диалоге.

        Отображает полную инструкцию в модальном окне без занятия
        основного пространства страницы.

        Examples:
          python> page._show_detailed_guide()
          python> # Детальный гид показан в диалоге
        """
        with ui.dialog().props("maximized") as dialog:
            with ui.card().classes("w-full max-w-4xl"):
                with ui.card_section():
                    with ui.row().classes("items-center justify-between"):
                        ui.label(
                            "🚀 Руководство по использованию A101 HR Profile Generator"
                        ).classes("text-h5 font-bold")
                        ui.button(icon="close", on_click=dialog.close).props(
                            "flat round"
                        )

                    ui.separator()

                    # Detailed guide content
                    with ui.row().classes("w-full gap-8 mt-6"):
                        with ui.column().classes("flex-1"):
                            ui.label("🔍 Шаг 1: Поиск должности").classes(
                                "text-h6 font-medium mb-2"
                            )
                            ui.label(
                                "• Введите название должности в поле поиска"
                            ).classes("text-body1 mb-1")
                            ui.label("• Система покажет доступные варианты").classes(
                                "text-body1 mb-1"
                            )
                            ui.label("• Выберите подходящий департамент").classes(
                                "text-body1 mb-4"
                            )

                        with ui.column().classes("flex-1"):
                            ui.label("🚀 Шаг 2: Генерация профиля").classes(
                                "text-h6 font-medium mb-2"
                            )
                            ui.label(
                                "• Нажмите кнопку 'Сгенерировать профиль'"
                            ).classes("text-body1 mb-1")
                            ui.label(
                                "• ИИ создаст детальный профиль должности"
                            ).classes("text-body1 mb-1")
                            ui.label("• Процесс займет 1-2 минуты").classes(
                                "text-body1 mb-4"
                            )

                        with ui.column().classes("flex-1"):
                            ui.label("📥 Шаг 3: Результат").classes(
                                "text-h6 font-medium mb-2"
                            )
                            ui.label("• Просмотрите сгенерированный профиль").classes(
                                "text-body1 mb-1"
                            )
                            ui.label("• Скачайте в формате JSON или Markdown").classes(
                                "text-body1 mb-1"
                            )
                            ui.label("• Используйте профиль в работе HR").classes(
                                "text-body1 mb-4"
                            )

        dialog.open()

    async def render(self):
        """
        @doc
        Рендеринг оптимизированной страницы генератора с улучшенным UX.

        Новый layout:
        - 3% экрана: компактный баннер (закрываемый)
        - 15% экрана: секция поиска
        - 60% экрана: объединенная область результатов с разделителем
        - 22% экрана: управление файлами (сворачиваемое)

        Обеспечивает быстрый отклик UI (< 300ms) и лучший UX.
        """
        with ui.column().classes("w-full gap-4"):
            # 1. Компактный приветственный баннер (3% экрана)
            self._render_compact_welcome_banner()

            # 2. Секция поиска (15% экрана)
            await self.search.render_search_section()

            # 3. Объединенная область результатов и генерации (60% экрана)
            with ui.card().classes("w-full").style("min-height: 60vh"):
                with ui.card_section():
                    with ui.row().classes("w-full gap-4"):
                        # Левая панель: результаты поиска и генерация (70% ширины)
                        with ui.column().classes("w-2/3 gap-4"):
                            await self.generator.render_generator_section()

                        # Правая панель: просмотр профиля (30% ширины)
                        with ui.column().classes("w-1/3"):
                            self.viewer.render_profile_viewer()

            # 4. Секция управления файлами (сворачиваемая, 22% экрана)
            with ui.expansion(
                "📁 Управление файлами", icon="folder", value=False
            ).classes("w-full"):
                await self.files.render_files_section()

        # 🚀 ПРОИЗВОДИТЕЛЬНОСТЬ: Асинхронная загрузка данных в фоне после рендеринга UI
        # Это обеспечивает мгновенный отклик страницы (< 300ms)
        asyncio.create_task(self._background_data_loading())

    async def reload_search_data(self):
        """Перезагрузка данных для компонента поиска."""
        await self.search.force_reload_data()

    async def _background_data_loading(self):
        """
        @doc
        Асинхронная загрузка данных в фоне для оптимизации производительности.

        Загружает данные поиска (4376 позиций) после рендеринга UI,
        обеспечивая мгновенный отклик страницы (< 300ms вместо 1570ms).

        Examples:
          python> await generator_page._background_data_loading()
          python> # Данные загружены в фоне, UI отзывчив
        """
        try:
            logger.info(
                "🚀 Starting background data loading for optimal performance..."
            )

            # Небольшая задержка, чтобы UI успел полностью отрендериться
            await asyncio.sleep(0.1)

            # Загружаем данные поиска асинхронно
            await self.search.load_search_data()

            logger.info("✅ Background data loading completed successfully")

        except Exception as e:
            logger.warning(
                f"Background data loading failed (fallback mode will be used): {e}"
            )
            # Ошибка не критична - компонент поиска имеет fallback suggestions

    def _handle_generate_request(self, department: str, position: str):
        """
        @doc
        Обработчик запроса генерации от ProfileViewerComponent.

        Запускает генерацию нового профиля через GeneratorComponent.

        Args:
            department: Название департамента
            position: Название должности

        Examples:
          python> page._handle_generate_request("Группа анализа данных", "Аналитик BI")
          # Запущена генерация нового профиля
        """
        logger.info(
            f"Generate request from ProfileViewerComponent: {department}/{position}"
        )

        # Устанавливаем позицию в генераторе (position, department)
        self.generator.set_position(position, department)

        # Запускаем генерацию в background task
        asyncio.create_task(self.generator._start_generation())

    def _handle_tab_switch(self, tab_id: str):
        """
        @doc
        Обработчик переключения табов в ProfileViewerComponent.

        Args:
            tab_id: ID переключенного таба

        Examples:
          python> page._handle_tab_switch("markdown")
          python> # Логируется переключение таба
        """
        logger.info(f"Tab switched to: {tab_id}")

        # Можно добавить аналитику или специальную логику для определенных табов
        if tab_id == "markdown":
            logger.debug(
                "User viewing Markdown tab - ensure markdown content is generated"
            )
        elif tab_id == "versions":
            logger.debug("User viewing versions tab - versions management active")

    async def _handle_generation_complete(self, result: Dict[str, Any]):
        """
        @doc
        Обработчик завершения генерации профиля.

        Args:
            result: Результат генерации профиля

        Examples:
          python> await page._handle_generation_complete(generation_result)
          python> # Профиль отображен в viewer
        """
        logger.info(f"Generation completed: {result.get('profile_id', 'unknown')}")

        try:
            # Отправляем результат в ProfileViewerComponent для отображения
            if result.get("success"):
                await self.viewer.show_profile(
                    {"task_result": result, "view_mode": "single"}
                )
                ui.notify("✅ Профиль успешно сгенерирован!", type="positive")
            else:
                error_msg = result.get("error", "Неизвестная ошибка")
                ui.notify(f"❌ Ошибка генерации: {error_msg}", type="negative")

        except Exception as e:
            logger.error(f"Error handling generation completion: {e}")
            ui.notify("❌ Ошибка отображения сгенерированного профиля", type="negative")

    # === Error Recovery Coordination Methods ===

    def _setup_recovery_monitoring(self):
        """
        @doc
        Setup comprehensive error recovery monitoring for the page.

        Coordinates recovery between all components and provides
        centralized error handling and recovery orchestration.

        Examples:
          python> page._setup_recovery_monitoring()
          python> # Recovery monitoring active across all components
        """
        # Only setup monitoring if error recovery coordinator is available
        if self.error_recovery_coordinator is not None:
            # Setup API health monitoring callbacks
            self.error_recovery_coordinator.health_monitor.on_recovery = (
                self._on_api_recovery
            )
            self.error_recovery_coordinator.health_monitor.on_degradation = (
                self._on_api_degradation
            )

            # Register page-level recovery callbacks
            self.error_recovery_coordinator.register_recovery_callback(
                "generator_page", self._on_page_recovery_callback
            )

        logger.info("Error recovery monitoring setup completed")

    def _on_api_recovery(self):
        """
        @doc
        Handle API recovery notification.

        Triggered when API health monitor detects service recovery.
        Coordinates fallback → normal mode transitions across components.

        Examples:
          python> page._on_api_recovery()
          python> # All components notified of API recovery
        """
        logger.info("API recovered - coordinating component recovery")

        try:
            # Show recovery notification
            ui.notify("🔄 Соединение с сервером восстановлено", type="positive")

            # Trigger component recovery
            asyncio.create_task(self._coordinate_component_recovery())

        except Exception as e:
            logger.error(f"Error handling API recovery: {e}")

    def _on_api_degradation(self, error_message: str):
        """
        @doc
        Handle API degradation notification.

        Triggered when API health monitor detects service issues.
        Coordinates normal → fallback mode transitions across components.

        Args:
            error_message: Error message describing the degradation

        Examples:
          python> page._on_api_degradation("Connection timeout")
          python> # All components switched to fallback mode
        """
        logger.warning(
            f"API degradation detected - coordinating fallback: {error_message}"
        )

        try:
            # Show degradation notification
            ui.notify(
                "⚠️ Проблемы с сервером - переключение в ограниченный режим",
                type="warning",
            )

            # Enable recovery mode for page
            self.recovery_active = True

        except Exception as e:
            logger.error(f"Error handling API degradation: {e}")

    async def _coordinate_component_recovery(self):
        """
        @doc
        Coordinate recovery across all components.

        Orchestrates the transition from fallback to normal mode
        ensuring all components are properly synchronized.

        Examples:
          python> await page._coordinate_component_recovery()
          python> # All components recovered and synchronized
        """
        try:
            logger.info("Starting coordinated component recovery...")

            recovery_tasks = []

            # Trigger recovery for each component
            if hasattr(self.search, "force_reload_data"):
                recovery_tasks.append(self.search.force_reload_data(from_recovery=True))

            if hasattr(self.generator, "reset_component_state"):
                recovery_tasks.append(self.generator.reset_component_state())

            if hasattr(self.viewer, "reset_component_state"):
                recovery_tasks.append(self.viewer.reset_component_state())

            if hasattr(self.files, "reset_component_state"):
                recovery_tasks.append(self.files.reset_component_state())

            # Execute recovery tasks with timeout
            if recovery_tasks:
                await asyncio.wait_for(
                    asyncio.gather(*recovery_tasks, return_exceptions=True),
                    timeout=30.0,
                )

            # Reset page recovery state
            self.recovery_active = False

            logger.info("Coordinated component recovery completed successfully")
            ui.notify("✅ Все компоненты восстановлены", type="positive")

        except asyncio.TimeoutError:
            logger.error("Component recovery timeout")
            ui.notify("⚠️ Восстановление завершено с ограничениями", type="warning")
        except Exception as e:
            logger.error(f"Error during coordinated recovery: {e}")
            ui.notify("❌ Ошибка восстановления компонентов", type="negative")

    async def _on_page_recovery_callback(self, recovered_state: Dict[str, Any]):
        """
        @doc
        Handle page-level state recovery.

        Args:
            recovered_state: Previously saved page state

        Examples:
          python> await page._on_page_recovery_callback({"recovery_active": True})
          python> # Page state recovered from coordinator
        """
        try:
            logger.info("Recovering generator page state...")

            # Restore page-level state
            self.recovery_active = recovered_state.get("recovery_active", False)

            # Trigger component coordination if needed
            if self.recovery_active:
                await self._coordinate_component_recovery()

            ui.notify("🔄 Страница генератора восстановлена", type="positive")
            logger.info("Generator page state recovery completed")

        except Exception as e:
            logger.error(f"Error during page state recovery: {e}")
            ui.notify("⚠️ Частичное восстановление страницы", type="warning")

    async def start_error_recovery(self):
        """
        @doc
        Start error recovery systems for the page.

        Initializes all error recovery mechanisms including
        API health monitoring, circuit breakers, and cleanup.

        Examples:
          python> await page.start_error_recovery()
          python> # All recovery systems active
        """
        try:
            logger.info("Starting generator page error recovery systems...")

            # Start the error recovery coordinator
            await self.error_recovery_coordinator.start()

            logger.info("Generator page error recovery systems started successfully")

        except Exception as e:
            logger.error(f"Failed to start error recovery systems: {e}")
            raise

    async def stop_error_recovery(self):
        """
        @doc
        Stop error recovery systems and cleanup resources.

        Performs graceful shutdown of all recovery mechanisms
        and cleans up any tracked resources.

        Examples:
          python> await page.stop_error_recovery()
          python> # All recovery systems stopped, resources cleaned up
        """
        try:
            logger.info("Stopping generator page error recovery systems...")

            # Stop the error recovery coordinator (includes cleanup)
            await self.error_recovery_coordinator.stop()

            # Reset page state
            self.recovery_active = False

            logger.info("Generator page error recovery systems stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping recovery systems: {e}")

    async def reset_all_components(self):
        """
        @doc
        Reset all components to clean state.

        Emergency reset function that clears all component states
        and restarts them from scratch. Use as last resort.

        Examples:
          python> await page.reset_all_components()
          python> # All components reset to clean state
        """
        try:
            logger.info("Performing emergency reset of all components...")

            # Show loading indicator
            ui.notify("🔄 Сброс всех компонентов...", type="info")

            # Reset each component
            reset_tasks = []

            if hasattr(self.search, "reset_component_state"):
                reset_tasks.append(self.search.reset_component_state())

            if hasattr(self.generator, "reset_component_state"):
                reset_tasks.append(self.generator.reset_component_state())

            if hasattr(self.viewer, "reset_component_state"):
                reset_tasks.append(self.viewer.reset_component_state())

            if hasattr(self.files, "reset_component_state"):
                reset_tasks.append(self.files.reset_component_state())

            # Execute resets with timeout
            if reset_tasks:
                await asyncio.wait_for(
                    asyncio.gather(*reset_tasks, return_exceptions=True), timeout=20.0
                )

            # Reset page state
            self.recovery_active = False

            logger.info("Emergency component reset completed")
            ui.notify("✅ Все компоненты успешно сброшены", type="positive")

        except Exception as e:
            logger.error(f"Error during emergency reset: {e}")
            ui.notify("❌ Ошибка при сбросе компонентов", type="negative")

    def get_recovery_status(self) -> Dict[str, Any]:
        """
        @doc
        Get comprehensive recovery status for all components.

        Returns:
            Dict with recovery status, statistics, and health info

        Examples:
          python> status = page.get_recovery_status()
          python> print(status['overall_health'])  # "HEALTHY"
        """
        try:
            # Get coordinator stats
            coordinator_stats = self.error_recovery_coordinator.get_overall_stats()

            # Get component-specific status
            component_status = {}

            if hasattr(self.search, "get_selected_position_data"):
                component_status["search"] = {
                    "has_data": bool(self.search.get_selected_position_data()),
                    "fallback_mode": getattr(self.search, "fallback_mode", False),
                }

            if hasattr(self.generator, "get_generation_status"):
                component_status["generator"] = self.generator.get_generation_status()

            if hasattr(self.files, "get_download_status"):
                component_status["files"] = self.files.get_download_status()

            return {
                "page_recovery_active": self.recovery_active,
                "coordinator_stats": coordinator_stats,
                "component_status": component_status,
                "recovery_systems_running": self.error_recovery_coordinator.is_started,
                "timestamp": asyncio.get_event_loop().time(),
            }

        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return {
                "error": str(e),
                "page_recovery_active": self.recovery_active,
                "timestamp": asyncio.get_event_loop().time(),
            }

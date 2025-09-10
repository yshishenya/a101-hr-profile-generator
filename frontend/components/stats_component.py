"""
@doc
Единый простой компонент статистики для A101 HR Profile Generator.

Минималистичный компонент следующий принципам UltraThink:
- Один компонент для всех страниц
- Один API метод для получения данных
- Простая адаптивная структура без избыточности
- Красивый дизайн в стиле проекта

Examples:
  python> stats = StatsComponent(api_client, "dashboard")
  python> await stats.render()
"""

from nicegui import ui
import logging
import asyncio
from typing import Literal, Optional

logger = logging.getLogger(__name__)


class StatsComponent:
    """
    @doc
    Единый компонент статистики для всех страниц.

    Стили:
    - "dashboard": подробная статистика для главной
    - "compact": компактная для страницы генератора
    - "minimal": минимальная для header

    Examples:
      python> stats = StatsComponent(api_client, "dashboard")
      python> await stats.render()
    """

    def __init__(
        self,
        api_client,
        style: Literal["dashboard", "compact", "minimal"] = "dashboard",
    ):
        self.api_client = api_client
        self.style = style

        # UI элементы
        self.positions_label = None
        self.profiles_label = None
        self.progress_text = None
        self.status_chip = None

        # Состояние
        self.last_data = None
        self.refresh_timer = None

    async def render(self):
        """Отрисовка в выбранном стиле"""
        if self.style == "dashboard":
            await self._render_dashboard()
        elif self.style == "compact":
            await self._render_compact()
        elif self.style == "minimal":
            await self._render_minimal()

        # Загружаем данные и настраиваем обновления
        await self._load_and_update()
        self._setup_refresh()

    async def _render_dashboard(self):
        """Единообразная статистика для dashboard"""
        with ui.card().classes("w-full mb-4 shadow-sm"):
            with ui.card_section().classes("p-4"):
                # Заголовок
                with ui.row().classes("items-center justify-between mb-4"):
                    ui.label("📊 Статистика системы").classes(
                        "text-h6 text-primary font-medium"
                    )
                    self.status_chip = ui.chip("Загрузка", color="grey").props(
                        "size=sm"
                    )

                # Основные метрики в строку - ЕДИНООБРАЗНО
                with ui.row().classes("w-full justify-between gap-4"):
                    # Должности
                    with ui.column().classes("items-center"):
                        self.positions_label = ui.label("1,553").classes(
                            "text-h4 font-bold text-primary"
                        )
                        ui.label("должностей").classes("text-body2 text-grey-6")

                    # Профили
                    with ui.column().classes("items-center"):
                        self.profiles_label = ui.label("2").classes(
                            "text-h4 font-bold text-primary"
                        )
                        ui.label("создано").classes("text-body2 text-grey-6")

                    # Покрытие - без прогресс бара
                    with ui.column().classes("items-center"):
                        self.progress_text = ui.label("0.1%").classes(
                            "text-h4 font-bold text-primary"
                        )
                        ui.label("покрытие").classes("text-body2 text-grey-6")

    async def _render_compact(self):
        """Компактная единообразная статистика для генератора"""
        with ui.card().classes("w-full mb-4 shadow-sm"):
            with ui.card_section().classes("p-3"):
                with ui.row().classes("items-center justify-between"):
                    ui.label("📊 Система").classes("text-h6 text-primary font-medium")
                    self.status_chip = ui.chip("Готов", color="positive").props(
                        "size=xs"
                    )

                # Единообразные метрики в строку
                with ui.row().classes("w-full justify-between mt-3"):
                    with ui.column().classes("items-center"):
                        self.positions_label = ui.label("1,553").classes(
                            "text-h6 font-bold text-primary"
                        )
                        ui.label("должностей").classes("text-caption text-grey-6")

                    with ui.column().classes("items-center"):
                        self.profiles_label = ui.label("2").classes(
                            "text-h6 font-bold text-primary"
                        )
                        ui.label("создано").classes("text-caption text-grey-6")

                    with ui.column().classes("items-center"):
                        self.progress_text = ui.label("0.1%").classes(
                            "text-h6 font-bold text-primary"
                        )
                        ui.label("покрытие").classes("text-caption text-grey-6")

    async def _render_minimal(self):
        """Минимальная статистика для header"""
        with ui.row().classes("items-center gap-3"):
            ui.icon("analytics", size="1rem").classes("text-white opacity-70")
            self.positions_label = ui.label("1,553").classes(
                "text-body2 text-white font-medium"
            )
            ui.label("должностей").classes("text-body2 text-white opacity-60")
            ui.label("•").classes("text-white opacity-40")
            self.profiles_label = ui.label("2").classes(
                "text-body2 text-white font-medium"
            )
            ui.label("профилей").classes("text-body2 text-white opacity-60")

    async def _load_and_update(self):
        """Загрузка и обновление данных"""
        try:
            data = await self.api_client.get_dashboard_stats()
            if data:
                await self._update_ui(data)
                self.last_data = data
                logger.debug(
                    f"Stats updated: {data['profiles_count']} of {data['positions_count']}"
                )
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
            await self._show_error_state()

    async def _update_ui(self, data):
        """Обновление UI элементов"""
        positions = data.get("positions_count", 1553)
        profiles = data.get("profiles_count", 0)
        completion = data.get("completion_percentage", 0)
        active_tasks = data.get("active_tasks_count", 0)

        # Обновляем числа единообразно
        if self.positions_label:
            self.positions_label.text = f"{positions:,}"
        if self.profiles_label:
            self.profiles_label.text = f"{profiles:,}"
        if self.progress_text:
            self.progress_text.text = f"{completion:.1f}%"

        # Обновляем статус
        if self.status_chip:
            if active_tasks > 0:
                self.status_chip.set_text(f"🔄 {active_tasks} активных")
                self.status_chip.props("color=orange")
            else:
                import time

                update_time = time.strftime("%H:%M")
                self.status_chip.set_text(f"✅ {update_time}")
                self.status_chip.props("color=positive")

    async def _show_error_state(self):
        """Состояние ошибки"""
        if self.status_chip:
            self.status_chip.set_text("⚠️ Ошибка")
            self.status_chip.props("color=negative")

    def _setup_refresh(self):
        """Автоматическое обновление каждые 2 минуты"""
        if self.style in ["dashboard", "compact"]:  # Не обновляем minimal в header
            self.refresh_timer = ui.timer(120, self._auto_refresh)

    async def _auto_refresh(self):
        """Автоматическое обновление"""
        try:
            await self._load_and_update()
        except Exception as e:
            logger.error(f"Auto refresh failed: {e}")

    async def manual_refresh(self):
        """Ручное обновление"""
        try:
            await self._load_and_update()
            if self.style != "minimal":
                ui.notify("✅ Статистика обновлена", type="positive")
        except Exception as e:
            logger.error(f"Manual refresh failed: {e}")
            if self.style != "minimal":
                ui.notify("❌ Ошибка обновления", type="negative")

    def cleanup(self):
        """Очистка ресурсов"""
        if self.refresh_timer:
            self.refresh_timer.cancel()


if __name__ == "__main__":
    print("✅ StatsComponent - Simple unified statistics solution")
    print("🎨 Styles: dashboard, compact, minimal")
    print("🚀 Features: Single API call, auto-refresh, Material Design")

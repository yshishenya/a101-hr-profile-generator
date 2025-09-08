"""
@doc
Home Dashboard компонент для главной страницы A101 HR Profile Generator.

Отображает статистику системы, быстрые действия, недавнюю активность
и структуру компании для навигации.

Examples:
  python> dashboard = DashboardComponent(api_client)
  python> await dashboard.create()
"""

from nicegui import ui
import asyncio
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DashboardComponent:
    """
    @doc
    Компонент главной страницы (Home Dashboard) после логина.
    
    Включает:
    - Статистику системы (количество профилей, статусы)
    - Быстрые действия (поиск, генерация)
    - Недавнюю активность (последние профили, активные задачи)
    - Структуру компании для навигации
    
    Examples:
      python> dashboard = DashboardComponent(api_client)
      python> await dashboard.create()
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.stats_data = {}
        self.recent_activity = []
        self.departments_data = []
        self.active_tasks = []
        
        # UI элементы для обновления
        self.stats_card = None
        self.activity_card = None
        self.departments_grid = None
        
    async def create(self):
        """
        @doc
        Создает полный dashboard интерфейс.
        
        Загружает данные с backend и отображает все компоненты.
        
        Examples:
          python> await dashboard.create()
        """
        # Загружаем данные параллельно
        await self._load_dashboard_data()
        
        # Создаем интерфейс
        self._create_page_header()
        await self._create_system_stats()
        self._create_quick_actions()
        await self._create_recent_activity()
        
        # Запускаем фоновые обновления
        self._start_background_updates()
    
    async def _load_dashboard_data(self):
        """Загрузка всех данных для dashboard"""
        try:
            # Параллельная загрузка данных
            tasks = [
                self._fetch_catalog_stats(),
                self._fetch_profiles_stats(),
                self._fetch_active_tasks()
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("✅ Dashboard data loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load dashboard data: {e}")
            ui.notify(f"Ошибка загрузки данных: {e}", type='negative')
    
    async def _fetch_catalog_stats(self):
        """Получение статистики каталога"""
        try:
            response = await self.api_client.get_catalog_stats()
            if response and response.get('success'):
                self.stats_data['catalog'] = response['data']
        except Exception as e:
            logger.error(f"Failed to fetch catalog stats: {e}")
            self.stats_data['catalog'] = self._get_mock_catalog_stats()
    
    async def _fetch_profiles_stats(self):
        """Получение статистики профилей"""
        try:
            response = await self.api_client.get_profiles(limit=1)
            if response:
                total = response.get('pagination', {}).get('total', 0)
                self.stats_data['profiles_count'] = total
        except Exception as e:
            logger.error(f"Failed to fetch profiles stats: {e}")
            self.stats_data['profiles_count'] = 0
    
    async def _fetch_active_tasks(self):
        """Получение активных задач генерации"""
        try:
            response = await self.api_client.get_active_generation_tasks()
            if response:
                self.active_tasks = response[:5]  # Последние 5 задач
        except Exception as e:
            logger.error(f"Failed to fetch active tasks: {e}")
            self.active_tasks = []
    
    
    def _create_page_header(self):
        """Создание заголовка страницы"""
        with ui.row().classes('w-full items-center justify-between mb-6'):
            ui.label('🏢 Генерация профилей должностей').classes('text-h4 text-weight-medium')
            
            # Кнопка обновления
            ui.button(
                icon='refresh',
                on_click=self._refresh_dashboard
            ).props('flat round').tooltip('Обновить данные')
    
    async def _create_system_stats(self):
        """Создание карточки статистики системы"""
        with ui.card().classes('w-full mb-6'):
            ui.label('📊 Статус системы').classes('text-h6 q-mb-md')
            
            catalog_stats = self.stats_data.get('catalog', {})
            positions_stats = catalog_stats.get('positions', {})
            
            total_positions = positions_stats.get('total_count', 2844)  # Fallback
            profiles_count = self.stats_data.get('profiles_count', 0)
            in_progress = len(self.active_tasks)
            no_profiles = total_positions - profiles_count
            
            # Расчет процентов
            coverage_percent = (profiles_count / total_positions * 100) if total_positions > 0 else 0
            
            self.stats_card = ui.row().classes('w-full')
            with self.stats_card:
                # Основная статистика
                with ui.card().classes('flex-1 text-center p-4'):
                    ui.label(str(total_positions)).classes('text-h4 text-weight-bold text-primary')
                    ui.label('Всего должностей').classes('text-caption text-grey-6')
                
                with ui.card().classes('flex-1 text-center p-4'):
                    ui.label(str(profiles_count)).classes('text-h4 text-weight-bold text-green')
                    ui.label(f'С профилями ({coverage_percent:.1f}%)').classes('text-caption text-grey-6')
                
                with ui.card().classes('flex-1 text-center p-4'):
                    ui.label(str(in_progress)).classes('text-h4 text-weight-bold text-orange')
                    ui.label('В процессе').classes('text-caption text-grey-6')
                
                with ui.card().classes('flex-1 text-center p-4'):
                    ui.label(str(no_profiles)).classes('text-h4 text-weight-bold text-red')
                    ui.label(f'Без профилей ({100-coverage_percent:.1f}%)').classes('text-caption text-grey-6')
    
    def _create_quick_actions(self):
        """Создание панели быстрых действий"""
        with ui.card().classes('w-full mb-6'):
            ui.label('🎯 Быстрые действия').classes('text-h6 q-mb-md')
            
            with ui.row().classes('w-full q-gutter-md'):
                ui.button(
                    '🔍 Найти должность',
                    on_click=lambda: ui.navigate.to('/search')
                ).classes('flex-1').props('size=lg color=primary')
                
                ui.button(
                    '📋 Все профили', 
                    on_click=lambda: ui.navigate.to('/profiles')
                ).classes('flex-1').props('size=lg color=secondary')
                
                ui.button(
                    '⚡ Быстрая генерация',
                    on_click=self._quick_generate
                ).classes('flex-1').props('size=lg color=positive')
                
                ui.button(
                    '📊 Статистика',
                    on_click=lambda: ui.navigate.to('/analytics')
                ).classes('flex-1').props('size=lg color=info')
    
    async def _create_recent_activity(self):
        """Создание ленты недавней активности"""
        with ui.card().classes('w-full mb-6'):
            ui.label('📈 Недавняя активность').classes('text-h6 q-mb-md')
            
            self.activity_card = ui.column().classes('w-full')
            await self._update_activity_feed()
    
    async def _update_activity_feed(self):
        """Обновление ленты активности"""
        if not self.activity_card:
            return
            
        self.activity_card.clear()
        
        with self.activity_card:
            # Активные задачи
            if self.active_tasks:
                for task in self.active_tasks[:3]:
                    with ui.row().classes('w-full items-center q-py-sm'):
                        if task.get('status') == 'processing':
                            ui.icon('autorenew', color='orange').classes('q-mr-sm')
                            progress = task.get('progress', 0)
                            ui.label(f"⚙️ Генерируется: {task.get('current_step', 'Неизвестно')} ({progress}%)")
                        elif task.get('status') == 'completed':
                            ui.icon('check_circle', color='green').classes('q-mr-sm')
                            ui.label(f"✅ Создан: {task.get('position', 'Профиль')} ({self._format_time(task.get('completed_at'))})")
            
            # Если нет активности
            if not self.active_tasks:
                ui.label('Нет недавней активности').classes('text-grey-6 q-py-md')
                ui.label('Начните с создания первого профиля!').classes('text-caption text-grey-7')
    
    def _format_time(self, timestamp: Optional[str]) -> str:
        """Форматирование времени для отображения"""
        if not timestamp:
            return "недавно"
        
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            diff = now - dt
            
            if diff.seconds < 60:
                return "только что"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60} мин назад"
            elif diff.days == 0:
                return f"{diff.seconds // 3600} час назад"
            else:
                return f"{diff.days} дн назад"
        except:
            return "недавно"
    
    def _start_background_updates(self):
        """Запуск фоновых обновлений"""
        # Обновляем активные задачи каждые 10 секунд
        ui.timer(10.0, self._update_active_tasks)
    
    async def _update_active_tasks(self):
        """Обновление активных задач"""
        try:
            await self._fetch_active_tasks()
            await self._update_activity_feed()
        except Exception as e:
            logger.error(f"Failed to update active tasks: {e}")
    
    async def _refresh_dashboard(self):
        """Полное обновление dashboard"""
        ui.notify('Обновление данных...', type='info')
        
        try:
            await self._load_dashboard_data()
            await self._update_activity_feed()
            ui.notify('Данные обновлены', type='positive')
        except Exception as e:
            ui.notify(f'Ошибка обновления: {e}', type='negative')
    
    def _quick_generate(self):
        """Быстрая генерация - открывает модал выбора"""
        ui.notify('Быстрая генерация (в разработке)', type='info')
        # Здесь будет модал для быстрого выбора должности
    
    def _get_mock_catalog_stats(self) -> Dict[str, Any]:
        """Mock данные статистики каталога"""
        return {
            'departments': {'total_count': 545},
            'positions': {'total_count': 2844},
            'cache_status': {'departments_cached': True}
        }


class DashboardPage:
    """
    @doc
    Полная страница Dashboard для использования в routing.
    
    Examples:
      python> page = DashboardPage(api_client)
      python> await page.render()
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.dashboard = DashboardComponent(api_client)
    
    async def render(self):
        """
        @doc
        Рендеринг полной страницы dashboard.
        
        Examples:
          python> await dashboard_page.render()
        """
        # Настройка страницы
        ui.page_title('Dashboard - A101 HR Profile Generator')
        
        # Контейнер страницы
        with ui.column().classes('w-full max-w-7xl mx-auto p-4'):
            await self.dashboard.create()


if __name__ == "__main__":
    print("✅ Dashboard component created successfully!")
    print("📋 Components:")
    print("  - DashboardComponent: Main dashboard logic")
    print("  - DashboardPage: Full page wrapper")
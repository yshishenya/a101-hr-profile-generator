"""
@doc
Основное NiceGUI приложение для фронтенда системы генерации профилей А101.

Интегрируется с FastAPI backend через REST API.
Использует JWT аутентификацию и Material Design интерфейс.

Examples:
  python> # Запуск приложения
  python> from main import main
  python> main()
"""

from nicegui import ui, app
import logging
import asyncio

logger = logging.getLogger(__name__)

# Импортируем компоненты и сервисы
try:
    # Relative imports для запуска как модуль
    from .components.ui.auth_component import AuthComponent
    from .components.ui.header_component import HeaderComponent
    from .components.ui.stats_component import StatsComponent
    # Модулярные компоненты
    from .pages.generator_page import GeneratorPage
    from .services.api_client import APIClient
    from .utils.config import FrontendConfig
except ImportError:
    # Absolute imports для прямого запуска
    from components.ui.auth_component import AuthComponent
    from components.ui.header_component import HeaderComponent
    from components.ui.stats_component import StatsComponent
    # Модулярные компоненты
    from pages.generator_page import GeneratorPage
    from services.api_client import APIClient
    from utils.config import FrontendConfig

# Конфигурация
config = FrontendConfig()

# Глобальный API клиент
api_client = APIClient(base_url=config.BACKEND_URL)



async def on_successful_login():
    """
    @doc
    Callback функция, вызываемая после успешной авторизации.

    Загружает статистику через упрощенный API client метод.

    Examples:
      python> # Вызывается автоматически из AuthComponent
      python> await on_successful_login()
    """
    logger.info("🔄 Loading dashboard stats after successful authentication...")

    try:
        # Предзагружаем статистику одним методом API клиента
        stats_data = await api_client.get_dashboard_stats()

        if stats_data:
            logger.info("✅ Dashboard stats loaded successfully")
            logger.debug(
                f"Stats: {stats_data['profiles_count']} profiles of {stats_data['positions_count']} positions"
            )
        else:
            logger.warning("⚠️ Dashboard stats loaded with fallback data")

    except Exception as e:
        logger.error(f"❌ Error loading dashboard stats: {e}")




@ui.page("/login")
async def login_page(redirect_to: str = "/") -> None:
    """
    @doc
    Страница авторизации с формой входа.

    Использует AuthComponent для отображения формы и обработки входа.
    После успешной авторизации перенаправляет пользователя.

    Examples:
      python> # Доступ по URL /login
      python> # Поддерживает redirect_to параметр
    """

    # Если пользователь уже авторизован, перенаправляем
    if app.storage.user.get("authenticated", False):
        ui.navigate.to(redirect_to)
        return

    # Настройка страницы
    ui.page_title("Авторизация - A101 HR Profile Generator")

    with ui.column().classes("w-full h-screen justify-center items-center"):
        with ui.card().classes("w-96 p-6"):
            # Логотип и заголовок
            with ui.row().classes("w-full justify-center mb-4"):
                ui.icon("business", size="48px").classes("text-primary")

            ui.label("A101 HR Profile Generator").classes(
                "text-h5 text-center w-full mb-2"
            )
            ui.label("Авторизация в системе").classes(
                "text-subtitle1 text-center w-full text-grey-6 mb-6"
            )

            # Компонент авторизации с callback для загрузки данных
            auth_component = AuthComponent(
                api_client, redirect_to, on_success=on_successful_login
            )
            await auth_component.create()


@ui.page("/")
async def main_page() -> None:
    """
    @doc
    Главная страница приложения - Home Dashboard.

    Отображается после успешной авторизации.
    Содержит статистику системы, быстрые действия и навигацию.

    Examples:
      python> # Доступна только авторизованным пользователям
      python> # Автоматическая проверка через middleware
    """

    # Проверка авторизации
    if not app.storage.user.get("authenticated", False):
        ui.navigate.to("/login?redirect_to=/")
        return

    # Unified header component
    header = HeaderComponent(api_client)
    await header.render(current_page="home")

    # Главный контент - Dashboard
    with ui.column().classes("w-full max-w-7xl mx-auto p-4"):
        # Dashboard со статистикой
        try:
            # Создаем компонент статистики
            stats = StatsComponent(api_client, style="dashboard")
            await stats.render()

            # Быстрые действия
            with ui.card().classes("w-full mb-6"):
                ui.label("🎯 Быстрые действия").classes("text-h6 q-mb-md")

                with ui.row().classes("w-full q-gutter-md"):
                    ui.button(
                        "🔍 Найти должность",
                        on_click=lambda: ui.navigate.to("/generator"),
                    ).classes("flex-1").props("size=lg color=primary")

                    ui.button(
                        "📋 Все профили", on_click=lambda: ui.navigate.to("/profiles")
                    ).classes("flex-1").props("size=lg color=secondary")

                    ui.button(
                        "📊 Статистика", on_click=lambda: ui.navigate.to("/analytics")
                    ).classes("flex-1").props("size=lg color=info")

            # Данные загружаются автоматически компонентом статистики
        except Exception as e:
            # Fallback если dashboard не загружается
            with ui.card().classes("w-full p-6 text-center"):
                ui.label("🚀 A101 HR Profile Generator").classes("text-h4 mb-4")
                ui.label("Добро пожаловать!").classes("text-h6 mb-4")

                ui.markdown(
                    f"""
        ### ❌ Ошибка загрузки dashboard: {e}

        Попробуйте:
        - Обновить страницу
        - Проверить подключение к серверу
        - Обратиться к администратору

        ### Быстрые ссылки:
        - [Генератор профилей](/generator)
        - [Все профили](/profiles)
        - [Статистика](/analytics)
        """
                ).classes("text-body1")


@ui.page("/generator")
async def generator_page() -> None:
    """
    @doc
    Страница генератора профилей должностей с интегрированным поиском.

    Единый интерфейс для:
    - Поиска должностей среди 4,376 позиций
    - Настройки параметров генерации
    - Запуска и отслеживания процесса генерации

    Examples:
      python> # Доступна только авторизованным пользователям
      python> # URL: /generator
    """

    # Проверка авторизации
    if not app.storage.user.get("authenticated", False):
        ui.navigate.to("/login?redirect_to=/generator")
        return

    ui.page_title("🎯 Генератор профилей - A101 HR")

    # Unified header component
    header = HeaderComponent(api_client)
    await header.render(current_page="generator")

    # Main content with unified styling - убираем max-width для более широкого поля поиска
    with ui.column().classes("w-full mx-auto p-4").style("max-width: none !important;"):
        # Создаем и рендерим новую композитную страницу
        generator_page_content = GeneratorPage(api_client)
        await generator_page_content.render()


async def logout() -> None:
    """
    @doc
    Выход пользователя из системы.

    Очищает пользовательскую сессию и перенаправляет на страницу входа.
    Отправляет запрос logout на backend для инвалидации токена.

    Examples:
      python> await logout()
      python> # Пользователь перенаправлен на /login
    """

    try:
        # Пытаемся сделать logout на backend
        await api_client.logout()
    except Exception as e:
        # Логируем ошибку, но продолжаем logout локально
        print(f"Ошибка logout на backend: {e}")

    # Очищаем локальную сессию
    app.storage.user.clear()

    # Уведомляем пользователя и перенаправляем
    ui.notify("Вы вышли из системы", type="positive")
    ui.navigate.to("/login")


def main():
    """
    @doc
    Запуск NiceGUI приложения.

    Конфигурирует и запускает frontend сервер на порту 8033.
    Подключается к backend API на порту 8022.

    Examples:
      python> main()
      python> # Сервер запущен на http://localhost:8033
    """

    print(f"🚀 Starting A101 HR Frontend on {config.HOST}:{config.PORT}")
    print(f"🔗 Backend URL: {config.BACKEND_URL}")

    # Настройка приложения
    ui.run(
        host=config.HOST,
        port=config.PORT,
        title="A101 HR Profile Generator",
        favicon="🏢",
        dark=None,  # Автоматический режим
        reload=config.DEBUG,
        show=config.DEBUG,  # Автоматически открыть браузер в debug режиме
        storage_secret=config.STORAGE_SECRET,  # Для app.storage.user
    )


@ui.page("/profiles")
async def profiles_page():
    """
    @doc
    Страница списка всех созданных профилей.

    Заглушка - будет разработана позднее.

    Examples:
      python> # Переход по /profiles показывает заглушку
    """
    # Проверка авторизации
    if not app.storage.user.get("authenticated", False):
        ui.navigate.to("/login")
        return

    # Заголовок страницы
    header_comp = HeaderComponent(api_client)
    await header_comp.create()

    # Основное содержимое
    with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
        ui.label("📋 Список профилей").classes("text-h4 font-bold text-primary")

        with ui.card().classes("w-full p-8"):
            with ui.column().classes("items-center gap-4"):
                ui.icon("🚧", size="4rem").classes("text-orange-500")
                ui.label("🚧 Страница в разработке").classes("text-h5 font-medium")
                ui.label("Здесь будет список всех созданных профилей должностей.").classes("text-body1 text-center")

                with ui.row().classes("gap-4 mt-4"):
                    ui.button("← Назад к генератору",
                            on_click=lambda: ui.navigate.to("/generator")).props("outlined")


@ui.page("/analytics")
async def analytics_page():
    """
    @doc
    Страница аналитики и статистики.

    Заглушка - будет разработана позднее.

    Examples:
      python> # Переход по /analytics показывает заглушку
    """
    # Проверка авторизации
    if not app.storage.user.get("authenticated", False):
        ui.navigate.to("/login")
        return

    # Заголовок страницы
    header_comp = HeaderComponent(api_client)
    await header_comp.create()

    # Основное содержимое
    with ui.column().classes("w-full max-w-6xl mx-auto p-6 gap-6"):
        ui.label("📈 Статистика и аналитика").classes("text-h4 font-bold text-primary")

        with ui.card().classes("w-full p-8"):
            with ui.column().classes("items-center gap-4"):
                ui.icon("🚧", size="4rem").classes("text-orange-500")
                ui.label("🚧 Страница в разработке").classes("text-h5 font-medium")
                ui.label("Здесь будут графики, метрики и аналитика по генерации профилей.").classes("text-body1 text-center")

                with ui.row().classes("gap-4 mt-4"):
                    ui.button("← Назад к генератору",
                            on_click=lambda: ui.navigate.to("/generator")).props("outlined")


if __name__ in {"__main__", "__mp_main__"}:
    main()

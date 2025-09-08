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
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Импортируем компоненты и сервисы
try:
  # Relative imports для запуска как модуль
  from .components.auth_component import AuthComponent
  from .services.api_client import APIClient
  from .utils.config import FrontendConfig
except ImportError:
  # Absolute imports для прямого запуска
  from components.auth_component import AuthComponent
  from services.api_client import APIClient
  from utils.config import FrontendConfig

# Конфигурация
config = FrontendConfig()

# Глобальный API клиент
api_client = APIClient(base_url=config.BACKEND_URL)

# Список страниц, не требующих авторизации
UNRESTRICTED_PAGES = {'/login'}


class AuthMiddleware(BaseHTTPMiddleware):
  """
  @doc
  Middleware для проверки авторизации пользователей.
  
  Перенаправляет неавторизованных пользователей на страницу входа.
  Проверяет валидность JWT токена через backend API.
  
  Examples:
    python> # Автоматически используется в NiceGUI app
    python> app.add_middleware(AuthMiddleware)
  """
  
  async def dispatch(self, request: Request, call_next):
    # Пропускаем статические файлы и API NiceGUI
    if (request.url.path.startswith('/_nicegui') or 
        request.url.path.startswith('/static') or
        request.url.path in UNRESTRICTED_PAGES):
      return await call_next(request)
    
    # Проверяем авторизацию
    if not app.storage.user.get('authenticated', False):
      return RedirectResponse(f'/login?redirect_to={request.url.path}')
    
    # Проверяем валидность токена
    token = app.storage.user.get('access_token')
    if token and not await api_client.validate_token(token):
      # Токен невалиден, очищаем сессию
      app.storage.user.clear()
      return RedirectResponse(f'/login?redirect_to={request.url.path}')
    
    return await call_next(request)


# Добавляем middleware к приложению
app.add_middleware(AuthMiddleware)


@ui.page('/login')
async def login_page(redirect_to: str = '/') -> None:
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
  if app.storage.user.get('authenticated', False):
    ui.navigate.to(redirect_to)
    return
  
  # Настройка страницы
  ui.page_title('Авторизация - A101 HR Profile Generator')
  
  with ui.column().classes('w-full h-screen justify-center items-center bg-grey-1'):
    with ui.card().classes('w-96 p-6'):
      # Логотип и заголовок
      with ui.row().classes('w-full justify-center mb-4'):
        ui.icon('business', size='48px').classes('text-primary')
      
      ui.label('A101 HR Profile Generator').classes('text-h5 text-center w-full mb-2')
      ui.label('Авторизация в системе').classes('text-subtitle1 text-center w-full text-grey-6 mb-6')
      
      # Компонент авторизации
      auth_component = AuthComponent(api_client, redirect_to)
      await auth_component.create()


@ui.page('/')
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
  
  # Получаем информацию о пользователе
  user_info = app.storage.user.get('user_info', {})
  username = user_info.get('username', 'Пользователь')
  full_name = user_info.get('full_name', username)
  
  # Заголовок с навигацией
  with ui.header().classes('bg-primary text-white shadow-2'):
    with ui.row().classes('w-full items-center justify-between px-4 py-2'):
      with ui.row().classes('items-center gap-4'):
        ui.label('A101 HR Profile Generator').classes('text-h6')
        
        # Навигационные ссылки
        ui.button('Главная', on_click=lambda: ui.navigate.to('/')).props('flat').classes('text-white')
        ui.button('Профили', on_click=lambda: ui.navigate.to('/profiles')).props('flat').classes('text-white')
        ui.button('История', on_click=lambda: ui.navigate.to('/history')).props('flat').classes('text-white')
      
      # Информация о пользователе и выход
      with ui.row().classes('items-center gap-2'):
        ui.icon('person').classes('text-lg')
        ui.label(f'{full_name}').classes('text-subtitle1')
        
        ui.button(
          'Выйти',
          icon='logout',
          on_click=lambda: logout()
        ).props('flat').classes('text-white')
  
  # Главный контент - Dashboard
  with ui.column().classes('w-full max-w-7xl mx-auto p-4'):
    # Импортируем и создаем dashboard
    try:
      try:
        # Relative imports для запуска как модуль
        from .components.dashboard_component import DashboardComponent
      except ImportError:
        # Absolute imports для прямого запуска
        from components.dashboard_component import DashboardComponent
      
      dashboard = DashboardComponent(api_client)
      await dashboard.create()
    except Exception as e:
      # Fallback если dashboard не загружается
      with ui.card().classes('w-full p-6 text-center'):
        ui.label('🚀 A101 HR Profile Generator').classes('text-h4 mb-4')
        ui.label(f'Добро пожаловать, {full_name}!').classes('text-h6 mb-4')
        
        ui.markdown(f"""
        ### ❌ Ошибка загрузки dashboard: {e}
        
        Попробуйте:
        - Обновить страницу
        - Проверить подключение к серверу
        - Обратиться к администратору
        
        ### Быстрые ссылки:
        - [Найти должность](/search)
        - [Все профили](/profiles)
        - [Статистика](/analytics)
        """).classes('text-body1')


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
  ui.notify('Вы вышли из системы', type='positive')
  ui.navigate.to('/login')


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
    title='A101 HR Profile Generator',
    favicon='🏢',
    dark=None,  # Автоматический режим
    reload=config.DEBUG,
    show=config.DEBUG,  # Автоматически открыть браузер в debug режиме
    storage_secret=config.STORAGE_SECRET  # Для app.storage.user
  )


if __name__ in {"__main__", "__mp_main__"}:
  main()
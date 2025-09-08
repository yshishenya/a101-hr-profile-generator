"""
@doc
Компонент аутентификации с Material Design интерфейсом.

Предоставляет форму входа в систему с валидацией ввода,
обработкой ошибок и интеграцией с backend API.

Examples:
  python> auth = AuthComponent(api_client, "/dashboard")  
  python> await auth.create()  # Создает UI компонент
"""

import asyncio
from typing import Optional, Callable, Awaitable

from nicegui import ui, app
from ..services.api_client import APIClient, APIError, handle_api_error


class AuthComponent:
  """
  @doc
  Компонент формы авторизации с Material Design.
  
  Интегрируется с APIClient для аутентификации пользователей.
  Поддерживает валидацию ввода и обработку ошибок.
  
  Examples:
    python> auth = AuthComponent(api_client, "/")
    python> await auth.create()
  """
  
  def __init__(
    self,
    api_client: APIClient,
    redirect_to: str = '/',
    on_success: Optional[Callable[[], Awaitable[None]]] = None
  ):
    self.api_client = api_client
    self.redirect_to = redirect_to
    self.on_success = on_success
    
    # UI элементы
    self.username_input: Optional[ui.input] = None
    self.password_input: Optional[ui.input] = None  
    self.remember_checkbox: Optional[ui.checkbox] = None
    self.login_button: Optional[ui.button] = None
    self.loading_spinner: Optional[ui.spinner] = None
    
    # Состояние
    self.is_loading = False
  
  async def create(self) -> None:
    
    """Creates a login form UI component with username and password fields."""
    with ui.column().classes('w-full gap-4'):
      # Поле логина
      self.username_input = ui.input(
        label='Логин',
        placeholder='Введите ваш логин'
      ).props('outlined clearable').classes('w-full')
      
      self.username_input.on('keydown.enter', self._handle_enter_key)
      
      # Поле пароля
      self.password_input = ui.input(
        label='Пароль',
        password=True,
        password_toggle_button=True,
        placeholder='Введите пароль'
      ).props('outlined clearable').classes('w-full')
      
      self.password_input.on('keydown.enter', self._handle_enter_key)
      
      # Чекбокс "Запомнить меня"
      self.remember_checkbox = ui.checkbox(
        'Запомнить меня',
        value=False
      ).classes('mt-2')
      
      # Кнопка входа
      with ui.row().classes('w-full justify-center mt-4'):
        self.login_button = ui.button(
          'Войти',
          icon='login',
          on_click=self._handle_login
        ).props('size=lg color=primary').classes('w-full')
        
      # Индикатор загрузки (скрытый по умолчанию)
      self.loading_spinner = ui.spinner(size='lg').classes('hidden')
      
      # Дополнительная информация
      with ui.row().classes('w-full justify-center mt-6'):
        ui.label('По умолчанию: admin/admin123 или hr/hr123').classes(
          'text-caption text-grey-6 text-center'
        )
  
  async def _handle_login(self) -> None:
    
    """Handle the login button press event.
    
    This asynchronous function validates user credentials, sends an authorization
    request,  and processes the result with appropriate notifications. It manages
    loading states and  handles both expected and unexpected errors, ensuring a
    smooth user experience during  the login process.
    """
    if self.is_loading:
      return
    
    # Получаем данные формы
    username = self.username_input.value.strip() if self.username_input.value else ''
    password = self.password_input.value.strip() if self.password_input.value else ''
    remember_me = self.remember_checkbox.value if self.remember_checkbox else False
    
    # Валидация
    validation_error = self._validate_credentials(username, password)
    if validation_error:
      ui.notify(validation_error, type='negative', icon='warning')
      return
    
    # Показываем индикатор загрузки
    await self._set_loading(True)
    
    try:
      # Попытка авторизации
      result = await self.api_client.login(username, password, remember_me)
      
      if result.get('success'):
        # Сохраняем данные в сессию
        app.storage.user.update({
          'authenticated': True,
          'access_token': result.get('access_token'),
          'token_type': result.get('token_type', 'bearer'),
          'user_info': result.get('user_info', {}),
          'expires_in': result.get('expires_in', 24 * 3600)
        })
        
        # Уведомляем об успехе
        user_info = result.get('user_info', {})
        welcome_name = user_info.get('full_name', user_info.get('username', 'Пользователь'))
        ui.notify(f'Добро пожаловать, {welcome_name}!', type='positive', icon='check_circle')
        
        # Вызываем callback если есть
        if self.on_success:
          await self.on_success()
        
        # Небольшая задержка для показа уведомления
        await asyncio.sleep(0.5)
        
        # Перенаправляем
        ui.navigate.to(self.redirect_to)
        
      else:
        # Неожиданный ответ от API
        ui.notify('Неожиданная ошибка авторизации', type='negative', icon='error')
        
    except APIError as e:
      # Обработка ошибок API
      handle_api_error(e, "авторизации")
      
      # Дополнительная обработка для конкретных ошибок
      if e.status_code == 401:
        # Очищаем поля пароля при неверных учетных данных
        if self.password_input:
          self.password_input.value = ''
          # Устанавливаем фокус на поле логина
          await asyncio.sleep(0.1)
          if self.username_input:
            self.username_input.run_method('focus')
      
    except Exception as e:
      # Неожиданные ошибки
      ui.notify(f'Неожиданная ошибка: {str(e)}', type='negative', icon='error')
      
    finally:
      # Скрываем индикатор загрузки
      await self._set_loading(False)
  
  def _validate_credentials(self, username: str, password: str) -> Optional[str]:
    
    """Validate user credentials before submission.
    
    This function checks the completeness of the username and password fields  and
    enforces basic requirements. It returns an error message if validation  fails,
    or None if the validation is successful. The username must be at  least 3
    characters long, and the password must also meet a minimum length  requirement,
    albeit with a softer constraint for demonstration purposes.
    """
    if not username:
      return 'Введите логин'
    
    if not password:
      return 'Введите пароль'
    
    if len(username) < 3:
      return 'Логин должен содержать минимум 3 символа'
    
    if len(password) < 3:  # Более мягкое требование для демо
      return 'Пароль должен содержать минимум 3 символа'
    
    return None
  
  async def _handle_enter_key(self, _) -> None:
    """Handles the Enter key press in input fields."""
    await self._handle_login()
  
  async def _set_loading(self, loading: bool) -> None:
    
    """Manage the loading state of the form.
    
    This function shows or hides the loading indicator and enables or disables form
    elements during the execution of a request. It updates the properties of the
    username input, password input, remember checkbox, and login button based on
    the loading state. Additionally, it manages the visibility of the loading
    spinner to provide feedback to the user.
    """
    self.is_loading = loading
    
    # Управление состоянием элементов формы
    if self.username_input:
      self.username_input.props(f'disable={loading}')
    
    if self.password_input:
      self.password_input.props(f'disable={loading}')
    
    if self.remember_checkbox:
      self.remember_checkbox.props(f'disable={loading}')
    
    if self.login_button:
      if loading:
        self.login_button.props('loading disable')
        self.login_button._props['icon'] = 'hourglass_empty'
      else:
        self.login_button.props('loading=false disable=false')
        self.login_button._props['icon'] = 'login'
    
    # Индикатор загрузки
    if self.loading_spinner:
      if loading:
        self.loading_spinner.classes(remove='hidden')
      else:
        self.loading_spinner.classes(add='hidden')
  
  def clear_form(self) -> None:
    
    """Clears the authorization form fields."""
    if self.username_input:
      self.username_input.value = ''
    
    if self.password_input:
      self.password_input.value = ''
    
    if self.remember_checkbox:
      self.remember_checkbox.value = False
  
  def focus_username(self) -> None:
    
    """Set focus on the username input field."""
    if self.username_input:
      self.username_input.run_method('focus')


# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ UI КОМПОНЕНТЫ
# ============================================================================

class AuthCard:
  """
  @doc
  Обертка для формы авторизации в виде карточки Material Design.
  
  Предоставляет готовый UI контейнер для AuthComponent
  с логотипом, заголовком и стилизацией.
  
  Examples:
    python> card = AuthCard(api_client)
    python> await card.create()
  """
  
  def __init__(self, api_client: APIClient, redirect_to: str = '/'):
    self.api_client = api_client
    self.redirect_to = redirect_to
  
  async def create(self) -> None:
    
    """Creates an authorization card."""
    with ui.column().classes('w-full h-screen justify-center items-center bg-grey-1'):
      with ui.card().classes('w-96 p-6 elevation-8'):
        # Заголовок с иконкой
        with ui.row().classes('w-full justify-center mb-4'):
          ui.icon('business', size='48px').classes('text-primary')
        
        ui.label('A101 HR Profile Generator').classes('text-h5 text-center w-full mb-2')
        ui.label('Система генерации профилей должностей').classes(
          'text-subtitle2 text-center w-full text-grey-6 mb-6'
        )
        
        # Форма авторизации
        auth_component = AuthComponent(self.api_client, self.redirect_to)
        await auth_component.create()
        
        # Дополнительная информация
        with ui.expansion('Помощь', icon='help').classes('w-full mt-6'):
          ui.markdown("""
          **Учетные записи по умолчанию:**
          - **Администратор:** admin / admin123
          - **HR сотрудник:** hr / hr123
          
          **Возможности системы:**
          - Генерация профилей должностей с помощью AI
          - Каталог организационной структуры  
          - Экспорт в различных форматах
          - Мониторинг качества генерации
          """).classes('text-caption')


if __name__ == "__main__":
  # Демонстрация компонента
  print("✅ AuthComponent создан успешно!")
  print("📍 Основные возможности:")
  print("  - Material Design форма авторизации")
  print("  - Валидация ввода")
  print("  - Обработка ошибок API")
  print("  - Индикаторы загрузки")
  print("  - Интеграция с APIClient")
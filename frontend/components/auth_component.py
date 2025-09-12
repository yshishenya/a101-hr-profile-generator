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
        redirect_to: str = "/",
        on_success: Optional[Callable[[], Awaitable[None]]] = None,
    ):
        self.api_client = api_client
        self.redirect_to = redirect_to
        self.on_success = on_success

        # UI элементы
        self.username_input: Optional[ui.input] = None
        self.password_input: Optional[ui.input] = None
        self.remember_checkbox: Optional[ui.checkbox] = None
        self.login_button: Optional[ui.button] = None

        # Состояние
        self.is_loading = False

    async def create(self) -> None:
        """
        @doc
        Создание UI компонента формы авторизации.

        Создает форму входа с полями логина/пароля и кнопкой входа.
        Настраивает обработчики событий и валидацию.

        Examples:
          python> await auth_component.create()
          python> # Форма отображается в текущем UI контексте
        """

        with ui.column().classes("w-full gap-4"):
            # Поле логина
            self.username_input = (
                ui.input(label="Логин", placeholder="Введите ваш логин")
                .props("outlined clearable")
                .classes("w-full")
            )

            self.username_input.on("keydown.enter", self._handle_enter_key)

            # Поле пароля
            self.password_input = (
                ui.input(
                    label="Пароль",
                    password=True,
                    password_toggle_button=True,
                    placeholder="Введите пароль",
                )
                .props("outlined clearable")
                .classes("w-full")
            )

            self.password_input.on("keydown.enter", self._handle_enter_key)

            # Чекбокс "Запомнить меня"
            self.remember_checkbox = ui.checkbox("Запомнить меня", value=False).classes(
                "mt-2"
            )

            # Кнопка входа
            with ui.row().classes("w-full justify-center mt-4"):
                self.login_button = (
                    ui.button("Войти", icon="login", on_click=self._handle_login)
                    .props("size=lg color=primary")
                    .classes("w-full")
                )



    async def _handle_login(self) -> None:
        """
        @doc
        Обработчик нажатия кнопки входа.

        Выполняет валидацию данных, отправляет запрос авторизации
        и обрабатывает результат с соответствующими уведомлениями.

        Examples:
          python> # Вызывается автоматически при нажатии кнопки "Войти"
          python> await auth._handle_login()
        """

        if self.is_loading:
            return

        # Получаем данные формы
        username = (
            self.username_input.value.strip() if self.username_input.value else ""
        )
        password = (
            self.password_input.value.strip() if self.password_input.value else ""
        )
        remember_me = self.remember_checkbox.value if self.remember_checkbox else False

        # Валидация
        validation_error = self._validate_credentials(username, password)
        if validation_error:
            ui.notify(validation_error, type="negative", icon="warning")
            return

        # Показываем индикатор загрузки
        await self._set_loading(True)

        try:
            # Попытка авторизации
            result = await self.api_client.login(username, password, remember_me)

            if result.get("success"):
                # Сохраняем данные в сессию
                app.storage.user.update(
                    {
                        "authenticated": True,
                        "access_token": result.get("access_token"),
                        "token_type": result.get("token_type", "bearer"),
                        "user_info": result.get("user_info", {}),
                        "expires_in": result.get("expires_in", 24 * 3600),
                    }
                )

                # КРИТИЧЕСКИ ВАЖНО: Обновляем токены в глобальном api_client
                # После сохранения в storage, заставляем api_client перезагрузить токены
                self.api_client.reload_tokens_from_storage()

                # Уведомляем об успехе
                user_info = result.get("user_info", {})
                welcome_name = user_info.get(
                    "full_name", user_info.get("username", "Пользователь")
                )
                ui.notify(
                    f"Добро пожаловать, {welcome_name}!",
                    type="positive",
                    icon="check_circle",
                )

                # Вызываем callback если есть
                if self.on_success:
                    await self.on_success()

                # Небольшая задержка для показа уведомления
                await asyncio.sleep(0.5)

                # Перенаправляем
                ui.navigate.to(self.redirect_to)

            else:
                # Неожиданный ответ от API
                ui.notify(
                    "Неожиданная ошибка авторизации", type="negative", icon="error"
                )

        except APIError as e:
            # Обработка ошибок API
            handle_api_error(e, "авторизации")

            # Очищаем пароль при ошибке авторизации
            if e.status_code == 401:
                self.password_input.value = ""
                await asyncio.sleep(0.1)
                self.username_input.run_method("focus")

        except Exception as e:
            # Неожиданные ошибки
            ui.notify(f"Неожиданная ошибка: {str(e)}", type="negative", icon="error")

        finally:
            # Скрываем индикатор загрузки
            await self._set_loading(False)

    def _validate_credentials(self, username: str, password: str) -> Optional[str]:
        """
        @doc
        Валидация учетных данных перед отправкой.

        Проверяет заполненность полей и базовые требования.
        Возвращает сообщение об ошибке или пустую строку если валидация прошла.

        Examples:
          python> error = auth._validate_credentials("", "pass")
          python> if error: print(error)  # "Введите логин"
        """

        if not username:
            return "Введите логин"

        if not password:
            return "Введите пароль"

        if len(username) < 3:
            return "Логин должен содержать минимум 3 символа"

        if len(password) < 3:  # Более мягкое требование для демо
            return "Пароль должен содержать минимум 3 символа"

        return None

    async def _handle_enter_key(self, _) -> None:
        """
        @doc
        Обработчик нажатия клавиши Enter в полях ввода.

        Автоматически запускает процесс авторизации при нажатии Enter
        в любом поле формы.

        Examples:
          python> # Автоматически вызывается при нажатии Enter
          python> # в полях логина или пароля
        """
        await self._handle_login()

    async def _set_loading(self, loading: bool) -> None:
        """
        @doc
        Управление состоянием загрузки формы.

        Показывает/скрывает индикатор загрузки и блокирует/разблокирует
        элементы формы во время выполнения запроса.

        Examples:
          python> await auth._set_loading(True)   # Показать загрузку
          python> await auth._set_loading(False)  # Скрыть загрузку
        """

        self.is_loading = loading

        # Управление состоянием элементов формы
        if self.username_input:
            self.username_input.props(f"disable={loading}")

        if self.password_input:
            self.password_input.props(f"disable={loading}")

        if self.remember_checkbox:
            self.remember_checkbox.props(f"disable={loading}")

        if self.login_button:
            if loading:
                self.login_button.props("loading disable")
                self.login_button._props["icon"] = "hourglass_empty"
            else:
                self.login_button.props("loading=false disable=false")
                self.login_button._props["icon"] = "login"







"""
@doc
HTTP клиент для взаимодействия с FastAPI backend.

Обеспечивает авторизацию через JWT токены, автоматическое обновление токенов,
и обработку ошибок API. Используется во всех frontend компонентах.

Examples:
  python> client = APIClient("http://localhost:8022")
  python> result = await client.login("admin", "admin123")
  python> if result["success"]: print("Logged in!")
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx
from nicegui import ui

logger = logging.getLogger(__name__)


@dataclass
class LoginCredentials:
    """Учетные данные для входа"""

    username: str
    password: str
    remember_me: bool = False


@dataclass
class UserInfo:
    """Информация о пользователе"""

    id: int
    username: str
    full_name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class APIError(Exception):
    """Исключение для ошибок API"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class APIClient:
    """
    @doc
    HTTP клиент для взаимодействия с FastAPI backend.

    Поддерживает JWT аутентификацию, автоматическое обновление токенов,
    и централизованную обработку ошибок API.

    Examples:
      python> client = APIClient("http://localhost:8022")
      python> await client.login("admin", "password")
      python> profile = await client.get_profile("123")
    """

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._remember_me: bool = False

        # HTTP клиент с настройками
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

        # Загружаем токены из NiceGUI storage
        self._load_tokens_from_storage()

    def _load_tokens_from_storage(self):
        """Загрузка токенов из NiceGUI storage и localStorage"""
        logger.debug("_load_tokens_from_storage: Starting token loading process")

        try:
            from nicegui import app

            # Загружаем из NiceGUI storage
            if hasattr(app, "storage") and hasattr(app.storage, "user"):
                token_data = app.storage.user.get("token_data")
                if token_data:
                    self._access_token = token_data.get("access_token")
                    expires_timestamp = token_data.get("expires_timestamp")
                    self._remember_me = token_data.get("remember_me", False)
                    
                    # Восстанавливаем expires_at из timestamp
                    if expires_timestamp:
                        self._token_expires_at = datetime.fromtimestamp(expires_timestamp)
                        
                        # Проверяем не истек ли токен
                        if datetime.now() >= self._token_expires_at:
                            logger.info("Token expired, clearing from storage")
                            self._clear_expired_token()
                            return
                    
                    if self._access_token:
                        logger.info("Loaded access token from NiceGUI storage")
                        return

            # Если remember_me был установлен, пробуем загрузить из localStorage
            try:
                from nicegui import ui
                if hasattr(ui, "run_javascript"):
                    token_data_str = ui.run_javascript(
                        'localStorage.getItem("hr_token_data")', timeout=1.0
                    )
                    
                    if token_data_str:
                        import json
                        token_data = json.loads(token_data_str)
                        self._access_token = token_data.get("access_token")
                        expires_timestamp = token_data.get("expires_timestamp")
                        self._remember_me = token_data.get("remember_me", False)
                        
                        # Восстанавливаем expires_at из timestamp
                        if expires_timestamp:
                            self._token_expires_at = datetime.fromtimestamp(expires_timestamp)
                            
                            # Проверяем не истек ли токен
                            if datetime.now() >= self._token_expires_at:
                                logger.info("Token expired, clearing from localStorage")
                                self._clear_expired_token()
                                return
                        
                        if self._access_token:
                            # Синхронизируем обратно в NiceGUI storage
                            if hasattr(app, "storage") and hasattr(app.storage, "user"):
                                app.storage.user["token_data"] = token_data
                            logger.info("Loaded access token from localStorage")
                            return

            except Exception as browser_e:
                logger.debug(f"Could not load from browser storage: {browser_e}")

        except Exception as e:
            logger.debug(f"Could not load tokens from storage: {e}")

        # Fallback: загружаем из environment variables (только для разработки)
        if not self._access_token:
            import os
            test_token = os.getenv("TEST_JWT_TOKEN")
            if test_token:
                self._access_token = test_token
                logger.info("✅ Loaded TEST_JWT_TOKEN from environment variables")
                
                # Сохраняем в NiceGUI storage без localStorage (test token)
                try:
                    from nicegui import app
                    if hasattr(app, "storage") and hasattr(app.storage, "user"):
                        app.storage.user["token_data"] = {
                            "access_token": self._access_token,
                            "remember_me": False,
                            "expires_timestamp": None  # Test token не истекает
                        }
                except Exception as save_e:
                    logger.debug(f"Could not save token to storage: {save_e}")

        logger.debug(
            f"_load_tokens_from_storage: Final token state={'present' if self._access_token else 'None/empty'}"
        )

    def _save_tokens_to_storage(self):
        """Сохранение токенов с учетом remember_me"""
        try:
            from nicegui import app
            import json

            if not self._access_token:
                return

            # Подготавливаем данные токена
            token_data = {
                "access_token": self._access_token,
                "remember_me": self._remember_me,
                "expires_timestamp": self._token_expires_at.timestamp() if self._token_expires_at else None
            }

            # Всегда сохраняем в NiceGUI storage (session storage)
            if hasattr(app, "storage") and hasattr(app.storage, "user"):
                app.storage.user["token_data"] = token_data
                app.storage.user["authenticated"] = True

            # Если remember_me=True, также сохраняем в localStorage
            if self._remember_me:
                try:
                    from nicegui import ui
                    if hasattr(ui, "run_javascript"):
                        token_data_str = json.dumps(token_data)
                        ui.run_javascript(
                            f'localStorage.setItem("hr_token_data", {json.dumps(token_data_str)})'
                        )
                        logger.debug("Saved token to localStorage (remember_me=True)")
                except Exception as browser_e:
                    logger.debug(f"Could not save to localStorage: {browser_e}")
            else:
                # Если remember_me=False, убираем из localStorage
                try:
                    from nicegui import ui
                    if hasattr(ui, "run_javascript"):
                        ui.run_javascript('localStorage.removeItem("hr_token_data")')
                        logger.debug("Removed token from localStorage (remember_me=False)")
                except Exception as browser_e:
                    logger.debug(f"Could not remove from localStorage: {browser_e}")

            logger.info(f"Saved tokens to storage (remember_me={self._remember_me})")
        except Exception as e:
            logger.debug(f"Could not save tokens to storage: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Получение заголовков авторизации"""
        if self._access_token:
            # DEBUG: Log token info (first 10 chars for security)
            token_preview = (
                self._access_token[:10] + "..."
                if len(self._access_token) > 10
                else self._access_token
            )
            logger.debug(
                f"_get_auth_headers: Creating Authorization header with token {token_preview}"
            )
            return {"Authorization": f"Bearer {self._access_token}"}

        logger.warning(
            "_get_auth_headers: No token available - returning empty headers"
        )
        return {}

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        @doc
        Выполнение HTTP запроса к API.

        Автоматически добавляет авторизационные заголовки,
        обрабатывает ошибки и логирует запросы.

        Examples:
          python> response = await client._make_request("POST", "/auth/login", {"username": "admin"})
          python> data = response["data"]
        """

        url = f"{self.base_url}{endpoint}"
        headers = {}

        # DEBUG: Log initial token state
        logger.debug(
            f"_make_request: require_auth={require_auth}, self._access_token={'present' if self._access_token else 'None/empty'}"
        )

        if require_auth:
            # Проверяем и обновляем токен при необходимости
            token_valid = await self._ensure_valid_token()
            logger.debug(f"_make_request: _ensure_valid_token returned {token_valid}")

            if not token_valid:
                logger.error(
                    f"_make_request: No valid token for {method} {endpoint}, raising APIError"
                )
                raise APIError("Не удалось получить валидный токен авторизации", 401)

            auth_headers = self._get_auth_headers()
            logger.debug(f"_make_request: auth_headers = {auth_headers}")
            headers.update(auth_headers)

        try:
            logger.debug(
                f"Making {method} request to {url} with headers: {list(headers.keys())}"
            )

            response = await self.client.request(
                method=method, url=url, json=data, params=params, headers=headers
            )

            # Логируем ответ
            logger.debug(f"Response {response.status_code} from {url}")

            # Проверяем статус
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass

                error_message = error_data.get("detail", f"HTTP {response.status_code}")
                raise APIError(
                    message=error_message,
                    status_code=response.status_code,
                    details=error_data,
                )

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout for request to {url}")
            raise APIError("Превышено время ожидания ответа от сервера")

        except httpx.NetworkError as e:
            logger.error(f"Network error for {url}: {e}")
            raise APIError(f"Ошибка сети: {str(e)}")

        except APIError:
            raise

        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            raise APIError(f"Неожиданная ошибка: {str(e)}")

    async def _ensure_valid_token(self) -> bool:
        """Проверка и автоматическое обновление токена при необходимости"""
        logger.debug(
            f"_ensure_valid_token: self._access_token={'present' if self._access_token else 'None/empty'}"
        )

        if not self._access_token:
            logger.warning("_ensure_valid_token: No access token available")
            return False

        # Проверяем срок действия токена
        if self._token_expires_at:
            now = datetime.now()
            
            # Если токен истек
            if now >= self._token_expires_at:
                logger.info("Access token expired, attempting refresh")
                return await self._refresh_token_internal()
            
            # Если токен истекает в ближайшие 5 минут - обновляем превентивно
            elif (self._token_expires_at - now).total_seconds() < 300:
                logger.info("Access token expires soon, refreshing preemptively")
                return await self._refresh_token_internal()

        logger.debug("_ensure_valid_token: Token is valid")
        return True
        
    async def _refresh_token_internal(self) -> bool:
        """Внутренний метод для обновления токена через /api/auth/refresh"""
        try:
            # Используем текущий токен для запроса обновления
            headers = {"Authorization": f"Bearer {self._access_token}"}
            
            response = await self.client.request(
                method="POST",
                url=f"{self.base_url}/api/auth/refresh",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("access_token"):
                    self._access_token = data["access_token"]
                    
                    # Обновляем время истечения
                    expires_in = data.get("expires_in", 24 * 3600)
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    # Сохраняем обновленный токен
                    self._save_tokens_to_storage()
                    
                    logger.info("Successfully refreshed access token")
                    return True
                    
            logger.error(f"Token refresh failed: {response.status_code}")
            self._clear_expired_token()
            return False
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            self._clear_expired_token()
            return False
            
    def _clear_expired_token(self):
        """Очищаем истекший токен из всех хранилищ"""
        self._access_token = None
        self._token_expires_at = None
        
        try:
            from nicegui import app, ui
            
            # Очищаем NiceGUI storage
            if hasattr(app, "storage") and hasattr(app.storage, "user"):
                app.storage.user.pop("token_data", None)
                app.storage.user.pop("authenticated", None)
            
            # Очищаем localStorage
            if hasattr(ui, "run_javascript"):
                ui.run_javascript('localStorage.removeItem("hr_token_data")')
                
        except Exception as e:
            logger.debug(f"Could not clear expired token: {e}")

    # ============================================================================
    # AUTHENTICATION API
    # ============================================================================

    async def login(
        self, username: str, password: str, remember_me: bool = False
    ) -> Dict[str, Any]:
        """
        @doc
        Авторизация пользователя в системе.

        Отправляет учетные данные на backend и сохраняет полученный JWT токен.
        Возвращает информацию о пользователе и статус авторизации.

        Examples:
          python> result = await client.login("admin", "admin123")
          python> if result["success"]: print("Successfully logged in")
        """

        login_data = {
            "username": username,
            "password": password,
            "remember_me": remember_me,
        }

        try:
            response = await self._make_request(
                "POST", "/api/auth/login", data=login_data, require_auth=False
            )

            # Сохраняем токены с учетом remember_me
            if response.get("access_token"):
                self._access_token = response["access_token"]
                self._remember_me = remember_me

                # Рассчитываем время истечения токена
                expires_in = response.get("expires_in", 24 * 3600)  # seconds
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                # Сохраняем с учетом remember_me
                self._save_tokens_to_storage()

                logger.info(f"Successfully logged in user: {username} (remember_me={remember_me})")

            return response

        except APIError as e:
            logger.error(f"Login failed for user {username}: {e.message}")
            raise

    async def logout(self) -> Dict[str, Any]:
        """
        @doc
        Выход пользователя из системы.

        Инвалидирует токен на backend и очищает локальные данные авторизации.

        Examples:
          python> result = await client.logout()
          python> print(result["message"])
        """

        try:
            response = await self._make_request("POST", "/api/auth/logout")

            # Очищаем все данные токенов
            self._clear_all_tokens()

            logger.info("Successfully logged out")
            return response

        except APIError as e:
            # Даже если backend logout не удался, очищаем локальные данные
            self._clear_all_tokens()
            logger.debug(f"Logout failed on backend (clearing local data): {e.message}")
            return {"success": True, "message": "Локальный выход выполнен"}
            
    def _clear_all_tokens(self):
        """Полная очистка всех токенов и связанных данных"""
        self._access_token = None
        self._token_expires_at = None
        self._remember_me = False

        try:
            from nicegui import app, ui
            
            # Очищаем NiceGUI storage
            if hasattr(app, "storage") and hasattr(app.storage, "user"):
                app.storage.user.pop("token_data", None)
                app.storage.user.pop("authenticated", None)
            
            # Очищаем localStorage
            if hasattr(ui, "run_javascript"):
                ui.run_javascript('localStorage.removeItem("hr_token_data")')
                logger.debug("Cleared tokens from all storages")
                
        except Exception as e:
            logger.debug(f"Could not clear token storages: {e}")

    async def refresh_token(self) -> bool:
        """
        @doc
        Публичный метод для обновления JWT токена.

        Получает новый access token с использованием текущего токена.
        Возвращает True если обновление успешно.

        Examples:
          python> success = await client.refresh_token()
          python> if success: print("Token refreshed")
        """
        return await self._refresh_token_internal()

    async def validate_token(self, token: Optional[str] = None) -> bool:
        """
        @doc
        Проверка валидности токена.

        Отправляет запрос на backend для проверки действительности токена.

        Examples:
          python> is_valid = await client.validate_token()
          python> if not is_valid: print("Need to login again")
        """

        if token:
            old_token = self._access_token
            self._access_token = token

        try:
            await self._make_request("GET", "/api/auth/validate")
            return True

        except APIError:
            return False

        finally:
            if token and "old_token" in locals():
                self._access_token = old_token

    async def get_current_user(self) -> Dict[str, Any]:
        """
        @doc
        Получение информации о текущем пользователе.

        Возвращает полную информацию об авторизованном пользователе.

        Examples:
          python> user_info = await client.get_current_user()
          python> print(user_info["username"])
        """

        return await self._make_request("GET", "/api/auth/me")

    # ============================================================================
    # SYSTEM API
    # ============================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        @doc
        Проверка состояния backend системы.

        Не требует авторизации. Возвращает статус всех компонентов системы.

        Examples:
          python> health = await client.health_check()
          python> print(health["status"])
        """

        return await self._make_request("GET", "/health", require_auth=False)

    # ============================================================================
    # CATALOG API (планируется)
    # ============================================================================

    async def get_departments(self) -> Dict[str, Any]:
        """Получение списка департаментов (будет реализовано)"""
        return await self._make_request("GET", "/api/catalog/departments")

    async def get_positions(self, department: str) -> Dict[str, Any]:
        """Получение должностей в департаменте (будет реализовано)"""
        return await self._make_request("GET", f"/api/catalog/positions/{department}")

    # ============================================================================
    # PROFILES API (планируется)
    # ============================================================================

    async def generate_profile(
        self, department: str, position: str, employee_name: str = None
    ) -> Dict[str, Any]:
        """Генерация профиля должности (будет реализовано)"""
        data = {"department": department, "position": position}
        if employee_name:
            data["employee_name"] = employee_name

        return await self._make_request("POST", "/api/generation/generate", data=data)

    async def get_profiles(self, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """Получение списка профилей (будет реализовано)"""
        params = {"limit": limit, "page": page}
        return await self._make_request("GET", "/api/profiles/", params=params)

    async def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """Получение конкретного профиля (будет реализовано)"""
        return await self._make_request("GET", f"/api/profiles/{profile_id}")

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def is_authenticated(self) -> bool:
        """Проверка состояния авторизации"""
        return bool(
            self._access_token
            and (not self._token_expires_at or datetime.now() < self._token_expires_at)
        )

    def get_token(self) -> Optional[str]:
        """Получение текущего токена"""
        return self._access_token

    def set_token(self, token: str, expires_in: int = 24 * 3600):
        """Установка токена вручную"""
        self._access_token = token
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

    # ========================================================================
    # DASHBOARD API METHODS
    # ========================================================================

    async def get_catalog_stats(self) -> Dict[str, Any]:
        """
        @doc
        Получение статистики каталога для dashboard.

        Examples:
          python> stats = await client.get_catalog_stats()
          python> print(f"Total positions: {stats['positions']['total_count']}")
        """
        return await self._make_request("GET", "/api/catalog/stats")

    async def get_departments_list(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        @doc
        Получение списка департаментов для navigation.

        Examples:
          python> deps = await client.get_departments_list()
          python> print(f"Found {len(deps['data']['departments'])} departments")
        """
        params = {"force_refresh": force_refresh} if force_refresh else None
        return await self._make_request(
            "GET", "/api/catalog/departments", params=params
        )

    async def get_positions_for_department(
        self, department: str, force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        @doc
        Получение должностей для конкретного департамента.

        Examples:
          python> positions = await client.get_positions_for_department("IT Department")
          python> print(f"Found {len(positions['data']['positions'])} positions")
        """
        params = {"force_refresh": force_refresh} if force_refresh else None
        return await self._make_request(
            "GET", f"/api/catalog/positions/{department}", params=params
        )

    async def search_departments(self, query: str) -> Dict[str, Any]:
        """
        @doc
        Поиск департаментов по запросу.

        Examples:
          python> results = await client.search_departments("архитект")
          python> print(f"Found {len(results['data']['departments'])} matches")
        """
        params = {"q": query}
        return await self._make_request("GET", "/api/catalog/search", params=params)

    async def search_positions(
        self, query: str, department: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        @doc
        Поиск должностей по запросу с опциональной фильтрацией по департаменту.

        Examples:
          python> results = await client.search_positions("разработчик")
          python> print(f"Found {len(results['data']['positions'])} positions")
          python> it_results = await client.search_positions("разработчик", "ДИТ")
          python> print(f"Found {len(it_results['data']['positions'])} IT positions")
        """
        params = {"q": query}
        if department:
            params["department"] = department
        return await self._make_request(
            "GET", "/api/catalog/search/positions", params=params
        )

    async def get_profiles_list(
        self,
        page: int = 1,
        limit: int = 20,
        department: Optional[str] = None,
        position: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        @doc
        Получение списка профилей с фильтрацией.

        Examples:
          python> profiles = await client.get_profiles_list(department="IT")
          python> print(f"Found {profiles['pagination']['total']} profiles")
        """
        params = {"page": page, "limit": limit}
        if department:
            params["department"] = department
        if position:
            params["position"] = position
        if search:
            params["search"] = search
        if status:
            params["status"] = status

        return await self._make_request("GET", "/api/profiles/", params=params)

    async def get_profile_by_id(self, profile_id: str) -> Dict[str, Any]:
        """
        @doc
        Получение конкретного профиля по ID.

        Examples:
          python> profile = await client.get_profile_by_id("uuid-here")
          python> print(f"Profile: {profile['position']}")
        """
        return await self._make_request("GET", f"/api/profiles/{profile_id}")

    async def start_profile_generation(
        self,
        department: str,
        position: str,
        employee_name: Optional[str] = None,
        temperature: float = 0.1,
        save_result: bool = True,
    ) -> Dict[str, Any]:
        """
        @doc
        Запуск генерации профиля должности.

        Examples:
          python> task = await client.start_profile_generation("IT", "Developer")
          python> print(f"Task ID: {task['task_id']}")
        """
        data = {
            "department": department,
            "position": position,
            "temperature": temperature,
            "save_result": save_result,
        }
        if employee_name:
            data["employee_name"] = employee_name

        return await self._make_request("POST", "/api/generation/start", data=data)

    async def get_generation_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        @doc
        Получение статуса задачи генерации.

        Examples:
          python> status = await client.get_generation_task_status(task_id)
          python> print(f"Progress: {status['task']['progress']}%")
        """
        return await self._make_request("GET", f"/api/generation/{task_id}/status")

    async def get_generation_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        @doc
        Получение результата генерации профиля.

        Examples:
          python> result = await client.get_generation_task_result(task_id)
          python> print(f"Profile generated: {result['success']}")
        """
        return await self._make_request("GET", f"/api/generation/{task_id}/result")

    async def cancel_generation_task(self, task_id: str) -> Dict[str, Any]:
        """
        @doc
        Отмена задачи генерации.

        Examples:
          python> result = await client.cancel_generation_task(task_id)
          python> print(f"Cancelled: {result['message']}")
        """
        return await self._make_request("DELETE", f"/api/generation/{task_id}")

    async def get_active_generation_tasks(self) -> List[Dict[str, Any]]:
        """
        @doc
        Получение активных задач генерации пользователя.

        Examples:
          python> tasks = await client.get_active_generation_tasks()
          python> print(f"Active tasks: {len(tasks)}")
        """
        return await self._make_request("GET", "/api/generation/tasks/active")

    # ============================================================================
    # DASHBOARD STATISTICS METHODS
    # ============================================================================

    async def get_dashboard_stats(self) -> Optional[Dict[str, Any]]:
        """
        @doc
        Получение единой статистики для dashboard.

        Оптимизированный метод для получения всей статистики одним запросом.
        Возвращает данные о департаментах, должностях, профилях и активных задачах.

        Examples:
          python> stats = await client.get_dashboard_stats()
          python> print(f"Positions: {stats['positions_count']}")
        """
        try:
            response = await self._make_request("GET", "/api/dashboard/stats/minimal")
            if response and response.get("success"):
                return response["data"]
            else:
                logger.warning("Failed to get dashboard stats from API")
                # Fallback данные для graceful degradation
                return {
                    "positions_count": 1553,
                    "profiles_count": 0,
                    "completion_percentage": 0.0,
                    "active_tasks_count": 0,
                    "last_updated": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            # Fallback данные при ошибке
            return {
                "positions_count": 1553,
                "profiles_count": 0,
                "completion_percentage": 0.0,
                "active_tasks_count": 0,
                "last_updated": datetime.now().isoformat(),
            }

    def reload_tokens_from_storage(self):
        """
        @doc
        Публичный метод для перезагрузки токенов из storage.

        Используется после логина или когда нужно обновить токены
        в уже существующем экземпляре APIClient.

        Examples:
          python> api_client.reload_tokens_from_storage()
          python> # Токены будут загружены из NiceGUI storage или localStorage
        """
        logger.info("reload_tokens_from_storage: Manual token reload requested")
        old_token_state = "present" if self._access_token else "None/empty"

        self._load_tokens_from_storage()

        new_token_state = "present" if self._access_token else "None/empty"
        logger.info(
            f"reload_tokens_from_storage: Token state changed from {old_token_state} to {new_token_state}"
        )

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()

    def __del__(self):
        """Cleanup при удалении объекта"""
        try:
            asyncio.create_task(self.close())
        except:
            pass


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def handle_api_error(error: APIError, context: str = "API request") -> None:
    """
    @doc
    Обработка ошибок API с пользовательскими уведомлениями.

    Отображает соответствующие уведомления в UI в зависимости от типа ошибки.

    Examples:
      python> try:
      python>   await client.login("wrong", "pass")
      python> except APIError as e:
      python>   handle_api_error(e, "login")
    """

    logger.error(f"{context} failed: {error.message}")

    # Определяем тип уведомления и сообщение
    if error.status_code == 401:
        ui.notify("Неверные учетные данные", type="negative", icon="lock")
    elif error.status_code == 403:
        ui.notify("Недостаточно прав доступа", type="negative", icon="block")
    elif error.status_code == 404:
        ui.notify("Ресурс не найден", type="negative", icon="search_off")
    elif error.status_code == 500:
        ui.notify("Ошибка сервера. Попробуйте позже", type="negative", icon="error")
    elif error.status_code and error.status_code >= 400:
        ui.notify(f"Ошибка: {error.message}", type="negative", icon="warning")
    else:
        ui.notify(
            f"Ошибка соединения: {error.message}", type="negative", icon="wifi_off"
        )


if __name__ == "__main__":
    # Простой тест API клиента
    async def test_client():
        client = APIClient("http://localhost:8022")

        try:
            health = await client.health_check()
            print(f"✅ Backend health: {health['status']}")

            # Тест неверного логина
            try:
                await client.login("wrong", "password")
            except APIError as e:
                print(f"❌ Expected login error: {e.message}")

        except APIError as e:
            print(f"❌ API Error: {e.message}")
        finally:
            await client.close()

    asyncio.run(test_client())

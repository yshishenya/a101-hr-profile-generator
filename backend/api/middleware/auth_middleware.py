"""
@doc JWT Authentication Middleware

Middleware для автоматической проверки JWT токенов в API layer.
Размещен здесь, так как отвечает за HTTP authentication.

Examples:
    python>
    middleware = JWTAuthMiddleware(app, auth_service)
    # Автоматически проверяет JWT токены для защищенных endpoints
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import logging

from ...services.auth_service import auth_service

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    @doc Middleware для автоматической проверки JWT токенов

    Применяется ко всем защищенным endpoints автоматически.
    Размещен в API layer так как обрабатывает HTTP requests.

    Examples:
        python>
        app.add_middleware(JWTAuthMiddleware, auth_service=auth_service)
        # Все API endpoints будут проверять JWT автоматически
    """

    # Endpoints, которые не требуют авторизации
    EXEMPT_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/validate",
        "/static",
    }

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        @doc Обработка запроса с проверкой авторизации

        Examples:
            python>
            # Middleware автоматически вызывается для каждого запроса
            # Проверяет Authorization header и валидирует JWT токен
        """

        # Проверяем, нужна ли авторизация для этого пути
        path = request.url.path

        # Пропускаем неавторизованные пути
        if (
            path in self.EXEMPT_PATHS
            or path.startswith("/static/")
            or path.startswith("/docs")
            or path.startswith("/redoc")
        ):
            return await call_next(request)

        # Извлекаем токен из заголовка Authorization
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error": "Требуется авторизация",
                    "detail": "Отсутствует токен авторизации",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        # Извлекаем токен
        token = auth_header.split(" ")[1]

        # Проверяем токен через services layer (допустимо в API layer)
        if auth_service is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Сервис авторизации не инициализирован",
                    "detail": "Internal server error",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        user_data = auth_service.verify_token(token)

        if not user_data:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error": "Недействительный токен",
                    "detail": "Токен авторизации недействителен или истек",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        # Добавляем информацию о пользователе в request state
        request.state.user = user_data

        # Продолжаем обработку запроса
        return await call_next(request)
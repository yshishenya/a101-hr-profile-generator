"""
@doc Request Logging Middleware

Middleware для детального логирования HTTP запросов в API layer.

Examples:
    python>
    app.add_middleware(RequestLoggingMiddleware)
    # Логирует все HTTP запросы с метриками производительности
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import logging

from ...services.auth_service import auth_service

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    @doc Middleware для детального логирования HTTP запросов

    Расширенная версия базового логирования из main.py.
    Размещен в API layer так как обрабатывает HTTP requests.

    Examples:
        python>
        app.add_middleware(RequestLoggingMiddleware)
        # 📥 GET /api/profiles - user:admin from 127.0.0.1
        # 📤 GET /api/profiles - ✅ 200 - user:admin - 0.123s
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        @doc Логирование запроса и ответа с детальными метриками

        Examples:
            python>
            # Автоматически логирует каждый HTTP запрос
            # Включает IP, user agent, время выполнения, статус код
        """

        start_time = time.time()

        # Информация о запросе
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Определяем пользователя если есть авторизация
        user_info = "anonymous"
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                if auth_service is not None:
                    user_data = auth_service.verify_token(token)
                    if user_data:
                        user_info = f"user:{user_data['username']}"
            except Exception:
                # AuthService issues - не падаем, просто логируем как anonymous
                pass

        logger.info(f"📥 {method} {path} - {user_info} from {client_ip}")

        try:
            # Выполняем запрос
            response = await call_next(request)

            # Вычисляем время выполнения
            process_time = time.time() - start_time

            # Логируем ответ
            status_code = response.status_code
            status_emoji = (
                "✅"
                if 200 <= status_code < 300
                else "⚠️" if 300 <= status_code < 400 else "❌"
            )

            logger.info(
                f"📤 {method} {path} - {status_emoji} {status_code} - "
                f"{user_info} - {process_time:.3f}s"
            )

            # Добавляем заголовки с метриками
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = str(hash(f"{client_ip}-{start_time}"))

            return response

        except Exception as e:
            process_time = time.time() - start_time

            logger.error(
                f"💥 {method} {path} - ERROR - {user_info} - {process_time:.3f}s - {str(e)}"
            )

            # Возвращаем структурированную ошибку
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Внутренняя ошибка сервера",
                    "detail": "Произошла непредвиденная ошибка",
                    "timestamp": datetime.now().isoformat(),
                    "path": path,
                },
            )
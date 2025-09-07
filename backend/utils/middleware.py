"""
Middleware для системы генерации профилей должностей А101.

Содержит middleware для:
- JWT авторизации
- Логирования запросов
- Обработки ошибок
- CORS
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import logging

from ..services.auth_service import auth_service

logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для автоматической проверки JWT токенов.
    
    Применяется ко всем защищенным endpoints автоматически.
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
        "/static"
    }
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с проверкой авторизации"""
        
        # Проверяем, нужна ли авторизация для этого пути
        path = request.url.path
        
        # Пропускаем неавторизованные пути
        if (path in self.EXEMPT_PATHS or 
            path.startswith("/static/") or 
            path.startswith("/docs") or 
            path.startswith("/redoc")):
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
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Извлекаем токен
        token = auth_header.split(" ")[1]
        
        # Проверяем токен
        user_data = auth_service.verify_token(token)
        
        if not user_data:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "error": "Недействительный токен",
                    "detail": "Токен авторизации недействителен или истек",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Добавляем информацию о пользователе в request state
        request.state.user = user_data
        
        # Продолжаем обработку запроса
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для детального логирования HTTP запросов.
    
    Расширенная версия базового логирования из main.py.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Логирование запроса и ответа с детальными метриками"""
        
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
            user_data = auth_service.verify_token(token)
            if user_data:
                user_info = f"user:{user_data['username']}"
        
        logger.info(f"📥 {method} {path} - {user_info} from {client_ip}")
        
        try:
            # Выполняем запрос
            response = await call_next(request)
            
            # Вычисляем время выполнения
            process_time = time.time() - start_time
            
            # Логируем ответ
            status_code = response.status_code
            status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"
            
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Внутренняя ошибка сервера",
                    "detail": "Произошла непредвиденная ошибка",
                    "timestamp": datetime.now().isoformat(),
                    "path": path
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления security headers.
    
    Добавляет важные заголовки безопасности ко всем ответам.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Добавление security headers к ответу"""
        
        response = await call_next(request)
        
        # Добавляем security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Строгий Content Security Policy для производства
        # В разработке более мягкий CSP для работы с документацией
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:;"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


async def get_request_user(request: Request) -> dict:
    """
    Utility function для получения пользователя из request state.
    
    Используется в endpoints для получения текущего пользователя.
    """
    return getattr(request.state, 'user', None)


if __name__ == "__main__":
    print("✅ Middleware modules created successfully!")
    print("🔧 Available middleware:")
    print("  - JWTAuthMiddleware: Automatic JWT token validation")
    print("  - RequestLoggingMiddleware: Detailed request/response logging") 
    print("  - SecurityHeadersMiddleware: Security headers for all responses")
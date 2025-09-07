"""
API endpoints для аутентификации пользователей системы генерации профилей А101.

Endpoints:
- POST /api/auth/login - Авторизация пользователя
- POST /api/auth/logout - Выход из системы  
- POST /api/auth/refresh - Обновление токена
- GET /api/auth/me - Информация о текущем пользователе
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.schemas import (
    LoginRequest, LoginResponse, UserInfo, BaseResponse, ErrorResponse
)
from ..services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

# Создаем роутер для auth endpoints
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# HTTP Bearer схема для JWT токенов
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency для получения текущего пользователя из JWT токена.
    Используется для защищенных endpoints.
    """
    token = credentials.credentials
    user_data = auth_service.verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


@auth_router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    request: Request
):
    """
    Авторизация пользователя в системе.
    
    Процесс авторизации:
    1. Проверка учетных данных пользователя  
    2. Создание JWT токена
    3. Создание пользовательской сессии
    4. Возврат токена и информации о пользователе
    
    Returns:
        LoginResponse с JWT токеном и информацией о пользователе
    """
    try:
        # Получаем информацию о клиенте
        user_agent = request.headers.get("user-agent", "Unknown")
        client_ip = request.client.host if request.client else "Unknown"
        
        logger.info(f"Login attempt for user: {login_request.username} from IP: {client_ip}")
        
        # Выполняем авторизацию
        result = await auth_service.login(
            login_request, 
            user_agent=user_agent,
            ip_address=client_ip
        )
        
        if result:
            logger.info(f"Successful login for user: {login_request.username}")
            return result
        else:
            logger.warning(f"Failed login attempt for user: {login_request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user {login_request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при авторизации"
        )


@auth_router.post("/logout", response_model=BaseResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Выход пользователя из системы.
    
    Инвалидирует все активные сессии пользователя.
    """
    try:
        user_id = current_user["user_id"]
        username = current_user["username"]
        
        # Инвалидируем все сессии пользователя
        auth_service.invalidate_user_sessions(user_id)
        
        logger.info(f"User {username} logged out successfully")
        
        return BaseResponse(
            success=True,
            message="Вы успешно вышли из системы"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выходе из системы"
        )


@auth_router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Получение информации о текущем авторизованном пользователе.
    
    Returns:
        UserInfo с полной информацией о пользователе
    """
    try:
        user_data = current_user["user"]
        
        return UserInfo(
            id=user_data["id"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"]
        )
        
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения информации о пользователе"
        )


@auth_router.post("/refresh", response_model=LoginResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Обновление JWT токена.
    
    Создает новый токен с тем же временем жизни для текущего пользователя.
    """
    try:
        user_data = current_user["user"]
        
        # Создаем новый токен
        new_token = auth_service.create_access_token(user_data)
        
        user_info = UserInfo(
            id=user_data["id"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            last_login=user_data["last_login"]
        )
        
        logger.info(f"Token refreshed for user: {user_data['username']}")
        
        return LoginResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24 hours in seconds
            user_info=user_info,
            success=True,
            message="Токен обновлен успешно"
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления токена"
        )


@auth_router.get("/validate", response_model=BaseResponse)
async def validate_token(current_user: dict = Depends(get_current_user)):
    """
    Проверка валидности текущего токена.
    
    Endpoint для frontend для проверки, что токен все еще действителен.
    """
    return BaseResponse(
        success=True,
        message=f"Токен действителен для пользователя {current_user['username']}"
    )


# Дополнительные utility функции для использования в других модулях

def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Опциональная авторизация - не вызывает исключение если токен невалиден.
    Возвращает None если пользователь не авторизован.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return auth_service.verify_token(token)


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency для endpoints, требующих admin права.
    В текущей реализации проверяет username == 'admin'
    """
    if current_user["username"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    return current_user


if __name__ == "__main__":
    print("✅ Auth API endpoints created successfully!")
    print("📍 Available endpoints:")
    print("  - POST /api/auth/login")
    print("  - POST /api/auth/logout") 
    print("  - POST /api/auth/refresh")
    print("  - GET /api/auth/me")
    print("  - GET /api/auth/validate")
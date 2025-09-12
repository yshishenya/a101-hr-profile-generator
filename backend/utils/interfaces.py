"""
@doc Utility interfaces for dependency injection and clean architecture

Минимальный набор интерфейсов для разрыва архитектурных зависимостей.
Следует принципу YAGNI - создаем только необходимые абстракции.

Examples:
    python>
    # Использование в middleware
    auth: AuthInterface = AuthService()
    user_data = auth.verify_token(token)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AuthInterface(ABC):
    """
    @doc Интерфейс для аутентификации пользователей
    
    Разрывает зависимость utils.middleware → services.auth_service
    Позволяет middleware быть независимым от конкретной реализации аутентификации.
    
    Examples:
        python>
        class JWTAuthMiddleware:
            def __init__(self, auth: AuthInterface):
                self.auth = auth
                
            async def authenticate(self, token: str):
                return self.auth.verify_token(token)
    """
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Проверка и декодирование токена аутентификации.
        
        Args:
            token: JWT токен для проверки
            
        Returns:
            Optional[Dict]: Данные пользователя если токен валиден, None если нет
        """
        pass
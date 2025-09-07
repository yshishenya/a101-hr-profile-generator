"""
@doc Custom exception classes for A101 HR Profile Generator

Реализует стандартизированные исключения для различных типов ошибок системы.
Обеспечивает консистентную обработку ошибок с правильными HTTP статусами.

Examples:
    python>
    # Бизнес-логика ошибки
    raise ValidationError("Invalid department name", field="department")
    
    # Ошибка базы данных  
    raise DatabaseError("Connection failed", operation="SELECT")
    
    # Ошибка внешнего API
    raise ExternalAPIError("OpenRouter timeout", service="openrouter", status_code=503)
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException


class BaseAppException(HTTPException):
    """
    @doc Базовый класс для всех исключений приложения
    
    Расширяет FastAPI HTTPException с дополнительными метаданными
    для улучшенного логирования и отладки.
    
    Examples:
        python>
        # Создание базового исключения
        raise BaseAppException(
            status_code=400,
            message="Something went wrong",
            error_code="BASE_ERROR",
            details={"field": "value"}
        )
    """
    
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        internal_message: Optional[str] = None
    ):
        self.error_code = error_code
        self.message = message
        self.internal_message = internal_message or message
        self.details = details or {}
        
        # FastAPI HTTPException detail
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "details": self.details
            }
        )


class ValidationError(BaseAppException):
    """
    @doc Ошибки валидации входных данных
    
    Используется для ошибок валидации запросов, неправильных параметров,
    нарушений бизнес-правил и constraint violations.
    
    Examples:
        python>
        # Ошибка валидации поля
        raise ValidationError("Department name is required", field="department")
        
        # Множественные ошибки валидации
        raise ValidationError(
            "Multiple validation errors",
            errors=[
                {"field": "department", "message": "Required field"},
                {"field": "position", "message": "Invalid format"}
            ]
        )
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if errors:
            details["validation_errors"] = errors
        
        super().__init__(
            status_code=400,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs
        )


class AuthenticationError(BaseAppException):
    """
    @doc Ошибки аутентификации и авторизации
    
    Examples:
        python>
        # Неверные учетные данные
        raise AuthenticationError("Invalid credentials")
        
        # Истекший токен
        raise AuthenticationError("Token expired", error_code="TOKEN_EXPIRED")
    """
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            status_code=401,
            message=message,
            error_code=kwargs.get("error_code", "AUTH_ERROR"),
            **kwargs
        )


class AuthorizationError(BaseAppException):
    """
    @doc Ошибки авторизации (недостаточно прав)
    
    Examples:
        python>
        # Недостаточно прав
        raise AuthorizationError("Insufficient permissions", required_role="admin")
    """
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            status_code=403,
            message=message,
            error_code="AUTHORIZATION_ERROR",
            **kwargs
        )


class NotFoundError(BaseAppException):
    """
    @doc Ошибки "не найдено"
    
    Examples:
        python>
        # Профиль не найден
        raise NotFoundError("Profile not found", resource="profile", resource_id="123")
        
        # Департамент не найден
        raise NotFoundError("Department not found", resource="department", name="IT")
    """
    
    def __init__(self, message: str, resource: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if resource:
            details["resource"] = resource
        
        # Handle extra kwargs by adding them to details instead of passing to parent
        extra_kwargs = {}
        for key, value in kwargs.items():
            if key not in ['internal_message']:
                details[key] = value
            else:
                extra_kwargs[key] = value
            
        super().__init__(
            status_code=404,
            message=message,
            error_code="NOT_FOUND",
            details=details,
            **extra_kwargs
        )


class DatabaseError(BaseAppException):
    """
    @doc Ошибки базы данных
    
    Examples:
        python>
        # Ошибка подключения
        raise DatabaseError("Connection failed", operation="connect")
        
        # Constraint violation
        raise DatabaseError("Unique constraint violation", 
                           operation="INSERT", table="profiles")
    """
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        
        # Handle extra kwargs by adding them to details
        internal_message = kwargs.pop("internal_message", None)
        for key, value in kwargs.items():
            details[key] = value
        
        super().__init__(
            status_code=500,
            message="Database operation failed",
            error_code="DATABASE_ERROR",
            details=details,
            internal_message=internal_message or message
        )


class ExternalAPIError(BaseAppException):
    """
    @doc Ошибки внешних API (OpenRouter, Langfuse)
    
    Examples:
        python>
        # OpenRouter API недоступен
        raise ExternalAPIError("OpenRouter API timeout", 
                              service="openrouter", status_code=503)
        
        # Langfuse ошибка
        raise ExternalAPIError("Langfuse connection failed", 
                              service="langfuse", status_code=500)
    """
    
    def __init__(
        self,
        message: str,
        service: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.pop("details", {})
        details["service"] = service
        if status_code:
            details["external_status_code"] = status_code
        
        # Handle extra kwargs by adding them to details
        internal_message = kwargs.pop("internal_message", None)
        for key, value in kwargs.items():
            details[key] = value
        
        super().__init__(
            status_code=503,  # Service Unavailable
            message=f"External service '{service}' error",
            error_code="EXTERNAL_API_ERROR",
            details=details,
            internal_message=internal_message or message
        )


class ConfigurationError(BaseAppException):
    """
    @doc Ошибки конфигурации системы
    
    Examples:
        python>
        # Отсутствует API ключ
        raise ConfigurationError("OpenRouter API key not configured", 
                                config_key="OPENROUTER_API_KEY")
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        
        # Handle extra kwargs by adding them to details
        internal_message = kwargs.pop("internal_message", None)
        for key, value in kwargs.items():
            details[key] = value
            
        super().__init__(
            status_code=500,
            message="Configuration error",
            error_code="CONFIG_ERROR",
            details=details,
            internal_message=internal_message or message
        )


class ProfileGenerationError(BaseAppException):
    """
    @doc Ошибки процесса генерации профилей
    
    Examples:
        python>
        # Ошибка LLM генерации
        raise ProfileGenerationError("LLM generation failed", 
                                   stage="generation", model="gemini-2.5-flash")
        
        # Ошибка валидации результата
        raise ProfileGenerationError("Generated profile validation failed", 
                                   stage="validation", score=0.3)
    """
    
    def __init__(
        self,
        message: str,
        stage: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.pop("details", {})
        if stage:
            details["generation_stage"] = stage
        if task_id:
            details["task_id"] = task_id
        
        # Handle extra kwargs by adding them to details
        internal_message = kwargs.pop("internal_message", None)
        for key, value in kwargs.items():
            details[key] = value
            
        super().__init__(
            status_code=422,  # Unprocessable Entity
            message="Profile generation failed",
            error_code="GENERATION_ERROR",
            details=details,
            internal_message=internal_message or message
        )


class RateLimitError(BaseAppException):
    """
    @doc Ошибки превышения лимитов (rate limiting)
    
    Examples:
        python>
        # Превышен лимит API запросов
        raise RateLimitError("API rate limit exceeded", 
                           limit=100, reset_time=3600)
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        reset_time: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.pop("details", {})
        if limit:
            details["limit"] = limit
        if reset_time:
            details["reset_time"] = reset_time
            
        super().__init__(
            status_code=429,  # Too Many Requests
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            **kwargs
        )


# Convenience exception mapping for common HTTP status codes
EXCEPTION_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
    422: ProfileGenerationError,
    429: RateLimitError,
    500: DatabaseError,
    503: ExternalAPIError,
}
"""
@doc Global exception handlers for FastAPI application

Централизованная обработка всех исключений приложения с логированием,
стандартизированными ответами и мониторингом ошибок.

Examples:
    python>
    # Использование в FastAPI приложении
    from .utils.exception_handlers import setup_exception_handlers
    setup_exception_handlers(app)
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    BaseAppException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    ExternalAPIError,
    ConfigurationError,
    ProfileGenerationError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    status_code: int = 500,
) -> Dict[str, Any]:
    """
    @doc Создание стандартизированного ответа об ошибке

    Examples:
        python>
        # Базовый error response
        response = create_error_response("VALIDATION_ERROR", "Invalid input")

        # С дополнительными деталями
        response = create_error_response(
            "DATABASE_ERROR",
            "Connection failed",
            details={"table": "profiles", "operation": "SELECT"},
            request_id="req-123"
        )
    """
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
        },
    }


async def base_app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """
    @doc Обработчик для всех BaseAppException

    Examples:
        python>
        # Автоматически вызывается FastAPI при возникновении BaseAppException
        raise ValidationError("Invalid department")
        # → {"success": false, "error": {...}}
    """
    request_id = str(uuid.uuid4())

    # Логирование с соответствующим уровнем
    log_level = logging.ERROR
    if exc.status_code < 500:
        log_level = logging.WARNING

    logger.log(
        log_level,
        f"[{request_id}] {exc.error_code}: {exc.internal_message} "
        f"(Status: {exc.status_code}) - {request.method} {request.url}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "url": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=request_id,
            status_code=exc.status_code,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    @doc Обработчик стандартных HTTPException

    Examples:
        python>
        # FastAPI HTTPException → стандартизированный формат
        raise HTTPException(status_code=404, detail="Not found")
        # → {"success": false, "error": {...}}
    """
    request_id = str(uuid.uuid4())

    # Определяем error_code на основе status_code
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }

    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    logger.warning(
        f"[{request_id}] HTTP {exc.status_code}: {message} - {request.method} {request.url}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error_code=error_code,
            message=message,
            request_id=request_id,
            status_code=exc.status_code,
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    @doc Обработчик ошибок валидации FastAPI/Pydantic

    Examples:
        python>
        # Pydantic validation error → структурированный ответ
        # Автоматически вызывается при неправильном JSON в запросе
    """
    request_id = str(uuid.uuid4())

    # Форматируем ошибки валидации
    validation_errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            {
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
            }
        )

    logger.warning(
        f"[{request_id}] Validation error: {len(validation_errors)} fields - "
        f"{request.method} {request.url}",
        extra={
            "request_id": request_id,
            "validation_errors": validation_errors,
            "url": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=422,
        content=create_error_response(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"validation_errors": validation_errors},
            request_id=request_id,
            status_code=422,
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    @doc Обработчик для всех неперехваченных исключений

    Examples:
        python>
        # Любое неожиданное исключение → безопасный ответ пользователю
        # + полное логирование для разработчиков
    """
    request_id = str(uuid.uuid4())

    # Полное логирование с traceback для отладки
    logger.error(
        f"[{request_id}] Unhandled exception: {type(exc).__name__}: {str(exc)} - "
        f"{request.method} {request.url}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "url": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "traceback": traceback.format_exc(),
        },
    )

    # Безопасный ответ для пользователя (не раскрываем внутренние детали)
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            error_code="INTERNAL_ERROR",
            message="An internal server error occurred",
            details={"request_id": request_id},
            request_id=request_id,
            status_code=500,
        ),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    @doc Регистрация всех обработчиков исключений в FastAPI приложении

    Examples:
        python>
        # В main.py
        from .utils.exception_handlers import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)
    """

    # Специфические exception handlers (в порядке приоритета)
    app.add_exception_handler(BaseAppException, base_app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Generic handler для всех остальных исключений
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("✅ Exception handlers registered successfully")


# Utility функции для создания стандартных исключений
def create_validation_error(
    message: str, field: str = None, **kwargs
) -> ValidationError:
    """Helper для создания ValidationError"""
    return ValidationError(message=message, field=field, **kwargs)


def create_not_found_error(
    resource: str, resource_id: str = None, **kwargs
) -> NotFoundError:
    """Helper для создания NotFoundError"""
    message = f"{resource.title()} not found"
    details = kwargs.get("details", {})
    if resource_id:
        details["resource_id"] = resource_id
    return NotFoundError(message=message, resource=resource, details=details, **kwargs)


def create_database_error(operation: str, table: str = None, **kwargs) -> DatabaseError:
    """Helper для создания DatabaseError"""
    return DatabaseError(
        message=f"Database {operation} failed",
        operation=operation,
        table=table,
        **kwargs,
    )


def create_external_api_error(
    service: str, operation: str, **kwargs
) -> ExternalAPIError:
    """Helper для создания ExternalAPIError"""
    return ExternalAPIError(
        message=f"{service} {operation} failed", service=service, **kwargs
    )

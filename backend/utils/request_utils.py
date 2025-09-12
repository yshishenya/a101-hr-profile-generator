"""
@doc Request Utilities

Утилиты для работы с HTTP requests в utils layer.

Examples:
    python>
    from utils.request_utils import get_request_user
    user = get_request_user(request)
"""

from fastapi import Request
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_request_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    @doc Utility function для получения пользователя из request state

    Используется в endpoints для получения текущего пользователя
    после обработки JWT middleware.

    Args:
        request: FastAPI Request объект

    Returns:
        Optional[Dict]: Данные пользователя из JWT токена или None

    Examples:
        python>
        @router.get("/protected")
        async def protected_endpoint(request: Request):
            user = get_request_user(request)
            return {"user": user}
    """
    return getattr(request.state, "user", None)
"""
API endpoints для каталога департаментов и должностей системы генерации профилей А101.

Endpoints:
- GET /api/catalog/departments - Получение списка всех департаментов
- GET /api/catalog/departments/{department_name} - Детальная информация о департаменте
- GET /api/catalog/positions/{department} - Получение должностей для департамента
- GET /api/catalog/search - Поиск департаментов
- GET /api/catalog/search/positions - Поиск должностей
"""

from fastapi import APIRouter, Query, Path, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
import logging

from ..models.schemas import BaseResponse, ErrorResponse
from ..services.catalog_service import catalog_service
from ..api.auth import get_current_user

logger = logging.getLogger(__name__)

# Создаем роутер для catalog endpoints
catalog_router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


@catalog_router.get("/departments", response_model=Dict[str, Any])
async def get_departments(
    force_refresh: bool = Query(False, description="Принудительное обновление кеша"),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a list of all available departments.
    
    Args:
        force_refresh (bool): Force cache refresh (default is False).
    
    Returns:
        Dict[str, Any]: A dictionary containing the list of departments and metadata.
    """
    try:
        logger.info(
            f"Getting departments list (force_refresh={force_refresh}) for user {current_user['username']}"
        )

        departments = catalog_service.get_departments(force_refresh=force_refresh)

        response = {
            "success": True,
            "message": f"Найдено {len(departments)} департаментов",
            "data": {
                "departments": departments,
                "total_count": len(departments),
                "cached": not force_refresh,
                "last_updated": departments[0]["last_updated"] if departments else None,
            },
        }

        logger.info(f"Successfully returned {len(departments)} departments")
        return response

    except Exception as e:
        logger.error(f"Error getting departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения списка департаментов: {str(e)}",
        )


@catalog_router.get("/departments/{department_name}", response_model=Dict[str, Any])
async def get_department_details(
    department_name: str = Path(..., description="Название департамента"),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve detailed information about a specific department."""
    try:
        logger.info(
            f"Getting details for department '{department_name}' for user {current_user['username']}"
        )

        department_details = catalog_service.get_department_details(department_name)

        if not department_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Департамент '{department_name}' не найден",
            )

        response = {
            "success": True,
            "message": f"Информация о департаменте '{department_name}' получена",
            "data": department_details,
        }

        logger.info(f"Successfully returned details for department '{department_name}'")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting department details for '{department_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения информации о департаменте: {str(e)}",
        )


@catalog_router.get("/positions/{department}", response_model=Dict[str, Any])
async def get_positions(
    department: str = Path(..., description="Название департамента"),
    force_refresh: bool = Query(False, description="Принудительное обновление кеша"),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a list of positions for a specific department.
    
    This function fetches detailed information about positions within a given
    department, including the position title, level (1-5, where 1 is the highest),
    category (management, technical, specialist, etc.), and department name.  It
    also groups the positions by their levels and categories for analytical
    purposes. The function can optionally refresh the cache to ensure the latest
    data is retrieved.
    
    Args:
        department: Название департамента.
        force_refresh: Принудительное обновление кеша.
    """
    try:
        logger.info(
            f"Getting positions for department '{department}' (force_refresh={force_refresh}) for user {current_user['username']}"
        )

        positions = catalog_service.get_positions(
            department, force_refresh=force_refresh
        )

        if not positions:
            logger.warning(f"No positions found for department '{department}'")

        # Группировка по уровням для аналитики
        levels_stats = {}
        categories_stats = {}

        for position in positions:
            level = position["level"]
            category = position["category"]

            levels_stats[level] = levels_stats.get(level, 0) + 1
            categories_stats[category] = categories_stats.get(category, 0) + 1

        response = {
            "success": True,
            "message": f"Найдено {len(positions)} должностей для департамента '{department}'",
            "data": {
                "department": department,
                "positions": positions,
                "total_count": len(positions),
                "statistics": {"levels": levels_stats, "categories": categories_stats},
                "cached": not force_refresh,
                "last_updated": positions[0]["last_updated"] if positions else None,
            },
        }

        logger.info(
            f"Successfully returned {len(positions)} positions for department '{department}'"
        )
        return response

    except Exception as e:
        logger.error(f"Error getting positions for department '{department}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения должностей для департамента: {str(e)}",
        )


@catalog_router.get("/search", response_model=Dict[str, Any])
async def search_departments(
    q: str = Query(..., min_length=1, description="Поисковой запрос"),
    current_user: dict = Depends(get_current_user),
):
    """Search for departments by name or path in the organizational structure.
    
    Args:
        q (str): Search query (minimum 1 character).
    
    Returns:
        Dict[str, Any]: Search results.
    """
    try:
        logger.info(
            f"Searching departments with query '{q}' for user {current_user['username']}"
        )

        search_results = catalog_service.search_departments(q)

        response = {
            "success": True,
            "message": f"По запросу '{q}' найдено {len(search_results)} департаментов",
            "data": {
                "query": q,
                "departments": search_results,
                "total_count": len(search_results),
            },
        }

        logger.info(f"Search '{q}' returned {len(search_results)} results")
        return response

    except Exception as e:
        logger.error(f"Error searching departments with query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка поиска департаментов: {str(e)}",
        )


@catalog_router.get("/search/positions", response_model=Dict[str, Any])
async def search_positions(
    q: str = Query(
        ..., min_length=1, description="Поисковой запрос для поиска должностей"
    ),
    department: Optional[str] = Query(
        None, description="Фильтр по департаменту (опционально)"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Search for job positions by title, department, level, or category."""
    try:
        logger.info(
            f"Searching positions with query '{q}' (department filter: {department}) for user {current_user['username']}"
        )

        search_results = catalog_service.search_positions(
            q, department_filter=department
        )

        # Группировка результатов по департаментам для удобства
        departments_breakdown = {}
        levels_breakdown = {}
        categories_breakdown = {}

        for position in search_results:
            dept_name = position["department"]
            level = position["level"]
            category = position["category"]

            departments_breakdown[dept_name] = (
                departments_breakdown.get(dept_name, 0) + 1
            )
            levels_breakdown[level] = levels_breakdown.get(level, 0) + 1
            categories_breakdown[category] = categories_breakdown.get(category, 0) + 1

        response = {
            "success": True,
            "message": f"По запросу '{q}' найдено {len(search_results)} должностей",
            "data": {
                "query": q,
                "department_filter": department,
                "positions": search_results,
                "total_count": len(search_results),
                "breakdown": {
                    "departments": departments_breakdown,
                    "levels": levels_breakdown,
                    "categories": categories_breakdown,
                },
            },
        }

        logger.info(f"Position search '{q}' returned {len(search_results)} results")
        return response

    except Exception as e:
        logger.error(f"Error searching positions with query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка поиска должностей: {str(e)}",
        )


@catalog_router.post("/cache/clear", response_model=BaseResponse)
async def clear_cache(
    cache_type: Optional[str] = Query(
        None, description="Тип кеша (departments, positions или пустой для всех)"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Clears the cache for departments, positions, or all caches.
    
    Args:
        cache_type: Type of cache to clear (departments, positions, or None for all).
    """
    try:
        # Проверяем права администратора
        if current_user["username"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для очистки кеша. Требуются права администратора.",
            )

        logger.info(
            f"Clearing cache (type: {cache_type or 'all'}) by admin user {current_user['username']}"
        )

        catalog_service.clear_cache(cache_type)

        response = BaseResponse(
            success=True,
            message=f"Кеш {'(' + cache_type + ')' if cache_type else ''} успешно очищен",
        )

        logger.info(f"Cache cleared successfully by {current_user['username']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка очистки кеша: {str(e)}",
        )


@catalog_router.get("/stats", response_model=Dict[str, Any])
async def get_catalog_stats(current_user: dict = Depends(get_current_user)):
    """Retrieve statistics for the catalog.
    
    This function gathers and returns overall statistics related to the catalog,
    including the total number of departments, the total number of positions,  and
    the distribution of positions by levels and categories. It also checks  the
    cache status for departments and positions, providing insights into  the
    current state of the catalog data.
    
    Args:
        current_user (dict): The current user information, obtained via
    """
    try:
        logger.info(f"Getting catalog stats for user {current_user['username']}")

        departments = catalog_service.get_departments()

        total_positions = 0
        all_levels = {}
        all_categories = {}

        # Собираем статистику по всем департаментам
        for dept in departments:
            positions = catalog_service.get_positions(dept["name"])
            total_positions += len(positions)

            for pos in positions:
                level = pos["level"]
                category = pos["category"]

                all_levels[level] = all_levels.get(level, 0) + 1
                all_categories[category] = all_categories.get(category, 0) + 1

        response = {
            "success": True,
            "message": "Статистика каталога получена",
            "data": {
                "departments": {
                    "total_count": len(departments),
                    "with_positions": len(
                        [d for d in departments if d["positions_count"] > 0]
                    ),
                },
                "positions": {
                    "total_count": total_positions,
                    "average_per_department": (
                        round(total_positions / len(departments), 2)
                        if departments
                        else 0
                    ),
                    "levels_distribution": all_levels,
                    "categories_distribution": all_categories,
                },
                "cache_status": {
                    "departments_cached": catalog_service._departments_cache
                    is not None,
                    "positions_cached_count": len(catalog_service._positions_cache),
                    "last_departments_update": (
                        catalog_service._last_departments_update.isoformat()
                        if catalog_service._last_departments_update
                        else None
                    ),
                },
            },
        }

        logger.info(
            f"Successfully returned catalog stats: {len(departments)} departments, {total_positions} positions"
        )
        return response

    except Exception as e:
        logger.error(f"Error getting catalog stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики каталога: {str(e)}",
        )


if __name__ == "__main__":
    print("✅ Catalog API endpoints created successfully!")
    print("📍 Available endpoints:")
    print("  - GET /api/catalog/departments")
    print("  - GET /api/catalog/departments/{department_name}")
    print("  - GET /api/catalog/positions/{department}")
    print("  - GET /api/catalog/search")
    print("  - POST /api/catalog/cache/clear")
    print("  - GET /api/catalog/stats")

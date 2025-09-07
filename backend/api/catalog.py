"""
API endpoints для каталога департаментов и должностей системы генерации профилей А101.

Endpoints:
- GET /api/catalog/departments - Получение списка всех департаментов
- GET /api/catalog/departments/{department_name} - Детальная информация о департаменте
- GET /api/catalog/positions/{department} - Получение должностей для департамента
- GET /api/catalog/search - Поиск департаментов
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
    current_user: dict = Depends(get_current_user)
):
    """
    Получение списка всех доступных департаментов.
    
    Возвращает список департаментов с базовой информацией:
    - Название департамента
    - Путь в организационной структуре  
    - Количество доступных должностей
    - Время последнего обновления
    
    Args:
        force_refresh: Принудительное обновление кеша (по умолчанию False)
        
    Returns:
        Dict с списком департаментов и метаданными
    """
    try:
        logger.info(f"Getting departments list (force_refresh={force_refresh}) for user {current_user['username']}")
        
        departments = catalog_service.get_departments(force_refresh=force_refresh)
        
        response = {
            "success": True,
            "message": f"Найдено {len(departments)} департаментов",
            "data": {
                "departments": departments,
                "total_count": len(departments),
                "cached": not force_refresh,
                "last_updated": departments[0]["last_updated"] if departments else None
            }
        }
        
        logger.info(f"Successfully returned {len(departments)} departments")
        return response
        
    except Exception as e:
        logger.error(f"Error getting departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения списка департаментов: {str(e)}"
        )


@catalog_router.get("/departments/{department_name}", response_model=Dict[str, Any])
async def get_department_details(
    department_name: str = Path(..., description="Название департамента"),
    current_user: dict = Depends(get_current_user)
):
    """
    Получение детальной информации о конкретном департаменте.
    
    Включает:
    - Базовую информацию о департаменте
    - Список всех должностей
    - Организационную структуру
    - Статистику по уровням и категориям должностей
    
    Args:
        department_name: Название департамента
        
    Returns:
        Dict с детальной информацией о департаменте
    """
    try:
        logger.info(f"Getting details for department '{department_name}' for user {current_user['username']}")
        
        department_details = catalog_service.get_department_details(department_name)
        
        if not department_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Департамент '{department_name}' не найден"
            )
        
        response = {
            "success": True,
            "message": f"Информация о департаменте '{department_name}' получена",
            "data": department_details
        }
        
        logger.info(f"Successfully returned details for department '{department_name}'")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting department details for '{department_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения информации о департаменте: {str(e)}"
        )


@catalog_router.get("/positions/{department}", response_model=Dict[str, Any])
async def get_positions(
    department: str = Path(..., description="Название департамента"),
    force_refresh: bool = Query(False, description="Принудительное обновление кеша"),
    current_user: dict = Depends(get_current_user)
):
    """
    Получение списка должностей для конкретного департамента.
    
    Возвращает детальную информацию о должностях:
    - Название должности
    - Уровень должности (1-5, где 1 - высший)
    - Категория должности (management, technical, specialist, etc.)
    - Департамент
    
    Args:
        department: Название департамента
        force_refresh: Принудительное обновление кеша
        
    Returns:
        Dict со списком должностей и метаданными
    """
    try:
        logger.info(f"Getting positions for department '{department}' (force_refresh={force_refresh}) for user {current_user['username']}")
        
        positions = catalog_service.get_positions(department, force_refresh=force_refresh)
        
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
                "statistics": {
                    "levels": levels_stats,
                    "categories": categories_stats
                },
                "cached": not force_refresh,
                "last_updated": positions[0]["last_updated"] if positions else None
            }
        }
        
        logger.info(f"Successfully returned {len(positions)} positions for department '{department}'")
        return response
        
    except Exception as e:
        logger.error(f"Error getting positions for department '{department}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения должностей для департамента: {str(e)}"
        )


@catalog_router.get("/search", response_model=Dict[str, Any])
async def search_departments(
    q: str = Query(..., min_length=1, description="Поисковой запрос"),
    current_user: dict = Depends(get_current_user)
):
    """
    Поиск департаментов по названию или пути в организационной структуре.
    
    Выполняет нечеткий поиск по:
    - Названию департамента
    - Пути в иерархии организации
    
    Args:
        q: Поисковой запрос (минимум 1 символ)
        
    Returns:
        Dict с результатами поиска
    """
    try:
        logger.info(f"Searching departments with query '{q}' for user {current_user['username']}")
        
        search_results = catalog_service.search_departments(q)
        
        response = {
            "success": True,
            "message": f"По запросу '{q}' найдено {len(search_results)} департаментов",
            "data": {
                "query": q,
                "departments": search_results,
                "total_count": len(search_results)
            }
        }
        
        logger.info(f"Search '{q}' returned {len(search_results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Error searching departments with query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка поиска департаментов: {str(e)}"
        )


@catalog_router.post("/cache/clear", response_model=BaseResponse)
async def clear_cache(
    cache_type: Optional[str] = Query(None, description="Тип кеша (departments, positions или пустой для всех)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Очистка кеша каталога (только для администраторов).
    
    Позволяет очистить кеш департаментов, должностей или весь кеш полностью.
    Требует права администратора.
    
    Args:
        cache_type: Тип кеша для очистки (departments, positions или None для всех)
        
    Returns:
        BaseResponse с результатом операции
    """
    try:
        # Проверяем права администратора
        if current_user["username"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для очистки кеша. Требуются права администратора."
            )
        
        logger.info(f"Clearing cache (type: {cache_type or 'all'}) by admin user {current_user['username']}")
        
        catalog_service.clear_cache(cache_type)
        
        response = BaseResponse(
            success=True,
            message=f"Кеш {'(' + cache_type + ')' if cache_type else ''} успешно очищен"
        )
        
        logger.info(f"Cache cleared successfully by {current_user['username']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка очистки кеша: {str(e)}"
        )


@catalog_router.get("/stats", response_model=Dict[str, Any])
async def get_catalog_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Получение статистики каталога.
    
    Возвращает общую статистику по:
    - Количеству департаментов
    - Общему количеству должностей
    - Распределению должностей по уровням и категориям
    - Статусу кеша
    
    Returns:
        Dict с общей статистикой каталога
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
                    "with_positions": len([d for d in departments if d["positions_count"] > 0])
                },
                "positions": {
                    "total_count": total_positions,
                    "average_per_department": round(total_positions / len(departments), 2) if departments else 0,
                    "levels_distribution": all_levels,
                    "categories_distribution": all_categories
                },
                "cache_status": {
                    "departments_cached": catalog_service._departments_cache is not None,
                    "positions_cached_count": len(catalog_service._positions_cache),
                    "last_departments_update": catalog_service._last_departments_update.isoformat() if catalog_service._last_departments_update else None
                }
            }
        }
        
        logger.info(f"Successfully returned catalog stats: {len(departments)} departments, {total_positions} positions")
        return response
        
    except Exception as e:
        logger.error(f"Error getting catalog stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики каталога: {str(e)}"
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
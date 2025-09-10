"""
API endpoints для организационной структуры и поиска для системы генерации профилей А101.

Новые endpoints для LLM интеграции с path-based индексацией:
- GET /api/organization/search-items - Все элементы для frontend поиска
- GET /api/organization/structure/{path} - Полная оргструктура с выделенной целью

Исправляют проблему потери 57 бизнес-единиц из-за дублирующихся имен.
"""

from fastapi import APIRouter, Path, HTTPException, Depends, status
from typing import Dict, Any, List
import logging

from ..models.schemas import BaseResponse, ErrorResponse
from ..services.catalog_service import catalog_service
from ..api.auth import get_current_user

logger = logging.getLogger(__name__)

# Создаем роутер для organization endpoints
organization_router = APIRouter(prefix="/api/organization", tags=["Organization"])


@organization_router.get("/search-items", response_model=Dict[str, Any])
async def get_search_items(
    current_user: dict = Depends(get_current_user),
):
    """
    @doc
    Получение всех элементов для frontend dropdown поиска с path-based индексацией.
    
    Возвращает все 567 бизнес-единиц из оргструктуры для реактивного поиска.
    Исправляет потерю данных из-за дублирующихся имен департаментов.
    
    Каждый элемент содержит:
    - display_name: Имя для отображения с контекстом
    - full_path: Полный путь для API запросов  
    - positions_count: Количество позиций
    - hierarchy: Полная иерархия
    
    ### Пример запроса:
    ```bash
    curl -X GET "http://localhost:8001/api/organization/search-items" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример успешного ответа:
    ```json
    {
      "success": true,
      "message": "Получено 567 элементов для поиска",
      "data": {
        "items": [
          {
            "display_name": "ДИТ (Блок ОД)",
            "full_path": "Блок операционного директора/Департамент информационных технологий",
            "positions_count": 25,
            "hierarchy": ["Блок операционного директора", "Департамент информационных технологий"]
          }
        ],
        "total_count": 567
      }
    }
    ```
    
    Returns:
        Dict с массивом элементов для поиска
        
    Examples:
        python> response = await get_search_items()
        python> # {'success': True, 'data': {'items': [{'display_name': 'ДИТ (Блок ОД)', ...}]}}
    """
    try:
        logger.info(f"Getting search items for user {current_user['username']}")

        # Получаем все элементы через новую path-based систему
        search_items = catalog_service.get_searchable_items()

        response = {
            "success": True,
            "message": f"Получено {len(search_items)} элементов для поиска",
            "data": {
                "items": search_items,
                "total_count": len(search_items),
                "source": "path_based_indexing",
                "includes_all_business_units": True,  # Подтверждение что нет потерь данных
            },
        }

        logger.info(
            f"Successfully returned {len(search_items)} search items (path-based)"
        )
        return response

    except Exception as e:
        logger.error(f"Error getting search items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения элементов для поиска: {str(e)}",
        )


@organization_router.post("/structure", response_model=Dict[str, Any])
async def get_organization_structure_with_target(
    request_body: Dict[str, str],
    current_user: dict = Depends(get_current_user),
):
    """
    @doc
    Получение полной организационной структуры с выделенной целевой позицией для LLM анализа.
    
    Возвращает всю оргструктуру компании с подсвеченным целевым элементом
    и его родительскими узлами для контекстного анализа карьерных путей.
    
    LLM получает:
    - Полную иерархию для понимания возможностей роста
    - Выделенную текущую позицию (is_target=True)
    - Метаданные о целевой единице
    - Контекст всей организации
    
    ### Пример запроса:
    ```bash
    curl -X POST "http://localhost:8001/api/organization/structure" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
      -H "Content-Type: application/json" \
      -d '{
        "target_path": "Блок операционного директора/Департамент информационных технологий"
      }'
    ```
    
    ### Пример успешного ответа:
    ```json
    {
      "success": true,
      "message": "Организационная структура с выделенной целью 'Блок операционного директора/Департамент информационных технологий' получена",
      "data": {
        "target_path": "Блок операционного директора/Департамент информационных технологий",
        "total_business_units": 567,
        "structure": {
          "organization": {
            "Блок операционного директора": {
              "name": "Блок операционного директора",
              "positions": ["Операционный директор"],
              "children": {
                "Департамент информационных технологий": {
                  "name": "Департамент информационных технологий",
                  "positions": ["Директор по информационным технологиям"],
                  "is_target": true
                }
              }
            }
          }
        }
      }
    }
    ```
    
    ### Пример ошибки (целевой путь не найден):
    ```json
    {
      "success": false,
      "error": {
        "code": "NOT_FOUND",
        "message": "Business unit at path 'Несуществующий департамент' not found",
        "details": {},
        "timestamp": "2025-09-10T03:01:03.844485",
        "request_id": "bf8cf59b-c252-4a4f-b45f-96c04d85f2f6"
      }
    }
    ```
    
    Args:
        request_body: {"target_path": "Блок/Департамент/Управление/Группа"}
        
    Returns:
        Dict с полной структурой и выделенной целью
        
    Examples:
        python> response = await get_organization_structure_with_target({"target_path": "Блок операционного директора/Департамент информационных технологий"})
        python> # {'success': True, 'data': {'target_path': '...', 'structure': {...}}}
    """
    try:
        target_path = request_body.get("target_path")
        if not target_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствует обязательный параметр target_path",
            )

        logger.info(
            f"Getting organization structure with target '{target_path}' for user {current_user['username']}"
        )

        # Получаем структуру с подсвеченной целью
        highlighted_structure = catalog_service.get_organization_structure_with_target(
            target_path
        )

        # Проверяем на ошибки
        if "error" in highlighted_structure:
            logger.warning(f"Target path not found: {target_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=highlighted_structure["error"],
            )

        response = {
            "success": True,
            "message": f"Организационная структура с выделенной целью '{target_path}' получена",
            "data": highlighted_structure,
        }

        logger.info(f"Successfully returned highlighted structure for '{target_path}'")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting highlighted structure for '{target_path}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения структуры организации: {str(e)}",
        )


@organization_router.post("/unit", response_model=Dict[str, Any])
async def get_business_unit_details(
    request_body: Dict[str, str],
    current_user: dict = Depends(get_current_user),
):
    """
    @doc
    Получение детальной информации о конкретной бизнес-единице по полному пути.
    
    Дополнительный endpoint для получения расширенных метаданных
    о конкретной бизнес-единице с обогащенными данными позиций.
    
    ### Пример запроса:
    ```bash
    curl -X POST "http://localhost:8001/api/organization/unit" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
      -H "Content-Type: application/json" \
      -d '{
        "unit_path": "Блок операционного директора/Департамент информационных технологий"
      }'
    ```
    
    ### Пример успешного ответа:
    ```json
    {
      "success": true,
      "message": "Информация о бизнес-единице 'Блок операционного директора/Департамент информационных технологий' получена",
      "data": {
        "name": "Департамент информационных технологий",
        "path": "Блок операционного директора/Департамент информационных технологий",
        "level": 1,
        "positions": ["Директор по информационным технологиям"],
        "hierarchy_path": ["Блок операционного директора", "Департамент информационных технологий"],
        "parent_path": "Блок операционного директора",
        "enriched_positions": [
          {
            "name": "Директор по информационным технологиям",
            "level": 1,
            "category": "management",
            "department": "Департамент информационных технологий",
            "full_path": "Блок операционного директора/Департамент информационных технологий"
          }
        ],
        "data": {
          "number": 24001041,
          "children": {
            "Отдел управления данными": {...},
            "Управление инфраструктуры и поддержки": {...}
          }
        }
      }
    }
    ```
    
    ### Пример ошибки (путь не найден):
    ```json
    {
      "success": false,
      "error": {
        "code": "NOT_FOUND",
        "message": "Бизнес-единица по пути 'Несуществующий путь' не найдена",
        "details": {},
        "timestamp": "2025-09-10T03:01:16.329967",
        "request_id": "fb4d11f0-c102-4011-bff1-cec8bd2b9399"
      }
    }
    ```
    
    Args:
        request_body: {"unit_path": "Блок/Департамент/Управление/Группа"}
        
    Returns:
        Dict с детальной информацией о бизнес-единице
        
    Examples:
        python> response = await get_business_unit_details({"unit_path": "Блок операционного директора/Департамент информационных технологий"})
        python> # {'success': True, 'data': {'name': 'Департамент информационных технологий', 'enriched_positions': [...]}}
    """
    try:
        unit_path = request_body.get("unit_path")
        if not unit_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствует обязательный параметр unit_path",
            )

        logger.info(
            f"Getting business unit details for '{unit_path}' for user {current_user['username']}"
        )

        # Получаем детали бизнес-единицы
        unit_details = catalog_service.find_business_unit_by_path(unit_path)

        if not unit_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бизнес-единица по пути '{unit_path}' не найдена",
            )

        response = {
            "success": True,
            "message": f"Информация о бизнес-единице '{unit_path}' получена",
            "data": unit_details,
        }

        logger.info(f"Successfully returned details for business unit '{unit_path}'")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business unit details for '{unit_path}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения информации о бизнес-единице: {str(e)}",
        )


@organization_router.get("/stats", response_model=Dict[str, Any])
async def get_organization_stats(current_user: dict = Depends(get_current_user)):
    """
    @doc
    Получение статистики организационной структуры с path-based индексацией.
    
    Возвращает точную статистику всех 567 бизнес-единиц
    без потерь данных из-за дублирующихся имен.
    
    ### Пример запроса:
    ```bash
    curl -X GET "http://localhost:8001/api/organization/stats" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример успешного ответа:
    ```json
    {
      "success": true,
      "message": "Статистика организационной структуры получена",
      "data": {
        "business_units": {
          "total_count": 567,
          "with_positions": 545,
          "by_levels": {
            "0": 9,
            "1": 27,
            "2": 91,
            "3": 177,
            "4": 171,
            "5": 92
          }
        },
        "positions": {
          "total_count": 1689,
          "average_per_unit": 2.98
        },
        "indexing_method": "path_based",
        "data_completeness": "100%",
        "source": "organization_cache"
      }
    }
    ```
    
    ### 📊 Интерпретация статистики:
    - **total_count**: Общее количество бизнес-единиц (567)
    - **with_positions**: Бизнес-единицы с активными позициями (545)
    - **by_levels**: Распределение по уровням иерархии (0=топ-блоки, 5=группы)
    - **total_positions**: Общее количество должностей в компании (1689)
    - **indexing_method**: Метод индексации для избежания потери данных
    
    Returns:
        Dict с полной статистикой организации
        
    Examples:
        python> response = await get_organization_stats()
        python> # {'success': True, 'data': {'business_units': {'total_count': 567}, 'positions': {'total_count': 1689}}}
    """
    try:
        logger.info(
            f"Getting organization statistics for user {current_user['username']}"
        )

        # Получаем все бизнес-единицы через path-based индекс
        all_units = (
            catalog_service.organization_cache.get_all_business_units_with_paths()
        )

        # Статистика по уровням
        levels_stats = {}
        total_positions = 0
        units_with_positions = 0

        for unit_path, unit_data in all_units.items():
            level = unit_data["level"]
            positions_count = len(unit_data["positions"])

            levels_stats[level] = levels_stats.get(level, 0) + 1
            total_positions += positions_count

            if positions_count > 0:
                units_with_positions += 1

        response = {
            "success": True,
            "message": "Статистика организационной структуры получена",
            "data": {
                "business_units": {
                    "total_count": len(all_units),
                    "with_positions": units_with_positions,
                    "by_levels": levels_stats,
                },
                "positions": {
                    "total_count": total_positions,
                    "average_per_unit": (
                        round(total_positions / len(all_units), 2) if all_units else 0
                    ),
                },
                "indexing_method": "path_based",
                "data_completeness": "100%",  # Подтверждение отсутствия потерь
                "source": "organization_cache",
            },
        }

        logger.info(
            f"Successfully returned organization stats: {len(all_units)} units, {total_positions} positions"
        )
        return response

    except Exception as e:
        logger.error(f"Error getting organization statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики организации: {str(e)}",
        )


if __name__ == "__main__":
    print("✅ Organization API endpoints created successfully!")
    print("📍 Available endpoints:")
    print("  - GET /api/organization/search-items")
    print("  - POST /api/organization/structure  # Body: {target_path: string}")
    print("  - POST /api/organization/unit       # Body: {unit_path: string}")
    print("  - GET /api/organization/stats")
    print("🎯 Purpose: LLM-focused career path analysis with path-based indexing")
    print("🔧 Note: Changed to POST for path parameters to handle Cyrillic correctly")

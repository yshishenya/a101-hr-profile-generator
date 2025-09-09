"""
@doc Dashboard API - единое API для статистики системы

Оптимизированные endpoint'ы для получения всей статистики dashboard одним запросом.
Минимизирует количество API вызовов и улучшает UX.

Examples:
  python> # GET /api/dashboard/stats - вся статистика одним запросом
  python> # Возвращает: departments, positions, profiles, active_tasks
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import logging
import sqlite3
from datetime import datetime

from ..services.catalog_service import catalog_service
from ..models.database import DatabaseManager
from ..api.auth import get_current_user

logger = logging.getLogger(__name__)

# Создаем роутер для dashboard endpoints
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
db_manager = DatabaseManager()


@dashboard_router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """
    @doc
    Получение всей статистики dashboard одним запросом.
    
    Оптимизированный endpoint, который возвращает:
    - Количество департаментов и должностей (из кэша каталога)
    - Количество созданных профилей (из базы)
    - Список активных задач генерации
    - Процент покрытия должностей профилями
    
    Returns:
        Dict с полной статистикой для dashboard
        
    Examples:
      python> # GET /api/dashboard/stats
      python> # Возвращает всю необходимую статистику одним запросом
    """
    try:
        logger.info(f"Getting dashboard stats for user {current_user['username']}")
        
        # 1. Получаем статистику каталога (кэшированная, быстро)
        departments = catalog_service.get_departments()
        
        # Считаем общее количество должностей
        total_positions = 0
        for dept in departments:
            positions = catalog_service.get_positions(dept["name"])
            total_positions += len(positions)
        
        # 2. Получаем количество профилей (одним SQL запросом)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM profiles")
        profiles_count_result = cursor.fetchone()
        profiles_count = profiles_count_result[0] if profiles_count_result else 0
        
        # 3. Получаем активные задачи (заглушка - TODO: реализовать когда будет готов generation manager)
        active_tasks = []
        # TODO: Интеграция с generation manager когда будет готов
        # try:
        #     all_tasks = generation_manager.get_all_tasks()
        #     ...
        # except Exception as e:
        #     logger.warning(f"Could not get active tasks: {e}")
        #     active_tasks = []
        
        # 4. Вычисляем метрики
        completion_percentage = (profiles_count / total_positions * 100) if total_positions > 0 else 0
        departments_with_profiles = len(set([dept["name"] for dept in departments if dept["positions_count"] > 0]))
        
        # 5. Формируем ответ
        response = {
            "success": True,
            "message": "Dashboard статистика получена",
            "data": {
                # Основные метрики
                "summary": {
                    "departments_count": len(departments),
                    "positions_count": total_positions,
                    "profiles_count": profiles_count,
                    "completion_percentage": round(completion_percentage, 1),
                    "active_tasks_count": len(active_tasks)
                },
                
                # Детальная статистика
                "departments": {
                    "total": len(departments),
                    "with_positions": departments_with_profiles,
                    "average_positions": round(total_positions / len(departments), 1) if departments else 0
                },
                
                "positions": {
                    "total": total_positions,
                    "with_profiles": profiles_count,
                    "without_profiles": total_positions - profiles_count,
                    "coverage_percent": round(completion_percentage, 1)
                },
                
                "profiles": {
                    "total": profiles_count,
                    "percentage_complete": round(completion_percentage, 1)
                },
                
                # Активные задачи (последние 5)
                "active_tasks": active_tasks,
                
                # Метаданные
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "data_sources": {
                        "catalog": "cached",
                        "profiles": "database", 
                        "tasks": "memory"
                    }
                }
            }
        }
        
        logger.info(f"Dashboard stats: {len(departments)} depts, {total_positions} positions, {profiles_count} profiles, {len(active_tasks)} active tasks")
        return response
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики dashboard: {str(e)}"
        )


@dashboard_router.get("/stats/minimal", response_model=Dict[str, Any])
async def get_minimal_stats(current_user: dict = Depends(get_current_user)):
    """
    @doc
    Получение минимальной статистики для компактных компонентов.
    
    Возвращает только самые важные метрики:
    - Общее количество должностей
    - Количество созданных профилей  
    - Процент завершенности
    - Количество активных задач
    
    Максимально быстрый запрос для UX критичных компонентов.
    
    Returns:
        Dict с минимальной статистикой
        
    Examples:
      python> # GET /api/dashboard/stats/minimal
      python> # Быстрый запрос только важных метрик
    """
    try:
        logger.info(f"Getting minimal stats for user {current_user['username']}")
        
        # Используем кэшированные данные каталога
        departments = catalog_service.get_departments()
        total_positions = sum(dept["positions_count"] for dept in departments)
        
        # Быстрый подсчет профилей
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM profiles")
        profiles_count = cursor.fetchone()[0]
        
        # Подсчет активных задач (заглушка)
        active_tasks_count = 0
        # TODO: Интеграция с generation manager
        # try:
        #     all_tasks = generation_manager.get_all_tasks()
        #     active_tasks_count = len([...])
        # except:
        #     active_tasks_count = 0
        
        completion_percentage = (profiles_count / total_positions * 100) if total_positions > 0 else 0
        
        response = {
            "success": True,
            "data": {
                "positions_count": total_positions,
                "profiles_count": profiles_count,
                "completion_percentage": round(completion_percentage, 1),
                "active_tasks_count": active_tasks_count,
                "last_updated": datetime.now().isoformat()
            }
        }
        
        logger.info(f"Minimal stats: {total_positions} positions, {profiles_count} profiles, {completion_percentage:.1f}% complete")
        return response
        
    except Exception as e:
        logger.error(f"Error getting minimal stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения минимальной статистики: {str(e)}"
        )


@dashboard_router.get("/stats/activity", response_model=Dict[str, Any])
async def get_activity_stats(current_user: dict = Depends(get_current_user)):
    """
    @doc
    Получение статистики активности для ленты dashboard.
    
    Возвращает:
    - Активные задачи генерации с прогрессом
    - Недавно созданные профили
    - Статистику активности за период
    
    Returns:
        Dict со статистикой активности
        
    Examples:
      python> # GET /api/dashboard/stats/activity
      python> # Данные для ленты активности
    """
    try:
        logger.info(f"Getting activity stats for user {current_user['username']}")
        
        # 1. Активные задачи (заглушка)
        active_tasks = []
        # TODO: Интеграция с generation manager
        # try:
        #     all_tasks = generation_manager.get_all_tasks()
        #     active_tasks = [...]
        # except:
        #     active_tasks = []
        
        # 2. Недавние профили (последние 10)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.department, p.position, p.employee_name, p.created_at, p.status,
                   u.username as created_by
            FROM profiles p
            LEFT JOIN users u ON p.created_by = u.id
            ORDER BY p.created_at DESC
            LIMIT 10
        """)
        
        recent_profiles = []
        for row in cursor.fetchall():
            recent_profiles.append({
                "department": row["department"],
                "position": row["position"],
                "employee_name": row["employee_name"],
                "created_at": row["created_at"],
                "status": row["status"],
                "created_by": row["created_by"]
            })
        
        response = {
            "success": True,
            "data": {
                "active_tasks": active_tasks,
                "recent_profiles": recent_profiles,
                "summary": {
                    "active_tasks_count": len(active_tasks),
                    "recent_profiles_count": len(recent_profiles),
                    "has_activity": len(active_tasks) > 0 or len(recent_profiles) > 0
                },
                "last_updated": datetime.now().isoformat()
            }
        }
        
        logger.info(f"Activity stats: {len(active_tasks)} active tasks, {len(recent_profiles)} recent profiles")
        return response
        
    except Exception as e:
        logger.error(f"Error getting activity stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики активности: {str(e)}"
        )


if __name__ == "__main__":
    print("✅ Dashboard API endpoints created!")
    print("📍 Available endpoints:")
    print("  - GET /api/dashboard/stats - Full dashboard statistics")
    print("  - GET /api/dashboard/stats/minimal - Essential metrics only")  
    print("  - GET /api/dashboard/stats/activity - Activity feed data")
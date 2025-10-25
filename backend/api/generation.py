"""
API endpoints для асинхронной генерации профилей должностей.

Реализует современный паттерн async task processing:
1. POST /api/generation/start - запуск генерации (возвращает task_id)
2. GET /api/generation/{task_id}/status - получение статуса задачи
3. GET /api/generation/{task_id}/result - получение результата
4. DELETE /api/generation/{task_id} - отмена задачи
"""

import asyncio
import uuid
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from ..core.config import config
from ..core.profile_generator import ProfileGenerator
from .auth import get_current_user
from ..models.database import get_db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generation", tags=["generation"])


# Pydantic модели
class GenerationRequest(BaseModel):
    department: str = Field(..., description="Название департамента")
    position: str = Field(..., description="Название должности")
    employee_name: Optional[str] = Field(
        None, description="ФИО сотрудника (опционально)"
    )
    temperature: float = Field(
        0.1, ge=0.0, le=1.0, description="Температура генерации LLM"
    )
    save_result: bool = Field(True, description="Сохранять ли результат в файл")


class GenerationTask(BaseModel):
    task_id: str
    status: str  # "queued", "processing", "completed", "failed", "cancelled"
    progress: Optional[int] = Field(None, description="Прогресс в процентах (0-100)")
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(
        None, description="Оценочное время в секундах"
    )
    current_step: Optional[str] = Field(None, description="Текущий этап обработки")
    error_message: Optional[str] = None


class GenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_duration: Optional[int] = None


class TaskStatusResponse(BaseModel):
    task: GenerationTask
    result: Optional[Dict[str, Any]] = None


# In-memory storage для задач (в продакшене использовать Redis)
_active_tasks: Dict[str, Dict[str, Any]] = {}
_task_results: Dict[str, Dict[str, Any]] = {}


async def get_profile_generator() -> ProfileGenerator:
    """Dependency для получения ProfileGenerator с актуальными настройками"""
    if not config.openrouter_configured:
        raise HTTPException(
            status_code=503,
            detail="OpenRouter API не сконфигурирован. Добавьте OPENROUTER_API_KEY в .env",
        )

    # ProfileGenerator теперь сам получает настройки из config
    generator = ProfileGenerator()

    return generator


async def background_generate_profile(
    task_id: str, request: GenerationRequest, user_id: int
):
    """Background task для генерации профиля"""

    # Обновляем статус на "processing"
    _active_tasks[task_id].update(
        {
            "status": "processing",
            "started_at": datetime.now(),
            "current_step": "Инициализация генератора профилей",
            "progress": 5,
        }
    )

    try:
        # Получаем генератор
        generator = await get_profile_generator()

        # Обновляем прогресс
        _active_tasks[task_id].update(
            {"current_step": "Подготовка данных компании", "progress": 15}
        )

        # Валидация системы
        validation_result = await generator.validate_system()
        if not validation_result["system_ready"]:
            raise Exception(f"Система не готова: {validation_result['errors']}")

        _active_tasks[task_id].update(
            {"current_step": "Генерация профиля через LLM", "progress": 30}
        )

        # Создаем profile_id заранее
        profile_id = str(uuid.uuid4())

        # Генерация профиля с передачей profile_id
        result = await generator.generate_profile(
            department=request.department,
            position=request.position,
            employee_name=request.employee_name,
            temperature=request.temperature,
            save_result=request.save_result,
            profile_id=profile_id,  # Передаем UUID в генератор
        )

        _active_tasks[task_id].update(
            {"current_step": "Сохранение результата", "progress": 90}
        )

        # Сохраняем в БД с уже известным profile_id
        if result["success"]:
            await save_generation_to_db(result, user_id, task_id, profile_id)

        # Завершаем задачу
        _active_tasks[task_id].update(
            {
                "status": "completed" if result["success"] else "failed",
                "completed_at": datetime.now(),
                "current_step": "Завершено",
                "progress": 100,
                "error_message": (
                    "; ".join(result.get("errors", []))
                    if not result["success"]
                    else None
                ),
            }
        )

        # Сохраняем результат
        _task_results[task_id] = result

        logger.info(f"✅ Generation task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"❌ Generation task {task_id} failed: {e}")

        _active_tasks[task_id].update(
            {
                "status": "failed",
                "completed_at": datetime.now(),
                "current_step": "Ошибка генерации",
                "progress": 0,
                "error_message": str(e),
            }
        )


async def save_generation_to_db(
    result: Dict[str, Any], user_id: int, task_id: str, profile_id: str
):
    """Сохранение результата генерации в базу данных"""
    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Сохраняем профиль с правильной схемой
        cursor.execute(
            """
            INSERT INTO profiles (
                id, department, position, employee_name,
                profile_data, metadata_json,
                generation_time_seconds, input_tokens, output_tokens, total_tokens,
                validation_score, completeness_score,
                created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                profile_id,
                result["metadata"]["generation"]["department"],
                result["metadata"]["generation"]["position"],
                result["metadata"]["generation"].get("employee_name"),
                json.dumps(result["profile"], ensure_ascii=False),
                json.dumps(result["metadata"], ensure_ascii=False),
                result["metadata"]["generation"]["duration"],
                result["metadata"]["llm"].get("input_tokens", 0),
                result["metadata"]["llm"].get("output_tokens", 0),
                result["metadata"]["llm"].get("tokens_used", 0),
                result["metadata"]["validation"].get("validation_score", 0.0),
                result["metadata"]["validation"].get("completeness_score", 0.0),
                user_id,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

        logger.info(f"💾 Saved generation result to database: profile_id={profile_id}")

    except Exception as e:
        logger.error(f"❌ Failed to save generation to DB: {e}")


@router.post("/start", response_model=GenerationResponse)
async def start_generation(
    request: GenerationRequest,
    current_user=Depends(get_current_user),
):
    """
    Запуск асинхронной генерации профиля должности

    ### Пример запроса:
    ```bash
    curl -X POST "http://localhost:8001/api/generation/start" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
      -H "Content-Type: application/json" \
      -d '{
        "department": "Группа анализа данных",
        "position": "Аналитик данных",
        "employee_name": "Тест Тестов",
        "temperature": 0.1,
        "save_result": true
      }'
    ```

    ### Пример успешного ответа:
    ```json
    {
      "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
      "status": "queued",
      "message": "Генерация профиля 'Аналитик данных' в 'Группа анализа данных' запущена",
      "estimated_duration": 45
    }
    ```

    Returns:
        task_id и примерное время выполнения
    """
    # Создаем уникальный ID задачи
    task_id = str(uuid.uuid4())

    # Оценочное время генерации (30-60 секунд)
    estimated_duration = 45

    # Регистрируем задачу
    _active_tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None,
        "estimated_duration": estimated_duration,
        "current_step": "В очереди на обработку",
        "request": request.dict(),
        "user_id": current_user["user_id"],
    }

    # Запускаем background task используя asyncio.create_task для true async execution
    # BackgroundTasks блокирует ответ до завершения задачи - используем asyncio напрямую
    asyncio.create_task(
        background_generate_profile(task_id, request, current_user["user_id"])
    )

    logger.info(
        f"🚀 Started generation task {task_id} for user {current_user['username']}"
    )

    return GenerationResponse(
        task_id=task_id,
        status="queued",
        message=f"Генерация профиля '{request.position}' в '{request.department}' запущена",
        estimated_duration=estimated_duration,
    )


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, current_user=Depends(get_current_user)):
    """
    Получение статуса задачи генерации
    
    ### Пример запроса:
    ```bash
    curl -X GET "http://localhost:8001/api/generation/7feeb5ed-9e9d-419b-8a1d-e892accdd2c1/status" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример ответа (задача выполняется):
    ```json
    {
      "task": {
        "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
        "status": "processing",
        "progress": 30,
        "created_at": "2025-09-10T02:52:46.830887",
        "started_at": "2025-09-10T02:52:46.831493",
        "estimated_duration": 45,
        "current_step": "Генерация профиля через LLM"
      },
      "result": null
    }
    ```
    
    ### Пример ответа (ошибка):
    ```json
    {
      "task": {
        "status": "failed",
        "progress": 100,
        "current_step": "Завершено",
        "error_message": "Generation failed: [Errno 2] No such file or directory: '/app/generated_profiles'"
      },
      "result": null
    }
    ```

    Args:
        task_id: ID задачи генерации

    Returns:
        Текущий статус задачи и результат (если доступен)
    """
    if task_id not in _active_tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task_data = _active_tasks[task_id]

    # Проверяем права доступа
    if task_data["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")

    # Формируем ответ
    task = GenerationTask(**task_data)
    result = _task_results.get(task_id) if task.status == "completed" else None

    return TaskStatusResponse(task=task, result=result)


@router.get("/{task_id}/result")
async def get_task_result(task_id: str, current_user=Depends(get_current_user)):
    """
    Получение результата генерации профиля
    
    ### Пример запроса:
    ```bash
    curl -X GET "http://localhost:8001/api/generation/7feeb5ed-9e9d-419b-8a1d-e892accdd2c1/result" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример успешного ответа:
    ```json
    {
      "success": true,
      "profile": {
        "position_title": "Аналитик данных",
        "department_broad": "Группа анализа данных",
        "professional_skills": [...],
        "responsibility_areas": [...]
      },
      "metadata": {
        "generation": {
          "timestamp": "2025-09-10T02:52:55.650672",
          "duration": 12.48,
          "temperature": 0.1
        },
        "llm": {
          "model": "google/gemini-2.5-flash",
          "tokens": {"input": 35821, "output": 2925, "total": 38746}
        }
      }
    }
    ```
    
    ### Пример ошибки (задача в процессе):
    ```json
    {
      "detail": "Задача еще выполняется. Статус: processing"
    }
    ```

    Args:
        task_id: ID задачи генерации

    Returns:
        Полный результат генерации профиля
    """
    if task_id not in _active_tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task_data = _active_tasks[task_id]

    # Проверяем права доступа
    if task_data["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")

    # Проверяем статус задачи
    if task_data["status"] not in ["completed", "failed"]:
        raise HTTPException(
            status_code=202,
            detail=f"Задача еще выполняется. Статус: {task_data['status']}",
        )

    if task_id not in _task_results:
        raise HTTPException(status_code=404, detail="Результат не найден")

    return _task_results[task_id]


@router.delete("/{task_id}")
async def cancel_task(task_id: str, current_user=Depends(get_current_user)):
    """
    Отмена задачи генерации (если возможно)
    
    ### Пример запроса:
    ```bash
    curl -X DELETE "http://localhost:8001/api/generation/7feeb5ed-9e9d-419b-8a1d-e892accdd2c1" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример успешной отмены:
    ```json
    {
      "success": true,
      "timestamp": "2025-09-10T03:00:00.000000",
      "message": "Задача отменена"
    }
    ```
    
    ### Пример ошибки (нельзя отменить):
    ```json
    {
      "detail": "Нельзя отменить завершенную задачу"
    }
    ```

    Args:
        task_id: ID задачи генерации
    """
    if task_id not in _active_tasks:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task_data = _active_tasks[task_id]

    # Проверяем права доступа
    if task_data["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")

    # Отменяем только если задача еще не завершена
    if task_data["status"] in ["queued", "processing"]:
        _active_tasks[task_id].update(
            {
                "status": "cancelled",
                "completed_at": datetime.now(),
                "current_step": "Отменено пользователем",
                "error_message": "Задача отменена пользователем",
            }
        )

        logger.info(f"🛑 Cancelled generation task {task_id}")

        return {"message": "Задача отменена"}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Нельзя отменить задачу в статусе: {task_data['status']}",
        )


@router.get("/tasks/active")
async def get_active_tasks(
    current_user=Depends(get_current_user),
) -> List[GenerationTask]:
    """
    Получение списка активных задач пользователя
    
    ### Пример запроса:
    ```bash
    curl -X GET "http://localhost:8001/api/generation/tasks/active" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример ответа (нет активных задач):
    ```json
    []
    ```
    
    ### Пример ответа (есть активные задачи):
    ```json
    [
      {
        "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
        "status": "processing",
        "progress": 45,
        "created_at": "2025-09-10T02:52:46.830887",
        "current_step": "Генерация профиля через LLM",
        "estimated_duration": 45
      }
    ]
    ```

    Returns:
        Список активных задач генерации для текущего пользователя
    """
    user_tasks = []

    for task_data in _active_tasks.values():
        if task_data["user_id"] == current_user["user_id"]:
            # Исключаем завершенные задачи старше 1 часа
            if task_data["status"] in ["completed", "failed", "cancelled"]:
                completed_at = task_data.get("completed_at")
                if completed_at and datetime.now() - completed_at > timedelta(hours=1):
                    continue

            user_tasks.append(GenerationTask(**task_data))

    return user_tasks


@router.post("/cleanup")
async def cleanup_old_tasks(current_user=Depends(get_current_user)):
    """
    Очистка старых завершенных задач (только admin)
    
    Удаляет все задачи старше 24 часов со статусом completed/failed/cancelled.
    
    ### Пример запроса:
    ```bash
    curl -X POST "http://localhost:8001/api/generation/cleanup" \
      -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    ### Пример успешной очистки:
    ```json
    {
      "success": true,
      "timestamp": "2025-09-10T03:00:00.000000",
      "message": "Очищено 5 старых задач"
    }
    ```
    
    ### Пример ошибки доступа:
    ```json
    {
      "detail": "Только admin может очищать задачи"
    }
    ```
    """
    if current_user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Только admin может очищать задачи")

    cleanup_count = 0
    cutoff_time = datetime.now() - timedelta(hours=24)

    # Удаляем старые задачи
    tasks_to_remove = []
    for task_id, task_data in _active_tasks.items():
        if task_data["status"] in ["completed", "failed", "cancelled"]:
            completed_at = task_data.get("completed_at")
            if completed_at and completed_at < cutoff_time:
                tasks_to_remove.append(task_id)

    for task_id in tasks_to_remove:
        del _active_tasks[task_id]
        if task_id in _task_results:
            del _task_results[task_id]
        cleanup_count += 1

    logger.info(f"🧹 Cleaned up {cleanup_count} old tasks")

    return {
        "message": f"Очищено {cleanup_count} старых задач",
        "active_tasks": len(_active_tasks),
    }


def initialize_generation_system():
    """Инициализация системы генерации при запуске"""
    logger.info("🧹 Initializing generation system...")
    _active_tasks.clear()
    _task_results.clear()
    logger.info("✅ Generation system initialized")

"""
API endpoints для асинхронной генерации профилей должностей.

Реализует современный паттерн async task processing:
1. POST /api/generation/start - запуск генерации (возвращает task_id)
2. GET /api/generation/{task_id}/status - получение статуса задачи
3. GET /api/generation/{task_id}/result - получение результата
4. DELETE /api/generation/{task_id} - отмена задачи
"""

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
from ..models.database import db_manager

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
    """Retrieve a ProfileGenerator instance with current settings."""
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

    # Обновляем статус на "processing"
    """Background task for generating a profile.
    
    This function manages the asynchronous process of generating a user profile.
    It updates the status of the task, validates the system, and generates the
    profile  using a specified generator. The function also handles progress
    updates and  saves the result to the database, while logging any errors that
    occur during  the process.
    """
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

        # Генерация профиля
        result = await generator.generate_profile(
            department=request.department,
            position=request.position,
            employee_name=request.employee_name,
            temperature=request.temperature,
            save_result=request.save_result,
        )

        _active_tasks[task_id].update(
            {"current_step": "Сохранение результата", "progress": 90}
        )

        # Сохраняем в БД
        if result["success"]:
            await save_generation_to_db(result, user_id, task_id)

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


async def save_generation_to_db(result: Dict[str, Any], user_id: int, task_id: str):
    """Saves the generation result to the database."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Создаем уникальный ID для профиля
        profile_id = str(uuid.uuid4())

        # Сохраняем профиль с правильной схемой
        cursor.execute(
            """
            INSERT INTO profiles (
                id, department, position, employee_name,
                profile_data, metadata_json,
                generation_duration_ms, tokens_used, langfuse_trace_id,
                created_by, created_at, updated_at, generation_task_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                profile_id,
                result["metadata"]["generation"]["department"],
                result["metadata"]["generation"]["position"],
                result["metadata"]["generation"].get("employee_name"),
                json.dumps(result["profile"], ensure_ascii=False),
                json.dumps(result["metadata"], ensure_ascii=False),
                int(result["metadata"]["generation"]["duration"] * 1000),
                result["metadata"]["llm"].get("tokens_used", 0),
                result["metadata"].get("langfuse_trace_id"),
                user_id,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                task_id,
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
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    # Создаем уникальный ID задачи
    """Starts the asynchronous generation of a job profile."""
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

    # Запускаем background task
    background_tasks.add_task(
        background_generate_profile, task_id, request, current_user["user_id"]
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
    """Retrieve the status of a generation task.
    
    Args:
        task_id: ID of the generation task.
    
    Returns:
        Current status of the task and result (if available).
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
    """Retrieve the result of a task generation.
    
    This function checks if the provided task_id exists in the active tasks.  It
    verifies the current user's access rights to the task and checks the  task's
    status. If the task is still in progress or the result is not  found,
    appropriate HTTP exceptions are raised. Finally, it returns the  result of the
    task if all checks pass.
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
    """Cancels a generation task if possible.
    
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
    """Retrieve a list of active tasks for the current user.
    
    This function checks the `_active_tasks` dictionary for tasks associated with
    the `current_user`. It filters out tasks that are completed, failed, or
    cancelled and older than one hour. The resulting active tasks are then
    returned as a list of `GenerationTask` instances.
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
    """Cleans up old completed tasks for admin users.
    
    This function checks if the current user is an admin before proceeding to
    remove tasks that have been completed, failed, or cancelled more than 24  hours
    ago. It iterates through the `_active_tasks` dictionary to identify  tasks that
    meet the criteria and removes them from both `_active_tasks`  and
    `_task_results`. The total number of tasks cleaned up is logged and  returned
    in the response.
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

"""
@doc Profile Management API endpoints

Реализует CRUD операции для управления сгенерированными профилями должностей.
Включает получение, поиск, фильтрацию, обновление и удаление профилей.

Examples:
    python>
    # GET /api/profiles - получить список профилей с пагинацией
    # GET /api/profiles/{profile_id} - получить конкретный профиль
    # DELETE /api/profiles/{profile_id} - удалить профиль
    # PUT /api/profiles/{profile_id} - обновить метаданные профиля
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import json
import sqlite3
from datetime import datetime

from ..models.schemas import ProfileResponse, ProfileListResponse, ProfileUpdateRequest
from .auth import get_current_user
from ..models.database import DatabaseManager
from ..utils.validators import (
    validate_profile_id,
    validate_pagination,
    validate_search_query,
    validate_optional_string,
    validate_status,
    validate_profile_update_request,
)
from ..utils.exceptions import NotFoundError, ValidationError, DatabaseError
from ..services.profile_storage_service import ProfileStorageService

router = APIRouter(prefix="/api/profiles", tags=["Profile Management"])
db_manager = DatabaseManager()
storage_service = ProfileStorageService()


@router.get("/", response_model=ProfileListResponse)
async def get_profiles(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей на страницу"),
    department: Optional[str] = Query(None, description="Фильтр по департаменту"),
    position: Optional[str] = Query(None, description="Фильтр по должности"),
    search: Optional[str] = Query(
        None, description="Поиск по имени/департаменту/должности"
    ),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    current_user: dict = Depends(get_current_user),
):
    """
    @doc Получить список профилей с пагинацией и фильтрацией

    Examples:
        python>
        # Получить первые 20 профилей
        GET /api/profiles?page=1&limit=20

        # Поиск профилей по департаменту
        GET /api/profiles?department=IT&page=1&limit=10

        # Текстовый поиск
        GET /api/profiles?search=developer&page=1&limit=5
    """
    # Валидация параметров запроса
    page, limit = validate_pagination(page, limit)
    department = validate_optional_string(department, "department", max_length=200)
    position = validate_optional_string(position, "position", max_length=200)
    search = validate_search_query(search)
    if status:
        status = validate_status(status)

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Базовый запрос
        base_query = """
            SELECT p.id as profile_id, p.department, p.position, p.employee_name,
                   p.created_at, p.updated_at, p.status, p.validation_score,
                   p.completeness_score, u.full_name as created_by_name, u.username as created_by_username
            FROM profiles p
            LEFT JOIN users u ON p.created_by = u.id
            WHERE 1=1
        """

        # Параметры для запроса
        params = []
        conditions = []

        # Применяем фильтры
        if department:
            conditions.append("p.department LIKE ?")
            params.append(f"%{department}%")

        if position:
            conditions.append("p.position LIKE ?")
            params.append(f"%{position}%")

        if search:
            conditions.append(
                """
                (p.employee_name LIKE ? OR 
                 p.department LIKE ? OR 
                 p.position LIKE ?)
            """
            )
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        if status:
            conditions.append("p.status = ?")
            params.append(status)

        # Собираем финальный запрос с условиями
        where_clause = " AND " + " AND ".join(conditions) if conditions else ""
        count_query = f"SELECT COUNT(*) FROM profiles p WHERE 1=1{where_clause}"

        # Считаем общее количество
        cursor.execute(count_query, params)
        count_result = cursor.fetchone()
        total_count = count_result[0] if count_result else 0

        # Добавляем пагинацию
        offset = (page - 1) * limit
        final_query = f"""
            {base_query}{where_clause}
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        # Выполняем основной запрос
        cursor.execute(final_query, params)
        rows = cursor.fetchall()

        profiles = []
        for row in rows:
            profile = {
                "profile_id": row["profile_id"],
                "department": row["department"],
                "position": row["position"],
                "employee_name": row["employee_name"],
                "status": row["status"],
                "validation_score": row["validation_score"],
                "completeness_score": row["completeness_score"],
                "created_at": row["created_at"],
                "created_by_username": row["created_by_username"],
                "actions": {
                    "download_json": f"/api/profiles/{row['profile_id']}/download/json",
                    "download_md": f"/api/profiles/{row['profile_id']}/download/md"
                }
            }
            profiles.append(profile)

        # Вычисляем метаданные пагинации
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1

        return {
            "profiles": profiles,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
            "filters_applied": {
                "department": department,
                "position": position,
                "search": search,
                "status": status,
            },
        }

    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch profiles: {str(e)}", operation="SELECT", table="profiles"
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected database error: {str(e)}", operation="SELECT", table="profiles"
        )


@router.get("/{profile_id}")
async def get_profile(profile_id: str, current_user: dict = Depends(get_current_user)):
    """
    @doc Получить конкретный профиль по ID

    Examples:
        python>
        # Получить профиль по ID
        GET /api/profiles/123e4567-e89b-12d3-a456-426614174000
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.*, u.full_name as created_by_name
            FROM profiles p
            LEFT JOIN users u ON p.created_by = u.id
            WHERE p.id = ?
        """,
            (profile_id,),
        )

        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        # Парсим JSON данные
        profile_data = json.loads(row["profile_data"])
        metadata = json.loads(row["metadata_json"])

        return {
            "profile_id": row["id"],
            "profile": profile_data.get("profile", profile_data), 
            "metadata": metadata,
            "created_at": row["created_at"],
            "created_by_username": row["created_by_name"],
            "actions": {
                "download_json": f"/api/profiles/{row['id']}/download/json",
                "download_md": f"/api/profiles/{row['id']}/download/md"
            }
        }

    except json.JSONDecodeError as e:
        raise DatabaseError(
            f"Invalid JSON data in profile {profile_id}: {str(e)}",
            operation="JSON_DECODE",
            table="profiles",
        )
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error fetching profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profiles",
        )


@router.put("/{profile_id}")
async def update_profile_metadata(
    profile_id: str,
    update_request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    @doc Обновить метаданные профиля (имя сотрудника, статус)

    Examples:
        python>
        # Обновить имя сотрудника
        PUT /api/profiles/123e4567-e89b-12d3-a456-426614174000
        {
            "employee_name": "Иванов Иван Иванович",
            "status": "completed"
        }
    """
    # Валидация profile_id и данных обновления
    profile_id = validate_profile_id(profile_id)
    validated_updates = validate_profile_update_request(
        employee_name=update_request.employee_name, status=update_request.status
    )

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля
        cursor.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        # Подготавливаем поля для обновления из валидированных данных
        update_fields = []
        params = []

        for field_name, field_value in validated_updates.items():
            update_fields.append(f"{field_name} = ?")
            params.append(field_value)

        # Добавляем updated_at
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(profile_id)

        # Выполняем обновление
        update_query = f"""
            UPDATE profiles 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """

        cursor.execute(update_query, params)
        conn.commit()

        if cursor.rowcount == 0:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        return {"message": "Profile updated successfully", "profile_id": profile_id}

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to update profile {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error updating profile {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Удалить профиль (soft delete - помечаем как архивный)

    Examples:
        python>
        # Удалить профиль
        DELETE /api/profiles/123e4567-e89b-12d3-a456-426614174000
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля
        cursor.execute("SELECT id, status FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()

        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        if row["status"] == "archived":
            raise ValidationError(
                "Profile is already archived",
                field="status",
                details={"current_status": "archived", "operation": "delete"},
            )

        # Soft delete - помечаем как архивный
        cursor.execute(
            """
            UPDATE profiles 
            SET status = 'archived', updated_at = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), profile_id),
        )

        conn.commit()

        return {
            "message": "Profile archived successfully",
            "profile_id": profile_id,
            "status": "archived",
        }

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to delete profile {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error deleting profile {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )


@router.post("/{profile_id}/restore")
async def restore_profile(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Восстановить архивный профиль

    Examples:
        python>
        # Восстановить профиль из архива
        POST /api/profiles/123e4567-e89b-12d3-a456-426614174000/restore
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля
        cursor.execute("SELECT id, status FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()

        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        if row["status"] != "archived":
            raise ValidationError(
                "Profile is not archived",
                field="status",
                details={"current_status": row["status"], "operation": "restore"},
            )

        # Восстанавливаем профиль
        cursor.execute(
            """
            UPDATE profiles 
            SET status = 'completed', updated_at = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), profile_id),
        )

        conn.commit()

        return {
            "message": "Profile restored successfully",
            "profile_id": profile_id,
            "status": "completed",
        }

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to restore profile {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error restoring profile {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )


@router.get("/{profile_id}/download/json")
async def download_profile_json(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Скачать JSON файл профиля

    Examples:
        python>
        # Скачать JSON файл профиля
        GET /api/profiles/123e4567-e89b-12d3-a456-426614174000/download/json
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Получаем информацию о профиле из БД
        cursor.execute(
            """
            SELECT id, department, position, created_at
            FROM profiles
            WHERE id = ?
        """,
            (profile_id,),
        )

        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        # Вычисляем путь к JSON файлу детерминистически
        created_at = datetime.fromisoformat(row["created_at"])
        json_path, _ = storage_service.get_profile_paths(
            profile_id=row["id"],
            department=row["department"],
            position=row["position"],
            created_at=created_at,
        )

        # Проверяем существование файла
        if not json_path.exists():
            raise NotFoundError(
                f"Profile JSON file not found at {json_path}",
                resource="file",
                resource_id=str(json_path),
            )

        # Возвращаем файл для скачивания
        return FileResponse(
            path=str(json_path),
            filename=f"profile_{row['position']}_{profile_id[:8]}.json",
            media_type="application/json",
            headers={"Content-Disposition": "attachment"},
        )

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error downloading profile {profile_id}: {str(e)}",
            operation="FILE_ACCESS",
            table="profiles",
        )


@router.get("/{profile_id}/download/md")
async def download_profile_md(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Скачать MD файл профиля

    Examples:
        python>
        # Скачать MD файл профиля
        GET /api/profiles/123e4567-e89b-12d3-a456-426614174000/download/md
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Получаем информацию о профиле из БД
        cursor.execute(
            """
            SELECT id, department, position, created_at
            FROM profiles
            WHERE id = ?
        """,
            (profile_id,),
        )

        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        # Вычисляем путь к MD файлу детерминистически
        created_at = datetime.fromisoformat(row["created_at"])
        _, md_path = storage_service.get_profile_paths(
            profile_id=row["id"],
            department=row["department"],
            position=row["position"],
            created_at=created_at,
        )

        # Проверяем существование файла
        if not md_path.exists():
            raise NotFoundError(
                f"Profile MD file not found at {md_path}",
                resource="file",
                resource_id=str(md_path),
            )

        # Возвращаем файл для скачивания
        return FileResponse(
            path=str(md_path),
            filename=f"profile_{row['position']}_{profile_id[:8]}.md",
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment"},
        )

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error downloading profile {profile_id}: {str(e)}",
            operation="FILE_ACCESS",
            table="profiles",
        )

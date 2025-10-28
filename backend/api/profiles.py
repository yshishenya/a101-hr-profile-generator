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

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import json
import sqlite3
import tempfile
import io
import os
import zipfile
from datetime import datetime
from pathlib import Path

from ..models.schemas import (
    ProfileListResponse,
    ProfileUpdateRequest,
    ProfileContentUpdateRequest,
    BulkDownloadRequest,
)
from .auth import get_current_user
from ..models.database import get_db_manager
from ..core.config import config
from ..utils.validators import (
    validate_profile_id,
    validate_pagination,
    validate_search_query,
    validate_optional_string,
    validate_status,
    validate_profile_update_request,
)
from ..utils.exceptions import (
    NotFoundError,
    ValidationError,
    DatabaseError,
    ServiceUnavailableError,
)
from ..core.storage_service import ProfileStorageService
from ..core.markdown_service import ProfileMarkdownService
from ..core.docx_service import initialize_docx_service

router = APIRouter(prefix="/api/profiles", tags=["Profile Management"])
storage_service = ProfileStorageService()
markdown_service = ProfileMarkdownService()
docx_service = initialize_docx_service()


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

    Возвращает список всех профилей с поддержкой пагинации, фильтрации по
    департаменту, должности, статусу и текстового поиска по всем полям.

    **Query Parameters:**
    - `page` (int): Номер страницы (по умолчанию: 1)
    - `limit` (int): Количество записей на страницу (1-100, по умолчанию: 20)
    - `department` (str, optional): Фильтр по названию департамента
      (поддерживает частичное совпадение)
    - `position` (str, optional): Фильтр по названию должности
      (поддерживает частичное совпадение)
    - `search` (str, optional): Текстовый поиск по имени сотрудника,
      департаменту и должности
    - `status` (str, optional): Фильтр по статусу
      ('completed', 'archived', 'in_progress')

    **Response Model:** ProfileListResponse
    - `profiles`: Массив профилей с базовой информацией
    - `pagination`: Метаданные пагинации (общее количество, страницы, навигация)
    - `filters_applied`: Примененные фильтры

    **Authentication:** Требуется Bearer Token

    Examples:
        bash>
        # 1. Получить первую страницу (5 записей на страницу)
        curl -X GET "http://localhost:8001/api/profiles/?page=1&limit=5" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json"

        # Response (200 OK):
        {
          "profiles": [
            {
              "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
              "department": "Группа анализа данных",
              "position": "Старший аналитик данных",
              "employee_name": "Иванова Анна Сергеевна",
              "status": "completed",
              "validation_score": 0.95,
              "completeness_score": 0.87,
              "created_at": "2025-01-10T14:30:22",
              "created_by_username": "admin",
              "actions": {
                "download_json": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/json",
                "download_md": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/md",
                "download_docx": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/docx"
              }
            }
          ],
          "pagination": {
            "page": 1,
            "limit": 5,
            "total": 8,
            "total_pages": 2,
            "has_next": true,
            "has_prev": false
          },
          "filters_applied": {
            "department": null,
            "position": null,
            "search": null,
            "status": null
          }
        }

        # 2. Фильтрация по департаменту (URL encoded)
        curl -X GET "http://localhost:8001/api/profiles/?department=%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%20%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%20%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Note: "Группа анализа данных" должно быть URL encoded

        # Response (200 OK) - только профили из указанного департамента:
        {
          "profiles": [
            {
              "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
              "department": "Группа анализа данных",
              "position": "Старший аналитик данных",
              "employee_name": "Иванова Анна Сергеевна",
              "status": "completed"
            }
          ],
          "pagination": {
            "page": 1,
            "limit": 20,
            "total": 1,
            "total_pages": 1,
            "has_next": false,
            "has_prev": false
          },
          "filters_applied": {
            "department": "Группа анализа данных",
            "position": null,
            "search": null,
            "status": null
          }
        }

        # 3. Текстовый поиск (поиск "analyst")
        curl -X GET "http://localhost:8001/api/profiles/?search=analyst" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (200 OK) - профили, содержащие "analyst" в названии должности:
        {
          "profiles": [
            {
              "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
              "department": "Группа анализа данных",
              "position": "Старший аналитик данных",
              "employee_name": "Иванова Анна Сергеевна"
            }
          ],
          "filters_applied": {
            "search": "analyst"
          }
        }

        # 4. Комбинированный поиск с пагинацией
        curl -X GET "http://localhost:8001/api/profiles/?page=2&limit=3&status=completed" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"
    """
    # Валидация параметров запроса
    page, limit = validate_pagination(page, limit)
    department = validate_optional_string(department, "department", max_length=200)
    position = validate_optional_string(position, "position", max_length=200)
    search = validate_search_query(search)
    if status:
        status = validate_status(status)

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Базовый запрос - оптимизирован с LEFT JOIN вместо подзапроса для производительности
        base_query = """
            SELECT p.id as profile_id, p.department, p.position, p.employee_name,
                   p.created_at, p.updated_at, p.status, p.validation_score,
                   p.completeness_score, p.current_version,
                   COALESCE(vc.version_count, 0) as version_count,
                   u.full_name as created_by_name, u.username as created_by_username
            FROM profiles p
            LEFT JOIN users u ON p.created_by = u.id
            LEFT JOIN (
                SELECT profile_id, COUNT(*) as version_count
                FROM profile_versions
                GROUP BY profile_id
            ) vc ON vc.profile_id = p.id
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
                "current_version": row["current_version"],
                "version_count": row["version_count"],
                "created_at": row["created_at"],
                "created_by_username": row["created_by_username"],
                "actions": {
                    "download_json": f"/api/profiles/{row['profile_id']}/download/json",
                    "download_md": f"/api/profiles/{row['profile_id']}/download/md",
                    "download_docx": f"/api/profiles/{row['profile_id']}/download/docx",
                },
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

    Возвращает полную информацию о профиле, включая все данные профиля,
    метаданные генерации и информацию о создателе.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля

    **Response:** Полный объект профиля с метаданными
    - `profile_id`: UUID профиля
    - `profile`: Полные данные профиля в JSON формате
    - `metadata`: Метаданные генерации (время, токены, модель)
    - `created_at`: Дата создания
    - `created_by_username`: Имя создателя
    - `actions`: Ссылки на действия (скачивание файлов)

    **Authentication:** Требуется Bearer Token

    Examples:
        bash>
        # 1. Получить профиль по ID
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json"

        # Response (200 OK):
        {
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
          "profile": {
            "position_info": {
              "title": "Старший аналитик данных",
              "department": "Группа анализа данных",
              "reporting_to": "Руководитель группы анализа данных",
              "subordinates": [],
              "employment_type": "full_time"
            },
            "responsibilities": [
              "Проведение глубокого анализа больших объемов данных",
              "Создание аналитических отчетов и дашбордов",
              "Разработка прогнозных моделей"
            ],
            "qualifications": {
              "education": "Высшее образование в области математики, статистики или IT",
              "experience": "От 3 лет опыта работы с данными",
              "skills": ["Python", "SQL", "Tableau", "Machine Learning"]
            },
            "kpis": [
              {
                "name": "Точность прогнозных моделей",
                "target_value": "> 85%",
                "measurement_frequency": "ежемесячно"
              }
            ]
          },
          "metadata": {
            "generation_id": "gen_20250110_143022_abc123",
            "model_used": "gemini-2.0-flash-exp",
            "tokens_used": 1250,
            "generation_time_ms": 3400,
            "langfuse_trace_id": "trace_abc123def456",
            "prompt_version": "v2.1"
          },
          "created_at": "2025-01-10T14:30:22",
          "created_by_username": "admin",
          "actions": {
            "download_json": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/json",
            "download_md": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/md",
            "download_docx": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/docx"
          }
        }

        # 2. Ошибка - профиль не найден
        curl -X GET "http://localhost:8001/api/profiles/nonexistent-profile-id" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-profile-id"
          }
        }

        # 3. Ошибка авторизации
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer invalid-token"

        # Response (401 Unauthorized):
        {
          "detail": "Invalid authentication token"
        }
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
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
                "download_md": f"/api/profiles/{row['id']}/download/md",
                "download_docx": f"/api/profiles/{row['id']}/download/docx",
            },
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

    Позволяет обновить метаданные существующего профиля. Поддерживается
    изменение имени сотрудника и статуса профиля.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для обновления

    **Request Body:** ProfileUpdateRequest
    - `employee_name` (str, optional): Новое имя сотрудника (только кириллица, пробелы, дефисы)
    - `status` (str, optional): Новый статус ('completed', 'archived', 'in_progress')

    **Response:** Сообщение об успешном обновлении
    - `message`: Текст подтверждения
    - `profile_id`: UUID обновленного профиля

    **Authentication:** Требуется Bearer Token

    **Validation Rules:**
    - `employee_name`: Максимум 200 символов, только кириллица, пробелы, дефисы
    - `status`: Должен быть одним из допустимых значений

    Examples:
        bash>
        # 1. Успешное обновление имени и статуса
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json" \
          -d '{
            "employee_name": "Петрова Мария Александровна",
            "status": "completed"
          }'

        # Response (200 OK):
        {
          "message": "Profile updated successfully",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef"
        }

        # 2. Обновление только имени сотрудника
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json" \
          -d '{
            "employee_name": "Сидоров Алексей Викторович"
          }'

        # Response (200 OK):
        {
          "message": "Profile updated successfully",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef"
        }

        # 3. Ошибка валидации - неправильное имя с спецсимволами
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json" \
          -d '{
            "employee_name": "John@Smith#123"
          }'

        # Response (422 Unprocessable Entity):
        {
          "detail": {
            "error": "Invalid employee_name format",
            "error_code": "VALIDATION_ERROR",
            "field": "employee_name",
            "details": {
              "allowed_pattern": "Only Cyrillic letters, spaces, and hyphens",
              "provided_value": "John@Smith#123"
            }
          }
        }

        # 4. Ошибка - профиль не найден
        curl -X PUT "http://localhost:8001/api/profiles/nonexistent-id" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json" \
          -d '{
            "employee_name": "Новое Имя"
          }'

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-id"
          }
        }

        # 5. Обновление статуса
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json" \
          -d '{
            "status": "archived"
          }'
    """
    # Валидация profile_id и данных обновления
    profile_id = validate_profile_id(profile_id)
    validated_updates = validate_profile_update_request(
        employee_name=update_request.employee_name, status=update_request.status
    )

    try:
        conn = get_db_manager().get_connection()
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


@router.put("/{profile_id}/content")
async def update_profile_content(
    profile_id: str,
    update_request: ProfileContentUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> dict[str, str]:
    """
    @doc Обновить содержимое профиля (profile_data)

    Позволяет обновить полное содержимое профиля (все секции).
    Этот endpoint используется для редактирования всех полей профиля:
    обязанностей, навыков, компетенций, образования, KPI и т.д.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для обновления

    **Request Body:** ProfileContentUpdateRequest
    - `profile_data` (dict): Полное содержимое профиля в JSON формате

    **Response:** Сообщение об успешном обновлении
    - `message`: Текст подтверждения
    - `profile_id`: UUID обновленного профиля

    **Authentication:** Требуется Bearer Token

    **Validation Rules:**
    Обязательные секции profile_data:
    - `position_title`: Название позиции (строка)
    - `department_specific`: Департамент (строка)
    - `responsibility_areas`: Зоны ответственности (массив объектов)
    - `professional_skills`: Профессиональные навыки (массив объектов)
    - `corporate_competencies`: Корпоративные компетенции (массив строк)
    - `personal_qualities`: Личные качества (массив строк)
    - `experience_and_education`: Опыт и образование (объект)

    Опциональные секции:
    - `careerogram`: Карьерограмма
    - `workplace_provisioning`: Обеспечение рабочего места
    - `performance_metrics`: Показатели эффективности
    - `additional_information`: Дополнительная информация
    - И другие секции

    Examples:
        bash>
        # Успешное обновление содержимого профиля
        curl -X PUT "http://localhost:8001/api/profiles/{profile_id}/content" \
          -H "Authorization: Bearer TOKEN" \
          -H "Content-Type: application/json" \
          -d '{
            "profile_data": {
              "position_title": "Backend Python Developer",
              "department_specific": "Департамент информационных технологий",
              "responsibility_areas": [
                {
                  "area": ["Разработка backend-сервисов"],
                  "tasks": ["Разработка API", "Интеграции с 1С"]
                }
              ],
              "professional_skills": [
                {
                  "skill_category": "Технические",
                  "specific_skills": [
                    {
                      "skill_name": "Python",
                      "proficiency_level": 3
                    }
                  ]
                }
              ],
              "corporate_competencies": ["Инновационность", "Результативность"],
              "personal_qualities": ["аналитическое мышление", "ответственность"],
              "experience_and_education": {
                "education_level": "Высшее",
                "total_work_experience": "От 3 лет"
              }
            }
          }'

        # Response (200 OK):
        {
          "message": "Profile content updated successfully",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef"
        }
    """
    # Валидация profile_id
    validate_profile_id(profile_id)

    try:
        # Получаем подключение к БД
        db_manager = get_db_manager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля
        cursor.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        # Сериализуем profile_data в JSON
        profile_data_json = json.dumps(
            update_request.profile_data, ensure_ascii=False, indent=2
        )

        # Обновляем profile_data и updated_at
        update_query = """
            UPDATE profiles
            SET profile_data = ?,
                updated_at = ?
            WHERE id = ?
        """

        cursor.execute(
            update_query,
            (profile_data_json, datetime.now().isoformat(), profile_id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        return {
            "message": "Profile content updated successfully",
            "profile_id": profile_id,
        }

    except (NotFoundError, ValidationError):
        raise
    except json.JSONEncodeError as e:
        raise ValidationError(
            f"Failed to encode profile_data to JSON: {str(e)}",
            field="profile_data",
        )
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to update profile content {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error updating profile content {profile_id}: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Удалить профиль (soft delete - помечаем как архивный)

    Выполняет «мягкое» удаление профиля, изменяя его статус на 'archived' вместо
    физического удаления из базы данных. Архивные профили можно восстановить.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для архивирования

    **Response:** Подтверждение архивирования
    - `message`: Текст подтверждения операции
    - `profile_id`: UUID архивированного профиля
    - `status`: Новый статус профиля ('archived')

    **Authentication:** Требуется Bearer Token

    **Business Logic:**
    - Проверяет существование профиля
    - Проверяет, что профиль еще не архивирован
    - Изменяет статус на 'archived' с обновлением времени
    - Архивированные профили исключаются из обычных поисков

    Examples:
        bash>
        # 1. Успешное архивирование профиля
        curl -X DELETE "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json"

        # Response (200 OK):
        {
          "message": "Profile archived successfully",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
          "status": "archived"
        }

        # 2. Ошибка - попытка архивировать уже архивированный профиль
        curl -X DELETE "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (422 Unprocessable Entity):
        {
          "detail": {
            "error": "Profile is already archived",
            "error_code": "VALIDATION_ERROR",
            "field": "status",
            "details": {
              "current_status": "archived",
              "operation": "delete"
            }
          }
        }

        # 3. Ошибка - профиль не найден
        curl -X DELETE "http://localhost:8001/api/profiles/nonexistent-profile-id" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-profile-id"
          }
        }

        # 4. Проверка результата архивирования через список профилей
        curl -X GET "http://localhost:8001/api/profiles/?status=archived" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N10.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response: список архивных профилей
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
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

    Восстанавливает архивированный профиль, возвращая ему статус 'completed'.
    Профиль снова становится доступным для обычных поисков и операций.

    **Path Parameters:**
    - `profile_id` (str): UUID архивированного профиля для восстановления

    **Response:** Подтверждение восстановления
    - `message`: Текст подтверждения операции
    - `profile_id`: UUID восстановленного профиля
    - `status`: Новый статус профиля ('completed')

    **Authentication:** Требуется Bearer Token

    **Business Logic:**
    - Проверяет существование профиля
    - Проверяет, что профиль действительно архивирован
    - Восстанавливает статус 'completed' с обновлением времени
    - Восстановленный профиль возвращается в обычные поиски

    Examples:
        bash>
        # 1. Успешное восстановление архивированного профиля
        curl -X POST "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/restore" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          -H "Content-Type: application/json"

        # Response (200 OK):
        {
          "message": "Profile restored successfully",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
          "status": "completed"
        }

        # 2. Ошибка - попытка восстановить неархивированный профиль
        curl -X POST "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/restore" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (422 Unprocessable Entity):
        {
          "detail": {
            "error": "Profile is not archived",
            "error_code": "VALIDATION_ERROR",
            "field": "status",
            "details": {
              "current_status": "completed",
              "operation": "restore"
            }
          }
        }

        # 3. Ошибка - профиль не найден
        curl -X POST "http://localhost:8001/api/profiles/nonexistent-profile-id/restore" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-profile-id"
          }
        }

        # 4. Проверка результата восстановления
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response: профиль со статусом 'completed'
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
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
    profile_id: str,
    version: Optional[int] = Query(None, ge=1, description="Номер версии для скачивания (опционально)"),
    current_user: dict = Depends(get_current_user)
):
    """
    @doc Скачать JSON файл профиля (с поддержкой версий)

    Скачивает полный профиль в JSON формате. Если указан параметр version,
    скачивается конкретная версия из истории. Без параметра - текущая версия из файловой системы.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для скачивания

    **Query Parameters:**
    - `version` (int, optional): Номер версии для скачивания (>= 1)

    **Response:** Файл JSON для скачивания
    - Content-Type: application/json
    - Content-Disposition: attachment
    - Имя файла: profile_{position}_{profile_id_short}_v{version}.json

    **Authentication:** Требуется Bearer Token

    **File Location Logic:**
    - Файлы хранятся в /generated_profiles/{department}/
    - Путь вычисляется детерминистично по profile_id + created_at
    - Имя файла: {position}_{timestamp}.json

    **Error Cases:**
    - 404: Профиль не найден в базе данных
    - 404: JSON файл не найден в файловой системе
    - 401: Невалидный токен авторизации

    Examples:
        bash>
        # 1. Успешное скачивание JSON файла
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/json" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          --output "profile_data_analyst.json"

        # Response (200 OK): Скачивание файла начнется автоматически
        # Headers:
        # Content-Type: application/json
        # Content-Disposition: attachment; filename="profile_Старший_аналитик_данных_4aec3e73.json"
        # Content-Length: 15420

        # File content: Полные данные профиля в JSON формате

        # 2. Ошибка - файл не найден (профиль существует, но файлы удалены)
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/json" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile JSON file not found at /generated_profiles/Группа_анализа_данных/Старший_аналитик_данных_20250110_143022.json",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "file",
            "resource_id": "/generated_profiles/Группа_анализа_данных/Старший_аналитик_данных_20250110_143022.json"
          }
        }

        # 3. Ошибка - профиль не найден в базе данных
        curl -X GET "http://localhost:8001/api/profiles/nonexistent-profile-id/download/json" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-profile-id"
          }
        }

        # 4. Пример скачивания с корректным именем файла
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/json" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          --output "/tmp/my_profile_$(date +%Y%m%d).json" \
          --silent --show-error

        # Проверка результата скачивания:
        ls -la /tmp/my_profile_*.json
        file /tmp/my_profile_*.json  # Покажет 'JSON data'
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Если запрошена конкретная версия - получаем из profile_versions
        if version is not None:
            # Проверяем существование профиля
            cursor.execute("SELECT position FROM profiles WHERE id = ?", (profile_id,))
            profile_row = cursor.fetchone()
            if not profile_row:
                raise NotFoundError(
                    "Profile not found", resource="profile", resource_id=profile_id
                )

            # Получаем конкретную версию
            cursor.execute(
                """
                SELECT profile_content, version_number
                FROM profile_versions
                WHERE profile_id = ? AND version_number = ?
            """,
                (profile_id, version),
            )

            version_row = cursor.fetchone()
            if not version_row:
                raise NotFoundError(
                    f"Version {version} not found for profile",
                    resource="profile_version",
                    resource_id=f"{profile_id}/{version}",
                )

            # Парсим JSON и возвращаем как файл из памяти
            profile_content = json.loads(version_row["profile_content"])
            json_bytes = json.dumps(profile_content, ensure_ascii=False, indent=2).encode('utf-8')

            return StreamingResponse(
                io.BytesIO(json_bytes),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="profile_{profile_row["position"]}_{profile_id[:8]}_v{version}.json"'
                }
            )

        # Если версия НЕ указана - используем текущую логику (файл с диска)
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
        json_path, _, _ = storage_service.get_profile_paths(
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


@router.get("/{profile_id}/download/docx")
async def download_profile_docx(
    profile_id: str,
    version: Optional[int] = Query(None, ge=1, description="Номер версии для скачивания (опционально)"),
    current_user: dict = Depends(get_current_user)
):
    """
    @doc Скачать DOCX файл профиля (с поддержкой версий)

    Скачивает профиль в формате Microsoft Word (DOCX). Если указан параметр version,
    скачивается конкретная версия (генерируется на лету из БД).

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для скачивания

    **Query Parameters:**
    - `version` (int, optional): Номер версии для скачивания (>= 1)

    **Response:** Файл Microsoft Word для скачивания
    - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
    - Content-Disposition: attachment
    - Имя файла: profile_{position}_{profile_id_short}_v{version}.docx

    **Authentication:** Требуется Bearer Token

    **File Location Logic:**
    - DOCX файлы хранятся рядом с JSON в /generated_profiles/{department}/
    - Путь вычисляется детерминистично по profile_id + created_at
    - Имя файла: {position}_{timestamp}.docx

    **DOCX Content Features:**
    - Корпоративные стили A101 (синий цвет, структурированные таблицы)
    - Профессиональные таблицы для навыков, KPI, инструментов
    - Заголовки с иконками и правильным форматированием
    - Метаданные генерации в подвале документа
    - Готовый для редактирования и печати формат

    **Error Cases:**
    - 404: Профиль не найден в базе данных
    - 404: DOCX файл не найден в файловой системе
    - 401: Невалидный токен авторизации

    Examples:
        bash>
        # 1. Успешное скачивание DOCX файла
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/docx" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
          --output "profile.docx"

        # Response (200 OK): Скачивание файла начнется автоматически
        # Headers:
        # Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
        # Content-Disposition: attachment; filename="profile_Старший_аналитик_данных_4aec3e73.docx"

        # 2. Ошибка - файл не найден (профиль существует, но DOCX файл удален)
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/docx" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile DOCX file not found at /generated_profiles/Группа_анализа_данных/Старший_аналитик_данных_20250110_143022.docx",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "file",
            "resource_id": "/generated_profiles/Группа_анализа_данных/Старший_аналитик_данных_20250110_143022.docx"
          }
        }
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Если запрошена конкретная версия - генерируем DOCX на лету
        if version is not None:
            # Проверяем существование профиля
            cursor.execute("SELECT position FROM profiles WHERE id = ?", (profile_id,))
            profile_row = cursor.fetchone()
            if not profile_row:
                raise NotFoundError(
                    "Profile not found", resource="profile", resource_id=profile_id
                )

            # Получаем конкретную версию
            cursor.execute(
                """
                SELECT profile_content, version_number
                FROM profile_versions
                WHERE profile_id = ? AND version_number = ?
            """,
                (profile_id, version),
            )

            version_row = cursor.fetchone()
            if not version_row:
                raise NotFoundError(
                    f"Version {version} not found for profile",
                    resource="profile_version",
                    resource_id=f"{profile_id}/{version}",
                )

            # Парсим JSON и генерируем DOCX через docx_service
            if not docx_service:
                raise ServiceUnavailableError("DOCX generation service is not available")

            profile_content = json.loads(version_row["profile_content"])

            # Создаем временный файл для DOCX
            temp_fd, temp_docx_path = tempfile.mkstemp(suffix=".docx")
            try:
                os.close(temp_fd)  # Закрываем дескриптор, docx_service откроет файл сам

                # Генерируем DOCX
                docx_service.create_docx_from_json(profile_content, temp_docx_path)

                # Возвращаем временный файл
                return FileResponse(
                    path=temp_docx_path,
                    filename=f'profile_{profile_row["position"]}_{profile_id[:8]}_v{version}.docx',
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": "attachment"},
                    background=lambda: Path(temp_docx_path).unlink(missing_ok=True)  # Удаляем после отправки
                )
            except Exception as e:
                # Очищаем временный файл при ошибке
                Path(temp_docx_path).unlink(missing_ok=True)
                raise

        # Если версия НЕ указана - используем текущую логику (файл с диска)
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

        # Вычисляем путь к DOCX файлу детерминистически
        created_at = datetime.fromisoformat(row["created_at"])
        _, _, docx_path = storage_service.get_profile_paths(
            profile_id=row["id"],
            department=row["department"],
            position=row["position"],
            created_at=created_at,
        )

        # Проверяем существование файла
        if not docx_path.exists():
            raise NotFoundError(
                f"Profile DOCX file not found at {docx_path}",
                resource="file",
                resource_id=str(docx_path),
            )

        # Возвращаем файл для скачивания
        return FileResponse(
            path=str(docx_path),
            filename=f"profile_{row['position']}_{profile_id[:8]}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
    profile_id: str,
    version: Optional[int] = Query(None, ge=1, description="Номер версии для скачивания (опционально)"),
    current_user: dict = Depends(get_current_user)
):
    """
    @doc Скачать MD файл профиля (с поддержкой версий)

    Скачивает профиль в Markdown формате. Если указан параметр version,
    скачивается конкретная версия (генерируется на лету из БД).

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для скачивания

    **Query Parameters:**
    - `version` (int, optional): Номер версии для скачивания (>= 1)

    **Response:** Файл Markdown для скачивания
    - Content-Type: text/markdown
    - Content-Disposition: attachment
    - Имя файла: profile_{position}_{profile_id_short}_v{version}.md

    **Authentication:** Требуется Bearer Token

    **File Location Logic:**
    - MD файлы хранятся рядом с JSON в /generated_profiles/{department}/
    - Путь вычисляется детерминистично по profile_id + created_at
    - Имя файла: {position}_{timestamp}.md

    **Markdown Content Structure:**
    - Заголовок с названием должности
    - Общая информация (департамент, подчинение)
    - Обязанности (маркированный список)
    - Квалификация и навыки
    - KPI и метрики (таблица)
    - Метаданные генерации

    **Error Cases:**
    - 404: Профиль не найден в базе данных
    - 404: MD файл не найден в файловой системе
    - 401: Невалидный токен авторизации

    Examples:
        bash>
        # 1. Успешное скачивание MD файла
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/md" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          --output "profile_analyst.md"

        # Response (200 OK): Скачивание файла начнется автоматически
        # Headers:
        # Content-Type: text/markdown
        # Content-Disposition: attachment; filename="profile_Старший_аналитик_данных_4aec3e73.md"
        # Content-Length: 8240

        # File content: Профиль в Markdown с красивым форматированием

        # 2. Просмотр содержимого файла в терминале
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/md" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE" \
          --silent | head -20

        # Output: Первые 20 строк MD файла
        # # Старший аналитик данных
        #
        # ## Общая информация
        # - **Департамент:** Группа анализа данных
        # - **Подчиняется:** Руководитель группы

        # 3. Ошибка - файл не найден (профиль существует, но MD файл удален)
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/md" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile MD file not found at /generated_profiles/Группа_анализа_данных/Старший_аналитик_данных_20250110_143022.md",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "file",
            "resource_id": "/generated_profiles/Группа_анализа_данных/Старший_аналитик_данных_20250110_143022.md"
          }
        }

        # 4. Ошибка - профиль не найден
        curl -X GET "http://localhost:8001/api/profiles/nonexistent-profile-id/download/md" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-profile-id"
          }
        }

        # 5. Комбинированное скачивание обоих форматов
        PROFILE_ID="4aec3e73-c9bd-4d25-a123-456789abcdef"
        AUTH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMTA5Mzc5N30.K8FgXOaVtDyVQs-wc2D8UgPMqGwNb_-pE3YKwN9TjeE"

        # Скачивание JSON
        curl -X GET "http://localhost:8001/api/profiles/${PROFILE_ID}/download/json" \
          -H "Authorization: Bearer ${AUTH_TOKEN}" \
          --output "profile_data.json" --silent

        # Скачивание MD
        curl -X GET "http://localhost:8001/api/profiles/${PROFILE_ID}/download/md" \
          -H "Authorization: Bearer ${AUTH_TOKEN}" \
          --output "profile_readable.md" --silent

        echo "Downloaded both formats:"
        ls -la profile_*
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Если запрошена конкретная версия - генерируем MD на лету
        if version is not None:
            # Проверяем существование профиля
            cursor.execute("SELECT position FROM profiles WHERE id = ?", (profile_id,))
            profile_row = cursor.fetchone()
            if not profile_row:
                raise NotFoundError(
                    "Profile not found", resource="profile", resource_id=profile_id
                )

            # Получаем конкретную версию
            cursor.execute(
                """
                SELECT profile_content, version_number
                FROM profile_versions
                WHERE profile_id = ? AND version_number = ?
            """,
                (profile_id, version),
            )

            version_row = cursor.fetchone()
            if not version_row:
                raise NotFoundError(
                    f"Version {version} not found for profile",
                    resource="profile_version",
                    resource_id=f"{profile_id}/{version}",
                )

            # Парсим JSON и генерируем MD через markdown_service
            profile_content = json.loads(version_row["profile_content"])
            md_content = markdown_service.generate_from_json(profile_content)
            md_bytes = md_content.encode('utf-8')

            return StreamingResponse(
                io.BytesIO(md_bytes),
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="profile_{profile_row["position"]}_{profile_id[:8]}_v{version}.md"'
                }
            )

        # Если версия НЕ указана - используем текущую логику (файл с диска)
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
        _, md_path, _ = storage_service.get_profile_paths(
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


# ============================================================================
# PROFILE VERSIONING ENDPOINTS
# ============================================================================


@router.get("/{profile_id}/versions")
async def get_profile_versions(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Получить список всех версий профиля

    Возвращает полный список версий профиля с метаданными каждой версии.
    Показывает, какая версия является текущей активной.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля

    **Response:** Список версий профиля
    - `versions`: Массив объектов версий (сортировка по version_number DESC)
    - `current_version`: Номер текущей активной версии
    - `total_versions`: Общее количество версий

    **Version Object Structure:**
    - `version_number` (int): Номер версии
    - `created_at` (datetime): Дата создания версии
    - `created_by_username` (str): Имя создателя версии
    - `version_type` (str): Тип версии ('generated', 'regenerated', 'edited')
    - `validation_score` (float): Оценка валидации
    - `completeness_score` (float): Оценка полноты
    - `is_current` (bool): Является ли версия текущей активной

    **Authentication:** Требуется Bearer Token

    Examples:
        bash>
        # 1. Получить список версий профиля
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (200 OK):
        {
          "versions": [
            {
              "version_number": 3,
              "created_at": "2025-01-15T10:30:00",
              "created_by_username": "admin",
              "version_type": "edited",
              "validation_score": 0.95,
              "completeness_score": 0.92,
              "is_current": true
            },
            {
              "version_number": 2,
              "created_at": "2025-01-12T14:20:00",
              "created_by_username": "hr_manager",
              "version_type": "regenerated",
              "validation_score": 0.90,
              "completeness_score": 0.88,
              "is_current": false
            },
            {
              "version_number": 1,
              "created_at": "2025-01-10T09:15:00",
              "created_by_username": "admin",
              "version_type": "generated",
              "validation_score": 0.85,
              "completeness_score": 0.82,
              "is_current": false
            }
          ],
          "current_version": 3,
          "total_versions": 3
        }

        # 2. Ошибка - профиль не найден
        curl -X GET "http://localhost:8001/api/profiles/nonexistent-id/versions" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Profile not found",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile",
            "resource_id": "nonexistent-id"
          }
        }
    """
    # Валидация profile_id
    profile_id = validate_profile_id(profile_id)

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля и получаем current_version
        cursor.execute(
            "SELECT current_version FROM profiles WHERE id = ?", (profile_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        current_version = row["current_version"] or 1

        # Получаем все версии профиля
        cursor.execute(
            """
            SELECT version_number, created_at, created_by_username, version_type,
                   validation_score, completeness_score
            FROM profile_versions
            WHERE profile_id = ?
            ORDER BY version_number DESC
        """,
            (profile_id,),
        )

        versions = []
        for v in cursor.fetchall():
            versions.append(
                {
                    "version_number": v["version_number"],
                    "created_at": v["created_at"],
                    "created_by_username": v["created_by_username"],
                    "version_type": v["version_type"],
                    "validation_score": v["validation_score"],
                    "completeness_score": v["completeness_score"],
                    "is_current": v["version_number"] == current_version,
                }
            )

        return {
            "versions": versions,
            "current_version": current_version,
            "total_versions": len(versions),
        }

    except NotFoundError:
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch versions for profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profile_versions",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error fetching versions for profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profile_versions",
        )


@router.get("/{profile_id}/versions/{version_number}")
async def get_profile_version(
    profile_id: str, version_number: int, current_user: dict = Depends(get_current_user)
):
    """
    @doc Получить конкретную версию профиля

    Возвращает полные данные конкретной версии профиля, включая содержимое
    профиля и метаданные генерации.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля
    - `version_number` (int): Номер версии (должен быть >= 1)

    **Response:** Полные данные версии
    - `version_number` (int): Номер версии
    - `profile_content` (object): Полное содержимое профиля
    - `generation_metadata` (object): Метаданные генерации
    - `created_at` (datetime): Дата создания версии
    - `created_by_username` (str): Имя создателя
    - `version_type` (str): Тип версии
    - `validation_score` (float): Оценка валидации
    - `completeness_score` (float): Оценка полноты
    - `is_current` (bool): Является ли текущей активной версией

    **Authentication:** Требуется Bearer Token

    Examples:
        bash>
        # 1. Получить версию 2 профиля
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/2" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (200 OK):
        {
          "version_number": 2,
          "profile_content": {
            "position_info": {
              "title": "Старший аналитик данных",
              "department": "Группа анализа данных",
              ...
            },
            "responsibilities": [...],
            "qualifications": {...},
            "kpis": [...]
          },
          "generation_metadata": {
            "generation_id": "gen_20250112_142000_xyz789",
            "model_used": "gemini-2.0-flash-exp",
            "tokens_used": 1300,
            ...
          },
          "created_at": "2025-01-12T14:20:00",
          "created_by_username": "hr_manager",
          "version_type": "regenerated",
          "validation_score": 0.90,
          "completeness_score": 0.88,
          "is_current": false
        }

        # 2. Ошибка - версия не найдена
        curl -X GET "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/999" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Version 999 not found for profile",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile_version",
            "resource_id": "4aec3e73-c9bd-4d25-a123-456789abcdef/999"
          }
        }
    """
    # Валидация
    profile_id = validate_profile_id(profile_id)

    if version_number < 1:
        raise ValidationError(
            "Version number must be >= 1",
            field="version_number",
            details={"provided_value": version_number},
        )

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля и получаем current_version
        cursor.execute(
            "SELECT current_version FROM profiles WHERE id = ?", (profile_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        current_version = row["current_version"] or 1

        # Получаем конкретную версию
        cursor.execute(
            """
            SELECT version_number, profile_content, generation_metadata,
                   created_at, created_by_username, version_type,
                   validation_score, completeness_score
            FROM profile_versions
            WHERE profile_id = ? AND version_number = ?
        """,
            (profile_id, version_number),
        )

        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                f"Version {version_number} not found for profile",
                resource="profile_version",
                resource_id=f"{profile_id}/{version_number}",
            )

        # Парсим JSON данные
        profile_content = json.loads(row["profile_content"])
        generation_metadata = (
            json.loads(row["generation_metadata"])
            if row["generation_metadata"]
            else None
        )

        return {
            "version_number": row["version_number"],
            "profile_content": profile_content,
            "generation_metadata": generation_metadata,
            "created_at": row["created_at"],
            "created_by_username": row["created_by_username"],
            "version_type": row["version_type"],
            "validation_score": row["validation_score"],
            "completeness_score": row["completeness_score"],
            "is_current": row["version_number"] == current_version,
        }

    except (NotFoundError, ValidationError):
        raise
    except json.JSONDecodeError as e:
        raise DatabaseError(
            f"Invalid JSON data in version {version_number}: {str(e)}",
            operation="JSON_DECODE",
            table="profile_versions",
        )
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch version {version_number} for profile {profile_id}: {str(e)}",
            operation="SELECT",
            table="profile_versions",
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error fetching version {version_number}: {str(e)}",
            operation="SELECT",
            table="profile_versions",
        )


@router.put("/{profile_id}/versions/{version_number}/set-active")
async def set_active_version(
    profile_id: str, version_number: int, current_user: dict = Depends(get_current_user)
):
    """
    @doc Установить версию как текущую активную

    Устанавливает указанную версию профиля как текущую активную. Активная версия
    отображается в списке профилей и используется при просмотре профиля.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля
    - `version_number` (int): Номер версии для активации (должен быть >= 1)

    **Response:** Подтверждение операции
    - `message`: Текст подтверждения
    - `profile_id`: UUID профиля
    - `previous_version`: Номер предыдущей активной версии
    - `current_version`: Номер новой активной версии

    **Business Logic:**
    - Проверяет существование профиля и версии
    - Обновляет поле current_version в таблице profiles
    - Обновляет profile_data в профиле данными из выбранной версии
    - Обновляет updated_at timestamp

    **Authentication:** Требуется Bearer Token

    Examples:
        bash>
        # 1. Установить версию 2 как активную
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/2/set-active" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
          -H "Content-Type: application/json"

        # Response (200 OK):
        {
          "message": "Version 2 set as active",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
          "previous_version": 3,
          "current_version": 2
        }

        # 2. Ошибка - версия не найдена
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/999/set-active" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Version 999 not found for profile",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile_version",
            "resource_id": "4aec3e73-c9bd-4d25-a123-456789abcdef/999"
          }
        }

        # 3. Попытка установить уже активную версию (допустимо)
        curl -X PUT "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/3/set-active" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (200 OK):
        {
          "message": "Version 3 set as active",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
          "previous_version": 3,
          "current_version": 3
        }
    """
    # Валидация
    profile_id = validate_profile_id(profile_id)

    if version_number < 1:
        raise ValidationError(
            "Version number must be >= 1",
            field="version_number",
            details={"provided_value": version_number},
        )

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля и получаем current_version
        cursor.execute(
            "SELECT current_version FROM profiles WHERE id = ?", (profile_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        previous_version = row["current_version"] or 1

        # Проверяем существование версии и получаем её данные
        cursor.execute(
            """
            SELECT profile_content, generation_metadata
            FROM profile_versions
            WHERE profile_id = ? AND version_number = ?
        """,
            (profile_id, version_number),
        )

        version_row = cursor.fetchone()
        if not version_row:
            raise NotFoundError(
                f"Version {version_number} not found for profile",
                resource="profile_version",
                resource_id=f"{profile_id}/{version_number}",
            )

        # Обновляем профиль: устанавливаем новую активную версию
        cursor.execute(
            """
            UPDATE profiles
            SET current_version = ?,
                profile_data = ?,
                metadata_json = ?,
                updated_at = ?
            WHERE id = ?
        """,
            (
                version_number,
                version_row["profile_content"],
                version_row["generation_metadata"],
                datetime.now().isoformat(),
                profile_id,
            ),
        )

        conn.commit()

        return {
            "message": f"Version {version_number} set as active",
            "profile_id": profile_id,
            "previous_version": previous_version,
            "current_version": version_number,
        }

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(
            f"Failed to set version {version_number} as active: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )
    except Exception as e:
        conn.rollback()
        raise DatabaseError(
            f"Unexpected error setting version {version_number} as active: {str(e)}",
            operation="UPDATE",
            table="profiles",
        )


@router.delete("/{profile_id}/versions/{version_number}")
async def delete_profile_version(
    profile_id: str, version_number: int, current_user: dict = Depends(get_current_user)
):
    """
    @doc Удалить конкретную версию профиля

    Удаляет указанную версию профиля из истории версий. Нельзя удалить
    текущую активную версию или последнюю оставшуюся версию.

    **Path Parameters:**
    - `profile_id` (str): UUID профиля
    - `version_number` (int): Номер версии для удаления (должен быть >= 1)

    **Response:** Подтверждение удаления
    - `message`: Текст подтверждения
    - `profile_id`: UUID профиля
    - `deleted_version`: Номер удаленной версии
    - `remaining_versions`: Количество оставшихся версий

    **Business Logic:**
    - Проверяет, что версия не является текущей активной
    - Проверяет, что это не последняя версия (минимум 1 версия должна остаться)
    - Удаляет версию из таблицы profile_versions

    **Authentication:** Требуется Bearer Token

    **Validation Rules:**
    - Нельзя удалить текущую активную версию (вернет 422)
    - Нельзя удалить последнюю оставшуюся версию (вернет 422)
    - Версия должна существовать (иначе 404)

    Examples:
        bash>
        # 1. Успешное удаление версии 1 (не активной)
        curl -X DELETE "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/1" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
          -H "Content-Type: application/json"

        # Response (200 OK):
        {
          "message": "Version 1 deleted successfully",
          "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
          "deleted_version": 1,
          "remaining_versions": 2
        }

        # 2. Ошибка - попытка удалить текущую активную версию
        curl -X DELETE "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/3" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (422 Unprocessable Entity):
        {
          "detail": {
            "error": "Cannot delete current active version",
            "error_code": "VALIDATION_ERROR",
            "field": "version_number",
            "details": {
              "current_version": 3,
              "requested_version": 3,
              "hint": "Set another version as active before deleting this one"
            }
          }
        }

        # 3. Ошибка - попытка удалить последнюю оставшуюся версию
        curl -X DELETE "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/1" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (422 Unprocessable Entity):
        {
          "detail": {
            "error": "Cannot delete last remaining version",
            "error_code": "VALIDATION_ERROR",
            "field": "version_number",
            "details": {
              "total_versions": 1,
              "hint": "Profile must have at least one version"
            }
          }
        }

        # 4. Ошибка - версия не найдена
        curl -X DELETE "http://localhost:8001/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/versions/999" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

        # Response (404 Not Found):
        {
          "detail": {
            "error": "Version 999 not found for profile",
            "error_code": "RESOURCE_NOT_FOUND",
            "resource": "profile_version",
            "resource_id": "4aec3e73-c9bd-4d25-a123-456789abcdef/999"
          }
        }
    """
    # Валидация
    profile_id = validate_profile_id(profile_id)

    if version_number < 1:
        raise ValidationError(
            "Version number must be >= 1",
            field="version_number",
            details={"provided_value": version_number},
        )

    try:
        conn = get_db_manager().get_connection()
        cursor = conn.cursor()

        # Проверяем существование профиля и получаем current_version
        cursor.execute(
            "SELECT current_version FROM profiles WHERE id = ?", (profile_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise NotFoundError(
                "Profile not found", resource="profile", resource_id=profile_id
            )

        current_version = row["current_version"] or 1

        # Проверяем, что удаляемая версия не является текущей активной
        if version_number == current_version:
            raise ValidationError(
                "Cannot delete current active version",
                field="version_number",
                details={
                    "current_version": current_version,
                    "requested_version": version_number,
                    "hint": "Set another version as active before deleting this one",
                },
            )

        # Проверяем существование версии
        cursor.execute(
            """
            SELECT version_number
            FROM profile_versions
            WHERE profile_id = ? AND version_number = ?
        """,
            (profile_id, version_number),
        )

        if not cursor.fetchone():
            raise NotFoundError(
                f"Version {version_number} not found for profile",
                resource="profile_version",
                resource_id=f"{profile_id}/{version_number}",
            )

        # Проверяем, что это не последняя версия
        cursor.execute(
            "SELECT COUNT(*) as count FROM profile_versions WHERE profile_id = ?",
            (profile_id,),
        )
        total_versions = cursor.fetchone()["count"]

        if total_versions <= 1:
            raise ValidationError(
                "Cannot delete last remaining version",
                field="version_number",
                details={
                    "total_versions": total_versions,
                    "hint": "Profile must have at least one version",
                },
            )

        # Удаляем версию
        cursor.execute(
            """
            DELETE FROM profile_versions
            WHERE profile_id = ? AND version_number = ?
        """,
            (profile_id, version_number),
        )

        conn.commit()

        return {
            "message": f"Version {version_number} deleted successfully",
            "profile_id": profile_id,
            "deleted_version": version_number,
            "remaining_versions": total_versions - 1,
        }

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(
            f"Failed to delete version {version_number}: {str(e)}",
            operation="DELETE",
            table="profile_versions",
        )
    except Exception as e:
        conn.rollback()
        raise DatabaseError(
            f"Unexpected error deleting version {version_number}: {str(e)}",
            operation="DELETE",
            table="profile_versions",
        )


# ============================================================================
# PROFILE REGENERATION ENDPOINT (TODO)
# ============================================================================


@router.post("/{profile_id}/regenerate")
async def regenerate_profile(
    profile_id: str, current_user: dict = Depends(get_current_user)
):
    """
    @doc Регенерировать профиль (создать новую версию)

    TODO: Полная реализация требует интеграции с background tasks из generation.py.

    Планируемая логика:
    1. Получить current_version и данные профиля
    2. Запустить background task для регенерации
    3. После генерации:
       - Увеличить current_version
       - Создать новую запись в profile_versions с version_type='regenerated'
       - Обновить profile_data в profiles
    4. Вернуть task_id для polling статуса

    **Path Parameters:**
    - `profile_id` (str): UUID профиля для регенерации

    **Response:** Task information для polling
    - `task_id`: ID фоновой задачи
    - `message`: Информационное сообщение

    **Authentication:** Требуется Bearer Token
    """
    profile_id = validate_profile_id(profile_id)

    # TODO: Реализовать полную логику регенерации
    # Требуется:
    # 1. Импортировать ProfileGenerator
    # 2. Создать background task аналогично generation.py
    # 3. Интегрировать с существующей системой версионирования

    raise ServiceUnavailableError(
        "Profile regeneration is not yet implemented. "
        "Please use the generation endpoint to create a new profile."
    )


# ============================================================================
# BULK DOWNLOAD ENDPOINT
# ============================================================================


@router.post("/bulk-download")
async def bulk_download_profiles(
    request: BulkDownloadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    @doc Массовое скачивание профилей в ZIP архиве

    Скачивает несколько профилей одним ZIP архивом. Поддерживает до 100 профилей за раз.
    Использует streaming response для эффективной работы с большими объемами данных.

    **Request Body:**
    - `profile_ids` (List[str]): Список UUID профилей (1-100)
    - `format` (str): Формат файлов - "json", "md", или "docx" (по умолчанию "docx")

    **Response:** ZIP архив для скачивания
    - Content-Type: application/zip
    - Content-Disposition: attachment
    - Имя файла: profiles_{count}.zip

    **Authentication:** Требуется Bearer Token

    **Error Cases:**
    - 400: Невалидный запрос (пустой список, некорректные UUID, неподдерживаемый формат)
    - 404: Один или несколько профилей не найдены (пропускаются, остальные включаются в архив)
    - 401: Невалидный токен авторизации

    Examples:
        bash>
        # 1. Скачать 3 профиля в DOCX формате
        curl -X POST "http://localhost:8001/api/profiles/bulk-download" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
          -H "Content-Type: application/json" \
          -d '{
            "profile_ids": [
              "4aec3e73-c9bd-4d25-a123-456789abcdef",
              "b1fc8d92-e5ae-4f36-b234-567890abcdef",
              "c2gd9ea3-f6bf-5g47-c345-678901bcdefg"
            ],
            "format": "docx"
          }' \
          --output "profiles_3.zip"

        # 2. Скачать профили в JSON формате
        curl -X POST "http://localhost:8001/api/profiles/bulk-download" \
          -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
          -H "Content-Type: application/json" \
          -d '{
            "profile_ids": ["4aec3e73-c9bd-4d25-a123-456789abcdef"],
            "format": "json"
          }' \
          --output "profile.zip"

        # Response (200 OK): ZIP архив скачивается автоматически
        # Headers:
        # Content-Type: application/zip
        # Content-Disposition: attachment; filename="profiles_3.zip"
    """
    profile_ids = request.profile_ids
    file_format = request.format

    # Создаем ZIP в памяти
    zip_buffer = io.BytesIO()

    conn = get_db_manager().get_connection()
    cursor = conn.cursor()

    successful_count = 0
    failed_ids = []

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for profile_id in profile_ids:
                try:
                    # Валидируем profile_id
                    profile_id = validate_profile_id(profile_id)

                    # Получаем информацию о профиле
                    cursor.execute(
                        """
                        SELECT id, department, position, created_at, profile_data
                        FROM profiles
                        WHERE id = ?
                        """,
                        (profile_id,)
                    )

                    row = cursor.fetchone()
                    if not row:
                        # Профиль не найден - пропускаем и добавляем в список failed
                        failed_ids.append(profile_id)
                        continue

                    # Генерируем безопасное имя файла
                    position_name = row["position"].replace("/", "_").replace("\\", "_")
                    profile_id_short = profile_id[:8]

                    if file_format == "json":
                        # JSON - берем из БД
                        profile_data = json.loads(row["profile_data"])
                        content = json.dumps(profile_data, ensure_ascii=False, indent=2)
                        filename = f"profile_{position_name}_{profile_id_short}.json"
                        zip_file.writestr(filename, content.encode('utf-8'))

                    elif file_format == "md":
                        # Markdown - генерируем на лету
                        created_at = datetime.fromisoformat(row["created_at"])
                        _, md_path, _ = storage_service.get_profile_paths(
                            profile_id=row["id"],
                            department=row["department"],
                            position=row["position"],
                            created_at=created_at
                        )

                        # Если MD файл существует - используем его
                        if md_path.exists():
                            with open(md_path, 'rb') as f:
                                content = f.read()
                        else:
                            # Генерируем MD из JSON
                            profile_data = json.loads(row["profile_data"])
                            md_content = markdown_service.generate_from_json(profile_data)
                            content = md_content.encode('utf-8')

                        filename = f"profile_{position_name}_{profile_id_short}.md"
                        zip_file.writestr(filename, content)

                    elif file_format == "docx":
                        # DOCX - генерируем на лету
                        created_at = datetime.fromisoformat(row["created_at"])
                        _, _, docx_path = storage_service.get_profile_paths(
                            profile_id=row["id"],
                            department=row["department"],
                            position=row["position"],
                            created_at=created_at
                        )

                        # Если DOCX файл существует - используем его
                        if docx_path.exists():
                            with open(docx_path, 'rb') as f:
                                content = f.read()
                        else:
                            # Генерируем DOCX из JSON
                            profile_data = json.loads(row["profile_data"])
                            content = docx_service.generate_from_json(profile_data)

                        filename = f"profile_{position_name}_{profile_id_short}.docx"
                        zip_file.writestr(filename, content)

                    successful_count += 1

                except Exception as e:
                    # Ошибка обработки конкретного профиля - пропускаем
                    failed_ids.append(profile_id)
                    continue

        # Подготавливаем ZIP для отправки
        zip_buffer.seek(0)

        # Определяем имя файла
        if successful_count == 0:
            raise NotFoundError(
                "No profiles could be downloaded",
                resource="profiles",
                resource_id=",".join(profile_ids)
            )

        filename = f"profiles_{successful_count}.zip"

        # Возвращаем streaming response
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Successful-Count": str(successful_count),
                "X-Failed-Count": str(len(failed_ids))
            }
        )

    except (NotFoundError, ValidationError):
        raise
    except sqlite3.Error as e:
        raise DatabaseError(
            f"Failed to fetch profiles for bulk download: {str(e)}",
            operation="SELECT",
            table="profiles"
        )
    except Exception as e:
        raise DatabaseError(
            f"Unexpected error during bulk download: {str(e)}",
            operation="BULK_DOWNLOAD",
            table="profiles"
        )

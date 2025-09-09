"""
@doc Input validation utilities for A101 HR Profile Generator

Централизованная валидация входных данных для всех API endpoints.
Включает бизнес-логику валидации и проверки на уровне приложения.

Examples:
    python>
    # Валидация департамента
    validate_department_name("IT Department")  # ✅
    validate_department_name("")  # ❌ ValidationError

    # Валидация профиля
    validate_profile_id("123e4567-e89b-12d3-a456-426614174000")  # ✅
"""

import re
import uuid
from typing import Optional, Dict, Any

from .exceptions import ValidationError


def validate_required_string(
    value: Optional[str], field_name: str, min_length: int = 1, max_length: int = 500
) -> str:
    """
    @doc Валидация обязательного строкового поля

    Examples:
        python>
        # Успешная валидация
        name = validate_required_string("John Doe", "employee_name")

        # Ошибка валидации
        validate_required_string("", "department")  # ValidationError
        validate_required_string(None, "position")  # ValidationError
    """
    if value is None:
        raise ValidationError(f"{field_name} is required", field=field_name)

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field=field_name)

    value = value.strip()

    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters long",
            field=field_name,
            details={"min_length": min_length, "actual_length": len(value)},
        )

    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be no more than {max_length} characters long",
            field=field_name,
            details={"max_length": max_length, "actual_length": len(value)},
        )

    return value


def validate_optional_string(
    value: Optional[str], field_name: str, min_length: int = 0, max_length: int = 500
) -> Optional[str]:
    """
    @doc Валидация опционального строкового поля

    Examples:
        python>
        # Опциональное поле
        desc = validate_optional_string(None, "description")  # None
        desc = validate_optional_string("Some text", "description")  # "Some text"
    """
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field=field_name)

    value = value.strip()

    if len(value) == 0:
        return None

    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters long",
            field=field_name,
        )

    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be no more than {max_length} characters long",
            field=field_name,
        )

    return value


def validate_department_name(department: str) -> str:
    """
    @doc Валидация названия департамента

    Examples:
        python>
        # Валидные департаменты
        validate_department_name("IT Department")
        validate_department_name("Отдел кадров")
        validate_department_name("Sales & Marketing")

        # Невалидные департаменты
        validate_department_name("")  # ValidationError
        validate_department_name("IT")  # ValidationError (слишком короткое)
    """
    department = validate_required_string(
        department, "department", min_length=3, max_length=200
    )

    # Проверяем на подозрительные символы
    if re.search(r'[<>{}()[\]"|\'`]', department):
        raise ValidationError(
            "Department name contains invalid characters",
            field="department",
            details={"invalid_chars": "< > { } ( ) [ ] | \" ' `"},
        )

    return department


def validate_position_name(position: str) -> str:
    """
    @doc Валидация названия должности

    Examples:
        python>
        # Валидные должности
        validate_position_name("Software Developer")
        validate_position_name("HR Manager")
        validate_position_name("Старший разработчик")

        # Невалидные должности
        validate_position_name("")  # ValidationError
        validate_position_name("Dev")  # ValidationError (слишком короткое)
    """
    position = validate_required_string(
        position, "position", min_length=3, max_length=200
    )

    # Проверяем на подозрительные символы
    if re.search(r'[<>{}()[\]"|\'`]', position):
        raise ValidationError(
            "Position name contains invalid characters",
            field="position",
            details={"invalid_chars": "< > { } ( ) [ ] | \" ' `"},
        )

    return position


def validate_employee_name(name: Optional[str]) -> Optional[str]:
    """
    @doc Валидация ФИО сотрудника

    Examples:
        python>
        # Валидные имена
        validate_employee_name("Иванов Иван Иванович")
        validate_employee_name("John Smith")
        validate_employee_name(None)  # Опционально

        # Невалидные имена
        validate_employee_name("A")  # ValidationError (слишком короткое)
    """
    if name is None:
        return None

    name = validate_optional_string(name, "employee_name", min_length=2, max_length=200)

    if name and re.search(r'[<>{}()[\]"|\'`@#$%^&*]', name):
        raise ValidationError(
            "Employee name contains invalid characters",
            field="employee_name",
            details={"invalid_chars": "< > { } ( ) [ ] | \" ' ` @ # $ % ^ & *"},
        )

    return name


def validate_profile_id(profile_id: str) -> str:
    """
    @doc Валидация ID профиля (UUID format)

    Examples:
        python>
        # Валидный UUID
        validate_profile_id("123e4567-e89b-12d3-a456-426614174000")

        # Невалидный UUID
        validate_profile_id("invalid-id")  # ValidationError
        validate_profile_id("")  # ValidationError
    """
    if not profile_id:
        raise ValidationError("Profile ID is required", field="profile_id")

    try:
        uuid.UUID(profile_id)
    except ValueError:
        raise ValidationError(
            "Profile ID must be a valid UUID",
            field="profile_id",
            details={
                "format": "UUID4",
                "example": "123e4567-e89b-12d3-a456-426614174000",
            },
        )

    return profile_id


def validate_pagination(page: int, limit: int) -> tuple[int, int]:
    """
    @doc Валидация параметров пагинации

    Examples:
        python>
        # Валидная пагинация
        validate_pagination(1, 20)  # (1, 20)
        validate_pagination(5, 50)  # (5, 50)

        # Невалидная пагинация
        validate_pagination(0, 20)  # ValidationError
        validate_pagination(1, 1000)  # ValidationError
    """
    if page < 1:
        raise ValidationError(
            "Page number must be greater than 0", field="page", details={"min_value": 1}
        )

    if limit < 1:
        raise ValidationError(
            "Limit must be greater than 0", field="limit", details={"min_value": 1}
        )

    if limit > 100:
        raise ValidationError(
            "Limit cannot exceed 100", field="limit", details={"max_value": 100}
        )

    return page, limit


def validate_status(status: str) -> str:
    """
    @doc Валидация статуса профиля

    Examples:
        python>
        # Валидные статусы
        validate_status("completed")
        validate_status("processing")
        validate_status("failed")
        validate_status("archived")

        # Невалидный статус
        validate_status("invalid")  # ValidationError
    """
    valid_statuses = {"completed", "processing", "failed", "archived"}

    if status not in valid_statuses:
        raise ValidationError(
            f"Invalid status value",
            field="status",
            details={"valid_values": list(valid_statuses), "provided_value": status},
        )

    return status


def validate_temperature(temperature: float) -> float:
    """
    @doc Валидация temperature параметра для LLM

    Examples:
        python>
        # Валидная temperature
        validate_temperature(0.1)  # 0.1
        validate_temperature(0.5)  # 0.5
        validate_temperature(1.0)  # 1.0

        # Невалидная temperature
        validate_temperature(-0.1)  # ValidationError
        validate_temperature(1.5)  # ValidationError
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError("Temperature must be a number", field="temperature")

    if temperature < 0.0 or temperature > 1.0:
        raise ValidationError(
            "Temperature must be between 0.0 and 1.0",
            field="temperature",
            details={"min_value": 0.0, "max_value": 1.0, "provided_value": temperature},
        )

    return float(temperature)


def validate_search_query(query: Optional[str]) -> Optional[str]:
    """
    @doc Валидация поискового запроса

    Examples:
        python>
        # Валидные запросы
        validate_search_query("developer")
        validate_search_query("IT department")
        validate_search_query(None)

        # Невалидные запросы
        validate_search_query("")  # None (пустой запрос)
        validate_search_query("a" * 300)  # ValidationError (слишком длинный)
    """
    if not query:
        return None

    query = query.strip()

    if len(query) == 0:
        return None

    if len(query) > 200:
        raise ValidationError(
            "Search query is too long",
            field="search",
            details={"max_length": 200, "actual_length": len(query)},
        )

    # Проверяем на подозрительные паттерны (SQL injection, XSS)
    suspicious_patterns = [
        r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",  # SQL keywords
        r"(<script|<iframe|<object|javascript:)",  # XSS patterns
        r"(UNION\s+SELECT|OR\s+1=1|AND\s+1=1)",  # SQL injection patterns
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValidationError(
                "Search query contains potentially malicious content",
                field="search",
                details={"reason": "security_filter"},
            )

    return query


def validate_json_data(data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    """
    @doc Валидация JSON данных на базовом уровне

    Examples:
        python>
        # Валидные данные
        validate_json_data({"key": "value"}, "profile_data")

        # Невалидные данные
        validate_json_data({}, "profile_data")  # ValidationError (пустой)
        validate_json_data({"x" * 1000: "y"}, "data")  # ValidationError (слишком большой ключ)
    """
    if not isinstance(data, dict):
        raise ValidationError(f"{schema_name} must be a JSON object", field=schema_name)

    if len(data) == 0:
        raise ValidationError(f"{schema_name} cannot be empty", field=schema_name)

    # Проверяем размер JSON (предотвращаем DoS атаки)
    json_str = str(data)
    if len(json_str) > 100_000:  # 100KB limit
        raise ValidationError(
            f"{schema_name} is too large",
            field=schema_name,
            details={"max_size_bytes": 100_000, "actual_size": len(json_str)},
        )

    # Проверяем глубину вложенности
    def check_depth(obj, current_depth=0, max_depth=10):
        if current_depth > max_depth:
            raise ValidationError(
                f"{schema_name} has too many nested levels",
                field=schema_name,
                details={"max_depth": max_depth},
            )

        if isinstance(obj, dict):
            for value in obj.values():
                check_depth(value, current_depth + 1, max_depth)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, current_depth + 1, max_depth)

    check_depth(data)

    return data


# Комбинированные валидаторы для API endpoints
def validate_profile_generation_request(
    department: str,
    position: str,
    employee_name: Optional[str] = None,
    temperature: float = 0.1,
) -> Dict[str, Any]:
    """
    @doc Комплексная валидация запроса генерации профиля

    Examples:
        python>
        # Валидный запрос
        data = validate_profile_generation_request(
            "IT Department",
            "Senior Developer",
            "John Doe",
            0.1
        )
    """
    return {
        "department": validate_department_name(department),
        "position": validate_position_name(position),
        "employee_name": validate_employee_name(employee_name),
        "temperature": validate_temperature(temperature),
    }


def validate_profile_search_request(
    page: int = 1,
    limit: int = 20,
    department: Optional[str] = None,
    position: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    @doc Комплексная валидация запроса поиска профилей

    Examples:
        python>
        # Валидный поиск
        params = validate_profile_search_request(
            page=1, limit=20,
            department="IT", search="developer"
        )
    """
    page, limit = validate_pagination(page, limit)

    filters = {
        "page": page,
        "limit": limit,
        "department": validate_optional_string(
            department, "department", max_length=200
        ),
        "position": validate_optional_string(position, "position", max_length=200),
        "search": validate_search_query(search),
        "status": validate_status(status) if status else None,
    }

    return {k: v for k, v in filters.items() if v is not None or k in ["page", "limit"]}


def validate_profile_update_request(
    employee_name: Optional[str] = None, status: Optional[str] = None
) -> Dict[str, Any]:
    """
    @doc Валидация запроса обновления профиля

    Examples:
        python>
        # Валидное обновление
        data = validate_profile_update_request(
            employee_name="Jane Doe",
            status="completed"
        )
    """
    updates = {}

    if employee_name is not None:
        updates["employee_name"] = validate_employee_name(employee_name)

    if status is not None:
        updates["status"] = validate_status(status)

    if not updates:
        raise ValidationError(
            "At least one field must be provided for update",
            details={"valid_fields": ["employee_name", "status"]},
        )

    return updates

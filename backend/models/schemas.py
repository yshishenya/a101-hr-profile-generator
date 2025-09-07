"""
Pydantic модели для API запросов и ответов системы генерации профилей А101.

Модели организованы по категориям:
- Authentication: Аутентификация и сессии
- Profile Generation: Генерация профилей
- Catalog: Каталоги департаментов и должностей
- Export: Экспорт данных
- System: Системная информация
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
import uuid


# ================================
# БАЗОВЫЕ МОДЕЛИ
# ================================

class BaseResponse(BaseModel):
    """Базовая модель ответа API"""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)
    message: Optional[str] = None


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(default=1, ge=1, description="Номер страницы")
    limit: int = Field(default=20, ge=1, le=100, description="Количество элементов на странице")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseResponse):
    """Ответ с пагинацией"""
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


# ================================
# AUTHENTICATION MODELS
# ================================

class LoginRequest(BaseModel):
    """Запрос на авторизацию"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    remember_me: bool = False


class LoginResponse(BaseResponse):
    """Ответ на успешную авторизацию"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_info: "UserInfo"


class UserInfo(BaseModel):
    """Информация о пользователе"""
    id: int
    username: str
    full_name: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


# ================================
# PROFILE GENERATION MODELS
# ================================

class GenerationStatus(str, Enum):
    """Статусы генерации профилей"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProfileGenerationRequest(BaseModel):
    """Запрос на генерацию профиля должности"""
    department: str = Field(..., min_length=2, max_length=200, description="Название департамента")
    position: str = Field(..., min_length=2, max_length=200, description="Название должности")
    employee_name: Optional[str] = Field(None, max_length=200, description="ФИО сотрудника (опционально)")
    
    # Дополнительные параметры генерации
    temperature: float = Field(default=0.1, ge=0.0, le=1.0, description="Температура LLM генерации")
    include_examples: bool = Field(default=True, description="Включить примеры профилей архитекторов")
    
    @field_validator("department", "position")
    @classmethod
    def validate_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Поле не может быть пустым")
        return v.strip()


class AsyncGenerationRequest(ProfileGenerationRequest):
    """Запрос на асинхронную генерацию профиля"""
    callback_url: Optional[str] = Field(None, description="URL для callback уведомлений")


class AsyncGenerationResponse(BaseResponse):
    """Ответ на запрос асинхронной генерации"""
    task_id: str
    status: GenerationStatus = GenerationStatus.PENDING
    estimated_completion: Optional[datetime] = None


class GenerationTaskStatus(BaseModel):
    """Статус выполнения задачи генерации"""
    task_id: str
    status: GenerationStatus
    progress: int = Field(ge=0, le=100, description="Прогресс выполнения в %")
    current_step: Optional[str] = None
    
    # Результат или ошибка
    result_profile_id: Optional[str] = None
    error_message: Optional[str] = None
    
    # Временные метки
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProfileValidation(BaseModel):
    """Результаты валидации профиля"""
    is_valid: bool
    completeness_score: float = Field(ge=0.0, le=1.0)
    errors: List[str] = []
    warnings: List[str] = []


class ProfileMetadata(BaseModel):
    """Метаданные генерации профиля"""
    model_config = ConfigDict(protected_namespaces=())
    
    generation_time_seconds: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model_name: str = "gemini-2.5-flash"
    temperature: float
    validation: ProfileValidation


class ProfileData(BaseModel):
    """Основные данные профиля должности"""
    # Базовая информация
    position_title: str
    department: str
    employee_name: Optional[str] = None
    
    # Структурированные данные профиля (соответствуют JSON Schema)
    basic_info: Dict[str, Any]
    responsibilities: List[Dict[str, Any]]
    professional_skills: Dict[str, List[Dict[str, Any]]]
    corporate_competencies: List[str]
    personal_qualities: List[str]
    education_experience: Dict[str, Any]
    career_paths: Dict[str, List[str]]


class ProfileResponse(BaseResponse):
    """Полный ответ с профилем должности"""
    profile_id: str
    profile: ProfileData
    metadata: ProfileMetadata
    created_at: datetime
    created_by_username: Optional[str] = None


class ProfileSummary(BaseModel):
    """Краткая информация о профиле для списков"""
    profile_id: str
    department: str
    position: str
    employee_name: Optional[str]
    status: GenerationStatus
    validation_score: float
    completeness_score: float
    created_at: datetime
    created_by_username: Optional[str]


# ================================
# CATALOG MODELS
# ================================

class DepartmentInfo(BaseModel):
    """Информация о департаменте"""
    name: str
    path: str  # Полный путь в иерархии
    level: int
    employees_count: int = 0
    has_positions: bool = True


class CatalogResponse(BaseResponse):
    """Ответ каталога департаментов или должностей"""
    items: List[Union[DepartmentInfo, str]]
    total_count: int


# ================================
# EXPORT MODELS
# ================================

class ExportFormat(str, Enum):
    """Поддерживаемые форматы экспорта"""
    JSON = "json"
    MARKDOWN = "md"
    EXCEL = "xlsx"


class ExportRequest(BaseModel):
    """Запрос на экспорт профиля"""
    profile_ids: List[str] = Field(..., min_items=1, max_items=50)
    format: ExportFormat
    include_metadata: bool = True
    compress: bool = False  # Для множественного экспорта


class ExportResponse(BaseResponse):
    """Ответ на запрос экспорта"""
    download_url: str
    filename: str
    file_size: int  # в байтах
    expires_at: datetime


# ================================
# SYSTEM MODELS  
# ================================

class ComponentStatus(BaseModel):
    """Статус компонента системы"""
    name: str
    status: str  # operational, degraded, down
    details: Optional[str] = None
    last_check: datetime


class SystemHealthResponse(BaseResponse):
    """Ответ проверки здоровья системы"""
    status: str  # healthy, degraded, unhealthy
    uptime_seconds: int
    version: str
    environment: str
    
    components: List[ComponentStatus]
    
    external_services: Dict[str, bool]  # openrouter_configured, langfuse_configured
    
    # Статистика
    total_profiles: int = 0
    successful_generations_today: int = 0
    active_tasks: int = 0


class SystemStats(BaseModel):
    """Системная статистика"""
    total_profiles: int
    total_users: int
    generations_today: int
    successful_generations: int
    failed_generations: int
    avg_generation_time: Optional[float]
    total_tokens_used: int


# ================================
# ERROR MODELS
# ================================

class ErrorDetail(BaseModel):
    """Детали ошибки"""
    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    success: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    error: str
    details: Optional[List[ErrorDetail]] = None
    path: Optional[str] = None
    request_id: Optional[str] = None


# ================================
# SEARCH & FILTER MODELS
# ================================

class ProfileSearchRequest(BaseModel):
    """Запрос поиска профилей"""
    query: Optional[str] = Field(None, max_length=200, description="Поисковый запрос")
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[GenerationStatus] = None
    created_by: Optional[str] = None
    
    # Фильтры по дате
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    # Фильтры по качеству
    min_validation_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    min_completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Сортировка  
    sort_by: str = Field(default="created_at", description="Поле для сортировки")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class ProfileSearchResponse(PaginatedResponse):
    """Ответ поиска профилей"""
    profiles: List[ProfileSummary]
    filters_applied: Dict[str, Any]


# ================================
# WEBHOOK MODELS (для будущего использования)
# ================================

class WebhookEvent(BaseModel):
    """Событие webhook"""
    event_type: str  # generation.completed, generation.failed
    profile_id: Optional[str] = None
    task_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


# Обновляем forward references
LoginResponse.model_rebuild()


if __name__ == "__main__":
    # Тестирование Pydantic моделей
    print("🔍 Тестирование Pydantic моделей...")
    
    # Тест запроса генерации
    generation_request = ProfileGenerationRequest(
        department="ДИТ",
        position="Системный архитектор",
        employee_name="Иванов Иван Иванович"
    )
    print("✅ ProfileGenerationRequest:", generation_request.dict())
    
    # Тест ответа
    profile_response = ProfileResponse(
        profile_id="test-123",
        profile=ProfileData(
            position_title="Системный архитектор",
            department="ДИТ",
            basic_info={"test": "data"},
            responsibilities=[],
            professional_skills={},
            corporate_competencies=[],
            personal_qualities=[],
            education_experience={},
            career_paths={}
        ),
        metadata=ProfileMetadata(
            generation_time_seconds=15.5,
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            temperature=0.1,
            validation=ProfileValidation(
                is_valid=True,
                completeness_score=0.95
            )
        ),
        created_at=datetime.now()
    )
    
    print("✅ ProfileResponse создан успешно")
    print("✅ Все Pydantic модели работают корректно!")
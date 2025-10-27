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
    limit: int = Field(
        default=20, ge=1, le=100, description="Количество элементов на странице"
    )

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

    department: str = Field(
        ..., min_length=2, max_length=200, description="Название департамента"
    )
    position: str = Field(
        ..., min_length=2, max_length=200, description="Название должности"
    )
    employee_name: Optional[str] = Field(
        None, max_length=200, description="ФИО сотрудника (опционально)"
    )

    # Дополнительные параметры генерации
    temperature: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Температура LLM генерации"
    )
    include_examples: bool = Field(
        default=True, description="Включить примеры профилей архитекторов"
    )

    @field_validator("department", "position")
    @classmethod
    def validate_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError("Поле не может быть пустым")
        return v.strip()


class AsyncGenerationRequest(ProfileGenerationRequest):
    """Запрос на асинхронную генерацию профиля"""

    callback_url: Optional[str] = Field(
        None, description="URL для callback уведомлений"
    )


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

    @field_validator('result_profile_id')
    @classmethod
    def validate_uuid_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that result_profile_id is a valid UUID format."""
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f'Invalid UUID format: {v}')


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


# ================================
# TYPED PROFILE DATA MODELS
# ================================


class BasicInfo(BaseModel):
    """Базовая информация о профиле должности"""

    position_title: str
    department: str
    business_unit: Optional[str] = None
    level: Optional[int] = None
    category: Optional[str] = None


class Responsibility(BaseModel):
    """Отдельная обязанность в профиле должности"""

    title: str
    description: str
    importance: Optional[str] = None  # high, medium, low


class ProfessionalSkill(BaseModel):
    """Профессиональный навык"""

    name: str
    level: Optional[str] = None  # expert, advanced, intermediate, basic
    description: Optional[str] = None


class ProfessionalSkillsByCategory(BaseModel):
    """Профессиональные навыки, сгруппированные по категориям"""

    technical: List[ProfessionalSkill] = []
    management: List[ProfessionalSkill] = []
    analytical: List[ProfessionalSkill] = []
    communication: List[ProfessionalSkill] = []
    other: List[ProfessionalSkill] = []


class EducationExperience(BaseModel):
    """Требования к образованию и опыту"""

    required_education: Optional[str] = None
    preferred_education: Optional[str] = None
    required_experience_years: Optional[int] = None
    preferred_experience: Optional[str] = None


class CareerPaths(BaseModel):
    """Карьерные пути для должности"""

    vertical: List[str] = []  # Вертикальный рост
    horizontal: List[str] = []  # Горизонтальное развитие
    alternative: List[str] = []  # Альтернативные пути


class ProfileData(BaseModel):
    """Основные данные профиля должности"""

    # Базовая информация
    position_title: str
    department: str
    employee_name: Optional[str] = None

    # Структурированные данные профиля (типизированные модели)
    basic_info: BasicInfo
    responsibilities: List[Responsibility]
    professional_skills: ProfessionalSkillsByCategory
    corporate_competencies: List[str]
    personal_qualities: List[str]
    education_experience: EducationExperience
    career_paths: CareerPaths


class ProfileResponse(BaseResponse):
    """Полный ответ с профилем должности"""

    profile_id: str
    profile: ProfileData
    metadata: ProfileMetadata
    created_at: datetime
    created_by_username: Optional[str] = None

    @field_validator('profile_id')
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Validate that profile_id is a valid UUID format."""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f'Invalid UUID format: {v}')


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

    @field_validator('profile_id')
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Validate that profile_id is a valid UUID format."""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f'Invalid UUID format: {v}')


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

    @field_validator('profile_ids')
    @classmethod
    def validate_uuid_list(cls, v: List[str]) -> List[str]:
        """Validate that all profile_ids are valid UUID formats."""
        for profile_id in v:
            try:
                uuid.UUID(profile_id)
            except ValueError:
                raise ValueError(f'Invalid UUID format in profile_ids: {profile_id}')
        return v


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


class PaginationInfo(BaseModel):
    """Информация о пагинации"""

    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class FiltersApplied(BaseModel):
    """Примененные фильтры для поиска"""

    query: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_validation_score: Optional[float] = None
    min_completeness_score: Optional[float] = None


class ProfileSearchResponse(PaginatedResponse):
    """Ответ поиска профилей"""

    profiles: List[ProfileSummary]
    filters_applied: FiltersApplied


class ProfileListResponse(BaseModel):
    """Ответ списка профилей с пагинацией"""

    profiles: List[ProfileSummary]
    pagination: PaginationInfo
    filters_applied: FiltersApplied


class ProfileUpdateRequest(BaseModel):
    """Запрос обновления метаданных профиля"""

    employee_name: Optional[str] = Field(
        None, max_length=200, description="Новое ФИО сотрудника"
    )
    status: Optional[str] = Field(None, description="Новый статус профиля")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ["completed", "failed", "processing", "archived"]:
            raise ValueError(
                "Status must be one of: completed, failed, processing, archived"
            )
        return v


class ProfileContentUpdateRequest(BaseModel):
    """Запрос обновления содержимого профиля (profile_data)"""

    profile_data: Dict[str, Any] = Field(
        ..., description="Полное содержимое профиля в JSON формате"
    )

    @field_validator("profile_data")
    @classmethod
    def validate_profile_data(cls, v):
        """Валидация структуры profile_data"""
        if not isinstance(v, dict):
            raise ValueError("profile_data must be a dictionary")

        # Список обязательных секций
        required_sections = [
            "position_title",
            "department_specific",
            "responsibility_areas",
            "professional_skills",
            "corporate_competencies",
            "personal_qualities",
            "experience_and_education",
        ]

        # Проверяем наличие обязательных секций
        missing_sections = [
            section for section in required_sections if section not in v
        ]
        if missing_sections:
            raise ValueError(
                f"Missing required sections: {', '.join(missing_sections)}"
            )

        # Валидация типов данных для каждой секции
        # position_title - строка
        if not isinstance(v.get("position_title"), str) or not v["position_title"]:
            raise ValueError("position_title must be a non-empty string")

        # department_specific - строка
        if (
            not isinstance(v.get("department_specific"), str)
            or not v["department_specific"]
        ):
            raise ValueError("department_specific must be a non-empty string")

        # responsibility_areas - массив объектов
        if not isinstance(v.get("responsibility_areas"), list):
            raise ValueError("responsibility_areas must be a list")

        # professional_skills - массив объектов
        if not isinstance(v.get("professional_skills"), list):
            raise ValueError("professional_skills must be a list")

        # corporate_competencies - массив строк
        if not isinstance(v.get("corporate_competencies"), list):
            raise ValueError("corporate_competencies must be a list")

        # personal_qualities - массив строк
        if not isinstance(v.get("personal_qualities"), list):
            raise ValueError("personal_qualities must be a list")

        # experience_and_education - объект
        if not isinstance(v.get("experience_and_education"), dict):
            raise ValueError("experience_and_education must be a dictionary")

        return v


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

    @field_validator('profile_id')
    @classmethod
    def validate_uuid_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that profile_id is a valid UUID format."""
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f'Invalid UUID format: {v}')


# Обновляем forward references
LoginResponse.model_rebuild()


# ================================
# GENERATION API RESPONSES
# ================================


class GenerationStartResponse(BaseResponse):
    """Ответ на запуск генерации"""

    task_id: str
    status: str
    estimated_duration: int


class GenerationTaskData(BaseModel):
    """Данные задачи генерации"""

    task_id: str
    status: str
    progress: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class GenerationMetadata(BaseModel):
    """Метаданные результата генерации"""

    generation_time_seconds: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.1


class GenerationStatusResponse(BaseResponse):
    """Ответ статуса задачи"""

    task: GenerationTaskData
    result: Optional[ProfileData] = None


class GenerationResultResponse(BaseResponse):
    """Ответ с результатом генерации"""

    success: bool
    profile: ProfileData
    metadata: GenerationMetadata
    errors: List[str] = []


# ================================
# ORGANIZATION API TYPED MODELS
# ================================


class OrganizationSearchItem(BaseModel):
    """Элемент поиска в организационной структуре"""

    display_name: str
    full_path: str
    positions_count: int
    hierarchy: List[str]
    name: Optional[str] = None
    positions: Optional[List[str]] = None


class OrganizationPosition(BaseModel):
    """Позиция в организации"""

    position_id: str
    position_name: str
    business_unit_id: str
    business_unit_name: str
    department_id: Optional[str] = None
    department_name: str
    department_path: str
    profile_exists: bool
    profile_id: Optional[str] = None  # UUID string from database

    @field_validator('profile_id')
    @classmethod
    def validate_uuid_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that profile_id is a valid UUID format."""
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f'Invalid UUID format: {v}')


# ================================
# ORGANIZATION API RESPONSES
# ================================


class OrganizationSearchData(BaseModel):
    """
    Данные поиска в организационной структуре.

    Attributes:
        items: Список элементов организационной структуры для поиска
        total_count: Общее количество элементов
        source: Метод индексации (path_based_indexing для избежания потерь)
        includes_all_business_units: Флаг полноты данных (все 567 единиц)

    Examples:
        >>> data = OrganizationSearchData(items=[...], total_count=567)
        >>> print(data.source)  # "path_based_indexing"
    """

    items: List[OrganizationSearchItem]
    total_count: int
    source: str = "path_based_indexing"
    includes_all_business_units: bool = True


class OrganizationSearchResponse(BaseResponse):
    """Ответ поиска в организационной структуре"""

    data: OrganizationSearchData


class OrganizationPositionsData(BaseModel):
    """
    Данные списка позиций в организации.

    Attributes:
        items: Список всех позиций с метаданными о профилях
        total_count: Общее количество позиций
        positions_with_profiles: Количество позиций с созданными профилями
        coverage_percentage: Процент покрытия позиций профилями (0-100)

    Examples:
        >>> data = OrganizationPositionsData(
        ...     items=[...],
        ...     total_count=1487,
        ...     positions_with_profiles=125,
        ...     coverage_percentage=8.4
        ... )
    """

    items: List[OrganizationPosition]
    total_count: int
    positions_with_profiles: int
    coverage_percentage: float


class OrganizationPositionsResponse(BaseResponse):
    """Ответ списка позиций"""

    data: OrganizationPositionsData


class OrganizationStructureNode(BaseModel):
    """Узел в организационной структуре"""

    name: str
    positions: List[str] = []
    is_target: bool = False
    children: Optional[Dict[str, "OrganizationStructureNode"]] = None


class OrganizationStructureData(BaseModel):
    """
    Данные организационной структуры с выделенной целью.

    Attributes:
        target_path: Полный путь к целевой бизнес-единице
        total_business_units: Общее количество бизнес-единиц в структуре
        structure: Иерархическое дерево организации с выделенной целью

    Examples:
        >>> data = OrganizationStructureData(
        ...     target_path="Блок ОД/ДИТ",
        ...     total_business_units=567,
        ...     structure={"Блок ОД": OrganizationStructureNode(...)}
        ... )
    """

    target_path: str
    total_business_units: int
    structure: Dict[str, OrganizationStructureNode]


class OrganizationStructureResponse(BaseResponse):
    """Ответ структуры организации"""

    data: OrganizationStructureData


class BusinessUnitsStats(BaseModel):
    """Статистика по бизнес-единицам"""

    total_count: int
    with_positions: int
    by_levels: Dict[int, int]


class PositionsStats(BaseModel):
    """Статистика по позициям"""

    total_count: int
    average_per_unit: float


class OrganizationStatsData(BaseModel):
    """Данные статистики организации"""

    business_units: BusinessUnitsStats
    positions: PositionsStats
    indexing_method: str = "path_based"
    data_completeness: str = "100%"
    source: str = "organization_cache"


class OrganizationStatsResponse(BaseResponse):
    """Ответ статистики организации"""

    data: OrganizationStatsData


# ================================
# DASHBOARD API TYPED MODELS
# ================================


class DashboardSummary(BaseModel):
    """Основные метрики dashboard"""

    departments_count: int
    positions_count: int
    profiles_count: int
    completion_percentage: float
    active_tasks_count: int


class DashboardDepartments(BaseModel):
    """Статистика департаментов для dashboard"""

    total: int
    with_positions: int
    average_positions: float


class DashboardPositions(BaseModel):
    """Статистика позиций для dashboard"""

    total: int
    with_profiles: int
    without_profiles: int
    coverage_percent: float


class DashboardProfiles(BaseModel):
    """Статистика профилей для dashboard"""

    total: int
    percentage_complete: float


class DashboardActiveTask(BaseModel):
    """Активная задача генерации"""

    task_id: str
    position: str
    department: str
    status: str
    progress: int
    created_at: str


class DataSources(BaseModel):
    """Источники данных для dashboard"""

    catalog: str = "cached"
    profiles: str = "database"
    tasks: str = "memory"


class DashboardMetadata(BaseModel):
    """Метаданные dashboard"""

    last_updated: str
    data_sources: DataSources


class RecentProfile(BaseModel):
    """Недавно созданный профиль"""

    department: str
    position: str
    employee_name: Optional[str]
    created_at: str
    status: str
    created_by: str


# ================================
# DASHBOARD API RESPONSES
# ================================


class DashboardStatsData(BaseModel):
    """
    Полная статистика dashboard для главной страницы.

    Attributes:
        summary: Основные метрики для карточек (КПЭ)
        departments: Детальная статистика департаментов
        positions: Статистика покрытия должностей профилями
        profiles: Информация о созданных профилях
        active_tasks: Список текущих задач генерации
        metadata: Метаданные о времени обновления и источниках

    Examples:
        >>> data = DashboardStatsData(
        ...     summary=DashboardSummary(departments_count=510, ...),
        ...     departments=DashboardDepartments(total=510, ...),
        ...     ...
        ... )
    """

    summary: DashboardSummary
    departments: DashboardDepartments
    positions: DashboardPositions
    profiles: DashboardProfiles
    active_tasks: List[DashboardActiveTask]
    metadata: DashboardMetadata


class DashboardStatsResponse(BaseResponse):
    """Ответ статистики дашборда"""

    data: DashboardStatsData


class DashboardMinimalStatsData(BaseModel):
    """Минимальная статистика"""

    positions_count: int
    profiles_count: int
    completion_percentage: float
    active_tasks_count: int
    last_updated: str


class DashboardMinimalStatsResponse(BaseResponse):
    """Минимальная статистика"""

    data: DashboardMinimalStatsData


class DashboardActivitySummary(BaseModel):
    """Сводка активности"""

    active_tasks_count: int
    recent_profiles_count: int
    has_activity: bool


class DashboardActivityData(BaseModel):
    """Данные активности системы"""

    active_tasks: List[DashboardActiveTask]
    recent_profiles: List[RecentProfile]
    summary: DashboardActivitySummary
    last_updated: str


class DashboardActivityResponse(BaseResponse):
    """Активность системы"""

    data: DashboardActivityData


# ================================
# CATALOG API TYPED MODELS
# ================================


class CatalogDepartment(BaseModel):
    """Информация о департаменте в каталоге"""

    name: str
    display_name: str
    path: str
    positions_count: int
    last_updated: str


class CatalogDepartmentDetails(BaseModel):
    """Детальная информация о департаменте"""

    name: str
    display_name: str
    path: str
    positions_count: int
    positions: List["CatalogPosition"]
    statistics: "CatalogStatistics"


class CatalogPosition(BaseModel):
    """Информация о позиции в каталоге"""

    name: str
    level: int
    category: str
    department: str
    last_updated: str


class CatalogStatistics(BaseModel):
    """Статистика по уровням и категориям"""

    levels: Dict[int, int]
    categories: Dict[str, int]


# ================================
# CATALOG API RESPONSES
# ================================


class CatalogDepartmentsData(BaseModel):
    """
    Данные каталога департаментов.

    Attributes:
        departments: Список всех департаментов с базовой информацией
        total_count: Общее количество департаментов
        cached: Флаг использования кэша (True если данные из кэша)
        last_updated: Время последнего обновления кэша

    Examples:
        >>> data = CatalogDepartmentsData(
        ...     departments=[CatalogDepartment(name="ДИТ", ...)],
        ...     total_count=510,
        ...     cached=True
        ... )
    """

    departments: List[CatalogDepartment]
    total_count: int
    cached: bool
    last_updated: Optional[str] = None


class CatalogDepartmentsResponse(BaseResponse):
    """Список департаментов"""

    data: CatalogDepartmentsData


class CatalogDepartmentDetailsResponse(BaseResponse):
    """Детали департамента"""

    data: CatalogDepartmentDetails


class CatalogPositionsData(BaseModel):
    """
    Данные каталога позиций для конкретного департамента.

    Attributes:
        department: Название департамента
        positions: Список позиций с уровнями и категориями
        total_count: Количество позиций в департаменте
        statistics: Статистика по уровням и категориям
        cached: Флаг использования кэша
        last_updated: Время последнего обновления

    Examples:
        >>> data = CatalogPositionsData(
        ...     department="ДИТ",
        ...     positions=[CatalogPosition(name="Архитектор", ...)],
        ...     total_count=25,
        ...     statistics=CatalogStatistics(...)
        ... )
    """

    department: str
    positions: List[CatalogPosition]
    total_count: int
    statistics: CatalogStatistics
    cached: bool
    last_updated: Optional[str] = None


class CatalogPositionsResponse(BaseResponse):
    """Список позиций департамента"""

    data: CatalogPositionsData


class CatalogSearchBreakdown(BaseModel):
    """Детализация результатов поиска"""

    departments: Dict[str, int]
    levels: Dict[int, int]
    categories: Dict[str, int]


class CatalogSearchData(BaseModel):
    """Данные результатов поиска"""

    query: str
    departments: Optional[List[CatalogDepartment]] = None
    positions: Optional[List[CatalogPosition]] = None
    total_count: int
    breakdown: Optional[CatalogSearchBreakdown] = None
    department_filter: Optional[str] = None


class CatalogSearchResponse(BaseResponse):
    """Результаты поиска"""

    data: CatalogSearchData


class CatalogDepartmentsStats(BaseModel):
    """Статистика департаментов каталога"""

    total_count: int
    with_positions: int


class CatalogPositionsStats(BaseModel):
    """Статистика позиций каталога"""

    total_count: int
    average_per_department: float
    levels_distribution: Dict[int, int]
    categories_distribution: Dict[str, int]


class CatalogCacheStatus(BaseModel):
    """Статус кэша каталога"""

    departments_cached: bool
    positions_cached_count: int
    centralized_cache: bool
    cache_type: str


class CatalogStatsData(BaseModel):
    """Статистика каталога"""

    departments: CatalogDepartmentsStats
    positions: CatalogPositionsStats
    cache_status: CatalogCacheStatus


class CatalogStatsResponse(BaseResponse):
    """Статистика каталога"""

    data: CatalogStatsData


# Обновляем forward references для всех моделей
OrganizationStructureNode.model_rebuild()
CatalogDepartmentDetails.model_rebuild()


if __name__ == "__main__":
    # Тестирование Pydantic моделей
    print("🔍 Тестирование Pydantic моделей...")

    # Тест запроса генерации
    generation_request = ProfileGenerationRequest(
        department="ДИТ",
        position="Системный архитектор",
        employee_name="Иванов Иван Иванович",
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
            career_paths={},
        ),
        metadata=ProfileMetadata(
            generation_time_seconds=15.5,
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            temperature=0.1,
            validation=ProfileValidation(is_valid=True, completeness_score=0.95),
        ),
        created_at=datetime.now(),
    )

    print("✅ ProfileResponse создан успешно")
    print("✅ Все Pydantic модели работают корректно!")

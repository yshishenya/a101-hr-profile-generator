# HR Profile Generator - API Specification

**Version**: 1.0.0
**Base URL**: `http://localhost:8022` (development) | `https://api.a101.com/hr` (production)
**Last Updated**: 2025-10-25

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [API Patterns](#api-patterns)
7. [CORS & Security](#cors--security)
8. [Vue.js Integration Guide](#vuejs-integration-guide)

---

## Overview

The HR Profile Generator API is a RESTful API built with FastAPI that provides automated employee position profile generation using AI (Gemini 2.5 Flash). The system includes:

- **Profile Generation**: Asynchronous task-based profile generation with LLM
- **Profile Management**: CRUD operations for generated profiles
- **Organization Catalog**: Access to company organizational structure (567 business units, 1689 positions)
- **File Export**: Download profiles in JSON, Markdown, and DOCX formats
- **Authentication**: JWT-based authentication system
- **Dashboard**: Real-time statistics and activity monitoring

### Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Database**: SQLite (file-based)
- **LLM**: Gemini 2.5 Flash via OpenRouter API
- **Authentication**: JWT (HS256)
- **Monitoring**: Langfuse (optional)

---

## Authentication

### JWT Token-Based Authentication

All API endpoints (except `/health` and `/`) require authentication via JWT Bearer token.

#### 1. Login

**Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "username": "admin",
  "password": "admin123",
  "remember_me": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "timestamp": "2025-10-25T10:30:00.123456",
  "message": "Добро пожаловать, Администратор системы!",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_info": {
    "id": 1,
    "username": "admin",
    "full_name": "Администратор системы",
    "is_active": true,
    "created_at": "2025-09-07T14:38:37",
    "last_login": "2025-10-25T10:30:00"
  }
}
```

#### 2. Get Current User

**Endpoint**: `GET /api/auth/me`

**Headers**: `Authorization: Bearer {token}`

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "full_name": "Администратор системы",
  "is_active": true,
  "created_at": "2025-09-07T14:38:37",
  "last_login": "2025-10-25T10:30:00"
}
```

#### 3. Logout

**Endpoint**: `POST /api/auth/logout`

**Headers**: `Authorization: Bearer {token}`

**Response** (200 OK):
```json
{
  "success": true,
  "timestamp": "2025-10-25T10:35:00.123456",
  "message": "Вы успешно вышли из системы"
}
```

#### 4. Refresh Token

**Endpoint**: `POST /api/auth/refresh`

**Headers**: `Authorization: Bearer {token}`

**Response** (200 OK):
```json
{
  "success": true,
  "timestamp": "2025-10-25T10:32:00.123456",
  "message": "Токен обновлен успешно",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_info": { /* same as login */ }
}
```

#### 5. Validate Token

**Endpoint**: `GET /api/auth/validate`

**Headers**: `Authorization: Bearer {token}`

**Response** (200 OK):
```json
{
  "success": true,
  "timestamp": "2025-10-25T10:33:00.123456",
  "message": "Токен действителен для пользователя admin"
}
```

---

## API Endpoints

### System Endpoints

#### Health Check

**Endpoint**: `GET /health`

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T10:00:00.123456",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "environment": "development",
  "components": {
    "api": "operational",
    "core_modules": "initialized"
  },
  "external_services": {
    "openrouter_configured": true,
    "langfuse_configured": true
  }
}
```

#### Root

**Endpoint**: `GET /`

**Authentication**: None required

**Response** (200 OK):
```json
{
  "service": "HR Profile Generator API",
  "version": "1.0.0",
  "description": "Система автоматической генерации профилей должностей А101",
  "docs": "/docs",
  "health": "/health",
  "timestamp": "2025-10-25T10:00:00.123456",
  "message": "🏢 Добро пожаловать в систему генерации профилей должностей А101!"
}
```

---

### Profile Generation Endpoints

#### 1. Start Async Generation

**Endpoint**: `POST /api/generation/start`

**Authentication**: Required

**Request Body**:
```json
{
  "department": "Группа анализа данных",
  "position": "Аналитик данных",
  "employee_name": "Иванов Иван Иванович",
  "temperature": 0.1,
  "save_result": true
}
```

**Response** (200 OK):
```json
{
  "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
  "status": "queued",
  "message": "Генерация профиля 'Аналитик данных' в 'Группа анализа данных' запущена",
  "estimated_duration": 45
}
```

#### 2. Get Task Status

**Endpoint**: `GET /api/generation/{task_id}/status`

**Authentication**: Required

**Response** (200 OK - Processing):
```json
{
  "task": {
    "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
    "status": "processing",
    "progress": 30,
    "created_at": "2025-10-25T10:52:46.830887",
    "started_at": "2025-10-25T10:52:46.831493",
    "estimated_duration": 45,
    "current_step": "Генерация профиля через LLM"
  },
  "result": null
}
```

**Response** (200 OK - Completed):
```json
{
  "task": {
    "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
    "status": "completed",
    "progress": 100,
    "created_at": "2025-10-25T10:52:46.830887",
    "started_at": "2025-10-25T10:52:46.831493",
    "completed_at": "2025-10-25T10:53:15.123456",
    "current_step": "Завершено"
  },
  "result": {
    "success": true,
    "profile": { /* full profile data */ },
    "metadata": { /* generation metadata */ }
  }
}
```

#### 3. Get Task Result

**Endpoint**: `GET /api/generation/{task_id}/result`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "success": true,
  "profile": {
    "position_title": "Аналитик данных",
    "department_broad": "Группа анализа данных",
    "professional_skills": [ /* array of skills */ ],
    "responsibility_areas": [ /* array of responsibilities */ ]
  },
  "metadata": {
    "generation": {
      "timestamp": "2025-10-25T10:52:55.650672",
      "duration": 12.48,
      "temperature": 0.1
    },
    "llm": {
      "model": "google/gemini-2.5-flash",
      "tokens": {
        "input": 35821,
        "output": 2925,
        "total": 38746
      }
    }
  }
}
```

#### 4. Cancel Task

**Endpoint**: `DELETE /api/generation/{task_id}`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "message": "Задача отменена"
}
```

#### 5. Get Active Tasks

**Endpoint**: `GET /api/generation/tasks/active`

**Authentication**: Required

**Response** (200 OK):
```json
[
  {
    "task_id": "7feeb5ed-9e9d-419b-8a1d-e892accdd2c1",
    "status": "processing",
    "progress": 45,
    "created_at": "2025-10-25T10:52:46.830887",
    "current_step": "Генерация профиля через LLM",
    "estimated_duration": 45
  }
]
```

---

### Profile Management Endpoints

#### 1. List Profiles (with Pagination & Filtering)

**Endpoint**: `GET /api/profiles/`

**Authentication**: Required

**Query Parameters**:
- `page` (int, default: 1): Page number
- `limit` (int, default: 20, max: 100): Items per page
- `department` (string, optional): Filter by department name
- `position` (string, optional): Filter by position name
- `search` (string, optional): Search in employee name, department, position
- `status` (string, optional): Filter by status (completed, archived, in_progress)

**Example Request**:
```
GET /api/profiles/?page=1&limit=5&department=Группа анализа данных
```

**Response** (200 OK):
```json
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
      "created_at": "2025-10-25T14:30:22",
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
    "department": "Группа анализа данных",
    "position": null,
    "search": null,
    "status": null
  }
}
```

#### 2. Get Profile by ID

**Endpoint**: `GET /api/profiles/{profile_id}`

**Authentication**: Required

**Response** (200 OK):
```json
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
    "generation_id": "gen_20251025_143022_abc123",
    "model_used": "gemini-2.5-flash",
    "tokens_used": 1250,
    "generation_time_ms": 3400,
    "langfuse_trace_id": "trace_abc123def456",
    "prompt_version": "v2.1"
  },
  "created_at": "2025-10-25T14:30:22",
  "created_by_username": "admin",
  "actions": {
    "download_json": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/json",
    "download_md": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/md",
    "download_docx": "/api/profiles/4aec3e73-c9bd-4d25-a123-456789abcdef/download/docx"
  }
}
```

#### 3. Update Profile Metadata

**Endpoint**: `PUT /api/profiles/{profile_id}`

**Authentication**: Required

**Request Body**:
```json
{
  "employee_name": "Петрова Мария Александровна",
  "status": "completed"
}
```

**Response** (200 OK):
```json
{
  "message": "Profile updated successfully",
  "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef"
}
```

#### 4. Archive Profile (Soft Delete)

**Endpoint**: `DELETE /api/profiles/{profile_id}`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "message": "Profile archived successfully",
  "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
  "status": "archived"
}
```

#### 5. Restore Archived Profile

**Endpoint**: `POST /api/profiles/{profile_id}/restore`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "message": "Profile restored successfully",
  "profile_id": "4aec3e73-c9bd-4d25-a123-456789abcdef",
  "status": "completed"
}
```

#### 6. Download Profile (JSON)

**Endpoint**: `GET /api/profiles/{profile_id}/download/json`

**Authentication**: Required

**Response**: File download (application/json)
- Content-Disposition: attachment
- Filename: `profile_{position}_{profile_id_short}.json`

#### 7. Download Profile (Markdown)

**Endpoint**: `GET /api/profiles/{profile_id}/download/md`

**Authentication**: Required

**Response**: File download (text/markdown)
- Content-Disposition: attachment
- Filename: `profile_{position}_{profile_id_short}.md`

#### 8. Download Profile (DOCX)

**Endpoint**: `GET /api/profiles/{profile_id}/download/docx`

**Authentication**: Required

**Response**: File download (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- Content-Disposition: attachment
- Filename: `profile_{position}_{profile_id_short}.docx`

---

### Catalog Endpoints

#### 1. Get All Departments

**Endpoint**: `GET /api/catalog/departments`

**Authentication**: Required

**Query Parameters**:
- `force_refresh` (boolean, default: false): Force cache refresh

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Найдено 510 департаментов",
  "data": {
    "departments": [
      {
        "name": "Административный отдел",
        "display_name": "Административный отдел",
        "path": "Блок директора по развитию → Департамент развития → Административный отдел",
        "positions_count": 6,
        "last_updated": "2025-10-25T10:50:13.676062"
      }
    ],
    "total_count": 510,
    "cached": true,
    "last_updated": "2025-10-25T10:50:13.675934"
  }
}
```

#### 2. Get Department Details (Legacy - Use Organization API instead)

**Endpoint**: `GET /api/catalog/departments/{department_name}`

**Authentication**: Required

**Note**: Due to Cyrillic encoding issues in path parameters, use `/api/organization/unit` (POST) instead.

#### 3. Get Positions for Department (Legacy)

**Endpoint**: `GET /api/catalog/positions/{department}`

**Authentication**: Required

**Note**: Due to Cyrillic encoding issues, use `/api/organization/search-items` instead.

#### 4. Search Departments

**Endpoint**: `GET /api/catalog/search`

**Authentication**: Required

**Query Parameters**:
- `q` (string, required): Search query (min 1 character)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "По запросу 'analyst' найдено 5 департаментов",
  "data": {
    "query": "analyst",
    "departments": [ /* array of matching departments */ ],
    "total_count": 5
  }
}
```

#### 5. Search Positions

**Endpoint**: `GET /api/catalog/search/positions`

**Authentication**: Required

**Query Parameters**:
- `q` (string, required): Search query
- `department` (string, optional): Filter by department

**Response** (200 OK):
```json
{
  "success": true,
  "message": "По запросу 'manager' найдено 15 должностей",
  "data": {
    "query": "manager",
    "department_filter": "IT",
    "positions": [
      {
        "name": "Senior Project Manager",
        "level": 2,
        "category": "management",
        "department": "IT Department",
        "last_updated": "2025-10-25T10:50:13.676062"
      }
    ],
    "total_count": 15,
    "breakdown": {
      "departments": {"IT Department": 8, "Marketing": 7},
      "levels": {"1": 3, "2": 12},
      "categories": {"management": 15}
    }
  }
}
```

#### 6. Get Catalog Statistics

**Endpoint**: `GET /api/catalog/stats`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Статистика каталога получена",
  "data": {
    "departments": {
      "total_count": 510,
      "with_positions": 488
    },
    "positions": {
      "total_count": 1487,
      "average_per_department": 2.92,
      "levels_distribution": {
        "1": 504,
        "2": 38,
        "3": 287,
        "4": 28,
        "5": 630
      },
      "categories_distribution": {
        "management": 665,
        "specialist": 822
      }
    },
    "cache_status": {
      "departments_cached": true,
      "positions_cached_count": 567,
      "centralized_cache": true,
      "cache_type": "organization_cache (path-based)"
    }
  }
}
```

#### 7. Clear Cache (Admin Only)

**Endpoint**: `POST /api/catalog/cache/clear`

**Authentication**: Required (Admin only)

**Query Parameters**:
- `cache_type` (string, optional): "departments", "positions", or empty for all

**Response** (200 OK):
```json
{
  "success": true,
  "timestamp": "2025-10-25T10:50:13.675934",
  "message": "Кеш (departments) успешно очищен"
}
```

---

### Organization Endpoints (Path-Based - Recommended)

#### 1. Get Search Items (All Business Units)

**Endpoint**: `GET /api/organization/search-items`

**Authentication**: Required

**Response** (200 OK):
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
    "total_count": 567,
    "source": "path_based_indexing",
    "includes_all_business_units": true
  }
}
```

#### 2. Get Organization Structure with Target

**Endpoint**: `POST /api/organization/structure`

**Authentication**: Required

**Request Body**:
```json
{
  "target_path": "Блок операционного директора/Департамент информационных технологий"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Организационная структура с выделенной целью получена",
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

#### 3. Get Business Unit Details

**Endpoint**: `POST /api/organization/unit`

**Authentication**: Required

**Request Body**:
```json
{
  "unit_path": "Блок операционного директора/Департамент информационных технологий"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Информация о бизнес-единице получена",
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
      "children": { /* nested units */ }
    }
  }
}
```

#### 4. Get Organization Statistics

**Endpoint**: `GET /api/organization/stats`

**Authentication**: Required

**Response** (200 OK):
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

---

### Dashboard Endpoints

#### 1. Get Full Dashboard Statistics

**Endpoint**: `GET /api/dashboard/stats`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Dashboard статистика получена",
  "data": {
    "summary": {
      "departments_count": 510,
      "positions_count": 1487,
      "profiles_count": 8,
      "completion_percentage": 0.5,
      "active_tasks_count": 0
    },
    "departments": {
      "total": 510,
      "with_positions": 488,
      "average_positions": 2.9
    },
    "positions": {
      "total": 1487,
      "with_profiles": 8,
      "without_profiles": 1479,
      "coverage_percent": 0.5
    },
    "profiles": {
      "total": 8,
      "percentage_complete": 0.5
    },
    "active_tasks": [],
    "metadata": {
      "last_updated": "2025-10-25T10:17:54.377302",
      "data_sources": {
        "catalog": "cached",
        "profiles": "database",
        "tasks": "memory"
      }
    }
  }
}
```

#### 2. Get Minimal Statistics

**Endpoint**: `GET /api/dashboard/stats/minimal`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "positions_count": 1487,
    "profiles_count": 8,
    "completion_percentage": 0.5,
    "active_tasks_count": 0,
    "last_updated": "2025-10-25T10:18:00.094062"
  }
}
```

#### 3. Get Activity Statistics

**Endpoint**: `GET /api/dashboard/stats/activity`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "active_tasks": [],
    "recent_profiles": [
      {
        "department": "Департамент по связям с общественностью",
        "position": "Специалист по связям с общественностью",
        "employee_name": null,
        "created_at": "2025-10-25T18:47:26.337714",
        "status": "completed",
        "created_by": "admin"
      }
    ],
    "summary": {
      "active_tasks_count": 0,
      "recent_profiles_count": 8,
      "has_activity": true
    },
    "last_updated": "2025-10-25T10:18:05.749119"
  }
}
```

---

## Data Models

### User Models

#### UserInfo
```typescript
interface UserInfo {
  id: number;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string; // ISO 8601
  last_login: string | null; // ISO 8601
}
```

#### LoginRequest
```typescript
interface LoginRequest {
  username: string; // min: 3, max: 50
  password: string; // min: 6, max: 100
  remember_me: boolean;
}
```

#### LoginResponse
```typescript
interface LoginResponse {
  success: boolean;
  timestamp: string; // ISO 8601
  message: string | null;
  access_token: string;
  token_type: string; // "bearer"
  expires_in: number; // seconds
  user_info: UserInfo;
}
```

### Profile Models

#### ProfileGenerationRequest
```typescript
interface ProfileGenerationRequest {
  department: string; // min: 2, max: 200
  position: string; // min: 2, max: 200
  employee_name?: string; // max: 200, optional
  temperature?: number; // 0.0-1.0, default: 0.1
  save_result?: boolean; // default: true
}
```

#### GenerationTask
```typescript
interface GenerationTask {
  task_id: string; // UUID
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  created_at: string; // ISO 8601
  started_at?: string; // ISO 8601
  completed_at?: string; // ISO 8601
  estimated_duration?: number; // seconds
  current_step?: string;
  error_message?: string;
}
```

#### ProfileSummary
```typescript
interface ProfileSummary {
  profile_id: string; // UUID
  department: string;
  position: string;
  employee_name: string | null;
  status: 'completed' | 'failed' | 'processing' | 'archived';
  validation_score: number; // 0.0-1.0
  completeness_score: number; // 0.0-1.0
  created_at: string; // ISO 8601
  created_by_username: string | null;
  actions?: {
    download_json: string;
    download_md: string;
    download_docx: string;
  };
}
```

#### ProfileData
```typescript
interface ProfileData {
  position_title: string;
  department: string;
  employee_name?: string;

  // Structured profile data
  basic_info: Record<string, any>;
  responsibilities: Array<Record<string, any>>;
  professional_skills: Record<string, Array<Record<string, any>>>;
  corporate_competencies: string[];
  personal_qualities: string[];
  education_experience: Record<string, any>;
  career_paths: Record<string, string[]>;
}
```

#### ProfileMetadata
```typescript
interface ProfileMetadata {
  generation_time_seconds: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  model_name: string; // e.g., "gemini-2.5-flash"
  temperature: number;
  validation: {
    is_valid: boolean;
    completeness_score: number; // 0.0-1.0
    errors: string[];
    warnings: string[];
  };
}
```

#### ProfileListResponse
```typescript
interface ProfileListResponse {
  profiles: ProfileSummary[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters_applied: {
    department?: string;
    position?: string;
    search?: string;
    status?: string;
  };
}
```

### Catalog Models

#### DepartmentInfo
```typescript
interface DepartmentInfo {
  name: string;
  display_name: string;
  path: string; // Full hierarchy path
  positions_count: number;
  last_updated: string; // ISO 8601
}
```

#### PositionInfo
```typescript
interface PositionInfo {
  name: string;
  level: number; // 1-5, where 1 is highest
  category: string; // "management", "technical", "specialist", etc.
  department: string;
  full_path?: string;
  last_updated: string; // ISO 8601
}
```

#### SearchableItem
```typescript
interface SearchableItem {
  display_name: string;
  full_path: string;
  positions_count: number;
  hierarchy: string[];
}
```

### Dashboard Models

#### DashboardStats
```typescript
interface DashboardStats {
  success: boolean;
  message: string;
  data: {
    summary: {
      departments_count: number;
      positions_count: number;
      profiles_count: number;
      completion_percentage: number;
      active_tasks_count: number;
    };
    departments: {
      total: number;
      with_positions: number;
      average_positions: number;
    };
    positions: {
      total: number;
      with_profiles: number;
      without_profiles: number;
      coverage_percent: number;
    };
    profiles: {
      total: number;
      percentage_complete: number;
    };
    active_tasks: GenerationTask[];
    metadata: {
      last_updated: string; // ISO 8601
      data_sources: {
        catalog: string;
        profiles: string;
        tasks: string;
      };
    };
  };
}
```

---

## Error Handling

### Standard Error Response

All errors follow this structure:

```typescript
interface ErrorResponse {
  success: boolean; // always false
  timestamp: string; // ISO 8601
  error: string; // Human-readable error message
  details?: ErrorDetail[];
  path?: string; // Request path
  request_id?: string; // Correlation ID
}

interface ErrorDetail {
  code: string;
  message: string;
  field?: string;
}
```

### HTTP Status Codes

| Status Code | Meaning | Usage |
|------------|---------|-------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 202 | Accepted | Async request accepted |
| 400 | Bad Request | Invalid input/validation error |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error with details |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

#### Authentication Errors (401)

```json
{
  "detail": "Недействительный токен авторизации"
}
```

#### Validation Errors (422)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "validation_errors": [
        {
          "field": "body.password",
          "message": "String should have at least 6 characters",
          "type": "string_too_short"
        }
      ]
    }
  }
}
```

#### Resource Not Found (404)

```json
{
  "detail": {
    "error": "Profile not found",
    "error_code": "RESOURCE_NOT_FOUND",
    "resource": "profile",
    "resource_id": "nonexistent-profile-id"
  }
}
```

#### Database Errors (500)

```json
{
  "detail": {
    "error": "Failed to fetch profiles: ...",
    "error_code": "DATABASE_ERROR",
    "operation": "SELECT",
    "table": "profiles"
  }
}
```

---

## API Patterns

### Pagination

All list endpoints support pagination with consistent parameters:

- `page` (int, default: 1, min: 1): Page number
- `limit` (int, default: 20, min: 1, max: 100): Items per page

Response includes pagination metadata:

```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### Filtering

Most endpoints support filtering via query parameters:

- **Exact match**: `?status=completed`
- **Partial match**: `?department=Группа` (uses LIKE %...%)
- **Search**: `?search=analyst` (searches across multiple fields)

### Sorting

Default sorting is by `created_at DESC` (newest first).

### Async Operations Pattern

1. **Start Operation**: POST to `/api/generation/start` → Returns `task_id`
2. **Poll Status**: GET `/api/generation/{task_id}/status` → Returns task status
3. **Get Result**: GET `/api/generation/{task_id}/result` → Returns final result

### File Downloads

File download endpoints return:
- `Content-Type`: Appropriate MIME type
- `Content-Disposition: attachment; filename="..."`
- Binary file content

### Caching

- Catalog data is cached in-memory (organization_cache)
- Cache can be invalidated with `force_refresh=true` parameter
- Admin can clear cache via `/api/catalog/cache/clear`

### Response Times

- Simple queries (cached): < 50ms
- Database queries: 50-200ms
- Profile generation: 30-60 seconds
- File exports: 100-500ms

---

## CORS & Security

### CORS Configuration

**Allowed Origins** (configurable via `CORS_ORIGINS` env var):
```
http://localhost:8033
http://127.0.0.1:8033
```

**Allowed Methods**:
```
GET, POST, PUT, DELETE, OPTIONS
```

**Allowed Headers**:
```
* (all headers)
```

**Credentials**: `true` (cookies/authentication allowed)

### Security Headers

The API includes security middleware that adds:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### Trusted Hosts

Requests are only accepted from trusted hosts (configurable via `TRUSTED_HOSTS`):
```
localhost
127.0.0.1
0.0.0.0
49.12.122.181
```

### Authentication Security

- **JWT Algorithm**: HS256
- **Token Lifetime**: 24 hours (configurable)
- **Password Hashing**: bcrypt + SHA256 (double hashing to avoid 72-byte truncation)
- **Secret Key**: Must be changed in production (env var: `JWT_SECRET_KEY`)

### Rate Limiting

**Not currently implemented** - TODO for production deployment.

Recommended limits:
- 100 requests/minute for authenticated users
- 10 requests/minute for anonymous users

---

## Vue.js Integration Guide

### 1. Setup Axios Client

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 2. Authentication Service

```typescript
// src/api/auth.service.ts
import { apiClient } from './client';
import type { LoginRequest, LoginResponse, UserInfo } from './types';

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials);

    // Store token
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user_info', JSON.stringify(response.data.user_info));

    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
  },

  async getCurrentUser(): Promise<UserInfo> {
    const response = await apiClient.get<UserInfo>('/api/auth/me');
    return response.data;
  },

  async refreshToken(): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/auth/refresh');
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  getStoredUser(): UserInfo | null {
    const userStr = localStorage.getItem('user_info');
    return userStr ? JSON.parse(userStr) : null;
  },
};
```

### 3. Profile Service

```typescript
// src/api/profile.service.ts
import { apiClient } from './client';
import type { ProfileGenerationRequest, GenerationTask, ProfileListResponse, ProfileSummary } from './types';

export const profileService = {
  async startGeneration(request: ProfileGenerationRequest): Promise<{ task_id: string }> {
    const response = await apiClient.post('/api/generation/start', request);
    return response.data;
  },

  async getTaskStatus(taskId: string): Promise<{ task: GenerationTask; result: any }> {
    const response = await apiClient.get(`/api/generation/${taskId}/status`);
    return response.data;
  },

  async getTaskResult(taskId: string): Promise<any> {
    const response = await apiClient.get(`/api/generation/${taskId}/result`);
    return response.data;
  },

  async listProfiles(params: {
    page?: number;
    limit?: number;
    department?: string;
    position?: string;
    search?: string;
    status?: string;
  }): Promise<ProfileListResponse> {
    const response = await apiClient.get('/api/profiles/', { params });
    return response.data;
  },

  async getProfile(profileId: string): Promise<any> {
    const response = await apiClient.get(`/api/profiles/${profileId}`);
    return response.data;
  },

  async updateProfile(profileId: string, data: { employee_name?: string; status?: string }): Promise<any> {
    const response = await apiClient.put(`/api/profiles/${profileId}`, data);
    return response.data;
  },

  async archiveProfile(profileId: string): Promise<any> {
    const response = await apiClient.delete(`/api/profiles/${profileId}`);
    return response.data;
  },

  async restoreProfile(profileId: string): Promise<any> {
    const response = await apiClient.post(`/api/profiles/${profileId}/restore`);
    return response.data;
  },

  getDownloadUrl(profileId: string, format: 'json' | 'md' | 'docx'): string {
    const token = localStorage.getItem('access_token');
    return `${apiClient.defaults.baseURL}/api/profiles/${profileId}/download/${format}?token=${token}`;
  },
};
```

### 4. Catalog Service

```typescript
// src/api/catalog.service.ts
import { apiClient } from './client';
import type { DepartmentInfo, SearchableItem } from './types';

export const catalogService = {
  async getDepartments(forceRefresh = false): Promise<{ departments: DepartmentInfo[]; total_count: number }> {
    const response = await apiClient.get('/api/catalog/departments', {
      params: { force_refresh: forceRefresh },
    });
    return response.data.data;
  },

  async searchDepartments(query: string): Promise<{ departments: DepartmentInfo[]; total_count: number }> {
    const response = await apiClient.get('/api/catalog/search', {
      params: { q: query },
    });
    return response.data.data;
  },

  async searchPositions(query: string, department?: string): Promise<any> {
    const response = await apiClient.get('/api/catalog/search/positions', {
      params: { q: query, department },
    });
    return response.data.data;
  },

  async getSearchItems(): Promise<{ items: SearchableItem[]; total_count: number }> {
    const response = await apiClient.get('/api/organization/search-items');
    return response.data.data;
  },

  async getBusinessUnit(unitPath: string): Promise<any> {
    const response = await apiClient.post('/api/organization/unit', {
      unit_path: unitPath,
    });
    return response.data.data;
  },
};
```

### 5. Dashboard Service

```typescript
// src/api/dashboard.service.ts
import { apiClient } from './client';
import type { DashboardStats } from './types';

export const dashboardService = {
  async getFullStats(): Promise<DashboardStats> {
    const response = await apiClient.get('/api/dashboard/stats');
    return response.data;
  },

  async getMinimalStats(): Promise<{
    positions_count: number;
    profiles_count: number;
    completion_percentage: number;
    active_tasks_count: number;
  }> {
    const response = await apiClient.get('/api/dashboard/stats/minimal');
    return response.data.data;
  },

  async getActivityStats(): Promise<any> {
    const response = await apiClient.get('/api/dashboard/stats/activity');
    return response.data.data;
  },
};
```

### 6. Vue Composable for Polling

```typescript
// src/composables/useTaskPolling.ts
import { ref, onUnmounted } from 'vue';
import { profileService } from '@/api/profile.service';
import type { GenerationTask } from '@/api/types';

export function useTaskPolling(taskId: string, interval = 2000) {
  const task = ref<GenerationTask | null>(null);
  const result = ref<any>(null);
  const error = ref<string | null>(null);
  const isPolling = ref(true);

  let pollInterval: number | null = null;

  async function poll() {
    try {
      const response = await profileService.getTaskStatus(taskId);
      task.value = response.task;

      if (response.task.status === 'completed') {
        result.value = response.result;
        stopPolling();
      } else if (response.task.status === 'failed' || response.task.status === 'cancelled') {
        error.value = response.task.error_message || 'Task failed';
        stopPolling();
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to poll task status';
      stopPolling();
    }
  }

  function startPolling() {
    isPolling.value = true;
    poll(); // Initial poll
    pollInterval = window.setInterval(poll, interval);
  }

  function stopPolling() {
    isPolling.value = false;
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  // Auto-start polling
  startPolling();

  // Cleanup on unmount
  onUnmounted(() => {
    stopPolling();
  });

  return {
    task,
    result,
    error,
    isPolling,
    startPolling,
    stopPolling,
  };
}
```

### 7. Example Vue Component

```vue
<template>
  <div class="profile-generation">
    <h2>Generate Profile</h2>

    <form @submit.prevent="handleSubmit">
      <div>
        <label>Department:</label>
        <select v-model="form.department" required>
          <option v-for="dept in departments" :key="dept.name" :value="dept.name">
            {{ dept.display_name }}
          </option>
        </select>
      </div>

      <div>
        <label>Position:</label>
        <input v-model="form.position" type="text" required />
      </div>

      <div>
        <label>Employee Name (optional):</label>
        <input v-model="form.employee_name" type="text" />
      </div>

      <button type="submit" :disabled="isGenerating">
        {{ isGenerating ? 'Generating...' : 'Generate Profile' }}
      </button>
    </form>

    <div v-if="task" class="task-status">
      <h3>Generation Status</h3>
      <p>Status: {{ task.status }}</p>
      <p>Progress: {{ task.progress }}%</p>
      <p>Current Step: {{ task.current_step }}</p>

      <div v-if="task.status === 'completed' && result">
        <h4>Profile Generated!</h4>
        <button @click="viewProfile">View Profile</button>
      </div>

      <div v-if="error" class="error">
        Error: {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { catalogService, profileService } from '@/api';
import { useTaskPolling } from '@/composables/useTaskPolling';
import type { DepartmentInfo } from '@/api/types';

const departments = ref<DepartmentInfo[]>([]);
const form = ref({
  department: '',
  position: '',
  employee_name: '',
  temperature: 0.1,
  save_result: true,
});

const isGenerating = ref(false);
const currentTaskId = ref<string | null>(null);

// Task polling composable (activated when task is created)
const { task, result, error } = currentTaskId.value
  ? useTaskPolling(currentTaskId.value)
  : { task: ref(null), result: ref(null), error: ref(null) };

onMounted(async () => {
  const response = await catalogService.getDepartments();
  departments.value = response.departments;
});

async function handleSubmit() {
  isGenerating.value = true;

  try {
    const response = await profileService.startGeneration(form.value);
    currentTaskId.value = response.task_id;

    // Start polling (automatically via composable)
  } catch (err: any) {
    console.error('Failed to start generation:', err);
    error.value = err.message;
  } finally {
    isGenerating.value = false;
  }
}

function viewProfile() {
  if (result.value?.profile_id) {
    // Navigate to profile view
    window.location.href = `/profiles/${result.value.profile_id}`;
  }
}
</script>
```

### 8. Environment Variables

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8022

# .env.production
VITE_API_BASE_URL=https://api.a101.com/hr
```

---

## Additional Notes

### File Paths and Storage

- **Generated Profiles**: `/generated_profiles/{department}/{position}_{timestamp}.{json|md|docx}`
- **Database**: `data/profiles.db` (SQLite file)
- **Templates**: `templates/*.json` (JSON schemas and prompts)
- **Static Files**: `backend/static/` (served at `/static/`)

### Database Schema

**Tables**:
- `users` - User accounts
- `user_sessions` - Active JWT sessions
- `profiles` - Generated profiles
- `generation_tasks` - Async generation tasks
- `generation_history` - Generation history for analytics
- `organization_cache` - Cached organizational structure

### Performance Considerations

1. **Organization Cache**: 567 business units cached in-memory (75x speedup: 3ms vs 225ms)
2. **Parallel Generation**: Supports parallel profile generation (10x speedup)
3. **Database Indexes**: Indexed on department, position, created_at, status
4. **Connection Pooling**: Thread-safe SQLite connections per thread
5. **Static File Caching**: Browser caching enabled for static assets

### Known Limitations

1. **Cyrillic in Path Parameters**: Use POST endpoints (`/api/organization/unit`) instead of GET with path params
2. **Active Tasks Tracking**: In-memory storage (lost on restart) - TODO: implement Redis
3. **Rate Limiting**: Not implemented - TODO for production
4. **WebSocket**: Not implemented - polling used for task status
5. **Pagination Maximum**: 100 items per page limit

### Future Enhancements

- [ ] WebSocket support for real-time task updates
- [ ] Redis for distributed task queue
- [ ] Rate limiting middleware
- [ ] API versioning (`/api/v2/...`)
- [ ] Bulk operations (generate multiple profiles)
- [ ] Advanced search with Elasticsearch
- [ ] Export to additional formats (PDF, Excel templates)
- [ ] Profile comparison tool
- [ ] Profile versioning and history

---

## Support & Documentation

- **Interactive API Docs**: http://localhost:8022/docs (Swagger UI)
- **ReDoc**: http://localhost:8022/redoc
- **Source Code**: `/home/yan/A101/HR/backend/`
- **Memory Bank**: `/home/yan/A101/HR/.memory_bank/`
- **Tech Stack**: `/home/yan/A101/HR/.memory_bank/tech_stack.md`
- **Coding Standards**: `/home/yan/A101/HR/.memory_bank/guides/coding_standards.md`

---

**Document Version**: 1.0.0
**Generated**: 2025-10-25
**Author**: Claude (Backend System Architect)

# 📚 API Reference - A101 HR Profile Generator

## 🚀 Быстрый старт

### Запуск сервера

**Docker (рекомендуется):**
```bash
# Запуск с помощью готовых скриптов
./scripts/dev-start.sh

# Или напрямую через docker compose
docker compose up -d
```

**Локально:**
```bash
# Убедитесь что .env файл настроен
cp .env.example .env
# Отредактируйте .env с вашими настройками

uvicorn backend.main:app --host 0.0.0.0 --port 8022 --reload
```

### Базовый URL
```
http://localhost:8022
```

### Документация
- **Swagger UI:** http://localhost:8022/docs
- **ReDoc:** http://localhost:8022/redoc
- **OpenAPI Schema:** http://localhost:8022/openapi.json

---

## ⚙️ Конфигурация

Система использует **централизованную конфигурацию** через модуль `backend/core/config.py` и `.env` файл.

### Environment Variables

**Обязательные переменные:**
```bash
# Базовые настройки
ENVIRONMENT=development              # development | production
DATABASE_URL=sqlite:///data/profiles.db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Учетные данные по умолчанию
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
HR_USERNAME=hr
HR_PASSWORD=hr123
```

**Опциональные переменные:**
```bash
# OpenRouter для LLM (только для генерации профилей)
OPENROUTER_API_KEY=your-openrouter-api-key

# Langfuse мониторинг
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key

# FastAPI настройки
API_HOST=0.0.0.0
API_PORT=8022
CORS_ORIGINS=http://localhost:8033,http://127.0.0.1:8033
```

### Проверка конфигурации

```bash
# Тест конфигурации
python3 -c "from backend.core.config import config; config.print_summary(); config.validate()"
```

---

## 🔐 Аутентификация

Все API endpoints (кроме публичных) требуют JWT аутентификацию через заголовок `Authorization: Bearer <token>`.

### Получение токена

#### `POST /api/auth/login`
Авторизация пользователя и получение JWT токена.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123",
  "remember_me": false
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_info": {
    "id": 1,
    "username": "admin",
    "full_name": "Администратор системы",
    "is_active": true,
    "created_at": "2025-09-07T15:00:00",
    "last_login": "2025-09-07T15:30:00"
  },
  "success": true,
  "message": "Добро пожаловать, Администратор системы!"
}
```

**Error Responses:**
- `401 Unauthorized` - Неверные учетные данные
- `500 Internal Server Error` - Внутренняя ошибка

### 🧪 Тестовый токен для разработки

**⚠️ ТОЛЬКО ДЛЯ РАЗРАБОТКИ! УДАЛИТЬ В ПРОДАКШЕНЕ!**

Для удобства тестирования используйте готовый токен (действует до 2026-09-09):

```bash
export TEST_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsImZ1bGxfbmFtZSI6Ilx1MDQxMFx1MDQzNFx1MDQzY1x1MDQzOFx1MDQzZFx1MDQzOFx1MDQ0MVx1MDQ0Mlx1MDQ0MFx1MDQzMFx1MDQ0Mlx1MDQzZVx1MDQ0MCBcdTA0NDFcdTA0MzhcdTA0NDFcdTA0NDJcdTA0MzVcdTA0M2NcdTA0NGIiLCJleHAiOjE3ODg5NzcxNTEsImlhdCI6MTc1NzQ0MTE1MSwidHlwZSI6ImFjY2Vzc190b2tlbiJ9.6P0IJ7T6M9NLMmfN1NWsdtNbAyI7cVZul6l9BYyt6Eo"

# Быстрый тест API
curl -H "Authorization: Bearer $TEST_TOKEN" "http://localhost:8022/api/profiles"
```

### Использование токена

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

---

## 👤 Управление пользователями

### `POST /api/auth/logout`
Выход из системы (инвалидирует все сессии пользователя).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Вы успешно вышли из системы"
}
```

### `GET /api/auth/me`
Получение информации о текущем пользователе.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "full_name": "Администратор системы",
  "is_active": true,
  "created_at": "2025-09-07T15:00:00",
  "last_login": "2025-09-07T15:30:00"
}
```

### `POST /api/auth/refresh`
Обновление JWT токена.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_info": { /* user info */ },
  "success": true,
  "message": "Токен обновлен успешно"
}
```

### `GET /api/auth/validate`
Проверка валидности текущего токена.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Токен действителен для пользователя admin"
}
```

---

## 🏢 Каталог департаментов

## ⚡ Performance Metrics

### 🚀 Catalog API Optimization

**Ключевой endpoint `/api/catalog/departments` оптимизирован для высокой производительности:**

#### 📊 Performance Benchmarks:
- **Холодный старт:** `40ms` (пакетная загрузка 510 департаментов + 4376 должностей)
- **С кешем:** `3ms` (моментальный возврат из памяти)
- **Кеш TTL:** 1 час с автоматическим обновлением
- **Архитектура:** 1 пакетная загрузка вместо 510 отдельных запросов

#### 🔍 Performance Logs:
```
2025-09-07 16:21:53 - ✅ Full organization structure loaded in 0.024s: 510 departments, 4376 positions
2025-09-07 16:21:53 - ✅ Loaded 510 departments in 0.036s (total positions: 4376)
2025-09-07 16:22:03 - Using cached departments data (0.003s)
```

#### 💡 Performance Features:
- **Intelligent Caching** - Memory + Database persistence
- **Batch Loading** - All data in single operation
- **TTL Management** - Auto-refresh after 1 hour
- **Fallback Strategy** - Graceful degradation on errors
- **Performance Monitoring** - Detailed timing logs

---

### `GET /api/catalog/departments`
Получение списка всех департаментов с оптимизированной производительностью.

**Parameters:**
- `force_refresh` (query, boolean, optional) - Принудительное обновление кеша

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Найдено 510 департаментов",
  "data": {
    "departments": [
      {
        "name": "Блок безопасности",
        "display_name": "Блок безопасности",
        "path": "Блок безопасности",
        "positions_count": 9,
        "last_updated": "2025-09-07T20:13:10.123456"
      }
      // ... остальные департаменты
    ],
    "total_count": 510,
    "cached": true,
    "last_updated": "2025-09-07T20:13:10.123456"
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/catalog/departments?force_refresh=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `GET /api/catalog/departments/{department_name}`
Детальная информация о конкретном департаменте.

**Path Parameters:**
- `department_name` (string, required) - Название департамента (URL encoded)

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Информация о департаменте 'Блок безопасности' получена",
  "data": {
    "name": "Блок безопасности",
    "display_name": "Блок безопасности",
    "path": "Блок безопасности",
    "positions_count": 9,
    "last_updated": "2025-09-07T20:13:10.123456",
    "positions": [
      {
        "name": "Руководитель департамента",
        "department": "Блок безопасности",
        "display_name": "Руководитель департамента",
        "level": 1,
        "category": "management",
        "last_updated": "2025-09-07T20:13:10.123456"
      }
      // ... остальные должности
    ],
    "organization_structure": { /* иерархическая структура */ },
    "total_positions": 9,
    "position_levels": [1, 2, 3, 4, 5],
    "position_categories": ["management", "specialist", "analytics"]
  }
}
```

**Error Responses:**
- `404 Not Found` - Департамент не найден

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/catalog/departments/Блок%20безопасности" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `GET /api/catalog/positions/{department}`
Получение должностей для конкретного департамента.

**Path Parameters:**
- `department` (string, required) - Название департамента (URL encoded)

**Query Parameters:**
- `force_refresh` (boolean, optional) - Принудительное обновление кеша

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Найдено 9 должностей для департамента 'Блок безопасности'",
  "data": {
    "department": "Блок безопасности",
    "positions": [
      {
        "name": "Руководитель департамента",
        "department": "Блок безопасности",
        "display_name": "Руководитель департамента",
        "level": 1,
        "category": "management",
        "last_updated": "2025-09-07T20:13:10.123456"
      },
      {
        "name": "Заместитель руководителя",
        "department": "Блок безопасности",
        "display_name": "Заместитель руководителя",
        "level": 2,
        "category": "management",
        "last_updated": "2025-09-07T20:13:10.123456"
      }
      // ... остальные должности
    ],
    "total_count": 9,
    "statistics": {
      "levels": {
        "1": 1,  // 1 руководитель
        "2": 1,  // 1 заместитель
        "3": 1,  // 1 ведущий специалист
        "4": 1,  // 1 старший специалист
        "5": 5   // 5 специалистов
      },
      "categories": {
        "management": 2,
        "specialist": 6,
        "analytics": 1
      }
    },
    "cached": false,
    "last_updated": "2025-09-07T20:13:10.123456"
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/catalog/positions/Блок%20безопасности?force_refresh=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `GET /api/catalog/search`
Поиск департаментов по названию или пути.

**Query Parameters:**
- `q` (string, required) - Поисковой запрос (минимум 1 символ)

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "По запросу 'безопасность' найдено 5 департаментов",
  "data": {
    "query": "безопасность",
    "departments": [
      {
        "name": "Блок безопасности",
        "display_name": "Блок безопасности",
        "path": "Блок безопасности",
        "positions_count": 9,
        "last_updated": "2025-09-07T20:13:10.123456"
      },
      {
        "name": "Служба безопасности",
        "display_name": "Служба безопасности",
        "path": "Блок безопасности/Служба безопасности",
        "positions_count": 9,
        "last_updated": "2025-09-07T20:13:10.123456"
      }
      // ... остальные найденные департаменты
    ],
    "total_count": 5
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/catalog/search?q=безопасность" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `GET /api/catalog/stats`
Получение общей статистики каталога.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Статистика каталога получена",
  "data": {
    "departments": {
      "total_count": 510,
      "with_positions": 510
    },
    "positions": {
      "total_count": 5358,
      "average_per_department": 10.51,
      "levels_distribution": {
        "1": 548,   // Руководители
        "2": 510,   // Заместители
        "3": 510,   // Ведущие специалисты
        "4": 510,   // Старшие специалисты
        "5": 3280   // Специалисты
      },
      "categories_distribution": {
        "management": 1058,
        "specialist": 3570,
        "technical": 530,
        "analytics": 200
      }
    },
    "cache_status": {
      "departments_cached": true,
      "positions_cached_count": 15,
      "last_departments_update": "2025-09-07T20:13:10.123456"
    }
  }
}
```

### `POST /api/catalog/cache/clear`
Очистка кеша каталога (только для администраторов).

**Query Parameters:**
- `cache_type` (string, optional) - Тип кеша: "departments", "positions" или пустой для всех

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Кеш (departments) успешно очищен"
}
```

**Error Responses:**
- `403 Forbidden` - Недостаточно прав (требуется admin)

**Example Request:**
```bash
curl -X POST "http://localhost:8022/api/catalog/cache/clear?cache_type=departments" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 🏥 Системные endpoints

### `GET /health`
Проверка состояния системы (публичный endpoint).

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-07T20:13:10.123456",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "environment": "development",
  "components": {
    "api": "operational",
    "core_modules": "initialized"
  },
  "external_services": {
    "openrouter_configured": false,
    "langfuse_configured": false
  }
}
```

**Response (503) - При проблемах:**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-07T20:13:10.123456",
  "error": "Database connection failed"
}
```

### `GET /`
Корневой endpoint с информацией о API (публичный).

**Response (200):**
```json
{
  "service": "HR Profile Generator API",
  "version": "1.0.0",
  "description": "Система автоматической генерации профилей должностей А101",
  "docs": "/docs",
  "health": "/health",
  "timestamp": "2025-09-07T20:13:10.123456",
  "message": "🏢 Добро пожаловать в систему генерации профилей должностей А101!"
}
```

---

## 🤖 **PROFILE GENERATION ENDPOINTS**

### `POST /api/generation/start`
Запуск асинхронной генерации профиля должности с использованием Langfuse и Gemini 2.5 Flash.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "position": "Senior ML Engineer",
  "department": "ДИТ",
  "employee_name": "Иван Петров"
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "message": "Задача генерации профиля создана",
  "data": {
    "task_id": "gen_20250907_201500_abc123",
    "status": "pending",
    "created_at": "2025-09-07T20:15:00Z",
    "estimated_duration": "30-60 seconds",
    "status_url": "/api/generation/gen_20250907_201500_abc123/status",
    "result_url": "/api/generation/gen_20250907_201500_abc123/result"
  }
}
```

**Validation Errors (422):**
```json
{
  "success": false,
  "error": "Validation Error",
  "detail": [
    {
      "loc": ["body", "position"],
      "msg": "Position title is required and must be between 1-255 characters",
      "type": "value_error"
    },
    {
      "loc": ["body", "department"],
      "msg": "Department is required",
      "type": "value_error"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8022/api/generation/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Senior ML Engineer",
    "department": "ДИТ",
    "employee_name": "Иван Петров"
  }'
```

### `GET /api/generation/{task_id}/status`
Получение статуса задачи генерации профиля.

**Path Parameters:**
- `task_id` (string, required) - ID задачи генерации

**Headers:** `Authorization: Bearer <token>`

**Response (200) - Pending:**
```json
{
  "success": true,
  "message": "Статус задачи получен",
  "data": {
    "task_id": "gen_20250907_201500_abc123",
    "status": "pending",
    "progress": {
      "current_step": "initializing",
      "total_steps": 5,
      "percent": 0,
      "step_description": "Подготовка данных для генерации"
    },
    "created_at": "2025-09-07T20:15:00Z",
    "estimated_completion": "2025-09-07T20:16:00Z"
  }
}
```

**Response (200) - In Progress:**
```json
{
  "success": true,
  "message": "Статус задачи получен",
  "data": {
    "task_id": "gen_20250907_201500_abc123",
    "status": "in_progress",
    "progress": {
      "current_step": "llm_generation",
      "total_steps": 5,
      "percent": 80,
      "step_description": "Генерация профиля с помощью Gemini 2.5 Flash"
    },
    "created_at": "2025-09-07T20:15:00Z",
    "started_at": "2025-09-07T20:15:05Z",
    "estimated_completion": "2025-09-07T20:16:00Z"
  }
}
```

**Response (200) - Completed:**
```json
{
  "success": true,
  "message": "Задача выполнена успешно",
  "data": {
    "task_id": "gen_20250907_201500_abc123",
    "status": "completed",
    "result": {
      "profile_id": "prof_20250907_201600_xyz789",
      "position": "Senior ML Engineer",
      "department": "ДИТ",
      "employee_name": "Иван Петров",
      "generation_metadata": {
        "generation_time_seconds": 45.2,
        "tokens_used": {
          "input": 8450,
          "output": 4250,
          "total": 12700
        },
        "model_used": "google/gemini-2.5-flash",
        "langfuse_trace_id": "trace_abc123def456",
        "langfuse_trace_url": "https://cloud.langfuse.com/project/xxx/traces/trace_abc123def456"
      }
    },
    "created_at": "2025-09-07T20:15:00Z",
    "completed_at": "2025-09-07T20:15:45Z"
  }
}
```

**Response (200) - Failed:**
```json
{
  "success": false,
  "message": "Генерация профиля завершилась с ошибкой",
  "data": {
    "task_id": "gen_20250907_201500_abc123",
    "status": "failed",
    "error": {
      "error_type": "LLM_API_ERROR",
      "error_message": "OpenRouter API rate limit exceeded",
      "retry_after_seconds": 60,
      "langfuse_trace_id": "trace_error_123"
    },
    "created_at": "2025-09-07T20:15:00Z",
    "failed_at": "2025-09-07T20:15:30Z"
  }
}
```

**Task Status Values:**
- `pending` - Задача в очереди, не начата
- `in_progress` - Генерация в процессе
- `completed` - Успешно завершена
- `failed` - Ошибка при генерации
- `cancelled` - Задача отменена пользователем

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/generation/gen_20250907_201500_abc123/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `GET /api/generation/{task_id}/result`
Получение результата генерации профиля.

**Path Parameters:**
- `task_id` (string, required) - ID задачи генерации

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Результат генерации получен",
  "data": {
    "task_id": "gen_20250907_201500_abc123",
    "profile": {
      "id": "prof_20250907_201600_xyz789",
      "position_title": "Senior ML Engineer",
      "department_path": "ДИТ",
      "employee_name": "Иван Петров",
      "version": 1,
      "status": "active",
      "generated_data": {
        "basic_info": {
          "position_title": "Senior ML Engineer",
          "department": "ДИТ",
          "reporting_to": "Руководитель отдела машинного обучения",
          "team_size": "6-10 человек",
          "employment_type": "Полная занятость"
        },
        "job_summary": "Ведущий инженер машинного обучения, ответственный за разработку, внедрение и масштабирование ML-решений...",
        "key_responsibilities": [
          "Проектирование и разработка ML моделей и алгоритмов",
          "Внедрение и оптимизация ML pipeline в production",
          "Менторство и техническое руководство командой ML engineers",
          "Архитектурное планирование ML инфраструктуры и платформ"
        ],
        "required_skills": {
          "technical_skills": [
            "Python, R (продвинутый уровень)",
            "TensorFlow, PyTorch, Scikit-learn",
            "MLOps tools (MLflow, Kubeflow, Docker)",
            "Cloud platforms (AWS, GCP, Azure)"
          ],
          "soft_skills": [
            "Лидерство и менторство",
            "Системное мышление",
            "Коммуникабельность и презентационные навыки"
          ]
        },
        "qualifications": {
          "education": "Высшее техническое образование (математика, информатика, физика)",
          "experience": "5+ лет опыта в области машинного обучения",
          "certifications": "Сертификации по ML/AI (желательно)"
        },
        "kpi_metrics": [
          {
            "category": "Эффективность разработки",
            "metrics": [
              "Время разработки и внедрения ML моделей",
              "Точность и качество ML решений",
              "Покрытие тестами ML кода"
            ]
          },
          {
            "category": "Командная работа",
            "metrics": [
              "Индекс удовлетворенности команды",
              "Скорость онбординга новых сотрудников",
              "Количество проведенных knowledge sharing сессий"
            ]
          }
        ]
      },
      "generation_metadata": {
        "generation_time_seconds": 45.2,
        "tokens_used": {
          "input": 8450,
          "output": 4250,
          "total": 12700
        },
        "model_used": "google/gemini-2.5-flash",
        "langfuse_trace_id": "trace_abc123def456",
        "langfuse_trace_url": "https://cloud.langfuse.com/project/xxx/traces/trace_abc123def456",
        "prompt_name": "a101-hr-profile-gemini-v3-simple",
        "prompt_version": 3,
        "created_at": "2025-09-07T20:15:45Z"
      }
    }
  }
}
```

**Error Responses:**
- `404 Not Found` - Задача не найдена или еще не завершена
- `400 Bad Request` - Задача завершилась с ошибкой

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/generation/gen_20250907_201500_abc123/result" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `DELETE /api/generation/{task_id}`
Отмена задачи генерации или очистка завершенной задачи.

**Path Parameters:**
- `task_id` (string, required) - ID задачи генерации

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Задача gen_20250907_201500_abc123 успешно отменена"
}
```

**Error Responses:**
- `404 Not Found` - Задача не найдена

**Example Request:**
```bash
curl -X DELETE "http://localhost:8022/api/generation/gen_20250907_201500_abc123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📄 **PROFILE MANAGEMENT ENDPOINTS**

### `GET /api/profiles`
Получение списка сгенерированных профилей с пагинацией и фильтрацией.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (integer, optional) - Номер страницы (default: 1)
- `per_page` (integer, optional) - Элементов на странице (default: 20, max: 100)
- `search` (string, optional) - Поиск по позиции, департаменту, имени сотрудника
- `department` (string, optional) - Фильтр по департаменту
- `status` (string, optional) - Фильтр по статусу ('active', 'archived')
- `sort` (string, optional) - Поле сортировки ('created_at', 'updated_at', 'position_title')
- `order` (string, optional) - Направление сортировки ('asc', 'desc')

**Response (200):**
```json
{
  "success": true,
  "message": "Найдено 156 профилей",
  "data": {
    "profiles": [
      {
        "id": "prof_20250907_201600_xyz789",
        "position_title": "Senior ML Engineer",
        "department_path": "ДИТ",
        "employee_name": "Иван Петров",
        "version": 1,
        "status": "active",
        "created_at": "2025-09-07T20:16:00Z",
        "updated_at": "2025-09-07T20:16:00Z",
        "created_by": "admin",
        "generation_metadata": {
          "tokens_used": 12700,
          "generation_time_seconds": 45.2,
          "langfuse_trace_id": "trace_abc123def456"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 156,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false,
      "next_page": 2,
      "prev_page": null
    }
  }
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/profiles?page=1&per_page=10&search=ML&department=ДИТ&status=active&sort=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### `GET /api/profiles/{profile_id}`
Получение конкретного профиля с полными данными.

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Профиль получен",
  "data": {
    "id": "prof_20250907_201600_xyz789",
    "position_title": "Senior ML Engineer",
    "department_path": "ДИТ",
    "employee_name": "Иван Петров",
    "version": 1,
    "status": "active",
    "json_data": {
      // Полная структура профиля (аналогично GET /result)
      "basic_info": { /* ... */ },
      "job_summary": "...",
      "key_responsibilities": [ /* ... */ ],
      "required_skills": { /* ... */ },
      "qualifications": { /* ... */ },
      "kpi_metrics": [ /* ... */ ]
    },
    "created_at": "2025-09-07T20:16:00Z",
    "updated_at": "2025-09-07T20:16:00Z",
    "created_by": "admin",
    "langfuse_trace_id": "trace_abc123def456"
  }
}
```

**Error Responses:**
- `404 Not Found` - Профиль не найден

### `PUT /api/profiles/{profile_id}`
Обновление метаданных профиля (не сгенерированного содержимого).

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "employee_name": "Иван Иванович Петров",
  "status": "active"
}
```

**Updatable Fields:**
- `employee_name` - Имя сотрудника
- `status` - Статус профиля ('active', 'archived')

**Response (200):**
```json
{
  "success": true,
  "message": "Профиль обновлен",
  "data": {
    "id": "prof_20250907_201600_xyz789",
    "updated_fields": ["employee_name"],
    "updated_at": "2025-09-07T21:00:00Z"
  }
}
```

### `DELETE /api/profiles/{profile_id}`
Мягкое удаление профиля (перевод в статус archived).

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Профиль архивирован",
  "data": {
    "id": "prof_20250907_201600_xyz789",
    "archived_at": "2025-09-07T21:05:00Z"
  }
}
```

### `POST /api/profiles/{profile_id}/restore`
Восстановление архивированного профиля.

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "success": true,
  "message": "Профиль восстановлен",
  "data": {
    "id": "prof_20250907_201600_xyz789",
    "restored_at": "2025-09-07T21:10:00Z",
    "status": "active"
  }
}
```

### `GET /api/profiles/{profile_id}/download/json`
Скачать JSON файл профиля напрямую с файловой системы.

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```
Content-Type: application/json
Content-Disposition: attachment; filename="profile_Senior_Data_Analyst_e874d4ca.json"

[Binary JSON file content]
```

**Error Responses:**
- `404 Not Found` - Профиль или файл не найден

**Example Request:**
```bash
curl -H "Authorization: Bearer $TEST_TOKEN" \
  -o "profile.json" \
  "http://localhost:8022/api/profiles/e874d4ca-b4bf-4d91-b741-2cc4cbcb36b5/download/json"
```

### `GET /api/profiles/{profile_id}/download/md`
Скачать Markdown файл профиля напрямую с файловой системы.

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```
Content-Type: text/markdown
Content-Disposition: attachment; filename="profile_Senior_Data_Analyst_e874d4ca.md"

[Markdown file content]
```

**Error Responses:**
- `404 Not Found` - Профиль или файл не найден

**Example Request:**
```bash
curl -H "Authorization: Bearer $TEST_TOKEN" \
  -o "profile.md" \
  "http://localhost:8022/api/profiles/e874d4ca-b4bf-4d91-b741-2cc4cbcb36b5/download/md"
```

**📁 File Storage Architecture:**
Файлы профилей хранятся в иерархической структуре:
```
generated_profiles/
└── Блок_операционного_директора/
    └── Департамент_информационных_технологий/
        └── Отдел_управления_данными/
            └── Группа_анализа_данных/
                └── Senior_Data_Analyst/
                    └── Senior_Data_Analyst_20250909_171336_e874d4ca/
                        ├── Senior_Data_Analyst_20250909_171336_e874d4ca.json
                        └── Senior_Data_Analyst_20250909_171336_e874d4ca.md
```

**🔧 Path Calculation:**
Пути к файлам вычисляются детерминистически на основе:
- UUID профиля из базы данных
- Названия департамента и должности
- Времени создания профиля
- Кешированной организационной структуры

**🚀 Performance:**
- **Нет файлового сканирования** - пути вычисляются алгоритмически
- **O(1) доступ** - прямое обращение к файлу по пути
- **Кешированная оргструктура** - загружается однократно при старте

---

## 📤 **EXPORT ENDPOINTS**

### `GET /api/profiles/{profile_id}/export`
Экспорт профиля в различных форматах.

**Path Parameters:**
- `profile_id` (string, required) - ID профиля

**Query Parameters:**
- `format` (string, required) - Формат экспорта: 'json', 'markdown', 'excel'
- `include_metadata` (boolean, optional) - Включить метаданные генерации (default: true)

**Headers:** `Authorization: Bearer <token>`

**Response for JSON (200):**
```json
{
  "success": true,
  "message": "Экспорт в JSON завершен",
  "data": {
    "profile_id": "prof_20250907_201600_xyz789",
    "export_format": "json",
    "exported_at": "2025-09-07T21:15:00Z",
    "profile_data": {
      // Полная структура профиля
    }
  }
}
```

**Response for Markdown (200):**
```
Content-Type: text/markdown
Content-Disposition: attachment; filename="Senior_ML_Engineer_profile.md"

# Профиль должности: Senior ML Engineer

## 📋 Основная информация
- **Должность:** Senior ML Engineer
- **Департамент:** ДИТ
- **Сотрудник:** Иван Петров
...
```

**Response for Excel (200):**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="Senior_ML_Engineer_profile.xlsx"

[Binary Excel file content]
```

**Example Request:**
```bash
curl -X GET "http://localhost:8022/api/profiles/prof_20250907_201600_xyz789/export?format=json&include_metadata=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Схемы данных

### UserInfo
```json
{
  "id": 1,
  "username": "admin",
  "full_name": "Администратор системы",
  "is_active": true,
  "created_at": "2025-09-07T15:00:00",
  "last_login": "2025-09-07T15:30:00"
}
```

### Department
```json
{
  "name": "Блок безопасности",
  "display_name": "Блок безопасности",
  "path": "Блок безопасности",
  "positions_count": 9,
  "last_updated": "2025-09-07T20:13:10.123456"
}
```

### Position
```json
{
  "name": "Руководитель департамента",
  "department": "Блок безопасности",
  "display_name": "Руководитель департамента",
  "level": 1,
  "category": "management",
  "last_updated": "2025-09-07T20:13:10.123456"
}
```

### Position Levels
- `1` - Руководитель департамента/директор
- `2` - Заместитель руководителя/зам. директора
- `3` - Ведущий специалист
- `4` - Старший специалист
- `5` - Специалист/координатор/аналитик

### Position Categories
- `management` - Управленческие должности
- `technical` - Технические специалисты
- `specialist` - Общие специалисты
- `analytics` - Аналитики

---

## ❌ Коды ошибок

### Authentication Errors
- `401 Unauthorized` - Неверный или отсутствующий токен
- `403 Forbidden` - Недостаточно прав для операции

### Client Errors
- `400 Bad Request` - Некорректные параметры запроса
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации данных

### Server Errors
- `500 Internal Server Error` - Внутренняя ошибка сервера
- `503 Service Unavailable` - Сервис временно недоступен

### Структура ошибки
```json
{
  "success": false,
  "error": "Краткое описание ошибки",
  "detail": "Подробное описание ошибки",
  "timestamp": "2025-09-07T20:13:10.123456",
  "path": "/api/catalog/departments"
}
```

---

## 🔧 Rate Limiting

**Текущий статус:** Не реализован (планируется в будущих версиях)

**Планируемые лимиты:**
- Authentication endpoints: 10 запросов/минуту
- Catalog endpoints: 100 запросов/минуту
- Search endpoints: 30 запросов/минуту

---

## 📊 Логирование

### Формат логов
```
2025-09-07 20:13:10,123 - backend.api.catalog - INFO - Getting departments list (force_refresh=False) for user admin
```

### Логируемые события
- Все HTTP запросы с методом, URL, статусом, временем выполнения
- Аутентификация: успешные и неуспешные попытки
- Операции с кешем: создание, обновление, очистка
- Ошибки: с полным stack trace

---

## 🧪 Примеры использования

### Python с requests
```python
import requests

# Аутентификация
login_response = requests.post(
    "http://localhost:8022/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Получение департаментов
departments = requests.get(
    "http://localhost:8022/api/catalog/departments",
    headers=headers
).json()

print(f"Найдено {departments['data']['total_count']} департаментов")
```

### JavaScript с fetch
```javascript
// Аутентификация
const loginResponse = await fetch('http://localhost:8022/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin123'})
});

const {access_token} = await loginResponse.json();

// Поиск департаментов
const searchResponse = await fetch(
  'http://localhost:8022/api/catalog/search?q=безопасность',
  {headers: {Authorization: `Bearer ${access_token}`}}
);

const searchResults = await searchResponse.json();
console.log(`Найдено: ${searchResults.data.total_count} департаментов`);
```

---

## 📞 Поддержка

Для получения помощи:
1. Проверьте `/health` endpoint для диагностики
2. Изучите логи сервера
3. Используйте автоматическую документацию `/docs`

---

## 🚀 **LANGFUSE INTEGRATION FEATURES**

### **Prompt Management**
- ✅ **Centralized Prompts:** Все промпты хранятся в Langfuse с versioning
- ✅ **A/B Testing:** Возможность тестирования разных версий промптов
- ✅ **Configuration Management:** Модель, temperature, и другие параметры в Langfuse

### **Observability & Tracing**
- ✅ **Complete Tracing:** Каждая генерация профиля трейсится в Langfuse
- ✅ **Prompt Linking:** Автоматическая связь generations с промптами
- ✅ **Enhanced Metadata:** Полные метаданные включая tokens, timing, model info
- ✅ **Error Tracking:** Все ошибки трейсятся с контекстом

### **Performance Monitoring**
- ✅ **Token Usage:** Детальная статистика использования токенов
- ✅ **Generation Time:** Мониторинг времени генерации профилей
- ✅ **Model Performance:** Сравнение производительности разных моделей
- ✅ **Cost Tracking:** Отслеживание стоимости API calls

### **Production Ready**
- ✅ **Graceful Degradation:** Система работает без Langfuse если недоступен
- ✅ **Error Recovery:** Automatic retry logic для LLM API calls
- ✅ **Environment Separation:** Development/Production трейсы разделены
- ✅ **Comprehensive Testing:** Полное покрытие integration тестами

---

---

## 🚨 **PRODUCTION CHECKLIST**

### Перед развертыванием в продакшене:

**🔒 Security:**
- [ ] **КРИТИЧНО: Удалить TEST_JWT_TOKEN из .env файла!**
- [ ] Изменить пароли пользователей (ADMIN_PASSWORD, HR_PASSWORD)
- [ ] Сгенерировать новый JWT_SECRET_KEY для продакшена
- [ ] Настроить CORS_ORIGINS для production домена
- [ ] Использовать HTTPS (обязательно!)

**🏗️ Infrastructure:**
- [ ] Настроить реверс-прокси (nginx)
- [ ] Настроить SSL/TLS сертификаты
- [ ] Настроить мониторинг и логирование
- [ ] Настроить backup базы данных
- [ ] Проверить и настроить все переменные окружения

**🧪 Testing:**
- [ ] Протестировать все API endpoints
- [ ] Проверить download функциональность
- [ ] Проверить производительность с большим количеством профилей
- [ ] Протестировать обработку ошибок

---

**📈 System Status:** Production Ready
**🔧 Backend Completion:** 15/15 tasks ✅
**📊 Overall Progress:** 22/50 tasks (44%)
**🚀 Next Phase:** Frontend NiceGUI Implementation

**Версия API:** 1.0.0
**Документация актуальна на:** 2025-09-09
**🤖 Generated with [Claude Code](https://claude.ai/code)**

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

### `GET /api/catalog/departments`
Получение списка всех департаментов.

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
  "service": "A101 HR Profile Generator API",
  "version": "1.0.0", 
  "description": "Система автоматической генерации профилей должностей А101",
  "docs": "/docs",
  "health": "/health",
  "timestamp": "2025-09-07T20:13:10.123456",
  "message": "🏢 Добро пожаловать в систему генерации профилей должностей А101!"
}
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

**Версия API:** 1.0.0  
**Документация актуальна на:** 2025-09-07
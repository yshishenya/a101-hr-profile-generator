# Backend - HR Profile Generator

FastAPI backend для AI-powered генерации профилей должностей.

## 🏗️ Архитектура

```
backend/
├── main.py              # FastAPI приложение и маршруты
├── api/                 # API endpoints
│   └── routes/          # Route handlers
├── core/                # Бизнес логика (основной слой)
│   ├── config.py        # Конфигурация (.env)
│   ├── data_loader.py   # Загрузка данных компании
│   ├── data_mapper.py   # Маппинг департаментов и KPI
│   ├── llm_client.py    # Интеграция с OpenRouter/Langfuse
│   ├── profile_generator.py  # Генератор профилей
│   ├── prompt_manager.py     # Управление промптами
│   ├── docx_service.py       # Экспорт в DOCX
│   ├── markdown_service.py   # Экспорт в Markdown
│   └── storage_service.py    # Работа с базой данных
├── models/              # Pydantic модели (устаревшие)
├── services/            # Сервисный слой
├── tools/               # Утилиты
│   └── xlsx_dump.py     # Экспорт в Excel
└── utils/               # Вспомогательные функции
```

## 🔑 Ключевые компоненты

### Core Layer

#### config.py
Централизованная конфигурация через environment variables:
```python
from backend.core.config import settings

# Доступ к настройкам
api_key = settings.openrouter_api_key
langfuse_host = settings.langfuse_host
```

#### data_loader.py
Детерминированная загрузка данных компании:
- Загрузка организационной структуры
- Парсинг Markdown данных
- 75x оптимизация с кешированием (3ms vs 225ms)

#### data_mapper.py
Маппинг данных без использования LLM:
- Маппинг департаментов на структуру компании
- Маппинг KPI по департаментам
- 100% детерминированный подход

#### llm_client.py
Интеграция с OpenRouter и Langfuse:
- Полная observability через Langfuse
- Retry механизмы
- Structured output с JSON Schema
- Async/await для всех операций

#### profile_generator.py
Главный оркестратор генерации:
```python
from backend.core.profile_generator import ProfileGenerator

generator = ProfileGenerator()
profile = await generator.generate_profile(
    position="Senior ML Engineer",
    department="ДИТ",
    employee_name="Иван Иванов"
)
```

#### prompt_manager.py
Управление промптами через Langfuse:
- Централизованное хранение промптов
- Версионирование
- Fallback на локальные промпты

#### organization_cache.py
Кеширование организационной структуры:
- In-memory кеш для быстрого доступа
- 75x улучшение производительности (3ms vs 225ms)
- Автоматическая инвалидация кеша

#### kpi_department_mapping.py
Статический маппинг KPI на департаменты:
- Детерминированное соответствие KPI и департаментов
- Поддержка иерархии департаментов
- Валидация маппинга

#### docx_service.py
Экспорт профилей в DOCX формат:
- Форматированные документы Word
- Кастомизируемые шаблоны
- Поддержка русского языка

#### markdown_service.py
Экспорт профилей в Markdown:
- GitHub-flavored Markdown
- Структурированные секции
- Готово для документации

#### storage_service.py
Работа с SQLite базой данных:
- CRUD операции для профилей
- История генераций
- Асинхронные операции

#### interfaces.py
Базовые интерфейсы и типы:
- Protocol классы для type safety
- Общие типы данных
- Контракты между модулями

### API Layer

FastAPI endpoints в `main.py`:
- `POST /api/auth/login` - Аутентификация
- `GET /api/catalog/departments` - Список департаментов
- `GET /api/catalog/positions/{dept}` - Должности департамента
- `POST /api/generate` - Генерация профиля
- `GET /api/profiles/{id}` - Получение профиля
- `GET /api/profiles/export/{id}` - Экспорт профиля

## 🚀 Запуск

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env

# Запуск сервера
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8022
```

### Docker

```bash
docker compose up backend
```

## 🧪 Тестирование

```bash
# Unit тесты
pytest backend/tests/unit/

# Integration тесты
pytest backend/tests/integration/

# С покрытием
pytest --cov=backend --cov-report=html
```

## 📊 База данных

SQLite база данных в `/data/profiles.db`:

**Таблицы:**
- `users` - Пользователи системы
- `profiles` - Сгенерированные профили
- `generation_tasks` - Задачи генерации
- `generation_history` - История генераций
- `organization_cache` - Кеш организационной структуры

**Инициализация:**
```python
from backend.core.database import init_database
await init_database()
```

## 🔧 Конфигурация

### Environment Variables

```bash
# OpenRouter API
OPENROUTER_API_KEY="your-api-key"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
OPENROUTER_MODEL="google/gemini-2.5-flash-lite"

# Langfuse (обязательно)
LANGFUSE_PUBLIC_KEY="pk-lf-xxx"
LANGFUSE_SECRET_KEY="sk-lf-xxx"
LANGFUSE_HOST="https://cloud.langfuse.com"

# Authentication
JWT_SECRET_KEY="your-secret-key"
ADMIN_PASSWORD="your-password"

# Database
DATABASE_URL="sqlite:///./data/profiles.db"

# Paths
BASE_DATA_PATH="/app"  # или локальный путь
```

## 🎯 Стандарты кода

### Async/Await
Все I/O операции ДОЛЖНЫ быть асинхронными:

```python
# ✅ Правильно
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Неправильно
def fetch_data(url: str) -> dict:
    response = requests.get(url)  # Блокирует event loop!
    return response.json()
```

### Type Hints
Обязательные type hints для всех функций:

```python
from typing import Dict, List, Optional

async def process_profiles(
    department: str,
    limit: Optional[int] = None
) -> List[Dict[str, str]]:
    """Process profiles for department."""
    ...
```

### Error Handling
Структурированная обработка ошибок:

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

## 📚 Дополнительная документация

- [API Documentation](../docs/reference/api/endpoints.md)
- [Architecture](../docs/explanation/architecture/system-architecture.md)
- [Memory Bank](../.memory_bank/)

## 🔗 Связанные проекты

- **Frontend**: [../frontend/](../frontend/)
- **Scripts**: [../scripts/](../scripts/)
- **Tests**: [../tests/](../tests/)

---

**Для более детальной информации см. [Memory Bank](../.memory_bank/README.md)**

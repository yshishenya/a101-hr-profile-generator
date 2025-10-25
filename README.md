# 🏢 A101 HR Profile Generator

**Автоматическая генерация профилей должностей для компании А101 с использованием AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Langfuse](https://img.shields.io/badge/Langfuse-Observability-orange.svg)](https://langfuse.com)

## 🎯 Описание проекта

A101 HR Profile Generator - это AI-powered система для автоматического создания детальных профилей должностей на основе данных компании А101. Система использует **детерминированную логику для маппинга данных**, **Gemini 2.5 Flash через OpenRouter**, и **полную интеграцию с Langfuse** для observability.

### 🆕 Что нового (2025-10-25)

**⚡ Миграция на AsyncOpenAI** - система переведена на асинхронный HTTP клиент для **истинно параллельной генерации профилей**. Это дает **8-10x ускорение** при пакетной генерации (100 профилей за ~6 минут вместо ~50 минут).

📖 Подробности: [ASYNC_OPENAI_MIGRATION.md](docs/ASYNC_OPENAI_MIGRATION.md)

### ✨ Ключевые особенности

- 🤖 **AI-генерация профилей** с использованием Google Gemini 2.5 Flash Lite
- 🚀 **Параллельная генерация** через AsyncOpenAI - 10x ускорение для больших пакетов
- 🔗 **Langfuse Prompt Management** - централизованное управление промптами и трейсинг
- 📊 **Детерминированная обработка данных** - 100% точность маппинга департаментов и KPI
- ⚡ **Оптимизированная производительность** - 75x ускорение загрузки каталога (3ms с кешем)
- 📈 **Comprehensive Observability** - полный трейсинг генераций с метаданными
- 🎯 **Structured Output** - JSON Schema валидация для консистентных результатов
- 📄 **Множественные форматы экспорта** (JSON, Markdown, Excel)

## 🏗️ Архитектура системы

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   NiceGUI UI    │ ◄──────────────► │   FastAPI       │
│   (Frontend)    │                  │   (Backend)     │
│   Port: 8033    │                  │   Port: 8022    │
└─────────────────┘                  └─────────────────┘
                                            │
           ┌─────────────────────┬───────────┼─────────┬─────────────────┐
           │                     │           │         │                 │
  ┌────────▼─────────┐  ┌────────▼───────────▼─────────▼─────┐  ┌─────────▼─────────┐
  │   SQLite DB      │  │     Backend Core Layers        │  │  OpenRouter API   │
  │   (Profiles)     │  │  ┌─────────────────────────┐   │  │   (Gemini LLM)    │
  │                  │  │  │   ProfileGenerator      │   │  │                   │
  └──────────────────┘  │  └─────────────────────────┘   │  └───────────────────┘
                        │  ┌─────────────────────────┐   │           
                        │  │      DataLoader         │   │  ┌─────────────────────┐
                        │  │  (Deterministic Logic)  │   │  │     Langfuse        │
                        │  └─────────────────────────┘   │  │   (Monitoring)      │
                        └─────────────────────────────────┘  └─────────────────────┘
```

## 📊 Прогресс проекта

### **Фазы разработки:**
- **ФАЗА 1:** Backend API Implementation **[15/15 задач]** ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
- **ФАЗА 2:** Frontend NiceGUI Implementation **[12/15 задач]** ✅✅✅✅✅✅✅✅✅✅✅✅⬜⬜⬜
- **ФАЗА 3:** Testing & Quality Assurance **[2/8 задач]** ✅✅⬜⬜⬜⬜⬜⬜
- **ФАЗА 4:** Deployment & DevOps **[3/7 задач]** ✅✅✅⬜⬜⬜⬜
- **ФАЗА 5:** Documentation & Polish **[4/5 задач]** ✅✅✅✅⬜

**Общий прогресс:** **36/50 задач (72%)** 🎯

### ✅ **Выполнено (ФАЗА 1 - Backend):**
- **Core Infrastructure:** FastAPI приложение, SQLite база, JWT authentication
- **Data Processing:** Детерминированные мапперы для организации и KPI
- **AI Integration:** Полная интеграция с Langfuse + OpenRouter + Gemini 2.5 Flash
- **Performance:** 75x оптимизация загрузки каталога, 10x параллельная генерация
- **API Endpoints:** Полный CRUD профилей, async генерация, multiple exports
- **Observability:** Комплексный трейсинг с enriched metadata

### ✅ **Выполнено (ФАЗА 2 - Frontend):**
- **NiceGUI Interface:** Полнофункциональный веб-интерфейс
- **Profile Generator Page:** Форма генерации с валидацией
- **API Client:** Асинхронное взаимодействие с backend
- **Error Handling:** Обработка ошибок и восстановление
- **Export Options:** Поддержка всех форматов экспорта

### ✅ **Выполнено (ФАЗА 3 - Testing):**
- **Integration Tests:** Тесты API endpoints и E2E user journeys
- **Architecture Tests:** Проверка целостности архитектуры

### ✅ **Выполнено (ФАЗА 4 - DevOps):**
- **Docker:** Контейнеризация backend и frontend
- **Docker Compose:** Оркестрация сервисов
- **Environment Management:** Конфигурация через .env

### ✅ **Выполнено (ФАЗА 5 - Documentation):**
- **Memory Bank:** Полная техническая документация
- **Diátaxis Structure:** Реорганизация документации
- **Backend README:** Детальная документация backend
- **Contributing Guide:** Гайд для контрибьюторов

### 🔄 **В работе:**
- **Unit Tests:** Покрытие тестами 80%+
- **Production Deployment:** Финальная подготовка к prod

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Docker & Docker Compose (рекомендуется)
- **OpenRouter API ключ** для Gemini 2.5 Flash
- **Langfuse ключи** (public + secret) - обязательно для работы системы

### 🐳 Быстрый старт с Docker (Рекомендуется)

```bash
# 1. Клонируем репозиторий
git clone https://github.com/your-username/a101-hr-profile-generator.git
cd a101-hr-profile-generator

# 2. Копируем пример конфигурации
cp .env.example .env

# 3. Настраиваем переменные окружения в .env
OPENROUTER_API_KEY="your-openrouter-api-key"
LANGFUSE_PUBLIC_KEY="pk-lf-your-public-key"
LANGFUSE_SECRET_KEY="sk-lf-your-secret-key"
LANGFUSE_HOST="https://cloud.langfuse.com"
BASE_DATA_PATH="/app"
JWT_SECRET_KEY="your-jwt-secret-for-auth"
ADMIN_PASSWORD="your-admin-password"

# 4. Запускаем систему
docker compose up --build

# Backend API доступен на:
# http://localhost:8022/docs (Swagger)
# http://localhost:8022/health (Health Check)
```

### 🔧 Локальная разработка

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Настройка переменных окружения (как выше)
export OPENROUTER_API_KEY="your-key"
export LANGFUSE_PUBLIC_KEY="your-key"
export LANGFUSE_SECRET_KEY="your-key"
export BASE_DATA_PATH="/home/yan/A101/HR"

# 3. Инициализация базы данных (опционально, создается автоматически)
# python backend/models/database.py

# 4. Запуск сервера
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8022
```

### 🧪 Тестирование интеграции

```bash
# Проверка полного пайплайна
python test_fixed_prompt_linking.py

# Тестирование подключений
python check_langfuse_api.py

# Создание промптов в Langfuse
python create_langfuse_prompt.py
```

## 📁 Структура проекта

```
a101-hr-profile-generator/
├── 📦 backend/                    # FastAPI Backend
│   ├── README.md                 # Backend документация
│   ├── main.py                   # Основное приложение
│   ├── api/                      # API endpoints
│   ├── core/                     # Бизнес логика
│   │   ├── config.py             # Централизованная конфигурация (.env)
│   │   ├── data_loader.py        # Детерминированная загрузка данных
│   │   ├── llm_client.py         # Langfuse OpenAI интеграция
│   │   ├── profile_generator.py  # Главный генератор профилей
│   │   └── prompt_manager.py     # Langfuse Prompt Management
│   ├── tools/                    # Утилиты и инструменты
│   └── models/                   # Модели данных (legacy)
├── 🎨 frontend/                  # NiceGUI Frontend
├── 📚 docs/                      # Документация (структурированная)
│   ├── README.md                 # Навигация по документации
│   ├── getting-started/          # Руководства для начинающих
│   ├── guides/                   # Практические руководства
│   │   ├── deployment/           # Deployment гайды
│   │   ├── development/          # Development гайды
│   │   └── operations/           # Operations гайды
│   ├── explanation/              # Концепции и архитектура
│   │   ├── architecture/         # Архитектурная документация
│   │   └── concepts/             # Концепции системы
│   ├── reference/                # Справочная информация
│   │   ├── api/                  # API документация
│   │   ├── schemas/              # JSON схемы
│   │   └── configuration/        # Конфигурация
│   ├── specs/                    # Технические спецификации
│   ├── org_structure/            # Организационная структура компании
│   ├── IT systems/               # IT системы и потоки данных
│   ├── KPI/                      # KPI исходные файлы и анализы
│   ├── Profiles/                 # Шаблоны профилей
│   └── archive/                  # Архивные отчеты и анализы
│       ├── reports/              # Отчеты по кварталам
│       ├── analysis/             # Технические анализы
│       └── implementation-plans/ # Планы реализации
├── 📄 templates/                 # JSON схемы и промпты
│   ├── job_profile_schema.json   # Основная схема профиля
│   └── generation_prompt.txt     # Базовый промпт
├── 🗂️ data/                     # Данные и база данных
│   ├── profiles.db               # SQLite база данных
│   ├── structure.json            # Организационная структура компании
│   ├── KPI/                      # KPI по департаментам (MD файлы)
│   ├── anonymized_digitization_map.md
│   └── Карта Компании А101.md    # Основная карта компании
├── 🧠 .memory_bank/              # Memory Bank (для Claude Code)
│   ├── README.md                 # Основная память проекта
│   ├── tech_stack.md             # Технологический стек
│   ├── current_tasks.md          # Текущие задачи
│   ├── guides/                   # Руководства
│   ├── patterns/                 # Архитектурные паттерны
│   └── workflows/                # Рабочие процессы
├── 🧪 scripts/                   # Утилиты и скрипты
│   ├── it_department_profile_generator.py  # Генератор профилей для ДИТ
│   ├── universal_profile_generator.py      # Универсальный генератор
│   ├── upload_prompt_to_langfuse.py        # Загрузка промптов
│   ├── sync_prompts_from_langfuse.py       # Синхронизация промптов
│   ├── performance_profiler.py             # Профилирование производительности
│   ├── dev-start.sh / dev-stop.sh          # Dev скрипты
│   └── README_IT_Generator.md              # Документация генератора
├── 🧪 tests/                     # Тесты
│   ├── integration/              # Integration и E2E тесты
│   │   ├── test_api_endpoints.py
│   │   ├── test_generation_flow.py
│   │   ├── test_e2e_user_journeys.py
│   │   └── INTEGRATION_TEST_REPORT.md
│   └── test_architecture_integrity.py
├── 📁 feedback/                  # Обратная связь по профилям
│   └── *.docx                    # DOCX файлы с комментариями
├── 📝 README.md                  # Этот файл
├── 📋 CHANGELOG.md               # История изменений
├── 🤝 CONTRIBUTING.md            # Гайд для контрибьюторов
└── 🤖 CLAUDE.md                  # Claude Code конфигурация
```

## 🔧 Конфигурация

### Environment Variables (.env файл)

```bash
# 🔑 OpenRouter (Обязательно)
OPENROUTER_API_KEY="your-openrouter-api-key"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
OPENROUTER_MODEL="google/gemini-2.5-flash-lite"

# 📊 Langfuse (Обязательно для работы системы)
LANGFUSE_PUBLIC_KEY="pk-lf-your-public-key"
LANGFUSE_SECRET_KEY="sk-lf-your-secret-key"
LANGFUSE_HOST="https://cloud.langfuse.com"

# 🔐 Аутентификация
JWT_SECRET_KEY="your-jwt-secret-key-for-auth"
ADMIN_PASSWORD="your-admin-password"

# 📁 Пути и конфигурация
BASE_DATA_PATH="/app"  # или локальный путь для разработки
DATABASE_URL="sqlite:///./database.db"
ENVIRONMENT="development"  # development, staging, production
```

### База данных

Система использует SQLite для простоты развертывания:
- **Путь:** `/data/profiles.db`
- **Таблицы:** users, profiles, generation_tasks, generation_history, organization_cache
- **Миграции:** Автоматические при первом запуске

## 📖 API Documentation

### Основные endpoints

```
GET  /health                           # Проверка состояния системы
POST /api/auth/login                   # Аутентификация
GET  /api/catalog/departments          # Список департаментов (⚡ кешируется)
GET  /api/catalog/positions/{dept}     # Должности департамента
POST /api/generate                     # 🤖 Генерация профиля (Langfuse integration)
GET  /api/profiles/{id}               # Получение сохраненного профиля
GET  /api/profiles/export/{id}        # Экспорт профиля
```

### 🧪 Тестовые endpoints

```bash
# Тестирование интеграции с Langfuse
curl -X POST "http://localhost:8022/api/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{
    "position": "Senior ML Engineer",
    "department": "ДИТ",
    "employee_name": "Test User"
  }'
```

Полная документация доступна в `/docs` после запуска сервера.

## 🧪 Тестирование

### 🔗 Langfuse Integration Tests

```bash
# Полный пайплайн с prompt linking
python test_fixed_prompt_linking.py

# Детальное исследование OpenRouter responses
python test_openrouter_response_details.py

# Трейсинг и observability
python test_full_trace_pipeline.py
```

### 🔬 Unit тесты

```bash
# Integration тесты
pytest tests/integration/

# Architecture тесты
pytest tests/test_architecture_integrity.py

# Все тесты
pytest
```

## 📚 Документация

Полная документация проекта организована по принципу **Diátaxis Framework**:

### 🎯 Основные разделы

- **[📖 Документация](docs/)** - Полная документация проекта
  - [Начало работы](docs/getting-started/) - Туториалы для новых пользователей
  - [Практические руководства](docs/guides/) - Решение конкретных задач
  - [Концепции и архитектура](docs/explanation/) - Понимание системы
  - [Справочная информация](docs/reference/) - API, схемы, конфигурация

- **[🧠 Memory Bank](.memory_bank/)** - Техническая память проекта (для Claude Code)
  - [Tech Stack](.memory_bank/tech_stack.md) - Технологический стек
  - [Coding Standards](.memory_bank/guides/coding_standards.md) - Стандарты кодирования
  - [Current Tasks](.memory_bank/current_tasks.md) - Текущие задачи

- **[📦 Backend](backend/README.md)** - Backend документация
- **[🤝 Contributing](CONTRIBUTING.md)** - Гайд для контрибьюторов
- **[📋 Changelog](CHANGELOG.md)** - История изменений

### 🔗 Быстрые ссылки

| Для кого | Начните с |
|----------|-----------|
| **Новые пользователи** | [Быстрый старт](docs/getting-started/quick-start.md) |
| **Разработчики** | [Backend README](backend/README.md) → [Tech Stack](.memory_bank/tech_stack.md) |
| **DevOps инженеры** | [Docker Deployment](docs/guides/deployment/docker-deployment.md) |
| **Контрибьюторы** | [CONTRIBUTING.md](CONTRIBUTING.md) |

## 🤝 Contributing

Мы приветствуем вклад в проект! Пожалуйста, ознакомьтесь с **[CONTRIBUTING.md](CONTRIBUTING.md)** для получения детальной информации о:
- Настройке окружения разработки
- Стандартах кодирования
- Процессе создания Pull Request
- Архитектурных принципах проекта

## 📄 License

Этот проект распространяется под лицензией MIT. См. `LICENSE` для подробностей.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) - Modern web framework
- [NiceGUI](https://nicegui.io) - Python web UI framework
- [Langfuse](https://langfuse.com) - LLM observability
- [OpenRouter](https://openrouter.ai) - LLM API gateway

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**
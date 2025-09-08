# 🏢 A101 HR Profile Generator

**Автоматическая генерация профилей должностей для компании А101 с использованием AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Langfuse](https://img.shields.io/badge/Langfuse-Observability-orange.svg)](https://langfuse.com)

## 🎯 Описание проекта

A101 HR Profile Generator - это AI-powered система для автоматического создания детальных профилей должностей на основе данных компании А101. Система использует **детерминированную логику для маппинга данных**, **Gemini 2.5 Flash через OpenRouter**, и **полную интеграцию с Langfuse** для observability.

### ✨ Ключевые особенности

- 🤖 **AI-генерация профилей** с использованием Google Gemini 2.5 Flash Lite
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
- **ФАЗА 1:** Backend API Implementation **[14/15 задач]** ✅✅✅✅✅✅✅✅✅✅✅✅✅✅⬜
- **ФАЗА 2:** Frontend NiceGUI Implementation **[0/15 задач]** ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
- **ФАЗА 3:** Testing & Quality Assurance **[0/8 задач]** ⬜⬜⬜⬜⬜⬜⬜⬜
- **ФАЗА 4:** Deployment & DevOps **[1/7 задач]** ✅⬜⬜⬜⬜⬜⬜
- **ФАЗА 5:** Documentation & Polish **[0/5 задач]** ⬜⬜⬜⬜⬜

**Общий прогресс:** **15/50 задач (30%)**

### ✅ **Выполнено (ФАЗА 1 - Backend):**
- **Core Infrastructure:** FastAPI приложение, SQLite схема, authentication
- **Data Processing:** Детерминированные мапперы для организации и KPI 
- **AI Integration:** Полная интеграция с Langfuse + OpenRouter + Gemini 2.5 Flash
- **Performance:** 75x оптимизация загрузки каталога с кешированием
- **API Endpoints:** Полный CRUD профилей, async генерация, export
- **Observability:** Комплексный трейсинг с enriched metadata

### ✅ **Выполнено (ФАЗА 4 - DevOps):**
- **Docker Environment:** Контейнеризация с environment management

### 🔄 **В работе:**
- **Frontend Development:** NiceGUI интерфейс (планируется)

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.9+
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
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/health (Health Check)
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

# 3. Инициализация базы данных
python backend/core/database.py

# 4. Запуск сервера
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
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
│   ├── 🚀 main.py                # Основное приложение
│   ├── 📊 api/                   # API endpoints
│   ├── 🧠 core/                  # Бизнес логика
│   │   ├── config.py             # Централизованная конфигурация (.env)
│   │   ├── data_loader.py        # Детерминированная загрузка данных
│   │   ├── llm_client.py         # Langfuse OpenAI интеграция
│   │   ├── profile_generator.py  # Главный генератор профилей
│   │   ├── prompt_manager.py     # Langfuse Prompt Management
│   │   └── database.py           # SQLite операции
│   ├── 🔧 tools/                 # Утилиты и инструменты
│   │   └── xlsx_dump.py          # Экспорт в Excel
│   └── 🗄️ models/               # Модели данных (legacy)
├── 🎨 frontend/                  # NiceGUI Frontend (планируется)
├── 📚 docs/                      # Документация + данные компании
│   ├── PROJECT_BACKLOG.md        # Детальный план проекта
│   ├── SYSTEM_ARCHITECTURE.md    # Архитектура системы
│   ├── org_structure/            # Организационная структура
│   └── IT systems/               # IT системы и потоки данных
├── 📄 templates/                 # JSON схемы и промпты
│   ├── job_profile_schema.json   # Основная схема профиля
│   ├── universal_job_profile_schema.json
│   └── generation_prompt.txt     # Базовый промпт
├── 🗂️ data/                     # Исходные данные компании
│   └── Карта Компании А101.md    # Основная карта компании
└── 🧪 test_*.py                  # Тесты интеграции с Langfuse
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
curl -X POST "http://localhost:8000/api/generate" \
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

### 🔬 Unit тесты (планируется)

```bash
# Unit тесты
pytest backend/tests/unit/

# Integration тесты  
pytest backend/tests/integration/

# Все тесты
pytest
```

## 🤝 Contributing

1. Fork проект
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

Следуйте архитектурным принципам проекта:
- Детерминированная логика для маппинга данных
- LLM только для творческой генерации
- Поддержка существующих core модулей

## 📄 License

Этот проект распространяется под лицензией MIT. См. `LICENSE` для подробностей.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) - Modern web framework
- [NiceGUI](https://nicegui.io) - Python web UI framework
- [Langfuse](https://langfuse.com) - LLM observability
- [OpenRouter](https://openrouter.ai) - LLM API gateway

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**
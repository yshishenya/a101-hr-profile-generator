# 🏢 A101 HR Profile Generator

**Автоматическая генерация профилей должностей для компании А101 с использованием AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![NiceGUI](https://img.shields.io/badge/NiceGUI-Material%20Design-purple.svg)](https://nicegui.io)

## 🎯 Описание проекта

A101 HR Profile Generator - это AI-powered система для автоматического создания детальных профилей должностей на основе данных компании А101. Система использует **детерминированную логику для маппинга данных** и **Gemini 2.5 Flash для творческой генерации контента**.

### ✨ Ключевые особенности

- 🤖 **AI-генерация профилей** с использованием Gemini 2.5 Flash
- 📊 **Детерминированная обработка данных** - 100% точность маппинга
- 🎨 **Material Design интерфейс** на NiceGUI
- ⚡ **Асинхронная генерация** для сложных профилей
- 📈 **Интеграция с Langfuse** для мониторинга качества
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
- **ФАЗА 1:** Backend API Implementation **[2/12 задач]** ✅✅⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
- **ФАЗА 2:** Frontend NiceGUI Implementation **[0/15 задач]** ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
- **ФАЗА 3:** Testing & Quality Assurance **[0/8 задач]** ⬜⬜⬜⬜⬜⬜⬜⬜
- **ФАЗА 4:** Deployment & DevOps **[0/7 задач]** ⬜⬜⬜⬜⬜⬜⬜
- **ФАЗА 5:** Documentation & Polish **[0/5 задач]** ⬜⬜⬜⬜⬜

**Общий прогресс:** **2/47 задач (4%)**

### ✅ **Выполнено:**
- **Task 1.1:** FastAPI Application Setup - Базовое приложение с CORS, middleware, health check
- **Task 1.2:** Database Models & Schema - SQLite схема + 20+ Pydantic моделей

### 🔄 **В работе:**
- **Task 1.3:** Authentication API - JWT токены, session management

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.9+
- OpenRouter API ключ для Gemini 2.5 Flash
- Langfuse ключи (опционально)

### Установка

```bash
# Клонируем репозиторий
git clone https://github.com/your-username/a101-hr-profile-generator.git
cd a101-hr-profile-generator

# Устанавливаем зависимости
pip install -r requirements.txt

# Настраиваем переменные окружения
export OPENROUTER_API_KEY="your-openrouter-api-key"
export LANGFUSE_PUBLIC_KEY="your-langfuse-key"    # Опционально
export LANGFUSE_SECRET_KEY="your-langfuse-secret" # Опционально
```

### Запуск Backend API

```bash
# Запуск FastAPI сервера
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8022

# API документация будет доступна на:
# http://localhost:8022/docs (Swagger)
# http://localhost:8022/redoc (Redoc)
```

### Инициализация базы данных

```bash
# Создание схемы и начальных данных
python backend/models/database.py

# Пользователи по умолчанию:
# admin / admin123
# hr / hr123
```

## 📁 Структура проекта

```
a101-hr-profile-generator/
├── 📦 backend/                    # FastAPI Backend
│   ├── 🚀 main.py                # Основное приложение
│   ├── 📊 api/                   # API endpoints
│   ├── 🧠 core/                  # Бизнес логика
│   │   ├── data_mapper.py        # Детерминированное маппинг
│   │   ├── data_loader.py        # Загрузка и подготовка данных
│   │   ├── llm_client.py         # Gemini 2.5 Flash client
│   │   └── profile_generator.py  # Главный генератор
│   ├── 🗄️ models/               # Модели данных
│   │   ├── database.py           # SQLite схема
│   │   └── schemas.py            # Pydantic модели
│   └── 🔧 utils/                 # Утилиты
├── 🎨 frontend/                  # NiceGUI Frontend (планируется)
├── 📚 docs/                      # Документация
│   ├── PROJECT_BACKLOG.md        # Детальный план проекта
│   ├── SYSTEM_ARCHITECTURE.md    # Архитектура системы
│   └── USER_JOURNEY_MVP.md       # UX дизайн
├── 📄 templates/                 # Шаблоны и схемы
└── 🗂️ data/                     # Данные компании
```

## 🔧 Конфигурация

### Environment Variables

```bash
# Обязательные
OPENROUTER_API_KEY="your-openrouter-api-key"

# Опциональные  
LANGFUSE_PUBLIC_KEY="your-langfuse-key"
LANGFUSE_SECRET_KEY="your-langfuse-secret"
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
GET  /api/catalog/departments          # Список департаментов
GET  /api/catalog/positions/{dept}     # Должности департамента
POST /api/profiles/generate            # Генерация профиля (sync)
POST /api/profiles/generate-async      # Генерация профиля (async)
GET  /api/profiles/{id}               # Получение профиля
GET  /api/profiles/export/{id}        # Экспорт профиля
```

Полная документация доступна в `/docs` после запуска сервера.

## 🧪 Тестирование

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
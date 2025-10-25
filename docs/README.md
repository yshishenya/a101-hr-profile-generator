# 📚 Документация HR Profile Generator

Добро пожаловать в документацию проекта! Эта документация организована по принципу **Diátaxis Framework** для максимальной эффективности поиска информации.

## 🧭 Навигация по документации

### 📖 Начало работы (Getting Started - Tutorials)
Пошаговые руководства для новых пользователей:

- **[Быстрый старт](getting-started/quick-start.md)** - Запуск системы за 5 минут
- **[Установка](getting-started/installation.md)** - Детальная установка и настройка
- **[Первый профиль](getting-started/first-profile.md)** - Создание вашего первого профиля должности

### 🔧 Практические руководства (How-To Guides)
Решение конкретных задач:

#### Deployment
- **[Docker Deployment](guides/deployment/docker-deployment.md)** - Развертывание с Docker
- **[Docker Bind Mounts](guides/deployment/docker-bind-mounts.md)** - Работа с bind mounts
- **[Production Deployment](guides/deployment/deployment-guide.md)** - Продакшен развертывание

#### Development
- **[Локальная разработка](guides/development/local-setup.md)** - Настройка окружения разработки
- **[Тестирование](guides/development/testing-guide.md)** - Запуск и написание тестов

#### Operations
- **[Docker Management](guides/operations/docker-management.md)** - Управление Docker контейнерами

### 💡 Концепции и объяснения (Explanation)
Понимание того, как работает система:

#### Архитектура
- **[Системная архитектура](explanation/architecture/system-architecture.md)** - Общая архитектура системы
- **[Потоки данных](explanation/architecture/data-flow.md)** - Как данные движутся в системе
- **[LLM интеграция](explanation/architecture/llm-integration.md)** - Интеграция с языковыми моделями

#### Концепции
- **[Генерация профилей](explanation/concepts/profile-generation.md)** - Как работает генерация
- **[KPI маппинг](explanation/concepts/kpi-mapping.md)** - Система соответствия KPI

### 📋 Справочная информация (Reference)
Техническая документация:

#### API
- **[API Endpoints](reference/api/endpoints.md)** - Все API эндпоинты

#### Схемы
- **[Схема профиля](reference/schemas/profile-schema.md)** - JSON Schema профиля должности

#### Конфигурация
- **[Переменные окружения](reference/configuration/environment-variables.md)** - Все env переменные

### 📐 Технические спецификации (Specs)
Детальные спецификации функций:

- **[KPI Filtering Spec](specs/KPI_FILTERING_IMPLEMENTATION_SPEC.md)** - Спецификация фильтрации KPI
- **[Future Features](specs/future-features/)** - Планируемые функции

### 🏢 Данные компании (Company Data)
Данные и структуры компании:

- **[Организационная структура](org_structure/)** - Иерархия компании
- **[IT системы](IT%20systems/)** - Описание IT систем и потоков данных
- **[KPI](KPI/)** - Каталог KPI по департаментам

### 🗄️ Архив (Archive)
Исторические отчеты и анализы:

#### Отчеты
- **[Отчеты Q1 2025](archive/reports/2025-Q1/)** - Квартальные отчеты
  - Phase 1 Complete Report
  - Security Audit Report
  - Production Readiness Report
  - End to End Test Report

#### Анализы
- **[Архитектура](archive/analysis/architecture/)** - Архитектурные анализы
- **[Производительность](archive/analysis/performance/)** - Анализы производительности
- **[Промпты](archive/analysis/prompts/)** - Анализы и улучшения промптов
- **[KPI](archive/analysis/kpi/)** - Анализы системы KPI

#### Планы реализации
- **[Планы Q1 2025](archive/implementation-plans/2025-Q1/)** - Детальные планы реализации

## 🎯 Быстрые ссылки

### Для новых пользователей
1. Начните с [Быстрого старта](getting-started/quick-start.md)
2. Изучите [Системную архитектуру](explanation/architecture/system-architecture.md)
3. Прочитайте [Руководство по deployment](guides/deployment/docker-deployment.md)

### Для разработчиков
1. Настройте [Локальное окружение](guides/development/local-setup.md)
2. Изучите [Backend README](../backend/README.md)
3. Ознакомьтесь с [API Reference](reference/api/endpoints.md)

### Для операторов
1. [Docker Management](guides/operations/docker-management.md)
2. [Production Deployment](guides/deployment/deployment-guide.md)
3. [Environment Variables](reference/configuration/environment-variables.md)

## 📝 Дополнительная информация

- **[CHANGELOG](../CHANGELOG.md)** - История изменений проекта
- **[CONTRIBUTING](../CONTRIBUTING.md)** - Как внести вклад в проект
- **[Memory Bank](../.memory_bank/README.md)** - Техническая память проекта (для Claude Code)

## 🔍 Не нашли что искали?

- Проверьте [Memory Bank](../.memory_bank/) для технической информации
- Посмотрите [архив отчетов](archive/reports/) для исторического контекста
- Создайте issue в репозитории проекта

---

**💡 Совет:** Документация следует принципу **Single Source of Truth**. Если вы нашли устаревшую информацию, пожалуйста, создайте issue или pull request.

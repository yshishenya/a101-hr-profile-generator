# Аудит документации проекта

**Дата:** 2025-10-25
**Статус:** 🔍 Обнаружены критические несоответствия

## 🔴 Критические несоответствия

### 1. Frontend - описан как "планируется", но существует

**Проблема:**
- В README.md указано: "Frontend NiceGUI Implementation [0/15 задач]"
- **Реальность:** Frontend полностью реализован и работает!

**Реальная структура frontend/:**
```
frontend/
├── main.py                    # Главное приложение NiceGUI
├── components/
│   ├── core/                  # Базовые компоненты
│   └── ui/                    # UI компоненты
├── pages/
│   └── generator_page.py      # Страница генерации профилей
├── services/
│   └── api_client.py          # Клиент для backend API
├── core/
│   └── error_recovery.py      # Обработка ошибок
├── utils/
│   └── config.py              # Конфигурация frontend
└── static/css/                # Стили
```

**Действие:** Обновить README с реальным статусом Frontend

---

### 2. Memory Bank Current Tasks - устаревшие задачи

**Проблема:** `.memory_bank/current_tasks.md` содержит задачи из другого проекта:

❌ **Неактуальные задачи:**
- [SETUP-01] Poetry - **НЕ ИСПОЛЬЗУЕТСЯ** (используется pip/requirements.txt)
- [SETUP-02] PostgreSQL - **НЕ ИСПОЛЬЗУЕТСЯ** (используется SQLite)
- [BOT-01] Telegram bot - **НЕ В ЭТОМ ПРОЕКТЕ**
- [CORE-01] Due diligence - **НЕ ОТНОСИТСЯ** (это HR профили)
- [SCRAPE-01] Scraping - **НЕ В ПРОЕКТЕ**

**Действие:** Полностью переписать current_tasks.md с актуальными задачами

---

### 3. Структура data/ - несоответствие описанию

**Описано в README:**
```
data/
└── Карта Компании А101.md
```

**Реальная структура:**
```
data/
├── profiles.db                # ⚠️ НЕ УПОМЯНУТ - SQLite база
├── structure.json             # ⚠️ НЕ УПОМЯНУТ - Оргструктура
├── KPI/                       # ⚠️ НЕ УПОМЯНУТА - Директория KPI
│   ├── KPI_ДИТ.md
│   ├── KPI_АС.md
│   └── ... (9 файлов)
├── anonymized_digitization_map.md
└── Карта Компании А101.md
```

**Действие:** Обновить описание структуры data/

---

### 4. tests/ - вообще не описана

**Проблема:** Есть полноценная директория tests/ с integration тестами:

```
tests/
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_generation_flow.py
│   ├── test_e2e_user_journeys.py
│   ├── live_api_test.py
│   └── INTEGRATION_TEST_REPORT.md
└── test_architecture_integrity.py
```

**Действие:** Добавить описание тестов в README и создать docs/guides/development/testing-guide.md

---

### 5. scripts/ - слабо описаны

**Проблема:** В README упоминается только 2 скрипта, но их больше:

**Реальная структура scripts/:**
```
scripts/
├── it_department_profile_generator.py      # ✅ Упомянут
├── upload_prompt_to_langfuse.py            # ✅ Упомянут
├── sync_prompts_from_langfuse.py           # ⚠️ НЕ УПОМЯНУТ
├── universal_profile_generator.py          # ⚠️ НЕ УПОМЯНУТ
├── test_prompt_fallback.py                 # ⚠️ НЕ УПОМЯНУТ
├── performance_profiler.py                 # ⚠️ НЕ УПОМЯНУТ
├── kpi_to_hybrid_md_converter.py           # ⚠️ НЕ УПОМЯНУТ
├── dev-start.sh                            # ⚠️ НЕ УПОМЯНУТ
├── dev-stop.sh                             # ⚠️ НЕ УПОМЯНУТ
├── start-frontend.sh                       # ⚠️ НЕ УПОМЯНУТ
└── README_IT_Generator.md                  # ⚠️ НЕ УПОМЯНУТ
```

**Действие:** Обновить описание scripts/ и создать документацию для утилит

---

### 6. backend/core/ - неполное описание

**Проблема:** В backend/README.md упомянуты не все модули

**Фактические модули в backend/core/:**
```python
config.py                  # ✅ Упомянут
data_loader.py             # ✅ Упомянут
data_mapper.py             # ✅ Упомянут
llm_client.py              # ✅ Упомянут
profile_generator.py       # ✅ Упомянут
prompt_manager.py          # ✅ Упомянут
docx_service.py            # ⚠️ Упомянут кратко
markdown_service.py        # ⚠️ Упомянут кратко
storage_service.py         # ⚠️ Упомянут как database.py (ОШИБКА!)
organization_cache.py      # ❌ НЕ УПОМЯНУТ
kpi_department_mapping.py  # ❌ НЕ УПОМЯНУТ
interfaces.py              # ❌ НЕ УПОМЯНУТ
```

**Действие:** Обновить backend/README.md

---

### 7. Product Brief - шаблонный текст

**Проблема:** `.memory_bank/product_brief.md` содержит placeholder текст:

```markdown
## Project Goal (WHY)
Profile generatorof empleyyes  # ⚠️ Опечатка и неинформативно

## Target Audience (FOR WHOM)
<!-- Update with your target users -->  # ⚠️ Не заполнено

## Key Features
<!-- Update with your project's main features -->  # ⚠️ Не заполнено
```

**Действие:** Заполнить Product Brief реальными данными

---

## 🟡 Минорные проблемы

### 8. Docker ports несоответствие

**В README указано:**
- Frontend: Port 8033
- Backend: Port 8022

**Нужно проверить:** docker-compose.yml для подтверждения

---

### 9. Python версия

**В README указано:** Python 3.9+
**В .memory_bank/tech_stack.md указано:** Python 3.11+
**В requirements.txt:** Не указана минимальная версия

**Действие:** Унифицировать требование к версии Python

---

### 10. Отсутствует описание feedback/

**Проблема:** Есть директория feedback/ с docx файлами обратной связи, но она не описана

---

## 📋 План исправлений

### Приоритет 1 (Критично):
1. ✅ Обновить README.md - статус Frontend
2. ✅ Переписать .memory_bank/current_tasks.md
3. ✅ Обновить описание структуры data/
4. ✅ Добавить описание tests/
5. ✅ Заполнить Product Brief

### Приоритет 2 (Важно):
6. ✅ Обновить backend/README.md
7. ✅ Создать описание scripts/
8. ✅ Унифицировать версию Python
9. ✅ Проверить docker ports

### Приоритет 3 (Желательно):
10. ⚠️ Создать docs/guides/development/testing-guide.md
11. ⚠️ Создать docs/reference/scripts/utilities.md
12. ⚠️ Добавить описание feedback/

---

## Следующие шаги

1. Обновить все критические несоответствия
2. Синхронизировать версии документов
3. Создать недостающие руководства
4. Обновить Memory Bank

**Статус:** Готов к исправлениям ✅

# 🔴 КРИТИЧЕСКИЕ ПРОТИВОРЕЧИЯ В ДОКУМЕНТАЦИИ

**Дата:** 2025-10-25
**Статус:** 🔴 ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ НЕСООТВЕТСТВИЯ

## ⚠️ КРИТИЧЕСКИЕ ПРОБЛЕМЫ

### 1. 🔴 .memory_bank/tech_stack.md - ШАБЛОННЫЙ ТЕКСТ!

**Проблема:** Файл содержит шаблонный текст, который НЕ соответствует реальному проекту!

#### ❌ Противоречие #1: Package Management
**В tech_stack.md (строка 7):**
```
- **Package Management**: Poetry (dependency management and virtual environments)
```

**РЕАЛЬНОСТЬ:**
- ❌ pyproject.toml НЕ СУЩЕСТВУЕТ
- ✅ Проект использует **pip + requirements.txt**

**Действие:** ИСПРАВИТЬ - Poetry → pip/requirements.txt

---

#### ❌ Противоречие #2: Framework
**В tech_stack.md (строка 5):**
```
- **Framework**: FastAPI (FastAPI/Django/Flask)
```

**РЕАЛЬНОСТЬ:**
- ✅ Используется ТОЛЬКО FastAPI
- ❌ Django и Flask НЕ используются

**Действие:** ИСПРАВИТЬ - убрать (FastAPI/Django/Flask), оставить только FastAPI

---

#### ❌ Противоречие #3: Database Driver
**В tech_stack.md (строка 64):**
```
- **Async Driver**: asyncpg for PostgreSQL
```

**РЕАЛЬНОСТЬ:**
- ❌ PostgreSQL НЕ используется
- ✅ Используется **SQLite**
- ✅ Нет async драйвера для SQLite (используется aiosqlite или sync sqlite3)

**Действие:** ИСПРАВИТЬ - asyncpg for PostgreSQL → aiosqlite for SQLite

---

#### ❌ Противоречие #4: Project Structure
**В tech_stack.md (строки 30-43):**
```
HR profile generator/
├── src/              # Source code
│   ├── api/         # API endpoints
│   ├── core/        # Business logic
│   ├── models/      # Data models
│   ├── services/    # Service layer
│   └── utils/       # Utilities
├── pyproject.toml   # Poetry configuration
```

**РЕАЛЬНОСТЬ:**
```
HR/
├── backend/         # Backend code (НЕ src/)
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── utils/
├── frontend/        # Frontend (отсутствует в шаблоне!)
├── requirements.txt # pip (НЕ pyproject.toml!)
```

**Действие:** ПОЛНОСТЬЮ ПЕРЕПИСАТЬ секцию Project Structure

---

### 2. 🟡 README.md - Мелкие несоответствия

#### ⚠️ Проблема #1: Port в команде запуска
**В README.md (строка 144):**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**docker-compose.yml показывает:**
- Backend port: 8022
- Frontend port: 8033

**Действие:** Изменить 8000 → 8022 для консистентности

---

#### ⚠️ Проблема #2: Frontend "(планируется)"
**В README.md (строка 176):**
```
├── 🎨 frontend/                  # NiceGUI Frontend (планируется)
```

**РЕАЛЬНОСТЬ:**
- ✅ Frontend РЕАЛИЗОВАН и работает
- ✅ Есть в docker-compose.yml
- ✅ Есть директория frontend/ с кодом

**Действие:** Убрать "(планируется)"

---

#### ⚠️ Проблема #3: Database инициализация
**В README.md (строка 141):**
```bash
python backend/core/database.py
```

**РЕАЛЬНОСТЬ:**
- ❌ Файл backend/core/database.py НЕ СУЩЕСТВУЕТ
- ✅ Реальный файл: backend/models/database.py

**Действие:** Исправить путь: backend/core/database.py → backend/models/database.py

---

### 3. 🟡 tech_stack.md - Дополнительные проблемы

#### ⚠️ Проблема #4: pyproject.toml в примерах
**В tech_stack.md (строки 311-354):**
```toml
[tool.poetry]
name = "HR profile generator"
...
[tool.poetry.dependencies]
python = "^3.11"
```

**РЕАЛЬНОСТЬ:**
- ❌ pyproject.toml НЕ СУЩЕСТВУЕТ
- ✅ Используется requirements.txt

**Действие:** УДАЛИТЬ ВСЮ СЕКЦИЮ про pyproject.toml или заменить на requirements.txt

---

## 📊 Сводка проблем

| Файл | Критических | Средних | Всего |
|------|-------------|---------|-------|
| .memory_bank/tech_stack.md | 4 | 1 | 5 |
| README.md | 0 | 3 | 3 |
| **ИТОГО** | **4** | **4** | **8** |

---

## 🎯 План исправлений

### Приоритет 1 (КРИТИЧНО - исправить немедленно):

1. ✅ **tech_stack.md - Package Management**
   - [ ] Poetry → pip/requirements.txt

2. ✅ **tech_stack.md - Framework**
   - [ ] FastAPI (FastAPI/Django/Flask) → FastAPI

3. ✅ **tech_stack.md - Database Driver**
   - [ ] asyncpg for PostgreSQL → aiosqlite/sqlite3 for SQLite

4. ✅ **tech_stack.md - Project Structure**
   - [ ] Полностью переписать секцию с реальной структурой

### Приоритет 2 (ВАЖНО):

5. ⚠️ **README.md - Backend port**
   - [ ] 8000 → 8022

6. ⚠️ **README.md - Frontend статус**
   - [ ] Убрать "(планируется)"

7. ⚠️ **README.md - Database инициализация**
   - [ ] backend/core/database.py → backend/models/database.py

8. ⚠️ **tech_stack.md - pyproject.toml примеры**
   - [ ] Удалить или заменить на requirements.txt

---

## 🔍 Дополнительные находки

### Потенциальные проблемы для проверки:

1. **backend/README.md** - указано database.py, нужно проверить путь
2. **CONTRIBUTING.md** - упоминания Poetry?
3. **docs/guides/** - инструкции по установке могут ссылаться на Poetry

---

## ⚡ Следующие шаги

1. Исправить ВСЕ противоречия в tech_stack.md
2. Исправить мелкие несоответствия в README.md
3. Перепроверить ВСЮ документацию на консистентность
4. Создать финальный отчет о согласованности

---

**Статус:** 🔴 ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ
**Критичность:** ВЫСОКАЯ - tech_stack.md содержит неверную информацию о технологиях!

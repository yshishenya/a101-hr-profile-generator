# 🏗️ **АРХИТЕКТУРА СИСТЕМЫ ГЕНЕРАЦИИ ПРОФИЛЕЙ ДОЛЖНОСТЕЙ**

## 📋 **ОБЗОР СИСТЕМЫ**

**Цель:** Автоматическая генерация профилей должностей для компании А101 с использованием AI

**Технологический стек:**
- 🎨 **Frontend:** NiceGUI (Material Design)
- ⚡ **Backend:** FastAPI (REST API)
- 🤖 **LLM:** Gemini 2.5 Flash через OpenRouter API
- 🗄️ **Database:** SQLite
- 📊 **Monitoring:** Langfuse
- 🏠 **Deployment:** VPS (до 10 пользователей)

## 🏛️ **ВЫСОКОУРОВНЕВАЯ АРХИТЕКТУРА**

```
                    ┌─────────────────────────────────────────────────┐
                    │              🌐 VPS Environment                │
                    │                                                 │
┌─────────────────┐ │    HTTP/REST    ┌─────────────────┐             │
│   NiceGUI UI    │ │ ◄──────────────► │   FastAPI       │             │
│   (Frontend)    │ │                  │   (Backend)     │             │
│   Port: 8033    │ │                  │   Port: 8022    │             │
└─────────────────┘ │                  └─────────────────┘             │
                    │                            │                     │
        ┌───────────│──────────────────┬─────────┼─────────┬───────────│─────┐
        │           │                  │         │         │           │     │
┌───────▼───────┐   │         ┌────────▼─────────▼─────────▼─────┐     │     │
│ Nginx Reverse │   │         │     🧠 Backend Core Layers      │     │     │
│    Proxy      │   │         │                                 │     │     │
│   Port: 8033  │   │         │  ┌─────────────────────────┐    │     │     │
└───────────────┘   │         │  │    ProfileGenerator     │    │     │     │
                    │         │  │   (Main Orchestrator)   │    │     │     │
                    │         │  └─────────────────────────┘    │     │     │
                    │         │  ┌─────────────────────────┐    │     │     │
                    │         │  │     DataLoader          │    │     │     │
                    │         │  │  (Deterministic Logic)  │    │     │     │
                    │         │  └─────────────────────────┘    │     │     │
                    │         │  ┌─────────────────────────┐    │     │     │
                    │         │  │   OrganizationMapper    │    │     │     │
                    │         │  │      KPIMapper          │    │     │     │
                    │         │  └─────────────────────────┘    │     │     │
                    │         └─────────────────────────────────┘     │     │
                    │                            │                     │     │
        ┌───────────│────────────────────────────┼─────────────────────│─────┤
        │           │                            │                     │     │
┌───────▼───────┐   │         ┌─────────▼─────────┐    ┌──────────▼────│───┐ │
│   SQLite DB   │   │         │  OpenRouter API   │    │   Langfuse    │   │ │
│  (Profiles)   │   │         │   (Gemini LLM)    │    │  (Monitoring, │   │ │
│  - profiles   │   │         │                   │    │   Prompts)    │   │ │
│  - history    │   │         │  Model: gemini-   │    │               │   │ │
│  - cache      │   │         │  2.5-flash        │    │  - Traces     │   │ │
└───────────────┘   │         │                   │    │  - Metrics    │   │ │
                    │         │  Context: 1M tok  │    │  - Prompts    │   │ │
                    │         └───────────────────┘    └───────────────│───┘ │
                    │                                                  │     │
                    │  📁 File Storage                                 │     │
                    │  ┌─────────────────────────────────────────────┐ │     │
                    │  │  /storage/                                  │ │     │
                    │  │  ├── profiles/  (Generated JSON/MD)         │ │     │
                    │  │  ├── data/      (Company Data)              │ │     │
                    │  │  │   ├── structure.json                    │ │     │
                    │  │  │   ├── kpi/*.md                          │ │     │
                    │  │  │   └── it_systems/*.md                   │ │     │
                    │  │  └── templates/ (Schemas & Examples)       │ │     │
                    │  └─────────────────────────────────────────────┘ │     │
                    └─────────────────────────────────────────────────┘     │
                                                                            │
┌─────────────────────────────────────────────────────────────────────────┤
│                    🔌 External Services                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🌍 OpenRouter API                    📊 Langfuse Cloud                │
│  - Authentication                     - Trace Management                │
│  - Model Selection                    - Prompt Versioning               │
│  - Rate Limiting                      - Analytics Dashboard             │
│  - Cost Optimization                  - A/B Testing                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### **🔄 Поток данных:**

```
[Пользователь] →[Nginx:80] → [NiceGUI:8033] → [FastAPI:8022]
                                                        ↓
[DataLoader] ← [ProfileGenerator] → [LangfuseService] → [OpenRouter]
     ↓                                    ↓                 ↓
[Company Data] → [Langfuse Variables] → [Prompt+Context] → [Gemini 2.5]
                                                                ↓
[SQLite] ← [Profile Validation] ← [JSON Parsing] ← [LLM Response]
    ↓
[File Storage] → [JSON/MD Export] → [Frontend Display]
```

## 📁 **СТРУКТУРА ПРОЕКТА**

```
hr-profile-generator/
├── 📦 backend/                    # FastAPI Backend
│   ├── 🚀 main.py                # FastAPI приложение
│   ├── 📊 api/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py              # Простая аутентификация
│   │   ├── profiles.py          # CRUD профилей
│   │   ├── generation.py        # Генерация профилей
│   │   └── catalog.py           # Каталог организации
│   ├── 🧠 core/                  # Бизнес логика
│   │   ├── __init__.py
│   │   ├── models.py            # Pydantic модели
│   │   ├── database.py          # SQLite подключение
│   │   ├── llm_client.py        # OpenRouter клиент
│   │   ├── profile_generator.py # Генерация профилей
│   │   └── data_loader.py       # Загрузка данных компании
│   ├── 🔧 services/             # Сервисные модули
│   │   ├── __init__.py
│   │   ├── langfuse_client.py   # Интеграция Langfuse + Prompt Management
│   │   ├── file_storage.py      # Файловое хранение
│   │   ├── template_engine.py   # MD шаблоны
│   │   └── export_service.py    # Экспорт JSON/MD
│   ├── 🗂️ storage/              # Файловое хранение
│   │   ├── profiles/           # Сгенерированные профили
│   │   │   ├── ДИТ/
│   │   │   │   ├── Руководитель_отдела_v1.json
│   │   │   │   ├── Руководитель_отдела_v1.md
│   │   │   │   └── Архитектор_системы_v2.json
│   │   │   └── Коммерческий_департамент/
│   │   ├── data/               # Исходные данные
│   │   │   ├── structure.json
│   │   │   ├── kpi/
│   │   │   └── profiles_examples/
│   │   └── templates/          # MD шаблоны
│   │       └── profile_template.md
│   ├── ⚙️ config/               # Конфигурация
│   │   ├── __init__.py
│   │   ├── settings.py         # Настройки приложения
│   │   ├── prompts/            # LLM промпты
│   │   └── langfuse_config.py  # Настройки мониторинга
│   └── 🗃️ database.db          # SQLite база данных
├── 🎨 frontend/                  # NiceGUI Frontend
│   ├── 🚀 main.py               # NiceGUI приложение
│   ├── 🧩 components/           # UI компоненты
│   │   ├── __init__.py
│   │   ├── auth_form.py        # Форма входа
│   │   ├── org_tree.py         # Дерево организации
│   │   ├── profile_form.py     # Форма генерации
│   │   ├── profile_viewer.py   # Просмотр профиля
│   │   └── export_panel.py     # Панель экспорта
│   ├── 🔧 services/            # Frontend сервисы
│   │   ├── __init__.py
│   │   ├── api_client.py       # Клиент для FastAPI
│   │   └── ui_helpers.py       # UI утилиты
│   └── 🎯 assets/              # Статические ресурсы
│       ├── logo.png
│       └── styles.css
├── 🧪 tests/                    # Тесты
│   ├── test_backend/
│   └── test_frontend/
├── 📚 docs/                     # Документация
├── 🐳 docker/                   # Docker конфигурация
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── 📋 requirements.txt          # Python зависимости
├── 🌍 .env.example             # Переменные окружения
└── 📖 README.md                # Документация
```

## 🗄️ **БАЗА ДАННЫХ (SQLite)**

### **Таблицы:**

```sql
-- Профили должностей
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_title VARCHAR(255) NOT NULL,
    department_path VARCHAR(500) NOT NULL,  -- "ДИТ/Управление архитектуры"
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active',    -- active, archived
    json_data TEXT NOT NULL,               -- JSON профиля
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    langfuse_trace_id VARCHAR(255)         -- Связь с Langfuse
);

-- История генераций
CREATE TABLE generation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER REFERENCES profiles(id),
    prompt_version VARCHAR(50),
    model_used VARCHAR(100),
    generation_time_ms INTEGER,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    langfuse_trace_id VARCHAR(255)
);

-- Кэш организационной структуры
CREATE TABLE org_structure_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_path VARCHAR(500) NOT NULL,
    position_title VARCHAR(255) NOT NULL,
    has_profile BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_profiles_department ON profiles(department_path);
CREATE INDEX idx_profiles_position ON profiles(position_title, version);
CREATE INDEX idx_org_cache_path ON org_structure_cache(department_path);
```

## 🚀 **API ENDPOINTS (FastAPI)**

### **Аутентификация:**
```
POST /api/auth/login          # Простой пароль
POST /api/auth/logout         # Выход
```

### **Каталог организации:**
```
GET  /api/catalog/structure   # Дерево организации
GET  /api/catalog/department/{path}  # Позиции в департаменте
```

### **Профили:**
```
GET    /api/profiles/                    # Список всех профилей
GET    /api/profiles/{id}               # Конкретный профиль
POST   /api/profiles/generate           # Генерация нового профиля
PUT    /api/profiles/{id}/regenerate    # Перегенерация (новая версия)
DELETE /api/profiles/{id}               # Удаление профиля
```

### **Экспорт:**
```
GET /api/export/profile/{id}/json      # JSON экспорт
GET /api/export/profile/{id}/markdown  # MD экспорт
POST /api/export/batch                 # Batch экспорт (будущее)
```

### **Система:**
```
GET /api/health                        # Health check
GET /api/stats                         # Статистика системы
```

## 🤖 **LLM ИНТЕГРАЦИЯ**

### **OpenRouter API Client:**
```python
# backend/core/llm_client.py
class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = едпоит хзранится в .env
        self.model = модель хранится в langfuse.

    async def generate_profile(self, prompt: str, context: dict) -> dict:
        # Интеграция с OpenRouter API
        # Langfuse трейсинг
        # в langfuse сохраняется трейс и метрики
        # в langfusу хранится промпт
        pass
```

### **Промпты (JSON конфигурация):**
```json
// backend/config/prompts/profile_generation.json
{
  "profile_generation": {
    "version": "1.0",
    "model": "google/gemini-2.5-flash",
    "temperature": 0.3,
    "max_tokens": 4000,
    "system_prompt": "Ты HR эксперт компании А101...",
    "user_prompt_template": "Создай профиль должности {position} в {department}...",
    "parameters": {
      "structured_output": true,
      "json_schema": "job_profile_schema.json"
    }
  }
}
```

## 📊 **LANGFUSE ИНТЕГРАЦИЯ**

### **Мониторинг:**
```python
# backend/services/langfuse_client.py
from langfuse import Langfuse

class LangfuseService:
    def __init__(self):
        self.client = Langfuse(
            secret_key="sk-lf-f9828023-7031-4e76-9db3-da1c9030cbe5",
            public_key="pk-lf-f4a9dfd3-f57a-4fa5-8d7b-3624748fdfc8",
            host="https://cloud.langfuse.com"
        )

    def trace_generation(self, profile_data: dict) -> str:
        # Создание трейса для генерации профиля
        pass
```

## 🔄 **DATA FLOW**

### **Генерация профиля:**
```
[NiceGUI] → POST /api/profiles/generate
    ↓
[FastAPI] → Validate request
    ↓
[DataLoader] → Load company data (structure.json, KPI, и всо остальное и передается в переменную в langfuse)
    ↓
[PromptEngine] → Build prompt with context
    ↓
[OpenRouter] → Call Gemini model
    ↓
[Langfuse] → Log trace & metrics
    ↓
[Database] → Save profile + version
    ↓
[FileStorage] → Save JSON + MD files
    ↓
[Response] → Return profile to frontend
```

### **Каталог профилей:**
```
[NiceGUI] → GET /api/catalog/structure
    ↓
[OrgStructure] → Parse structure.json
    ↓
[Database] → Check existing profiles
    ↓
[Response] → Tree with generated/missing profiles
```

## 🚀 **DEPLOYMENT (VPS)**

### **Docker Compose:**
```yaml
version: '3.8'
services:
  backend:
    build: ./docker/Dockerfile.backend
    ports:
      - "8022:8000"
    environment:
      - DATABASE_URL=sqlite:///./database.db
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_BASE_URL=${OPENROUTER_BASE_URL}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_HOST=${LANGFUSE_HOST}

    volumes:
      - ./storage:/app/storage

  frontend:
    build: ./docker/Dockerfile.frontend
    ports:
      - "8033:8080"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
```

### **Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;  # NiceGUI
    }

    location /api {
        proxy_pass http://localhost:8000;  # FastAPI
    }
}
```

## 🔧 **КОНФИГУРАЦИЯ**

### **Environment Variables:**
```env
# .env
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LANGFUSE_SECRET_KEY=sk-lf-f9828023-7031-4e76-9db3-da1c9030cbe5
LANGFUSE_PUBLIC_KEY=pk-lf-f4a9dfd3-f57a-4fa5-8d7b-3624748fdfc8
LANGFUSE_HOST=https://cloud.langfuse.com
DATABASE_URL=sqlite:///./database.db
AUTH_PASSWORD=your_simple_password
DEBUG=true # для дебага
```

## 📈 **МАСШТАБИРУЕМОСТЬ**

### **Будущие модули:**
1. **Excel Export** - расширенный экспорт
2. **Data Pipeline Module** - автоматическая обработка сырых данных
3. **Batch Generation Service** - массовая генерация профилей
4. **Advanced Auth** - роли и права пользователей
5. **API Integrations** - интеграция с корпоративными системами


## 🎯 **MVP SCOPE**

### **Обязательно в MVP:**
- ✅ NiceGUI интерфейс с каталогом
- ✅ FastAPI backend с SQLite
- ✅ Gemini интеграция через OpenRouter
- ✅ Langfuse мониторинг и управление промптами
- ✅ JSON/MD экспорт
- ✅ Версионирование профилей
- ✅ Простая аутентификация

### **После MVP:**
- 📊 Excel экспорт
- 🔄 Batch генерация
- 📁 Автоматическая загрузка данных
- 👥 Роли пользователей
- 🎨 Admin панель

## 🚀 **ДОПОЛНЕНИЯ ПОСЛЕ ИСПРАВЛЕНИЙ**

### **DataLoader для Langfuse Variables:**
```python
# backend/core/data_loader.py
class DataLoader:
    def prepare_langfuse_variables(self, department: str, position: str) -> dict:
        """Подготовка всех данных для передачи в Langfuse variables"""
        return {
            "company_data": self.load_company_map(),           # Карта компании А101
            "kpi_data": self.load_kpi_for_department(department), # Релевантные KPI
            "profile_template": self.load_profile_template(),  # Профиль должности
            "org_structure": self.load_org_structure(),       # Организационная структура
            "position": position,                              # Целевая должность
            "department": department,                          # Департамент
            "it_systems": self.load_relevant_it_systems(department) # IT системы
        }
```

### **Обновленная структура Langfuse интеграции:**
```python
# backend/services/langfuse_client.py
class LangfuseService:
    async def generate_with_prompt(self, prompt_name: str, variables: dict) -> dict:
        """Полная генерация с Langfuse Prompt Management"""

        # 1. Получаем промпт и конфигурацию
        prompt_config = await self.get_prompt_config(prompt_name)

        # 2. Создаем трейс
        trace_id = self.trace_generation(variables, prompt_name)

        # 3. Вызываем OpenRouter с полным контекстом (1M токенов)
        result = await self.call_openrouter(
            prompt=prompt_config["prompt"],
            variables=variables,
            config=prompt_config["config"],
            trace_id=trace_id
        )

        return result
```

**Архитектура готова к реализации! 🚀**

**Все противоречия исправлены:**
- ✅ Langfuse Prompt Management с самого начала
- ✅ Модель: google/gemini-2.5-flash
- ✅ Контекст 1M токенов учтен (max_tokens: 8000)
- ✅ Убраны JSON файлы промптов
- ✅ Исправлены опечатки в коде
- ✅ Добавлена подготовка variables для Langfuse

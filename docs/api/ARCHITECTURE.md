# Backend API Architecture

**HR Profile Generator - System Architecture Overview**

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Vue.js SPA  │  │  NiceGUI UI  │  │  Mobile/Desktop Apps     │  │
│  │  (Port 5173) │  │  (Port 8033) │  │  (Future)                │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬────────────────┘  │
└─────────┼──────────────────┼────────────────────┼───────────────────┘
          │                  │                    │
          │ HTTP/JSON        │ HTTP/JSON          │ HTTP/JSON
          │ JWT Bearer       │ JWT Bearer         │ JWT Bearer
          │                  │                    │
┌─────────▼──────────────────▼────────────────────▼───────────────────┐
│                       API Gateway Layer                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              FastAPI Application (Port 8022)                 │   │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │   │
│  │  │   CORS     │  │  Security   │  │  Request Logging     │ │   │
│  │  │ Middleware │  │  Headers    │  │  Middleware          │ │   │
│  │  └────────────┘  └─────────────┘  └──────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼──────────┐ ┌───────▼────────┐ ┌────────▼──────────────┐
│   API Router Layer  │ │  Auth Router   │ │  Static Files Router  │
│                     │ │                │ │                       │
│ /api/generation     │ │ /api/auth      │ │ /static/*             │
│ /api/profiles       │ │                │ │                       │
│ /api/organization   │ │                │ │                       │
│ /api/catalog        │ │                │ │                       │
│ /api/dashboard      │ │                │ │                       │
└─────────┬───────────┘ └────────┬───────┘ └───────────────────────┘
          │                      │
          │                      │
┌─────────▼──────────────────────▼────────────────────────────────────┐
│                      Business Logic Layer                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Core Services                             │   │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐ │   │
│  │  │ Profile        │  │ Organization    │  │ Catalog      │ │   │
│  │  │ Generator      │  │ Cache           │  │ Service      │ │   │
│  │  │                │  │ (567 units)     │  │              │ │   │
│  │  └────────┬───────┘  └────────┬────────┘  └──────┬───────┘ │   │
│  └───────────┼────────────────────┼──────────────────┼─────────┘   │
│              │                    │                  │              │
│  ┌───────────▼────────────────────▼──────────────────▼─────────┐   │
│  │                    Utility Services                          │   │
│  │  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │   Auth     │  │  DOCX    │  │ Markdown │  │  Storage │  │   │
│  │  │  Service   │  │ Service  │  │ Service  │  │  Service │  │   │
│  │  └────────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼──────────┐ ┌───────▼────────┐ ┌────────▼──────────────┐
│  Data Access Layer  │ │  External APIs │ │  File System          │
│                     │ │                │ │                       │
│ ┌─────────────────┐ │ │ ┌────────────┐ │ │ /generated_profiles/  │
│ │ DatabaseManager │ │ │ │ OpenRouter │ │ │  └─ {department}/     │
│ │  (SQLite)       │ │ │ │ (Gemini)   │ │ │     └─ {profile}.json │
│ │                 │ │ │ └────────────┘ │ │     └─ {profile}.md   │
│ │ - users         │ │ │                │ │     └─ {profile}.docx │
│ │ - profiles      │ │ │ ┌────────────┐ │ │                       │
│ │ - sessions      │ │ │ │  Langfuse  │ │ │ /data/                │
│ │ - tasks         │ │ │ │ (Monitor)  │ │ │  └─ profiles.db       │
│ │ - org_cache     │ │ │ └────────────┘ │ │                       │
│ └─────────────────┘ │ │                │ │ /templates/           │
│                     │ │                │ │  └─ prompts/          │
└─────────────────────┘ └────────────────┘ └───────────────────────┘
```

---

## API Request Flow

### Example: Generate Profile Request

```
1. Client Request
   ↓
   POST /api/generation/start
   Headers: Authorization: Bearer {jwt_token}
   Body: { department, position, employee_name }

2. Middleware Chain
   ↓
   Security Middleware → Add security headers
   ↓
   CORS Middleware → Validate origin
   ↓
   Request Logging → Log request details
   ↓
   Auth Middleware → Verify JWT token

3. Router Layer
   ↓
   generation_router.start_generation()
   ↓
   Extract current_user from JWT
   ↓
   Validate request body (Pydantic)

4. Business Logic
   ↓
   Create task_id (UUID)
   ↓
   Store task in _active_tasks (in-memory)
   ↓
   Launch background_generate_profile() via asyncio.create_task()
   ↓
   Return immediate response: { task_id, status: "queued" }

5. Background Processing
   ↓
   Update task status to "processing"
   ↓
   Initialize ProfileGenerator
   ↓
   Load organization data from OrganizationCache
   ↓
   Build LLM prompt with company data
   ↓
   Call OpenRouter API (Gemini 2.5 Flash)
   ↓
   Parse JSON response
   ↓
   Validate profile structure
   ↓
   Generate export files (JSON, MD, DOCX)
   ↓
   Save to database (profiles table)
   ↓
   Save files to /generated_profiles/{dept}/
   ↓
   Update task status to "completed"
   ↓
   Store result in _task_results

6. Client Polling
   ↓
   GET /api/generation/{task_id}/status (every 2s)
   ↓
   Return: { task: {...}, result: {...} }
   ↓
   When status=completed, client gets final result
```

---

## Data Flow Diagram

```
┌──────────────┐
│  Frontend    │
│  (Vue.js)    │
└──────┬───────┘
       │
       │ 1. POST /api/auth/login
       ├──────────────────────────────────┐
       │                                   ▼
       │                          ┌────────────────┐
       │                          │  AuthService   │
       │                          │  - Verify      │
       │                          │  - Create JWT  │
       │                          │  - Create      │
       │                          │    Session     │
       │                          └────────┬───────┘
       │                                   │
       │ 2. { access_token }              │ Store in DB
       │◀──────────────────────────────────┤
       │                                   ▼
       │                          ┌────────────────┐
       │                          │   Database     │
       │                          │  - users       │
       │                          │  - sessions    │
       │                          └────────────────┘
       │
       │ 3. POST /api/generation/start
       │    (with JWT token)
       ├──────────────────────────────────┐
       │                                   ▼
       │                          ┌────────────────────┐
       │                          │  GenerationRouter  │
       │                          │  - Validate JWT    │
       │                          │  - Create task     │
       │                          └────────┬───────────┘
       │                                   │
       │ 4. { task_id }                   │ Launch async
       │◀──────────────────────────────────┤
       │                                   ▼
       │                          ┌─────────────────────┐
       │                          │ ProfileGenerator    │
       │                          │  1. Load org data   │
       │                          │  2. Build prompt    │
       │                          │  3. Call LLM        │
       │                          │  4. Parse response  │
       │                          │  5. Save files      │
       │                          │  6. Save to DB      │
       │                          └──┬────────┬─────────┘
       │                             │        │
       │ 5. Poll: GET /status       │        │
       │◀───────────────────────────┤        │
       │    { progress: 30% }        │        │
       │                             │        ▼
       │                             │   ┌──────────────┐
       │                             │   │  OpenRouter  │
       │                             │   │   (Gemini)   │
       │                             │   └──────┬───────┘
       │                             │          │
       │                             │          │ LLM Response
       │ 6. Poll: GET /status       │          │
       │◀───────────────────────────┤◀─────────┘
       │    { progress: 100%,        │
       │      result: {...} }        │
       │                             │
       │ 7. GET /result              │
       ├─────────────────────────────┤
       │                             ▼
       │                    ┌────────────────┐
       │                    │   Database     │
       │                    │  - profiles    │
       │                    │  - tasks       │
       │                    └────────────────┘
       │
       │ 8. { profile_data }
       │◀──────────────────────────────────
       │
       │ 9. GET /download/docx
       ├──────────────────────────────────┐
       │                                   ▼
       │                          ┌────────────────┐
       │                          │  StorageService│
       │                          │  - Locate file │
       │                          │  - Stream blob │
       │                          └────────┬───────┘
       │                                   │
       │ 10. File download                │ Read from FS
       │◀──────────────────────────────────┤
       │                                   ▼
       │                          ┌────────────────┐
       │                          │  File System   │
       │                          │  /generated_   │
       │                          │   profiles/    │
       │                          └────────────────┘
```

---

## Database Schema

```sql
-- Users & Authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,         -- bcrypt + SHA256
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,                 -- UUID session ID
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    user_agent TEXT,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Profile Data
CREATE TABLE profiles (
    id TEXT PRIMARY KEY,                 -- UUID profile ID
    department TEXT NOT NULL,
    position TEXT NOT NULL,
    employee_name TEXT,

    profile_data TEXT NOT NULL,          -- JSON profile content
    metadata_json TEXT NOT NULL,         -- Generation metadata

    generation_time_seconds REAL NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,

    validation_score REAL DEFAULT 0.0,   -- 0.0-1.0
    completeness_score REAL DEFAULT 0.0, -- 0.0-1.0

    created_by INTEGER,                  -- User ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    status TEXT DEFAULT 'completed',     -- completed, failed, processing, archived

    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Async Tasks
CREATE TABLE generation_tasks (
    id TEXT PRIMARY KEY,                 -- UUID task ID
    department TEXT NOT NULL,
    position TEXT NOT NULL,
    employee_name TEXT,
    generation_params TEXT,              -- JSON params

    status TEXT DEFAULT 'pending',       -- pending, processing, completed, failed, cancelled
    progress INTEGER DEFAULT 0,          -- 0-100
    current_step TEXT,

    result_profile_id TEXT,              -- Profile ID when completed
    error_message TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,

    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (result_profile_id) REFERENCES profiles(id)
);

-- Organization Cache
CREATE TABLE organization_cache (
    id INTEGER PRIMARY KEY,
    cache_key TEXT NOT NULL UNIQUE,
    cache_type TEXT NOT NULL,            -- department_structure, kpi_mapping, positions

    data_json TEXT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    access_count INTEGER DEFAULT 0,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_profiles_department ON profiles(department);
CREATE INDEX idx_profiles_position ON profiles(position);
CREATE INDEX idx_profiles_created_at ON profiles(created_at);
CREATE INDEX idx_profiles_status ON profiles(status);
CREATE INDEX idx_tasks_status ON generation_tasks(status);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
```

---

## Service Layer Architecture

### ProfileGenerator (Core Service)

```python
class ProfileGenerator:
    """
    Main service for AI-powered profile generation.

    Workflow:
    1. Load organization data from cache
    2. Extract department context
    3. Build structured prompt with examples
    4. Call LLM (Gemini 2.5 Flash)
    5. Parse and validate JSON response
    6. Generate export files (JSON, MD, DOCX)
    7. Save to database and file system
    """

    def __init__(self):
        self.llm_client = LLMClient()
        self.data_loader = DataLoader()
        self.organization_cache = organization_cache
        self.storage_service = StorageService()

    async def generate_profile(
        self,
        department: str,
        position: str,
        employee_name: Optional[str] = None,
        temperature: float = 0.1,
        save_result: bool = True,
        profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Extract organization context
        # 2. Build LLM prompt
        # 3. Call OpenRouter API
        # 4. Validate response
        # 5. Save results
        # 6. Return profile data + metadata
```

### OrganizationCache (Performance Layer)

```python
class OrganizationCache:
    """
    Centralized cache for organizational structure.

    Performance Improvement: 75x speedup (3ms vs 225ms)

    Features:
    - Path-based indexing (avoids duplicate names)
    - 567 business units cached in-memory
    - 1689 positions with full metadata
    - Hierarchical structure with parent/child relationships
    """

    def __init__(self):
        self._business_units: Dict[str, Dict] = {}
        self._positions_by_path: Dict[str, List] = {}
        self._loaded = False

    def get_all_business_units_with_paths(self) -> Dict[str, Dict]:
        # Returns all 567 units indexed by full path
        # Example: "Блок ОД/ДИТ/Отдел разработки"

    def find_by_path(self, path: str) -> Optional[Dict]:
        # Fast O(1) lookup by path
```

### CatalogService (API Layer)

```python
class CatalogService:
    """
    API service for browsing organizational catalog.

    Provides:
    - Department listing and search
    - Position search by department
    - Hierarchical structure navigation
    """

    def __init__(self):
        self.organization_cache = organization_cache

    def get_departments(self, force_refresh: bool = False) -> List[Dict]:
        # Returns all departments from cache

    def get_searchable_items(self) -> List[Dict]:
        # Returns all 567 units for autocomplete/search
```

### AuthService (Security Layer)

```python
class AuthService:
    """
    Authentication and authorization service.

    Features:
    - JWT token generation and validation
    - Password hashing (bcrypt + SHA256)
    - Session management
    - User verification
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.pwd_context = CryptContext(schemes=["bcrypt"])

    def create_access_token(self, user_data: Dict) -> str:
        # Generate JWT token with HS256 algorithm
        # Expires in 24 hours (configurable)

    def verify_token(self, token: str) -> Optional[Dict]:
        # Decode and validate JWT token
```

---

## Security Architecture

### Authentication Flow

```
1. User Login
   ↓
   Username + Password (plaintext)
   ↓
2. Pre-hash with SHA256
   ↓
   SHA256(password) → prehashed_password
   ↓
3. Hash with bcrypt
   ↓
   bcrypt.hash(prehashed_password) → stored_hash
   ↓
4. Compare with DB
   ↓
   bcrypt.verify(prehashed_password, stored_hash) → True/False
   ↓
5. Generate JWT
   ↓
   JWT({ user_id, username, exp: now + 24h }) → access_token
   ↓
6. Return Token
   ↓
   { access_token, user_info }
```

### Request Authorization

```
1. Client Request
   ↓
   Headers: Authorization: Bearer {token}
   ↓
2. Auth Middleware
   ↓
   Extract token from header
   ↓
3. Verify JWT
   ↓
   jwt.decode(token, secret_key, algorithms=["HS256"])
   ↓
4. Check Expiration
   ↓
   if exp < now → 401 Unauthorized
   ↓
5. Load User Data
   ↓
   { user_id, username, ... }
   ↓
6. Inject into Request
   ↓
   current_user available in endpoint
```

### Security Headers

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Performance Optimizations

### 1. Organization Cache (In-Memory)

**Before**: 225ms per lookup (file read + parse)
**After**: 3ms per lookup (in-memory dict)
**Improvement**: 75x faster

### 2. Database Indexes

```sql
-- Speeds up profile listing by department
CREATE INDEX idx_profiles_department ON profiles(department);

-- Speeds up profile listing by date
CREATE INDEX idx_profiles_created_at ON profiles(created_at);

-- Speeds up status filtering
CREATE INDEX idx_profiles_status ON profiles(status);

-- Speeds up task queries
CREATE INDEX idx_tasks_status ON generation_tasks(status);
```

### 3. Thread-Safe Database Connections

**Problem**: SQLite connections cannot be shared across threads
**Solution**: threading.local() storage for per-thread connections

```python
class DatabaseManager:
    def __init__(self, db_path: str):
        self._local = threading.local()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(db_path)
        return self._local.connection
```

### 4. Async Profile Generation

**Pattern**: Fire-and-forget with asyncio.create_task()

```python
# Don't wait for generation to complete
asyncio.create_task(background_generate_profile(task_id, request, user_id))

# Return immediately
return { "task_id": task_id, "status": "queued" }
```

### 5. Pagination

**Pattern**: LIMIT + OFFSET for efficient large dataset handling

```sql
SELECT * FROM profiles
WHERE department LIKE ?
ORDER BY created_at DESC
LIMIT ? OFFSET ?;
```

---

## Scaling Considerations

### Current Architecture (Single Instance)

- **Database**: SQLite (file-based, single writer)
- **Task Queue**: In-memory dict (lost on restart)
- **Cache**: In-memory (per-instance)
- **Max Concurrent Tasks**: Limited by asyncio event loop

### Production Scaling (Recommendations)

#### 1. Database Migration

```
SQLite → PostgreSQL
- Multi-writer support
- Better concurrent performance
- Connection pooling
- Full-text search
```

#### 2. Task Queue

```
In-Memory → Redis + Celery
- Persistent task storage
- Distributed workers
- Priority queues
- Retry mechanisms
```

#### 3. Caching

```
In-Memory → Redis
- Shared cache across instances
- Distributed caching
- Cache invalidation
- TTL support
```

#### 4. Load Balancing

```
┌─────────┐
│ Nginx   │ ← Load Balancer
└────┬────┘
     │
     ├─→ FastAPI Instance 1
     ├─→ FastAPI Instance 2
     └─→ FastAPI Instance 3
         ↓
    ┌──────────┐
    │ Redis    │ ← Shared Cache + Queue
    └──────────┘
         ↓
    ┌──────────┐
    │PostgreSQL│ ← Shared Database
    └──────────┘
```

#### 5. File Storage

```
Local FS → S3 / MinIO
- Distributed file storage
- Scalable storage
- CDN integration
- Backup/versioning
```

---

## Monitoring & Observability

### Current Setup

1. **Logging**: Python logging module
   - Console output (development)
   - File output (app.log)
   - Request/response logging

2. **LLM Monitoring**: Langfuse (optional)
   - Token usage tracking
   - Trace generation requests
   - Cost analysis
   - Quality monitoring

### Production Monitoring (Recommendations)

1. **APM**: Sentry or Datadog
   - Error tracking
   - Performance monitoring
   - Real-time alerts

2. **Metrics**: Prometheus + Grafana
   - Request rate
   - Response time
   - Error rate
   - Task queue depth
   - LLM token usage

3. **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
   - Centralized logs
   - Search and analysis
   - Dashboards

---

## API Design Patterns

### 1. Resource-Based URLs

```
✅ Good:
/api/profiles/{id}
/api/generation/{task_id}/status

❌ Bad:
/api/getProfile?id=123
/api/checkTaskStatus?taskId=456
```

### 2. HTTP Methods

```
GET    /api/profiles     → List profiles
POST   /api/profiles     → Create profile
GET    /api/profiles/{id}→ Get profile
PUT    /api/profiles/{id}→ Update profile
DELETE /api/profiles/{id}→ Delete/archive profile
```

### 3. Standard Response Format

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed",
  "timestamp": "2025-10-25T10:00:00Z"
}
```

### 4. Error Response Format

```json
{
  "success": false,
  "error": "Resource not found",
  "details": {
    "code": "RESOURCE_NOT_FOUND",
    "resource": "profile",
    "resource_id": "abc123"
  },
  "timestamp": "2025-10-25T10:00:00Z"
}
```

### 5. Async Operations

```
Pattern: POST → Poll → GET Result

1. POST /api/generation/start
   → { task_id, status: "queued" }

2. GET /api/generation/{task_id}/status
   → { task: { status, progress }, result: null }

3. GET /api/generation/{task_id}/result
   → { profile, metadata }
```

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | Web framework |
| **Language** | Python | 3.11+ | Backend language |
| **Database** | SQLite | 3.x | Data storage |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM |
| **Auth** | JWT (python-jose) | Latest | Authentication |
| **Password** | bcrypt (passlib) | Latest | Password hashing |
| **LLM** | OpenRouter API | - | AI integration |
| **Model** | Gemini 2.5 Flash | - | Profile generation |
| **Monitoring** | Langfuse | Latest | LLM observability |
| **Validation** | Pydantic | 2.5+ | Data validation |
| **HTTP Client** | httpx | Latest | Async HTTP |
| **File Export** | python-docx | Latest | DOCX generation |
| **Markdown** | Custom | - | MD generation |
| **Server** | Uvicorn | Latest | ASGI server |
| **CORS** | FastAPI middleware | - | Cross-origin |
| **Static Files** | FastAPI StaticFiles | - | File serving |

---

## File Structure

```
backend/
├── api/                    # API endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── generation.py      # Profile generation endpoints
│   ├── profiles.py        # Profile CRUD endpoints
│   ├── organization.py    # Organization catalog (path-based)
│   ├── catalog.py         # Catalog (legacy)
│   ├── dashboard.py       # Dashboard statistics
│   └── middleware/        # Custom middleware
│       ├── auth_middleware.py
│       ├── logging_middleware.py
│       └── security_middleware.py
├── core/                   # Business logic
│   ├── profile_generator.py  # Main generation logic
│   ├── llm_client.py         # OpenRouter API client
│   ├── organization_cache.py # Organization data cache
│   ├── data_loader.py        # Data loading utilities
│   ├── storage_service.py    # File storage management
│   ├── docx_service.py       # DOCX generation
│   ├── markdown_service.py   # Markdown generation
│   └── config.py             # Configuration management
├── services/               # Service layer
│   ├── auth_service.py    # Authentication service
│   └── catalog_service.py # Catalog service
├── models/                 # Data models
│   ├── schemas.py         # Pydantic models (API)
│   └── database.py        # SQLAlchemy models (DB)
├── utils/                  # Utilities
│   ├── validators.py      # Input validation
│   ├── exceptions.py      # Custom exceptions
│   └── exception_handlers.py  # Global error handlers
├── static/                 # Static files
└── main.py                # FastAPI application entry

data/
├── profiles.db            # SQLite database
└── organization/          # Organization data files

generated_profiles/
└── {department}/
    ├── {profile}.json
    ├── {profile}.md
    └── {profile}.docx

templates/
└── prompts/              # LLM prompt templates
    └── profile_generation.json
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-25
**Author**: Claude (Backend System Architect)

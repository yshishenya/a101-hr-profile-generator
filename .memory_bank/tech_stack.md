# Technology Stack and Conventions

**Last Updated**: 2025-10-28
**Status**: Current (Post Week 6)

---

## 🏗️ Core Architecture

### Backend
- **Language**: Python 3.11+ (modern, type-safe approach)
- **Framework**: FastAPI (async web framework)
- **Asynchronous Runtime**: asyncio with async/await patterns
- **Package Management**: pip + requirements.txt
- **Database**: SQLite (file-based SQL database)
- **LLM Integration**: OpenRouter API (Gemini 2.5 Flash) + Langfuse (observability)

### Frontend (Vue.js 3 MVP)
- **Framework**: Vue.js 3.5+ (Composition API with `<script setup>`)
- **Language**: TypeScript 5.7+ (strict mode enabled)
- **UI Framework**: Vuetify 3.7+ (Material Design components)
- **State Management**: Pinia 2.2+ (Composition API style)
- **Routing**: Vue Router 4.4+
- **Build Tool**: Vite 6.0+
- **HTTP Client**: Axios 1.7+
- **Package Management**: npm
- **Testing**: Vitest 2.1+ (unit/component), Playwright 1.49+ (E2E)
- **Code Quality**: ESLint 9+ + Prettier 3+

### DevOps
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (serves Vue frontend + proxies to FastAPI)
- **Environment**: .env files for configuration
- **Git**: Conventional Commits standard

---

## 📂 Project Structure

```
HR/
├── backend/                    # FastAPI Backend (Python)
│   ├── api/                    # API endpoints (REST)
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── catalog.py          # Organization catalog
│   │   ├── dashboard.py        # Statistics and metrics
│   │   ├── generation.py       # Profile generation
│   │   ├── organization.py     # Organization structure
│   │   └── profiles.py         # Profile CRUD + bulk operations
│   ├── core/                   # Business logic
│   │   ├── ai_profile_generator.py
│   │   ├── data_mapper.py
│   │   ├── docx_generator.py
│   │   └── profile_validator.py
│   ├── models/                 # Data models
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas (28+ response models)
│   ├── services/               # Service layer
│   │   ├── catalog_service.py  # Organization catalog (LRU cache)
│   │   ├── docx_service.py
│   │   ├── markdown_service.py
│   │   └── storage_service.py
│   ├── tools/                  # Utilities and tools
│   ├── utils/                  # Helper functions
│   │   ├── errors.py           # Custom exceptions (5 classes)
│   │   └── position_utils.py
│   ├── main.py                 # FastAPI application entry point
│   └── README.md
│
├── frontend-vue/               # Vue.js 3 Frontend (TypeScript)
│   ├── src/
│   │   ├── assets/             # Static assets
│   │   ├── components/         # Vue components
│   │   │   ├── common/         # BaseCard, ConfirmDeleteDialog
│   │   │   ├── layout/         # AppLayout, AppHeader
│   │   │   └── profiles/       # 26 profile-related components
│   │   ├── composables/        # Composition API reusable logic
│   │   │   ├── useAnalytics.ts     # Analytics tracking
│   │   │   ├── useProfileVersions.ts
│   │   │   ├── useSearch.ts        # Tree search functionality
│   │   │   ├── useTaskStatus.ts    # Polling mechanism
│   │   │   └── useTheme.ts
│   │   ├── router/             # Vue Router configuration
│   │   ├── services/           # API clients
│   │   │   ├── api.ts          # Axios instance + interceptors
│   │   │   ├── catalog.service.ts
│   │   │   ├── dashboard.service.ts
│   │   │   ├── generation.service.ts
│   │   │   └── profile.service.ts
│   │   ├── stores/             # Pinia stores
│   │   │   ├── auth.ts
│   │   │   ├── catalog.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── generator.ts
│   │   │   └── profiles/       # Modularized (7 files)
│   │   ├── types/              # TypeScript type definitions
│   │   │   ├── analytics.ts
│   │   │   ├── api.ts
│   │   │   ├── index.ts
│   │   │   ├── profile.ts
│   │   │   └── version.ts
│   │   ├── utils/              # Utility functions
│   │   │   ├── errors.ts       # Error handling helpers
│   │   │   ├── exportHelper.ts # Bulk download (JSZip)
│   │   │   ├── formatters.ts   # Date, number formatters
│   │   │   └── logger.ts
│   │   ├── views/              # Route components
│   │   │   ├── LoginView.vue
│   │   │   └── UnifiedProfilesView.vue  # Main workspace
│   │   ├── App.vue
│   │   ├── main.ts
│   │   └── style.css
│   ├── tests/                  # Unit tests (Vitest)
│   │   ├── components/         # Component tests
│   │   └── utils/              # Utility tests
│   ├── e2e/                    # E2E tests (Playwright)
│   │   ├── profile-versioning.spec.ts
│   │   └── README.md
│   ├── .eslintrc.cjs           # ESLint config
│   ├── .prettierrc.json        # Prettier config
│   ├── package.json            # npm dependencies
│   ├── playwright.config.ts    # Playwright config
│   ├── tsconfig.json           # TypeScript config
│   ├── vite.config.ts          # Vite config
│   └── vitest.config.ts        # Vitest config
│
├── data/                       # Data files and SQLite database
│   ├── profiles.db             # Main database
│   └── organization.json       # Organization structure
│
├── templates/                  # JSON schemas and prompts
│   ├── profile_schema.json
│   └── prompts/                # Langfuse-managed prompts
│
├── tests/                      # Backend tests
│   ├── integration/
│   ├── unit/
│   │   ├── test_catalog_service.py  # 15 tests
│   │   └── test_schemas.py          # 30 tests
│   └── conftest.py
│
├── scripts/                    # Utility scripts
├── .memory_bank/               # Memory Bank (Claude Code knowledge base)
├── docs/                       # Documentation (208 files)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt            # Backend Python dependencies
├── .env.example
├── .gitignore
├── CLAUDE.md                   # Claude Code instructions
└── README.md
```

---

## 🐍 Backend: Python + FastAPI

### Type Safety
- **Type Hints**: typing module for all function signatures
- **Static Analysis**: mypy for compile-time type checking
- **Pydantic**: Runtime data validation and settings management
- **NO `Any` types**: All types must be explicitly defined

### Code Quality Tools
- **black**: Code formatting (line length: 100 characters)
- **ruff**: Fast Python linter
- **mypy**: Static type checker
- **pre-commit**: Git hooks for automated checks

### Testing Framework
- **pytest**: Primary testing framework
- **pytest-asyncio**: For testing async code
- **pytest-cov**: Code coverage reporting
- **Minimum Coverage**: 80%

### Key Dependencies
```txt
# Web Framework
fastapi>=0.104.1
uvicorn[standard]>=0.24.0

# Data Validation
pydantic>=2.5.0
pydantic-settings>=2.0.0

# Async HTTP
httpx>=0.27.0

# Database
sqlalchemy>=2.0.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt==4.1.3
python-multipart>=0.0.6

# Data Processing
pandas>=2.1.0
openpyxl>=3.1.0
python-docx>=1.1.0

# LLM & Monitoring
langfuse
openai>=1.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

---

## ⚡ Frontend: Vue.js 3 + TypeScript

### TypeScript Strict Mode (MANDATORY)
- **NO `any` types allowed** - TypeScript strict mode enabled
- **Type safety**: 100% compliance required
- **Error handling**: `catch (error: unknown)` pattern mandatory

### Vue 3 Composition API
- **`<script setup>` only** - NO Options API
- **Composables**: Reusable logic extracted to composables/
- **Type safety**: All props/emits typed with TypeScript
- **File size limits**: Components <300 lines, Stores <500 lines

### Code Quality
- **ESLint**: 0 errors, 0 warnings (100% clean)
- **Prettier**: Auto-formatting on save
- **TypeScript**: `vue-tsc` type checking passing
- **Tests**: 80%+ coverage required

### Key Dependencies
```json
{
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.4.5",
    "pinia": "^2.2.6",
    "vuetify": "^3.7.4",
    "axios": "^1.12.2",
    "@mdi/font": "^7.4.47",
    "@tanstack/vue-virtual": "^3.13.12",
    "dompurify": "^3.2.2",
    "js-cookie": "^3.0.5",
    "jszip": "^3.10.1",
    "file-saver": "^2.0.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "vite": "^6.0.3",
    "typescript": "~5.7.2",
    "vitest": "^2.1.8",
    "@playwright/test": "^1.49.1",
    "eslint": "^9.17.0",
    "prettier": "^3.4.2",
    "@vue/test-utils": "^2.4.6",
    "@testing-library/vue": "^8.1.0",
    "happy-dom": "^16.8.0"
  }
}
```

### Component Architecture
```
Views (Route Components)
  ↓ uses
Components (Reusable UI)
  ↓ uses
Stores (State Management)
  ↓ uses
Services (API Clients)
  ↓ calls
Backend API
```

### State Management (Pinia)
- **Composition API style**: `setup()` function pattern
- **Modular stores**: Large stores split into modules (profiles/ has 7 files)
- **Type safety**: All state, getters, actions fully typed

### Testing Strategy
- **Unit Tests**: Vitest for utils, composables, stores (207 tests, 100% passing)
- **Component Tests**: @vue/test-utils + @testing-library/vue
- **E2E Tests**: Playwright (22 scenarios)
- **Coverage**: 80%+ required for new code

---

## 🔒 Authentication & Security

### Backend
- **JWT tokens**: python-jose for token generation
- **Password hashing**: passlib with bcrypt
- **Token expiration**: Configurable via environment
- **Secure headers**: CORS configured for production

### Frontend
- **Token storage**: HTTP-only cookies (secure)
- **Axios interceptors**: Auto-attach tokens
- **Router guards**: Protected routes check authentication
- **XSS protection**: DOMPurify for sanitizing HTML

---

## 🗄️ Database

### SQLite
- **File-based**: Simple deployment, no separate DB server
- **ORM**: SQLAlchemy 2.0+
- **Connection pooling**: For performance
- **Schema management**: `db_manager.create_schema()`

### Key Tables
- `profiles` - Generated profile documents
- `users` - User accounts
- `generation_tasks` - Async profile generation status
- `profile_versions` - Version history

---

## 🚀 API Architecture

### REST API (FastAPI)
- **BaseResponse pattern**: All endpoints return consistent format
  ```json
  {
    "success": boolean,
    "timestamp": datetime,
    "message": optional string,
    "data": { ... }
  }
  ```
- **28+ Pydantic response models** in `backend/models/schemas.py`
- **Authentication**: JWT Bearer tokens
- **CORS**: Configured for Vue.js frontend
- **Documentation**: Auto-generated OpenAPI/Swagger at `/docs`

### Key Endpoints
- **Auth**: `/api/auth/*` - Login, logout, token refresh
- **Catalog**: `/api/organization/*` - Organization structure
- **Dashboard**: `/api/dashboard/*` - Statistics
- **Generation**: `/api/generation/*` - Profile generation
- **Profiles**: `/api/profiles/*` - CRUD + bulk operations

---

## 🔄 Asynchronous Patterns (CRITICAL)

**All I/O operations MUST be asynchronous:**

### HTTP Requests
```python
import httpx

async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
```

### File Operations
```python
import aiofiles

async def read_file_async(path: str) -> str:
    async with aiofiles.open(path, mode='r') as f:
        return await f.read()
```

---

## ⛔ Prohibited Practices

### Backend (Python)
1. ❌ **Synchronous I/O in async code** - Use httpx, aiofiles
2. ❌ **Using `Any` type hints** - Specify concrete types
3. ❌ **Storing secrets in code** - Use .env files
4. ❌ **Raw SQL without parameterization** - SQL injection risk
5. ❌ **Empty exception handlers** - Always log and handle properly

### Frontend (Vue.js/TypeScript)
1. ❌ **Using `any` types** - TypeScript strict mode enabled
2. ❌ **Options API** - Only Composition API with `<script setup>`
3. ❌ **Importing Services in Components** - Use Stores
4. ❌ **Files >300 lines (components) or >500 lines (stores)**
5. ❌ **Skipping tests** - 80%+ coverage required
6. ❌ **Creating components without checking Component Library**

---

## 🧪 Testing Standards

### Backend
```python
import pytest

@pytest.mark.asyncio
async def test_example():
    """Test with arrange-act-assert pattern."""
    # Arrange
    expected = {"result": "success"}

    # Act
    result = await async_function()

    # Assert
    assert result == expected
```

### Frontend
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('Component', () => {
  it('should render correctly', () => {
    const wrapper = mount(Component)
    expect(wrapper.text()).toContain('Expected')
  })
})
```

---

## 📦 Performance Optimization

### Backend
1. **LRU Cache**: `@lru_cache(maxsize=1024)` for expensive computations
2. **Connection pooling**: Database and HTTP clients
3. **Async operations**: All I/O operations non-blocking
4. **Batch operations**: Process multiple items efficiently

### Frontend
1. **Virtual scrolling**: `@tanstack/vue-virtual` for large lists (1000+ items)
2. **Lazy loading**: Components loaded on demand
3. **Debouncing**: Search inputs debounced (300ms)
4. **Memoization**: Computed properties for expensive calculations

---

## 🔄 Git Workflow

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring

### Commit Messages (Conventional Commits)
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance

**Example**: `feat(frontend): add bulk download functionality`

---

## 📚 Documentation Standards

### Code Documentation
- **Python**: Docstrings (Google style) for all functions
- **TypeScript**: JSDoc comments for complex logic
- **Components**: Props/events documented with types

### Project Documentation
- **Memory Bank** (`.memory_bank/`): Single source of truth
- **Implementation docs** (`docs/implementation/`): Feature specs
- **API docs**: Auto-generated from FastAPI
- **Testing docs**: Test plans and reports

---

**Version Control**: Git with Conventional Commits
**CI/CD**: Manual (planned automation in Week 7+)
**Deployment**: Docker + Docker Compose
**Monitoring**: Langfuse for LLM observability

---

**Note**: This stack reflects the state after Week 6 completion (2025-10-28). Vue.js 3 MVP migration successfully completed with production-ready code quality.

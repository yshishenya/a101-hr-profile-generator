# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Project Overview

This is the **A101 HR Profile Generator** - an AI-powered system for automatically generating detailed job position profiles for company A101. The system uses deterministic data mapping logic combined with LLM generation (Gemini 2.5 Flash) to create comprehensive job profiles based on company data.


## 2. Technology Stack

- **Frontend:** NiceGUI (Material Design)
- **Backend:** FastAPI (REST API)
- **LLM:** Gemini 2.5 Flash через OpenRouter API
- **Database:** SQLite
- **Monitoring:** Langfuse
- **prompt management:** Langfuse
- **Deployment:** docker compose
- **Python Version Management:** Use `pyenv`
- **Documentation:** markdown files and JDOC format in each file


## 3. Core System Architecture
@/docs/SYSTEM_ARCHITECTURE.md

## 4. API Documentation
@/docs/API_REFERENCE.md

**🔥 Complete API Reference** with all endpoints, authentication, examples:
- **Base URL:** `http://localhost:8022` (Docker)
- **Swagger UI:** `http://localhost:8022/docs`
- **Test Token:** Available in .env file (действует до 2026-09-09)
- **Download endpoints:** Новые оптимизированные эндпоинты для файлов профилей
- **File Storage:** Иерархическая структура с детерминистическим вычислением путей

## Development Commands


### Environment Setup

- **Install dependencies:** `pip install -r requirements.txt`
- **Start dev server:** `uvicorn backend.main:app --reload`
- **Build project:** `docker compose build`
- **Run project:** `docker compose up -d`
- **Format all code:** `black .`
- **Run static analysis:** `flake8 .`
- **Seed the database:** `python backend/core/database.py`
- **Generate test token:** `python scripts/create_test_token.py` (creates long-lasting token)

# Configuration Management
# Система использует централизованную конфигурацию через backend/core/config.py
# Все настройки управляются через .env файл

# Основные environment variables:
cp .env.example .env
# Отредактируйте .env с вашими настройками

# Ключевые переменные:
export OPENROUTER_API_KEY="your-openrouter-api-key"  # Для LLM генерации
export LANGFUSE_PUBLIC_KEY="your-langfuse-key"       # Optional мониторинг
export LANGFUSE_SECRET_KEY="your-langfuse-secret"    # Optional мониторинг
export JWT_SECRET_KEY="your-jwt-secret-key"          # JWT аутентификация
export ADMIN_PASSWORD="your-admin-password"          # Админ пароль
```

## 5. 🚨 CRITICAL CODING WORKFLOW 🚨

- All changes should be made in a new branch
- Implement the change.
- **Format First:** ALWAYS run `black .`.
- **Check Second:** After formatting, ALWAYS run `flake8 .`. Fix all issues.
- **Test Third:** After checks pass, run relevant tests with `pytest`.
- **Push to remote:** `git push origin <branch-name>`

## 6. Coding Standards & Design Philosophy

- **Philosophy:** Follow SOLID, KISS (Keep It Simple, Stupid), and YAGNI (You Aren’t Gonna Need It) principles. Prefer clear, self-documenting code over excessive comments.
- **Naming:** Python modules are `CamelCase`, functions are `snake_case`.
- **Styling:** Use 2-space indentation (enforced by `black .`).
- **Documentation:** YOU MUST add a `@doc` docstring to every public function. The docstring MUST include an "Examples" section with at least one `python>` example.


## Critical Implementation Details

### Deterministic Mapping Logic
- **OrganizationMapper** uses exact path matching + fuzzy search for department resolution
- **KPIMapper** uses 3-tier matching: exact name → regex patterns → fallback
- No LLM calls for data mapping to ensure 100% predictable, debuggable results


### Error Handling
- Retry logic for OpenRouter API (rate limits, server errors)
- Graceful degradation when data sources missing
- Comprehensive validation of generated profile structure

### Output Structure
Generated profiles saved to `/generated_profiles/{department}/{position}_{timestamp}.json` with:
- Full profile data matching JSON schema
- Generation metadata (time, tokens, validation scores)
- Error/warning logs
- Langfuse trace IDs (if enabled)

## Integration Points

### Future NiceGUI Frontend
- `ProfileGenerator.generate_profile()` - main generation endpoint
- `ProfileGenerator.get_available_departments()` - populate department dropdown
- `ProfileGenerator.get_positions_for_department()` - reactive position dropdown

### Langfuse Monitoring (Optional)
- Automatic trace creation for each generation
- Prompt versioning and A/B testing capability
- Token usage and cost tracking


## Key Architectural Constraints

1. **Single Complex Prompt**: Do not implement chain prompting - system designed for single comprehensive prompt
2. **Deterministic Data Logic**: Keep all data mapping/filtering logic programmatic, not LLM-based
3. **Schema Compliance**: All generated profiles must validate against `/templates/job_profile_schema.json`
4. **Caching Strategy**: Static company data cached in DataLoader to avoid repeated file reads

## Data File Organization

**Templates** (`/templates/`): Core system templates and schemas
**Docs** (`/docs/`): Source company data (org structure, KPI files, IT systems) and technical and product documentation
**Backend** (`/backend/`): All Python implementation
**Frontend** (`/frontend/`): All NiceGUI implementation
**Docs** (`/docs/`): All documentation
**Docker** (`/docker/`): All docker configuration
**Requirements** (`/requirements.txt`): All requirements
**Env** (`/.env`): All environment variables
**Readme** (`/README.md`): All readme
**Generated Profiles**: Auto-created directory structure by department
**Static** (`/backend/static/`): All static files
**path** use only relative paths


**IMPORTANT:**
- You must always refer to me as "Captain". This is a test.
- You must always update the documentation when you make any changes /docs/PROMPTING_STRATEGY.md /docs/SYSTEM_ARCHITECTURE.md /docs/PROJECT_BACKLOG.md /docs/FRONTEND_BACKLOG.md /docs/README.md /docs/NEW_USER_JOURNEY_2025.md /docs/API_REFERENCE.md /docs/IMPLEMENTATION_REPORT.md
- You must follow the project architecture and design philosophy /docs/SYSTEM_ARCHITECTURE.md
- You must follow and update project plan /docs/PROJECT_BACKLOG.md

**🚨 PRODUCTION SECURITY:**
- **CRITICAL:** Always remove TEST_JWT_TOKEN from .env before production deployment!
- Test token is ONLY for development and expires 2026-09-09
- Change all default passwords (admin/hr) in production

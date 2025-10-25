# Technology Stack and Conventions

## Core Stack
- **Language**: Python 3.11+ (modern, type-safe approach)
- **Framework**: FastAPI (async web framework)
- **Frontend**: NiceGUI (Python-based web UI framework)
- **Asynchronous Runtime**: asyncio with async/await patterns
- **Package Management**: pip + requirements.txt (Python standard package management)
- **Database**: SQLite (file-based SQL database)
- **LLM Integration**: OpenRouter (Gemini 2.5 Flash) + Langfuse (observability)

## Python-Specific Best Practices

### Type Safety
- **Type Hints**: Use typing module for all function signatures
- **Static Analysis**: mypy for compile-time type checking
- **Pydantic**: For runtime data validation and settings management
- **NO `Any` types**: All types must be explicitly defined

### Code Quality Tools
- **black**: Code formatting (line length: 88-100 characters)
- **ruff**: Fast Python linter (replaces flake8, isort, and more)
- **mypy**: Static type checker
- **pre-commit**: Git hooks for automated checks

### Testing Framework
- **pytest**: Primary testing framework
- **pytest-asyncio**: For testing async code
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking support
- **Minimum Coverage**: 80%

### Project Structure
```
HR/
├── backend/         # FastAPI Backend
│   ├── api/         # API endpoints
│   ├── core/        # Business logic
│   ├── models/      # Data models (Pydantic/SQLAlchemy)
│   ├── services/    # Service layer
│   ├── tools/       # Utilities and tools
│   ├── utils/       # Helper functions
│   └── main.py      # FastAPI application entry point
├── frontend/        # NiceGUI Frontend
│   ├── pages/       # UI pages
│   ├── components/  # Reusable UI components
│   ├── services/    # Frontend services
│   └── main.py      # NiceGUI application entry point
├── data/            # Data files and SQLite database
├── templates/       # JSON schemas and prompts
├── tests/           # Test suite
├── scripts/         # Utility scripts
├── requirements.txt # pip dependencies
└── .env.example     # Environment variables template
```

## Asynchronous Patterns (CRITICAL)

**All I/O operations MUST be asynchronous:**

### HTTP Requests
```python
import httpx
from typing import Dict, Any

async def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch data asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
```

### Database Operations
- **Database**: SQLite (file-based, simple deployment)
- **ORM**: SQLAlchemy 2.0+ with sync/async support
- **Driver**: sqlite3 (built-in) / aiosqlite (for async operations)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# SQLite connection
engine = create_engine("sqlite:///./data/profiles.db")
with Session(engine) as session:
    result = session.execute(query)
```

### File Operations
```python
import aiofiles

async def read_file_async(path: str) -> str:
    """Read file asynchronously."""
    async with aiofiles.open(path, mode='r') as f:
        return await f.read()
```

## Data Validation

### Pydantic Models
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    """User data model."""
    id: int
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    created_at: datetime
    is_active: bool = True

    @validator('email')
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility
```

## Environment Configuration

### Settings Management
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables."""
    # Required settings
    app_name: str = "HR profile generator"
    debug: bool = False

    # Database
    database_url: str

    # Optional settings
    redis_url: Optional[str] = None
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## Prohibited Practices

### FORBIDDEN:
1. **Synchronous I/O in async code** - Blocks event loop
   ```python
   # BAD
   async def bad_example():
       import requests
       response = requests.get(url)  # Blocks!

   # GOOD
   async def good_example():
       import httpx
       async with httpx.AsyncClient() as client:
           response = await client.get(url)
   ```

2. **Using `Any` type hints** - Defeats type safety
   ```python
   # BAD
   def process(data: Any) -> Any:
       ...

   # GOOD
   def process(data: Dict[str, int]) -> List[str]:
       ...
   ```

3. **Storing secrets in code**
   ```python
   # BAD
   API_KEY = "sk-1234567890"

   # GOOD
   from settings import settings
   API_KEY = settings.api_key
   ```

4. **Raw SQL without parameterization**
   ```python
   # BAD - SQL injection risk
   query = f"SELECT * FROM users WHERE id = {user_id}"

   # GOOD
   query = "SELECT * FROM users WHERE id = :user_id"
   result = await session.execute(query, {"user_id": user_id})
   ```

5. **Empty exception handlers**
   ```python
   # BAD
   try:
       risky_operation()
   except:
       pass

   # GOOD
   import logging
   logger = logging.getLogger(__name__)

   try:
       risky_operation()
   except SpecificError as e:
       logger.error(f"Failed to perform operation: {e}")
       raise
   ```

## Error Handling

### Structured Error Handling
```python
import logging
from typing import Optional, TypeVar, Callable
from functools import wraps

logger = logging.getLogger(__name__)
T = TypeVar('T')

async def with_retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    backoff: float = 1.0
) -> Optional[T]:
    """Retry async function with exponential backoff."""
    import asyncio

    for attempt in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise
            wait_time = backoff * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
            await asyncio.sleep(wait_time)
```

## Logging Standards

### Configuration
```python
import logging
import sys

def setup_logging(log_level: str = "INFO") -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
```

### Usage
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational information
- **WARNING**: Warning messages (something unexpected but handled)
- **ERROR**: Error messages (functionality impaired)
- **CRITICAL**: Critical errors (system cannot continue)

```python
logger.info(f"Processing request for user {user_id}")
logger.error(f"Failed to fetch data from API: {error}", exc_info=True)
```

## Testing Standards

### Test Structure
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_user_data():
    """Test user data fetching."""
    # Arrange
    user_id = "test_123"
    expected_data = {"id": user_id, "name": "Test User"}

    # Act
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        result = await fetch_user_data(user_id)

    # Assert
    assert result["id"] == user_id
    assert result["name"] == "Test User"
```

### Fixtures
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()
```

## Dependency Management

### requirements.txt
```txt
# Core Backend Dependencies
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.0.0
httpx>=0.27.0

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt==4.1.3
python-multipart>=0.0.6

# Frontend
nicegui>=2.24.0

# Environment
python-dotenv>=1.0.0

# Async Operations
aiofiles>=23.2.1

# Data Processing
pandas>=2.1.0
openpyxl>=3.1.0
python-docx>=1.1.0

# LLM & Monitoring
langfuse
openai>=1.0.0

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
structlog>=23.2.0
```

### Tool Configuration
Tools like black, ruff, mypy can be configured in `setup.cfg`:

```ini
# setup.cfg
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*

[tool.black]
line-length = 100
target-version = py311

[tool.ruff]
line-length = 100
target-version = py311

[tool.mypy]
python_version = 3.11
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Version Control

### Git Workflow
- **Branch Naming**: `feature/`, `bugfix/`, `hotfix/`, `docs/`
- **Commit Messages**: Use Conventional Commits format
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `docs:` - Documentation changes
  - `refactor:` - Code refactoring
  - `test:` - Adding tests
  - `chore:` - Maintenance tasks

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Performance Optimization

### Best Practices
1. **Use connection pooling** for databases and HTTP clients
2. **Cache frequently accessed data** (Redis, lru_cache)
3. **Batch operations** where possible
4. **Use async context managers** for resource management
5. **Profile before optimizing** (cProfile, py-spy)

### Caching Example
```python
from functools import lru_cache
from typing import List

@lru_cache(maxsize=128)
def expensive_computation(n: int) -> List[int]:
    """Cache expensive synchronous computations."""
    return [i ** 2 for i in range(n)]
```

## Security Best Practices

1. **Environment Variables**: All secrets in `.env` file
2. **Input Validation**: Pydantic models for all inputs
3. **SQL Injection**: Use ORM or parameterized queries
4. **Dependency Scanning**: Regular `pip list --outdated` and security audits with pip-audit
5. **HTTPS Only**: All external API calls over HTTPS

---

**Last Updated**: 2025-10-19
**Python Version**: 3.11+
**Framework**: FastAPI

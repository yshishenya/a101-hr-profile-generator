# Test Implementation Guide
**Companion to**: TEST_SCENARIOS_COMPREHENSIVE.md
**Date**: 2025-10-25

## Quick Start

### 1. Install Test Dependencies

```bash
cd /home/yan/A101/HR

# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-benchmark jsonschema

# Verify installation
pytest --version
```

### 2. Run All Tests

```bash
# Run full test suite
pytest tests/ -v --cov=backend --cov-report=html --cov-report=term

# Open coverage report
xdg-open htmlcov/index.html  # Linux
# or
open htmlcov/index.html      # macOS
```

### 3. Run Specific Test Categories

```bash
# Unit tests only (fast, ~2 minutes)
pytest tests/unit/ -v

# Integration tests (slower, ~10 minutes)
pytest tests/integration/ -v

# Regression tests (database-dependent)
pytest tests/regression/ -v

# Performance benchmarks
pytest tests/performance/ -v --benchmark-only

# Quality tests (manual review required)
pytest tests/quality/ -v -m manual
```

---

## Test File Structure

```
tests/
├── conftest.py                          # Shared fixtures
├── unit/
│   ├── test_schema_area_field.py        # Fix 1: area field type
│   ├── test_schema_performance_metrics_removed.py  # Fix 2: remove field
│   ├── test_schema_proficiency_description.py      # Fix 3: keep field
│   ├── test_prompt_careerogram_structure.py        # Fix 4: careerogram
│   ├── test_kpi_mapping_it.py                      # Fix 5: IT KPIs
│   ├── test_kpi_mapping_generic.py                 # Fix 6: Generic KPIs
│   ├── test_kpi_coverage.py                        # Fix 7: 100% coverage
│   ├── test_conditional_it_systems_full.py         # Fix 8: Full IT systems
│   ├── test_conditional_it_systems_compressed.py   # Fix 9: Compressed
│   └── test_conditional_it_systems_minimal.py      # Fix 10: Minimal
├── integration/
│   ├── test_full_generation_all_fixes.py           # All fixes together
│   └── test_golden_standard_comparison.py          # Golden standard
├── regression/
│   ├── test_old_profile_compatibility.py           # Backward compatibility
│   └── test_database_compatibility.py              # DB compatibility
├── performance/
│   ├── test_token_reduction.py                     # Token reduction
│   └── test_generation_time.py                     # Generation time
├── quality/
│   ├── test_manual_quality_review.py               # Manual review
│   ├── test_careerogram_quality.py                 # Careerogram readability
│   └── manual_review_scores.json                   # Review scores (created manually)
└── fixtures/
    └── golden_standard_profile.py                  # Golden standard data
```

---

## Implementation Steps

### Step 1: Create conftest.py

```bash
# Create tests directory if it doesn't exist
mkdir -p /home/yan/A101/HR/tests/{unit,integration,regression,performance,quality,fixtures}

# Create conftest.py
cat > /home/yan/A101/HR/tests/conftest.py << 'EOF'
"""
Shared pytest fixtures and configuration for HR Profile Generator tests
"""

import pytest
import asyncio
import json
from pathlib import Path
from backend.core.profile_generator import ProfileGenerator
from backend.core.data_loader import DataLoader
from backend.models.database import get_db_manager


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def profile_generator():
    """Fixture: ProfileGenerator instance"""
    return ProfileGenerator()


@pytest.fixture
def data_loader():
    """Fixture: DataLoader instance"""
    return DataLoader("/home/yan/A101/HR/data")


@pytest.fixture
def db_manager():
    """Fixture: Database manager instance"""
    return get_db_manager()


@pytest.fixture
async def sample_architect_profile(profile_generator):
    """Fixture: Pre-generated Архитектор 3к profile"""
    result = await profile_generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=False,
    )
    assert result["success"], f"Failed to generate sample profile: {result.get('errors')}"
    return result


@pytest.fixture
async def sample_it_profile(profile_generator):
    """Fixture: Pre-generated IT profile (Программист 1С)"""
    result = await profile_generator.generate_profile(
        department="Отдел CRM",
        position="Программист 1С",
        temperature=0.1,
        save_result=False,
    )
    assert result["success"], f"Failed to generate IT profile: {result.get('errors')}"
    return result


@pytest.fixture
def json_schema():
    """Fixture: Load JSON schema for validation"""
    schema_path = Path("/home/yan/A101/HR/templates/universal_job_profile_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def golden_standard_profile():
    """Fixture: Golden standard profile structure"""
    return {
        "position_title": "Архитектор 3 категории",
        "department_broad": "Проектный блок",
        "department_specific": "Бюро комплексного проектирования",
        "position_category": "Главный специалист",
        "responsibility_areas": [
            {
                "area": "Моделирование",  # String, not array!
                "tasks": [
                    "Создание архитектурных моделей",
                    "Подготовка чертежей и планов",
                ]
            }
        ],
        "professional_skills": [
            {
                "skill_category": "Технические системы и инструменты",
                "specific_skills": ["AutoCAD", "Revit"],
                "proficiency_level": "Продвинутый",
            }
        ],
        "personal_qualities": ["внимательность к деталям", "системное мышление"],
        "career_development": {
            "career_entry_positions": ["Архитектор 2 категории"],
            "career_growth_positions": ["Архитектор 1 категории", "Главный архитектор"],
        },
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "manual: Manual review tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "benchmark: Performance benchmark tests")
EOF
```

### Step 2: Create Test Runner Script

```bash
cat > /home/yan/A101/HR/scripts/run_tests.sh << 'EOF'
#!/bin/bash
# Test runner script for HR Profile Generator

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "HR Profile Generator - Test Suite"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}ERROR: pytest not found${NC}"
    echo "Install with: pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi

# Default: run all tests
TEST_CATEGORY="${1:-all}"

case "$TEST_CATEGORY" in
    unit)
        echo -e "${GREEN}Running UNIT tests...${NC}"
        pytest tests/unit/ -v --tb=short
        ;;
    integration)
        echo -e "${YELLOW}Running INTEGRATION tests (slow)...${NC}"
        pytest tests/integration/ -v --tb=short
        ;;
    regression)
        echo -e "${YELLOW}Running REGRESSION tests...${NC}"
        pytest tests/regression/ -v --tb=short
        ;;
    performance)
        echo -e "${YELLOW}Running PERFORMANCE benchmarks...${NC}"
        pytest tests/performance/ -v --benchmark-only
        ;;
    quality)
        echo -e "${YELLOW}Running QUALITY tests...${NC}"
        pytest tests/quality/ -v -m manual
        ;;
    coverage)
        echo -e "${GREEN}Running tests with COVERAGE report...${NC}"
        pytest tests/ -v --cov=backend --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
        ;;
    fast)
        echo -e "${GREEN}Running FAST tests only (unit tests)...${NC}"
        pytest tests/unit/ -v --maxfail=3 -x
        ;;
    all)
        echo -e "${GREEN}Running ALL tests...${NC}"
        pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing
        ;;
    *)
        echo -e "${RED}Unknown test category: $TEST_CATEGORY${NC}"
        echo ""
        echo "Usage: $0 [category]"
        echo ""
        echo "Categories:"
        echo "  unit         - Unit tests only (fast)"
        echo "  integration  - Integration tests (slow)"
        echo "  regression   - Regression tests"
        echo "  performance  - Performance benchmarks"
        echo "  quality      - Quality/manual review tests"
        echo "  coverage     - All tests with coverage report"
        echo "  fast         - Fast unit tests only (stops on first 3 failures)"
        echo "  all          - All tests (default)"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Test run completed${NC}"
EOF

chmod +x /home/yan/A101/HR/scripts/run_tests.sh
```

### Step 3: Create pytest.ini Configuration

```bash
cat > /home/yan/A101/HR/pytest.ini << 'EOF'
[pytest]
# Pytest configuration for HR Profile Generator

# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests

# Asyncio configuration
asyncio_mode = auto

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
    --color=yes

# Coverage options
[coverage:run]
source = backend
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False

# Test markers
markers =
    unit: Unit tests (fast)
    integration: Integration tests (slow)
    regression: Regression tests (backward compatibility)
    performance: Performance benchmark tests
    quality: Quality/manual review tests
    manual: Requires manual review
    slow: Slow-running tests (skip with -m "not slow")
    benchmark: Performance benchmarks

# Logging
log_cli = false
log_cli_level = INFO
log_file = tests/test_run.log
log_file_level = DEBUG

# Timeout (prevent hanging tests)
timeout = 600

# Parallel execution (optional, requires pytest-xdist)
# addopts = -n auto
EOF
```

---

## Example Test Implementation

### Example 1: Unit Test for area Field

```python
# File: tests/unit/test_schema_area_field.py

import pytest
from jsonschema import validate
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.asyncio
async def test_area_field_is_string_not_array(profile_generator, json_schema):
    """Test that area field is string, not array"""
    # Act
    result = await profile_generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=False,
    )

    # Assert
    assert result["success"], f"Generation failed: {result.get('errors', [])}"

    profile = result["profile"]
    responsibility_areas = profile.get("responsibility_areas", [])

    assert len(responsibility_areas) > 0, "No responsibility areas generated"

    for idx, area_obj in enumerate(responsibility_areas):
        area_value = area_obj.get("area")

        # Primary assertion: area must be string
        assert isinstance(area_value, str), (
            f"responsibility_areas[{idx}].area must be string, "
            f"got {type(area_value).__name__}: {area_value}"
        )

        # Validate against schema
        validate(instance=profile, schema=json_schema)
```

### Example 2: Integration Test

```python
# File: tests/integration/test_full_generation_all_fixes.py

import pytest
from backend.core.profile_generator import ProfileGenerator


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_generation_all_fixes(profile_generator, json_schema):
    """Integration test: All fixes applied and validated"""
    # Act
    result = await profile_generator.generate_profile(
        department="Бюро комплексного проектирования",
        position="Архитектор 3к",
        temperature=0.1,
        save_result=True,
    )

    # Assert
    assert result["success"]
    profile = result["profile"]

    # Validate all fixes
    # Fix 1: area is string
    for area_obj in profile["responsibility_areas"]:
        assert isinstance(area_obj["area"], str)

    # Fix 2: No performance_metrics
    assert "performance_metrics" not in profile

    # Fix 3: Careerogram structure
    career_dev = profile["career_development"]
    assert isinstance(career_dev, dict)
    assert isinstance(career_dev.get("career_entry_positions", []), list)

    # Schema validation
    from jsonschema import validate
    validate(instance=profile, schema=json_schema)
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_schema_area_field.py -v

# Run specific test function
pytest tests/unit/test_schema_area_field.py::test_area_field_is_string_not_array -v

# Run tests matching pattern
pytest -k "area_field" -v

# Run tests with markers
pytest -m unit -v              # Only unit tests
pytest -m "not slow" -v        # Skip slow tests
pytest -m "unit and not slow"  # Unit tests, not slow
```

### Coverage Commands

```bash
# Generate coverage report
pytest --cov=backend --cov-report=html

# Show missing lines
pytest --cov=backend --cov-report=term-missing

# Coverage for specific module
pytest --cov=backend.core.profile_generator --cov-report=term

# Fail if coverage below threshold
pytest --cov=backend --cov-fail-under=80
```

### Debugging Commands

```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show local variables on failure
pytest -l

# Enter debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Show full traceback
pytest --tb=long
```

### Performance Commands

```bash
# Run benchmarks
pytest tests/performance/ --benchmark-only

# Compare benchmarks
pytest tests/performance/ --benchmark-compare

# Save benchmark results
pytest tests/performance/ --benchmark-save=baseline

# Measure slowest tests
pytest --durations=10
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# File: .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run unit tests
      run: pytest tests/unit/ -v

    - name: Run integration tests
      run: pytest tests/integration/ -v

    - name: Generate coverage report
      run: pytest --cov=backend --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Issue: ModuleNotFoundError: No module named 'backend'
# Solution: Add project root to PYTHONPATH
export PYTHONPATH=/home/yan/A101/HR:$PYTHONPATH
pytest
```

#### 2. Async Test Failures

```bash
# Issue: RuntimeError: Event loop is closed
# Solution: Ensure pytest-asyncio is installed and configured
pip install pytest-asyncio
# Add to conftest.py: pytest_plugins = ('pytest_asyncio',)
```

#### 3. Database Lock Errors

```bash
# Issue: sqlite3.OperationalError: database is locked
# Solution: Use separate test database
# In conftest.py:
@pytest.fixture
def test_db():
    import tempfile
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    return db_file.name
```

#### 4. API Rate Limits

```bash
# Issue: OpenRouter API rate limit exceeded
# Solution: Mock LLM calls in unit tests
# Use pytest-mock or unittest.mock
```

---

## Best Practices

### 1. Test Organization

- **One test file per module**: `test_<module_name>.py`
- **One test class per feature**: `class TestAreaField:`
- **One assertion per test**: Clear failure messages
- **Use fixtures**: Reduce duplication

### 2. Test Naming

```python
# Good test names (describe what is tested and expected outcome)
def test_area_field_is_string_not_array()
def test_careerogram_structure_is_object_with_arrays()
def test_it_department_gets_it_specific_kpis()

# Bad test names (unclear what is being tested)
def test_area()
def test_careerogram()
def test_kpi()
```

### 3. Assertions

```python
# Good assertions (clear failure messages)
assert isinstance(area, str), (
    f"area must be string, got {type(area).__name__}: {area}"
)

# Bad assertions (unclear what went wrong)
assert isinstance(area, str)
```

### 4. Test Independence

```python
# Good: Each test is independent
@pytest.mark.asyncio
async def test_feature_a(profile_generator):
    result = await profile_generator.generate_profile(...)
    assert result["success"]

@pytest.mark.asyncio
async def test_feature_b(profile_generator):
    result = await profile_generator.generate_profile(...)
    assert result["success"]

# Bad: Tests depend on each other
test_results = {}

def test_feature_a():
    test_results["a"] = generate_profile()

def test_feature_b():
    # Depends on test_feature_a running first!
    assert test_results["a"]["success"]
```

---

## Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **pytest-benchmark**: https://pytest-benchmark.readthedocs.io/

---

**Last Updated**: 2025-10-25
**Status**: Ready for Use ✅

# Testing Documentation

This directory contains comprehensive testing documentation for the HR Profile Generator quality optimization fixes.

## Documents

### 1. TEST_SCENARIOS_COMPREHENSIVE.md
**Purpose**: Complete test scenarios covering all fixes
**Audience**: QA Engineers, Developers, Project Managers

**Contents**:
- 24 detailed test cases across 5 categories
- Unit, Integration, Regression, Performance, and Quality tests
- Test data fixtures and golden standards
- Success criteria and metrics
- Week-long execution plan

**Quick Links**:
- Test Strategy (Section 1)
- Unit Tests - Schema Fixes (Section 2)
- Unit Tests - Prompt Fixes (Section 3)
- Integration Tests (Section 6)
- Success Criteria Summary (Section 11)

### 2. TEST_IMPLEMENTATION_GUIDE.md
**Purpose**: Practical guide for running and implementing tests
**Audience**: Developers, DevOps

**Contents**:
- Quick start instructions
- Test file structure
- pytest configuration
- Example test implementations
- Troubleshooting guide
- CI/CD integration examples

**Quick Links**:
- Quick Start (Section 1)
- Test Runner Script (Section 2.2)
- Example Tests (Section 4)
- Running Tests (Section 5)
- Troubleshooting (Section 7)

## Overview of Fixes Being Tested

### Fix 1: Schema - `area` field type
**Before**: `"area": ["Моделирование", "Проектирование"]` (array)
**After**: `"area": "Моделирование"` (string)
**Impact**: 100% schema validation pass rate

### Fix 2: Schema - `performance_metrics` removed
**Before**: Field present but unused
**After**: Field removed from schema
**Impact**: Cleaner schema, no confusion

### Fix 3: Prompt - `careerogram` structure
**Before**: `["source_positions", "pos1", "target_positions", "pos2"]` (flat array)
**After**: `{"source_positions": ["pos1"], "target_positions": ["pos2"]}` (object)
**Impact**: 100% parseability (was 0%)

### Fix 4: Feature - KPI mapping
**Before**: 1.6% coverage (9/567 departments)
**After**: 100% coverage (all departments)
**Impact**: All profiles have relevant KPIs

### Fix 5: Feature - Conditional IT systems
**Before**: 158K tokens for all roles (full IT systems always loaded)
**After**: 15K tokens for IT roles, 3K for management, 1K for others
**Impact**: ~40% token reduction for non-IT roles

## Quick Start

### Install Dependencies

```bash
cd /home/yan/A101/HR
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-benchmark jsonschema
```

### Run All Tests

```bash
# Run full test suite with coverage
pytest tests/ -v --cov=backend --cov-report=html

# Or use the test runner script
./scripts/run_tests.sh all
```

### Run Specific Test Categories

```bash
# Unit tests only (fast, ~2 minutes)
./scripts/run_tests.sh unit

# Integration tests (slow, ~10 minutes)
./scripts/run_tests.sh integration

# Performance benchmarks
./scripts/run_tests.sh performance

# Generate coverage report
./scripts/run_tests.sh coverage
```

## Test Categories

### Unit Tests (15 tests)
- **Schema fixes**: 9 tests
  - area field type validation
  - performance_metrics removal
  - proficiency_description retention
- **Prompt fixes**: 3 tests
  - careerogram structure validation
- **KPI mapping**: 3 tests
  - IT department KPIs
  - Generic department KPIs
  - 100% coverage

### Integration Tests (2 tests)
- Full generation flow with all fixes
- Golden standard comparison

### Regression Tests (2 tests)
- Old profile format compatibility
- Database backward compatibility

### Performance Tests (2 tests)
- Token reduction measurement
- Generation time validation

### Quality Tests (2 tests)
- Manual HR review (10 profiles, target ≥8/10)
- Careerogram readability (100% parseable)

## Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| Schema validation | 100% | Automated (jsonschema) |
| Careerogram parseability | 100% | Automated + Manual |
| KPI coverage | 100% | Automated (567/567 depts) |
| Token reduction (non-IT) | ≥30% | Automated (benchmark) |
| Generation time | <90s | Automated (pytest) |
| Quality score | ≥8/10 | Manual (HR review) |
| Code coverage | ≥80% | Automated (pytest-cov) |

## Test Execution Plan

### Week 1: Full Testing Cycle

**Day 1-2**: Unit Tests
- Implement all 15 unit tests
- Run: `./scripts/run_tests.sh unit`
- **Target**: 100% pass rate

**Day 3**: Integration Tests
- Implement 2 integration tests
- Run: `./scripts/run_tests.sh integration`
- **Target**: All tests pass, golden standard match ≥95%

**Day 4**: Regression & Performance
- Implement 4 regression/performance tests
- Run: `./scripts/run_tests.sh regression performance`
- **Target**: No regressions, token reduction ≥30%

**Day 5**: Quality Review
- Generate 10 profiles for manual review
- HR team reviews (1-10 scale)
- Run: `./scripts/run_tests.sh quality`
- **Target**: Average score ≥8/10

## Test File Locations

```
/home/yan/A101/HR/
├── tests/
│   ├── conftest.py                     # Shared fixtures
│   ├── unit/                           # Unit tests (15)
│   ├── integration/                    # Integration tests (2)
│   ├── regression/                     # Regression tests (2)
│   ├── performance/                    # Performance tests (2)
│   ├── quality/                        # Quality tests (2)
│   └── fixtures/                       # Test data
├── pytest.ini                          # pytest configuration
├── scripts/
│   └── run_tests.sh                    # Test runner script
└── docs/
    └── testing/                        # This directory
        ├── README.md                   # This file
        ├── TEST_SCENARIOS_COMPREHENSIVE.md
        └── TEST_IMPLEMENTATION_GUIDE.md
```

## Commands Cheat Sheet

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific category
pytest tests/unit/ -v                # Unit tests
pytest tests/integration/ -v         # Integration tests
pytest -m performance --benchmark-only  # Benchmarks

# Run specific test
pytest tests/unit/test_schema_area_field.py::test_area_field_is_string_not_array -v

# Debugging
pytest -x            # Stop on first failure
pytest --pdb         # Enter debugger on failure
pytest -s            # Show print statements
pytest -l            # Show local variables

# Performance
pytest --durations=10  # Show 10 slowest tests
```

## Metrics Dashboard

After running tests, check these metrics:

### Coverage Report
```bash
# Generate and open coverage report
pytest --cov=backend --cov-report=html
xdg-open htmlcov/index.html
```

**Target**: ≥80% overall coverage

### Test Results Summary
```bash
# Run tests with summary
pytest tests/ -v --tb=short
```

**Target**:
- 23/23 tests passing (100%)
- 0 failures
- 0 errors

### Performance Benchmarks
```bash
# Run benchmarks
pytest tests/performance/ --benchmark-only
```

**Targets**:
- Token reduction: ≥30% for non-IT roles
- Generation time: <90s per profile
- Memory usage: <2GB

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'backend'`
**Solution**:
```bash
export PYTHONPATH=/home/yan/A101/HR:$PYTHONPATH
pytest
```

**Issue**: `RuntimeError: Event loop is closed`
**Solution**: Ensure pytest-asyncio is installed
```bash
pip install pytest-asyncio
```

**Issue**: API rate limits during testing
**Solution**: Mock LLM calls or use test API key with higher limits

## Next Steps

1. ✅ **Read TEST_SCENARIOS_COMPREHENSIVE.md** - Understand all test cases
2. ✅ **Read TEST_IMPLEMENTATION_GUIDE.md** - Learn how to implement tests
3. ⏳ **Implement fixes** in code
4. ⏳ **Write tests** following the test scenarios
5. ⏳ **Run test suite** and validate success criteria
6. ⏳ **Manual quality review** by HR team
7. ⏳ **Generate coverage report** and verify ≥80%
8. ⏳ **Document results** and create PR

## Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **JSON Schema**: https://json-schema.org/

## Support

For questions or issues:
1. Check **TEST_IMPLEMENTATION_GUIDE.md** Troubleshooting section
2. Review pytest documentation
3. Check existing test examples in `tests/` directory

---

**Document Version**: 1.0
**Last Updated**: 2025-10-25
**Status**: Ready for Use ✅

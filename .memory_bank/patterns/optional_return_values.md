# Optional Return Values Pattern

## Principle
When a function may not find a result or the result may legitimately be absent, use `Optional[T]` to explicitly communicate this to callers and enforce proper None handling.

## When to Use
- Search/lookup functions that may not find the requested item
- Functions that retrieve optional configuration
- Functions that parse data that may be missing
- Functions that attempt operations that may fail gracefully

## Pattern Implementation

### 1. Function Declaration
```python
from typing import Optional

def find_resource(name: str) -> Optional[str]:
    """
    Find resource by name.

    Args:
        name: Resource name to search for

    Returns:
        Resource path if found, None otherwise

    Example:
        >>> path = find_resource("config.yaml")
        >>> if path is not None:
        ...     # Use path safely
    """
    # Search logic here
    if resource_found:
        return resource_path
    return None  # Explicitly return None
```

### 2. Caller Must Handle None
```python
# ✅ CORRECT: Check for None before using
result = find_resource("foo")
if result is not None:
    path = base_dir / result  # Safe!
    process_file(path)
else:
    logger.warning("Resource 'foo' not found, using fallback")
    use_fallback()

# ❌ WRONG: Don't assume non-None
result = find_resource("foo")
path = base_dir / result  # CRASH if result is None!
```

### 3. Document the None Case
Always document what None means:

```python
def get_kpi_file(department: str) -> Optional[str]:
    """
    Get KPI file for department.

    Args:
        department: Department name

    Returns:
        KPI filename if department has specific KPI file,
        None if department should use generic template

    Note:
        None is NOT an error - it indicates the department
        should fall back to the generic KPI template.
    """
    # Implementation
```

## Real-World Example: KPI Mapping

This pattern prevented a critical bug in the HR profile generator where 71.2% of departments would crash.

### Before (Incorrect)
```python
def find_kpi_file(self, department: str) -> str:  # ❌ Assumes always returns string
    """Find KPI file for department."""
    # Returns None for 71.2% of departments
    # but signature doesn't indicate this!
    ...

# Caller code (crashes on None)
kpi_filename = self.find_kpi_file(department)
kpi_path = self.kpi_dir / kpi_filename  # ❌ CRASH: PosixPath / None
```

### After (Correct)
```python
def find_kpi_file(self, department: str) -> Optional[str]:  # ✅ Explicit Optional
    """
    Find KPI file for department.

    Returns:
        KPI filename if found, None if department has no specific KPI file
    """
    # Smart mapping + hierarchical inheritance
    match_result = self.dept_mapper.find_best_match(department)
    if match_result and kpi_path.exists():
        return kpi_file

    hierarchical_file = self._find_kpi_by_hierarchy(department)
    if hierarchical_file:
        return hierarchical_file

    return None  # ✅ Explicit None for 71.2% of departments

# Caller code (handles None gracefully)
kpi_filename = self.find_kpi_file(department)

if kpi_filename is not None:  # ✅ Check before using
    kpi_path = self.kpi_dir / kpi_filename
    if kpi_path.exists():
        # Load specific KPI file
        ...
else:
    # Fall back to generic template
    # This is NOT an error - it's expected behavior
    if self.templates_available:
        return self.get_kpi_template(department)
```

## Best Practices

### 1. Use Early Returns
```python
# ✅ GOOD: Early return for None case
def find_resource(name: str) -> Optional[str]:
    if name not in resource_map:
        return None  # Early return

    resource_path = resource_map[name]
    if not resource_path.exists():
        return None  # Early return

    return str(resource_path)

# ❌ BAD: Nested conditions
def find_resource(name: str) -> Optional[str]:
    if name in resource_map:
        resource_path = resource_map[name]
        if resource_path.exists():
            return str(resource_path)
        else:
            return None
    else:
        return None
```

### 2. Provide Fallback Behavior
```python
def load_config(config_name: str) -> Optional[dict]:
    """Load configuration file."""
    config_file = find_config_file(config_name)

    if config_file is None:
        logger.warning(f"Config '{config_name}' not found, using defaults")
        return None  # Caller will use defaults

    return parse_config(config_file)

# Caller handles None gracefully
config = load_config("app_settings")
if config is None:
    config = get_default_config()  # Fallback
```

### 3. Type Checkers Will Help
With `mypy` enabled, type mismatches are caught:

```python
def process_file(path: str) -> None:  # Expects str, not Optional[str]
    ...

# mypy will catch this error:
path = find_resource("foo")  # Optional[str]
process_file(path)  # ❌ mypy error: Expected str, got Optional[str]

# Fix: Check for None first
path = find_resource("foo")
if path is not None:
    process_file(path)  # ✅ mypy happy: str guaranteed here
```

## Anti-Patterns to Avoid

### ❌ Don't Use None for Errors
```python
# ❌ BAD: Using None for actual errors
def fetch_data(url: str) -> Optional[dict]:
    try:
        response = requests.get(url)
        return response.json()
    except requests.RequestException:
        return None  # Lost the error information!

# ✅ GOOD: Raise exceptions for errors
def fetch_data(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise FetchError(f"Failed to fetch {url}: {e}")
```

### ❌ Don't Return None AND Raise Exceptions
```python
# ❌ BAD: Inconsistent - sometimes None, sometimes exception
def find_user(user_id: int) -> Optional[User]:
    if user_id < 0:
        raise ValueError("Invalid user_id")  # Exception!

    user = db.get_user(user_id)
    return user if user else None  # None!

# ✅ GOOD: Consistent - always Optional
def find_user(user_id: int) -> Optional[User]:
    if user_id < 0:
        return None  # Treat as "not found"

    return db.get_user(user_id)  # May be None

# ✅ OR: Always raise exception
def get_user(user_id: int) -> User:  # Never returns None
    if user_id < 0:
        raise ValueError("Invalid user_id")

    user = db.get_user(user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")

    return user
```

### ❌ Don't Use Truthy Checks for Optional
```python
# ❌ RISKY: Truthy check can hide bugs
result = find_resource("foo")
if result:  # What if result is empty string ""?
    process(result)

# ✅ BETTER: Explicit None check
result = find_resource("foo")
if result is not None:
    process(result)  # Even if result is ""
```

## Testing Optional Returns

Always test both paths:

```python
def test_find_kpi_file_returns_none_for_unknown():
    """Test None is returned for unknown department."""
    mapper = KPIMapper()
    result = mapper.find_kpi_file("Unknown Department")

    assert result is None, "Should return None for unknown department"

def test_find_kpi_file_returns_string_for_known():
    """Test string is returned for known department."""
    mapper = KPIMapper()
    result = mapper.find_kpi_file("Known Department")

    assert result is not None, "Should return filename for known department"
    assert isinstance(result, str), f"Expected str, got {type(result)}"
```

## Related Patterns
- **Error Handling**: Use exceptions for exceptional cases, Optional for expected absences
- **Fallback Pattern**: Provide default values when Optional is None
- **Null Object Pattern**: Alternative to Optional for complex objects

## References
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- Bug Report: `docs/analysis/BACKEND_KPI_NONE_FIX.md` (KPI None handling crash)

---

**Last Updated**: 2025-10-25
**Pattern Category**: Type Safety, Error Prevention

# KPI Filtering Implementation Specification
## A101 HR Profile Generator - Position-Level KPI Filtering

**Priority:** High
**Complexity:** Medium
**Estimated Effort:** 2-3 weeks
**Status:** Ready for Implementation

---

## Problem Statement

Currently, the system loads ALL KPI data for a department and passes it to the LLM, regardless of the target position. This results in:

- **60-80% irrelevant KPI data** in the prompt context
- Risk of LLM confusion between KPIs for different positions
- Suboptimal use of token budget
- Reduced profile accuracy

**Example:** Generating profile for "Архитектор решений" receives KPIs for CIO, Department Heads, and all other positions in IT department.

---

## Solution Design

### Approach: Extend KPIMapper with Position-Aware Filtering

**File:** `/home/yan/A101/HR/backend/core/data_mapper.py`

**New method:** `load_kpi_content_for_position(department: str, position: str) -> str`

### Implementation Steps

#### Step 1: Parse KPI File Structure

```python
def _parse_kpi_file(self, content: str) -> tuple[dict, list]:
    """
    Parse KPI markdown file into structured components.

    Returns:
        tuple: (frontmatter_dict, table_rows_list)

    Example frontmatter:
        {
            'department': 'ДИТ',
            'positions_map': {
                'Директор по информационным технологиям': 'Сложеникин А.В.',
                'Руководитель отдела': 'Нор Е.А.'
            }
        }

    Example table row:
        {
            'kpi_name': 'Поддержание совокупного SLA',
            'target': '99.3%',
            'positions': {
                'Сложеникин Алексей Вячеславович': 0.1,
                'Нор Евгений Алексеевич': 0.0
            }
        }
    """
    import yaml
    import re

    # Split frontmatter and content
    parts = content.split('---')
    if len(parts) >= 3:
        frontmatter = yaml.safe_load(parts[1])
        markdown_content = '---'.join(parts[2:])
    else:
        frontmatter = {}
        markdown_content = content

    # Parse markdown table
    # Use regex to extract table structure
    # Return list of row dicts
    table_rows = self._parse_markdown_table(markdown_content)

    return frontmatter, table_rows
```

#### Step 2: Match Position to Column

```python
def _match_position_to_column(
    self,
    target_position: str,
    positions_map: dict
) -> Optional[str]:
    """
    Match user's position input to KPI file position name.

    Uses fuzzy matching to handle variations:
    - "Архитектор решений" -> "Руководитель управления"
    - "Начальник отдела" -> "Руководитель отдела"

    Args:
        target_position: User input position name
        positions_map: positions_map from KPI frontmatter

    Returns:
        Matched position name from KPI file or None
    """
    from thefuzz import fuzz

    # Direct match first
    if target_position in positions_map:
        return target_position

    # Fuzzy match with 80% threshold
    best_match = None
    best_score = 0

    for position_name in positions_map.keys():
        score = fuzz.ratio(
            target_position.lower(),
            position_name.lower()
        )
        if score > best_score and score >= 80:
            best_score = score
            best_match = position_name

    if best_match:
        logger.info(
            f"Fuzzy matched '{target_position}' to '{best_match}' "
            f"(confidence: {best_score}%)"
        )

    return best_match
```

#### Step 3: Filter KPI Rows

```python
def _filter_kpis_by_position(
    self,
    table_rows: list,
    position_column: str,
    include_corporate: bool = True
) -> list:
    """
    Filter KPI rows to include only those relevant to position.

    Args:
        table_rows: Parsed table data
        position_column: Matched position name
        include_corporate: Include corporate KPIs that apply to all

    Returns:
        Filtered list of KPI rows
    """
    filtered = []

    for row in table_rows:
        # Always include corporate KPIs
        if include_corporate and 'корпоративн' in row.get('kpi_name', '').lower():
            filtered.append(row)
            continue

        # Include if position has non-zero weight
        position_weight = row.get('positions', {}).get(position_column, 0)
        if position_weight and position_weight != 0:
            filtered.append(row)

    logger.info(
        f"Filtered KPIs: {len(filtered)} of {len(table_rows)} rows "
        f"relevant to '{position_column}'"
    )

    return filtered
```

#### Step 4: Rebuild Markdown

```python
def _rebuild_kpi_markdown(
    self,
    frontmatter: dict,
    filtered_rows: list,
    position_column: str
) -> str:
    """
    Reconstruct clean markdown with only relevant KPIs.

    Returns simplified table focused on target position.
    """
    # Build simplified header
    header = f"# KPI для позиции: {position_column}\n\n"
    header += f"Департамент: {frontmatter.get('department', 'N/A')}\n\n"

    # Build simplified table
    table = "| КПЭ | Целевое значение | Вес | Методика |\n"
    table += "|-----|------------------|-----|----------|\n"

    for row in filtered_rows:
        kpi_name = row.get('kpi_name', '')
        target = row.get('target', '')
        weight = row.get('positions', {}).get(position_column, '')
        methodology = row.get('methodology', '')

        table += f"| {kpi_name} | {target} | {weight} | {methodology} |\n"

    return header + table
```

#### Step 5: Main Method

```python
def load_kpi_content_for_position(
    self,
    department: str,
    position: str
) -> str:
    """
    Load KPI content filtered for specific position.

    This replaces load_kpi_content() for position-aware filtering.

    Args:
        department: Department name
        position: Position title

    Returns:
        Markdown string with filtered KPIs

    Raises:
        ValueError: If position not found in KPI file
    """
    # Find KPI file
    kpi_filename = self.find_kpi_file(department)
    kpi_path = self.kpi_dir / kpi_filename

    if not kpi_path.exists():
        logger.error(f"KPI file not found: {kpi_path}")
        return f"# KPI данные недоступны для {department}"

    try:
        # Load full content
        with open(kpi_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse structure
        frontmatter, table_rows = self._parse_kpi_file(content)

        # Match position
        position_column = self._match_position_to_column(
            position,
            frontmatter.get('positions_map', {})
        )

        if not position_column:
            logger.warning(
                f"Position '{position}' not found in KPI file. "
                f"Returning unfiltered content."
            )
            return self._clean_kpi_content(content)

        # Filter KPIs
        filtered_rows = self._filter_kpis_by_position(
            table_rows,
            position_column
        )

        if not filtered_rows:
            logger.warning(f"No KPIs found for '{position_column}'")
            return f"# KPI для {position}\n\nНет доступных KPI для данной позиции."

        # Rebuild markdown
        cleaned_content = self._rebuild_kpi_markdown(
            frontmatter,
            filtered_rows,
            position_column
        )

        logger.info(
            f"Loaded {len(filtered_rows)} filtered KPIs for '{position}' "
            f"in '{department}'"
        )

        return cleaned_content

    except Exception as e:
        logger.error(f"Error filtering KPI content: {e}")
        # Fallback to unfiltered
        return self.load_kpi_content(department)
```

---

## Integration Changes

### File: `/home/yan/A101/HR/backend/core/data_loader.py`

**Line 69 - Change from:**
```python
kpi_content = self.kpi_mapper.load_kpi_content(department)
```

**To:**
```python
kpi_content = self.kpi_mapper.load_kpi_content_for_position(
    department=department,
    position=position
)
```

**Add fallback handling:**
```python
try:
    kpi_content = self.kpi_mapper.load_kpi_content_for_position(
        department=department,
        position=position
    )
except Exception as e:
    logger.warning(f"Position-filtered KPIs failed, using full content: {e}")
    kpi_content = self.kpi_mapper.load_kpi_content(department)
```

---

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_kpi_mapper_filtering.py`

```python
def test_parse_kpi_file():
    """Test KPI file parsing."""
    mapper = KPIMapper()
    with open("data/KPI/KPI_ДИТ.md") as f:
        content = f.read()

    frontmatter, rows = mapper._parse_kpi_file(content)

    assert "department" in frontmatter
    assert len(rows) > 0
    assert "kpi_name" in rows[0]

def test_match_position_to_column():
    """Test fuzzy position matching."""
    mapper = KPIMapper()
    positions_map = {
        "Директор по информационным технологиям": "Иванов И.И.",
        "Руководитель отдела": "Петров П.П."
    }

    # Exact match
    result = mapper._match_position_to_column(
        "Директор по информационным технологиям",
        positions_map
    )
    assert result == "Директор по информационным технологиям"

    # Fuzzy match
    result = mapper._match_position_to_column(
        "Директор ИТ",
        positions_map
    )
    assert result == "Директор по информационным технологиям"

def test_filter_kpis_by_position():
    """Test KPI filtering logic."""
    mapper = KPIMapper()
    rows = [
        {
            "kpi_name": "Corporate KPI",
            "positions": {"Person A": 0.1, "Person B": 0.1}
        },
        {
            "kpi_name": "Personal KPI",
            "positions": {"Person A": 0.2, "Person B": 0}
        }
    ]

    filtered = mapper._filter_kpis_by_position(rows, "Person A")
    assert len(filtered) == 2  # Corporate + Personal

    filtered = mapper._filter_kpis_by_position(rows, "Person B")
    assert len(filtered) == 1  # Only Corporate

def test_load_kpi_content_for_position():
    """Integration test for full filtering flow."""
    mapper = KPIMapper()

    result = mapper.load_kpi_content_for_position(
        department="ДИТ",
        position="Директор по информационным технологиям"
    )

    assert "КПЭ" in result
    assert len(result) < 10000  # Should be filtered
```

### Integration Tests

**File:** `tests/integration/test_profile_generation_with_filtering.py`

```python
async def test_profile_generation_with_filtered_kpis():
    """Test end-to-end profile generation with KPI filtering."""
    generator = ProfileGenerator()

    result = await generator.generate_profile(
        department="ДИТ",
        position="Руководитель отдела",
        save_result=False
    )

    # Verify KPI filtering happened
    variables = generator.data_loader.prepare_langfuse_variables(
        "ДИТ",
        "Руководитель отдела"
    )

    kpi_data = variables["kpi_data"]
    assert "Руководитель отдела" in kpi_data
    assert len(kpi_data) < 5000  # Filtered content should be smaller
```

---

## Dependencies

Add to `requirements.txt`:

```
PyYAML>=6.0  # Already present
thefuzz>=0.20.0  # For fuzzy matching
python-Levenshtein>=0.21.0  # Speeds up thefuzz
```

---

## Monitoring & Logging

Add metrics tracking:

```python
# In KPIMapper class
self.filtering_metrics = {
    "total_requests": 0,
    "successful_matches": 0,
    "fuzzy_matches": 0,
    "fallbacks": 0,
    "avg_kpis_filtered": 0
}

def log_filtering_metrics(self):
    """Log KPI filtering performance metrics."""
    logger.info(f"KPI Filtering Metrics: {self.filtering_metrics}")
```

---

## Rollout Plan

### Phase 1: Development (1 week)
- Implement parsing methods
- Add fuzzy matching
- Build filtering logic
- Unit tests

### Phase 2: Integration (3 days)
- Update DataLoader
- Add error handling
- Integration tests
- Code review

### Phase 3: Testing (2 days)
- Test with all 9 KPI files
- Validate accuracy
- Performance benchmarks
- Bug fixes

### Phase 4: Deployment (2 days)
- Deploy to staging
- Validate with real profiles
- Monitor metrics
- Production deployment

### Phase 5: Optimization (1 week)
- Add caching
- Improve matching algorithm
- Performance tuning
- Documentation

---

## Success Metrics

1. **Filtering Accuracy:** >95% of positions correctly matched
2. **KPI Reduction:** 60-80% fewer KPI rows in context
3. **Performance:** <100ms filtering overhead
4. **Fallback Rate:** <5% of requests fall back to unfiltered

---

## Risk Mitigation

### Risk 1: Position Not Found in KPI File
**Mitigation:** Fallback to unfiltered content + log warning

### Risk 2: Parsing Errors
**Mitigation:** Try-catch with fallback + error logging

### Risk 3: Fuzzy Matching False Positives
**Mitigation:** Configurable threshold + manual review mode

### Risk 4: Performance Degradation
**Mitigation:** Implement caching + profiling + optimization

---

## Open Questions

1. Should we cache parsed KPI structures? (Yes, recommended)
2. What fuzzy match threshold? (Recommend 80%)
3. Should we filter corporate KPIs? (No, include for all positions)
4. How to handle positions with no KPIs? (Return message, don't fail)

---

## Code Review Checklist

- [ ] Parsing handles all 9 KPI files correctly
- [ ] Fuzzy matching tested with edge cases
- [ ] Fallback logic prevents failures
- [ ] Logging provides adequate debugging info
- [ ] Unit tests cover main code paths
- [ ] Integration tests validate end-to-end
- [ ] Performance tested (no significant overhead)
- [ ] Documentation updated
- [ ] Error handling comprehensive

---

**Specification prepared by:** Backend System Architect
**Specification version:** 1.0
**Ready for development:** Yes

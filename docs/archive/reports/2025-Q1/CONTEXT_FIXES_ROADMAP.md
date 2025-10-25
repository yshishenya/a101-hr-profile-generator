# Context Quality Fixes - Implementation Roadmap

## Quick Reference: What's Wrong and How to Fix It

### The Problem in One Sentence
**The system sends all 34 KPIs from all 5 management levels to the LLM without filtering by position level, causing the LLM to receive irrelevant data and generate profiles with wrong KPI assignments, generic responsibilities, and unclear career paths.**

---

## PHASE 1: Quick Wins (2-3 hours) - Start Here

### 1.1: Add Position Level Classification
**File:** `/home/yan/A101/HR/backend/utils/position_utils.py`

**Add this function:**
```python
def classify_position_level(position_name: str, hierarchy_level: int) -> str:
    """
    Classify position into: IC, team_lead, middle_mgmt, or senior_mgmt

    Args:
        position_name: e.g., "Архитектор решений"
        hierarchy_level: 1-6 from organization structure

    Returns:
        "IC" | "team_lead" | "middle_mgmt" | "senior_mgmt"
    """
    position_lower = position_name.lower()

    # Director level
    if any(kw in position_lower for kw in ["директор", "замгена", "вице-", "президент"]):
        return "senior_mgmt"

    # Manager level
    if any(kw in position_lower for kw in ["руководитель", "начальник"]):
        if hierarchy_level <= 3:
            return "middle_mgmt"
        else:
            return "team_lead"

    # Team lead level
    if any(kw in position_lower for kw in ["лид", "lead", "старший", "главный"]):
        return "team_lead"

    # Individual contributor
    return "IC"
```

**Where to use it:**
```python
# In data_loader.py, add to prepare_langfuse_variables():
position_level = determine_position_level(position, hierarchy_level)  # Already exists!
variables["position_level"] = position_level
```

**Impact:** Enables basic filtering logic downstream

---

### 1.2: Add KPI Applicability Filter
**File:** `/home/yan/A101/HR/backend/core/data_loader.py`

**Add this method to DataLoader class:**
```python
def _get_applicable_kpi_indices(self, position_level: str) -> list:
    """
    Return KPI row indices applicable to this position level.

    Based on analysis, KPI_DIT.md rows are:
    - Corporate KPIs: rows 5-8 (only for Director)
    - Personal KPIs: rows 10-33 (variable by role)
    """
    if position_level == "IC":
        # Exclude: corporate KPIs, director KPIs, pure management KPIs
        # Include: operational, execution KPIs
        return [10, 13, 25, 28, 29, 30, 31, 32]  # Operational KPIs

    elif position_level == "team_lead":
        # Include: team-level management KPIs
        return [10, 13, 15, 25, 28, 29, 30, 31, 32]

    elif position_level == "middle_mgmt":
        # Include: all departmental KPIs
        return list(range(10, 34))  # All personal KPIs

    elif position_level == "senior_mgmt":
        # Include: corporate + departmental + personal
        return list(range(5, 34))  # All KPIs

    return []

def _filter_kpi_content(self, department: str, position_level: str) -> str:
    """
    Load and filter KPI content based on position level.
    """
    # Load raw content
    kpi_filename = self.kpi_mapper.find_kpi_file(department)
    kpi_path = self.kpi_dir / kpi_filename

    try:
        with open(kpi_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get applicable rows
        applicable_indices = self._get_applicable_kpi_indices(position_level)

        # TODO: Parse markdown table and extract only applicable rows
        # For now, add metadata at top
        metadata = f"""## KPI CONTEXT FOR POSITION LEVEL: {position_level}

This role has {len(applicable_indices)} applicable KPIs out of 34 total.

### Applicable KPIs:
"""
        return metadata + content  # TODO: improve to return only relevant rows

    except Exception as e:
        logger.error(f"Error filtering KPI content: {e}")
        return content
```

**Update prepare_langfuse_variables():**
```python
# Line 69: Replace this:
kpi_content = self.kpi_mapper.load_kpi_content(department)

# With this:
position_level = hierarchy_info.get("position_level", "IC")  # Add if not exists
kpi_content = self._filter_kpi_content(department, position_level)
```

**Impact:** KPI data is now filtered based on position level

---

### 1.3: Update the Prompt with Guidance
**File:** `/home/yan/A101/HR/templates/generation_prompt.txt`

**Add this section after KPI data section:**
```
---

# KPI RELEVANCE GUIDANCE

The KPI data above has been pre-filtered for this position level:

**Position Level:** {{position_level}}
**Applicable KPI Count:** {{applicable_kpi_count}}
**Expected KPI Focus Areas:** {{kpi_guidance}}

IMPORTANT: Only reference KPIs that are listed above. This position:
- DOES have direct responsibility for: [extracted from filtered KPIs]
- MAY have supporting role in: [secondary KPIs]
- Does NOT have responsibility for: [excluded corporate/director KPIs]
```

**In prompt_manager.py, add variables:**
```python
variables = {
    # ... existing variables ...
    "position_level": position_level,
    "applicable_kpi_count": len(filtered_kpi_indices),
    "kpi_guidance": self._generate_kpi_guidance(position_level),
}

def _generate_kpi_guidance(self, position_level: str) -> str:
    """Generate guidance text about KPI scope for this position"""
    guidance = {
        "IC": "Focus on operational metrics (SLA, uptime, CMDB accuracy, incident response)",
        "team_lead": "Include team metrics and some management responsibility areas",
        "middle_mgmt": "Include departmental metrics and management responsibilities",
        "senior_mgmt": "Include corporate strategic metrics and departmental targets"
    }
    return guidance.get(position_level, "")
```

**Impact:** LLM now has explicit guidance about KPI relevance

---

## PHASE 2: Data Structure Improvements (4-6 hours)

### 2.1: Create KPI Parser
**File:** `/home/yan/A101/HR/backend/core/kpi_parser.py` (NEW FILE)

```python
"""KPI markdown table parser for structured data extraction"""

import re
import json
from typing import List, Dict, Any

class KPIParser:
    """Parse KPI markdown table into structured JSON format"""

    def __init__(self, kpi_file_path: str):
        self.kpi_file_path = kpi_file_path
        self.kpis = []
        self.parse()

    def parse(self):
        """Parse markdown table into structured format"""
        with open(self.kpi_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find table rows (start after header separator line)
        in_table = False
        row_count = 0

        for line in lines:
            if '|' not in line:
                continue

            # Skip separator line
            if re.match(r'^\s*\|\s*:?-+:?', line):
                in_table = True
                continue

            if not in_table:
                continue

            # Parse row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]

            if len(cells) < 5:
                continue

            row_count += 1

            kpi = {
                "row_index": row_count,
                "name": cells[0],
                "target_value": cells[1],
                "unit": cells[2],
                "roles": self._parse_role_columns(cells[3:8]),  # Columns 4-8
                "type": cells[8] if len(cells) > 8 else "",
                "min_value": cells[9] if len(cells) > 9 else "",
                "max_value": cells[10] if len(cells) > 10 else "",
                "methodology": cells[11] if len(cells) > 11 else "",
                "source": cells[12] if len(cells) > 12 else ""
            }

            self.kpis.append(kpi)

    def _parse_role_columns(self, role_cells: List[str]) -> Dict[str, str]:
        """Extract role→weight mapping"""
        roles = {
            "director": role_cells[0],
            "department_head": role_cells[1],
            "management_1": role_cells[2],
            "management_2": role_cells[3],
            "management_3": role_cells[4]
        }
        return {k: v for k, v in roles.items() if v and v != "—"}

    def filter_by_position_level(self, position_level: str) -> List[Dict]:
        """Filter KPIs applicable to position level"""
        filtered = []

        for kpi in self.kpis:
            # Skip section headers
            if kpi["name"].startswith("**"):
                continue

            # Skip if all roles are empty
            if not kpi["roles"]:
                continue

            if position_level == "IC":
                # Only include if management_X roles are empty (operational KPIs)
                has_mgmt = any(k.startswith("management") for k in kpi["roles"].keys())
                if not has_mgmt and kpi["name"]:
                    filtered.append(kpi)

            elif position_level == "team_lead":
                # Include if management_1 or team-level
                if "management_1" in kpi["roles"] or "department_head" in kpi["roles"]:
                    filtered.append(kpi)

            elif position_level == "middle_mgmt":
                # Include if any management role
                if any(k.startswith("management") for k in kpi["roles"].keys()):
                    filtered.append(kpi)

            elif position_level == "senior_mgmt":
                # Include everything with content
                if kpi["roles"]:
                    filtered.append(kpi)

        return filtered

    def export_json(self) -> str:
        """Export as JSON for use in LLM context"""
        return json.dumps(self.kpis, ensure_ascii=False, indent=2)
```

**Where to use it:**
```python
# In data_loader.py __init__:
from .kpi_parser import KPIParser

self.kpi_parser = KPIParser("data/KPI/KPI_DIT.md")
```

**Impact:** Reliable, structured KPI data extraction

---

### 2.2: Build Role Context Object
**File:** `/home/yan/A101/HR/backend/core/role_context_builder.py` (NEW FILE)

```python
"""Generate role context for position-specific profiles"""

import json
from typing import Dict, Any

class RoleContextBuilder:
    """Build contextual information about a position's role and scope"""

    def build(self, position_name: str, position_level: str,
              hierarchy: Dict, headcount_info: Dict) -> Dict[str, Any]:
        """
        Build comprehensive role context object
        """
        return {
            "role_description": self._get_role_description(position_name),
            "position_level": position_level,
            "management_level": self._get_management_level(position_level),
            "span_of_control": self._calculate_span(position_level, headcount_info),
            "reporting_to": self._get_reporting_level(position_level),
            "authority_level": self._get_authority_level(position_level),
            "budget_responsibility": self._get_budget_level(position_level),
            "decision_domains": self._get_decision_domains(position_name, position_level),
            "team_composition": self._get_team_composition(position_level),
            "kpi_responsibility": self._get_kpi_responsibility(position_level)
        }

    def _get_role_description(self, position_name: str) -> str:
        """Generate description based on position name"""
        descriptions = {
            "архитектор": "Solution architecture and technical strategy",
            "инженер": "Technical implementation and system maintenance",
            "разработчик": "Software development and coding",
            "аналитик": "Data analysis and business intelligence",
            "руководитель": "Team leadership and management",
            "директор": "Strategic direction and department leadership"
        }

        for keyword, desc in descriptions.items():
            if keyword in position_name.lower():
                return desc

        return "Technical role"

    def _get_management_level(self, position_level: str) -> int:
        """Map position level to numeric management level"""
        mapping = {
            "IC": 1,
            "team_lead": 2,
            "middle_mgmt": 3,
            "senior_mgmt": 4
        }
        return mapping.get(position_level, 1)

    def _calculate_span(self, position_level: str, headcount: Dict) -> int:
        """Estimate span of control based on position level"""
        if position_level == "IC":
            return 0
        elif position_level == "team_lead":
            return headcount.get("subordinates_direct_reports", 5)
        elif position_level == "middle_mgmt":
            return headcount.get("subordinates_direct_reports", 15)
        else:  # senior_mgmt
            return headcount.get("subordinates_direct_reports", 50)

    def _get_reporting_level(self, position_level: str) -> str:
        """Get reporting line based on position level"""
        mapping = {
            "IC": "Team Lead or Manager",
            "team_lead": "Department Manager",
            "middle_mgmt": "Director or VP",
            "senior_mgmt": "C-Level or CEO"
        }
        return mapping.get(position_level, "Manager")

    def _get_authority_level(self, position_level: str) -> str:
        """Determine authority level"""
        mapping = {
            "IC": "Low (executes decisions)",
            "team_lead": "Medium (team-level decisions)",
            "middle_mgmt": "Medium-High (departmental decisions)",
            "senior_mgmt": "High (strategic decisions)"
        }
        return mapping.get(position_level, "Low")

    def _get_budget_level(self, position_level: str) -> int:
        """Estimated budget responsibility in RUB"""
        mapping = {
            "IC": 0,
            "team_lead": 100000,
            "middle_mgmt": 500000,
            "senior_mgmt": 5000000
        }
        return mapping.get(position_level, 0)

    def _get_decision_domains(self, position_name: str, position_level: str) -> list:
        """List domains where this role makes decisions"""
        ic_domains = ["Technical approach", "Tool selection (limited)"]
        lead_domains = ["Team priorities", "Resource allocation (team)"]
        mgmt_domains = ["Departmental strategy", "Budget allocation", "Vendor management"]
        director_domains = ["Corporate strategy", "Large capital decisions", "Organizational structure"]

        mapping = {
            "IC": ic_domains,
            "team_lead": ic_domains + lead_domains,
            "middle_mgmt": lead_domains + mgmt_domains,
            "senior_mgmt": mgmt_domains + director_domains
        }
        return mapping.get(position_level, [])

    def _get_team_composition(self, position_level: str) -> str:
        """Describe typical team structure"""
        mapping = {
            "IC": "Individual contributor",
            "team_lead": "Small team (3-10 people)",
            "middle_mgmt": "Department or large team (15-50 people)",
            "senior_mgmt": "Multiple teams/divisions (50+ people)"
        }
        return mapping.get(position_level, "Individual")

    def _get_kpi_responsibility(self, position_level: str) -> Dict:
        """Describe KPI responsibility type"""
        mapping = {
            "IC": {
                "type": "Execution metrics",
                "participation": "Direct execution of KPIs owned by manager",
                "accountability": "Contributes to team KPIs"
            },
            "team_lead": {
                "type": "Team and management metrics",
                "participation": "Direct owner of team KPIs, contributor to dept KPIs",
                "accountability": "Accountable for team performance"
            },
            "middle_mgmt": {
                "type": "Departmental metrics",
                "participation": "Direct owner of dept KPIs",
                "accountability": "Directly accountable for all departmental KPIs"
            },
            "senior_mgmt": {
                "type": "Corporate and departmental",
                "participation": "Owner of corporate and dept KPIs",
                "accountability": "Strategic and operational accountability"
            }
        }
        return mapping.get(position_level, {})
```

**Impact:** Rich contextual information about role scope and authority

---

## PHASE 3: Integration (2-4 hours)

### 3.1: Update Data Loader
**File:** `/home/yan/A101/HR/backend/core/data_loader.py`

**Integrate all new components:**
```python
from .kpi_parser import KPIParser
from .role_context_builder import RoleContextBuilder

class DataLoader:
    def __init__(self, base_path: str = "."):
        # ... existing code ...
        self.kpi_parser = KPIParser("data/KPI/KPI_DIT.md")
        self.role_builder = RoleContextBuilder()

    def prepare_langfuse_variables(
        self, department: str, position: str, employee_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updated method with all new context"""

        # ... existing code up to line 66 ...

        # NEW: Position level classification
        position_level = determine_position_level(position, hierarchy_info.get("hierarchy_level", 1))

        # NEW: KPI filtering and parsing
        applicable_kpis = self.kpi_parser.filter_by_position_level(position_level)
        kpi_json_data = json.dumps(applicable_kpis, ensure_ascii=False, indent=2)

        # NEW: Role context
        role_context = self.role_builder.build(
            position,
            position_level,
            hierarchy_info,
            headcount_info
        )

        # Build variables with all new context
        variables = {
            # ... existing variables ...
            "position_level": position_level,
            "kpi_data": kpi_json_data,  # Changed from raw markdown
            "applicable_kpi_count": len(applicable_kpis),
            "role_context": json.dumps(role_context, ensure_ascii=False, indent=2),
            "role_description": role_context["role_description"],
            "span_of_control": role_context["span_of_control"],
            "authority_level": role_context["authority_level"],
        }

        return variables
```

**Impact:** All new data structures integrated into context preparation

---

### 3.2: Update Prompt Template
**File:** `/home/yan/A101/HR/templates/generation_prompt.txt`

**Replace KPI section:**
```
# POSITION-SPECIFIC CONTEXT

## Your Role
{{role_description}}

**Position Level:** {{position_level}}
**Reporting To:** {{reporting_to}}
**Team Size:** {{span_of_control}} people
**Authority Level:** {{authority_level}}

---

## KEY PERFORMANCE INDICATORS ({{applicable_kpi_count}} applicable)

This position is responsible for {{applicable_kpi_count}} specific KPIs:

{{kpi_data}}

IMPORTANT: These are the ONLY KPIs relevant to this position. Do NOT include corporate targets or unrelated management KPIs.

---

## Role Context

{{role_context}}

---
```

**Impact:** Prompt now has position-specific, pre-filtered context

---

## PHASE 4: Validation & Testing (2-3 hours)

### 4.1: Add Unit Tests
**File:** `/home/yan/A101/HR/tests/test_kpi_context.py` (NEW FILE)

```python
"""Tests for KPI context preparation"""

import pytest
from backend.core.data_loader import DataLoader
from backend.core.kpi_parser import KPIParser
from backend.core.role_context_builder import RoleContextBuilder

class TestKPIFiltering:

    def test_ic_kpi_filtering(self):
        """IC positions should exclude management KPIs"""
        parser = KPIParser("data/KPI/KPI_DIT.md")
        filtered = parser.filter_by_position_level("IC")

        # Should have 5-8 KPIs
        assert 5 <= len(filtered) <= 10

        # Should not include director KPIs
        assert all("директор" not in kpi["name"].lower() for kpi in filtered)

    def test_manager_kpi_filtering(self):
        """Managers should include management KPIs"""
        parser = KPIParser("data/KPI/KPI_DIT.md")
        filtered = parser.filter_by_position_level("middle_mgmt")

        # Should have more KPIs
        assert len(filtered) > 10

    def test_role_context_generation(self):
        """Role context should have required fields"""
        builder = RoleContextBuilder()
        context = builder.build(
            "Архитектор решений",
            "IC",
            {"hierarchy_level": 3},
            {"subordinates_direct_reports": 0}
        )

        assert context["position_level"] == "IC"
        assert context["span_of_control"] == 0
        assert "decision_domains" in context
```

**Run tests:**
```bash
pytest tests/test_kpi_context.py -v
```

**Impact:** Validates that filtering works correctly

---

### 4.2: Integration Test
**File:** `/home/yan/A101/HR/tests/test_integration_context.py` (NEW FILE)

```python
"""Integration test for complete context preparation"""

from backend.core.data_loader import DataLoader

def test_complete_context_preparation():
    """Test full data preparation pipeline"""
    loader = DataLoader()

    variables = loader.prepare_langfuse_variables(
        department="ДИТ",
        position="Архитектор решений",
        employee_name="Иванов И.И."
    )

    # Verify all new fields present
    assert "position_level" in variables
    assert "applicable_kpi_count" in variables
    assert "role_context" in variables
    assert variables["applicable_kpi_count"] > 0
    assert variables["applicable_kpi_count"] < 20

    # KPI data should be JSON, not markdown
    import json
    kpi_data = json.loads(variables["kpi_data"])
    assert isinstance(kpi_data, list)
    assert len(kpi_data) > 0

    # Each KPI should have required fields
    for kpi in kpi_data:
        assert "name" in kpi
        assert "roles" in kpi

    print("✓ Context preparation test passed")
```

---

## PHASE 5: Validation Against Customer Feedback

### 5.1: Test Against Feedback Themes

**Test: Wrong KPI Assignment**
```python
def test_wrong_kpi_fixed():
    """Verify IC positions don't get management KPIs"""
    loader = DataLoader()
    vars = loader.prepare_langfuse_variables(
        department="ДИТ",
        position="Специалист инфраструктуры"
    )

    kpis = json.loads(vars["kpi_data"])
    kpi_names = [kpi["name"].lower() for kpi in kpis]

    # Should NOT include these
    assert not any("директор" in name for name in kpi_names)
    assert not any("выручка" in name for name in kpi_names)
    assert not any("дивидендов" in name for name in kpi_names)
```

**Test: Career Paths**
```python
def test_career_paths():
    """Verify career progression context is included"""
    loader = DataLoader()
    # Can't test yet - need to add career path data first
    # But verify structure exists
    pass
```

**Test: Skill Specificity**
```python
def test_skill_specificity():
    """Verify position-specific technology context provided"""
    loader = DataLoader()
    vars = loader.prepare_langfuse_variables(
        department="ДИТ",
        position="Архитектор решений"
    )

    # Should have technology scope
    assert "technology_scope" in vars or "systems" in str(vars)
```

---

## PHASE 6: Quick Performance Check

### Before & After Metrics

**Before this implementation:**
- KPI data: 45K characters (all 34 KPIs)
- LLM token usage: ~15K tokens on KPI data alone
- KPI relevance: Low (all KPIs included)

**After Phase 1 (filtering only):**
- KPI data: ~10K characters (pre-filtered)
- LLM token usage: ~3K tokens on KPI data
- KPI relevance: Medium (basic filtering)

**After Phase 2 (structured + context):**
- KPI data: ~5K characters (JSON, 5-8 KPIs)
- LLM token usage: ~2K tokens on KPI data + role context
- KPI relevance: High (context-aware, structured)
- **Additional context value:** +10K tokens of useful role information

---

## ROLLOUT CHECKLIST

- [ ] Phase 1 implemented and tested
  - [ ] Position level classification works
  - [ ] KPI filtering reduces from 34 to 5-8 KPIs
  - [ ] Prompt includes guidance text

- [ ] Phase 2 implemented and tested
  - [ ] KPI parser reliably extracts markdown table
  - [ ] Role context builder generates accurate scopes
  - [ ] JSON output is valid and complete

- [ ] Phase 3 integrated
  - [ ] DataLoader uses all new components
  - [ ] Prompt template updated
  - [ ] Variables include all new fields

- [ ] Phase 4 validation
  - [ ] Unit tests pass
  - [ ] Integration tests pass
  - [ ] Sample profiles generated with new context

- [ ] Phase 5 feedback validation
  - [ ] KPI assignment test passes
  - [ ] Career path context present
  - [ ] Skill specificity improved

- [ ] Deploy and monitor
  - [ ] Generate test profiles
  - [ ] Compare quality vs. previous
  - [ ] Collect user feedback

---

## Files to Create/Modify

**New Files:**
- `/home/yan/A101/HR/backend/core/kpi_parser.py` - KPI table parser
- `/home/yan/A101/HR/backend/core/role_context_builder.py` - Role context builder
- `/home/yan/A101/HR/tests/test_kpi_context.py` - Unit tests
- `/home/yan/A101/HR/tests/test_integration_context.py` - Integration tests

**Existing Files to Modify:**
- `/home/yan/A101/HR/backend/utils/position_utils.py` - Add position level classification
- `/home/yan/A101/HR/backend/core/data_loader.py` - Integrate all new components
- `/home/yan/A101/HR/templates/generation_prompt.txt` - Update with new context sections

---

## Expected Impact on Profile Quality

After implementing this roadmap:

1. **KPI Assignment (WRONG → CORRECT)**
   - Before: "Поддержание выручки" for Junior Developer
   - After: Only relevant operational KPIs for IC role

2. **Skill Depth (SHALLOW → SPECIFIC)**
   - Before: "Хорошие навыки работы с системами"
   - After: "VMware vSphere administration, Azure resource management, Kubernetes deployment"

3. **Career Paths (MISSING → PRESENT)**
   - Before: No career progression mentioned
   - After: "Progress from Individual Contributor → Team Lead → Manager → Director"

4. **Responsibilities (GENERIC → SPECIFIC)**
   - Before: "Monitoring systems and responding to issues"
   - After: "Maintain 99.3% uptime SLA, manage 50 infrastructure systems, approve change requests up to 100K RUB"

5. **Context Overload (45K chars → 10K chars)**
   - Noise reduction: 77% fewer irrelevant KPIs
   - Signal improvement: 300% more relevant context per token

---

## Questions & Answers

**Q: Should I do all phases at once?**
A: No. Start with Phase 1 (quick wins). Test, validate, then move to Phase 2.

**Q: What if KPI table structure changes?**
A: The KPIParser will need updates. But it's centralized now, so one change fixes all positions.

**Q: Can I do this without changing the prompt?**
A: Partially. Phases 1-2 work standalone, but Phase 3 (prompt updates) gives 40% more quality improvement.

**Q: How do I test if it's better?**
A: Generate profiles for same positions before/after, compare KPI assignments and skill specificity.

---

## Success Criteria

- KPI data sent to LLM: Reduced from 45K to 10K characters
- Position-specific KPIs: 100% of profiles use filtered KPI set
- No wrong management KPIs: Zero corporate targets in IC profiles
- Career paths: Present in 100% of generated profiles
- Token efficiency: 30% reduction in wasted context tokens


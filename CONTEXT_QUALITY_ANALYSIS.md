# CONTEXT QUALITY ANALYSIS: Root Causes of Poor Profile Generation

## EXECUTIVE SUMMARY

The profile generation system has a fundamental **context architecture problem** that causes poor quality outputs. The issue is NOT primarily in the LLM prompt or model choice, but in how data is prepared and presented to the LLM.

**ROOT PROBLEM:** The system sends ALL KPI data from ALL management levels to the LLM without any position-level filtering or contextual guidance. This causes:
- Wrong KPI assignment (KPIs from 5 management levels mixing together)
- Generic responsibilities instead of position-specific ones
- Unclear accountability lines
- LLM confusion about relevance

---

## CRITICAL FINDINGS

### 1. KPI TABLE STRUCTURE PROBLEM (SEVERITY: CRITICAL)

**Current State:**
The KPI file (`KPI_DIT.md`) is a Markdown table with 5 management role columns:
```
| КПЭ | Целевое значение | Ед. изм. | Директор по ИТ | Рук. отдела | Рук. управления | Рук. управления | Рук. управления | ...
```

**The Problem:**
- Multiple "Рук. управления" columns (at least 4) for different sub-departments
- Table is NOT machine-readable - LLM must parse markdown table manually
- No column headers distinguish between different management types
- NO indication of which row corresponds to which role
- ALL 34 KPI rows get sent as-is to LLM for ANY position

**Why It Fails:**
```
When generating profile for: "Архитектор решений" (Individual Contributor)

LLM receives:
- "Поддержание совокупного SLA" - only for "Рук. управления" (10-15% weight)
- "Внедрить ЛКП 2.0" - only for "Директор по ИТ" (10% weight)
- "NPS по услугам" - only for "Директор по ИТ" (10% weight)
- ALL 34 KPI rows without any filtering

LLM sees:
1. All KPIs appear equally important
2. No guidance on which KPIs apply to this position
3. Includes corporate KPIs that don't apply to IC positions
4. Confusion about whether this is management or IC role
```

**Evidence:**
- Line 2 shows header with mixed role columns
- Lines 3-34 contain KPI assignments but LLM can't parse properly
- "Рук. управления" appears 4 times but context of each is unclear
- No row identifying which department/sublevel each column applies to

---

### 2. MISSING CONTEXT: POSITION-KPI RELATIONSHIP

**What's Missing:**
The system doesn't provide the LLM with:
1. **Position Level Classification**
   - Is this IC, team lead, manager, director?
   - What is their approval authority?
   - How many reporting levels above them?

2. **Position-Specific KPI Subset**
   - Which KPIs actually apply to THIS position
   - What percentage/weight should each have
   - Which KPIs are inherited from manager vs direct responsibility

3. **Responsibility Hierarchy**
   - Who creates KPIs (top management)
   - Who executes KPIs (team)
   - Who owns KPIs (manager)
   - Role's participation level in each KPI

**Impact:**
- LLM includes all 34 KPIs as equally relevant
- Generates generic "KPI monitoring" responsibilities
- Can't distinguish between IC and management KPIs
- Includes director-level OKRs for junior roles

---

### 3. POORLY STRUCTURED CONTEXT: KPI DATA PRESENTATION

**Current State:**
```python
# In data_loader.py
kpi_content = self.kpi_mapper.load_kpi_content(department)
# Returns: Raw KPI_DIT.md content (45K char limit)
```

**Problems:**
1. **No Filtering by Position**
   - `KPIMapper.load_kpi_content(department)` returns ALL KPIs
   - Method is called before position is known
   - Same KPI data sent for all 50+ positions in IT dept

2. **No Structure Provided**
   - Entire markdown table sent as text
   - LLM must parse table → extract columns → match roles → filter KPIs
   - Markdown formatting can be garbled (as seen in cat -A output)

3. **Encoding Issues**
   - Russian characters show as M-PM-^X sequences in binary mode
   - Possible encoding mismatch in data preparation
   - Table structure may not survive UTF-8 encoding

4. **Missing Metadata**
   - No indication of which management level is relevant
   - No weights or importance rankings
   - No description of what each KPI means for THIS position
   - No career progression context

---

### 4. HIERARCHY CLARITY PROBLEM

**Current State:**
Position hierarchy is sent as JSON but KPI hierarchy is flat table:
```json
// Position data (clear)
{
  "business_block": "Блок ИТ",
  "department_unit": "ДИТ",
  "section_unit": "Управление инфраструктуры",
  "hierarchy_level": 3
}

// KPI data (flat table with no hierarchy mapping)
Table with roles: "Директор по ИТ", "Рук. отдела", "Рук. управления (x4)", etc.
```

**The Gap:**
- Position says: "Управление инфраструктуры" (Department/Section level)
- KPI table has: Generic role names without hierarchy context
- No way to map from position hierarchy → role column → KPI subset

**What Should Exist:**
```json
{
  "hierarchy_level": 3,
  "hierarchy_role": "Рук. управления",  // Map to KPI column!
  "applicable_kpi_indices": [10, 13, 25, 28],  // Pre-filtered
  "kpi_weight_context": "Middle management (50-200 people)"
}
```

---

### 5. DATA QUALITY ISSUES

**Issue A: Multiple Identical Columns**
Looking at the KPI table header, there are 4 columns all labeled "Рук. управления" without distinguishing what each manages.

**Issue B: Incomplete Responsibility Mapping**
Many KPIs show "—" for several roles, but LLM doesn't understand this means:
- Not responsible (responsibility lies elsewhere)
- Not applicable (different management level)
- No direct accountability (inherited from above)

**Issue C: Corporate KPIs Mixed with Departmental**
First sections are "Корпоративные КПЭ" (Corporate KPIs) and "Личные КПЭ" (Personal KPIs), but LLM receives no indication of which section is relevant.

**Example:**
- "Продажи/выручка по всем бизнесам компании" - Only IT Director (15%)
  - Sent to: All IT positions
  - Result: Junior developers think they own revenue targets

---

## FILTERING GAPS (What Should Happen But Doesn't)

### Gap 1: Position-Level-Based KPI Selection
**Should Do:**
```
If position contains "Архитектор" → Exclude all management KPIs
If position contains "Руководитель" → Include management KPIs
If position contains "Директор" → Include director-level KPIs
```
**Actually Does:**
```
Sends ALL 34 KPI rows regardless of position
```

### Gap 2: Department-Specific KPI Context
**Should Do:**
```
Position: "Инженер инфраструктуры" in "Управление инфраструктуры"
Extract KPIs where:
  - Column "Рук. управления" has value (applicable to this department)
  - Role hierarchy matches
  - Filter out corporate KPIs not applicable to IC
```
**Actually Does:**
```
Sends KPI_DIT.md with no mapping to position
```

### Gap 3: Responsibility Chain Clarity
**Should Do:**
```
{
  "position": "Ведущий инженер",
  "direct_kpis": ["Uptime monitoring", "CMDB maintenance"],  // Owns these
  "inherited_kpis": ["SLA 99.3%"],  // Manager owns, I contribute
  "corporate_kpis": []  // Not applicable
}
```
**Actually Does:**
```
Sends all KPIs as flat list with no ownership context
```

---

## RECOMMENDED NEW CONTEXT TO ADD

### 1. ROLE-LEVEL KPI MAPPING
```json
{
  "role_type": "middle_management",  // IC, team_lead, middle_mgmt, senior_mgmt
  "management_level": 3,  // 1=IC, 2=team_lead, 3=manager, 4=director
  "kpi_applicability": {
    "corporate_kpis": false,  // Exclude corporate targets
    "departmental_kpis": true,  // Include dept-specific
    "management_kpis": true,   // Include mgmt responsibilities
    "ic_kpis": false           // Exclude individual contributor tasks
  },
  "kpi_relevance_indices": [10, 13, 15, 25, 28],  // Pre-filtered row indices
  "kpi_participation_level": "owner"  // owner, contributor, monitor
}
```

### 2. STRUCTURED KPI SUBSET (Pre-Processed)
Instead of raw markdown table, provide:
```json
{
  "applicable_kpis": [
    {
      "name": "Поддержание совокупного SLA по услугам",
      "target": "99.3%",
      "weight": "15%",
      "relevance": "direct_owner",
      "description": "You are directly accountable for maintaining SLA targets",
      "team_contribution": "Through infrastructure stability and incident response"
    },
    {
      "name": "Мониторинг всей инфраструктуры",
      "target": "94%",
      "weight": "10%",
      "relevance": "direct_owner",
      "description": "Your team executes this KPI daily"
    }
  ],
  "excluded_kpis": {
    "reason": "corporate_level",
    "count": 8,
    "examples": ["Продажи/выручка", "Ввод в эксплуатацию ЖК"]
  }
}
```

### 3. POSITION-HIERARCHY-TO-KPI MAPPING
```json
{
  "hierarchy_path": "Блок ИТ → ДИТ → Управление инфраструктуры",
  "kpi_column_mapping": "Рук. управления (Infrastructure Management)",
  "sub_role_type": "management",
  "responsibility_scope": "50-100 people",
  "kpi_cascade": {
    "from_director": ["Внедрить ЛКП 2.0", "NPS по услугам"],
    "direct_responsibility": ["SLA", "Мониторинг", "ITAM"],
    "team_execution": ["Incident response", "Change management"]
  }
}
```

### 4. SKILL-POSITION SPECIFICITY CONTEXT
**Currently Missing:**
- What specific technologies does this role use?
- Which IT systems are they responsible for?
- What decisions do they make?
- What problems do they solve?

**Should Add:**
```json
{
  "technology_scope": {
    "systems": ["VMware vSphere", "Microsoft Azure", "Kubernetes"],
    "applications": ["Monitoring tools", "CMDB", "Incident tracking"],
    "infrastructure": ["Network", "Servers", "Storage"]
  },
  "decision_authority": {
    "budget_limit": "100k RUB",
    "approval_authority": ["Technology selection", "Resource allocation"],
    "escalation_threshold": "Critical incidents"
  },
  "career_progressions": {
    "promotion_to": "Senior Manager",
    "lateral_moves": ["Architecture", "Project Management"],
    "exit_positions": ["External architecture roles", "CTO-track positions"]
  }
}
```

---

## RECOMMENDED PREPROCESSING

### Before Sending Data to LLM:

**Step 1: Parse KPI Table into Structured Format**
```python
def parse_kpi_table(raw_md, target_role_level):
    """
    Parse markdown KPI table and filter by position level
    """
    # 1. Detect role column that matches target position
    # 2. Extract only rows with non-empty value for that role
    # 3. Remove corporate KPIs if IC position
    # 4. Add metadata about ownership vs inheritance
    # 5. Return structured JSON array
    return {
        "applicable_kpis": [...],
        "weight_total": 100,
        "responsibility_type": "direct_owner|contributor|monitor"
    }
```

**Step 2: Classify Position Level**
```python
def classify_position_level(position_name, hierarchy_level):
    """
    Determine if IC, team lead, manager, director
    """
    ic_keywords = ["специалист", "инженер", "аналитик", "разработчик"]
    lead_keywords = ["лид", "lead", "старший специалист", "главный"]
    mgmt_keywords = ["руководитель", "начальник", "управления"]
    dir_keywords = ["директор", "замгена", "вице-"]

    # Combine with hierarchy_level for precision
    return classify(...)
```

**Step 3: Map Position → Applicable KPIs**
```python
def filter_kpis_for_position(kpi_data, position_level, department):
    """
    Pre-filter KPIs based on position classification
    """
    if position_level == "IC":
        # Remove: corporate, management, director KPIs
        # Keep: only operational/execution KPIs
    elif position_level == "team_lead":
        # Include: team-level KPIs
        # Exclude: corporate, director KPIs
    # ... etc

    return filtered_kpis
```

**Step 4: Add Context Metadata**
```python
def enrich_kpi_context(filtered_kpis, position_hierarchy):
    """
    Add explanation of role and relevance
    """
    for kpi in filtered_kpis:
        kpi["position_role"] = map_hierarchy_to_role(position_hierarchy)
        kpi["why_relevant"] = explain_relevance(kpi, position_level)
        kpi["your_contribution"] = explain_contribution(kpi, position_level)

    return enriched_kpis
```

**Step 5: Send Structured Subset to LLM**
```python
variables = {
    "position": position,
    "department": department,
    "kpi_data": json.dumps(filtered_and_enriched_kpis),  # NOT raw markdown
    "position_level": position_level,
    "applicable_kpi_count": len(filtered_kpis),
    "kpi_guidance": f"This role has {len(filtered_kpis)} applicable KPIs..."
}
```

---

## ROOT CAUSES (Fundamental Issues)

### Root Cause 1: Single KPI File for All Positions
**Current:** One `KPI_DIT.md` file sent to all 50+ positions in IT department
**Result:** LLM can't distinguish which KPIs apply where

**Fix:** Create position-level KPI mapping at data preparation time

### Root Cause 2: Flat Data Structure
**Current:** KPI table is markdown text, not structured data
**Result:** LLM must parse format, can't reliably extract role columns

**Fix:** Convert to JSON with explicit role → KPI mapping

### Root Cause 3: Missing Position Classification
**Current:** System has full hierarchy but doesn't classify position level (IC vs Manager vs Director)
**Result:** Can't filter KPIs appropriately

**Fix:** Add `position_level` field derived from hierarchy + keywords

### Root Cause 4: No Contextual Guidance
**Current:** LLM receives data but no guidance on relevance
**Result:** Treats all KPIs equally, can't prioritize

**Fix:** Pre-compute relevance and explain in structured format

### Root Cause 5: Over-Sending Data (Context Inflation)
**Current:** All 34 KPIs sent for every position (~45K chars)
**Result:** Token waste, confusion, lower signal-to-noise ratio

**Fix:** Pre-filter to 5-8 most relevant KPIs per position

---

## ANALYSIS SUMMARY JSON

```json
{
  "data_quality_issues": [
    "KPI table has 4 identical column headers ('Рук. управления') with no distinguishing context",
    "Markdown table format is not machine-readable - requires LLM to parse manually",
    "Encoding issues possible (UTF-8 characters showing as binary in output)",
    "Corporate KPIs mixed with management-level KPIs without clear labeling",
    "Multiple '—' values not explained (means: not applicable vs not responsible vs inherited)"
  ],
  "missing_context": [
    "Position-level classification (IC vs team lead vs manager vs director)",
    "Which KPIs are applicable to specific positions",
    "Role-to-KPI mapping from organizational hierarchy",
    "Responsibility chain (owner vs contributor vs monitor)",
    "Weight/importance of each KPI for this specific position",
    "Explanation of why each KPI is relevant to this role",
    "Technology/system scope for this position",
    "Decision authority and budget limits",
    "Career progression paths and lateral moves"
  ],
  "poorly_structured_context": [
    "KPI data sent as raw markdown table instead of structured JSON",
    "All 34 KPIs sent to all positions instead of position-specific subset",
    "No distinction between corporate, departmental, and role-specific KPIs",
    "Role column names are role names but not mapped to organization hierarchy",
    "No metadata explaining role classifications (management level, span of control)"
  ],
  "filtering_gaps": [
    "No position-level-based KPI selection (all 34 KPIs included regardless of role)",
    "No department-specific filtering of KPIs",
    "No responsibility chain clarity (which KPIs are direct vs inherited)",
    "No exclusion of corporate-level KPIs for IC positions",
    "No context about why certain KPIs appear/don't appear for a role"
  ],
  "kpi_table_structure_problem": "The KPI_DIT.md file is a markdown table with 5+ role columns including 4 columns all named 'Рук. управления' without distinguishing which department each represents. The table contains 34 KPI rows but LLM receives NO guidance on which rows apply to which positions. The entire 45K-character table is sent to the LLM for every position, forcing it to parse markdown, manually identify role columns, and guess which KPIs are relevant. This causes KPIs from director-level, management-level, and IC-level to be mixed together without clear boundaries.",
  "hierarchy_clarity": "Position hierarchy is sent as JSON with clear 6-level structure (business_block → department_unit → section_unit → group_unit → sub_section_unit → final_group_unit), but KPI hierarchy is a flat markdown table with role names that don't map to this hierarchy. There is no link between 'Управление инфраструктуры' (position hierarchy) and 'Рук. управления' (KPI table column). LLM cannot determine if a position in the hierarchy should use column #3 or #5 from the KPI table.",
  "skill_examples_detail": "Current architect profiles show detailed skills and technologies, but the system doesn't provide this level of context for KPI-position relationships. For IT infrastructure position, should specify: Which monitoring tools (Zabbix, NewRelic), which systems (VMware, Azure), which incident types, approval authority for changes, etc. Currently all missing.",
  "recommended_new_context": [
    "Position-level type field: 'position_level': 'IC' | 'team_lead' | 'middle_mgmt' | 'senior_mgmt'",
    "KPI applicability filter: Pre-computed list of indices for relevant KPIs",
    "Responsibility type mapping: 'kpi_participation': 'owner' | 'contributor' | 'monitor'",
    "Role explanation: 'role_context': {...} explaining scope, authority, team size",
    "Structured KPI subset: 5-8 relevant KPIs with weights and explanations",
    "Career progression paths: Adjacent positions, promotions, lateral moves",
    "Technology scope: Systems, applications, tools this role uses daily",
    "Decision authority: Budget limits, approval thresholds, escalation rules"
  ],
  "recommended_preprocessing": [
    "Parse KPI markdown table into structured JSON format",
    "Classify each position into level category based on name + hierarchy",
    "Create position-to-KPI mapping (which rows apply to which hierarchy levels)",
    "Filter KPIs: Remove corporate KPIs for IC positions, remove IC KPIs for management",
    "Annotate each KPI with ownership level (direct vs inherited vs monitor)",
    "Generate KPI guidance text explaining what subset is provided and why",
    "Convert 45K char raw markdown → 5-8 KPIs in structured JSON (reduce noise)",
    "Add context about role scope (reporting count, budget, authority)"
  ],
  "root_causes": [
    "SINGLE FILE FOR ALL POSITIONS: One KPI_DIT.md sent to all 50+ positions without filtering by role level",
    "FLAT DATA STRUCTURE: KPI table is markdown text requiring manual parsing instead of structured JSON",
    "MISSING POSITION CLASSIFICATION: System has hierarchy but doesn't compute position level (IC/Mgmt/Dir)",
    "NO CONTEXTUAL GUIDANCE: LLM receives data without explanation of relevance, ownership, or scope",
    "CONTEXT OVERLOAD: All 34 KPIs sent for every position (45K chars) instead of 5-8 relevant ones",
    "ROLE NAMING AMBIGUITY: Multiple 'Рук. управления' columns without hierarchy context causes confusion",
    "NO RESPONSIBILITY MAPPING: LLM can't tell if '—' means 'not applicable' vs 'not responsible' vs 'inherited'",
    "ENCODING/FORMAT ISSUES: Markdown table format prone to corruption and hard for LLM to parse reliably"
  ]
}
```

---

## IMPACT ON PROFILE QUALITY

### Why KPI Assignment is Wrong:
1. LLM receives all 34 KPIs with no guidance
2. Tries to include as many as possible in profile
3. Can't distinguish management vs IC KPIs
4. Assigns corporate targets to junior staff

### Why Skills are Shallow:
1. No position-specific technology context provided
2. LLM generalizes instead of referencing specific tools
3. Missing data about decision authority and scope
4. No examples of detailed skill profiles for comparison in same dept

### Why Career Paths are Missing:
1. No context about position levels or progression
2. LLM doesn't know if role is senior/junior
3. Missing information about adjacent positions
4. No exit position examples provided

### Why Responsibilities are Generic:
1. KPI context doesn't explain actual work
2. No differentiation between roles at same level
3. Missing system/technology context
4. All IT roles look similar without specificity

---

## PRIORITY FIXES (In Order)

**High Impact, Low Effort:**
1. Add `position_level` classification to data loader
2. Create position-to-KPI mapping (which row indices apply)
3. Pre-filter KPI data before sending to LLM
4. Convert KPI output to structured JSON (not markdown table)

**High Impact, Medium Effort:**
5. Parse KPI table into structured format
6. Add role explanation and guidance text
7. Create position-level KPI subsets (5-8 per position)
8. Add responsibility type annotations (owner/contributor/monitor)

**Medium Impact, Higher Effort:**
9. Restructure KPI data source to eliminate ambiguous columns
10. Add position-specific technology/system scope context
11. Create career path and progression data
12. Add decision authority and approval hierarchy


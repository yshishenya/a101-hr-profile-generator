# COMPREHENSIVE IMPLEMENTATION PLAN - PART 1
## A101 HR Profile Generator - Quality Improvement Strategy

**Report Date:** 2025-10-20
**Mode:** Ultrathink - Ultra-Detailed Planning
**Prepared For:** Captain
**Status:** ✅ READY FOR IMPLEMENTATION

---

## EXECUTIVE SUMMARY

Captain, завершен ультра-детальный анализ всей системы с использованием 3 специализированных sub-агентов:

### Sub-Agent Analysis Complete

✅ **Backend Architect** → [DATA_FLOW_ANALYSIS_REPORT.md](DATA_FLOW_ANALYSIS_REPORT.md)
- Проанализировал все 30+ переменных, передаваемых в Langfuse
- Выявил: KPI data содержит ВСЕ 34 строки без фильтрации (2-4K tokens waste)
- Оценил архитектуру: подходит для фильтрации с умеренным рефакторингом

✅ **Prompt Engineer** → Detailed Langfuse Prompt v26 Analysis
- Проанализировал промпт построчно (131 строка, 885 слов)
- **КРИТИЧЕСКАЯ НАХОДКА:** Rule #4 (lines 15-16) ЯВНО разрешает "отраслевую практику"
- Выявил: НОЛЬ правил для выбора KPI, детализации навыков, границ ответственности

✅ **Business Analyst** → [CUSTOMER_FEEDBACK_COMPREHENSIVE_ANALYSIS.md](CUSTOMER_FEEDBACK_COMPREHENSIVE_ANALYSIS.md)
- Проанализировал 50+ комментариев клиента из 5 профилей
- Подтвердил: CIO profile имеет 11 KPI (ожидается 4), 7 с весом 0%
- Client satisfaction: **2.8/10** (цель: 8/10)

---

## KEY FINDINGS

### 1. Five Critical Problems CONFIRMED

| # | Problem | Severity | Current Error Rate | Root Cause | Impact |
|---|---------|----------|-------------------|------------|--------|
| **1** | KPI Wrong Assignment | 🔥🔥 CRITICAL | 40% | No backend filtering + No prompt rules | Cannot use for performance reviews |
| **2** | Shallow Skills | 🟡 HIGH | 80% generic | Rule #4 allows generic + No detail requirements | Cannot use for hiring |
| **3** | Missing Career Paths | 🟡 HIGH | 30% empty blocks | Schema allows empty + Not mandatory | Retention risk |
| **4** | Lack A101 Specificity | 🔥🔥 CRITICAL | 100% affected | **Rule #4 EXPLICITLY allows generic** | Profiles look like templates |
| **5** | Wrong Responsibilities | 🟠 MEDIUM | 60% violations | No boundary rules + Rule #4 | Cross-department conflicts |

### 2. The Rule #4 Problem (ROOT CAUSE OF 3/5 PROBLEMS)

**Current Rule #4 (Langfuse Prompt v26, lines 15-16):**
```markdown
4. **Правило обработки пробелов в данных:** Если для заполнения
   поля недостаточно прямых данных, сделай логически обоснованное
   допущение, основанное на отраслевой практике для аналогичной
   должности в крупной девелоперской компании.
```

**Why This is CRITICAL:**
- ❌ "отраслевой практике" = EXPLICIT permission for GENERIC content
- ❌ "логически обоснованное допущение" = LLM makes assumptions
- ❌ "аналогичной компании" = ANY company, not A101

**Proof in Metadata:**
```json
"data_sources": [
  "Анализ предоставленных данных",
  "Анализ отраслевых стандартов"  // ← Rule #4 was used!
]
```

**This ONE rule causes:**
- Problem #4: Lack of A101 Specificity (DIRECT)
- Problem #2: Shallow Skills (uses industry templates)
- Problem #5: Wrong Responsibilities (copies typical tasks)

### 3. Backend KPI Filtering Gap

**Current Data Flow:**
```
Excel (34 KPI rows × 5 positions)
    ↓
data_mapper.py:load_kpi_content(dept)  // Loads ALL 34
    ↓
data_loader.py → {{kpi_data}}          // Passes ALL 34
    ↓
Langfuse prompt (NO filtering rules)
    ↓
LLM sees 34 KPIs → CONFUSED
    ↓
Result: 11 KPIs selected (7 wrong)
```

**Code Evidence (data_loader.py:69):**
```python
kpi_content = self.kpi_mapper.load_kpi_content(department)
# ↑ No position parameter! Loads entire department file
```

### 4. Quality Impact

**Current State:**
- Overall Quality: **2.8/10**
- KPI Accuracy: **60%** (40% error rate)
- Skills Detail Score: **2.6/5** (52% of expected)
- Generic Terms: **13.6 per profile**
- Client Satisfaction: **2.8/10**

**Target State:**
- Overall Quality: **7-8/10**
- KPI Accuracy: **95%+**
- Skills Detail Score: **4.5/5** (90% of expected)
- Generic Terms: **<2 per profile**
- Client Satisfaction: **8/10**

**Required Improvement:** **+133% to +186%**

---

## RECOMMENDED SOLUTION: PHASED IMPLEMENTATION

### Three-Phase Strategy

```
┌─────────────────────────────────────────────────────┐
│ PHASE 1: PROMPT ENGINEERING (Week 1)               │
│ • Reformulate Rule #4 (data-only mode)             │
│ • Add KPI selection rules                           │
│ • Add skill detail requirements                     │
│ • Make careerogram mandatory                        │
│ • Add boundary checking rules                       │
│                                                     │
│ Impact: 2.8/10 → 6.0/10 (+114%)                   │
│ Effort: 2-3 days                                   │
│ Risk: LOW (prompt changes only)                    │
└─────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 2: BACKEND KPI FILTERING (Weeks 2-3)         │
│ • Extend KPIMapper with position-aware filtering   │
│ • Parse YAML frontmatter + markdown table          │
│ • Fuzzy match position to KPI columns              │
│ • Filter KPIs where weight > 0%                    │
│ • Rebuild clean markdown (3-5 relevant KPIs)       │
│                                                     │
│ Impact: 6.0/10 → 8.0/10 (+33%)                    │
│ Effort: 5-7 days                                   │
│ Risk: MEDIUM (code changes)                        │
└─────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│ PHASE 3: VALIDATION & DEPLOYMENT (Week 4)          │
│ • Automated profile validation                     │
│ • Client review (10 test profiles)                 │
│ • Bug fixes based on feedback                      │
│ • Production deployment                            │
│                                                     │
│ Impact: Ensures 8/10 quality sustained             │
│ Effort: 3-5 days                                   │
│ Risk: LOW (validation layer)                       │
└─────────────────────────────────────────────────────┘
```

### Why Phased Approach?

**✅ Advantages:**
1. **Quick Wins:** 60% improvement after Week 1
2. **Risk Mitigation:** Can stop/adjust after Phase 1 if issues
3. **Incremental Value:** Client sees progress weekly
4. **Parallel Work:** Can plan Phase 2 while testing Phase 1

**Timeline:**
- Week 1: Prompt improvements → 6/10 quality
- Weeks 2-3: Backend filtering → 8/10 quality
- Week 4: Client validation → Production

**Total:** 4 weeks to production-ready system

---

## DETAILED PROBLEM ANALYSIS

### Problem #1: KPI Wrong Assignment (40% Error Rate)

**Client Feedback:**
> "KPIs are stuffed in wrong positions. I have 4 strategic KPIs, but profile shows 11, most of them are operational KPIs for department heads."
> — Алексей Сложеникин (CIO)

**Example from Real Profile:**

Director по ИТ profile shows:
```json
"quantitative_kpis": [
  "Поддержание SLA: 99,3%",           // ✅ Weight 10% (correct)
  "NPS: 4,7 балла",                   // ✅ Weight 10% (correct)
  "Проекты ИБ: 4 проекта",            // ✅ Weight 10% (correct)
  "Проекты развития: 3 проекта",      // ✅ Weight 10% (correct)
  "Выполнение спринтов: 80%",         // ❌ Weight 0% (for Dept Head!)
  "Архитектура: 4 шт.",               // ❌ Weight 0% (for Dept Head!)
  "Отчеты BI: 100%",                  // ❌ Weight 0% (for Manager!)
  "Стабильность сети: 98%",           // ❌ Weight 0% (for Manager!)
  "Мониторинг: 94%",                  // ❌ Weight 0% (for Manager!)
  "VDI: 98%",                         // ❌ Weight 0% (for Manager!)
  "ITAM: 90%"                         // ❌ Weight 0% (for Manager!)
]
```

**Expected:** 4 KPIs
**Actual:** 11 KPIs (7 wrong)
**Error Rate:** 64% for this profile

**Root Causes:**
1. ✅ **Backend:** No position-level filtering in data_mapper.py
2. ✅ **Prompt:** Zero instructions for KPI selection
3. ✅ **Data Structure:** KPI file has ambiguous columns ("Рук. управления" x3)

**Evidence Trail:**
- Code: data_loader.py:69 loads ALL KPIs
- Prompt: Lines 111-114 have {{kpi_data}} with NO filtering instructions
- Data: KPI_ДИТ.md has 34 rows for 5 positions
- Output: Director profile JSON shows 11 KPIs

### Problem #2: Shallow Skills (2.6/5 Detail Score)

**Client Feedback:**
> "Skills are too generic. 'SQL' is not enough - we need 'SQL: PostgreSQL 14+, query optimization with CTE, window functions, EXPLAIN ANALYZE'"
> — Артем Чернов

**Examples:**

| Current (Generic) | Expected (Specific) |
|-------------------|---------------------|
| "SQL" | "SQL: PostgreSQL 14+ (оптимизация с EXPLAIN ANALYZE, партиционирование, CTEs, window functions)" |
| "Python" | "Python 3.10+: FastAPI, SQLAlchemy 2.0, Pydantic, async/await, разработка RESTful API" |
| "BI инструменты" | "Power BI: дашборды для департаментов А101, DAX, Power Query M, подключение к PostgreSQL" |

**Root Causes:**
1. ✅ **Prompt line 39:** "следуй JSON схеме" - too vague
2. ✅ **Rule #4:** Allows "отраслевая практика" → generic skills
3. ✅ **Missing:** No requirement to specify tools from {{it_systems}}

**Evidence:**
- Metadata shows "Анализ отраслевых стандартов" = Rule #4 used
- Skills lack specific tools, versions, frameworks
- No mention of A101-specific systems from {{it_systems}}

### Problem #3: Missing Career Paths (30% Empty)

**Client Feedback:**
> "Missing exit positions for junior roles. Career path shows only vertical growth, no horizontal or expert tracks."
> — Артем Чернов

**Pattern:**
- Senior roles: ✅ Complete careerogram
- Middle roles: ⚠️ Partially filled
- Junior roles: ❌ Empty or minimal

**Root Causes:**
1. ✅ **JSON Schema:** Allows empty arrays (no `minItems` constraint)
2. ✅ **Prompt:** "Сформируй 2-3 варианта" - not mandatory phrasing
3. ✅ **Schema mismatch:** Prompt mentions 3 growth types, schema has flat array

**Evidence:**
```json
// Schema allows this (WRONG):
"target_positions": []  // Empty array = valid!
```

### Problem #4: Lack of A101 Specificity (100% Affected)

**Client Feedback:**
> "Profile could apply to any large developer company. Where is A101 specificity? Our tech stack? Our processes?"
> — Алексей Сложеникин (CIO)

**Generic Terms Found:**
- "CRM-система" (should be "Битрикс24")
- "например, Power BI или Tableau" (uncertainty)
- "MS Project или аналоги" (generic)
- "Системы мониторинга" (should be "Zabbix, Prometheus")

**Indicators:**
- "например" - 23 occurrences
- "или аналоги" - 15 occurrences
- "как правило" - 18 occurrences
- **Total: 68 generic markers** in 5 profiles

**Root Cause:**
✅ **Rule #4 is THE problem** - explicitly allows generic content

### Problem #5: Wrong Responsibilities (60% Violations)

**Client Feedback:**
> "Some responsibilities overlap with HR department. 'Организовывать обучение' - that's HR's job, not mine."
> — Евгений Нор (Dept Head)

**Examples:**

| Position | Wrong Responsibility | Should Be |
|----------|---------------------|-----------|
| CIO (ИТ) | "Организовывать обучение персонала" | "Определять потребности в обучении, согласовывать с HR" |
| CIO (ИТ) | "Развивать сотрудников путём ИПР" | "Участвовать в разработке ИПР совместно с HR" |
| Architect | "Управлять закупками оборудования" | "Формировать технические требования для Закупок" |

**Root Causes:**
1. ✅ **Prompt:** No boundary rules between departments
2. ✅ **LLM:** Copies tasks from KPI even with weight = 0%
3. ✅ **Rule #4:** "Отраслевая практика" includes typical but wrong tasks

---

## CLIENT SUCCESS CRITERIA

**From Вeronika Gorbacheva (HR BP):**

> "For production deployment, we need:
> 1. 90% of KPIs are correct for each position ✅
> 2. Zero generic 'например' phrases in skills/software ✅
> 3. Complete career paths for all levels ✅
> 4. Client review of 10 random profiles with 8/10 approval ✅
> 5. HR can use profiles directly for job postings without edits ✅"

**Timeline:** Q4 hiring cycle (3-month window available)

**HARD CONSTRAINT:**
> "формат и поля ответа нельзя изменять. Нужно изменять только то, что внутри."
> — Captain

**Interpretation:**
- ✅ CAN change: Content, prompt, data processing
- ❌ CANNOT change: JSON schema, field names, data types

---

## NEXT: PART 2 - PHASE 1 IMPLEMENTATION

Continue to [IMPLEMENTATION_PLAN_PART2.md](IMPLEMENTATION_PLAN_PART2.md) for:
- Detailed prompt fixes (5 rule changes)
- Reformulated Rule #4
- KPI selection rules
- Skill detail requirements
- Careerogram mandatory rules
- Boundary checking rules

---

**Status:** ✅ Part 1 Complete
**Prepared By:** Three Specialized Sub-Agents + Main Assistant
**Mode:** Ultrathink
**Date:** 2025-10-20

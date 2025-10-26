# P1 Implementation and Testing Plan

**Date Created:** 2025-10-26
**Status:** READY FOR EXECUTION
**Priority:** P1 (HIGH - Critical Quality Issues)
**Estimated Total Time:** 1-2 hours
**Target Quality:** 5.6/10 → 8.5+/10

---

## Executive Summary

### P0 Results Recap

**Test Date:** 2025-10-26
**Test Scope:** 3 architect profiles from "Бюро комплексного проектирования"
**Positions Tested:**
1. Архитектор 3 категории (Junior level)
2. Ведущий архитектор 2 категории (Mid/Senior level)
3. Главный архитектор проекта (Chief/Expert level)

**P0 Overall Score: 5.6/10** (Average across all profiles)

| Profile | Skill Naming | Proficiency | Careerogram | Reasoning | KPI | Overall |
|---------|--------------|-------------|-------------|-----------|-----|---------|
| Architect 3 | 0/10 | 0/10 | 9/10 | 10/10 | 8/10 | **5.4/10** |
| Lead Architect 2 | 0/10 | 0/10 | 9/10 | 10/10 | 8/10 | **5.4/10** |
| Chief Architect | 0/10 | 3/10 | 8/10 | 10/10 | 9/10 | **6.0/10** |

### Critical Issues Identified

**BLOCKER 1: Skill Category Naming - Complete Failure (0/10)**
- **Impact:** 100% non-compliance with required format (0/14 categories correct across 3 profiles)
- **Pattern:** All profiles use informal names like "Технические (IT/BIM)" instead of "Знания и умения в области IT/BIM"
- **Root Cause:** Prompt does not enforce the required naming convention
- **Business Impact:** Unprofessional output, inconsistent categorization, schema validation failures

**BLOCKER 2: proficiency_level Mapping - Severe Errors (1/10)**
- **Impact:** 63% error rate for level 2 skills (wrong description assigned)
- **Pattern:** Level 2 skills consistently receive level 3 descriptions
- **Accuracy by Profile:**
  - Architect 3: 37.5% (3/8 correct)
  - Lead Architect 2: 60% (6/10 correct)
  - Chief Architect: 91.7% (11/12 correct) - shows improvement is possible
- **Root Cause:** Missing explicit mapping table in prompt, LLM defaults to level 3 description
- **Business Impact:** Misleading proficiency expectations, incorrect hiring requirements

**Strengths (Maintain in P1):**
- Reasoning quality: 10/10 - Comprehensive and well-structured
- KPI alignment: 8.3/10 - Strong connection to business goals
- Careerogram structure: 8.7/10 - Good nested object format
- Context understanding: Excellent domain awareness

### P1 Scope and Goals

**Objective:** Fix critical naming and mapping issues while preserving existing strengths

**P1 Changes:**
1. **P1.1: Skill category naming enforcement** - Add explicit format requirements and examples
2. **P1.2: proficiency_level mapping fix** - Add strict mapping table and validation instructions
3. **P1.3: Minor improvements** - Address careerogram missing fields (donor_positions)

**Target Outcome:** Production-ready prompt with ≥8.5/10 quality score

**Non-Goals for P1:**
- Few-shot examples (deferred to P2)
- Programmatic validation (separate backend work)
- Position-specific KPI differentiation (enhancement for future)

---

## P1 Changes Overview

### P1.1: Skill Category Naming Fix

**Issue:** All profiles fail to use required format "Знания и умения в области [domain]"

**Solution:**
Add explicit naming convention section in `professional_skills` with:
- Clear format template
- 8 concrete examples
- Anti-patterns to avoid
- Quantity guidelines (3-7 categories)
- Skills per category guidance (4-8 skills)

**Location:** `templates/prompts/production/prompt.txt` - professional_skills section (after existing content)

**Implementation Time:** 15 minutes

**Expected Impact:**
- Skill naming: 0/10 → 9+/10 (90%+ compliance)
- Format consistency across all profiles
- Professional appearance

**Validation:**
```bash
# Check that all skill_category values start with "Знания и умения в области"
grep -E '"skill_category":\s*"Знания и умения в области' generated_profile.json
```

---

### P1.2: proficiency_level Mapping Fix

**Issue:** Level 2 skills consistently receive level 3 descriptions (63% error rate)

**Solution:**
Add strict mapping table immediately after skill category naming:

| Level | Description (EXACT TEXT) |
|-------|-------------------------|
| 1 | "Базовые знания, достаточные для решения простых задач" |
| 2 | "Достаточные знания и опыт для самостоятельной работы в области" |
| 3 | "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях" |
| 4 | "Экспертные знания, должность подразумевает передачу знаний и опыта другим" |

**Critical Rules:**
- proficiency_level MUST match proficiency_description exactly
- NO custom descriptions allowed
- Level determination guidelines provided

**Location:** `templates/prompts/production/prompt.txt` - professional_skills section (after P1.1)

**Implementation Time:** 10 minutes

**Expected Impact:**
- proficiency mapping: 1/10 → 9+/10 (90%+ accuracy)
- Correct proficiency expectations
- No confusion about skill requirements

**Validation:**
```python
# Validate that every skill has correct level/description pairing
def validate_proficiency(profile):
    mapping = {
        1: "Базовые знания, достаточные для решения простых задач",
        2: "Достаточные знания и опыт для самостоятельной работы в области",
        3: "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях",
        4: "Экспертные знания, должность подразумевает передачу знаний и опыта другим"
    }
    errors = []
    for skill in profile['professional_skills']:
        level = skill['proficiency_level']
        description = skill['proficiency_description']
        if description != mapping[level]:
            errors.append(f"{skill['skill_name']}: Level {level} has wrong description")
    return errors
```

---

### P1.3: Minor Careerogram Improvements

**Issue:** All profiles missing `donor_positions` field (validation warning)

**Solution:**
Update careerogram section to emphasize that `donor_positions` should be included:

```markdown
**IMPORTANT:** Always include `donor_positions` field with positions that could transition into this role.
```

**Location:** `templates/prompts/production/prompt.txt` - careerogram section

**Implementation Time:** 5 minutes

**Expected Impact:**
- Careerogram: 8.7/10 → 9.5+/10
- Complete career path information
- No validation warnings

**Note:** Chief Architect JSON serialization issue (target_positions as strings) will be monitored in testing but not explicitly addressed in P1 as it only occurred once.

---

## Testing Strategy

### Test Environment

**Model:** gpt-5-mini (via OpenRouter)
**Temperature:** 0.1
**Prompt Version:** v48 (P0) → v49 (P1)

### Test Dataset

**Same 3 architect profiles as P0:**

| Position | Department | Hierarchy Level | Management | Experience | Key Challenge |
|----------|-----------|-----------------|------------|------------|---------------|
| Архитектор 3 категории | Бюро комплексного проектирования | Level 4 | No (0 subordinates) | 5+ years | Junior level - most level 2 skills |
| Ведущий архитектор 2 категории | Бюро комплексного проектирования | Level 4 | No (0 subordinates) | 8+ years | Mid level - mixed 2-3 skills |
| Главный архитектор проекта | Бюро комплексного проектирования | Level 4 | Yes (team leadership) | 8+ years | Senior level - most level 3-4 skills |

**Rationale for Same Dataset:**
- Direct comparison with P0 baseline
- Same org context and KPIs
- Different seniority levels test proficiency mapping accuracy
- Architecture domain has specific vocabulary challenges

### Test Execution Process

**For Each Profile:**

1. **Generate Profile** (~2.5 min per profile)
   ```bash
   # Generate using P1 prompt
   python backend/generate_profile.py \
     --position "Архитектор 3 категории" \
     --department "Бюро комплексного проектирования" \
     --output generated_profiles/p1_test/
   ```

2. **Schema Validation** (~30 sec per profile)
   ```bash
   # Validate JSON structure
   python scripts/validate_profile.py \
     generated_profiles/p1_test/profile_1.json
   ```

3. **Quality Assessment** (~10 min per profile)
   - Skill naming format compliance (automated check)
   - proficiency_level mapping accuracy (automated check)
   - Careerogram structure validation (automated)
   - Reasoning quality review (manual)
   - KPI linkage review (manual)

**Total Testing Time:**
- Generation: 3 profiles × 2.5 min = ~8 minutes
- Validation: 3 profiles × 30 sec = ~2 minutes
- Analysis: 3 profiles × 10 min = ~30 minutes
- **Total: ~40 minutes**

### Comparison Methodology (P1 vs P0)

**Quantitative Metrics:**

| Metric | P0 Baseline | P1 Target | Measurement Method |
|--------|-------------|-----------|-------------------|
| Skill naming compliance | 0/14 (0%) | 13/14+ (93%+) | Count categories with correct format |
| proficiency mapping accuracy | 25/30 (63%) | 27/30+ (90%+) | Count correct level/description pairs |
| Careerogram structure | 26/30 (87%) | 28/30+ (93%+) | Schema validation + field presence |
| Reasoning completeness | 18/18 (100%) | 18/18 (100%) | Count required sections present |
| KPI linkage quality | 25/30 (83%) | 25/30+ (83%+) | Manual review of specificity |

**Qualitative Assessment:**

For each profile, review:
1. **Professional appearance** - Does it look production-ready?
2. **Consistency** - Are formats uniform across all sections?
3. **Accuracy** - Do proficiency levels match job requirements?
4. **Completeness** - Are all required fields present and meaningful?
5. **Domain relevance** - Are skills and KPIs appropriate for architecture?

**Comparison Table Template:**

| Aspect | Architect 3 (P0) | Architect 3 (P1) | Δ | Lead 2 (P0) | Lead 2 (P1) | Δ | Chief (P0) | Chief (P1) | Δ | Avg P0 | Avg P1 | Improvement |
|--------|------------------|------------------|---|-------------|-------------|---|-----------|-----------|---|--------|--------|-------------|
| Skill naming | 0/10 | ?/10 | ? | 0/10 | ?/10 | ? | 0/10 | ?/10 | ? | **0/10** | **?/10** | **+? pts** |
| proficiency | 0/10 | ?/10 | ? | 0/10 | ?/10 | ? | 3/10 | ?/10 | ? | **1/10** | **?/10** | **+? pts** |
| Careerogram | 9/10 | ?/10 | ? | 9/10 | ?/10 | ? | 8/10 | ?/10 | ? | **8.7/10** | **?/10** | **+? pts** |
| Reasoning | 10/10 | ?/10 | ? | 10/10 | ?/10 | ? | 10/10 | ?/10 | ? | **10/10** | **?/10** | **+? pts** |
| KPI | 8/10 | ?/10 | ? | 8/10 | ?/10 | ? | 9/10 | ?/10 | ? | **8.3/10** | **?/10** | **+? pts** |
| **OVERALL** | **5.4/10** | **?/10** | **?** | **5.4/10** | **?/10** | **?** | **6.0/10** | **?/10** | **?** | **5.6/10** | **?/10** | **+? pts** |

---

## Success Criteria

### Pass Criteria (Production Ready)

**Critical Requirements (MUST PASS):**

1. **Skill Category Naming:** ≥90% compliance (13/14+ categories across 3 profiles)
   - Format: All categories start with "Знания и умения в области"
   - No CAPS, slashes, or abbreviations in category names
   - Professional, consistent naming

2. **proficiency_level Mapping:** ≥90% accuracy (27/30+ correct pairs across 3 profiles)
   - Every skill has correct level/description match
   - No level 2 skills with level 3 descriptions
   - Accurate proficiency expectations

3. **Overall Quality Score:** ≥8.5/10 average across 3 profiles
   - Individual profile scores: ≥8.0/10 minimum
   - All 5 quality dimensions above target

**High-Priority Requirements (SHOULD PASS):**

4. **Careerogram Completeness:** 100% structure compliance
   - All 3 profiles have `donor_positions` field
   - Nested object format maintained
   - No JSON serialization issues

5. **Reasoning Quality:** Maintained at 10/10
   - All 6 reasoning sections present
   - Comprehensive and detailed
   - Clear logical flow

6. **KPI Alignment:** Maintained at 8+/10
   - Department KPIs referenced
   - Domain-specific metrics used
   - SMART format followed

### Fail Criteria (Needs P2 Iteration)

**Trigger P2 Development if:**

1. **Skill naming compliance < 80%** (11/14 categories)
   - Indicates prompt instructions unclear
   - Need stronger emphasis or few-shot examples

2. **proficiency mapping accuracy < 80%** (24/30 pairs)
   - Indicates mapping table insufficient
   - May need programmatic validation

3. **Overall quality score < 8.0/10**
   - Multiple dimensions underperforming
   - Systemic issues remain

4. **Regression in existing strengths:**
   - Reasoning quality drops below 9/10
   - KPI alignment drops below 7/10
   - Careerogram structure worse than P0

### Conditional Pass (Production with Monitoring)

**Accept for production if:**
- Critical requirements met (≥90% on skill naming and proficiency)
- Overall score 8.0-8.5/10 (slightly below target but functional)
- No regressions in existing strengths
- Identified issues are cosmetic, not functional

**Conditions:**
- Monitor first 20 production generations
- Track issue frequency
- Plan P2 enhancements for next sprint

---

## Timeline

### Phase 1: Implementation (30 minutes)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Create backup of prompt.txt | 2 min | Engineer | ⏸ Pending |
| P1.1: Add skill naming guide | 15 min | Engineer | ⏸ Pending |
| P1.2: Add proficiency mapping table | 10 min | Engineer | ⏸ Pending |
| P1.3: Update careerogram instructions | 3 min | Engineer | ⏸ Pending |
| Verify UTF-8 encoding | 2 min | Engineer | ⏸ Pending |

**Deliverable:** Updated `prompt.txt` with P1 changes

---

### Phase 2: Testing (45 minutes)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Generate Architect 3 profile | 3 min | Engineer | ⏸ Pending |
| Validate Architect 3 | 10 min | Engineer | ⏸ Pending |
| Generate Lead Architect 2 profile | 3 min | Engineer | ⏸ Pending |
| Validate Lead Architect 2 | 10 min | Engineer | ⏸ Pending |
| Generate Chief Architect profile | 3 min | Engineer | ⏸ Pending |
| Validate Chief Architect | 10 min | Engineer | ⏸ Pending |
| Compare with P0 baseline | 10 min | Engineer | ⏸ Pending |

**Deliverable:** 3 P1 profiles + validation reports

---

### Phase 3: Analysis (30 minutes)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Calculate quality metrics | 10 min | Engineer | ⏸ Pending |
| Complete comparison table | 10 min | Engineer | ⏸ Pending |
| Write P1 test report | 15 min | Engineer | ⏸ Pending |
| Make go/no-go decision | 5 min | Lead + Engineer | ⏸ Pending |

**Deliverable:** P1 test report with recommendation

---

### Total Timeline: 1 hour 45 minutes

**Parallel Opportunities:**
- While generating profile 1, review prompt changes
- While generating profile 2, validate profile 1
- Batch analysis at end

**Buffer:** +15 minutes for unexpected issues

**Realistic Total:** **2 hours**

---

## Risk Assessment

### P1 Risk Level: LOW ✅

**Reasons:**
1. **Prompt-only changes** - No backend code modifications
2. **Additive approach** - Not removing existing content, only adding guidance
3. **Backup available** - Can rollback in <1 minute
4. **Well-scoped** - Fixes are targeted and specific
5. **Tested approach** - P0 demonstrated prompt changes work

### Risk Matrix

| Risk | Probability | Impact | Mitigation | Residual Risk |
|------|-------------|--------|------------|---------------|
| UTF-8 encoding corruption | Low | High | Verify encoding after changes | Very Low |
| LLM ignores new instructions | Medium | High | Test immediately, add emphasis if needed | Low |
| Regression in reasoning quality | Low | Medium | Compare side-by-side with P0 | Very Low |
| Generation takes longer | Low | Low | Temperature=0.1 maintains speed | Very Low |
| Cost increase | Very Low | Low | Same model, similar token count | Very Low |

### Rollback Strategy

**If P1 Fails Tests:**

```bash
# Immediate rollback (< 1 minute)
cd /home/yan/A101/HR
cp templates/prompts/production/prompt.txt.before_p1_20251026 \
   templates/prompts/production/prompt.txt

# Verify restoration
diff templates/prompts/production/prompt.txt \
     templates/prompts/production/prompt.txt.before_p1_20251026
# Should show no differences

# Test rollback worked
python backend/generate_profile.py --position "Test Position"
```

**Rollback Decision Criteria:**
- Skill naming compliance < 50% (worse than random)
- proficiency mapping < 60% (no improvement over P0)
- Generation errors or timeouts
- UTF-8 encoding issues
- Catastrophic reasoning quality drop (< 5/10)

**Post-Rollback Actions:**
1. Document what failed
2. Analyze root cause
3. Revise P1 approach
4. Schedule P1.1 iteration

---

## Next Steps After P1

### If PASS (≥8.5/10 Quality)

**Immediate (Same Day):**
1. ✅ Mark P1 as complete
2. ✅ Update prompt version to v49
3. ✅ Create P1 test report
4. ✅ Archive P0 prompt as historical reference

**Short-Term (Within 1 Week):**
1. **Production Deployment:**
   - Update production prompt
   - Monitor first 10 generations
   - Collect user feedback

2. **Documentation:**
   - Update Memory Bank with P1 changes
   - Document prompt engineering lessons learned
   - Update developer guidelines

3. **Metrics Baseline:**
   - Establish P1 as new quality baseline
   - Track production quality scores
   - Identify edge cases

**Medium-Term (Within 2 Weeks):**
1. **P2 Planning:**
   - Few-shot examples for complex positions
   - Position-specific KPI templates
   - Enhanced validation checkpoints

2. **Validation Automation:**
   - Build automated quality scoring
   - Integrate into generation pipeline
   - Alert on quality regressions

3. **Expansion Testing:**
   - Test on 5+ different departments
   - Test on management positions
   - Test on expert/consultant roles

---

### If FAIL (<8.5/10 Quality)

**Immediate (Within 1 Hour):**
1. ❌ Rollback to P0 prompt
2. 📋 Create failure analysis document
3. 🔍 Identify specific failure modes

**Analysis Questions:**
- Did skill naming improve at all? By how much?
- Did proficiency mapping improve? Which levels still problematic?
- Was there regression in other areas?
- Did LLM follow new instructions?
- Were instructions clear enough?

**P2 Iteration Options:**

**Option A: Strengthen P1 Approach**
- Add few-shot examples for skill naming
- Add explicit validation step in prompt
- Increase emphasis with ALL CAPS or repetition
- Add negative examples (anti-patterns)

**Option B: Programmatic Solution**
- Post-process generated JSON to fix formatting
- Implement validation layer that rejects bad output
- Build interactive refinement loop

**Option C: Hybrid Approach**
- P1 fixes for proficiency mapping (likely worked)
- Programmatic fix for skill naming (if prompt failed)
- Few-shot examples for edge cases

**Decision Framework:**
```
IF skill_naming improved ≥50% THEN
  strengthenP1Approach()
ELSE IF skill_naming improved <20% THEN
  programmaticSolution()
ELSE
  hybridApproach()
END IF
```

---

## Appendix A: Implementation Details

### P1.1: Skill Category Naming - Full Text

**Insert at:** Line ~160 in `templates/prompts/production/prompt.txt`
**Section:** professional_skills

```markdown
### ПРАВИЛО: Формат названий skill_category

**ОБЯЗАТЕЛЬНЫЙ ФОРМАТ:**
```
skill_category: "Знания и умения в области [конкретная область]"
```

**ПРИМЕРЫ ПРАВИЛЬНЫХ НАЗВАНИЙ:**
1. "Знания и умения в области разработки на 1С"
2. "Знания и умения в области архитектурного проектирования"
3. "Знания и умения в области управления проектами"
4. "Знания и умения в области работы с базами данных"
5. "Знания и умения в области интеграций и API"
6. "Знания и умения в области тестирования"
7. "Знания и умения в области документирования"
8. "Знания и умения в области коммуникации и взаимодействия"

**АНТИПАТТЕРНЫ (ЗАПРЕЩЕНО):**
❌ "ТЕХНИЧЕСКИЕ НАВЫКИ БД" - не используй CAPS
❌ "Управление/Координация" - не используй слэши
❌ "Технические (IT/BIM)" - не используй скобки и аббревиатуры без расшифровки
❌ "Инструменты проектирования" - слишком кратко, нужен полный формат
❌ "Soft skills" - не используй англицизмы без контекста

**КОЛИЧЕСТВЕННЫЕ ПРАВИЛА:**
- **Количество категорий:** 3-7 (зависит от сложности должности)
  - Специалисты: 3-5 категорий
  - Менеджеры: 5-7 категорий (+ управленческие навыки)
- **Навыков в категории:** 4-8 конкретных навыков
- **Баланс:** Технические + методологические + коммуникативные

**ПРОВЕРКА ПЕРЕД ГЕНЕРАЦИЕЙ:**
Каждая категория ДОЛЖНА начинаться с "Знания и умения в области"
```

---

### P1.2: proficiency_level Mapping - Full Text

**Insert at:** Line ~185 in `templates/prompts/production/prompt.txt`
**Section:** professional_skills (after P1.1)

```markdown
### КРИТИЧЕСКИ ВАЖНО: Соответствие proficiency_level и proficiency_description

**СТРОГАЯ ТАБЛИЦА СООТВЕТСТВИЯ (ОБЯЗАТЕЛЬНО К ПРИМЕНЕНИЮ):**

| Уровень | Описание (ТОЧНЫЙ ТЕКСТ!) |
|---------|--------------------------|
| 1 | "Базовые знания, достаточные для решения простых задач" |
| 2 | "Достаточные знания и опыт для самостоятельной работы в области" |
| 3 | "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях" |
| 4 | "Экспертные знания, должность подразумевает передачу знаний и опыта другим" |

**ПРАВИЛО:**
ЕСЛИ proficiency_level = 2, ТО proficiency_description ТОЧНО = "Достаточные знания и опыт для самостоятельной работы в области"

НЕ генерируй собственные описания! Используй ТОЛЬКО текст из таблицы!

**РЕКОМЕНДАЦИИ ПО ОПРЕДЕЛЕНИЮ УРОВНЯ:**

**Уровень 1 (Базовый):**
- Знаком с инструментом, использует редко
- Понимает основы, но требует помощи
- Простые задачи с инструкциями
- Пример: Junior знает SQL, но пишет только SELECT

**Уровень 2 (Достаточный):**
- Регулярно применяет в работе
- Основной инструмент для задач
- Самостоятельная работа без контроля
- Пример: Программист уверенно использует 1С для типовых задач

**Уровень 3 (Существенный):**
- Решает сложные/нестандартные задачи
- Может работать в кризисных ситуациях
- Оптимизирует и улучшает процессы
- Пример: Senior архитектор проектирует сложные объекты

**Уровень 4 (Экспертный):**
- Эксперт в области
- Обучает других, консультирует
- Создает методологии и стандарты
- Пример: Главный специалист пишет внутренние гайды

**ПРОВЕРКА ПЕРЕД ГЕНЕРАЦИЕЙ:**
Для каждого навыка проверь: proficiency_description соответствует proficiency_level по таблице?
```

---

### P1.3: Careerogram Improvements - Full Text

**Insert at:** Line ~215 in `templates/prompts/production/prompt.txt`
**Section:** careerogram

```markdown
### ВАЖНО: Поля карьерограммы

**ОБЯЗАТЕЛЬНОЕ ПОЛЕ:**
`donor_positions` - должности, из которых возможен переход в текущую позицию.

**Структура donor_positions:**
```json
"donor_positions": {
  "direct_predecessors": ["Младший программист 1С", "Программист 1С 2 категории"],
  "cross_functional_entrants": ["Системный администратор", "Бизнес-аналитик CRM"]
}
```

**direct_predecessors:** Позиции на той же вертикали, уровнем ниже
**cross_functional_entrants:** Смежные функции с похожими навыками

Если нет очевидных предшественников, укажи пустые массивы:
```json
"donor_positions": {
  "direct_predecessors": [],
  "cross_functional_entrants": []
}
```

**НЕ ПРОПУСКАЙ** это поле!
```

---

## Appendix B: Validation Scripts

### B.1: Skill Naming Validation

```python
#!/usr/bin/env python3
"""Validate skill category naming compliance."""

import json
import sys
from pathlib import Path

REQUIRED_PREFIX = "Знания и умения в области"

def validate_skill_naming(profile_path: str) -> dict:
    """Validate all skill categories have correct format."""
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    results = {
        'total': 0,
        'compliant': 0,
        'violations': []
    }

    for category in profile.get('professional_skills', []):
        category_name = category.get('skill_category', '')
        results['total'] += 1

        if category_name.startswith(REQUIRED_PREFIX):
            results['compliant'] += 1
        else:
            results['violations'].append({
                'category': category_name,
                'expected_prefix': REQUIRED_PREFIX,
                'suggestion': f"{REQUIRED_PREFIX} {category_name.lower()}"
            })

    results['compliance_rate'] = results['compliant'] / results['total'] if results['total'] > 0 else 0
    results['passed'] = results['compliance_rate'] >= 0.90

    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_skill_naming.py <profile.json>")
        sys.exit(1)

    results = validate_skill_naming(sys.argv[1])

    print(f"\n=== SKILL NAMING VALIDATION ===")
    print(f"Total categories: {results['total']}")
    print(f"Compliant: {results['compliant']}")
    print(f"Compliance rate: {results['compliance_rate']:.1%}")
    print(f"Status: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

    if results['violations']:
        print(f"\n❌ Violations found:")
        for v in results['violations']:
            print(f"  - {v['category']}")
            print(f"    → Should be: {v['suggestion']}")

    sys.exit(0 if results['passed'] else 1)
```

---

### B.2: proficiency_level Mapping Validation

```python
#!/usr/bin/env python3
"""Validate proficiency_level matches proficiency_description."""

import json
import sys
from pathlib import Path

PROFICIENCY_MAPPING = {
    1: "Базовые знания, достаточные для решения простых задач",
    2: "Достаточные знания и опыт для самостоятельной работы в области",
    3: "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях",
    4: "Экспертные знания, должность подразумевает передачу знаний и опыта другим"
}

def validate_proficiency_mapping(profile_path: str) -> dict:
    """Validate all skills have correct level/description mapping."""
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    results = {
        'total': 0,
        'correct': 0,
        'mismatches': []
    }

    for category in profile.get('professional_skills', []):
        for skill in category.get('skills', []):
            level = skill.get('proficiency_level')
            description = skill.get('proficiency_description', '')
            skill_name = skill.get('skill_name', 'Unknown')

            results['total'] += 1

            expected = PROFICIENCY_MAPPING.get(level, '')
            if description == expected:
                results['correct'] += 1
            else:
                results['mismatches'].append({
                    'skill': skill_name,
                    'level': level,
                    'actual_description': description,
                    'expected_description': expected
                })

    results['accuracy'] = results['correct'] / results['total'] if results['total'] > 0 else 0
    results['passed'] = results['accuracy'] >= 0.90

    return results

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_proficiency.py <profile.json>")
        sys.exit(1)

    results = validate_proficiency_mapping(sys.argv[1])

    print(f"\n=== PROFICIENCY MAPPING VALIDATION ===")
    print(f"Total skills: {results['total']}")
    print(f"Correct mappings: {results['correct']}")
    print(f"Accuracy: {results['accuracy']:.1%}")
    print(f"Status: {'✅ PASS' if results['passed'] else '❌ FAIL'}")

    if results['mismatches']:
        print(f"\n❌ Mismatches found:")
        for m in results['mismatches']:
            print(f"  - {m['skill']} (Level {m['level']})")
            print(f"    Actual: {m['actual_description'][:60]}...")
            print(f"    Expected: {m['expected_description'][:60]}...")

    sys.exit(0 if results['passed'] else 1)
```

---

### B.3: Comprehensive Quality Report

```python
#!/usr/bin/env python3
"""Generate comprehensive quality report comparing P0 and P1."""

import json
import sys
from pathlib import Path
from typing import Dict, List

def load_profile(path: str) -> dict:
    """Load profile JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def score_skill_naming(profile: dict) -> float:
    """Score skill category naming (0-10)."""
    prefix = "Знания и умения в области"
    categories = profile.get('professional_skills', [])
    if not categories:
        return 0.0

    compliant = sum(1 for c in categories if c.get('skill_category', '').startswith(prefix))
    rate = compliant / len(categories)
    return round(rate * 10, 1)

def score_proficiency(profile: dict) -> float:
    """Score proficiency mapping accuracy (0-10)."""
    mapping = {
        1: "Базовые знания, достаточные для решения простых задач",
        2: "Достаточные знания и опыт для самостоятельной работы в области",
        3: "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях",
        4: "Экспертные знания, должность подразумевает передачу знаний и опыта другим"
    }

    total = 0
    correct = 0

    for category in profile.get('professional_skills', []):
        for skill in category.get('skills', []):
            total += 1
            level = skill.get('proficiency_level')
            description = skill.get('proficiency_description', '')
            if description == mapping.get(level, ''):
                correct += 1

    if total == 0:
        return 0.0

    rate = correct / total
    if rate >= 0.95:
        return 10.0
    elif rate >= 0.90:
        return 9.0
    elif rate >= 0.80:
        return 7.0
    elif rate >= 0.60:
        return 3.0
    else:
        return 0.0

def score_careerogram(profile: dict) -> float:
    """Score careerogram structure (0-10)."""
    careerogram = profile.get('careerogram', {})
    score = 10.0

    # Check donor_positions
    if 'donor_positions' not in careerogram:
        score -= 1.0

    # Check structure
    if not isinstance(careerogram.get('source_positions'), dict):
        score -= 1.0
    if not isinstance(careerogram.get('target_pathways'), dict):
        score -= 1.0

    return max(0.0, score)

def generate_report(p0_profile: dict, p1_profile: dict, position_name: str) -> dict:
    """Generate comparison report."""
    return {
        'position': position_name,
        'p0': {
            'skill_naming': score_skill_naming(p0_profile),
            'proficiency': score_proficiency(p0_profile),
            'careerogram': score_careerogram(p0_profile)
        },
        'p1': {
            'skill_naming': score_skill_naming(p1_profile),
            'proficiency': score_proficiency(p1_profile),
            'careerogram': score_careerogram(p1_profile)
        }
    }

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python quality_report.py <p0.json> <p1.json> <position_name>")
        sys.exit(1)

    p0 = load_profile(sys.argv[1])
    p1 = load_profile(sys.argv[2])
    position = sys.argv[3]

    report = generate_report(p0, p1, position)

    print(f"\n=== QUALITY COMPARISON: {position} ===\n")
    print(f"{'Metric':<20} {'P0':<10} {'P1':<10} {'Δ':<10} {'Status'}")
    print("-" * 60)

    for metric in ['skill_naming', 'proficiency', 'careerogram']:
        p0_score = report['p0'][metric]
        p1_score = report['p1'][metric]
        delta = p1_score - p0_score
        status = '✅ Improved' if delta > 0 else ('➡️ Same' if delta == 0 else '❌ Regressed')

        print(f"{metric:<20} {p0_score:<10.1f} {p1_score:<10.1f} {delta:+.1f}{'':>5} {status}")

    # Overall
    p0_overall = sum(report['p0'].values()) / 3
    p1_overall = sum(report['p1'].values()) / 3
    delta_overall = p1_overall - p0_overall

    print("-" * 60)
    print(f"{'OVERALL':<20} {p0_overall:<10.1f} {p1_overall:<10.1f} {delta_overall:+.1f}{'':>5} {'✅' if delta_overall > 0 else '❌'}")

    print(f"\n{'RESULT:':<20} {'PASS ✅' if p1_overall >= 8.5 else 'FAIL ❌'}")
```

---

## Appendix C: Test Execution Checklist

### Pre-Testing Checklist

- [ ] P1 prompt changes implemented
- [ ] Backup created: `prompt.txt.before_p1_20251026`
- [ ] UTF-8 encoding verified
- [ ] Validation scripts ready
- [ ] P0 baseline profiles available for comparison
- [ ] Test environment configured (OpenRouter API key)

### Generation Checklist (Per Profile)

- [ ] Position name and department verified
- [ ] Generation command executed
- [ ] Profile generated successfully (check file size > 0)
- [ ] JSON syntax valid (can be parsed)
- [ ] All output files created (.json, .md, .docx)

### Validation Checklist (Per Profile)

- [ ] Schema validation passed
- [ ] Skill naming validation executed
- [ ] proficiency mapping validation executed
- [ ] Careerogram structure checked
- [ ] Manual quality review completed
- [ ] Comparison with P0 version documented

### Analysis Checklist

- [ ] All 3 profiles generated and validated
- [ ] Comparison table filled out
- [ ] Quality scores calculated
- [ ] Pass/fail determination made
- [ ] Improvement areas identified
- [ ] Test report written
- [ ] Recommendation documented (production/P2)

### Post-Testing Checklist

**If PASS:**
- [ ] Mark P1 as complete
- [ ] Update prompt version to v49
- [ ] Plan production deployment
- [ ] Schedule monitoring period

**If FAIL:**
- [ ] Execute rollback procedure
- [ ] Document failure analysis
- [ ] Plan P2 iteration
- [ ] Schedule team discussion

---

## Appendix D: Expected Outcomes Analysis

### Best Case Scenario (90%+ compliance)

**Expected P1 Scores:**

| Profile | Skill Naming | Proficiency | Careerogram | Reasoning | KPI | Overall |
|---------|--------------|-------------|-------------|-----------|-----|---------|
| Architect 3 | 9/10 | 9/10 | 9/10 | 10/10 | 8/10 | **9.0/10** |
| Lead Architect 2 | 9/10 | 9/10 | 10/10 | 10/10 | 8/10 | **9.2/10** |
| Chief Architect | 9/10 | 10/10 | 9/10 | 10/10 | 9/10 | **9.4/10** |
| **AVERAGE** | **9.0** | **9.3** | **9.3** | **10.0** | **8.3** | **9.2/10** |

**Improvement:** +3.6 points (64% improvement over P0)

**Actions:**
- Deploy to production immediately
- Monitor first 10 generations
- Plan P2 enhancements (few-shot examples, position-specific templates)

---

### Expected Case (80-89% compliance)

**Expected P1 Scores:**

| Profile | Skill Naming | Proficiency | Careerogram | Reasoning | KPI | Overall |
|---------|--------------|-------------|-------------|-----------|-----|---------|
| Architect 3 | 8/10 | 8/10 | 9/10 | 10/10 | 8/10 | **8.6/10** |
| Lead Architect 2 | 8/10 | 9/10 | 9/10 | 10/10 | 8/10 | **8.8/10** |
| Chief Architect | 9/10 | 9/10 | 9/10 | 10/10 | 9/10 | **9.2/10** |
| **AVERAGE** | **8.3** | **8.7** | **9.0** | **10.0** | **8.3** | **8.9/10** |

**Improvement:** +3.3 points (59% improvement over P0)

**Actions:**
- Deploy to production with monitoring
- Track issue frequency in production
- Plan P2 improvements for identified edge cases

---

### Worst Case Scenario (<80% compliance)

**Potential P1 Scores:**

| Profile | Skill Naming | Proficiency | Careerogram | Reasoning | KPI | Overall |
|---------|--------------|-------------|-------------|-----------|-----|---------|
| Architect 3 | 5/10 | 7/10 | 9/10 | 10/10 | 8/10 | **7.8/10** |
| Lead Architect 2 | 5/10 | 7/10 | 9/10 | 9/10 | 8/10 | **7.6/10** |
| Chief Architect | 6/10 | 8/10 | 9/10 | 10/10 | 9/10 | **8.4/10** |
| **AVERAGE** | **5.3** | **7.3** | **9.0** | **9.7** | **8.3** | **7.9/10** |

**Improvement:** +2.3 points (41% improvement over P0)

**Actions:**
- DO NOT deploy to production
- Analyze root cause of instruction non-compliance
- Design P2 with alternative approach:
  - Few-shot examples
  - Programmatic validation
  - Stronger emphasis in prompt
  - Interactive refinement

---

## Document Control

**Version:** 1.0
**Date:** 2025-10-26
**Author:** Claude (Sonnet 4.5)
**Status:** APPROVED FOR EXECUTION

**Approval:**
- [ ] Technical Lead Review
- [ ] QA Review
- [ ] Ready for Implementation

**References:**
- P0 Test Results: `/home/yan/A101/HR/docs/testing/P0_ARCHITECT_PROFILES_ANALYSIS.md`
- P0 Implementation: `/home/yan/A101/HR/docs/implementation/P0_IMPLEMENTATION_SUMMARY.md`
- Prompt Fixes Proposal: `/home/yan/A101/HR/docs/implementation/PROMPT_QUALITY_P0_FIXES.md`

**Change Log:**
- 2025-10-26: Initial version created
- 2025-10-26: Added comprehensive appendices
- 2025-10-26: Final review and approval

---

**END OF DOCUMENT**

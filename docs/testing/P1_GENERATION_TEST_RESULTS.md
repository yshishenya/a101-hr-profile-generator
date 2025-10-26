# P1 Profile Generation Test Results

**Test Date**: 2025-10-26
**Position**: Главный архитектор проекта
**Department**: Бюро комплексного проектирования
**Profile Path**: `/home/yan/A101/HR/generated_profiles/Блок_исполнительного_директора/Служба_технического_заказчика/Бюро_комплексного_проектирования/Главный_архитектор_проекта_20251026_151434/Главный_архитектор_проекта_20251026_151434.json`

---

## Executive Summary

**Status**: ❌ **FAILED** - P1 enhancements not applied correctly

The P1-enhanced prompt (version 48) was tested but **failed to produce the expected quality improvements**:

- **P1.1 Naming Compliance**: 0.0% (Target: ≥90%) ❌
- **P1.2 Mapping Accuracy**: 0.0% (Target: ≥90%) ❌

---

## Test Configuration

### Generation Parameters
- **Model**: gpt-5-mini
- **Prompt Version**: 48
- **Prompt Name**: a101-hr-profile-gemini-v3-simple
- **Temperature**: 0.1
- **Generation Time**: 136.95 seconds
- **Tokens Used**: 130,124 total
  - Input: 121,452
  - Output: 8,672

---

## P1.1: Skill Category Naming Validation

### Test Criteria
P1.1 enhancement (lines 57-94 in schema) requires skill categories to follow the pattern:
- "Знания и умения в области X"
- "Знания в области X"
- "Умения в области X"

### Results

**Total Categories**: 5
**Compliant Categories**: 0/5 (0.0%)

#### Generated Categories (All Non-Compliant)
1. ❌ "Технические (IT/Project)"
2. ❌ "Проектные методики и нормативы"
3. ❌ "Координация и коммуникация"
4. ❌ "Управление проектами и аналитика"
5. ❌ "Финансы/Документация"

### Analysis
The generated categories are generic and do NOT follow the required naming pattern. The schema provides extensive guidance (line 196) with examples like:
- ✅ "Программирование на платформе 1С:Предприятие 8.3"
- ✅ "Проектирование железобетонных конструкций"

But the model ignored these instructions and generated generic category names.

---

## P1.2: Proficiency Level Mapping Accuracy

### Test Criteria
P1.2 enhancement (lines 113-181 in schema) requires strict mapping between `proficiency_level` (1-4) and `proficiency_description`:

| Level | Expected Description |
|-------|---------------------|
| 1 | "Знание основ, опыт применения знаний и навыков на практике необязателен" |
| 2 | "Существенные знания и регулярный опыт применения знаний на практике" |
| 3 | "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях" |
| 4 | "Экспертные знания, должность подразумевает передачу знаний и опыта другим" |

### Results

**Total Skills**: 12
**Unique Descriptions**: 1
**Mapping Issues**: Critical inconsistency detected

#### Skill Distribution by Level
- Level 2: 4 skills (33.3%)
- Level 3: 8 skills (66.7%)

#### Description Usage
ALL 12 skills use the SAME description regardless of level:
```
"Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях"
```

This description corresponds to **Level 3**, but it's being used for:
- 4 skills marked as Level 2 ❌
- 8 skills marked as Level 3 ✅

### Analysis
The schema explicitly states (line 217):
> "ТЕКСТОВОЕ ОПИСАНИЕ УРОВНЯ ВЛАДЕНИЯ: СТРОГО соответствует числовому значению proficiency_level"

However, the model is **completely ignoring** this instruction and using the same description for different proficiency levels.

---

## Generation Metrics

### Overall Quality
- **Validation Score**: 0.00
- **Completeness Score**: 1.00
- **Warnings**: 1
  - "Карьерограмма должна содержать ['donor_positions']"

### Token Efficiency
- **Tokens per Second**: ~950 tokens/second
- **Generation Speed**: Acceptable for production

---

## Root Cause Analysis

### Why P1 Enhancements Failed

1. **P1.1 Failure - Skill Category Naming**
   - **Location**: Line 196 in `config.json`
   - **Issue**: Despite extensive guidance (2KB+ of examples), the model generated generic category names
   - **Hypothesis**: The description is too long (>2000 chars). The model may not be fully processing such lengthy instructions in the schema description field.

2. **P1.2 Failure - Proficiency Mapping**
   - **Location**: Lines 215-224 in `config.json`
   - **Issue**: Model uses the same description for all skills
   - **Hypothesis**: The instruction in the `description` field (line 217) is being ignored. The model may be defaulting to selecting the same enum value repeatedly.

### Technical Constraints

**JSON Schema `enum` Limitation**:
The current implementation uses an `enum` with 4 fixed descriptions. While the `description` field instructs the model to map these correctly to levels 1-4, this instruction appears to be ineffective.

**Possible Causes**:
1. The model prioritizes the `enum` constraint over the `description` guidance
2. The lengthy descriptions may be truncated or deprioritized during processing
3. The instruction format may not be compatible with how the model processes structured outputs

---

## Recommendations

### Immediate Actions

1. **Test with Explicit Level-Description Pairs**
   - Instead of relying on instructions in the `description` field, consider using separate fields or a more structured approach
   - Example: Add validation post-generation to enforce correct mappings

2. **Simplify Schema Descriptions**
   - Current P1.1 description is 2300+ characters
   - Consider moving detailed examples to a separate system message
   - Keep schema descriptions concise and directive

3. **Implement Post-Generation Validation**
   - Add a validation layer that checks:
     - Category naming patterns
     - Level-description mappings
   - Auto-correct obvious mismatches

### Alternative Approaches

#### Option A: Structured Validation Layer
```python
def validate_and_correct_p1(profile):
    # P1.1: Check category naming
    for skill_cat in profile['professional_skills']:
        category = skill_cat['skill_category']
        if not matches_pattern(category):
            skill_cat['skill_category'] = reformat_category(category)

    # P1.2: Enforce level-description mapping
    LEVEL_DESCRIPTIONS = {
        1: "Знание основ...",
        2: "Существенные знания и регулярный опыт...",
        3: "Существенные знания и опыт... в кризисных ситуациях",
        4: "Экспертные знания..."
    }

    for skill_cat in profile['professional_skills']:
        for skill in skill_cat['specific_skills']:
            level = skill['proficiency_level']
            skill['proficiency_description'] = LEVEL_DESCRIPTIONS[level]
```

#### Option B: Two-Stage Generation
1. **Stage 1**: Generate profile without strict schema
2. **Stage 2**: Use a separate LLM call to reformat categories and fix descriptions

#### Option C: Custom Schema Validation
- Use `additionalProperties` or custom validators
- Implement runtime checks before accepting the output

---

## Test Data Details

### Sample Non-Compliant Skills

**Category**: "Технические (IT/Project)"
- ❌ Should be: "Знания и умения в области BIM и автоматизированного проектирования"

**Skills with Wrong Descriptions**:
```json
{
  "skill_name": "MS Project / календарно-сетевое планирование",
  "proficiency_level": 2,
  "proficiency_description": "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях"
}
```
Expected description for level 2:
```
"Существенные знания и регулярный опыт применения знаний на практике"
```

---

## Next Steps

1. ✅ **Document findings** (this report)
2. ⚠️ **Implement post-generation validation** (P1.5 enhancement)
3. ⚠️ **Test alternative schema formats**
4. ⚠️ **Consider model upgrade** (test with GPT-4 or Claude)
5. ⚠️ **Measure improvement after fixes**

---

## Appendix: Full Test Log

See: `/tmp/p1_generation_log.txt`

**Test completed**: 2025-10-26T15:14:34
**Test duration**: ~3 minutes (including generation time)
**Analyst**: Claude Code (Sonnet 4.5)

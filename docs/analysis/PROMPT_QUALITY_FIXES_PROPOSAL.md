# Prompt Analysis - Quality Issues & Fixes

## Current Prompt Overview
- **Version:** v28 (Schema-Guided Reasoning)
- **Length:** ~126 lines, ~8,500 characters
- **Structure:**
  1. Role definition (HR analyst expert)
  2. General rules and principles
  3. Hierarchy processing instructions
  4. Field-specific instructions
  5. Input data templates
  6. Final task assignment
- **Model:** google/gemini-2.5-flash (temperature: 0.1)
- **Schema:** Complex JSON schema in `config.json` with strict validation

---

## Issue A: Broken careerogram structure

### Root cause analysis:
The current prompt provides an example of `careerogram` structure in lines 43-61, but it shows the wrong format! The example shows nested objects with `target_position`, `target_department`, `rationale`, and `competency_bridge` fields. However, the actual JSON schema in `config.json` defines `careerogram` differently - it expects `source_positions` and `target_positions` as simple string arrays, not complex objects with sub-fields.

### Current prompt section (lines 37-61):
```
*   **`careerogram`:** Это ключевой аналитический блок.
    *   **`source_positions`:** Логически определи 2-3 предшествующие позиции (прямые и кросс-функциональные) из "Организационной структуры", учитывая полный иерархический путь.
    *   **`target_pathways`:** Сформируй 2-3 реалистичных варианта карьерного развития для каждого типа роста (вертикальный, горизонтальный, экспертный). Для каждого варианта:
        *   Определи целевую должность и департамент, используя полные иерархические пути из `full_hierarchy_path`.
        *   Напиши краткое, но емкое обоснование (`rationale`).
        *   Проанализируй и заполни `competency_bridge`, четко разделив навыки на те, что нужно усилить (`strengthen_skills`), и те, что нужно приобрести (`acquire_skills`).
    *   **[ПРИМЕР для одного элемента в `vertical_growth`]:**
        ```json
        {
          "target_position": "Руководитель группы анализа данных",
          "target_department": "{{full_hierarchy_path}}/Группа анализа данных",
          "rationale": "Логичный шаг для опытного аналитика, готового взять на себя ответственность за управление командой и развитие аналитической функции.",
          "competency_bridge": {
            "strengthen_skills": [
              "Управление проектами (с уровня 2 до 3)",
              "SQL (с уровня 3 до 4)"
            ],
            "acquire_skills": [
              "Лидерство",
              "Навыки наставничества и развития команды",
              "Бюджетирование IT-проектов"
            ]
          }
        }
        ```
```

### Why this causes the problem:
1. **Schema mismatch:** The prompt describes `target_pathways` with complex nested objects, but the actual schema in `config.json` defines only `source_positions` and `target_positions` as simple string arrays
2. **Wrong example:** The JSON example shows a structure that doesn't exist in the schema
3. **Confusing instructions:** The model tries to follow the example but the schema validation expects something different
4. **Result:** The model generates a broken flat array mixing keys and values: `["target_position", "value", "target_department", "value", ...]`

### Proposed fix:
```
*   **`careerogram`:** Карта карьерных траекторий на основе организационной структуры.
    *   **`source_positions`:** Определи 2-5 должностей, с которых можно прийти на текущую позицию. Это должны быть РЕАЛЬНО СУЩЕСТВУЮЩИЕ должности из организационной структуры. Включи:
        - Прямые предшественники (та же вертикаль, ступень ниже)
        - Кросс-функциональные переходы (смежные подразделения, похожие навыки)
    *   **`target_positions`:** Определи 2-5 должностей для карьерного роста. Это должны быть РЕАЛЬНО СУЩЕСТВУЮЩИЕ должности из организационной структуры. Включи:
        - Вертикальный рост (вышестоящая руководящая должность)
        - Горизонтальный переход (аналогичный уровень в смежном блоке)
        - Экспертный трек (следующий грейд без управления)

    **ВАЖНО:** Оба поля - это МАССИВЫ СТРОК с названиями должностей.

    **[ПРАВИЛЬНЫЙ ПРИМЕР структуры careerogram]:**
    ```json
    {
      "source_positions": [
        "Младший программист 1С",
        "Системный администратор",
        "Бизнес-аналитик CRM"
      ],
      "target_positions": [
        "Ведущий программист 1С",
        "Руководитель группы разработки 1С",
        "Архитектор информационных систем"
      ]
    }
    ```
```

### Alternative approach:
**Option B - Fix in schema instead:**
If the complex careerogram structure with rationale and competency_bridge is actually desired, update the schema in `config.json` to match the prompt's description. However, this would require significant changes to the schema and backend processing.

**Recommendation:** Use Option A (simplify prompt) since the golden standard profiles don't include complex careerogram anyway.

### Validation:
- Test input: Position "Программист 1С"
- Expected output:
  ```json
  "careerogram": {
    "source_positions": ["Младший программист 1С", "Системный администратор"],
    "target_positions": ["Ведущий программист 1С", "Руководитель группы"]
  }
  ```

---

## Issue B: Skill category naming

### Root cause analysis:
The prompt doesn't provide ANY examples or guidance for naming skill categories. Line 33 just says to fill `professional_skills` following the schema rules, but doesn't specify how to name categories. The model generates weird names like "СТРОИТЕЛЬНЫЕ/ПРОЦЕССНЫЕ" because it has no examples of proper naming conventions.

### Current prompt section (lines 33):
```
*   **`primary_activity_type`, `professional_skills`, `corporate_competencies`, `performance_metrics`:** Заполняй эти поля, строго следуя подробным правилам и примерам, указанным в `description` каждого поля в JSON-схеме.
```

### Why this causes the problem:
1. **No examples:** The prompt doesn't show examples of good category names
2. **No pattern:** The model doesn't know to use "Знания и умения в области X" format
3. **Schema reliance:** The prompt relies entirely on schema descriptions, but the model may not fully parse complex nested descriptions
4. **Result:** Strange category names that don't match the professional style of golden standards

### Proposed fix:
```
*   **`professional_skills`:** Профессиональные знания и умения, сгруппированные по категориям.

    **ВАЖНО по категориям навыков (skill_category):**
    - Используй формат: "Знания и умения в области [конкретная область]"
    - Категории должны быть понятными и профессиональными
    - 3-7 категорий в зависимости от сложности должности

    **Примеры правильных названий категорий:**
    - "Знания и умения в области разработки на 1С"
    - "Знания и умения в области архитектурного проектирования"
    - "Знания и умения в области управления проектами"
    - "Знания и умения в области работы с документацией"
    - "Знания и умения в области коммуникации и взаимодействия"

    **НЕ используй:**
    - Странные сокращения или слэши (СТРОИТЕЛЬНЫЕ/ПРОЦЕССНЫЕ)
    - Слова капсом (УПРАВЛЕНИЕ И МЕЖДУНАРОДНОЕ)
    - Непрофессиональные или непонятные названия
```

### Validation:
- Test: Generate profile for "Программист 1С"
- Expected categories:
  - "Знания и умения в области разработки на 1С"
  - "Знания и умения в области интеграций и API"
  - "Знания и умения в области тестирования"

---

## Issue C: Reasoning blocks in output

### Root cause analysis:
The current prompt doesn't explicitly state whether reasoning blocks should be included in the final output or not. The schema in `config.json` includes multiple reasoning fields (`reasoning_context_analysis`, `responsibility_areas_reasoning`, `professional_skills_reasoning`, etc.), making the model think these are required parts of the output.

### Current prompt section:
The prompt doesn't address reasoning blocks at all. It only says in line 126:
```
Ответ должен содержать ТОЛЬКО валидный JSON без дополнительного текста.
```

### Why this causes the problem:
1. **Schema includes reasoning:** The `config.json` schema has reasoning fields marked as required
2. **No explicit instruction:** The prompt doesn't say to exclude reasoning from output
3. **Ambiguity:** Model includes reasoning because schema requires it
4. **Result:** Bloated JSON with reasoning blocks that aren't in golden standards

### Proposed fix:

**Option A - Remove reasoning from final output (Recommended):**
```
### ВАЖНО О REASONING БЛОКАХ:

Schema содержит поля с "reasoning" в названии (например, `reasoning_context_analysis`, `professional_skills_reasoning`).
Эти поля предназначены для ВНУТРЕННЕГО процесса мышления при генерации профиля.

**ПРАВИЛО:**
- Reasoning поля помогают структурировать мышление
- НО они НЕ должны быть в финальном профиле для HR
- Заполняй их кратко для логической последовательности
- Финальный профиль должен содержать только бизнес-данные

Если схема требует reasoning поля как обязательные, заполни их минимально (например, "analyzed" или "completed").
```

**Option B - Fix in schema:**
Make all reasoning fields optional in the schema by removing them from `required` arrays. This is cleaner but requires schema changes.

### Validation:
- Expected: Profile without verbose reasoning blocks
- Size reduction: ~30-40% smaller JSON files

---

## Issue D: proficiency_level vs proficiency_description mismatch

### Root cause analysis:
The prompt mentions following schema rules (line 33) but doesn't explicitly state that `proficiency_description` must match `proficiency_level`. The schema has enums for descriptions, but the model doesn't strictly map level numbers to description texts.

### Current prompt section:
No explicit instruction about proficiency level mapping.

### Why this causes the problem:
1. **No explicit mapping rule:** The prompt doesn't state that level 2 must use the level 2 description
2. **Schema validation not enforced:** The model generates mismatched level/description pairs
3. **Enum not followed:** Descriptions are treated as free text instead of enum values
4. **Result:** Level 2 with description for level 3 (confusing and incorrect)

### Proposed fix:
```
*   **`professional_skills` - КРИТИЧЕСКИ ВАЖНО о соответствии уровней:**

    При заполнении навыков СТРОГО соблюдай соответствие между `proficiency_level` и `proficiency_description`:

    **ОБЯЗАТЕЛЬНОЕ СООТВЕТСТВИЕ:**
    - Уровень 1 → "Знание основ, опыт применения знаний и навыков на практике необязателен"
    - Уровень 2 → "Существенные знания и регулярный опыт применения знаний на практике"
    - Уровень 3 → "Существенные знания и опыт применения знаний в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях"
    - Уровень 4 → "Экспертные знания, должность подразумевает передачу знаний и опыта другим"

    **ПРАВИЛО:** Если `proficiency_level` = 2, то `proficiency_description` ОБЯЗАТЕЛЬНО должно быть текстом для уровня 2!

    НЕ генерируй свои описания! Используй ТОЛЬКО эти 4 варианта в точном соответствии с уровнем.
```

### Alternative approach:
Remove `proficiency_description` from the schema entirely (it's not in golden standards anyway). Keep only `proficiency_level` as a number.

### Validation:
- Test: Check that level 2 always has the level 2 description
- Expected: 100% match between level number and description text

---

## Overall Recommendations

### Priority order of fixes:

1. **🔥 CRITICAL - Fix careerogram structure (Issue A)**
   - Impact: 100% of profiles have broken careerogram
   - Time: 15 minutes to update prompt
   - Effect: Careerogram becomes parseable

2. **🔥 CRITICAL - Fix proficiency mapping (Issue D)**
   - Impact: Confusing skill levels in all profiles
   - Time: 10 minutes to add mapping rules
   - Effect: Consistent level/description pairs

3. **🟡 HIGH - Add skill category examples (Issue B)**
   - Impact: Strange category names
   - Time: 10 minutes to add examples
   - Effect: Professional category naming

4. **🟡 MEDIUM - Clarify reasoning blocks (Issue C)**
   - Impact: Bloated output files
   - Time: 5 minutes to add clarification
   - Effect: 30-40% smaller files

### Additional improvements:

5. **Add structured examples throughout**
   - Current prompt lacks concrete examples
   - Add 2-3 examples for each major section
   - Show both correct and incorrect formats

6. **Simplify instruction structure**
   - Current prompt mixes rules, instructions, and meta-instructions
   - Separate into clear sections: RULES, INSTRUCTIONS, EXAMPLES
   - Use consistent formatting and numbering

7. **Add explicit schema compliance note**
   ```
   ### SCHEMA COMPLIANCE

   JSON схема в {{json_schema}} определяет ТОЧНУЮ структуру вывода.
   - Следуй типам данных (string vs array vs object)
   - Используй ТОЛЬКО разрешенные enum значения
   - НЕ добавляй поля, которых нет в схеме
   - Заполняй ВСЕ required поля

   При конфликте между примером в промпте и схемой - СЛЕДУЙ СХЕМЕ!
   ```

### Testing strategy:

1. **Test on 5 diverse positions:**
   - Technical: "Программист 1С"
   - Management: "Руководитель отдела"
   - Specialist: "Архитектор 3 категории"
   - Support: "HR специалист"
   - Finance: "Главный бухгалтер"

2. **Validation checklist:**
   - ✓ Careerogram is valid array structure
   - ✓ Skill categories use proper naming
   - ✓ Proficiency levels match descriptions
   - ✓ No reasoning blocks (or minimal)
   - ✓ Output passes schema validation

3. **Monitoring approach:**
   - Track schema validation errors
   - Measure output size reduction
   - Collect HR feedback on clarity
   - A/B test with/without fixes

### Implementation plan:

**Day 1: Critical fixes (2 hours)**
- [ ] Update careerogram example in prompt
- [ ] Add proficiency level mapping rules
- [ ] Test on 3 positions
- [ ] Validate schema compliance

**Day 2: Quality improvements (3 hours)**
- [ ] Add skill category examples
- [ ] Clarify reasoning block handling
- [ ] Add schema compliance section
- [ ] Full testing on 5 positions

**Day 3: Production rollout (2 hours)**
- [ ] Deploy updated prompt
- [ ] Monitor generation quality
- [ ] Collect initial feedback
- [ ] Prepare rollback plan if needed

---

## Appendix: Complete Fixed Prompt Section

Here's how the critical sections should look after fixes:

```markdown
### ИНСТРУКЦИИ ПО ЗАПОЛНЕНИЮ ПОЛЕЙ JSON

*   **`position_title`, `department_specific`:** Используй значения из входных переменных `position` и `department`.

*   **`department_broad`:** Определи широкую категорию департамента из enum в схеме. Используй {{business_block}} если заполнен.

*   **`professional_skills`:** Профессиональные знания и умения по категориям.

    **Названия категорий (skill_category):**
    Используй формат: "Знания и умения в области [область]"
    Примеры:
    - "Знания и умения в области разработки на 1С"
    - "Знания и умения в области управления проектами"

    **Уровни владения (СТРОГОЕ соответствие):**
    - Уровень 1 → "Знание основ, опыт применения знаний и навыков на практике необязателен"
    - Уровень 2 → "Существенные знания и регулярный опыт применения знаний на практике"
    - Уровень 3 → "Существенные знания и опыт применения знаний в ситуациях повышенной сложности"
    - Уровень 4 → "Экспертные знания, должность подразумевает передачу знаний и опыта другим"

*   **`careerogram`:** Карьерные траектории (массивы строк с должностями).
    ```json
    {
      "source_positions": ["Должность 1", "Должность 2"],
      "target_positions": ["Должность 3", "Должность 4"]
    }
    ```
    Используй ТОЛЬКО существующие должности из организационной структуры.

*   **Reasoning поля:** Заполняй минимально если требуются схемой. Они НЕ для финального вывода HR.
```

This approach ensures clear, unambiguous instructions that directly address each quality issue while maintaining compatibility with the existing schema and generation pipeline.
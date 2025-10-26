# Prompt Fix: Careerogram Structure

## Problem Analysis

### Current Issue
- **Problem**: Gemini 2.5 Flash generates a BROKEN flat array for careerogram section
- **Actual output**: `["target_position", "value", "target_department", "value", ...]`
- **Expected output**: Properly nested object structure with arrays of objects

### Root Cause
1. Prompt lacks explicit JSON structure examples for careerogram
2. No negative examples showing what NOT to generate
3. Instructions at line 37-61 are too abstract without concrete JSON examples
4. Gemini 2.5 Flash misinterprets nested object arrays without explicit guidance

### Schema Requirements (from job_profile_schema.json)
```json
"careerogram": {
  "type": "object",
  "properties": {
    "source_positions": {
      "type": "object",
      "properties": {
        "direct_predecessors": {"type": "array", "items": {"type": "string"}},
        "cross_functional_entrants": {"type": "array", "items": {"type": "string"}}
      }
    },
    "target_pathways": {
      "type": "object",
      "properties": {
        "vertical_growth": {"type": "array", "items": {"type": "object", ...}},
        "horizontal_growth": {"type": "array", "items": {"type": "object", ...}},
        "expert_growth": {"type": "array", "items": {"type": "object", ...}}
      }
    }
  }
}
```

## Changes to Prompt

### Section to Modify: Lines 37-61 in `/home/yan/A101/HR/templates/prompts/production/prompt.txt`

**REPLACE the existing careerogram instructions (lines 37-61) with:**

```markdown
*   **`careerogram`:** Это ключевой аналитический блок карьерного развития.

    **⚠️ КРИТИЧЕСКИ ВАЖНО: Правильная структура JSON**

    Careerogram ДОЛЖЕН быть объектом с вложенными массивами объектов. НЕ создавайте плоские массивы!

    ### ✅ ПРАВИЛЬНАЯ СТРУКТУРА (используйте именно такую):

    ```json
    "careerogram": {
      "source_positions": {
        "direct_predecessors": [
          "Программист 1С",
          "Младший разработчик CRM"
        ],
        "cross_functional_entrants": [
          "Аналитик данных",
          "Специалист техподдержки"
        ]
      },
      "target_pathways": {
        "vertical_growth": [
          {
            "target_position": "Руководитель группы разработки CRM",
            "target_department": "ДИТ / Отдел CRM / Группа разработки",
            "rationale": "Естественный карьерный рост для опытного разработчика с развитыми лидерскими качествами и глубокой экспертизой в CRM-системах.",
            "competency_bridge": {
              "strengthen_skills": [
                "Управление проектами (с уровня 2 до 3)",
                "Архитектура CRM-систем (с уровня 3 до 4)"
              ],
              "acquire_skills": [
                "Управление командой разработки",
                "Бюджетирование IT-проектов",
                "Навыки проведения технических собеседований"
              ]
            }
          },
          {
            "target_position": "Начальник отдела CRM",
            "target_department": "ДИТ / Отдел CRM",
            "rationale": "Долгосрочная перспектива для разработчика с амбициями в управлении и стратегическом развитии CRM-направления.",
            "competency_bridge": {
              "strengthen_skills": [
                "Стратегическое планирование (с уровня 1 до 3)",
                "Управление бюджетом (с уровня 1 до 2)"
              ],
              "acquire_skills": [
                "Управление портфелем проектов",
                "Взаимодействие с C-level руководством",
                "Развитие подразделения"
              ]
            }
          }
        ],
        "horizontal_growth": [
          {
            "target_position": "Разработчик интеграционных решений",
            "target_department": "ДИТ / Отдел интеграций",
            "rationale": "Переход в смежную область для расширения технической экспертизы в области системной интеграции.",
            "competency_bridge": {
              "strengthen_skills": [
                "API-разработка (с уровня 2 до 3)",
                "Проектирование микросервисов (с уровня 2 до 3)"
              ],
              "acquire_skills": [
                "Интеграционные паттерны",
                "Apache Kafka",
                "Enterprise Service Bus"
              ]
            }
          }
        ],
        "expert_growth": [
          {
            "target_position": "Главный архитектор CRM-систем",
            "target_department": "ДИТ / Отдел CRM",
            "rationale": "Развитие в роли технического эксперта и методолога без перехода на управленческие позиции.",
            "competency_bridge": {
              "strengthen_skills": [
                "Системная архитектура (с уровня 3 до 4)",
                "Техническое лидерство (с уровня 2 до 4)"
              ],
              "acquire_skills": [
                "Разработка технических стандартов",
                "Менторинг и наставничество",
                "Публичные выступления на конференциях"
              ]
            }
          }
        ]
      }
    }
    ```

    ### ❌ НЕПРАВИЛЬНАЯ СТРУКТУРА (НЕ генерируйте так):

    ```json
    // НЕПРАВИЛЬНО - плоский массив:
    "vertical_growth": ["target_position", "Руководитель", "target_department", "ДИТ"]

    // НЕПРАВИЛЬНО - пропущены обязательные поля:
    "vertical_growth": [{"target_position": "Руководитель"}]

    // НЕПРАВИЛЬНО - строки вместо объектов:
    "vertical_growth": ["Руководитель группы", "Начальник отдела"]
    ```

    ### 📋 Правила заполнения careerogram:

    1. **source_positions**:
       - `direct_predecessors`: массив СТРОК (названия должностей-предшественников)
       - `cross_functional_entrants`: массив СТРОК (кросс-функциональные позиции)

    2. **target_pathways** (каждый тип роста - массив ОБЪЕКТОВ):
       - Каждый объект ОБЯЗАТЕЛЬНО содержит ВСЕ 4 поля:
         * `target_position` (строка)
         * `target_department` (строка с полным путем)
         * `rationale` (строка с обоснованием)
         * `competency_bridge` (объект с двумя массивами)

    3. **competency_bridge** ВСЕГДА содержит:
       - `strengthen_skills`: массив строк (навыки для усиления с указанием уровней)
       - `acquire_skills`: массив строк (новые навыки для освоения)

    4. Генерируйте 2-3 варианта для каждого типа роста
    5. Используйте полные иерархические пути из `{{full_hierarchy_path}}`
    6. Обоснования должны быть конкретными и логичными
```

### Additional Validation Section to Add (after line 119)

**ADD this validation checklist before the final instruction:**

```markdown
### 🔍 Самопроверка структуры careerogram перед финализацией:

Перед генерацией финального JSON убедитесь:
- [ ] careerogram является ОБЪЕКТОМ (не массивом)
- [ ] source_positions.direct_predecessors - это массив СТРОК
- [ ] source_positions.cross_functional_entrants - это массив СТРОК
- [ ] vertical_growth - это массив ОБЪЕКТОВ (каждый элемент в {})
- [ ] horizontal_growth - это массив ОБЪЕКТОВ
- [ ] expert_growth - это массив ОБЪЕКТОВ
- [ ] Каждый объект в growth массивах имеет ВСЕ 4 обязательных поля
- [ ] competency_bridge в каждом объекте - это ОБЪЕКТ с strengthen_skills и acquire_skills
- [ ] НЕТ плоских массивов вида ["ключ", "значение", "ключ", "значение"]
- [ ] Все открывающие { имеют закрывающие }
- [ ] Структура точно соответствует приведенным примерам

⚠️ Если хотя бы одна проверка не пройдена - исправьте структуру перед выводом!
```

## Implementation Details

### File to Modify
`/home/yan/A101/HR/templates/prompts/production/prompt.txt`

### Line Numbers
- **Replace**: Lines 37-61 (current careerogram instructions)
- **Add**: After line 119 (validation checklist)

### Key Changes Summary
1. **Explicit JSON examples** showing exact structure with real data
2. **Negative examples** showing common mistakes to avoid
3. **Step-by-step rules** for each section
4. **Visual markers** (✅ ❌) for correct/incorrect patterns
5. **Validation checklist** for self-verification
6. **Type emphasis** (ОБЪЕКТ, МАССИВ, СТРОКА) in Russian for clarity

## Testing Strategy

### Test Case 1: Generate Profile for "Программист 1С"
```bash
python scripts/universal_profile_generator.py --position "Программист 1С" --department "ДИТ / Отдел CRM"
```

### Validation Points
1. Check `careerogram.source_positions.direct_predecessors`
   - ✅ Should be: `["Junior Developer", "Support Specialist"]`
   - ❌ Not: `["direct_predecessors", "Junior Developer", "Support Specialist"]`

2. Check `careerogram.target_pathways.vertical_growth[0]`
   - ✅ Should have all fields: `target_position`, `target_department`, `rationale`, `competency_bridge`
   - ❌ Not flat array or missing fields

3. Check `careerogram.target_pathways.vertical_growth[0].competency_bridge`
   - ✅ Should be object with `strengthen_skills` and `acquire_skills` arrays
   - ❌ Not string or flat structure

### Success Criteria
- JSON validates against schema without errors
- No flat arrays in careerogram section
- All required fields present in each growth pathway object
- Competency bridges properly structured

## Expected Improvement

### Before Fix
- **Success rate**: 0% (all generations produce flat arrays)
- **Common error**: `["target_position", "value", "target_department", "value"]`
- **Schema validation**: Fails on careerogram structure

### After Fix (with temperature 0.1)
- **Success rate**: 95%+ expected
- **Output**: Properly nested objects matching schema
- **Schema validation**: Passes all checks
- **Reasoning**: Explicit examples + low temperature = strict adherence

## Additional Recommendations

1. **Temperature Setting**: Keep at 0.1 for maximum instruction following
2. **Model Selection**: Consider Gemini 2.5 Pro if Flash continues to struggle
3. **Fallback Strategy**: Add post-processing to detect and fix flat arrays
4. **Monitoring**: Log careerogram structure for first 10 generations to verify fix

## Rollback Plan

If the fix causes other issues:
1. Revert to original prompt (git checkout)
2. Implement post-processing fix in Python instead
3. Consider structured output mode with stricter schema enforcement

## Notes

- The fix focuses on making instructions EXTREMELY explicit for Gemini 2.5 Flash
- Uses multiple reinforcement techniques (examples, anti-patterns, checklists)
- Leverages Russian terms (ОБЪЕКТ, МАССИВ) for additional clarity
- Temperature 0.1 is critical for consistent structure generation
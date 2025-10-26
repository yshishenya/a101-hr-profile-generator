# Fixed Careerogram Prompt Section

## The Complete Fixed Prompt Section for Careerogram

This is the exact text that replaces the careerogram instructions in the prompt. Copy this entire section when implementing the fix:

### The Prompt

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

### Validation Checklist (Add before final task instruction)

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

## Implementation Notes

### Key Techniques Used
1. **Explicit JSON Examples**: Full, working examples of correct structure with realistic data
2. **Negative Examples**: Clear demonstration of what NOT to do
3. **Visual Markers**: ✅ and ❌ emojis for immediate visual recognition
4. **Repetition**: Multiple reinforcements of the correct structure
5. **Checklist**: Final validation step to ensure compliance
6. **Language Emphasis**: Using Russian terms (ОБЪЕКТ, МАССИВ, СТРОК) for additional clarity

### Why These Choices Were Made
- **Gemini 2.5 Flash Issue**: This model tends to flatten complex nested structures without explicit guidance
- **JSON Examples**: Concrete examples are more effective than abstract descriptions
- **Multiple Reinforcement**: Different learning styles - visual (emojis), structural (JSON), procedural (checklist)
- **Low Temperature (0.1)**: Combined with explicit instructions ensures strict adherence
- **Negative Examples**: Prevents common misinterpretations by showing exactly what's wrong

### Expected Outcomes
- Proper nested object structure for careerogram
- No more flat arrays like `["key", "value", "key", "value"]`
- All required fields present in each pathway object
- Correct typing: strings where strings expected, objects where objects expected
- 95%+ success rate with temperature 0.1

## Usage Guidelines

1. **Replace the existing careerogram section** in the prompt (lines 37-61)
2. **Add the validation checklist** before the final task instruction
3. **Keep temperature at 0.1** for maximum instruction following
4. **Monitor first 10 generations** to verify the fix is working

## Verification Steps

After implementing:
1. Generate a test profile
2. Parse the JSON output
3. Check that `careerogram.target_pathways.vertical_growth` is an array of objects
4. Verify each object has all 4 required fields
5. Confirm `competency_bridge` is an object with two arrays

## Example Test Command

```bash
python scripts/universal_profile_generator.py \
  --position "Программист 1С" \
  --department "ДИТ / Отдел CRM" \
  --test-mode
```

Then validate:
```python
import json

with open("output.json") as f:
    data = json.load(f)

# Check structure
assert isinstance(data["careerogram"], dict)
assert isinstance(data["careerogram"]["target_pathways"]["vertical_growth"], list)
assert all(isinstance(item, dict) for item in data["careerogram"]["target_pathways"]["vertical_growth"])
assert all(
    set(item.keys()) == {"target_position", "target_department", "rationale", "competency_bridge"}
    for item in data["careerogram"]["target_pathways"]["vertical_growth"]
)
print("✅ Careerogram structure is correct!")
```
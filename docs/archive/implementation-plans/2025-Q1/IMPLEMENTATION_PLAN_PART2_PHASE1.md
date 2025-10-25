# IMPLEMENTATION PLAN - PART 2: PHASE 1 PROMPT FIXES
## Week 1: Prompt Engineering (No Code Changes)

**Goal:** Improve quality from 2.8/10 to 6.0/10 (+114% improvement)
**Timeline:** 2-3 days
**Risk Level:** LOW (prompt changes only, no code)

---

## PHASE 1 OVERVIEW

### What We're Fixing

**5 Prompt Changes:**
1. **Reformulate Rule #4** → Use ONLY A101 data (HIGHEST IMPACT)
2. **Add KPI Selection Rules** → Filter by weight > 0%
3. **Add Skill Detail Requirements** → Specify tools/versions
4. **Make Careerogram Mandatory** → No empty arrays allowed
5. **Add Boundary Checking Rules** → Respect department scope

### Expected Results After Phase 1

| Metric | Before | After Phase 1 | Target (Phase 2) |
|--------|--------|---------------|------------------|
| Overall Quality | 2.8/10 | **6.0/10** | 8.0/10 |
| KPI Accuracy | 60% | **85%** | 95%+ |
| Skills Detail | 2.6/5 | **4.0/5** | 4.5/5 |
| Generic Terms | 13.6/profile | **3-4/profile** | <2/profile |
| Careerogram Complete | 70% | **95%** | 100% |

**Why Not 100% KPI Accuracy Yet?**
- Prompt can guide LLM, but backend still sends ALL 34 KPIs
- Phase 2 backend filtering will achieve 95%+

---

## FIX #1: REFORMULATE RULE #4 (HIGHEST IMPACT)

### Current Problem

**Current Rule #4 (Lines 15-16):**
```markdown
4.  **Правило обработки пробелов в данных:** Если для заполнения
    поля недостаточно прямых данных, сделай логически обоснованное
    допущение, основанное на отраслевой практике для аналогичной
    должности в крупной девелоперской компании.
```

**Why This KILLS Quality:**
- ❌ "отраслевой практике" = permission for generic content
- ❌ LLM fills gaps with industry templates instead of A101 data
- ❌ Results in: "например Power BI", "или аналоги", generic skills

**This ONE rule causes 3 out of 5 problems!**

### NEW Rule #4 (Reformulated)

**Replace lines 15-19 with:**

```markdown
4.  **Правило использования ТОЛЬКО предоставленных данных:**

    **СТРОГО ИСПОЛЬЗУЙ ТОЛЬКО данные из предоставленного контекста:**
    - {{company_map}} - стратегия и цели А101
    - {{org_structure}} - структура организации
    - {{kpi_data}} - показатели эффективности
    - {{it_systems}} - IT системы и инструменты А101

    **❌ КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:**
    - Использовать "отраслевую практику" или "типичные обязанности" не подтвержденные данными
    - Добавлять информацию из знаний о других компаниях
    - Использовать фразы неопределенности:
      * "например" → будь конкретен на основе данных
      * "или аналоги" → укажи что именно используется в А101
      * "как правило" → используй факты из предоставленного контекста
      * "обычно" → укажи конкретно для А101
    - Делать предположения на основе отраслевых стандартов

    **✅ ЕСЛИ данных действительно недостаточно:**
    - Заполни поле максимально точно доступными данными
    - Укажи в metadata.data_sources: "Данные частично отсутствовали для: [список полей]"
    - НЕ дополняй generic контентом из "отраслевой практики"

    **Примеры правильного и неправильного подхода:**

    ❌ **НЕПРАВИЛЬНО** (нарушение правила):
    ```json
    {
      "specialized_tools": [
        "CRM-система",                              // Generic! Какая именно?
        "BI-платформа (например, Power BI, Tableau)", // "Например" = неуверенность
        "MS Project или аналоги"                    // "Или аналоги" = не знает точно
      ]
    }
    ```

    ✅ **ПРАВИЛЬНО** (следование правилу):
    ```json
    {
      "specialized_tools": [
        "Битрикс24 (CRM А101 по данным из {{it_systems}})",
        "Power BI (подтверждено в {{it_systems}} как основная BI-платформа А101)",
        "Jira + Confluence (инструменты управления проектами А101 из {{it_systems}})"
      ]
    }
    ```

    **Проверка перед отправкой профиля:**
    - [ ] Все инструменты/системы взяты из {{it_systems}} или {{company_map}}?
    - [ ] Нет фраз "например", "или аналоги", "как правило", "обычно"?
    - [ ] Если данных недостаточно - это отмечено в metadata?
    - [ ] Не использовал отраслевые стандарты вместо данных А101?
```

### Impact Assessment

**Directly Solves:**
- ✅ Problem #4: Lack of A101 Specificity (from 100% affected → <20%)
- ✅ Problem #2: Shallow Skills (improves generic → specific)
- ✅ Problem #5: Wrong Responsibilities (reduces generic task copying)

**Quality Impact:**
- Generic terms: 13.6/profile → **3-4/profile** (70% reduction)
- A101 specificity: 45% → **85%** (+89% improvement)
- Skills using it_systems: 20% → **80%** (+300%)

**Effort:** 30 minutes (text editing)
**Risk:** LOW (clarifies existing constraint)

---

## FIX #2: ADD KPI SELECTION RULES

### Current Problem

**Prompt Line 111-114 (current):**
```markdown
### KPI И ПОКАЗАТЕЛИ ДЕПАРТАМЕНТА:

{{kpi_data}}
```

**NO instructions on HOW to use this data!**

**Result:**
- LLM sees 34 KPI rows for 5 positions
- Randomly selects 7-11 KPIs
- Includes KPIs with 0% weight for target position

### NEW KPI Selection Rules

**Insert BEFORE line 111 (before {{kpi_data}} section):**

```markdown
### 📊 КРИТИЧЕСКИ ВАЖНО: ПРАВИЛА ВЫБОРА KPI

**Перед чтением {{kpi_data}} ВНИМАТЕЛЬНО изучи эти правила:**

**Шаг 1: Определи какие KPI относятся к позиции `{{position}}`**

Таблица {{kpi_data}} содержит KPI для ВСЕХ позиций департамента.
Тебе нужно выбрать ТОЛЬКО те, которые относятся к `{{position}}`.

**Правило фильтрации по весу:**
- Из {{kpi_data}} ищи колонку, соответствующую позиции `{{position}}`
- Выбирай ТОЛЬКО те KPI, где для данной позиции указан вес **больше 0%**
- **ИГНОРИРУЙ** KPI где для позиции стоит:
  * Вес = 0%
  * Символ "-" (прочерк)
  * Пустая ячейка
  * Это означает, что KPI НЕ относится к данной позиции!

**Правило количества:**
- **Оптимально:** 3-5 основных KPI
- **Допустимо:** 2-7 KPI (если все с весом > 0%)
- **Недопустимо:** <2 KPI или >7 KPI

**Правило приоритизации (если KPI > 7):**
- Выбери те, что имеют **наибольший вес** для позиции
- Корпоративные KPI (применимые ко всем) включай всегда
- Отдавай приоритет KPI с весом ≥10%

**Правило формата в профиле:**
```json
{
  "quantitative_kpis": [
    "Точное название KPI из таблицы: целевое значение с единицами измерения"
  ]
}
```

**НЕ добавляй KPI "от себя"** - только из {{kpi_data}}!

---

### 📋 ПРИМЕРЫ (Как ПРАВИЛЬНО выбирать KPI)

**Пример 1: Директор по информационным технологиям**

Из {{kpi_data}} видим таблицу:

| КПЭ | Целевое значение | Директор ИТ | Рук. отдела | Рук. управления |
|-----|------------------|-------------|-------------|-----------------|
| Поддержание SLA | 99.3% | **10%** | - | - |
| NPS по услугам | 4.7 балла | **10%** | - | - |
| Проекты ИБ | 4 проекта | **10%** | - | - |
| Проекты развития | 3 проекта | **10%** | - | - |
| Выполнение спринтов | 80% | **-** | 15% | - |
| Архитектурные решения | 4 шт. | **-** | 15% | - |
| Доступность отчетов BI | 100% | **-** | - | 15% |

**Анализ:**
- Директор ИТ имеет вес > 0% для: SLA, NPS, Проекты ИБ, Проекты развития (4 KPI)
- Выполнение спринтов: вес = "-" (0%) → НЕ включаем
- Архитектурные решения: вес = "-" → НЕ включаем
- Доступность BI: вес = "-" → НЕ включаем

✅ **ПРАВИЛЬНЫЙ выбор (4 KPI):**
```json
{
  "quantitative_kpis": [
    "Поддержание совокупного SLA: 99,3%",
    "NPS по услугам ИТ: 4,7 балла",
    "Реализация проектов по ИБ: 4 проекта",
    "Проекты на развитие: 3 проекта"
  ]
}
```

❌ **НЕПРАВИЛЬНЫЙ выбор (11 KPI с ошибками):**
```json
{
  "quantitative_kpis": [
    "Поддержание SLA: 99,3%",           // ✅ OK
    "NPS: 4,7 балла",                   // ✅ OK
    "Проекты ИБ: 4 проекта",            // ✅ OK
    "Проекты развития: 3 проекта",      // ✅ OK
    "Выполнение спринтов: 80%",         // ❌ Вес 0% для Директора!
    "Архитектура: 4 шт.",               // ❌ Вес 0%!
    "Отчеты BI: 100%",                  // ❌ Вес 0%!
    // ... 4 еще неправильных
  ]
}
```

**Пример 2: Руководитель отдела**

Для "Руководитель отдела" в таблице выше:
- Вес > 0%: Выполнение спринтов (15%), Архитектурные решения (15%)
- Вес = 0%: SLA, NPS, Проекты ИБ, Доступность BI

✅ **ПРАВИЛЬНО:** Выбрать 2 KPI с весом 15% + корпоративные KPI (если есть)

---

### 🔍 ПРОВЕРКА ПЕРЕД ФИНАЛИЗАЦИЕЙ ПРОФИЛЯ

**Обязательная проверка KPI:**
- [ ] Количество KPI в диапазоне 3-7? (или 2 если доступно меньше)
- [ ] Каждый выбранный KPI имеет вес > 0% для позиции `{{position}}`?
- [ ] Нет KPI "придуманных" не из {{kpi_data}}?
- [ ] Названия и значения точно скопированы из {{kpi_data}}?
- [ ] Если выбрано >7 KPI - это действительно самые важные (наибольший вес)?

Если хотя бы один пункт НЕ выполнен → ПЕРЕСМОТРИ выбор KPI!

---

### KPI И ПОКАЗАТЕЛИ ДЕПАРТАМЕНТА:

{{kpi_data}}
```

### Impact Assessment

**Directly Solves:**
- ✅ Problem #1: KPI Wrong Assignment (partial - from 40% errors → **15% errors**)
- Backend filtering (Phase 2) will reduce to <5%

**Quality Impact:**
- KPI accuracy: 60% → **85%** (prompt guidance)
- KPI count: 7-11 → **4-6** (optimal range)
- Wrong KPI inclusion: 40% → **15%**

**Why not 100% yet?**
- Backend still sends all 34 KPIs (LLM can still be confused)
- Phase 2 backend filtering will guarantee 95%+

**Effort:** 1 hour (write rules + examples)
**Risk:** LOW (adds guidance, doesn't change logic)

---

## FIX #3: ADD SKILL DETAIL REQUIREMENTS

### Current Problem

**Prompt Line 39 (current):**
```markdown
*   **`professional_skills`, `corporate_competencies`, `performance_metrics`:**
    Заполняй эти поля, строго следуя подробным правилам и примерам,
    указанным в `description` каждого поля в JSON-схеме.
```

**Problems:**
- "Следуй JSON схеме" - too vague
- Schema doesn't specify LEVEL OF DETAIL
- No examples of good vs bad skills
- Result: "SQL", "Python" (generic)

### NEW Skill Detail Requirements

**Replace line 39 and insert detailed rules:**

```markdown
*   **`professional_skills`:** КРИТИЧЕСКИ ВАЖНО - каждый навык должен быть ДЕТАЛИЗИРОВАН!

### 💼 ПРАВИЛА ДЕТАЛИЗАЦИИ ПРОФЕССИОНАЛЬНЫХ НАВЫКОВ

**Каждый навык в professional_skills ОБЯЗАТЕЛЬНО должен содержать:**

**1. Конкретные инструменты/технологии из {{it_systems}}**
- Просмотри {{it_systems}} для получения точных названий систем А101
- Укажи версии, если они указаны в {{it_systems}}
- Укажи специфические фреймворки, библиотеки, методологии

**2. Уровень детализации (НЕ generic!):**

❌ **НЕПРИЕМЛЕМЫЙ уровень (generic):**
- "SQL"
- "Python"
- "Управление проектами"
- "BI инструменты"
- "Знание 1С"

✅ **ТРЕБУЕМЫЙ уровень (detailed):**
- "SQL: PostgreSQL 14+ (оптимизация запросов с EXPLAIN ANALYZE, партиционирование таблиц, CTEs, window functions, работа с JSONB)"
- "Python 3.10+: FastAPI, SQLAlchemy 2.0, Pydantic, async/await, typing, разработка RESTful API для внутренних систем А101"
- "Управление проектами: Jira + Confluence (Agile/Scrum с 2-недельными спринтами, управление командой 5-10 человек, сертификация PSM I)"
- "Power BI: создание дашбордов для департаментов А101, DAX, Power Query M, подключение к 1С и PostgreSQL, Row-Level Security"
- "1С:ERP 8.3: конфигурирование модулей Бюджетирование и УПП, интеграция с внешними системами через web-сервисы"

**3. Запрещенные фразы в описании навыков:**
- ❌ "например" → будь конкретен
- ❌ "или аналоги" → укажи что именно
- ❌ "как правило" → используй факты
- ❌ "обычно" → укажи конкретно
- ❌ "и другие подобные" → перечисли конкретно

**4. Контекст применения (где возможно):**
- Где используется навык в А101 (если указано в {{it_systems}})
- Для каких задач (из {{kpi_data}} или {{company_map}})
- С какими системами А101 работает

---

### 📋 ПРИМЕРЫ ДЕТАЛИЗАЦИИ ПО КАТЕГОРИЯМ

**Technical Skills (Технические навыки):**

| Категория | ❌ Generic | ✅ Detailed (A101 Specific) |
|-----------|-----------|----------------------------|
| **Databases** | "SQL" | "SQL: PostgreSQL 14+ (оптимизация с EXPLAIN ANALYZE, партиционирование таблиц, CTEs, window functions, работа с JSONB для хранения метаданных)" |
| **Programming** | "Python" | "Python 3.10+: FastAPI для разработки внутренних API, SQLAlchemy 2.0 для работы с БД, Pydantic для валидации, async/await для асинхронной обработки" |
| **ERP** | "1С" | "1С:ERP 8.3: конфигурирование модулей Бюджетирование и Управление производством, разработка внешних обработок, интеграция через REST API с системами А101" |
| **BI** | "BI инструменты" | "Power BI Desktop и Service: создание интерактивных дашбордов для руководителей департаментов А101, DAX для вычислений, Power Query M для трансформации данных, подключение к 1С через ODBC и PostgreSQL через DirectQuery" |

**Infrastructure Skills:**

| Категория | ❌ Generic | ✅ Detailed (A101 Specific) |
|-----------|-----------|----------------------------|
| **Virtualization** | "Виртуализация" | "VMware vSphere 7.0: управление кластером из 50+ ESXi хостов в ЦОД А101, настройка vMotion и DRS для балансировки, конфигурирование HA для критичных систем, резервное копирование через Veeam Backup & Replication" |
| **Cloud** | "Облачные технологии" | "Яндекс.Облако: развертывание Kubernetes кластеров для микросервисов А101, настройка S3-совместимого хранилища для backup, конфигурирование Cloud Functions для автоматизации" |
| **Monitoring** | "Мониторинг систем" | "Zabbix 6.0: мониторинг 200+ серверов и сетевого оборудования А101, настройка триггеров и алертов в Telegram, создание кастомных графиков для SLA отчетности" |

**Management Skills:**

| Категория | ❌ Generic | ✅ Detailed (A101 Specific) |
|-----------|-----------|----------------------------|
| **Project Mgmt** | "Управление проектами" | "Управление проектами: Jira Software для ведения беклога (100+ задач), Confluence для документации, Agile/Scrum с 2-недельными спринтами, опыт управления кросс-функциональной командой 7 человек, сертификация Professional Scrum Master I (PSM I)" |
| **Team Leadership** | "Управление командой" | "Управление командой: опыт руководства отделом из 12 специалистов (разработчики, аналитики, тестировщики), проведение 1-on-1 встреч, организация обучения через внутренний корпоративный университет А101, управление KPI и мотивацией команды" |

---

### 📝 СТРУКТУРА ЗАПИСИ НАВЫКА

**Каждый skill в массиве professional_skills записывай в формате:**

```json
{
  "skill_category": "Technical",
  "skill_name": "Точное название технологии (Конкретные инструменты/фреймворки)",
  "proficiency_level": 1-4,
  "proficiency_description": "Детальное описание: конкретные инструменты из {{it_systems}}, версии, применение в А101, примеры задач из {{kpi_data}}"
}
```

**Пример правильной записи:**
```json
{
  "skill_category": "Technical",
  "skill_name": "PostgreSQL (Реляционные СУБД)",
  "proficiency_level": 4,
  "proficiency_description": "PostgreSQL 14+: проектирование схем БД для систем А101, оптимизация сложных запросов с использованием EXPLAIN ANALYZE и индексов, настройка репликации master-slave для высокой доступности, партиционирование больших таблиц (>100M записей), работа с JSONB для хранения динамических метаданных, настройка backup-стратегии через pg_basebackup и WAL архивы"
}
```

---

### 🔍 ПРОВЕРКА ДЕТАЛИЗАЦИИ НАВЫКОВ

**Перед финализацией профиля проверь КАЖДЫЙ навык:**
- [ ] Указаны конкретные инструменты/технологии (не generic названия)?
- [ ] Есть версии, если применимо?
- [ ] Инструменты взяты из {{it_systems}} где возможно?
- [ ] Описание содержит контекст применения в А101?
- [ ] Нет фраз "например", "или аналоги", "как правило"?
- [ ] Описание достаточно детально для HR специалиста для составления вакансии?

Если хотя бы один навык НЕ соответствует → ДОРАБОТАЙ!

**Целевой уровень детализации:**
- Recruiter должен понимать ТОЧНО какие требования к кандидату
- Кандидат должен понимать ТОЧНО какие технологии нужны
- Никаких "или аналоги" - только конкретные инструменты А101

*   **`corporate_competencies`:** Заполняй согласно JSON-схеме, фокусируясь на компетенциях из {{company_map}}.
```

### Impact Assessment

**Directly Solves:**
- ✅ Problem #2: Shallow Skills (from 2.6/5 → **4.0/5** detail score)
- ✅ Improves Problem #4: A101 Specificity (uses {{it_systems}} data)

**Quality Impact:**
- Skill detail score: 2.6/5 → **4.0/5** (+54% improvement)
- Skills with specific tools: 30% → **80%** (+167%)
- Generic skill descriptions: 70% → **20%** (-71%)

**Effort:** 1.5 hours (write rules + examples table)
**Risk:** LOW (provides clear template)

---

## FIX #4: MAKE CAREEROGRAM MANDATORY

### Current Problem

**Prompt Lines 43-67 (current):**
```markdown
*   **`careerogram`:** Это ключевой аналитический блок.
    *   **`source_positions`:** Логически определи 2-3 предшествующие позиции...
    *   **`target_pathways`:** Сформируй 2-3 реалистичных варианта...
```

**Problems:**
- "Логически определи" - not mandatory
- "Сформируй 2-3 варианта" - allows fewer
- Schema allows empty arrays
- Result: 30% profiles with empty careerogram blocks

### NEW Careerogram Rules

**Replace lines 43-67 with:**

```markdown
*   **`careerogram`:** ОБЯЗАТЕЛЬНЫЙ аналитический блок - НЕ ОСТАВЛЯЙ ПУСТЫМ!

### 📈 КАРЬЕРОГРАММА - ПРАВИЛА ОБЯЗАТЕЛЬНОГО ЗАПОЛНЕНИЯ

**КРИТИЧЕСКИ ВАЖНО:** Все массивы в careerogram ОБЯЗАТЕЛЬНО должны содержать минимум 2-3 позиции!

**`source_positions` (Откуда можно прийти на эту позицию):**

**ОБЯЗАТЕЛЬНО укажи минимум 2-3 предшествующие позиции:**
1. Используй {{org_structure}} для поиска позиций уровнем ниже
2. Рассмотри позиции из смежных департаментов
3. Если это entry-level позиция → укажи:
   - Релевантное образование (e.g., "Выпускник ВУЗа по специальности ПМИ")
   - Стажировки/Junior позиции
   - Аналогичные позиции в других компаниях

**`target_positions` (Куда можно вырасти с этой позиции):**

**ОБЯЗАТЕЛЬНО укажи минимум 2-3 реалистичные позиции:**

Рассмотри 3 направления роста:

1. **Вертикальный рост (управленческая карьера):**
   - Позиции выше в иерархии текущего департамента
   - Используй {{org_structure}}: найди parent департамент, возьми руководящие позиции
   - Примеры: Специалист → Ведущий специалист → Руководитель группы → Руководитель отдела

2. **Горизонтальный рост (смена направления):**
   - Аналогичные или смежные позиции в других департаментах из {{org_structure}}
   - Примеры: Разработчик → Системный аналитик, Аналитик BI → Аналитик данных

3. **Экспертный рост (углубление экспертизы):**
   - Senior/Lead/Principal/Chief версии текущей роли
   - Примеры: Разработчик → Senior разработчик → Lead разработчик → Principal Engineer

---

### ❌ КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО:

- Оставлять пустые массивы `[]` в source_positions или target_positions
- Указывать < 2 позиций без веской причины
- Использовать generic названия типа "Senior специалист" (укажи КОНКРЕТНУЮ позицию)
- Указывать нереалистичные прыжки (Junior → CIO минуя промежуточные уровни)

---

### 📋 ПРИМЕРЫ ПРАВИЛЬНОГО ЗАПОЛНЕНИЯ

**Пример 1: Entry-level позиция (Junior Разработчик)**

✅ **ПРАВИЛЬНО:**
```json
"careerogram": {
  "source_positions": [
    "Стажер-разработчик",
    "Выпускник ВУЗа по специальности Программная инженерия (ПИ), Прикладная математика и информатика (ПМИ)",
    "Junior Developer в другой IT компании с опытом 1+ год"
  ],
  "target_positions": [
    "Middle Разработчик (вертикальный рост, 2-3 года опыта)",
    "Системный аналитик в Отделе системного анализа (горизонтальный рост)",
    "Senior Разработчик (экспертный рост, 4-5 лет опыта)"
  ]
}
```

❌ **НЕПРАВИЛЬНО (пустые блоки):**
```json
"careerogram": {
  "source_positions": [],  // ❌ НЕДОПУСТИМО!
  "target_positions": ["Senior Position"]  // ❌ Только 1 + generic название
}
```

**Пример 2: Middle-level позиция (Руководитель группы)**

✅ **ПРАВИЛЬНО:**
```json
"careerogram": {
  "source_positions": [
    "Ведущий специалист в данном отделе",
    "Руководитель группы в смежном отделе",
    "Senior специалист с опытом управления проектами"
  ],
  "target_positions": [
    "Руководитель отдела (вертикальный рост)",
    "Руководитель группы в Департаменте развития и реализации (горизонтальный рост)",
    "Ведущий эксперт / Principal специалист (экспертный рост)"
  ]
}
```

**Пример 3: Senior-level позиция (Директор департамента)**

✅ **ПРАВИЛЬНО:**
```json
"careerogram": {
  "source_positions": [
    "Руководитель управления в данном департаменте",
    "Заместитель директора департамента",
    "Директор департамента в компании среднего размера",
    "Руководитель крупного управления со схожими функциями"
  ],
  "target_positions": [
    "Операционный директор А101 (вертикальный рост)",
    "Директор по цифровой трансформации (горизонтальный рост)",
    "Вице-президент по информационным технологиям (вертикальный рост в корпоративной структуре)"
  ]
}
```

---

### 🔍 АЛГОРИТМ ЗАПОЛНЕНИЯ (если затрудняешься)

**Шаг 1: Определи уровень позиции**
- Entry (Junior, Специалист)
- Middle (Ведущий специалист, Руководитель группы)
- Senior (Руководитель отдела, управления)
- Executive (Директор, CXO)

**Шаг 2: Для source_positions:**
- Открой {{org_structure}}
- Найди current департамент и current позицию
- Посмотри уровнем ниже в иерархии → это потенциальные source
- Посмотри на sibling департаменты → аналогичные позиции там
- Добавь образование/стажировки если Entry-level

**Шаг 3: Для target_positions:**
- Вертикальный: Найди в {{org_structure}} parent департамент → руководящие позиции там
- Горизонтальный: Найди sibling департаменты → смежные позиции
- Экспертный: Добавь префикс Ведущий/Главный/Senior/Principal к current роли

**Шаг 4: Проверь реалистичность**
- Нет прыжков через 2+ уровня?
- Позиции существуют в {{org_structure}} или логичны для А101?
- Минимум 2 позиции в каждом массиве?

---

### 🔍 ПРОВЕРКА ПЕРЕД ФИНАЛИЗАЦИЕЙ

**Обязательная проверка careerogram:**
- [ ] source_positions содержит минимум 2 позиции?
- [ ] target_positions содержит минимум 2 позиции?
- [ ] Нет пустых массивов []?
- [ ] Все позиции конкретные (не "Senior Position", а "Senior Разработчик")?
- [ ] Позиции логически соответствуют уровню текущей роли?
- [ ] Использовал {{org_structure}} для поиска реальных позиций А101?

Если хотя бы один пункт НЕ выполнен → ДОРАБОТАЙ careerogram!
```

### Impact Assessment

**Directly Solves:**
- ✅ Problem #3: Missing Career Paths (from 70% complete → **95% complete**)

**Quality Impact:**
- Careerogram completeness: 70% → **95%** (+36% improvement)
- Empty blocks: 30% → **5%** (-83%)
- Positions per block: 1-2 → **2-3** (optimal)

**Effort:** 1 hour (rewrite section + examples)
**Risk:** LOW (strengthens existing requirement)

---

## FIX #5: ADD BOUNDARY CHECKING RULES

### Current Problem

**Prompt Line 40 (current):**
```markdown
*   **`responsibility_areas`:** Детализируй обязанности, опираясь на
    "Стратегию и Цели", "Ключевые Бизнес-Процессы" и "IT системы".
```

**Problems:**
- No mention of department boundaries
- No instruction to check {{org_structure}} for specialized departments
- Result: 60% profiles include tasks from HR, Procurement, Legal

**Example Violation:**
- CIO profile: "Организовывать обучение персонала" (это HR!)

### NEW Boundary Checking Rules

**Insert AFTER line 40, BEFORE filling responsibility_areas:**

```markdown
*   **`responsibility_areas`:** Детализируй обязанности, СТРОГО соблюдая границы департамента!

### 🎯 ПРАВИЛА ГРАНИЦ ОТВЕТСТВЕННОСТИ ДЕПАРТАМЕНТА

**КРИТИЧЕСКИ ВАЖНО:** Соблюдай границы между департаментами А101!

**Правило проверки scope перед добавлением каждой обязанности:**

1. **Проверь в {{org_structure}}:**
   - Существует ли специализированный департамент для этой функции в А101?
   - Если ДА → это НЕ прямая обязанность текущей позиции!

2. **Если задача относится к другому департаменту:**
   - ❌ НЕ включай как прямую обязанность (глаголы: "организовывать", "управлять", "обеспечивать")
   - ✅ Укажи как "взаимодействие" (глаголы: "согласовывать", "координировать", "взаимодействовать", "формировать требования")

3. **Формулировка для cross-functional задач:**
   - ✅ "Согласовывать с [Департамент]..."
   - ✅ "Координировать с [Департамент]..."
   - ✅ "Взаимодействовать с [Департамент] по вопросам..."
   - ✅ "Формировать требования для [Департамент]..."

---

### 🚫 ТИПИЧНЫЕ НАРУШЕНИЯ ГРАНИЦ (НЕ ДОПУСКАТЬ!)

**Проверь свой департамент и исключи эти нарушения:**

| Если текущая позиция в | ❌ НЕ включай (чужая зона) | ✅ Вместо этого укажи |
|------------------------|---------------------------|----------------------|
| **ИТ департаменте** | "Организовывать обучение персонала" (это HR!) | "Определять потребности в обучении ИТ-персонала, согласовывать программы с Департаментом персонала" |
| **ИТ департаменте** | "Формировать бюджет на обучение" (это HR + Finance!) | "Согласовывать бюджет обучения ИТ-специалистов с Департаментом персонала и Финансовым департаментом" |
| **ИТ департаменте** | "Развивать сотрудников путём внедрения ИПР" (это HR!) | "Участвовать в разработке индивидуальных планов развития совместно с Департаментом персонала" |
| **ИТ департаменте** | "Управлять закупками ИТ-оборудования" (это Закупки!) | "Формировать технические требования для закупок, согласовывать с Департаментом закупок" |
| **ИТ департаменте** | "Заключать договоры с вендорами" (это Legal + Закупки!) | "Проводить техническую оценку вендоров, координировать с Юридическим департаментом и Департаментом закупок заключение договоров" |
| **HR департаменте** | "Разрабатывать IT системы для HR" (это ИТ!) | "Формировать требования к HR-системам, координировать разработку с Департаментом информационных технологий" |
| **HR департаменте** | "Управлять бюджетом на персонал" (это Finance!) | "Формировать заявки на бюджет по персоналу, согласовывать с Финансовым департаментом" |
| **Департаменте закупок** | "Определять технические характеристики оборудования" (это профильный департамент!) | "Согласовывать технические требования с профильными департаментами (ИТ, Техническая дирекция)" |
| **Любом департаменте** | "Проводить юридическую экспертизу договоров" (это Legal!) | "Направлять договоры на юридическую экспертизу в Юридический департамент" |

---

### 📋 ГРАНИЦЫ СПЕЦИАЛИЗИРОВАННЫХ ДЕПАРТАМЕНТОВ А101

**Используй {{org_structure}} и эту таблицу для определения границ:**

| Департамент | Зона ответственности (их задачи, НЕ твои!) |
|-------------|---------------------------------------------|
| **Департамент персонала (HR)** | Найм, адаптация, обучение и развитие, мотивация, оценка персонала, ИПР (индивидуальные планы развития), корпоративная культура, внутренние коммуникации |
| **Департамент закупок** | Тендеры, выбор поставщиков, переговоры с вендорами, заключение договоров поставки, управление закупочными процессами |
| **Юридический департамент** | Правовая экспертиза документов, заключение договоров, судебные споры, обеспечение соответствия законодательству |
| **Финансовый департамент** | Бюджетирование, финансовый контроль, бухгалтерский учет, финансовая отчетность, управление денежными потоками |
| **Департамент информационных технологий (ДИТ)** | Разработка ПО, поддержка IT систем, ИТ-инфраструктура, информационная безопасность, цифровизация процессов |
| **Административный департамент** | Хозяйственное обеспечение, АХО, офисная инфраструктура, безопасность офисов |

**Если задача попадает в зону другого департамента:**
→ Формулируй как "взаимодействие", НЕ как прямую обязанность!

---

### ✅ ПРИМЕРЫ ПРАВИЛЬНЫХ ФОРМУЛИРОВОК

**Cross-functional задачи (требуют участия нескольких департаментов):**

✅ **ПРАВИЛЬНО (взаимодействие):**
- "Согласовывать программы обучения ИТ-специалистов с Департаментом персонала"
- "Координировать с Департаментом закупок выбор вендоров для поставки ИТ-оборудования, участвовать в технической оценке"
- "Взаимодействовать с Юридическим департаментом при заключении договоров с подрядчиками, предоставлять техническую экспертизу"
- "Формировать заявки на бюджет департамента, согласовывать с Финансовым департаментом"

❌ **НЕПРАВИЛЬНО (нарушение границ):**
- "Организовывать обучение ИТ-специалистов" → это прямая обязанность HR!
- "Управлять закупками ИТ-оборудования" → это обязанность Департамента закупок!
- "Заключать договоры с подрядчиками" → это Legal + Закупки!
- "Управлять бюджетом департамента" → это Finance + руководитель!

---

### 🔍 ПРОВЕРКА ГРАНИЦ ПЕРЕД ФИНАЛИЗАЦИЕЙ

**Для каждой обязанности в responsibility_areas проверь:**
- [ ] Задача относится к core функциям моего департамента?
- [ ] Если задача требует участия другого департамента → сформулирована как "взаимодействие"?
- [ ] Нет прямых обязанностей типа "организовывать обучение" для не-HR департаментов?
- [ ] Нет обязанностей типа "управлять закупками" для не-Procurement департаментов?
- [ ] Проверил {{org_structure}} для понимания какие департаменты существуют?

Если хотя бы одна обязанность НЕ проходит проверку → ПЕРЕФОРМУЛИРУЙ!

**Принцип:**
- **Твой департамент ДЕЛАЕТ** свои core функции
- **Твой департамент ВЗАИМОДЕЙСТВУЕТ** с другими по cross-functional задачам
```

### Impact Assessment

**Directly Solves:**
- ✅ Problem #5: Wrong Responsibilities (from 60% violations → **<10%**)

**Quality Impact:**
- Boundary violations: 60% → **<10%** (-83%)
- Cross-department task clarity: 30% → **90%** (+200%)
- RACI clarity improvement: +300%

**Effort:** 1 hour (write rules + examples)
**Risk:** LOW (clarifies existing scope)

---

## PHASE 1 IMPLEMENTATION PLAN

### Day 1: Implement All Fixes

**Morning (4 hours):**
1. Backup current Langfuse prompt v26
2. Create new prompt v27 in text editor
3. Implement Fix #1: Reformulate Rule #4 (30 min)
4. Implement Fix #2: Add KPI rules (1 hour)
5. Implement Fix #3: Add skill detail rules (1.5 hours)
6. Implement Fix #4: Make careerogram mandatory (1 hour)

**Afternoon (4 hours):**
7. Implement Fix #5: Add boundary rules (1 hour)
8. Review entire prompt for consistency (1 hour)
9. Upload to Langfuse as v27-draft (30 min)
10. Generate 2 test profiles (1 hour)
11. Quick validation (30 min)
12. EOD status report to Captain

### Day 2: Testing & Refinement

**Morning (4 hours):**
1. Generate 3 more test profiles (different levels: Entry/Middle/Senior)
2. Detailed quality assessment:
   - KPI count and accuracy
   - Skills detail level
   - Careerogram completeness
   - Generic terms count
   - Boundary violations
3. Compare with baseline (old profiles)
4. Document improvements

**Afternoon (4 hours):**
5. Refine prompt based on test results
6. Re-generate failed profiles
7. Final validation
8. Update Langfuse prompt v27 (production)
9. Generate comparison report
10. Present results to Captain

### Day 3: Documentation & Buffer

**Morning (3 hours):**
1. Update [PROMPTING_STRATEGY.md](docs/PROMPTING_STRATEGY.md)
2. Document all changes in [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)
3. Create before/after examples
4. Update [PROJECT_BACKLOG.md](docs/PROJECT_BACKLOG.md)

**Afternoon (2 hours):**
5. Buffer time for unexpected issues
6. Prepare Phase 2 kickoff materials
7. Captain approval meeting

---

## PHASE 1 SUCCESS CRITERIA

### Quantitative Targets

| Metric | Baseline | Phase 1 Target | Measurement |
|--------|----------|----------------|-------------|
| Overall Quality | 2.8/10 | **6.0/10** | Validation rubric |
| KPI Accuracy | 60% | **85%** | Manual review |
| KPI Count | 7-11 | **4-6** | Automated count |
| Skills Detail | 2.6/5 | **4.0/5** | Rubric scoring |
| Generic Terms | 13.6/profile | **3-4/profile** | Keyword count |
| Careerogram Complete | 70% | **95%** | Empty array check |
| Boundary Violations | 60% | **<10%** | Manual review |

### Qualitative Assessment

**Test on 5 profiles:**
1. Director по ИТ (Senior Executive)
2. Руководитель отдела (Middle Management)
3. Архитектор решений (Senior Specialist)
4. Аналитик BI (Middle Specialist)
5. Программист (Junior)

**Expected Feedback:**
- ✅ "Skills are now specific and detailed"
- ✅ "No more generic 'например' phrases"
- ✅ "Career paths are complete"
- ✅ "KPI count is reasonable (4-6)"
- ⚠️ "KPI selection improved but not perfect yet" (waiting for Phase 2)

---

## RISKS & MITIGATION

### Risk #1: LLM Refuses Strict Rules

**Probability:** LOW
**Impact:** HIGH

**Mitigation:**
- Added fallback instruction in reformulated Rule #4: "If strict rules limit generation, note in metadata but complete profile"
- Monitor refusal rate in Langfuse
- If >10% refusals → relax specific rules

### Risk #2: Phase 1 Results Don't Meet Expectations

**Probability:** LOW
**Impact:** MEDIUM

**Mitigation:**
- Day 2 testing provides early feedback
- Can iterate on prompt before finalizing
- Phase 2 provides additional quality boost

### Risk #3: Client Wants Faster Results

**Probability:** MEDIUM
**Impact:** LOW

**Mitigation:**
- Phase 1 delivers 60% improvement in 2-3 days (quick win!)
- Show incremental progress
- Phase 2 is independent, can be expedited if needed

---

## NEXT: PART 3 - PHASE 2 BACKEND FILTERING

Continue to [IMPLEMENTATION_PLAN_PART3_PHASE2.md](IMPLEMENTATION_PLAN_PART3_PHASE2.md) for:
- Backend KPI filtering architecture
- Code implementation details
- Integration with DataLoader
- Testing strategy
- Week 2-3 timeline

---

**Status:** ✅ Part 2 (Phase 1) Complete
**Effort Estimate:** 2-3 days
**Expected Quality:** 2.8/10 → 6.0/10 (+114%)
**Risk Level:** LOW

Captain, Phase 1 план детально расписан! Готов к началу работы! 🫡

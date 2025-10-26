й# План Работы: Распределение Задач Между Агентами

**Дата**: 2025-10-26
**Общее время**: 3-4 часа
**Количество агентов**: 4 (параллельная работа)

---

## 📊 Общая Структура Плана

### Этап 1: Подготовка (30 минут)
- **Агент**: general-purpose
- **Задачи**: Backup промпта, подготовка окружения

### Этап 2: Внедрение P0 Правок (2 часа) - ПАРАЛЛЕЛЬНО
- **Агент 1**: prompt-engineer (правки промпта)
- **Агент 2**: python-pro (код валидации)
- **Агент 3**: test-automator (автоматические тесты)

### Этап 3: Тестирование (1 час) - ПАРАЛЛЕЛЬНО
- **Агент 1-4**: general-purpose x 4 (генерация 4 профилей параллельно)

### Этап 4: Валидация и Отчет (30 минут)
- **Агент**: data-scientist (анализ результатов, отчет)

---

## 🎯 ЭТАП 1: Подготовка (30 минут)

### Задача 1.1: Создать Backup Текущего Промпта

**Агент**: general-purpose
**Время**: 5 минут
**Приоритет**: CRITICAL (без этого не начинаем)

**Команда**:
```bash
# Создать backup с timestamp
cp templates/prompts/production/prompt.txt \
   templates/prompts/production/prompt.txt.backup_$(date +%Y%m%d_%H%M%S)

# Также создать в archive
mkdir -p archive/prompts
cp templates/prompts/production/prompt.txt \
   archive/prompts/prompt_before_P0_fixes_$(date +%Y%m%d_%H%M%S).txt
```

**Критерий успеха**:
- ✅ Файлы backup созданы
- ✅ Можно откатиться в случае проблем

---

### Задача 1.2: Проверить Текущее Состояние

**Агент**: general-purpose
**Время**: 10 минут

**Команды**:
```bash
# Проверить что промпт существует
ls -lah templates/prompts/production/prompt.txt

# Проверить структуру
head -50 templates/prompts/production/prompt.txt

# Проверить что генератор работает
python -c "
from backend.core.profile_generator import ProfileGenerator
generator = ProfileGenerator()
print('Generator initialized successfully')
"
```

**Критерий успеха**:
- ✅ Промпт найден и читается
- ✅ Генератор инициализируется без ошибок

---

### Задача 1.3: Подготовить Тестовые Данные

**Агент**: general-purpose
**Время**: 15 минут

**Создать файл тестовых профилей**:
```python
# tests/test_data/test_profiles.py

TEST_PROFILES = [
    {
        "name": "Backend Python",
        "position": "Backend разработчик Python",
        "department": "Департамент информационных технологий",
        "expected_quality": 9.5,
        "sphere": "IT"
    },
    {
        "name": "Главбух",
        "position": "Главный бухгалтер",
        "department": "Финансовый департамент",
        "expected_quality": 9.3,
        "sphere": "Finance"
    },
    {
        "name": "HRBP",
        "position": "HR Business Partner",
        "department": "Департамент персонала",
        "expected_quality": 9.0,
        "sphere": "HR"
    },
    {
        "name": "Sales B2B",
        "position": "Менеджер по продажам B2B",
        "department": "Департамент продаж",
        "expected_quality": 8.5,
        "sphere": "Sales"
    }
]
```

**Критерий успеха**:
- ✅ Файл создан
- ✅ 4 тестовых профиля определены

---

## 🚀 ЭТАП 2: Внедрение P0 Правок (2 часа ПАРАЛЛЕЛЬНО)

### АГЕНТ 1: prompt-engineer - Правки Промпта

**Время**: 2 часа (110 минут)
**Файлы**: `templates/prompts/production/prompt.txt`

---

#### Задача 2.1.1: P0.1 - Конкретность vs Многословность (30 минут)

**Что сделать**:

Найти секцию с описанием `responsibility_areas` и добавить ПОСЛЕ неё:

```markdown
---

## ВАЖНО: КОНКРЕТНОСТЬ ЗАДАЧ vs МНОГОСЛОВНОСТЬ

### Правила описания задач:

1. **НАЧИНАТЬ С ДЕЙСТВИЯ** (существительное):
   - Моделирование, Контроль, Проверка, Создание, Подготовка, Координация
   - НЕ использовать инфинитивы: "Разрабатывать", "Обеспечивать"

2. **ДОБАВЛЯТЬ КОНКРЕТИКУ** (перечисления, списки, стандарты):

   ✅ ПРАВИЛЬНО:
   - "Моделирование перекрытий, колонн, пилонов, стен, окон, дверей"
   - "Проверка на соответствие ГОСТ, СНиП, СП, стандартам компании"
   - "Координация с КР, ОВ, ВК, ЭОМ, СС"
   - "Разработка REST API, GraphQL endpoints, GRPC сервисов"
   - "Подготовка отчетности: МСФО, РСБУ, налоговые декларации"

   ❌ НЕПРАВИЛЬНО:
   - "Разрабатывать архитектурные разделы проектов в соответствии с техническим заданием"
   - "Обеспечивать соответствие проектных решений нормативным требованиям"
   - "Осуществление подготовки документации"

3. **УБИРАТЬ СЛУЖЕБНЫЕ ФРАЗЫ** (filler phrases):
   - ❌ "в соответствии с техническим заданием и требованиями"
   - ❌ "обеспечивать соответствие проектных решений"
   - ❌ "осуществление подготовки"
   - ❌ "выполнение работ по"

4. **ДЛИНА - НЕ ГЛАВНОЕ**:
   - ✅ Если 80 символов, но 5 конкретных элементов → ХОРОШО
   - ❌ Если 50 символов, но 0 конкретики → ПЛОХО

### Формула успешной задачи:

```
[Действие] + [Конкретные элементы/список] + [опциональный контекст]
```

### Примеры по сферам:

**IT:**
- "Разработка микросервисов: REST API, GraphQL, GRPC, документация OpenAPI"
- "Оптимизация SQL: индексы, партиционирование, кэширование, анализ планов"

**Финансы:**
- "Подготовка отчетности: МСФО, РСБУ, управленческий учет, налоговые декларации"
- "Контроль дебиторской задолженности: мониторинг, напоминания, урегулирование"

**HR:**
- "Подбор специалистов: интервьюирование, assessment center, оффер, онбординг"
- "Оценка персонала: 360-feedback, калибровка, IDP, succession planning"

**Продажи:**
- "Ведение CRM: регистрация лидов, квалификация, pipeline management, отчеты"
- "Проведение презентаций: демо продукта, ROI-анализ, кейсы, Q&A"

### МЕТРИКА (для валидации):
- concrete_elements >= 2 (минимум 2 конкретных элемента на задачу)
- filler_ratio < 15% (максимум 15% служебных слов)
- action_word_first = True (задача начинается с действия)

---
```

**Критерий успеха**:
- ✅ Секция добавлена в промпт
- ✅ 10+ примеров правильных задач
- ✅ Метрики определены

---

#### Задача 2.1.2: P0.2 - Методики для Soft Skills (30 минут)

**Что сделать**:

Найти секцию с описанием `professional_skills` и добавить ПОСЛЕ неё:

```markdown
---

## ВАЖНО: МЕТОДИКИ ДЛЯ SOFT SKILLS

### Правило:

Для КАЖДОГО soft skill ОБЯЗАТЕЛЬНО указать методику/фреймворк.

### Применяется ТОЛЬКО к ролям:
- HR (HRBP, Recruiter, HR Manager, Trainer)
- Sales (Sales Manager, Account Manager, BD)
- Management (Team Lead, Department Head, Director)
- Customer Success (CS Manager, Support Manager)

### Если роль НЕ содержит soft skills → правило НЕ применяется

### Примеры трансформации:

❌ НЕПРАВИЛЬНО (без методики):
- "Коммуникация с заинтересованными сторонами"
- "Управление изменениями"
- "Развитие сотрудников"
- "Переговоры с клиентами"

✅ ПРАВИЛЬНО (с методикой):
- "Коммуникация с заинтересованными сторонами (RACI framework, stakeholder mapping, регулярные sync-up встречи)"
- "Управление изменениями (Kotter 8 steps, change communication plan, resistance management)"
- "Развитие сотрудников (GROW model, structured feedback, IDP, 70-20-10 learning)"
- "Переговоры с клиентами (BATNA, Win-Win approach, Principled Negotiation, active listening)"

### Справочник методик по типам soft skills:

**Coaching & Feedback:**
- GROW model (Goal, Reality, Options, Will)
- CLEAR model (Contract, Listen, Explore, Action, Review)
- SBI feedback (Situation-Behavior-Impact)
- Radical Candor framework

**Влияние и Убеждение:**
- Cialdini's 6 principles of influence
- SCARF model (Status, Certainty, Autonomy, Relatedness, Fairness)
- Storytelling techniques

**Переговоры:**
- BATNA (Best Alternative To Negotiated Agreement)
- Win-Win negotiation (Getting to Yes)
- Principled Negotiation
- ZOPA (Zone of Possible Agreement)

**Change Management:**
- Kotter's 8 steps
- ADKAR model (Awareness, Desire, Knowledge, Ability, Reinforcement)
- Lewin's Change Model (Unfreeze-Change-Refreeze)
- McKinsey 7S framework

**Stakeholder Management:**
- Power-Interest matrix
- RACI framework (Responsible, Accountable, Consulted, Informed)
- Stakeholder mapping
- Influence diagrams

**Лидерство:**
- Situational Leadership (Hersey-Blanchard)
- Transformational Leadership
- Servant Leadership
- Emotional Intelligence (Goleman)

**Презентации:**
- STAR method (Situation, Task, Action, Result)
- Pyramid Principle (McKinsey)
- Storytelling arc

**Управление Командой:**
- Tuckman's stages (Forming, Storming, Norming, Performing)
- Team Canvas
- Belbin Team Roles

### МЕТРИКА (для валидации):
- IF skill_type == "soft_skill"
- THEN has_methodology == True (упоминается минимум 1 методика/фреймворк)

---
```

**Критерий успеха**:
- ✅ Секция добавлена
- ✅ 30+ методик в справочнике
- ✅ Условие применения (только для soft skills ролей)

---

#### Задача 2.1.3: P0.3 - Regulatory Frameworks (10 минут)

**Что сделать**:

Найти секцию анализа контекста (в начале промпта) и добавить:

```markdown
---

## ВАЖНО: РЕГУЛЯТИВНЫЕ ТРЕБОВАНИЯ ПО СФЕРАМ

### Обязательные regulatory frameworks по доменам:

**Финансы (Finance):**
- МСФО/IFRS - международные стандарты финансовой отчетности
- РСБУ - российские стандарты бухгалтерского учета
- Налоговое законодательство РФ
- (Опционально) GAAP - для международных компаний

**HR (Human Resources):**
- ТК РФ (Трудовое право) - ОБЯЗАТЕЛЬНО для ВСЕХ HR ролей ❗
- 152-ФЗ (Персональные данные)
- Кадровое делопроизводство

**Legal (Юридический):**
- ГК РФ, специализация по отраслям
- Корпоративное право
- Антимонопольное законодательство (если применимо)

**Construction/Architecture (Строительство):**
- ГОСТ - государственные стандарты
- СНиП - строительные нормы и правила
- СП - своды правил
- Градостроительный кодекс

**Healthcare (Здравоохранение):**
- Медицинские стандарты
- Санитарные нормы
- Федеральный закон об охране здоровья

**IT (Информационные технологии):**
- Архитектурные паттерны (Microservices, Event-Driven, CQRS)
- Security best practices (OWASP Top 10, secure coding)
- (Опционально) ISO 27001 - для информационной безопасности

**Operations/Quality (Операции):**
- ISO 9001 - система менеджмента качества (если компания сертифицирована)
- Lean/Six Sigma (для производства)

### Автоматическое применение:

```
IF department in ["Финансовый департамент", "Бухгалтерия", "Finance"]:
    ADD skill: "МСФО/РСБУ - методики признания выручки, оценки активов, отчетность"
    ADD skill: "Налоговое законодательство РФ - расчеты, декларации, оптимизация"

IF department in ["Департамент персонала", "HR", "Human Resources"]:
    ADD skill: "Трудовое право РФ (ТК РФ) - оформление трудовых отношений, процедуры увольнения, взаимодействие с ГИТ, compliance" (Level 2-3)
    ADD skill: "Персональные данные (152-ФЗ) - обработка, хранение, защита, соответствие требованиям" (Level 2)

IF department in ["Юридический департамент", "Legal"]:
    ADD skill: "ГК РФ - корпоративное право, договорная работа, сопровождение сделок"

IF department in ["Архитектурное бюро", "Проектный институт", "Construction"]:
    ADD skill: "ГОСТ, СНиП, СП - нормативная база проектирования, соответствие стандартам"

IF department in ["IT", "Департамент информационных технологий"]:
    ADD skill: "Архитектурные паттерны - Microservices, Event-Driven, CQRS, проектирование систем"
```

### МЕТРИКА (для валидации):
- IF domain in ["Finance", "HR", "Legal", "Construction"]
- THEN has_regulatory_framework == True

---
```

**Критерий успеха**:
- ✅ Секция добавлена
- ✅ 5+ доменов покрыты
- ✅ Автоматическое применение описано

---

#### Задача 2.1.4: P0.4 - Разные Описания Уровней (30 минут)

**Что сделать**:

Найти секцию `proficiency_level` и ЗАМЕНИТЬ на:

```markdown
---

## УРОВНИ ВЛАДЕНИЯ (proficiency_level)

### КРИТИЧЕСКИ ВАЖНО: Для КАЖДОГО уровня используется РАЗНОЕ описание

**Категорически ЗАПРЕЩЕНО** копировать одинаковое описание для разных уровней!

### Определения уровней:

**Level 1 - Базовый (Junior, начальный уровень):**
```
"proficiency_description": "Базовые знания и опыт применения в стандартных ситуациях"
```

**Характеристики:**
- Может выполнять типовые задачи под контролем
- Знает основы, но требуется наставничество
- Применяет знания в простых, повторяющихся ситуациях
- Нуждается в руководстве при возникновении проблем

**Примеры навыков Level 1:**
- Знание основ языка программирования
- Базовые навыки работы с Excel
- Знание основных нормативных документов

---

**Level 2 - Средний (Middle, профессиональный уровень):**
```
"proficiency_description": "Существенные знания и опыт применения в ситуациях повышенной сложности"
```

**Характеристики:**
- Самостоятельно решает нестандартные задачи
- Понимает контекст и может адаптировать решения
- Работает в сложных проектах без постоянного контроля
- Может помогать junior специалистам

**Примеры навыков Level 2:**
- Оптимизация SQL запросов
- Продвинутый Excel (Power Query, макросы)
- Применение нормативов в нестандартных ситуациях

---

**Level 3 - Высокий (Senior, экспертный уровень):**
```
"proficiency_description": "Глубокие знания, опыт применения в кризисных ситуациях, готовность обучать других"
```

**Характеристики:**
- Эксперт в области, может обучать других
- Принимает решения в критических ситуациях
- Разрабатывает методологии и best practices
- Может быть ментором для команды

**Примеры навыков Level 3:**
- Архитектура систем, проектирование с нуля
- Финансовое моделирование и прогнозирование
- Экспертиза в сложных юридических кейсах

---

**Level 4 - Эксперт (для исключительных случаев):**
```
"proficiency_description": "Экспертные знания, способность разрабатывать методологии и стандарты, признанный эксперт в области"
```

**Характеристики:**
- Индустриальный эксперт, публикации, выступления
- Разрабатывает стандарты для компании/отрасли
- Консультирует топ-менеджмент по стратегическим вопросам

**Используется редко, только для исключительных компетенций**

---

### Распределение уровней в профиле (рекомендации):

**Junior позиции:**
- Level 1: 50-60% навыков
- Level 2: 30-40% навыков
- Level 3: 0-10% навыков

**Middle позиции:**
- Level 1: 10-20% навыков
- Level 2: 60-70% навыков
- Level 3: 20-30% навыков

**Senior позиции:**
- Level 1: 0-5% навыков
- Level 2: 30-40% навыков
- Level 3: 55-70% навыков

**Expert/Lead позиции:**
- Level 1: 0% навыков
- Level 2: 20-30% навыков
- Level 3: 60-70% навыков
- Level 4: 5-15% навыков

---

### ВАЛИДАЦИЯ (критически важно):

```python
# Проверка что описания РАЗНЫЕ для каждого уровня
descriptions = {}
for skill in all_skills:
    level = skill['proficiency_level']
    desc = skill['proficiency_description']
    descriptions[level] = desc

# ДОЛЖНО БЫТЬ: len(set(descriptions.values())) == len(descriptions)
# Т.е. все описания уникальны

assert len(set(descriptions.values())) == len(descriptions), \
    "ОШИБКА: Найдены одинаковые описания для разных уровней!"
```

### Примеры ПРАВИЛЬНЫХ описаний в профиле:

```json
{
  "professional_skills": [
    {
      "skill_name": "Python - разработка backend сервисов",
      "proficiency_level": 3,
      "proficiency_description": "Глубокие знания, опыт применения в кризисных ситуациях, готовность обучать других"
    },
    {
      "skill_name": "Docker - контейнеризация приложений",
      "proficiency_level": 2,
      "proficiency_description": "Существенные знания и опыт применения в ситуациях повышенной сложности"
    },
    {
      "skill_name": "Kubernetes - базовые концепции оркестрации",
      "proficiency_level": 1,
      "proficiency_description": "Базовые знания и опыт применения в стандартных ситуациях"
    }
  ]
}
```

### ⚠️ ЧАСТАЯ ОШИБКА (которую нужно избегать):

```json
❌ НЕПРАВИЛЬНО:
{
  "skill_name": "Python",
  "proficiency_level": 3,
  "proficiency_description": "Существенные знания и опыт применения в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях"
},
{
  "skill_name": "Docker",
  "proficiency_level": 2,
  "proficiency_description": "Существенные знания и опыт применения в ситуациях повышенной сложности, в т.ч. в кризисных ситуациях"
}

# ПРОБЛЕМА: Одинаковое описание для Level 3 и Level 2!
```

---
```

**Критерий успеха**:
- ✅ Секция заменена
- ✅ 3-4 уровня с РАЗНЫМИ описаниями
- ✅ Валидация описана
- ✅ Примеры правильных и неправильных описаний

---

### АГЕНТ 2: python-pro - Код Валидации

**Время**: 1.5 часа (90 минут)
**Файлы**:
- `backend/core/profile_validator.py` (новый)
- `backend/core/profile_generator.py` (обновление)

---

#### Задача 2.2.1: Создать Модуль Валидации (60 минут)

**Создать файл**: `backend/core/profile_validator.py`

```python
"""
Валидация профилей по новым метрикам P0.

Метрики:
- P0.1: Конкретность задач (concrete_elements >= 2, filler_ratio < 15%)
- P0.2: Методики для soft skills (has_methodology if soft_skill)
- P0.3: Regulatory frameworks (has_framework if applicable domain)
- P0.4: Разные уровни владения (unique descriptions per level)
"""

import re
from typing import Dict, List, Any, Tuple
import json


class ProfileValidator:
    """Валидатор качества профилей по метрикам P0."""

    # Служебные фразы (filler phrases)
    FILLER_PHRASES = [
        "в соответствии с",
        "обеспечивать соответствие",
        "осуществление подготовки",
        "выполнение работ по",
        "проведение мероприятий",
        "обеспечение выполнения"
    ]

    # Regulatory frameworks по доменам
    REGULATORY_FRAMEWORKS = {
        'finance': ['МСФО', 'IFRS', 'РСБУ', 'налоговый', 'GAAP'],
        'hr': ['ТК РФ', 'Трудовое право', '152-ФЗ', 'персональные данные'],
        'legal': ['ГК РФ', 'корпоративное право', 'АПК'],
        'construction': ['ГОСТ', 'СНиП', 'СП', 'градостроительный'],
        'it': ['архитектурн', 'паттерн', 'security', 'OWASP']
    }

    # Методики для soft skills
    SOFT_SKILL_METHODOLOGIES = [
        'GROW', 'CLEAR', 'SBI', 'BATNA', 'Kotter', 'ADKAR',
        'RACI', 'SCARF', 'Cialdini', 'Win-Win', 'framework',
        'model', 'method', 'approach', 'technique'
    ]

    def validate_task_concreteness(self, task: str) -> Dict[str, Any]:
        """
        P0.1: Валидация конкретности задачи.

        Returns:
            {
                'valid': bool,
                'concrete_elements': int,
                'filler_ratio': float,
                'issues': List[str]
            }
        """
        issues = []

        # Подсчет конкретных элементов (перечисления через запятую)
        concrete_elements = len([p for p in task.split(',') if len(p.strip()) > 2])

        # Если нет запятых, проверяем списки через союзы
        if concrete_elements <= 1:
            concrete_patterns = [' и ', ' или ', ': ']
            for pattern in concrete_patterns:
                concrete_elements += task.count(pattern)

        # Подсчет filler phrases
        filler_count = sum(1 for phrase in self.FILLER_PHRASES if phrase in task.lower())
        words_count = len(task.split())
        filler_ratio = filler_count / max(words_count, 1) if words_count > 0 else 0

        # Проверки
        if concrete_elements < 2:
            issues.append(f"Недостаточно конкретных элементов: {concrete_elements} < 2")

        if filler_ratio >= 0.15:
            issues.append(f"Слишком много служебных фраз: {filler_ratio:.1%} >= 15%")

        return {
            'valid': len(issues) == 0,
            'concrete_elements': concrete_elements,
            'filler_ratio': filler_ratio,
            'task_length': len(task),
            'issues': issues
        }

    def validate_soft_skill_methodology(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """
        P0.2: Валидация наличия методики для soft skill.

        Returns:
            {
                'valid': bool,
                'is_soft_skill': bool,
                'has_methodology': bool,
                'found_methodologies': List[str],
                'issues': List[str]
            }
        """
        issues = []
        skill_text = f"{skill.get('skill_name', '')} {skill.get('description', '')}".lower()

        # Определяем soft skill по ключевым словам
        soft_skill_keywords = [
            'coaching', 'leadership', 'коммуникац', 'переговор',
            'влияние', 'убеждение', 'изменени', 'stakeholder',
            'команд', 'презентац', 'обучен'
        ]
        is_soft_skill = any(keyword in skill_text for keyword in soft_skill_keywords)

        # Ищем методики
        found_methodologies = [
            method for method in self.SOFT_SKILL_METHODOLOGIES
            if method.lower() in skill_text
        ]
        has_methodology = len(found_methodologies) > 0

        # Валидация: если soft skill, должна быть методика
        if is_soft_skill and not has_methodology:
            issues.append(f"Soft skill без методики: {skill.get('skill_name', 'N/A')}")

        return {
            'valid': len(issues) == 0,
            'is_soft_skill': is_soft_skill,
            'has_methodology': has_methodology,
            'found_methodologies': found_methodologies,
            'issues': issues
        }

    def validate_regulatory_frameworks(
        self,
        profile: Dict[str, Any],
        domain: str = None
    ) -> Dict[str, Any]:
        """
        P0.3: Валидация наличия regulatory frameworks.

        Args:
            profile: Полный профиль
            domain: 'finance', 'hr', 'legal', 'construction', 'it'

        Returns:
            {
                'valid': bool,
                'domain': str,
                'required': bool,
                'has_framework': bool,
                'found_frameworks': List[str],
                'issues': List[str]
            }
        """
        issues = []

        # Автоопределение домена из department
        if not domain:
            department = profile.get('department_specific', '').lower()
            if any(word in department for word in ['финанс', 'бухгалтер', 'finance']):
                domain = 'finance'
            elif any(word in department for word in ['персонал', 'hr', 'кадр']):
                domain = 'hr'
            elif any(word in department for word in ['юридич', 'legal', 'правов']):
                domain = 'legal'
            elif any(word in department for word in ['проектир', 'архитектур', 'строител']):
                domain = 'construction'
            elif any(word in department for word in ['it', 'информац', 'разработ']):
                domain = 'it'
            else:
                domain = 'unknown'

        required_frameworks = self.REGULATORY_FRAMEWORKS.get(domain, [])
        required = len(required_frameworks) > 0

        # Проверяем наличие фреймворков в навыках
        profile_text = json.dumps(profile, ensure_ascii=False).lower()
        found_frameworks = [
            fw for fw in required_frameworks
            if fw.lower() in profile_text
        ]
        has_framework = len(found_frameworks) > 0

        # Валидация
        if required and not has_framework:
            issues.append(
                f"Отсутствуют regulatory frameworks для домена '{domain}'. "
                f"Ожидаются: {', '.join(required_frameworks)}"
            )

        return {
            'valid': len(issues) == 0,
            'domain': domain,
            'required': required,
            'has_framework': has_framework,
            'found_frameworks': found_frameworks,
            'expected_frameworks': required_frameworks,
            'issues': issues
        }

    def validate_proficiency_levels(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        P0.4: Валидация различающихся описаний уровней владения.

        Returns:
            {
                'valid': bool,
                'levels_found': List[int],
                'unique_descriptions': int,
                'should_be_unique': int,
                'duplicate_descriptions': Dict[str, List[int]],
                'issues': List[str]
            }
        """
        issues = []
        descriptions_by_level = {}

        # Собираем описания по уровням
        for skill_cat in profile.get('professional_skills', []):
            for skill in skill_cat.get('specific_skills', []):
                level = skill.get('proficiency_level')
                desc = skill.get('proficiency_description', '')
                if level and desc:
                    if level not in descriptions_by_level:
                        descriptions_by_level[level] = desc
                    elif descriptions_by_level[level] != desc:
                        # Разные описания для одного уровня - это ОК
                        pass

        levels_found = sorted(descriptions_by_level.keys())
        unique_descriptions = len(set(descriptions_by_level.values()))
        should_be_unique = len(descriptions_by_level)

        # Находим дубликаты
        desc_to_levels = {}
        for level, desc in descriptions_by_level.items():
            if desc not in desc_to_levels:
                desc_to_levels[desc] = []
            desc_to_levels[desc].append(level)

        duplicate_descriptions = {
            desc: levels for desc, levels in desc_to_levels.items()
            if len(levels) > 1
        }

        # Валидация: каждый уровень должен иметь уникальное описание
        if unique_descriptions < should_be_unique:
            issues.append(
                f"Найдены одинаковые описания для разных уровней: "
                f"{unique_descriptions} уникальных из {should_be_unique} уровней"
            )
            for desc, levels in duplicate_descriptions.items():
                issues.append(f"  Уровни {levels}: '{desc[:50]}...'")

        return {
            'valid': len(issues) == 0,
            'levels_found': levels_found,
            'unique_descriptions': unique_descriptions,
            'should_be_unique': should_be_unique,
            'duplicate_descriptions': duplicate_descriptions,
            'issues': issues
        }

    def validate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полная валидация профиля по всем метрикам P0.

        Returns:
            {
                'valid': bool,
                'quality_score': float (0-10),
                'metrics': {
                    'p0_1_tasks': {...},
                    'p0_2_soft_skills': {...},
                    'p0_3_regulatory': {...},
                    'p0_4_levels': {...}
                },
                'summary': {
                    'total_issues': int,
                    'critical_issues': List[str],
                    'warnings': List[str]
                }
            }
        """
        all_issues = []
        all_warnings = []

        # P0.1: Валидация задач
        tasks_results = []
        for area in profile.get('responsibility_areas', []):
            for task in area.get('tasks', []):
                result = self.validate_task_concreteness(task)
                tasks_results.append(result)
                if not result['valid']:
                    all_issues.extend(result['issues'])

        tasks_valid_ratio = (
            sum(1 for r in tasks_results if r['valid']) / len(tasks_results)
            if tasks_results else 0
        )

        # P0.2: Валидация soft skills
        soft_skills_results = []
        for skill_cat in profile.get('professional_skills', []):
            for skill in skill_cat.get('specific_skills', []):
                result = self.validate_soft_skill_methodology(skill)
                soft_skills_results.append(result)
                if not result['valid']:
                    all_warnings.extend(result['issues'])  # Warning, не critical

        soft_skills_valid_ratio = (
            sum(1 for r in soft_skills_results if r['valid']) / len(soft_skills_results)
            if soft_skills_results else 1.0
        )

        # P0.3: Валидация regulatory frameworks
        regulatory_result = self.validate_regulatory_frameworks(profile)
        if not regulatory_result['valid']:
            if regulatory_result['required']:
                all_issues.extend(regulatory_result['issues'])
            else:
                all_warnings.extend(regulatory_result['issues'])

        # P0.4: Валидация уровней владения
        levels_result = self.validate_proficiency_levels(profile)
        if not levels_result['valid']:
            all_issues.extend(levels_result['issues'])

        # Расчет quality score
        quality_score = (
            tasks_valid_ratio * 3 +  # 30% веса
            soft_skills_valid_ratio * 2 +  # 20% веса
            (1 if regulatory_result['valid'] else 0) * 2 +  # 20% веса
            (1 if levels_result['valid'] else 0) * 3  # 30% веса
        )

        return {
            'valid': len(all_issues) == 0,
            'quality_score': quality_score,
            'metrics': {
                'p0_1_tasks': {
                    'total_tasks': len(tasks_results),
                    'valid_tasks': sum(1 for r in tasks_results if r['valid']),
                    'valid_ratio': tasks_valid_ratio,
                    'avg_concrete_elements': (
                        sum(r['concrete_elements'] for r in tasks_results) / len(tasks_results)
                        if tasks_results else 0
                    ),
                    'avg_filler_ratio': (
                        sum(r['filler_ratio'] for r in tasks_results) / len(tasks_results)
                        if tasks_results else 0
                    )
                },
                'p0_2_soft_skills': {
                    'total_skills': len(soft_skills_results),
                    'soft_skills_count': sum(1 for r in soft_skills_results if r['is_soft_skill']),
                    'with_methodology': sum(
                        1 for r in soft_skills_results
                        if r['is_soft_skill'] and r['has_methodology']
                    ),
                    'valid_ratio': soft_skills_valid_ratio
                },
                'p0_3_regulatory': regulatory_result,
                'p0_4_levels': levels_result
            },
            'summary': {
                'total_issues': len(all_issues),
                'total_warnings': len(all_warnings),
                'critical_issues': all_issues,
                'warnings': all_warnings
            }
        }


def main():
    """Пример использования валидатора."""
    validator = ProfileValidator()

    # Пример профиля для валидации
    test_profile = {
        "department_specific": "Департамент персонала",
        "responsibility_areas": [
            {
                "area": ["Подбор и адаптация"],
                "tasks": [
                    "Подбор специалистов: интервьюирование, assessment center, оффер",
                    "Разрабатывать программы адаптации в соответствии с требованиями компании"
                ]
            }
        ],
        "professional_skills": [
            {
                "skill_category": "Подбор персонала",
                "specific_skills": [
                    {
                        "skill_name": "Интервьюирование",
                        "proficiency_level": 3,
                        "proficiency_description": "Глубокие знания..."
                    },
                    {
                        "skill_name": "Coaching сотрудников",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания..."
                    }
                ]
            }
        ]
    }

    result = validator.validate_profile(test_profile)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

**Критерий успеха**:
- ✅ Файл создан
- ✅ 4 метода валидации (P0.1-P0.4)
- ✅ Метод validate_profile (общий)
- ✅ Тесты работают

---

### АГЕНТ 3: test-automator - Автоматические Тесты

**Время**: 1 час (60 минут)
**Файлы**: `tests/test_profile_quality.py` (новый)

**Задача**: Создать автоматические тесты для валидации

```python
"""
Автоматические тесты для валидации качества профилей.
"""

import pytest
import sys
sys.path.insert(0, '/home/yan/A101/HR')

from backend.core.profile_validator import ProfileValidator


class TestP01TaskConcreteness:
    """Тесты для P0.1: Конкретность задач."""

    def test_good_task_with_list(self):
        """Хорошая задача со списком элементов."""
        validator = ProfileValidator()
        task = "Моделирование перекрытий, колонн, пилонов, стен, окон"
        result = validator.validate_task_concreteness(task)

        assert result['valid'] == True
        assert result['concrete_elements'] >= 5
        assert result['filler_ratio'] < 0.15

    def test_bad_task_with_filler(self):
        """Плохая задача с filler phrases."""
        validator = ProfileValidator()
        task = "Разрабатывать проекты в соответствии с техническим заданием и требованиями"
        result = validator.validate_task_concreteness(task)

        assert result['valid'] == False
        assert result['concrete_elements'] < 2

    def test_medium_task(self):
        """Средняя задача."""
        validator = ProfileValidator()
        task = "Подготовка отчетности: МСФО, РСБУ, налоговые декларации"
        result = validator.validate_task_concreteness(task)

        assert result['valid'] == True
        assert result['concrete_elements'] >= 3


class TestP02SoftSkillMethodologies:
    """Тесты для P0.2: Методики для soft skills."""

    def test_soft_skill_with_methodology(self):
        """Soft skill с методикой."""
        validator = ProfileValidator()
        skill = {
            "skill_name": "Coaching (GROW model, structured feedback)",
            "proficiency_level": 3
        }
        result = validator.validate_soft_skill_methodology(skill)

        assert result['valid'] == True
        assert result['is_soft_skill'] == True
        assert result['has_methodology'] == True

    def test_soft_skill_without_methodology(self):
        """Soft skill без методики - ошибка."""
        validator = ProfileValidator()
        skill = {
            "skill_name": "Coaching сотрудников",
            "proficiency_level": 2
        }
        result = validator.validate_soft_skill_methodology(skill)

        assert result['valid'] == False
        assert result['is_soft_skill'] == True
        assert result['has_methodology'] == False

    def test_technical_skill_no_methodology_needed(self):
        """Технический навык - методика не нужна."""
        validator = ProfileValidator()
        skill = {
            "skill_name": "Python - разработка backend",
            "proficiency_level": 3
        }
        result = validator.validate_soft_skill_methodology(skill)

        assert result['valid'] == True
        assert result['is_soft_skill'] == False


class TestP03RegulatoryFrameworks:
    """Тесты для P0.3: Regulatory frameworks."""

    def test_finance_with_frameworks(self):
        """Финансовый профиль с МСФО."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Финансовый департамент",
            "professional_skills": [{
                "skill_category": "Бухгалтерский учет",
                "specific_skills": [{
                    "skill_name": "МСФО - методики признания выручки"
                }]
            }]
        }
        result = validator.validate_regulatory_frameworks(profile)

        assert result['valid'] == True
        assert result['domain'] == 'finance'
        assert result['has_framework'] == True

    def test_hr_with_tk_rf(self):
        """HR профиль с ТК РФ."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент персонала",
            "professional_skills": [{
                "skill_category": "HR compliance",
                "specific_skills": [{
                    "skill_name": "Трудовое право РФ (ТК РФ)"
                }]
            }]
        }
        result = validator.validate_regulatory_frameworks(profile)

        assert result['valid'] == True
        assert result['domain'] == 'hr'
        assert result['has_framework'] == True

    def test_hr_without_tk_rf(self):
        """HR профиль БЕЗ ТК РФ - ошибка."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент персонала",
            "professional_skills": []
        }
        result = validator.validate_regulatory_frameworks(profile)

        assert result['valid'] == False
        assert result['domain'] == 'hr'
        assert result['required'] == True
        assert result['has_framework'] == False


class TestP04ProficiencyLevels:
    """Тесты для P0.4: Разные уровни владения."""

    def test_different_descriptions_for_levels(self):
        """Разные описания для каждого уровня - OK."""
        validator = ProfileValidator()
        profile = {
            "professional_skills": [{
                "skill_category": "Technical",
                "specific_skills": [
                    {
                        "skill_name": "Python",
                        "proficiency_level": 3,
                        "proficiency_description": "Глубокие знания, опыт в кризисных ситуациях"
                    },
                    {
                        "skill_name": "Docker",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания в сложных ситуациях"
                    },
                    {
                        "skill_name": "K8s",
                        "proficiency_level": 1,
                        "proficiency_description": "Базовые знания в стандартных ситуациях"
                    }
                ]
            }]
        }
        result = validator.validate_proficiency_levels(profile)

        assert result['valid'] == True
        assert result['unique_descriptions'] == 3
        assert result['should_be_unique'] == 3

    def test_same_description_for_different_levels(self):
        """Одинаковое описание для разных уровней - ошибка."""
        validator = ProfileValidator()
        profile = {
            "professional_skills": [{
                "skill_category": "Technical",
                "specific_skills": [
                    {
                        "skill_name": "Python",
                        "proficiency_level": 3,
                        "proficiency_description": "Существенные знания"
                    },
                    {
                        "skill_name": "Docker",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания"
                    }
                ]
            }]
        }
        result = validator.validate_proficiency_levels(profile)

        assert result['valid'] == False
        assert result['unique_descriptions'] < result['should_be_unique']


class TestProfileValidation:
    """Интеграционные тесты полной валидации профиля."""

    def test_good_profile_all_checks_pass(self):
        """Хороший профиль проходит все проверки."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент информационных технологий",
            "responsibility_areas": [{
                "area": ["Разработка"],
                "tasks": [
                    "Разработка REST API, GraphQL endpoints, GRPC сервисов",
                    "Оптимизация SQL: индексы, партиционирование, кэширование"
                ]
            }],
            "professional_skills": [{
                "skill_category": "Backend development",
                "specific_skills": [
                    {
                        "skill_name": "Python - разработка сервисов",
                        "proficiency_level": 3,
                        "proficiency_description": "Глубокие знания, опыт в кризисных ситуациях, обучение других"
                    },
                    {
                        "skill_name": "Docker - контейнеризация",
                        "proficiency_level": 2,
                        "proficiency_description": "Существенные знания в сложных ситуациях"
                    }
                ]
            }]
        }
        result = validator.validate_profile(profile)

        assert result['valid'] == True
        assert result['quality_score'] >= 8.0
        assert result['summary']['total_issues'] == 0

    def test_bad_profile_multiple_issues(self):
        """Плохой профиль с несколькими проблемами."""
        validator = ProfileValidator()
        profile = {
            "department_specific": "Департамент персонала",
            "responsibility_areas": [{
                "area": ["HR"],
                "tasks": [
                    "Разрабатывать программы в соответствии с требованиями"
                ]
            }],
            "professional_skills": [{
                "skill_category": "HR",
                "specific_skills": [
                    {
                        "skill_name": "Coaching",  # Без методики
                        "proficiency_level": 3,
                        "proficiency_description": "Знания"  # Одинаково для всех
                    },
                    {
                        "skill_name": "Recruitment",
                        "proficiency_level": 2,
                        "proficiency_description": "Знания"  # Одинаково
                    }
                ]
            }]
            # Нет ТК РФ!
        }
        result = validator.validate_profile(profile)

        assert result['valid'] == False
        assert result['quality_score'] < 7.0
        assert result['summary']['total_issues'] > 0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
```

**Критерий успеха**:
- ✅ 15+ тестов создано
- ✅ Покрытие всех 4 метрик P0
- ✅ Тесты проходят

---

## 🧪 ЭТАП 3: Тестирование (1 час ПАРАЛЛЕЛЬНО)

### Задача 3.1-3.4: Генерация 4 Профилей (Параллельно)

**4 агента general-purpose** запускаются ОДНОВРЕМЕННО:

**Агент 1**: Backend Python
```bash
python scripts/generate_single_profile.py \
  "Backend разработчик Python" \
  "Департамент информационных технологий"
```

**Агент 2**: Главбух
```bash
python scripts/generate_single_profile.py \
  "Главный бухгалтер" \
  "Финансовый департамент"
```

**Агент 3**: HRBP
```bash
python scripts/generate_single_profile.py \
  "HR Business Partner" \
  "Департамент персонала"
```

**Агент 4**: Sales B2B
```bash
python scripts/generate_single_profile.py \
  "Менеджер по продажам B2B" \
  "Департамент продаж"
```

**Время**: 15 минут на каждый профиль (параллельно = 15 минут total)

**Критерий успеха**:
- ✅ 4 профиля сгенерированы
- ✅ Файлы JSON созданы

---

## 📊 ЭТАП 4: Валидация и Отчет (30 минут)

### Задача 4.1: Валидировать Профили

**Агент**: python-pro
**Время**: 15 минут

**Скрипт валидации**:
```python
# scripts/validate_generated_profiles.py

import sys
import json
import glob
from pathlib import Path

sys.path.insert(0, '/home/yan/A101/HR')
from backend.core.profile_validator import ProfileValidator


def main():
    validator = ProfileValidator()

    # Находим последние сгенерированные профили
    profiles_dir = Path('generated_profiles')
    profile_files = sorted(profiles_dir.glob('*.json'), key=lambda x: x.stat().st_mtime)
    latest_profiles = profile_files[-4:]  # Последние 4

    results = []
    for profile_file in latest_profiles:
        print(f"\n{'='*60}")
        print(f"Валидация: {profile_file.name}")
        print(f"{'='*60}")

        with open(profile_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        result = validator.validate_profile(profile)
        result['file'] = profile_file.name
        result['position'] = profile.get('position_title', 'N/A')
        result['department'] = profile.get('department_specific', 'N/A')
        results.append(result)

        # Вывод результатов
        print(f"\n✅ VALID: {result['valid']}")
        print(f"📊 QUALITY SCORE: {result['quality_score']:.2f}/10")
        print(f"\n📈 МЕТРИКИ:")
        print(f"  P0.1 Задачи: {result['metrics']['p0_1_tasks']['valid_ratio']:.1%} валидных")
        print(f"       - Конкретных элементов: {result['metrics']['p0_1_tasks']['avg_concrete_elements']:.1f}")
        print(f"       - Filler phrases: {result['metrics']['p0_1_tasks']['avg_filler_ratio']:.1%}")

        print(f"  P0.2 Soft Skills: {result['metrics']['p0_2_soft_skills']['soft_skills_count']} найдено")
        print(f"       - С методиками: {result['metrics']['p0_2_soft_skills']['with_methodology']}")

        print(f"  P0.3 Regulatory: {result['metrics']['p0_3_regulatory']['domain']}")
        print(f"       - Найдено: {', '.join(result['metrics']['p0_3_regulatory']['found_frameworks'])}")

        print(f"  P0.4 Уровни: {result['metrics']['p0_4_levels']['unique_descriptions']}/{result['metrics']['p0_4_levels']['should_be_unique']} уникальных")

        if result['summary']['total_issues'] > 0:
            print(f"\n❌ ПРОБЛЕМЫ ({result['summary']['total_issues']}):")
            for issue in result['summary']['critical_issues'][:5]:
                print(f"   - {issue}")

        if result['summary']['total_warnings'] > 0:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({result['summary']['total_warnings']}):")
            for warning in result['summary']['warnings'][:3]:
                print(f"   - {warning}")

    # Сводная статистика
    print(f"\n\n{'='*60}")
    print(f"СВОДНАЯ СТАТИСТИКА")
    print(f"{'='*60}")

    avg_quality = sum(r['quality_score'] for r in results) / len(results)
    valid_count = sum(1 for r in results if r['valid'])

    print(f"\n📊 Средний Quality Score: {avg_quality:.2f}/10")
    print(f"✅ Валидных профилей: {valid_count}/{len(results)}")

    print(f"\n📋 По сферам:")
    for result in results:
        status = "✅" if result['valid'] else "❌"
        print(f"  {status} {result['position']}: {result['quality_score']:.2f}/10")

    # Сохранить результаты
    output_file = 'docs/testing/VALIDATION_RESULTS_P0.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Результаты сохранены: {output_file}")


if __name__ == "__main__":
    main()
```

**Критерий успеха**:
- ✅ Все профили провалидированы
- ✅ Метрики собраны
- ✅ Результаты сохранены

---

### Задача 4.2: Создать Финальный Отчет

**Агент**: data-scientist
**Время**: 15 минут

**Создать файл**: `docs/testing/P0_IMPLEMENTATION_REPORT.md`

С содержанием:
- Дата внедрения
- Внедренные правки (P0.1-P0.4)
- Результаты тестирования (4 профиля)
- Метрики качества (до/после)
- Выявленные проблемы
- Рекомендации

**Критерий успеха**:
- ✅ Отчет создан
- ✅ Включены все метрики
- ✅ Есть рекомендации

---

## ✅ Финальный Чек-лист

**ЭТАП 1: Подготовка**
- [ ] Backup промпта создан
- [ ] Окружение проверено
- [ ] Тестовые данные подготовлены

**ЭТАП 2: Внедрение (ПАРАЛЛЕЛЬНО)**
- [ ] P0.1 добавлено в промпт (Агент 1)
- [ ] P0.2 добавлено в промпт (Агент 1)
- [ ] P0.3 добавлено в промпт (Агент 1)
- [ ] P0.4 добавлено в промпт (Агент 1)
- [ ] Код валидации создан (Агент 2)
- [ ] Тесты созданы (Агент 3)

**ЭТАП 3: Тестирование (ПАРАЛЛЕЛЬНО)**
- [ ] Backend Python сгенерирован (Агент 1)
- [ ] Главбух сгенерирован (Агент 2)
- [ ] HRBP сгенерирован (Агент 3)
- [ ] Sales B2B сгенерирован (Агент 4)

**ЭТАП 4: Валидация**
- [ ] Профили провалидированы
- [ ] Отчет создан
- [ ] Результаты проанализированы

---

## 🎯 Критерии Успеха Всего Проекта

### Минимальные требования (MUST HAVE):

1. ✅ **Все 4 правки P0 внедрены** в промпт
2. ✅ **4 профиля сгенерированы** (IT, Finance, HR, Sales)
3. ✅ **Quality Score >= 9.0/10** для IT и Finance
4. ✅ **Quality Score >= 8.5/10** для HR и Sales
5. ✅ **Нет критичных ошибок** в валидации

### Желаемые результаты (NICE TO HAVE):

1. ⭐ **Средний Quality Score >= 9.0/10**
2. ⭐ **Все профили валидны** (valid = True)
3. ⭐ **Автоматические тесты проходят**
4. ⭐ **Отчет с рекомендациями**

---

**Общее время**: 3-4 часа
**Агентов задействовано**: 4 (параллельная работа)
**Ожидаемый результат**: Quality 9.2+/10, все профили production-ready

**Статус**: ✅ Готово к запуску

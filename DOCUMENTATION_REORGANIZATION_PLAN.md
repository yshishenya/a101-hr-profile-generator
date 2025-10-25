# План реорганизации документации

## Текущие проблемы

### Обнаруженные проблемы:
- **110 MD файлов** в проекте, из них **38 в корневой директории**
- Множество дублирующихся и устаревших отчетов
- Отсутствие четкой структуры и навигации
- Смешивание активной документации и архивных отчетов
- Дублирование файлов в разных директориях (корень, docs/, backend/)

### Категории документов для реорганизации:

#### 1. Анализы и отчеты (Archive)
```
ANALYSIS_INDEX.md
ANALYSIS_SUMMARY_FOR_CAPTAIN.md
ARCHITECTURE_INTEGRITY_REPORT.md
COMPREHENSIVE_SYSTEM_ANALYSIS.md
CONTEXT_FIXES_ROADMAP.md
CONTEXT_QUALITY_ANALYSIS.md
CRITICAL_FINDINGS_LANGFUSE_PROMPT.md
CRITICAL_FIXES_RECOMMENDATIONS.md
CUSTOMER_FEEDBACK_COMPREHENSIVE_ANALYSIS.md
DATA_FLOW_ANALYSIS_REPORT.md
ENDPOINT_FIXES_REPORT.md
END_TO_END_TEST_REPORT.md
FINAL_VERIFICATION_REPORT.md
KPI_CONVERSION_SUMMARY.md
KPI_FORMAT_ANALYSIS.md
LANGFUSE_PROMPT_ANALYSIS.md
performance_analysis_report.md
PHASE1_COMPLETE_REPORT.md
POSITION_VS_NAME_ANALYSIS.md
PROMPT_IMPROVEMENT_ANALYSIS.md
PROMPT_V27_COMPARISON.md
PROMPT_V28_SGR_IMPLEMENTATION.md
SECURITY_AUDIT_REPORT.md
```

#### 2. Планы реализации (Archive)
```
IMPLEMENTATION_PLAN_PART1.md
IMPLEMENTATION_PLAN_PART2_PHASE1.md
IMPLEMENTATION_PLAN_PART3_PHASE2.md
IMPLEMENTATION_PLAN_PART4_SUMMARY.md
```

#### 3. Спецификации (Specs)
```
KPI_FILTERING_IMPLEMENTATION_SPEC.md
```

#### 4. Deployment и DevOps
```
DOCKER_BIND_MOUNTS.md
DOCKER_DEPLOYMENT.md
docker-management.md
```

#### 5. Активная документация (Корень)
```
README.md
CHANGELOG.md
CLAUDE.md
QUICK_START_GUIDE.md
CODE_REVIEW_FIXES.md (временно, затем в архив)
PRODUCTION_READINESS_REPORT.md (временно, затем в архив)
```

#### 6. Данные и примеры (Data)
```
fixed_profile.md
```

## Новая структура документации

### Принципы организации:
1. **Diátaxis Framework**: Tutorials, How-To Guides, Explanation, Reference
2. **Single Source of Truth**: Один источник для каждого типа информации
3. **Lifecycle Management**: Разделение активных и архивных документов
4. **Clear Navigation**: Четкая навигация через README

### Предлагаемая структура:

```
/home/yan/A101/HR/
│
├── README.md                          # Главный вход в проект
├── CHANGELOG.md                       # История изменений
├── CONTRIBUTING.md                    # Гайд для контрибьюторов (создать)
├── CLAUDE.md                          # Claude Code конфигурация
│
├── .memory_bank/                      # Memory Bank (уже существует)
│   ├── README.md
│   ├── current_tasks.md
│   ├── tech_stack.md
│   └── ...
│
├── docs/
│   │
│   ├── README.md                      # Навигация по документации
│   │
│   ├── getting-started/               # 📚 Tutorials (Diátaxis)
│   │   ├── quick-start.md
│   │   ├── installation.md
│   │   └── first-profile.md
│   │
│   ├── guides/                        # 🔧 How-To Guides (Diátaxis)
│   │   ├── deployment/
│   │   │   ├── docker-deployment.md
│   │   │   ├── docker-bind-mounts.md
│   │   │   └── production-deployment.md
│   │   ├── development/
│   │   │   ├── local-setup.md
│   │   │   └── testing-guide.md
│   │   └── operations/
│   │       └── docker-management.md
│   │
│   ├── explanation/                   # 💡 Explanation (Diátaxis)
│   │   ├── architecture/
│   │   │   ├── system-architecture.md
│   │   │   ├── data-flow.md
│   │   │   └── llm-integration.md
│   │   └── concepts/
│   │       ├── profile-generation.md
│   │       └── kpi-mapping.md
│   │
│   ├── reference/                     # 📖 Reference (Diátaxis)
│   │   ├── api/
│   │   │   └── endpoints.md
│   │   ├── schemas/
│   │   │   └── profile-schema.md
│   │   └── configuration/
│   │       └── environment-variables.md
│   │
│   ├── specs/                         # 📋 Technical Specifications
│   │   ├── kpi-filtering-spec.md
│   │   └── future-features/
│   │
│   ├── data/                          # 🏢 Company Data
│   │   ├── org_structure/
│   │   ├── IT systems/
│   │   └── KPI/
│   │
│   └── archive/                       # 🗄️ Archived Reports & Analysis
│       ├── reports/
│       │   ├── 2025-Q1/
│       │   │   ├── phase1-complete-report.md
│       │   │   ├── security-audit-report.md
│       │   │   └── production-readiness-report.md
│       │   └── ...
│       ├── analysis/
│       │   ├── architecture/
│       │   ├── performance/
│       │   ├── prompts/
│       │   └── kpi/
│       └── implementation-plans/
│           └── 2025-Q1/
│
├── backend/
│   ├── README.md                      # Backend overview
│   └── docs/
│       ├── architecture.md
│       └── api-design.md
│
└── frontend/
    └── README.md                      # Frontend overview
```

## План действий

### Этап 1: Создание структуры директорий
1. Создать новые директории в docs/
2. Создать README.md файлы для навигации

### Этап 2: Перемещение файлов
1. Переместить отчеты в docs/archive/reports/
2. Переместить анализы в docs/archive/analysis/
3. Переместить deployment документы в docs/guides/deployment/
4. Переместить спецификации в docs/specs/
5. Переместить архитектурные документы в docs/explanation/architecture/

### Этап 3: Создание активной документации
1. Обновить главный README.md
2. Создать docs/README.md с навигацией
3. Создать CONTRIBUTING.md
4. Создать отдельные getting-started гайды
5. Создать reference документацию из существующих источников

### Этап 4: Очистка
1. Удалить дублирующиеся файлы
2. Обновить .gitignore
3. Создать архив старых backup файлов

### Этап 5: Обновление ссылок
1. Обновить все внутренние ссылки в документации
2. Обновить ссылки в коде (если есть)

## Приоритеты

### Высокий приоритет (сделать сейчас):
- ✅ Создать структуру директорий
- ✅ Переместить архивные отчеты
- ✅ Обновить главный README.md
- ✅ Создать docs/README.md

### Средний приоритет:
- Создать getting-started гайды
- Создать deployment гайды
- Создать CONTRIBUTING.md

### Низкий приоритет:
- Детальная reference документация
- Перевод всех документов на английский (опционально)

## Ожидаемые результаты

1. **Чистый корень проекта**: Только 5-7 ключевых файлов
2. **Структурированная документация**: Четкая организация по типам
3. **Легкая навигация**: README файлы с ссылками
4. **Разделение**: Активная документация vs архивные отчеты
5. **Соответствие стандартам**: Diátaxis framework, Documentation as Code

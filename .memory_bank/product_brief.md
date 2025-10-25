# Product Brief

## Project Name
A101 HR Profile Generator

## Project Goal (WHY)
Автоматизация создания детальных профилей должностей для компании А101 с использованием AI, чтобы:
- Сократить время создания профиля должности с нескольких часов до нескольких минут
- Обеспечить консистентность и полноту всех профилей
- Использовать данные организационной структуры и KPI компании
- Предоставить HR-специалистам современный инструмент для работы

## Target Audience (FOR WHOM)

### Основные пользователи:
- **HR-специалисты компании А101** - создание и управление профилями должностей
- **HR-менеджеры** - анализ и утверждение профилей
- **Руководители департаментов** - валидация требований к должностям

### Вторичные пользователи:
- **IT-администраторы** - развертывание и поддержка системы
- **Разработчики** - доработка и расширение функционала

### Стейкхолдеры:
- **Директор по персоналу** - стратегическое использование системы
- **Руководство компании** - оптимизация HR-процессов

## Key Features

### 1. 🤖 AI-Powered Generation
Автоматическая генерация полных профилей должностей с использованием Google Gemini 2.5 Flash:
- Детальное описание обязанностей
- Требования к образованию и опыту
- Необходимые компетенции и навыки
- Ключевые показатели эффективности (KPI)

### 2. 📊 Deterministic Data Mapping
100% точное соответствие данных компании без использования LLM:
- Автоматический маппинг департаментов из оргструктуры
- Точное назначение KPI по департаментам
- Загрузка актуальной структуры компании
- Кеширование для высокой производительности (75x ускорение)

### 3. 🔗 Langfuse Observability
Полный контроль и мониторинг всех AI-генераций:
- Централизованное управление промптами
- Версионирование промптов
- Детальный трейсинг каждой генерации
- Метрики производительности и качества
- Анализ использования LLM

### 4. 📄 Multiple Export Formats
Экспорт профилей в различных форматах:
- **JSON** - для интеграции с другими системами
- **Markdown** - для документации и веб-отображения
- **DOCX** - для печати и официальных документов
- **XLSX** - для табличного представления и анализа

### 5. ⚡ High Performance
Оптимизированная архитектура:
- Параллельная генерация профилей (10x ускорение)
- Кеширование организационного каталога (3ms vs 225ms)
- Асинхронная обработка всех I/O операций
- Structured Output с JSON Schema валидацией

## Business Success Metrics

### Productivity Metrics
- **Time Savings**: Сокращение времени создания профиля с 2-4 часов до 5-10 минут (90%+ экономия)
- **Throughput**: Возможность генерации 50+ профилей в день (vs 2-3 вручную)
- **Target**: 100% департаментов покрыты профилями должностей к концу квартала

### Quality Metrics
- **Consistency**: 100% профилей соответствуют единому шаблону
- **Completeness**: Все обязательные секции заполнены в 100% профилей
- **Accuracy**: KPI маппинг точность 100% (детерминированный подход)
- **User Satisfaction**: Целевой NPS > 8/10 от HR-специалистов

### Technical Metrics
- **Performance**: Генерация профиля < 30 секунд
- **Availability**: Uptime > 99.5%
- **Observability**: 100% генераций трейсятся в Langfuse
- **Cost Efficiency**: < $0.50 на генерацию профиля

## Competitive Advantages

### 🎯 Unique Value Proposition
- **Первая в своем роде система** для компании А101, заточенная под специфику организации
- **Гибридный подход**: детерминированный маппинг данных + творческая AI-генерация
- **Полная интеграция** с реальными данными компании (оргструктура, KPI)

### 💻 Technical Advantages
- **Современный стек**: FastAPI, NiceGUI, Gemini 2.5 Flash
- **Full Observability**: Langfuse для мониторинга и улучшения промптов
- **Type Safety**: 100% Python type hints, mypy проверки
- **Async-First**: Высокая производительность через async/await

### 🎨 User Experience Benefits
- **Простой интерфейс**: Интуитивная форма генерации
- **Быстрая генерация**: Результат за секунды, не часы
- **Множественные форматы**: Экспорт в нужный формат одним кликом
- **Прозрачность**: Видимость всех использованных данных

### 💰 Cost/Efficiency Improvements
- **ROI**: Окупаемость за 1-2 месяца при активном использовании
- **Масштабируемость**: Легко покрыть всю компанию
- **Maintenance**: Минимальные затраты на поддержку (SQLite, simple deployment)

### 🚀 Innovation Aspects
- **AI-First подход** к HR-процессам
- **Версионирование промптов** через Langfuse
- **Детерминированность** где это критично
- **Open for extension**: Легко добавлять новые источники данных

## User Stories

### For HR Specialists
**As an HR specialist**, I want to generate a complete job profile in minutes so that I can focus on strategic HR tasks instead of manual documentation.

**As an HR specialist**, I want to export profiles in different formats so that I can use them in presentations, official documents, and system integrations.

**As an HR specialist**, I want consistent profile structure so that all positions follow the same standards across the company.

### For HR Managers
**As an HR manager**, I want to quickly review and approve generated profiles so that we can maintain high quality while moving fast.

**As an HR manager**, I want to see which KPIs are assigned to positions so that I can ensure alignment with department goals.

### For Department Heads
**As a department head**, I want accurate representation of my department's positions so that job descriptions match actual responsibilities.

**As a department head**, I want to validate technical requirements so that we hire candidates with right skills.

### For IT Administrators
**As an IT administrator**, I want simple Docker deployment so that I can quickly set up the system without complex configuration.

**As an IT administrator**, I want comprehensive logging and monitoring so that I can troubleshoot issues efficiently.

## Technical Constraints

### Performance Requirements
- Profile generation: < 30 seconds per profile
- Catalog loading: < 5ms (with cache)
- API response time: < 1 second (95th percentile)

### Scalability Needs
- Support 100+ concurrent users
- Handle 1000+ profiles in database
- Process 50+ parallel generations

### Security Requirements
- JWT-based authentication
- Secure storage of API keys in environment variables
- No sensitive data in logs
- HTTPS for all external API calls

### Compliance Requirements
- GDPR compliance for employee data
- Secure handling of company confidential information
- Audit trail for all profile generations

### Platform Support
- Web UI accessible from modern browsers (Chrome, Firefox, Safari)
- Backend runs on Linux/Docker
- Python 3.11+ required

## Future Vision

### Phase 1: Core Functionality ✅ (Completed)
- AI-powered profile generation
- Deterministic data mapping
- Multiple export formats
- NiceGUI web interface
- Full Langfuse integration

### Phase 2: Enhanced Features (Q2 2025)
- Profile comparison and diff tool
- Profile versioning and history
- Advanced search and filtering
- Bulk generation capabilities
- Template customization

### Phase 3: Advanced Capabilities (Q3 2025)
- Integration with HR management systems
- Automated profile updates based on org changes
- Analytics and insights dashboard
- Role-based access control
- Multi-language support

### Long-term Vision
- **AI Assistant**: Conversational interface for profile creation
- **Recommendations**: Suggest improvements based on market data
- **Skills Taxonomy**: Integration with skills databases
- **Career Paths**: Generate career progression paths
- **Market Intelligence**: Salary and skills insights

---

**Last Updated:** 2025-10-25
**Status:** Active Development
**Phase:** Phase 1 Complete, Phase 2 Planning

**Note**: This is a living document. Update it as the project evolves and requirements change.

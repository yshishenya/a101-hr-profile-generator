# Frontend Documentation Index

Быстрый доступ ко всей документации фронтенда.

---

## 🎯 Обязательное чтение (в указанном порядке)

### Для AI Agent (Claude):

1. **[CLAUDE.md](../CLAUDE.md)** - Инструкции для AI agent
   - Секция "Vue 3 Frontend Architecture"
   - Mandatory reading sequence
   - Forbidden actions

### Для разработчиков:

1. **[Memory Bank README](./README.md)** - Главная страница
   - Mandatory Reading Sequence
   - Knowledge System Map

2. **[Frontend Coding Standards](./guides/frontend_coding_standards.md)** ⚠️ ОБЯЗАТЕЛЬНО!
   - TypeScript strict mode rules
   - Vue 3 Composition API standards
   - Error handling patterns
   - Component architecture (size limits)
   - Testing requirements (80%+)
   - Code review checklist

3. **[Frontend Architecture](./architecture/frontend_architecture.md)**
   - Technology stack
   - Layered architecture
   - Data flow patterns
   - State management (Pinia)
   - Testing strategy

4. **[Component Library](./architecture/component_library.md)** ⚠️ КРИТИЧНО!
   - **ПРОВЕРЯЙ ПЕРЕД СОЗДАНИЕМ ЛЮБОГО КОМПОНЕНТА!**
   - 12 переиспользуемых компонентов
   - Props/Events documentation
   - "Rule of Three"
   - Creation checklist

---

## 📚 Полная документация

### Architecture (Архитектура)

| Документ | Размер | Описание |
|----------|--------|----------|
| [Frontend Architecture](./architecture/frontend_architecture.md) | 900+ строк | Полное описание архитектуры Vue 3 SPA |
| [Component Library](./architecture/component_library.md) | 700+ строк | Каталог переиспользуемых компонентов |

### Guides (Руководства)

| Документ | Размер | Описание |
|----------|--------|----------|
| [Frontend Coding Standards](./guides/frontend_coding_standards.md) | 500+ строк | Стандарты кода для Vue 3 + TypeScript |
| [Coding Standards](./guides/coding_standards.md) | - | Backend стандарты (Python/FastAPI) |
| [Testing Strategy](./guides/testing_strategy.md) | - | Общая стратегия тестирования |

### Patterns (Паттерны)

| Документ | Описание |
|----------|----------|
| [API Standards](./patterns/api_standards.md) | Стандарты дизайна API |
| [Error Handling](./patterns/error_handling.md) | Паттерны обработки ошибок |

### Root Documents

| Документ | Размер | Описание |
|----------|--------|----------|
| [FRONTEND_DOCUMENTATION_SUMMARY.md](../FRONTEND_DOCUMENTATION_SUMMARY.md) | - | Полный summary всей документации |
| [WEEK_5_SUMMARY.md](../WEEK_5_SUMMARY.md) | - | Краткое резюме Week 5 работы |

---

## 🗺️ Навигация по темам

### Создание компонентов

1. **Перед созданием** → [Component Library](./architecture/component_library.md) (секция "Когда создавать")
2. **Структура** → [Frontend Coding Standards](./guides/frontend_coding_standards.md) (секция "Component Architecture")
3. **Props/Events** → [Frontend Coding Standards](./guides/frontend_coding_standards.md) (секция "Vue 3 Composition API")

### State Management

1. **Store структура** → [Frontend Coding Standards](./guides/frontend_coding_standards.md) (секция "State Management")
2. **Store patterns** → [Frontend Architecture](./architecture/frontend_architecture.md) (секция "State Management")
3. **Store modularization** → [Frontend Architecture](./architecture/frontend_architecture.md) (секция "Store Модуляризация")

### Testing

1. **Test requirements** → [Frontend Coding Standards](./guides/frontend_coding_standards.md) (секция "Testing")
2. **Test strategy** → [Frontend Architecture](./architecture/frontend_architecture.md) (секция "Testing Strategy")
3. **Test examples** → См. `src/utils/__tests__/`, `src/stores/__tests__/`

### Error Handling

1. **Patterns** → [Frontend Coding Standards](./guides/frontend_coding_standards.md) (секция "Error Handling")
2. **Helper functions** → `src/utils/errors.ts`
3. **Examples** → См. все store файлы

### TypeScript

1. **Strict mode rules** → [Frontend Coding Standards](./guides/frontend_coding_standards.md) (секция "TypeScript Type Safety")
2. **Type system** → [Frontend Architecture](./architecture/frontend_architecture.md) (секция "Type System")
3. **Type definitions** → `src/types/`

---

## 🚀 Quick Start

### Новый разработчик:

```bash
# 1. Прочитай основы
cat .memory_bank/README.md
cat CLAUDE.md  # секция Vue 3

# 2. Изучи стандарты
cat .memory_bank/guides/frontend_coding_standards.md

# 3. Изучи архитектуру
cat .memory_bank/architecture/frontend_architecture.md

# 4. КРИТИЧНО - изучи компоненты
cat .memory_bank/architecture/component_library.md
```

### Перед созданием компонента:

```bash
# Проверь Component Library
cat .memory_bank/architecture/component_library.md | grep -i "componentName"

# Проверь существующие
ls src/components/common/
ls src/components/generator/
ls src/components/profiles/
```

### Перед commit:

```bash
cd frontend-vue
npm run format
npm run lint
npm run type-check
npm test -- --run
npm run build
```

---

## 📊 Статистика документации

| Категория | Файлов | Строк кода | Статус |
|-----------|--------|------------|--------|
| Architecture | 2 | 1600+ | ✅ Complete |
| Guides | 3 | 500+ | ✅ Complete |
| Patterns | 2 | - | ✅ Complete |
| Root Summaries | 2 | - | ✅ Complete |
| **Итого** | **9** | **2100+** | **✅ Production Ready** |

---

## 🔗 Внешние ссылки

### Официальная документация:

- [Vue 3 Docs](https://vuejs.org/guide/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [Pinia Docs](https://pinia.vuejs.org/)
- [Vuetify 3 Docs](https://vuetifyjs.com/)
- [Vitest Docs](https://vitest.dev/)
- [Vite Docs](https://vitejs.dev/)

### Best Practices:

- [Vue 3 Style Guide](https://vuejs.org/style-guide/)
- [TypeScript Do's and Don'ts](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [Testing Library Best Practices](https://testing-library.com/docs/queries/about)

---

## 🎯 Цели документации

✅ **Предотвращение дублирования компонентов**  
✅ **Единые стандарты качества кода**  
✅ **Быстрый onboarding новых разработчиков**  
✅ **Консистентность архитектуры**  
✅ **Production-ready код**

---

**Последнее обновление**: 2025-10-26  
**Версия**: 1.0  
**Статус**: ✅ Complete

---

**Вопросы?** Проверьте [Component Library](./architecture/component_library.md) или [Frontend Coding Standards](./guides/frontend_coding_standards.md)

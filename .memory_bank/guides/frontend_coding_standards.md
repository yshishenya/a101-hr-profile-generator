# Frontend Coding Standards

## Обязательно к прочтению перед любой работой с фронтендом!

Этот документ определяет стандарты качества кода для Vue 3 + TypeScript фронтенда проекта HR Profile Generator.

**КРИТИЧНО**: Несоблюдение этих стандартов приведёт к отклонению кода на code review.

---

## 1. TypeScript Type Safety

### 1.1 Strict Mode (ОБЯЗАТЕЛЬНО)

**Статус**: ✅ ВКЛЮЧЁН в `tsconfig.app.json`

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

**Правила**:
- ❌ **ЗАПРЕЩЕНО** использовать `any` типы
- ✅ Используйте `unknown` с type guards
- ✅ Используйте явные типы для всех параметров и возвращаемых значений
- ✅ Используйте утилиты из `src/utils/errors.ts` для обработки ошибок

**Примеры**:

```typescript
// ❌ НЕПРАВИЛЬНО
catch (error: any) {
  const message = error.response?.data?.detail
}

// ✅ ПРАВИЛЬНО
import { getErrorMessage } from '@/utils/errors'

catch (error: unknown) {
  const message = getErrorMessage(error, 'Default message')
}
```

### 1.2 Типизация Props и Emits

**Все компоненты должны иметь явные типы**:

```typescript
// ✅ ПРАВИЛЬНО
interface Props {
  items: SearchableItem[]
  loading?: boolean
  maxResults?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  maxResults: 50
})

const emit = defineEmits<{
  'update:modelValue': [value: SearchableItem[]]
  'select': [item: SearchableItem]
}>()
```

### 1.3 Типы vs Interfaces

**Используйте**:
- `interface` для публичных API и props компонентов
- `type` для unions, intersections и сложных типов

```typescript
// Публичный API - interface
export interface SearchableItem {
  position_id: string
  position_name: string
}

// Сложные типы - type
export type ProfileValue =
  | string
  | number
  | ProfileValue[]
  | { [key: string]: ProfileValue }
```

---

## 2. Vue 3 Composition API

### 2.1 Script Setup (ОБЯЗАТЕЛЬНО)

**Все компоненты используют `<script setup>`**:

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

// Constants первыми
const MAX_ITEMS = 100

// Props и Emits
interface Props {
  items: Item[]
}
const props = defineProps<Props>()
const emit = defineEmits<{ select: [Item] }>()

// State
const selected = ref<Item | null>(null)

// Computed
const hasSelection = computed(() => selected.value !== null)

// Functions
function handleSelect(item: Item): void {
  selected.value = item
  emit('select', item)
}
</script>
```

### 2.2 Порядок элементов в компоненте

**Строго соблюдать порядок**:

1. Imports
2. Constants (UPPER_SNAKE_CASE)
3. Interfaces/Types
4. Props (с defineProps)
5. Emits (с defineEmits)
6. Stores (useSomeStore())
7. State (ref, reactive)
8. Computed properties
9. Lifecycle hooks (onMounted, onBeforeUnmount)
10. Functions (в порядке использования)
11. Watchers (последними)

### 2.3 Reactivity

```typescript
// ✅ ПРАВИЛЬНО - используйте ref для примитивов
const count = ref(0)
const user = ref<User | null>(null)

// ✅ ПРАВИЛЬНО - используйте reactive для объектов
const state = reactive({
  loading: false,
  error: null as string | null
})

// ❌ НЕПРАВИЛЬНО - не используйте reactive для примитивов
const count = reactive({ value: 0 })
```

---

## 3. Naming Conventions

### 3.1 Files and Components

```
✅ PascalCase для компонентов:
- BaseCard.vue
- ProfileContent.vue
- OrganizationTree.vue

✅ kebab-case для других файлов:
- formatters.ts
- error-handler.ts

✅ camelCase для composables:
- useTaskStatus.ts
- useDebounce.ts
```

### 3.2 Variables and Functions

```typescript
// ✅ camelCase для переменных и функций
const selectedItems = ref<Item[]>([])
function handleSelection(): void {}

// ✅ UPPER_SNAKE_CASE для констант
const MAX_RETRY_COUNT = 3
const API_TIMEOUT_MS = 5000

// ✅ PascalCase для типов и интерфейсов
interface UserProfile {}
type ProfileData = {}

// ✅ I-префикс ТОЛЬКО для интерфейсов из внешних библиотек
// В нашем коде НЕ используем I-префикс
```

### 3.3 Boolean Variables

```typescript
// ✅ ПРАВИЛЬНО - используйте префиксы is/has/can/should
const isLoading = ref(false)
const hasError = computed(() => error.value !== null)
const canSubmit = computed(() => isValid.value && !isLoading.value)

// ❌ НЕПРАВИЛЬНО
const loading = ref(false)
const error = computed(() => ...)
```

---

## 4. Error Handling

### 4.1 Try-Catch Blocks

**Всегда указывайте тип `unknown`**:

```typescript
// ✅ ПРАВИЛЬНО
try {
  await api.post('/endpoint', data)
} catch (error: unknown) {
  logger.error('Failed to save data', error)

  const message = error instanceof Error
    ? error.message
    : 'Unknown error'

  showNotification(message, 'error')
}
```

### 4.2 Axios Errors

**Используйте helper функцию**:

```typescript
import { getErrorMessage } from '@/utils/errors'

try {
  await api.get('/data')
} catch (error: unknown) {
  const message = getErrorMessage(error, 'Failed to load data')
  logger.error('API error', error)
  throw new CustomError(message, 'API_ERROR', error)
}
```

### 4.3 Custom Error Classes

```typescript
// Используйте существующие классы
import { ProfileError } from '@/stores/profiles'
import { CatalogError } from '@/stores/catalog'

// Или создайте новый по паттерну
export class CustomError extends Error {
  constructor(
    message: string,
    public code: string,
    public cause?: unknown
  ) {
    super(message)
    this.name = 'CustomError'
  }
}
```

---

## 5. Component Architecture

### 5.1 Component Size Limits

**Строгие лимиты**:
- ✅ Максимум **300 строк** на компонент
- ✅ Максимум **500 строк** на store/service файл
- ❌ Если превышено → ОБЯЗАТЕЛЬНО разбить на модули

**Пример модуляризации** (см. [stores/profiles/](../../frontend-vue/src/stores/profiles/)):
```
profiles/
├── types.ts       (30 lines)  - Типы и константы
├── state.ts       (72 lines)  - Reactive state
├── getters.ts     (108 lines) - Computed properties
├── actions-crud.ts (290 lines) - CRUD операции
└── index.ts       (158 lines) - Композиция
```

### 5.2 Переиспользование компонентов

**КРИТИЧНО**: Перед созданием нового компонента:

1. ✅ Проверьте [Component Library](../architecture/component_library.md)
2. ✅ Проверьте существующие компоненты в `src/components/common/`
3. ✅ Спросите себя: "Существует ли уже похожий компонент?"

**Существующие переиспользуемые компоненты**:

| Компонент | Назначение | Использование |
|-----------|------------|---------------|
| `BaseCard.vue` | Карточки с заголовком/действиями | Все карточки контента |
| `OrganizationTree.vue` | Дерево организации | Везде где нужно дерево |
| `PositionSearchAutocomplete.vue` | Поиск позиций | Все формы с выбором позиций |

### 5.3 Props Design

```typescript
// ✅ ПРАВИЛЬНО - специфичные типы
interface Props {
  items: SearchableItem[]      // ✅ явный тип
  loading?: boolean             // ✅ optional с default
  maxResults?: number           // ✅ optional с default
}

// ❌ НЕПРАВИЛЬНО
interface Props {
  items: any[]                  // ❌ any запрещён
  loading: boolean              // ❌ required без причины
  max: number                   // ❌ неясное название
}
```

---

## 6. State Management (Pinia)

### 6.1 Store Structure

**Обязательная структура Composition API**:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMyStore = defineStore('myStore', () => {
  // 1. State
  const items = ref<Item[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 2. Getters
  const itemCount = computed(() => items.value.length)
  const hasError = computed(() => error.value !== null)

  // 3. Actions
  async function loadItems(): Promise<void> {
    loading.value = true
    try {
      items.value = await api.get('/items')
    } catch (err: unknown) {
      error.value = getErrorMessage(err)
      throw new StoreError(error.value, 'LOAD_ERROR', err)
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    items,
    loading,
    error,
    // Getters
    itemCount,
    hasError,
    // Actions
    loadItems
  }
})
```

### 6.2 Store Модуляризация

**Когда модуляризовать**: Файл > 500 строк

**Паттерн**:
```
store-name/
├── types.ts       - Типы, error классы, константы
├── state.ts       - Вся reactive state
├── getters.ts     - Computed properties
├── actions-*.ts   - Группы actions (CRUD, filters, etc.)
└── index.ts       - Главный файл, композиция
```

### 6.3 Именование Actions

```typescript
// ✅ ПРАВИЛЬНО - глагол + существительное
async function loadItems(): Promise<void>
async function createProfile(data: ProfileData): Promise<void>
async function updateProfile(id: string, data: Partial<ProfileData>): Promise<void>
async function deleteProfile(id: string): Promise<void>

// ❌ НЕПРАВИЛЬНО
async function items(): Promise<void>       // не глагол
async function profile(data: any): Promise<void>  // неясно что делает
```

---

## 7. Testing

### 7.1 Test Coverage Requirements

**Обязательные метрики**:
- ✅ Минимум **80%** coverage для utils
- ✅ Минимум **80%** coverage для stores
- ✅ Минимум **60%** coverage для components

**Запуск**:
```bash
npm test              # Запуск всех тестов
npm run test:coverage # С отчётом coverage
```

### 7.2 Test Structure

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

describe('featureName', () => {
  beforeEach(() => {
    // Setup для каждого теста
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('subfeature', () => {
    it('should do expected behavior', async () => {
      // Arrange
      const input = 'test'

      // Act
      const result = await someFunction(input)

      // Assert
      expect(result).toBe('expected')
    })
  })
})
```

### 7.3 Test File Naming

```
✅ Рядом с исходным файлом в __tests__/:
src/utils/formatters.ts
src/utils/__tests__/formatters.test.ts

src/stores/catalog.ts
src/stores/__tests__/catalog.test.ts

✅ Для компонентов в tests/components/:
src/components/OrganizationTree.vue
tests/components/OrganizationTree.spec.ts
```

---

## 8. Code Style

### 8.1 ESLint & Prettier

**Конфигурация**: См. [.eslintrc.cjs](../../frontend-vue/.eslintrc.cjs), [.prettierrc.json](../../frontend-vue/.prettierrc.json)

**Автоматическое форматирование**:
```bash
npm run lint          # Проверка + автофикс
npm run format        # Prettier форматирование
```

**Основные правила**:
- Без точек с запятой (semi: false)
- Одинарные кавычки (singleQuote: true)
- 100 символов на строку (printWidth: 100)
- 2 пробела для отступов (tabWidth: 2)

### 8.2 Imports Organization

```typescript
// 1. External libraries
import { ref, computed } from 'vue'
import { useDebounceFn } from '@vueuse/core'

// 2. Stores
import { useCatalogStore } from '@/stores/catalog'

// 3. Services
import api from '@/services/api'

// 4. Utils
import { logger } from '@/utils/logger'
import { getErrorMessage } from '@/utils/errors'

// 5. Types
import type { SearchableItem } from '@/stores/catalog'
import type { ProfileData } from '@/types/profile'

// 6. Components (если нужны)
import BaseCard from '@/components/common/BaseCard.vue'
```

### 8.3 Comments and Documentation

**JSDoc для всех публичных функций**:

```typescript
/**
 * Загружает список позиций из API
 *
 * @throws {CatalogError} Если API недоступен
 * @returns Promise, который резолвится после загрузки
 *
 * @example
 * ```typescript
 * await store.loadSearchableItems()
 * console.log(store.searchableItems) // Массив позиций
 * ```
 */
async function loadSearchableItems(): Promise<void> {
  // Implementation
}
```

**Комментарии для сложной логики**:

```typescript
// BUGFIX-10: Проверка на изменение предотвращает бесконечный reactive loop
// modelValue change → selected change → emit update:modelValue → modelValue change...
const hasChanged = newIds.length !== selected.value.length ||
                   newIds.some(id => !selected.value.includes(id))
```

---

## 9. Performance

### 9.1 Computed vs Methods

```typescript
// ✅ ПРАВИЛЬНО - используйте computed для reactive данных
const filteredItems = computed(() => {
  return items.value.filter(item => item.active)
})

// ❌ НЕПРАВИЛЬНО - не используйте methods для reactive вычислений
function getFilteredItems() {
  return items.value.filter(item => item.active)
}
```

### 9.2 Watchers

```typescript
// ✅ ПРАВИЛЬНО - immediate: false по умолчанию
watch(source, (newValue, oldValue) => {
  // Выполнится только при изменении
})

// ✅ ПРАВИЛЬНО - используйте deep только когда нужно
watch(() => props.items, (newValue) => {
  // Для arrays/objects
}, { deep: true })

// ❌ НЕПРАВИЛЬНО - не злоупотребляйте immediate
watch(source, () => {
  // Будет вызвано сразу при mount
}, { immediate: true })
```

### 9.3 V-For Keys

```vue
<!-- ✅ ПРАВИЛЬНО - уникальный stable key -->
<div v-for="item in items" :key="item.id">
  {{ item.name }}
</div>

<!-- ❌ НЕПРАВИЛЬНО - index как key -->
<div v-for="(item, index) in items" :key="index">
  {{ item.name }}
</div>
```

---

## 10. Security

### 10.1 XSS Prevention

```vue
<!-- ✅ ПРАВИЛЬНО - используйте mustache syntax -->
<div>{{ userInput }}</div>

<!-- ⚠️ ИСПОЛЬЗУЙТЕ С ОСТОРОЖНОСТЬЮ - v-html только для доверенного контента -->
<div v-html="trustedHtmlContent"></div>
<!-- Требует комментария: <!-- eslint-disable-line vue/no-v-html --> -->
```

### 10.2 Sensitive Data

```typescript
// ❌ НИКОГДА не храните в коде
const API_KEY = 'secret-key-123'

// ✅ ПРАВИЛЬНО - используйте environment variables
const API_KEY = import.meta.env.VITE_API_KEY
```

---

## 11. Checklist перед Commit

**Обязательно выполнить**:

```bash
# 1. Форматирование
npm run format

# 2. Линтинг
npm run lint

# 3. Type check
npm run type-check

# 4. Тесты
npm test -- --run

# 5. Build
npm run build
```

**Все команды должны завершиться успешно!**

---

## 12. Code Review Критерии

### Код будет отклонён если:

- ❌ Используются `any` типы
- ❌ TypeScript strict mode errors
- ❌ ESLint errors (warnings допустимы)
- ❌ Тесты не проходят
- ❌ Coverage падает ниже 80% для utils/stores
- ❌ Файл > 300 строк (компонент) или > 500 строк (store)
- ❌ Создан дублирующий компонент вместо переиспользования
- ❌ Нет JSDoc для публичных функций
- ❌ Catch blocks без типа `unknown`
- ❌ Build fails

### Код будет одобрен если:

- ✅ Все чеклисты пройдены
- ✅ Следует архитектуре из [Frontend Architecture](../architecture/frontend_architecture.md)
- ✅ Переиспользует компоненты из [Component Library](../architecture/component_library.md)
- ✅ Имеет тесты с coverage > 80%
- ✅ Документирован JSDoc комментариями
- ✅ Следует всем правилам из этого документа

---

## 📚 Связанные документы

- [Frontend Architecture](../architecture/frontend_architecture.md) - Архитектура приложения
- [Component Library](../architecture/component_library.md) - Переиспользуемые компоненты
- [Testing Strategy](./testing_strategy.md) - Стратегия тестирования
- [Tech Stack](../tech_stack.md) - Используемые технологии

---

**Последнее обновление**: 2025-10-26
**Версия**: 1.0
**Статус**: ✅ Production Ready

# Frontend Architecture

## Обзор архитектуры Vue 3 SPA

Это **полное** руководство по архитектуре фронтенда HR Profile Generator.

**КРИТИЧНО**: Читайте этот документ перед началом любой работы с фронтендом!

---

## 1. Технологический стек

### Основные технологии

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Vue 3** | 3.x | Progressive framework |
| **TypeScript** | 5.x | Type safety (strict mode) |
| **Vite** | 7.x | Build tool & dev server |
| **Pinia** | 2.x | State management |
| **Vue Router** | 4.x | Routing |
| **Vuetify** | 3.x | UI component library |

### Dev Tools

| Инструмент | Назначение |
|------------|------------|
| **Vitest** | Unit testing |
| **@testing-library/vue** | Component testing |
| **ESLint** | Code linting |
| **Prettier** | Code formatting |
| **TypeScript** | Type checking |

### Ключевые библиотеки

```json
{
  "axios": "HTTP client",
  "fuse.js": "Fuzzy search",
  "@vueuse/core": "Vue composition utilities",
  "pinia-plugin-persistedstate": "State persistence"
}
```

---

## 2. Структура проекта

```
frontend-vue/
├── public/              # Статические файлы
├── src/
│   ├── assets/         # Изображения, стили
│   ├── components/     # Vue компоненты
│   │   ├── common/     # 🔄 Переиспользуемые компоненты (BaseCard, etc.)
│   │   ├── generator/  # Компоненты генератора профилей
│   │   ├── layout/     # Layout компоненты (Header, Layout)
│   │   └── profiles/   # Компоненты управления профилями
│   ├── composables/    # Composition функции (useTaskStatus)
│   ├── router/         # Vue Router конфигурация
│   ├── services/       # 🔌 API services
│   │   ├── api.ts      # Axios instance
│   │   ├── auth.service.ts
│   │   ├── catalog.service.ts
│   │   ├── dashboard.service.ts
│   │   ├── generation.service.ts
│   │   └── profile.service.ts
│   ├── stores/         # 🗃️ Pinia stores
│   │   ├── auth.ts
│   │   ├── catalog.ts
│   │   ├── generator.ts
│   │   └── profiles/   # Модулярный store
│   │       ├── types.ts
│   │       ├── state.ts
│   │       ├── getters.ts
│   │       ├── actions-crud.ts
│   │       ├── actions-filters.ts
│   │       ├── actions-unified.ts
│   │       └── index.ts
│   ├── types/          # 📝 TypeScript type definitions
│   │   ├── api.ts      # API response types
│   │   ├── profile.ts  # Profile data types
│   │   ├── generation.ts # Generation types
│   │   └── unified.ts  # Unified view types
│   ├── utils/          # 🛠️ Utility functions
│   │   ├── formatters.ts  # Date, number formatters
│   │   ├── logger.ts      # Logging utility
│   │   └── errors.ts      # Error handling utilities
│   ├── views/          # 📄 Page components
│   │   ├── DashboardView.vue
│   │   ├── GeneratorView.vue
│   │   ├── LoginView.vue
│   │   └── UnifiedProfilesView.vue
│   ├── App.vue         # Root component
│   └── main.ts         # Application entry point
├── tests/              # Unit & integration tests
│   └── components/     # Component tests
├── .eslintrc.cjs       # ESLint config
├── .prettierrc.json    # Prettier config
├── tsconfig.app.json   # TypeScript config (strict mode)
├── vite.config.ts      # Vite config
└── vitest.config.ts    # Vitest config
```

---

## 3. Архитектурные слои

### 3.1 Layered Architecture

```
┌─────────────────────────────────────┐
│         Views (Pages)               │  Роуты, композиция компонентов
├─────────────────────────────────────┤
│         Components                  │  Переиспользуемая UI логика
├─────────────────────────────────────┤
│      Stores (Pinia)                 │  State management, бизнес-логика
├─────────────────────────────────────┤
│         Services                    │  API взаимодействие
├─────────────────────────────────────┤
│      Utils & Helpers                │  Чистые функции, утилиты
└─────────────────────────────────────┘
```

**Правила взаимодействия слоёв**:

- ✅ Views → Components → Stores → Services → Utils
- ❌ НИКОГДА не вызывайте Services напрямую из Components
- ❌ НИКОГДА не импортируйте Stores в Services
- ✅ Stores — единственный слой для работы с API

### 3.2 Data Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│   View   │ ──────→ │  Store   │ ──────→ │ Service  │
│          │         │          │         │          │
│  UI      │ ←────── │  State   │ ←────── │ API call │
└──────────┘         └──────────┘         └──────────┘
     ↑                    ↑
     │                    │
     └─── Component ──────┘
```

**Поток данных**:
1. User action в View/Component
2. Call store action
3. Store вызывает Service
4. Service делает HTTP request
5. Response → Store updates state
6. Reactive update → Component re-renders

---

## 4. State Management (Pinia)

### 4.1 Store Design Patterns

**Composition API Style (ОБЯЗАТЕЛЬНО)**:

```typescript
// src/stores/example.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Item } from '@/types/item'

export const useExampleStore = defineStore('example', () => {
  // ═══ STATE ═══
  const items = ref<Item[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ═══ GETTERS ═══
  const itemCount = computed(() => items.value.length)
  const hasError = computed(() => error.value !== null)

  // ═══ ACTIONS ═══
  async function loadItems(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/items')
      items.value = response.data
    } catch (err: unknown) {
      error.value = getErrorMessage(err, 'Failed to load items')
      logger.error('Failed to load items', err)
      throw new ExampleError(error.value, 'LOAD_ERROR', err)
    } finally {
      loading.value = false
    }
  }

  function resetState(): void {
    items.value = []
    loading.value = false
    error.value = null
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
    loadItems,
    resetState
  }
})
```

### 4.2 Существующие Stores

| Store | Файл | Назначение |
|-------|------|------------|
| **Auth** | [auth.ts](../../frontend-vue/src/stores/auth.ts) | Аутентификация, user session |
| **Catalog** | [catalog.ts](../../frontend-vue/src/stores/catalog.ts) | Организационная структура, позиции |
| **Generator** | [generator.ts](../../frontend-vue/src/stores/generator.ts) | Генерация профилей, task tracking |
| **Profiles** | [profiles/](../../frontend-vue/src/stores/profiles/) | CRUD операции с профилями (модулярный) |

### 4.3 Store Communication

**Межстор взаимодействие**:

```typescript
// ✅ ПРАВИЛЬНО - импортируем другие stores в actions
export const useGeneratorStore = defineStore('generator', () => {
  async function startGeneration(positionId: string): Promise<void> {
    const catalogStore = useCatalogStore()

    // Проверяем что каталог загружен
    if (catalogStore.searchableItems.length === 0) {
      await catalogStore.loadSearchableItems()
    }

    // Используем данные из catalog store
    const position = catalogStore.getItemById(positionId)
    // ...
  }
})
```

---

## 5. Routing Architecture

### 5.1 Route Structure

```typescript
// src/router/index.ts
const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: AppLayout,          // Layout wrapper
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: DashboardView
      },
      {
        path: 'generator',
        name: 'generator',
        component: GeneratorView
      },
      {
        path: 'profiles',
        name: 'unified-profiles',
        component: UnifiedProfilesView
      }
    ]
  }
]
```

### 5.2 Navigation Guards

```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else {
    next()
  }
})
```

### 5.3 Route Meta Information

```typescript
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    title?: string
    icon?: string
  }
}
```

---

## 6. Component Architecture

### 6.1 Component Hierarchy

```
App.vue
│
├── LoginView.vue (standalone)
│
└── AppLayout.vue (authenticated layout)
    ├── AppHeader.vue
    │   ├── User menu
    │   └── Logout button
    │
    └── <router-view> (main content)
        ├── DashboardView.vue
        │   ├── BaseCard (stats)
        │   └── Charts
        │
        ├── GeneratorView.vue
        │   ├── v-tabs (Browse/Search/Bulk)
        │   ├── BrowseTreeTab
        │   │   └── OrganizationTree
        │   ├── QuickSearchTab
        │   │   └── PositionSearchAutocomplete
        │   └── BulkGenerationTab
        │       └── OrganizationTree
        │
        └── UnifiedProfilesView.vue
            ├── FilterBar
            ├── PositionsTable
            │   └── ProfileContent (в модальном окне)
            └── ProfileViewerModal
```

### 6.2 Component Types

#### 6.2.1 Common Components (Переиспользуемые)

**Расположение**: `src/components/common/`

Это **базовые** компоненты, которые используются по всему приложению.

| Компонент | Назначение | Props | Примеры использования |
|-----------|------------|-------|----------------------|
| **BaseCard** | Карточка с заголовком | `title`, `subtitle`, `actions` | Dashboard, Settings |

**КРИТИЧНО**: Всегда проверяйте `common/` перед созданием нового компонента!

#### 6.2.2 Feature Components

**Расположение**: `src/components/{feature}/`

Специализированные компоненты для конкретной фичи.

**Generator Components** (`src/components/generator/`):
- `BrowseTreeTab.vue` - Выбор через дерево организации
- `QuickSearchTab.vue` - Быстрый поиск позиций
- `BulkGenerationTab.vue` - Массовая генерация
- `OrganizationTree.vue` - 🔄 Дерево организационной структуры
- `PositionSearchAutocomplete.vue` - 🔄 Автокомплит поиска
- `GenerationProgressTracker.vue` - Трекер прогресса генерации

**Profiles Components** (`src/components/profiles/`):
- `FilterBar.vue` - Фильтры для списка профилей
- `PositionsTable.vue` - Таблица позиций с профилями
- `ProfileContent.vue` - Отображение содержимого профиля
- `ProfileViewerModal.vue` - Модальное окно просмотра

#### 6.2.3 Layout Components

**Расположение**: `src/components/layout/`

- `AppLayout.vue` - Главный layout с навигацией
- `AppHeader.vue` - Шапка приложения

### 6.3 Component Communication

**Props Down, Events Up**:

```vue
<!-- Parent -->
<template>
  <ChildComponent
    :items="items"
    :loading="loading"
    @select="handleSelect"
    @update:modelValue="handleUpdate"
  />
</template>

<script setup lang="ts">
const items = ref<Item[]>([])
const loading = ref(false)

function handleSelect(item: Item): void {
  console.log('Selected:', item)
}

function handleUpdate(value: Item[]): void {
  items.value = value
}
</script>
```

**V-Model для двустороннего биндинга**:

```vue
<!-- Child Component -->
<script setup lang="ts">
interface Props {
  modelValue: string[]
}
const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

function updateValue(newValue: string[]): void {
  emit('update:modelValue', newValue)
}
</script>
```

---

## 7. Service Layer

### 7.1 API Service Structure

**Базовый Axios instance** (`src/services/api.ts`):

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor для добавления auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor для обработки ошибок
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Redirect to login
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api
```

### 7.2 Специализированные Services

**Паттерн**: Каждый домен имеет свой service файл.

#### Auth Service (`src/services/auth.service.ts`)

```typescript
export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', {
      username,
      password
    })
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/api/auth/logout')
  }
}
```

#### Generation Service (`src/services/generation.service.ts`)

```typescript
export const generationService = {
  async startGeneration(
    department: string,
    position: string
  ): Promise<{ task_id: string }> {
    const response = await api.post('/api/generation/start', {
      department,
      position
    })
    return response.data
  },

  async checkStatus(taskId: string): Promise<TaskStatus> {
    const response = await api.get(`/api/generation/status/${taskId}`)
    return response.data
  },

  async getResult(taskId: string): Promise<GenerationResult> {
    const response = await api.get(`/api/generation/result/${taskId}`)
    return response.data
  }
}
```

### 7.3 Service Best Practices

```typescript
// ✅ ПРАВИЛЬНО - явные типы возвращаемых значений
async function getData(): Promise<DataResponse> {
  const response = await api.get<DataResponse>('/api/data')
  return response.data
}

// ✅ ПРАВИЛЬНО - обработка ошибок в store, не в service
async function getData(): Promise<DataResponse> {
  // Пусть ошибка пробросится в store
  const response = await api.get<DataResponse>('/api/data')
  return response.data
}

// ❌ НЕПРАВИЛЬНО - обработка ошибок в service
async function getData(): Promise<DataResponse | null> {
  try {
    const response = await api.get('/api/data')
    return response.data
  } catch (error) {
    console.error(error)
    return null
  }
}
```

---

## 8. Type System

### 8.1 Type Definition Strategy

**Где определять типы**:

| Категория | Расположение | Примеры |
|-----------|--------------|---------|
| API Responses | `types/api.ts` | `ApiResponse<T>`, `ApiError` |
| Domain Models | `types/{domain}.ts` | `types/profile.ts`, `types/generation.ts` |
| Component Props | В компоненте | `interface Props { ... }` |
| Store Types | `stores/{name}/types.ts` | Custom error classes |

### 8.2 Type Composition

```typescript
// Базовые типы
export interface BaseProfile {
  position_id: string
  position_name: string
  department: string
}

// Расширенные типы через intersection
export type FullProfile = BaseProfile & {
  competencies: Competency[]
  responsibilities: Responsibility[]
  created_at: string
}

// Union types для состояний
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

// Generic types для переиспользования
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
```

### 8.3 Type Guards

```typescript
// src/types/api.ts
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'status' in error &&
    'message' in error
  )
}

// Использование
if (isApiError(error)) {
  console.log(error.status, error.message)
}
```

---

## 9. Error Handling

### 9.1 Error Flow

```
User Action
    ↓
Store Action
    ↓
Service Call → API Error
    ↓
Store catches error
    ↓
Store sets error state
    ↓
Component shows error UI
```

### 9.2 Error Helper

**Используйте `getErrorMessage` helper**:

```typescript
// src/utils/errors.ts
export function getErrorMessage(error: unknown, fallback = 'Unknown error'): string {
  if (isAxiosError(error)) {
    return error.response?.data?.detail || error.message || fallback
  }
  if (error instanceof Error) {
    return error.message
  }
  return fallback
}
```

### 9.3 Custom Error Classes

```typescript
// src/stores/profiles/types.ts
export class ProfileError extends Error {
  constructor(
    message: string,
    public code: string,
    public cause?: unknown
  ) {
    super(message)
    this.name = 'ProfileError'
  }
}
```

---

## 10. Testing Strategy

### 10.1 Test Pyramid

```
        E2E Tests (TBD)
       /              \
      /   Integration   \
     /       Tests       \
    /____________________\
   /                      \
  /      Unit Tests        \
 /__________________________\
```

**Приоритеты**:
1. **Unit Tests** - Utils, pure functions (80%+ coverage)
2. **Integration Tests** - Stores with mocked API (80%+ coverage)
3. **Component Tests** - Critical components (60%+ coverage)
4. **E2E Tests** - To be determined

### 10.2 Что тестировать

**Utils** (100% coverage):
- ✅ Formatters (date, number, file size)
- ✅ Logger
- ✅ Error helpers

**Stores** (80%+ coverage):
- ✅ State initialization
- ✅ Getters calculations
- ✅ Actions success cases
- ✅ Actions error handling
- ✅ Side effects

**Components** (60%+ coverage):
- ✅ Props rendering
- ✅ Events emission
- ✅ User interactions
- ⚠️ Visual appearance (optional)

### 10.3 Test Structure

```typescript
// src/stores/__tests__/catalog.test.ts
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCatalogStore } from '../catalog'
import api from '@/services/api'

vi.mock('@/services/api')

describe('catalogStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('loadSearchableItems', () => {
    it('should load items successfully', async () => {
      // Arrange
      const mockItems = [{ position_id: '1', position_name: 'Manager' }]
      vi.mocked(api.get).mockResolvedValue({ data: mockItems })

      const store = useCatalogStore()

      // Act
      await store.loadSearchableItems()

      // Assert
      expect(store.searchableItems).toEqual(mockItems)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should handle errors', async () => {
      // Arrange
      vi.mocked(api.get).mockRejectedValue(new Error('Network error'))
      const store = useCatalogStore()

      // Act & Assert
      await expect(store.loadSearchableItems()).rejects.toThrow()
      expect(store.error).toBeTruthy()
    })
  })
})
```

---

## 11. Performance Patterns

### 11.1 Lazy Loading

**Routes**:
```typescript
const routes = [
  {
    path: '/profiles',
    component: () => import('@/views/UnifiedProfilesView.vue')
  }
]
```

**Components**:
```typescript
const HeavyComponent = defineAsyncComponent(
  () => import('./HeavyComponent.vue')
)
```

### 11.2 Computed Caching

```typescript
// ✅ ПРАВИЛЬНО - computed кэшируется
const filteredItems = computed(() => {
  return items.value.filter(item => item.active)
})

// ❌ НЕПРАВИЛЬНО - пересчитывается каждый раз
function getFilteredItems() {
  return items.value.filter(item => item.active)
}
```

### 11.3 Debouncing

```typescript
import { useDebounceFn } from '@vueuse/core'

const debouncedSearch = useDebounceFn((query: string) => {
  performSearch(query)
}, 300)
```

---

## 12. Build & Deployment

### 12.1 Environment Variables

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8022

# .env.production
VITE_API_BASE_URL=https://api.production.com
```

### 12.2 Build Commands

```bash
# Development
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Test
npm test

# Production build
npm run build

# Preview production build
npm run preview
```

### 12.3 Build Output

```
dist/
├── index.html
├── assets/
│   ├── index-{hash}.js    # Main bundle
│   ├── index-{hash}.css   # Styles
│   └── *.woff2            # Fonts
```

---

## 13. Key Design Decisions

### 13.1 Почему Composition API?

✅ **Преимущества**:
- Лучшая TypeScript поддержка
- Переиспользование логики (composables)
- Более явные dependencies
- Проще для tree-shaking

### 13.2 Почему модульные stores?

✅ **Преимущества**:
- Файлы < 300 строк
- Чёткое разделение ответственности
- Легче тестировать
- Легче поддерживать

Пример: `stores/profiles/` (833 строк → 7 модулей по < 300 строк)

### 13.3 Почему strict TypeScript?

✅ **Преимущества**:
- Ловит ошибки на этапе компиляции
- Лучший IntelliSense
- Документация через типы
- Безопаснее рефакторинг

---

## 14. Common Patterns

### 14.1 Loading States

```typescript
const loading = ref(false)
const error = ref<string | null>(null)

async function fetchData(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    // Fetch logic
  } catch (err: unknown) {
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}
```

### 14.2 Pagination

```typescript
const page = ref(1)
const pageSize = ref(25)
const totalItems = ref(0)

const paginatedItems = computed(() => {
  const start = (page.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allItems.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(totalItems.value / pageSize.value)
})
```

### 14.3 Filter & Search

```typescript
const searchQuery = ref('')
const filters = reactive({
  status: [],
  department: []
})

const filteredItems = computed(() => {
  let result = items.value

  // Text search
  if (searchQuery.value) {
    result = result.filter(item =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // Filters
  if (filters.status.length > 0) {
    result = result.filter(item => filters.status.includes(item.status))
  }

  return result
})
```

---

## 15. Migration & Upgrade Path

### 15.1 Будущие улучшения

- [ ] E2E тесты (Playwright/Cypress)
- [ ] Component visual regression tests
- [ ] Storybook для компонентов
- [ ] Bundle size optimization
- [ ] PWA support
- [ ] Internationalization (i18n)

### 15.2 Технический долг

Отслеживается в `.memory_bank/current_tasks.md`

---

## 16. Troubleshooting

### 16.1 Частые проблемы

**TypeScript ошибки после обновления зависимостей**:
```bash
# Очистить кэш и пересобрать
rm -rf node_modules/.vite
npm run build
```

**Тесты падают локально**:
```bash
# Очистить coverage
rm -rf coverage
npm test
```

**Hot reload не работает**:
```bash
# Перезапустить dev server
npm run dev -- --force
```

---

## 📚 Связанные документы

- **[Frontend Coding Standards](../guides/frontend_coding_standards.md)** - Правила написания кода
- **[Component Library](./component_library.md)** - Переиспользуемые компоненты
- **[Tech Stack](../tech_stack.md)** - Детали технологий
- **[Testing Strategy](../guides/testing_strategy.md)** - Стратегия тестирования

---

**Последнее обновление**: 2025-10-26
**Версия**: 1.0
**Статус**: ✅ Production Ready

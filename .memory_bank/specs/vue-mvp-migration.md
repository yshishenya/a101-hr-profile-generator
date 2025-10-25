# Vue.js MVP Migration Specification

**Feature ID**: VUE-MVP-001
**Priority**: High
**Status**: In Progress
**Created**: 2025-10-25
**Owner**: Development Team

---

## 1. Business Context

### 1.1 Problem Statement
Текущий NiceGUI фронтенд имеет следующие ограничения:
- ❌ Монолитная архитектура (компоненты >2000 строк)
- ❌ Отсутствие типизации → регулярные ошибки
- ❌ Нет мобильной версии
- ❌ Медленная разработка новых функций
- ❌ Нет покрытия тестами

### 1.2 Business Goals
- 🎯 Создать **простой, современный, реактивный** интерфейс
- 🎯 **MVP подход** - минимум функций, максимум пользы
- 🎯 Улучшить производительность на 80%
- 🎯 Добавить мобильную поддержку
- 🎯 Упростить добавление новых функций

### 1.3 Success Criteria
- ✅ Пользователи могут выполнять те же задачи, что и сейчас
- ✅ Интерфейс загружается <1 сек
- ✅ Работает на десктопе и планшетах
- ✅ Код покрыт тестами >80%
- ✅ Lighthouse score >90

---

## 2. MVP Scope (Минимально необходимые функции)

### 2.1 Must Have (Обязательно в MVP)

#### 🔐 Аутентификация
- Login страница (username + password)
- Logout функциональность
- JWT token управление
- Автоматический refresh токена
- Redirect на login при истечении сессии

#### 🏠 Dashboard (главная страница)
- Приветствие пользователя
- Статистика системы (карточки):
  - Всего позиций (1,689)
  - Всего профилей (сгенерированных)
  - Процент завершенности
- Quick actions кнопки:
  - "Генератор профилей"
  - "Массовая генерация"
  - "Все профили"

#### 🔍 Генератор профилей (одиночная генерация)
- **Поиск позиции:**
  - Автокомплит поиск по 1,689 позициям
  - Показ department в результатах
  - Debounce 300ms

- **Генерация:**
  - Форма с выбранной позицией
  - Кнопка "Сгенерировать"
  - Progress bar с real-time статусом
  - Polling каждые 2-3 сек

- **Просмотр результата:**
  - Карточка с профилем
  - Вкладки: Content, Metadata
  - **Inline редактирование** (новое!):
    - Кнопка "Редактировать"
    - Редактирование полей прямо в карточке
    - Сохранение изменений → новая версия
    - Отмена изменений
  - Кнопки экспорта:
    - JSON
    - Markdown
    - **DOCX** (новое!)
    - **XLSX** (новое!)

#### 🔄 Массовая генерация профилей (новое!)
- **Выбор позиций:**
  - Мультивыбор из списка всех позиций
  - Фильтр по отделу
  - Выбрать все позиции отдела
  - Отображение количества выбранных

- **Генерация:**
  - Кнопка "Сгенерировать выбранные"
  - Общий прогресс (X из Y завершено)
  - Статус каждой позиции:
    - ⏳ В очереди
    - 🔄 Генерируется
    - ✅ Готово
    - ❌ Ошибка
  - Возможность отмены

- **Результаты:**
  - Список сгенерированных профилей
  - Массовый экспорт:
    - ZIP архив с отдельными файлами
    - Один Excel файл (все профили в разных листах)

#### 📋 Список профилей
- Таблица с профилями:
  - Название позиции
  - Отдел
  - Дата создания
  - Статус
  - Версия (если редактировался)
- Пагинация (20 профилей на страницу)
- Базовые фильтры:
  - По отделу
  - По дате
  - По статусу
- Поиск по названию позиции
- Действия:
  - Просмотр профиля
  - Редактировать (inline)
  - Скачать (JSON, MD, DOCX, XLSX)
  - Массовое скачивание выбранных

#### 🎨 Темная тема (новое!)
- Переключатель темы в header
- Сохранение выбора в localStorage
- Поддержка system preference (auto)
- Все компоненты адаптированы под темную тему

### 2.2 Should Have (Желательно, можно в следующей итерации)
- 📱 Полная мобильная оптимизация (в MVP - desktop + tablet)
- 📊 Страница Analytics (в MVP - заглушка "Coming soon")
- ⚙️ Расширенные настройки пользователя
- 🔔 Push notifications о завершении генерации

### 2.3 Won't Have (Точно не в MVP, версия 2.0)
- ❌ Сравнение профилей side-by-side
- ❌ Workflow утверждения с email уведомлениями
- ❌ Admin панель (управление пользователями)
- ❌ Advanced analytics с графиками
- ❌ Полная мобильная версия (телефоны)
- ❌ PWA / Offline режим

---

## 3. Technical Architecture

### 3.1 Technology Stack (Простой и проверенный)

```yaml
Core:
  - Vue.js: 3.4+ (Composition API)
  - TypeScript: 5.0+ (строгая типизация, но не фанатично)
  - Vite: 5.0+ (быстрая сборка)

UI Framework:
  - Vuetify: 3.5+ (Material Design, много готовых компонентов)
  # Почему Vuetify?
  # - Простой в освоении
  # - 100+ готовых компонентов
  # - Адаптивный дизайн out-of-the-box
  # - Встроенная поддержка темной темы
  # - Не нужно писать много CSS

State Management:
  - Pinia: 2.1+ (официальный, простой)

Routing:
  - Vue Router: 4.2+

HTTP:
  - Axios: 1.6+ (interceptors для JWT)

Export Libraries:
  - docx: 8.5+ (DOCX генерация)
  - xlsx: 0.18+ (Excel генерация)
  - jszip: 3.10+ (ZIP архивы для bulk export)
  - file-saver: 2.0+ (сохранение файлов)

Forms:
  - Нет сложных библиотек валидации
  # Используем встроенный v-model + простые проверки
  # Для MVP не нужна VeeValidate

Testing:
  - Vitest: unit тесты (простые)
  - Cypress: E2E (критические пути)
```

### 3.2 Project Structure (Простая и понятная)

```
frontend-vue/
├── src/
│   ├── assets/              # Статика (логотипы, иконки)
│   ├── components/          # Переиспользуемые компоненты
│   │   ├── layout/
│   │   │   ├── AppHeader.vue      # Шапка сайта
│   │   │   └── AppLayout.vue      # Главный layout
│   │   ├── profile/
│   │   │   ├── ProfileCard.vue    # Карточка профиля
│   │   │   └── ProfileTable.vue   # Таблица профилей
│   │   └── common/
│   │       ├── LoadingSpinner.vue # Спиннер загрузки
│   │       └── EmptyState.vue     # Пустое состояние
│   ├── composables/         # Переиспользуемая логика
│   │   ├── useAuth.ts       # Логика аутентификации
│   │   ├── useApi.ts        # API вызовы
│   │   └── useNotify.ts     # Уведомления
│   ├── router/
│   │   └── index.ts         # Роутинг (5 страниц)
│   ├── services/            # API сервисы
│   │   ├── api.ts           # Axios instance + interceptors
│   │   ├── auth.service.ts  # Аутентификация
│   │   ├── profile.service.ts # Профили
│   │   └── catalog.service.ts # Каталог позиций
│   ├── stores/              # Pinia stores (простые!)
│   │   ├── auth.ts          # Хранение токена + user
│   │   └── catalog.ts       # Кэш позиций (1689 штук)
│   ├── types/               # TypeScript типы
│   │   ├── auth.ts
│   │   ├── profile.ts
│   │   └── api.ts
│   ├── views/               # Страницы (5 штук)
│   │   ├── LoginView.vue    # Страница логина
│   │   ├── DashboardView.vue # Главная
│   │   ├── GeneratorView.vue # Генератор
│   │   ├── ProfilesView.vue  # Список профилей
│   │   └── ProfileDetailView.vue # Детали профиля
│   ├── App.vue              # Корневой компонент
│   └── main.ts              # Entry point
├── public/                  # Статика (favicon, etc)
├── tests/
│   └── e2e/                 # E2E тесты (минимум)
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### 3.3 Component Simplicity Rules (Правила простоты)

**Каждый компонент должен быть:**
- ✅ Меньше 200 строк (если больше - разбить)
- ✅ Одна ответственность
- ✅ Минимум пропсов (max 5-7)
- ✅ Нет сложной логики во vue компонентах (логика в composables)

**Пример простого компонента:**
```vue
<template>
  <v-card>
    <v-card-title>{{ title }}</v-card-title>
    <v-card-text>{{ content }}</v-card-text>
    <v-card-actions>
      <v-btn @click="handleClick">Action</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
// Простой, понятный, без магии
defineProps<{
  title: string
  content: string
}>()

const emit = defineEmits<{
  action: []
}>()

const handleClick = () => {
  emit('action')
}
</script>
```

---

## 4. Design System (Простой и современный)

### 4.1 UI Принципы MVP
- **Простота > Красота** - функциональность важнее декора
- **Консистентность** - одинаковые паттерны везде
- **Responsive** - работает на desktop + tablet (mobile - позже)
- **Минималистичный** - без лишних элементов

### 4.2 Color Palette (Vuetify Material Design)
```scss
$primary: #1976D2    // Синий (основной цвет A101)
$secondary: #424242  // Темно-серый
$accent: #82B1FF     // Светло-синий
$error: #FF5252      // Красный для ошибок
$success: #4CAF50    // Зеленый для успеха
$warning: #FFC107    // Желтый для предупреждений
```

### 4.3 Typography (Vuetify defaults)
- **Font**: Roboto (стандарт Material Design)
- **Размеры**: Используем Vuetify классы (.text-h1, .text-body-1, etc.)

### 4.4 Spacing (Vuetify spacing classes)
- ma-{1-16}: margin
- pa-{1-16}: padding
- 1 unit = 4px

### 4.5 Key UI Patterns

#### Layout Pattern (все страницы одинаковые)
```
┌─────────────────────────────────────┐
│  AppHeader (logo, user, logout)     │
├─────────────────────────────────────┤
│                                     │
│  Page Content (v-container)         │
│                                     │
│  - max-width: 1200px                │
│  - pa-4 (padding 16px)              │
│                                     │
└─────────────────────────────────────┘
```

#### Loading Pattern
```vue
<v-progress-circular indeterminate color="primary" />
<!-- Простой спиннер, без анимаций -->
```

#### Empty State Pattern
```vue
<v-container class="text-center pa-8">
  <v-icon size="64" color="grey-lighten-1">mdi-inbox</v-icon>
  <p class="text-h6 mt-4">No profiles yet</p>
  <v-btn color="primary" to="/generator">Create First Profile</v-btn>
</v-container>
```

#### Error Pattern
```vue
<v-alert type="error" variant="tonal" closable>
  {{ errorMessage }}
</v-alert>
```

---

## 5. User Flows (MVP)

### 5.1 Flow 1: Login → Dashboard → Generator → View Profile

```
1. User opens site (/)
   ↓
2. Redirect to /login (if not authenticated)
   ↓
3. Enter username + password
   ↓
4. Click "Login" button
   ↓
5. Success → redirect to /dashboard
   ↓
6. See dashboard with stats + quick actions
   ↓
7. Click "Profile Generator" button
   ↓
8. Navigate to /generator
   ↓
9. Start typing in search field "Менеджер..."
   ↓
10. See autocomplete suggestions
    ↓
11. Select "Менеджер по продажам (Отдел продаж)"
    ↓
12. Click "Generate Profile" button
    ↓
13. See progress bar (0% → 50% → 100%)
    ↓
14. Profile appears in card below
    ↓
15. Switch between tabs (Content, Metadata)
    ↓
16. Click "Download JSON" button
    ↓
17. File downloads
```

### 5.2 Flow 2: View All Profiles

```
1. From dashboard click "All Profiles"
   ↓
2. Navigate to /profiles
   ↓
3. See table with all profiles (paginated)
   ↓
4. Use filters (department, date) - optional
   ↓
5. Click on profile row
   ↓
6. Navigate to /profiles/:id
   ↓
7. View profile details
   ↓
8. Download or go back
```

---

## 6. API Integration

### 6.1 Backend API (не меняется!)
Backend API уже готов и документирован в `docs/api/`.

**Используемые endpoints для MVP:**

```typescript
// Authentication
POST   /api/auth/login          // Login
POST   /api/auth/logout         // Logout
POST   /api/auth/refresh        // Refresh token
GET    /api/auth/me             // Get current user

// Catalog (кэшируем в Pinia store!)
GET    /api/organization/search-items  // 1689 позиций

// Profile Generation
POST   /api/generation/start           // Start generation
GET    /api/generation/{task_id}/status // Poll status
GET    /api/generation/{task_id}/result // Get result

// Profiles
GET    /api/profiles                   // List profiles (paginated)
GET    /api/profiles/{id}              // Get profile details
GET    /api/profiles/{id}/download/json // Download JSON
GET    /api/profiles/{id}/download/md   // Download Markdown

// Dashboard
GET    /api/dashboard/stats/minimal    // Dashboard stats
```

### 6.2 Axios Setup (простой)

```typescript
// services/api.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
  timeout: 30000,
})

// Request interceptor: добавляем JWT токен
api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Response interceptor: обрабатываем 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api
```

---

## 7. State Management (Pinia - простой!)

### 7.1 Auth Store (основной)

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(username: string, password: string) {
    const response = await authService.login(username, password)
    token.value = response.access_token
    user.value = response.user
    localStorage.setItem('token', response.access_token)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isAuthenticated, login, logout }
})
```

### 7.2 Catalog Store (кэш позиций)

```typescript
// stores/catalog.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCatalogStore = defineStore('catalog', () => {
  const positions = ref<Position[]>([])
  const isLoaded = ref(false)

  async function loadPositions() {
    if (isLoaded.value) return // Загружаем только один раз!

    const data = await catalogService.getPositions()
    positions.value = data
    isLoaded.value = true
  }

  function searchPositions(query: string) {
    return positions.value.filter(p =>
      p.name.toLowerCase().includes(query.toLowerCase())
    )
  }

  return { positions, isLoaded, loadPositions, searchPositions }
})
```

---

## 8. Testing Strategy (MVP)

### 8.1 Unit Tests (простые, быстрые)
- Тестируем только критичную логику:
  - Stores (Pinia)
  - Composables
  - Services (с моками API)

**Не тестируем:**
- Vue компоненты (в MVP не критично)
- Типы TypeScript (компилятор это проверит)

**Цель:** 60-70% покрытие (не 80%, это MVP!)

### 8.2 E2E Tests (критические пути)
Только самое важное:
1. Login → Dashboard
2. Dashboard → Generator → Generate → View
3. Profiles List → View Profile

**Инструмент:** Cypress (простой и наглядный)

---

## 9. Performance Requirements (MVP)

### 9.1 Loading Metrics
- ✅ Initial Load: <2 сек (не <1 сек, это MVP)
- ✅ Route Change: <500ms
- ✅ API Response: <200ms (backend уже быстрый)

### 9.2 Bundle Size
- ✅ Initial Bundle: <800 KB (gzipped)
- ✅ Используем code splitting для routes

### 9.3 Lighthouse Score
- ✅ Performance: >85 (не >90, это MVP)
- ✅ Accessibility: >90
- ✅ Best Practices: >90
- ✅ SEO: >80

---

## 10. Development Plan (Enhanced MVP)

### Week 1-2: Foundation & Authentication
- [ ] Project setup (Vite + Vue + TypeScript + Vuetify)
- [ ] Configure ESLint, Prettier
- [ ] Setup Axios + interceptors
- [ ] Create Pinia stores (auth, catalog)
- [ ] Implement login page
- [ ] Implement AppLayout + AppHeader with theme switcher
- [ ] Setup routing with guards
- [ ] **Dark theme support** (Vuetify themes)

**Deliverable:** Работающий login + темная тема + защищенные routes

### Week 3: Dashboard & Single Generation
- [ ] Dashboard page (stats + quick actions)
- [ ] Generator page:
  - [ ] Search с autocomplete
  - [ ] Generation form
  - [ ] Progress tracking
  - [ ] Result display
- [ ] Profile card component
- [ ] **Inline editing component**:
  - [ ] Edit mode toggle
  - [ ] Editable fields
  - [ ] Save/Cancel buttons
  - [ ] Versioning support

**Deliverable:** Одиночная генерация с редактированием

### Week 4: Export Functionality
- [ ] Export buttons (JSON, MD, DOCX, XLSX)
- [ ] **DOCX generation** (библиотека docx.js):
  - [ ] Форматированный документ
  - [ ] Таблицы, списки
  - [ ] Стили A101
- [ ] **XLSX generation** (библиотека xlsx):
  - [ ] Структурированные листы
  - [ ] Форматирование
- [ ] Download utilities
- [ ] Progress indicators для экспорта

**Deliverable:** Полный набор форматов экспорта

### Week 5: Bulk Generation
- [ ] Bulk generation page:
  - [ ] Multi-select позиций
  - [ ] Фильтр по отделу
  - [ ] "Выбрать все отдела"
  - [ ] Отображение выбранных (N позиций)
- [ ] Bulk generation process:
  - [ ] Параллельная генерация (с лимитом)
  - [ ] Общий прогресс
  - [ ] Статус по каждой позиции
  - [ ] Возможность отмены
- [ ] Bulk results view
- [ ] **Bulk export**:
  - [ ] ZIP архив
  - [ ] Единый Excel файл (multi-sheet)

**Deliverable:** Массовая генерация с экспортом

### Week 6: Profiles Management
- [ ] Profiles list page:
  - [ ] Table с пагинацией
  - [ ] Filters (department, date, status)
  - [ ] Search
  - [ ] Multi-select для массовых действий
- [ ] Profile detail page:
  - [ ] Full profile view
  - [ ] Inline editing
  - [ ] Version history
  - [ ] All export formats
- [ ] Bulk actions:
  - [ ] Bulk download (ZIP)
  - [ ] Bulk delete

**Deliverable:** Полное управление профилями

### Week 7: Polish & Optimization
- [ ] Error handling везде
- [ ] Loading states везде
- [ ] Empty states
- [ ] Responsive fixes (desktop + tablet)
- [ ] Performance optimization:
  - [ ] Code splitting
  - [ ] Lazy loading
  - [ ] Virtual scrolling для больших списков
- [ ] Theme consistency проверка

**Deliverable:** Отполированный UI/UX

### Week 8: Testing & Launch
- [ ] Unit tests (60-70% coverage):
  - [ ] Stores
  - [ ] Composables
  - [ ] Utils
- [ ] E2E tests (критические пути):
  - [ ] Login → Dashboard
  - [ ] Single generation
  - [ ] Bulk generation
  - [ ] Profile editing
  - [ ] Export flows
- [ ] Bug fixing
- [ ] Documentation
- [ ] Production build optimization

**Deliverable:** Production-ready Enhanced MVP

---

## 11. Acceptance Criteria (MVP)

### 11.1 Functional
- ✅ Пользователь может войти/выйти
- ✅ Пользователь может найти позицию (autocomplete)
- ✅ Пользователь может сгенерировать профиль
- ✅ Пользователь видит прогресс генерации
- ✅ Пользователь может просмотреть профиль
- ✅ Пользователь может скачать профиль (JSON, MD)
- ✅ Пользователь видит список всех профилей
- ✅ Пользователь может фильтровать профили
- ✅ Пользователь может открыть детали профиля

### 11.2 Non-Functional
- ✅ Загрузка страницы <2 сек
- ✅ Работает в Chrome, Firefox, Safari
- ✅ Работает на десктопе и планшете (iPad)
- ✅ Нет критических багов
- ✅ Все ошибки API обрабатываются gracefully
- ✅ TypeScript без ошибок компиляции
- ✅ ESLint без ошибок

### 11.3 Code Quality
- ✅ Все компоненты <200 строк
- ✅ Нет дублирования кода
- ✅ Используются Vuetify компоненты (не custom CSS)
- ✅ Stores простые и понятные
- ✅ Services имеют error handling

---

## 12. Out of Scope (Не в MVP!)

Следующие функции **точно не входят в MVP** и будут реализованы в следующих версиях:

- ❌ Массовая генерация профилей
- ❌ Inline редактирование профилей
- ❌ Сравнение профилей
- ❌ Workflow утверждения
- ❌ Admin панель
- ❌ DOCX/XLSX экспорт (только JSON/MD в MVP)
- ❌ Темная тема
- ❌ Настройки пользователя
- ❌ Push notifications
- ❌ Offline mode (PWA)
- ❌ Полная мобильная оптимизация (только планшеты в MVP)
- ❌ Advanced analytics

---

## 13. Risks & Mitigation

### 13.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Сложность Vuetify | Low | Medium | Vuetify простой, много документации |
| TypeScript замедлит разработку | Medium | Low | Используем не строгий режим для MVP |
| Performance проблемы | Low | High | Code splitting, lazy loading, profiling |
| API несовместимость | Very Low | High | API уже готов и протестирован |

### 13.2 Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Недооценка сроков | Medium | Medium | Буфер 1 неделя, MVP scope четкий |
| Scope creep | High | High | Строго следовать MVP scope, говорить "нет" |
| Недостаток ресурсов | Low | High | 1 разработчик full-time достаточно |

---

## 14. Success Metrics (KPI)

### 14.1 After 1 Month
- ✅ 80%+ пользователей используют новый фронт
- ✅ 0 критических багов
- ✅ Скорость генерации профиля: -30% (с 5 мин до 3.5 мин)

### 14.2 After 3 Months
- ✅ 100% миграция с NiceGUI
- ✅ Lighthouse score >85
- ✅ <5 багов в backlog
- ✅ Готовность к добавлению новых фич

---

## 15. Next Steps (After MVP)

После успешного запуска MVP (6 недель):

**Version 1.1 (Week 7-10):**
- Массовая генерация
- DOCX/XLSX экспорт
- Темная тема

**Version 1.2 (Week 11-14):**
- Inline редактирование
- Сравнение профилей
- Полная мобильная версия

**Version 2.0 (Week 15-20):**
- Admin панель
- Workflow утверждения
- Advanced analytics

---

## Appendix: Design Mockups (Simple Wireframes)

### A.1 Login Page
```
┌──────────────────────────────────┐
│                                  │
│        [A101 Logo]               │
│                                  │
│   ┌──────────────────────────┐   │
│   │  Username                │   │
│   └──────────────────────────┘   │
│                                  │
│   ┌──────────────────────────┐   │
│   │  Password      [👁]      │   │
│   └──────────────────────────┘   │
│                                  │
│   ┌──────────────────────────┐   │
│   │     LOGIN                │   │
│   └──────────────────────────┘   │
│                                  │
└──────────────────────────────────┘
```

### A.2 Dashboard Page
```
┌────────────────────────────────────────┐
│ [A101]  Dashboard   [User ▾] [Logout] │
├────────────────────────────────────────┤
│                                        │
│  Welcome back, Ivan! 👋                │
│                                        │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ 1,689    │ │ 234      │ │ 14%    │ │
│  │ Positions│ │ Profiles │ │ Done   │ │
│  └──────────┘ └──────────┘ └────────┘ │
│                                        │
│  Quick Actions:                        │
│  ┌──────────────────────────────────┐  │
│  │  🚀 Generate Profile             │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  📋 View All Profiles            │  │
│  └──────────────────────────────────┘  │
│                                        │
└────────────────────────────────────────┘
```

### A.3 Generator Page
```
┌────────────────────────────────────────┐
│ [A101]  Generator   [User ▾] [Logout] │
├────────────────────────────────────────┤
│                                        │
│  Search Position:                      │
│  ┌──────────────────────────────────┐  │
│  │ Менеджер...          [🔍]        │  │
│  └──────────────────────────────────┘  │
│    Менеджер по продажам (Продажи)      │
│    Менеджер по продукту (IT)           │
│                                        │
│  Selected: Менеджер по продажам        │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Generate Profile                │  │
│  └──────────────────────────────────┘  │
│                                        │
│  [Progress bar: 75% ████████░░]        │
│  Generating... (30 seconds left)       │
│                                        │
│  ┌────────────────────────────────┐    │
│  │ Profile: Менеджер по продажам  │    │
│  │ [Content] [Metadata]           │    │
│  │                                │    │
│  │ Description: ...               │    │
│  │ Responsibilities: ...          │    │
│  │                                │    │
│  │ [Download JSON] [Download MD]  │    │
│  └────────────────────────────────┘    │
│                                        │
└────────────────────────────────────────┘
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-25
**Status:** Ready for Implementation

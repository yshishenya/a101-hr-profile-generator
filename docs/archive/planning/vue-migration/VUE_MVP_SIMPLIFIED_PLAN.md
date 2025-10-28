# Vue.js MVP - Упрощенный план (на базе существующего API)

**Дата:** 2025-10-25
**Срок:** 8 недель
**Подход:** Максимально использовать существующий backend API

---

## 🔍 Анализ существующего Backend API

### ✅ Что УЖЕ ЕСТЬ на бэкенде:

#### Authentication (простая, БЕЗ RBAC!)
```
POST   /api/auth/login          # username + password
POST   /api/auth/logout         # logout
POST   /api/auth/refresh        # refresh token
GET    /api/auth/me             # current user
GET    /api/auth/validate       # validate token
```

**User model:**
```typescript
{
  id: number
  username: string
  full_name: string
  is_active: boolean
  created_at: string
  last_login: string
  // НЕТ ролей! Простая авторизация по паролю
}
```

#### Generation (Async - уже реализовано!)
```
POST   /api/generation/start               # Start task
GET    /api/generation/{task_id}/status    # Poll status
GET    /api/generation/{task_id}/result    # Get result
DELETE /api/generation/{task_id}           # Cancel
GET    /api/generation/tasks/active        # Active tasks list
```

**Generation Request:**
```json
{
  "department": "Группа анализа данных",
  "position": "Аналитик данных",
  "employee_name": "Иванов Иван",  // опционально
  "temperature": 0.1,
  "save_result": true
}
```

**Task statuses:** `queued`, `processing`, `completed`, `failed`, `cancelled`
**Progress tracking:** 0-100% с текущим шагом

#### Profiles Management
```
GET    /api/profiles/                      # List (pagination + filters)
GET    /api/profiles/{id}                  # Get by ID
PUT    /api/profiles/{id}                  # Update metadata
DELETE /api/profiles/{id}                  # Archive (soft delete)
POST   /api/profiles/{id}/restore          # Restore
GET    /api/profiles/{id}/download/json    # Download JSON
GET    /api/profiles/{id}/download/md      # Download Markdown
GET    /api/profiles/{id}/download/docx    # Download DOCX
```

**Filters:** `page`, `limit`, `department`, `position`, `search`, `status`

#### Organization Catalog
```
GET    /api/organization/search-items      # All 1689 positions
GET    /api/catalog/departments            # All departments
GET    /api/catalog/positions/{dept}       # Positions in dept
```

**Response format (search-items):**
```json
[
  {
    "id": "...",
    "name": "Аналитик данных",
    "department": "Группа анализа данных",
    "full_path": "Департамент/Группа/Позиция"
  }
]
```

#### Dashboard
```
GET    /api/dashboard/stats                # Full stats
GET    /api/dashboard/stats/minimal        # Minimal stats
GET    /api/dashboard/stats/activity       # Activity feed
```

---

## ❌ Чего НЕТ на бэкенде (нужно решить)

### 1. Массовая генерация
**Статус:** НЕТ специального endpoint
**Решение:**
- **Вариант A (рекомендую):** Фронт запускает N задач через `POST /api/generation/start`
- **Вариант B:** Добавить `POST /api/generation/bulk` на бэк

### 2. Inline редактирование профилей
**Статус:** Есть `PUT /api/profiles/{id}`, но он обновляет только metadata (employee_name, status)
**Решение:**
- **Вариант A:** Расширить `PUT /api/profiles/{id}` чтобы принимал `profile_content`
- **Вариант B:** Добавить `PATCH /api/profiles/{id}/content` на бэк

### 3. XLSX экспорт
**Статус:** Есть JSON, MD, DOCX. НЕТ XLSX
**Решение:**
- **Вариант A (рекомендую):** Добавить `GET /api/profiles/{id}/download/xlsx` на бэк
- **Вариант B:** Генерировать XLSX на фронте из JSON (библиотека xlsx)

### 4. Bulk download (ZIP архив)
**Статус:** НЕТ
**Решение:**
- **Вариант A:** Добавить `POST /api/profiles/download/bulk` (принимает массив ID) на бэк
- **Вариант B:** Фронт скачивает файлы по одному и упаковывает в ZIP (библиотека jszip)

### 5. Темная тема
**Статус:** Frontend feature, бэк не нужен
**Решение:** Vuetify themes + localStorage

---

## 📋 Упрощенный MVP Scope

### ВКЛЮЧАЕМ в MVP (8 недель):

#### Week 1-2: Foundation
- ✅ Vue 3 + TypeScript + Vite + Vuetify setup
- ✅ Простая авторизация (username/password, БЕЗ RBAC)
- ✅ JWT token management
- ✅ Axios interceptors
- ✅ Pinia stores (auth, catalog)
- ✅ Routing + guards
- ✅ Layout + Header
- ✅ **Темная тема** (Vuetify themes)

#### Week 3: Dashboard
- ✅ Dashboard page
- ✅ Stats cards (используем `/api/dashboard/stats/minimal`)
- ✅ Quick actions buttons

#### Week 4: Single Generation
- ✅ Generator page
- ✅ Position search autocomplete (кэш `/api/organization/search-items`)
- ✅ Generation form
- ✅ Progress tracking (polling `/api/generation/{task_id}/status`)
- ✅ Result display
- ✅ Download buttons (JSON, MD, DOCX) - используем существующие endpoints

#### Week 5: Profiles List
- ✅ Profiles table (pagination, filters)
- ✅ Search
- ✅ Profile detail view
- ✅ Download individual profiles

#### Week 6: Массовая генерация
**Решение:** Фронт запускает N задач параллельно (с лимитом 5 одновременных)
- ✅ Multi-select позиций
- ✅ Фильтр по отделу
- ✅ Запуск нескольких задач через `POST /api/generation/start`
- ✅ Отслеживание статуса всех задач
- ✅ Общий прогресс

#### Week 7: Inline editing + XLSX
**Требует изменений на бэке (минимальные):**
- 🔧 Backend: Расширить `PUT /api/profiles/{id}` для редактирования content
- 🔧 Backend: Добавить `GET /api/profiles/{id}/download/xlsx`
- ✅ Frontend: Inline editing UI
- ✅ Frontend: XLSX export button

#### Week 8: Bulk operations + Polish
**Требует изменений на бэке (опционально):**
- 🔧 Backend: `POST /api/profiles/download/bulk` (или делаем на фронте)
- ✅ Frontend: Bulk selection
- ✅ Frontend: Bulk download (ZIP)
- ✅ Error handling везде
- ✅ Loading states
- ✅ Responsive

### НЕ включаем в MVP:
- ❌ Admin панель
- ❌ Workflow утверждения
- ❌ Сравнение профилей
- ❌ Analytics страница (заглушка "Coming soon")
- ❌ Полная мобильная версия (только tablet)

---

## 🛠️ Минимальные изменения Backend (Week 7)

### 1. Inline editing support

**Файл:** `backend/api/profiles.py`

**Изменить endpoint:**
```python
@router.put("/{profile_id}")
async def update_profile(
    profile_id: str,
    employee_name: Optional[str] = None,
    status: Optional[str] = None,
    profile_content: Optional[dict] = None,  # НОВОЕ!
    user: dict = Depends(get_current_user),
    db_manager=Depends(get_db_manager)
):
    """
    Обновить профиль (metadata + content).

    Если передан profile_content, создается новая версия профиля.
    """
    # ... implementation
```

### 2. XLSX export

**Файл:** `backend/api/profiles.py`

**Добавить endpoint:**
```python
@router.get("/{profile_id}/download/xlsx")
async def download_profile_xlsx(
    profile_id: str,
    user: dict = Depends(get_current_user),
    db_manager=Depends(get_db_manager)
):
    """
    Скачать профиль в формате XLSX.

    Использует библиотеку openpyxl (уже в requirements.txt).
    """
    # ... implementation
```

### 3. Bulk download (опционально)

**Файл:** `backend/api/profiles.py`

**Добавить endpoint:**
```python
@router.post("/download/bulk")
async def download_profiles_bulk(
    profile_ids: List[str],
    format: str = "json",  # json, md, docx, xlsx
    user: dict = Depends(get_current_user),
    db_manager=Depends(get_db_manager)
):
    """
    Скачать несколько профилей в ZIP архиве.

    Response: application/zip
    """
    # ... implementation
```

**Оценка:** 3-4 часа работы на бэкенде

---

## 🎨 Frontend Architecture (Упрощенная)

### Technology Stack

```yaml
Core:
  Vue.js: 3.4+
  TypeScript: 5.0+ (НЕ строгий режим)
  Vite: 5.0+

UI:
  Vuetify: 3.5+ (Material Design)

State:
  Pinia: 2.1+

HTTP:
  Axios: 1.6+

Export (frontend):
  file-saver: 2.0+     # Save files
  jszip: 3.10+         # ZIP archives (if backend doesn't provide)
```

**УБРАЛИ из плана:**
- ❌ `docx` library (делаем на бэке)
- ❌ `xlsx` library (делаем на бэке, но можем оставить для bulk на фронте)

### Project Structure

```
frontend-vue/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppHeader.vue          # С переключателем темы
│   │   │   └── AppLayout.vue
│   │   ├── profile/
│   │   │   ├── ProfileCard.vue
│   │   │   ├── ProfileTable.vue
│   │   │   ├── ProfileEditor.vue       # Inline editing
│   │   │   └── ProfileExport.vue       # Export buttons
│   │   ├── generator/
│   │   │   ├── PositionSearch.vue      # Autocomplete
│   │   │   ├── GenerationForm.vue
│   │   │   ├── GenerationProgress.vue  # Progress tracking
│   │   │   └── BulkSelector.vue        # Bulk generation
│   │   └── common/
│   │       ├── LoadingSpinner.vue
│   │       └── EmptyState.vue
│   ├── composables/
│   │   ├── useAuth.ts
│   │   ├── useTheme.ts                # Dark theme toggle
│   │   ├── useGeneration.ts           # Generation polling
│   │   └── useBulkGeneration.ts       # Bulk tasks management
│   ├── router/
│   │   └── index.ts
│   ├── services/
│   │   ├── api.ts                     # Axios instance
│   │   ├── auth.service.ts
│   │   ├── profile.service.ts
│   │   ├── generation.service.ts
│   │   ├── catalog.service.ts
│   │   └── dashboard.service.ts
│   ├── stores/
│   │   ├── auth.ts                    # Simple auth (no RBAC)
│   │   └── catalog.ts                 # Cache 1689 positions
│   ├── types/
│   │   ├── auth.ts                    # User (без roles!)
│   │   ├── profile.ts
│   │   ├── generation.ts
│   │   └── api.ts
│   ├── views/
│   │   ├── LoginView.vue
│   │   ├── DashboardView.vue
│   │   ├── GeneratorView.vue          # Single generation
│   │   ├── BulkGeneratorView.vue      # Bulk generation
│   │   ├── ProfilesView.vue           # List
│   │   └── ProfileDetailView.vue      # Detail + edit
│   ├── plugins/
│   │   └── vuetify.ts                 # Light + Dark themes
│   ├── App.vue
│   └── main.ts
├── .env.example
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 📝 Упрощенные TypeScript типы (на базе реального API)

### Auth Types

```typescript
// types/auth.ts
export interface User {
  id: number
  username: string
  full_name: string
  is_active: boolean
  created_at: string
  last_login: string | null
  // НЕТ roles! Простая авторизация
}

export interface LoginRequest {
  username: string
  password: string
  remember_me?: boolean
}

export interface LoginResponse {
  success: boolean
  timestamp: string
  message: string
  access_token: string
  token_type: string
  expires_in: number
  user_info: User
}
```

### Generation Types

```typescript
// types/generation.ts
export interface GenerationRequest {
  department: string
  position: string
  employee_name?: string
  temperature?: number
  save_result?: boolean
}

export interface GenerationTask {
  task_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  estimated_duration: number | null
  current_step: string | null
  error_message: string | null
}

export interface GenerationResponse {
  task_id: string
  status: string
  message: string
  estimated_duration: number | null
}

export interface TaskStatusResponse {
  task: GenerationTask
  result: GenerationResult | null
}

export interface GenerationResult {
  success: boolean
  profile: any  // Profile content
  metadata: {
    generation: {
      timestamp: string
      duration: number
      temperature: number
    }
    llm: {
      model: string
      tokens: {
        input: number
        output: number
        total: number
      }
    }
  }
}
```

### Profile Types

```typescript
// types/profile.ts
export interface Position {
  id: string
  name: string
  department: string
  full_path: string
}

export interface Profile {
  profile_id: string
  department: string
  position: string
  employee_name: string | null
  status: 'completed' | 'archived' | 'in_progress'
  validation_score: number
  completeness_score: number
  created_at: string
  created_by_username: string
  actions: {
    download_json: string
    download_md: string
    download_docx: string
  }
}

export interface ProfileDetail {
  profile_id: string
  profile: any  // Full profile content
  metadata: any
  created_at: string
  created_by_username: string
  actions: {
    download_json: string
    download_md: string
    download_docx: string
  }
}

export interface ProfilesListResponse {
  profiles: Profile[]
  pagination: {
    page: number
    limit: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  filters_applied: {
    department: string | null
    position: string | null
    search: string | null
    status: string | null
  }
}
```

---

## 🚀 Week-by-Week Plan (Детальный)

### Week 1-2: Foundation & Auth

**Setup (Day 1):**
```bash
npm create vite@latest frontend-vue -- --template vue-ts
cd frontend-vue
npm install
npm install vuetify@^3.5.0 @mdi/font
npm install pinia@^2.1.0 vue-router@^4.2.0
npm install axios@^1.6.0
npm install file-saver@^2.0.0 jszip@^3.10.0
npm install -D @types/node sass
```

**Auth Service (Day 2-3):**
```typescript
// services/auth.service.ts
import api from './api'
import type { LoginRequest, LoginResponse, User } from '@/types/auth'

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', credentials)
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/api/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },

  async refresh(): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/refresh')
    return response.data
  }
}
```

**Auth Store (Day 4-5):**
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth.service'
import type { User, LoginRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: LoginRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await authService.login(credentials)
      token.value = response.access_token
      user.value = response.user_info
      localStorage.setItem('token', response.access_token)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout
  }
})
```

**Theme Composable (Day 6):**
```typescript
// composables/useTheme.ts
import { ref, watch } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'

export function useTheme() {
  const vuetifyTheme = useVuetifyTheme()
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  watch(isDark, (value) => {
    vuetifyTheme.global.name.value = value ? 'dark' : 'light'
    localStorage.setItem('theme', value ? 'dark' : 'light')
  })

  function toggleTheme() {
    isDark.value = !isDark.value
  }

  // Apply theme on mount
  vuetifyTheme.global.name.value = isDark.value ? 'dark' : 'light'

  return {
    isDark,
    toggleTheme
  }
}
```

**Deliverable Week 1-2:** Login работает + темная тема

---

### Week 3-8: ... (полный план в отдельном документе)

---

## 📊 Acceptance Criteria (Упрощенные)

### Functional
- ✅ Пользователь может войти (username/password)
- ✅ Пользователь может переключить тему (light/dark)
- ✅ Пользователь может найти позицию (autocomplete из 1689)
- ✅ Пользователь может сгенерировать 1 профиль
- ✅ Пользователь видит прогресс генерации
- ✅ Пользователь может скачать профиль (JSON, MD, DOCX, XLSX)
- ✅ Пользователь может запустить массовую генерацию (N позиций)
- ✅ Пользователь видит статус каждой задачи
- ✅ Пользователь может редактировать профиль (inline)
- ✅ Пользователь может скачать несколько профилей (ZIP)

### Non-Functional
- ✅ Загрузка <2 сек
- ✅ Работает в Chrome, Firefox, Safari
- ✅ Desktop + Tablet (mobile - нет)
- ✅ Темная тема работает корректно
- ✅ Нет критических багов
- ✅ TypeScript без ошибок

---

## ⚙️ Backend Changes Required

**Минимальные изменения (3-4 часа):**

1. **Week 7:** Расширить `PUT /api/profiles/{id}` для inline editing
2. **Week 7:** Добавить `GET /api/profiles/{id}/download/xlsx`
3. **Week 8:** Добавить `POST /api/profiles/download/bulk` (опционально)

**Если не делать на бэке:**
- XLSX можно генерировать на фронте (библиотека `xlsx`)
- Bulk download можно делать на фронте (скачать по одному + ZIP)

---

## 🎯 Next Steps

1. **Утвердить этот упрощенный план**
2. **Решить про backend changes:**
   - Делаем в Week 7 (рекомендую)
   - Или делаем все на фронте
3. **Начать инициализацию Vue.js проекта**

**Готовы начать?** 🚀

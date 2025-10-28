# Vue.js MVP - Детальный план реализации

**Дата начала:** 2025-10-25
**Срок:** 6 недель (до 2025-12-06)
**Подход:** Простой, современный, реактивный интерфейс для MVP

---

## 📌 Принципы разработки MVP

### KISS (Keep It Simple, Stupid)
- ✅ Используем готовые Vuetify компоненты (не пишем CSS)
- ✅ Минимум кастомизации
- ✅ Стандартные паттерны Vue.js
- ✅ Простая структура (не overengineering)

### YAGNI (You Aren't Gonna Need It)
- ❌ НЕ делаем: массовые операции, inline editing, admin панель
- ✅ Делаем: только то, что нужно для работы системы

### Правило 80/20
- 80% функциональности реализуем за 20% времени
- Остальные 20% функций - в следующих версиях

---

## Week 1-2: Foundation & Authentication

### Day 1: Project Setup (2-3 часа)

#### 1.1 Создание проекта
```bash
# В папке HR создаем новую директорию
cd /home/yan/A101/HR
mkdir frontend-vue
cd frontend-vue

# Инициализация Vite проекта с Vue + TypeScript
npm create vite@latest . -- --template vue-ts

# Установка зависимостей
npm install
```

#### 1.2 Установка Vuetify и зависимостей
```bash
# UI Framework
npm install vuetify@^3.5.0
npm install @mdi/font  # Material Design Icons

# State Management
npm install pinia@^2.1.0

# Routing
npm install vue-router@^4.2.0

# HTTP Client
npm install axios@^1.6.0

# Dev dependencies
npm install -D @types/node
npm install -D sass  # Для Vuetify
```

#### 1.3 Конфигурация Vite
Создать `vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8022',
        changeOrigin: true
      }
    }
  }
})
```

#### 1.4 Конфигурация TypeScript
Обновить `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": false,  // MVP: не строгий режим
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### 1.5 ESLint + Prettier
```bash
npm install -D eslint prettier eslint-plugin-vue @typescript-eslint/parser
npm install -D eslint-config-prettier eslint-plugin-prettier
```

`.eslintrc.cjs`:
```javascript
module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'prettier'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 2020,
    sourceType: 'module'
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'off',  // MVP: разрешаем any
    '@typescript-eslint/no-unused-vars': 'warn',
    'vue/multi-word-component-names': 'off'
  }
}
```

`.prettierrc`:
```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "none",
  "arrowParens": "avoid"
}
```

**Deliverable Day 1:** Проект настроен, dev сервер запускается `npm run dev`

---

### Day 2-3: Структура проекта и Vuetify (4-5 часов)

#### 2.1 Создание структуры папок
```bash
src/
├── assets/           # Статика
├── components/
│   ├── layout/
│   ├── profile/
│   └── common/
├── composables/
├── router/
├── services/
├── stores/
├── types/
├── views/
├── App.vue
├── main.ts
└── plugins/
    └── vuetify.ts
```

Создать скрипт для автоматического создания:
```bash
cd src
mkdir -p components/{layout,profile,common} composables router services stores types views plugins
```

#### 2.2 Настройка Vuetify
`src/plugins/vuetify.ts`:
```typescript
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi
    }
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',    // A101 Blue
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          success: '#4CAF50',
          warning: '#FFC107'
        }
      }
    }
  }
})
```

#### 2.3 Обновление main.ts
`src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import vuetify from './plugins/vuetify'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
```

#### 2.4 Создание базового App.vue
`src/App.vue`:
```vue
<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script setup lang="ts">
// Простой корневой компонент
</script>
```

**Deliverable Day 2-3:** Vuetify настроен, структура проекта создана

---

### Day 4-5: Типы и сервисы (5-6 часов)

#### 3.1 TypeScript типы
`src/types/auth.ts`:
```typescript
export interface User {
  id: number
  username: string
  full_name: string
  title: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface TokenData {
  access_token: string
  expires_at: number
}
```

`src/types/profile.ts`:
```typescript
export interface Position {
  id: string
  name: string
  department: string
  full_path: string
}

export interface Profile {
  id: string
  position_name: string
  department: string
  content: ProfileContent
  metadata: ProfileMetadata
  created_at: string
  updated_at: string
}

export interface ProfileContent {
  position_title: string
  description: string
  responsibilities: string[]
  required_skills: string[]
  qualifications: string[]
  experience_level: string
}

export interface ProfileMetadata {
  model: string
  tokens_used: number
  generation_time: number
  temperature: number
}

export interface GenerationTask {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: Profile
  error?: string
}
```

`src/types/api.ts`:
```typescript
export interface ApiError {
  message: string
  status?: number
  details?: any
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface DashboardStats {
  positions_count: number
  profiles_count: number
  completion_percentage: number
  active_tasks_count: number
}
```

#### 3.2 Axios Configuration
`src/services/api.ts`:
```typescript
import axios, { AxiosError, AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: добавляем JWT токен
api.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor: обрабатываем 401
api.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
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

#### 3.3 Auth Service
`src/services/auth.service.ts`:
```typescript
import api from './api'
import type { LoginRequest, LoginResponse } from '@/types/auth'

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await api.post<LoginResponse>('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/api/auth/logout')
  },

  async getCurrentUser() {
    const response = await api.get('/api/auth/me')
    return response.data
  }
}
```

#### 3.4 Profile Service
`src/services/profile.service.ts`:
```typescript
import api from './api'
import type { Profile, GenerationTask, PaginatedResponse } from '@/types'

export const profileService = {
  async startGeneration(position: string, department: string): Promise<GenerationTask> {
    const response = await api.post('/api/generation/start', {
      position_name: position,
      department
    })
    return response.data
  },

  async getTaskStatus(taskId: string): Promise<GenerationTask> {
    const response = await api.get(`/api/generation/${taskId}/status`)
    return response.data
  },

  async getTaskResult(taskId: string): Promise<Profile> {
    const response = await api.get(`/api/generation/${taskId}/result`)
    return response.data
  },

  async listProfiles(params?: {
    page?: number
    limit?: number
    department?: string
    search?: string
  }): Promise<PaginatedResponse<Profile>> {
    const response = await api.get('/api/profiles', { params })
    return response.data
  },

  async getProfile(id: string): Promise<Profile> {
    const response = await api.get(`/api/profiles/${id}`)
    return response.data
  },

  async downloadJSON(id: string): Promise<Blob> {
    const response = await api.get(`/api/profiles/${id}/download/json`, {
      responseType: 'blob'
    })
    return response.data
  },

  async downloadMarkdown(id: string): Promise<Blob> {
    const response = await api.get(`/api/profiles/${id}/download/md`, {
      responseType: 'blob'
    })
    return response.data
  }
}
```

#### 3.5 Catalog Service
`src/services/catalog.service.ts`:
```typescript
import api from './api'
import type { Position } from '@/types/profile'

export const catalogService = {
  async getPositions(): Promise<Position[]> {
    const response = await api.get('/api/organization/search-items')
    return response.data
  }
}
```

#### 3.6 Dashboard Service
`src/services/dashboard.service.ts`:
```typescript
import api from './api'
import type { DashboardStats } from '@/types/api'

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const response = await api.get('/api/dashboard/stats/minimal')
    return response.data
  }
}
```

**Deliverable Day 4-5:** Все типы и сервисы готовы

---

### Day 6-7: Pinia Stores (3-4 часа)

#### 4.1 Auth Store
`src/stores/auth.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth.service'
import type { User, LoginRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(credentials: LoginRequest) {
    loading.value = true
    error.value = null

    try {
      const response = await authService.login(credentials)
      token.value = response.access_token
      user.value = response.user
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
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
    }
  }

  async function loadUser() {
    if (!token.value) return

    try {
      user.value = await authService.getCurrentUser()
    } catch (err) {
      // Token invalid, clear it
      logout()
    }
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    loadUser
  }
})
```

#### 4.2 Catalog Store
`src/stores/catalog.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { catalogService } from '@/services/catalog.service'
import type { Position } from '@/types/profile'

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const positions = ref<Position[]>([])
  const isLoaded = ref(false)
  const loading = ref(false)

  // Getters
  const positionsCount = computed(() => positions.value.length)

  // Actions
  async function loadPositions() {
    if (isLoaded.value) return // Загружаем только один раз

    loading.value = true
    try {
      positions.value = await catalogService.getPositions()
      isLoaded.value = true
    } catch (err) {
      console.error('Failed to load positions:', err)
    } finally {
      loading.value = false
    }
  }

  function searchPositions(query: string): Position[] {
    if (!query) return []

    const lowerQuery = query.toLowerCase()
    return positions.value.filter(
      p =>
        p.name.toLowerCase().includes(lowerQuery) ||
        p.department.toLowerCase().includes(lowerQuery)
    )
  }

  return {
    positions,
    isLoaded,
    loading,
    positionsCount,
    loadPositions,
    searchPositions
  }
})
```

**Deliverable Day 6-7:** Pinia stores готовы

---

### Day 8-10: Routing & Layout (4-5 часов)

#### 5.1 Router Configuration
`src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue')
        },
        {
          path: 'generator',
          name: 'Generator',
          component: () => import('@/views/GeneratorView.vue')
        },
        {
          path: 'profiles',
          name: 'Profiles',
          component: () => import('@/views/ProfilesView.vue')
        },
        {
          path: 'profiles/:id',
          name: 'ProfileDetail',
          component: () => import('@/views/ProfileDetailView.vue')
        }
      ]
    }
  ]
})

// Route guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
```

#### 5.2 App Layout
`src/components/layout/AppLayout.vue`:
```vue
<template>
  <v-app>
    <app-header />

    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
</script>
```

#### 5.3 App Header
`src/components/layout/AppHeader.vue`:
```vue
<template>
  <v-app-bar color="primary" density="comfortable">
    <v-app-bar-title class="d-flex align-center">
      <v-icon icon="mdi-account-box-outline" class="mr-2" />
      A101 HR Profile Generator
    </v-app-bar-title>

    <v-spacer />

    <v-btn variant="text" to="/" exact>
      <v-icon icon="mdi-view-dashboard" class="mr-1" />
      Dashboard
    </v-btn>

    <v-btn variant="text" to="/generator">
      <v-icon icon="mdi-auto-fix" class="mr-1" />
      Generator
    </v-btn>

    <v-btn variant="text" to="/profiles">
      <v-icon icon="mdi-file-document-multiple" class="mr-1" />
      Profiles
    </v-btn>

    <v-spacer />

    <v-menu v-if="authStore.user">
      <template #activator="{ props }">
        <v-btn v-bind="props" variant="text">
          <v-icon icon="mdi-account-circle" class="mr-1" />
          {{ authStore.user.full_name }}
          <v-icon icon="mdi-menu-down" class="ml-1" />
        </v-btn>
      </template>

      <v-list>
        <v-list-item @click="handleLogout">
          <template #prepend>
            <v-icon icon="mdi-logout" />
          </template>
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
```

**Deliverable Day 8-10:** Routing и layout готовы

---

### Day 11-14: Login Page (3-4 часа)

#### 6.1 Login View
`src/views/LoginView.vue`:
```vue
<template>
  <v-app>
    <v-main>
      <v-container fill-height>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <v-card elevation="8" rounded="lg">
              <v-card-title class="text-h5 text-center pa-6">
                <v-icon icon="mdi-account-box-outline" size="48" color="primary" class="mb-4" />
                <div>A101 HR Profile Generator</div>
              </v-card-title>

              <v-card-text class="pa-6">
                <v-alert v-if="authStore.error" type="error" variant="tonal" class="mb-4">
                  {{ authStore.error }}
                </v-alert>

                <v-form @submit.prevent="handleLogin">
                  <v-text-field
                    v-model="form.username"
                    label="Username"
                    prepend-inner-icon="mdi-account"
                    variant="outlined"
                    :disabled="authStore.loading"
                    autofocus
                    required
                  />

                  <v-text-field
                    v-model="form.password"
                    label="Password"
                    prepend-inner-icon="mdi-lock"
                    :type="showPassword ? 'text' : 'password'"
                    :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                    variant="outlined"
                    :disabled="authStore.loading"
                    required
                    @click:append-inner="showPassword = !showPassword"
                  />

                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    :loading="authStore.loading"
                  >
                    Login
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({
  username: '',
  password: ''
})

const showPassword = ref(false)

const handleLogin = async () => {
  const success = await authStore.login(form.value)
  if (success) {
    router.push('/')
  }
}
</script>
```

**Deliverable Day 11-14:** Login страница полностью работает

---

### Week 1-2 Deliverables (Чек-лист)

По завершении недели 1-2 должно быть:
- [x] Vue.js 3 проект инициализирован с Vite
- [x] TypeScript настроен
- [x] Vuetify установлен и настроен
- [x] ESLint + Prettier настроены
- [x] Структура проекта создана
- [x] Все TypeScript типы определены
- [x] Все API сервисы реализованы
- [x] Pinia stores (auth, catalog) готовы
- [x] Routing настроен с guards
- [x] AppLayout + AppHeader готовы
- [x] Login страница полностью функциональна
- [x] JWT аутентификация работает
- [x] Автоматический редирект на login работает

**Тест Week 1-2:**
```bash
npm run dev
# 1. Открыть http://localhost:5173
# 2. Увидеть редирект на /login
# 3. Ввести credentials
# 4. Успешный логин → редирект на dashboard (пустой пока)
# 5. Нажать Logout → редирект на /login
```

---

## Week 3-4: Core Features

### Week 3: Dashboard View (описание в следующем разделе)
### Week 4: Generator View (описание в следующем разделе)

---

## Следующие шаги

После завершения Week 1-2, я предоставлю детальный план для Week 3-4 (Dashboard + Generator).

**Готовы начать?**

Нужна ли вам помощь с:
1. Инициализацией проекта (`npm create vite`)?
2. Установкой зависимостей?
3. Созданием файлов структуры?

Или вы хотите, чтобы я создал все файлы автоматически с помощью bash скриптов?

# Vue.js 3 Migration Plan - A101 HR Profile Generator

**Document Version:** 1.0.0
**Created:** 2025-10-25
**Target Framework:** Vue.js 3 with TypeScript
**Current Framework:** NiceGUI (Python-based)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Technology Stack Recommendations](#technology-stack-recommendations)
3. [Vue.js Application Architecture](#vuejs-application-architecture)
4. [Migration Strategy](#migration-strategy)
5. [Technical Challenges & Solutions](#technical-challenges--solutions)
6. [Development Environment Setup](#development-environment-setup)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Code Examples & Patterns](#code-examples--patterns)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Considerations](#deployment-considerations)

---

## 1. Executive Summary

### Current State Analysis

**NiceGUI Frontend Issues:**
- 21 Python files, ~4,334 lines of code
- Monolithic component (2,029 lines in single file - 55% of codebase)
- 61 methods in one component violating Single Responsibility Principle
- Direct HTTP calls in UI components (architecture violation)
- No separation between business logic and presentation
- Limited testing capabilities
- Poor scalability and maintainability

**Backend (Already Excellent):**
- FastAPI + Python 3.11+ with async/await
- Well-structured REST API
- JWT authentication
- SQLite database
- OpenRouter (Gemini 2.5 Flash) integration
- Langfuse observability

### Migration Goals

1. **Modern SPA architecture** with proper separation of concerns
2. **Type-safe development** with TypeScript
3. **Reactive state management** with Pinia
4. **Component-based UI** with reusable, testable components
5. **Professional developer experience** with HMR, linting, testing
6. **Improved performance** with lazy loading and code splitting
7. **Better maintainability** with clear architecture patterns

---

## 2. Technology Stack Recommendations

### 2.1 Core Framework

**Vue.js 3.4+ with Composition API**

**Justification:**
- **Composition API** provides better TypeScript support and code organization
- **`<script setup>`** syntax reduces boilerplate (30-40% less code)
- Built-in reactivity system (`ref`, `reactive`, `computed`, `watch`)
- Excellent performance with virtual DOM and tree-shaking
- Large ecosystem and community support
- Easier learning curve compared to React

**Why Composition API over Options API:**
```typescript
// Options API (old) - harder to organize logic
export default {
  data() { return { count: 0 } },
  methods: { increment() { this.count++ } },
  computed: { doubleCount() { return this.count * 2 } }
}

// Composition API (recommended) - logic grouped by feature
import { ref, computed } from 'vue'
export default {
  setup() {
    const count = ref(0)
    const increment = () => count.value++
    const doubleCount = computed(() => count.value * 2)
    return { count, increment, doubleCount }
  }
}

// script setup (best) - most concise
<script setup lang="ts">
import { ref, computed } from 'vue'
const count = ref(0)
const increment = () => count.value++
const doubleCount = computed(() => count.value * 2)
</script>
```

### 2.2 TypeScript Integration

**TypeScript 5.0+** (strongly recommended)

**Benefits:**
- Compile-time type checking prevents 60-70% of runtime errors
- Excellent IDE support (autocomplete, refactoring, navigation)
- Self-documenting code with interfaces and types
- Better refactoring safety
- Enforces consistent API contracts

**Configuration:**
```json
// tsconfig.json
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
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 2.3 State Management

**Pinia 2.1+** (official Vue state management)

**Why Pinia over Vuex:**
- TypeScript support out of the box
- Simpler API (no mutations, actions directly mutate state)
- Modular by design (stores are automatically code-split)
- DevTools integration
- Smaller bundle size (~1KB)

**Example Store:**
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => user.value?.fullName || 'Guest')

  // Actions
  async function login(credentials: LoginCredentials) {
    const response = await apiClient.post('/api/auth/login', credentials)
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('token', token.value)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isAuthenticated, userName, login, logout }
})
```

### 2.4 Router

**Vue Router 4.2+** (official routing solution)

**Features:**
- Nested routes
- Route guards (authentication, authorization)
- Lazy loading
- TypeScript support
- History mode (no hash in URLs)

**Configuration:**
```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/generator',
      name: 'generator',
      component: () => import('@/views/GeneratorView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
```

### 2.5 HTTP Client

**Axios 1.6+** (recommended over Fetch API)

**Why Axios:**
- Automatic JSON transformation
- Request/response interceptors (for auth tokens)
- Better error handling
- Request cancellation
- Progress tracking for file uploads
- Timeout configuration
- Wide browser support

**API Client Setup:**
```typescript
// services/api.ts
import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 2.6 Form Validation

**VeeValidate 4.12+** (recommended)

**Why VeeValidate:**
- Vue 3 native (uses Composition API)
- Built-in validation rules
- Custom validators support
- Yup/Zod schema integration
- Field-level and form-level validation
- TypeScript support

**Alternative:** Vuelidate 2.0 (lighter, more manual)

**Example:**
```typescript
// Form validation with VeeValidate
<script setup lang="ts">
import { useForm } from 'vee-validate'
import * as yup from 'yup'

const schema = yup.object({
  username: yup.string().required('Username is required').min(3),
  password: yup.string().required('Password is required').min(8)
})

const { handleSubmit, errors } = useForm({
  validationSchema: schema
})

const onSubmit = handleSubmit(async (values) => {
  await authStore.login(values)
})
</script>

<template>
  <form @submit="onSubmit">
    <Field name="username" v-slot="{ field, errors }">
      <input v-bind="field" type="text" />
      <span v-if="errors[0]">{{ errors[0] }}</span>
    </Field>
  </form>
</template>
```

### 2.7 UI Component Library

**Vuetify 3.5+** (Material Design) - RECOMMENDED

**Why Vuetify:**
- Material Design 3 components (matches current NiceGUI theme)
- 100+ ready-to-use components
- Excellent TypeScript support
- Built-in accessibility (WCAG 2.1 AA)
- Responsive grid system
- Theming system
- Active maintenance

**Alternative Options:**
- **Element Plus** - Enterprise-focused, good for admin panels
- **Quasar** - Full-featured framework with SSR support
- **Naive UI** - Modern, TypeScript-first
- **PrimeVue** - Enterprise components with themes

**Vuetify Example:**
```vue
<template>
  <v-app>
    <v-navigation-drawer app>
      <v-list>
        <v-list-item to="/">
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app color="primary">
      <v-app-bar-title>HR Profile Generator</v-app-bar-title>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
```

### 2.8 Build Tool

**Vite 5.0+** (strongly recommended over Vue CLI)

**Why Vite:**
- Lightning fast HMR (Hot Module Replacement)
- Native ESM-based dev server
- Optimized production builds with Rollup
- Out-of-the-box TypeScript support
- Plugin ecosystem
- Better performance than Webpack

**Configuration:**
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8033,
    proxy: {
      '/api': {
        target: 'http://localhost:8022',
        changeOrigin: true
      }
    }
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'ui': ['vuetify']
        }
      }
    }
  }
})
```

### 2.9 Code Quality Tools

**ESLint 8.0+ with TypeScript**
```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier'
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    'vue/multi-word-component-names': 'warn',
    '@typescript-eslint/no-unused-vars': 'error'
  }
}
```

**Prettier 3.0+**
```json
// .prettierrc.json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "none",
  "arrowParens": "always"
}
```

### 2.10 Testing Framework

**Vitest 1.0+** (unit testing)
- Vite-native (same config, extremely fast)
- Jest-compatible API
- TypeScript support
- Component testing with Vue Test Utils

**Cypress 13+** or **Playwright** (E2E testing)

---

## 3. Vue.js Application Architecture

### 3.1 Recommended Project Structure

```
frontend-vue/
├── public/                      # Static assets (served as-is)
│   └── favicon.ico
├── src/
│   ├── assets/                  # Build-time assets (images, fonts)
│   │   ├── images/
│   │   └── styles/
│   │       ├── main.scss
│   │       └── variables.scss
│   ├── components/              # Reusable components
│   │   ├── common/              # Generic reusable components
│   │   │   ├── AppButton.vue
│   │   │   ├── AppCard.vue
│   │   │   └── AppInput.vue
│   │   ├── layout/              # Layout components
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   └── AppFooter.vue
│   │   └── profile/             # Feature-specific components
│   │       ├── ProfileCard.vue
│   │       ├── ProfileForm.vue
│   │       └── ProfileSearch.vue
│   ├── composables/             # Composition API reusable logic
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useNotification.ts
│   │   └── useProfileGeneration.ts
│   ├── router/                  # Vue Router configuration
│   │   ├── index.ts
│   │   └── guards.ts
│   ├── services/                # API service layer
│   │   ├── api.ts               # Axios instance
│   │   ├── auth.service.ts
│   │   ├── catalog.service.ts
│   │   ├── generation.service.ts
│   │   └── profile.service.ts
│   ├── stores/                  # Pinia stores
│   │   ├── auth.ts
│   │   ├── catalog.ts
│   │   ├── generation.ts
│   │   └── profile.ts
│   ├── types/                   # TypeScript type definitions
│   │   ├── api.types.ts
│   │   ├── auth.types.ts
│   │   ├── generation.types.ts
│   │   └── profile.types.ts
│   ├── utils/                   # Utility functions
│   │   ├── format.ts
│   │   ├── validation.ts
│   │   └── constants.ts
│   ├── views/                   # Page-level components (routes)
│   │   ├── HomeView.vue
│   │   ├── LoginView.vue
│   │   ├── GeneratorView.vue
│   │   ├── ProfilesView.vue
│   │   └── AnalyticsView.vue
│   ├── App.vue                  # Root component
│   └── main.ts                  # Application entry point
├── tests/
│   ├── unit/                    # Unit tests (Vitest)
│   │   ├── components/
│   │   └── services/
│   └── e2e/                     # End-to-end tests (Cypress)
│       └── specs/
├── .env.development             # Development environment variables
├── .env.production              # Production environment variables
├── .eslintrc.cjs                # ESLint configuration
├── .prettierrc.json             # Prettier configuration
├── index.html                   # HTML entry point
├── package.json                 # npm dependencies
├── tsconfig.json                # TypeScript configuration
├── vite.config.ts               # Vite configuration
└── vitest.config.ts             # Vitest configuration
```

### 3.2 Component Architecture Patterns

**Component Hierarchy:**

```
App.vue (Root)
├── AppLayout.vue (Layout wrapper)
│   ├── AppHeader.vue
│   │   ├── UserMenu.vue
│   │   └── NotificationBell.vue
│   ├── AppSidebar.vue
│   │   └── NavigationMenu.vue
│   └── RouterView (Page content)
│       ├── HomeView.vue
│       │   ├── DashboardStats.vue
│       │   └── QuickActions.vue
│       ├── GeneratorView.vue
│       │   ├── ProfileSearch.vue
│       │   │   ├── SearchInput.vue
│       │   │   └── SearchResults.vue
│       │   ├── ProfileForm.vue
│       │   │   └── FormField.vue (multiple)
│       │   └── GenerationProgress.vue
│       └── ProfilesView.vue
│           ├── ProfileList.vue
│           ├── ProfileCard.vue
│           └── ProfileFilters.vue
```

**Component Design Principles:**

1. **Single Responsibility** - Each component does ONE thing well
2. **Props Down, Events Up** - Parent controls children via props, children notify via events
3. **Composition over Inheritance** - Use composables for shared logic
4. **Presentational vs Container** - Separate data fetching from presentation

**Example - Presentational Component:**
```vue
<!-- components/profile/ProfileCard.vue -->
<script setup lang="ts">
import type { Profile } from '@/types'

interface Props {
  profile: Profile
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  view: [id: string]
  download: [id: string, format: 'json' | 'md' | 'docx']
  delete: [id: string]
}>()
</script>

<template>
  <v-card :loading="loading">
    <v-card-title>{{ profile.position }}</v-card-title>
    <v-card-subtitle>{{ profile.department }}</v-card-subtitle>
    <v-card-text>
      <p>Created: {{ new Date(profile.createdAt).toLocaleDateString() }}</p>
    </v-card-text>
    <v-card-actions>
      <v-btn @click="emit('view', profile.id)">View</v-btn>
      <v-btn @click="emit('download', profile.id, 'json')">Download</v-btn>
      <v-btn color="error" @click="emit('delete', profile.id)">Delete</v-btn>
    </v-card-actions>
  </v-card>
</template>
```

**Example - Container Component:**
```vue
<!-- views/ProfilesView.vue -->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useProfileStore } from '@/stores/profile'
import ProfileCard from '@/components/profile/ProfileCard.vue'

const profileStore = useProfileStore()

onMounted(() => {
  profileStore.fetchProfiles()
})

const handleView = (id: string) => {
  profileStore.viewProfile(id)
}

const handleDownload = async (id: string, format: string) => {
  await profileStore.downloadProfile(id, format)
}
</script>

<template>
  <div class="profiles-view">
    <h1>All Profiles</h1>
    <div class="profile-grid">
      <ProfileCard
        v-for="profile in profileStore.profiles"
        :key="profile.id"
        :profile="profile"
        :loading="profileStore.loading"
        @view="handleView"
        @download="handleDownload"
      />
    </div>
  </div>
</template>
```

### 3.3 State Management Patterns

**Store Organization by Feature:**

```typescript
// stores/generation.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GenerationTask, GenerationRequest } from '@/types'
import generationService from '@/services/generation.service'

export const useGenerationStore = defineStore('generation', () => {
  // State
  const currentTask = ref<GenerationTask | null>(null)
  const taskHistory = ref<GenerationTask[]>([])
  const polling = ref(false)

  // Getters
  const isGenerating = computed(() =>
    currentTask.value?.status === 'processing' || currentTask.value?.status === 'queued'
  )

  const progress = computed(() => currentTask.value?.progress || 0)

  // Actions
  async function startGeneration(request: GenerationRequest) {
    try {
      const response = await generationService.start(request)
      currentTask.value = {
        taskId: response.task_id,
        status: response.status,
        progress: 0,
        createdAt: new Date()
      }

      // Start polling
      pollTaskStatus(response.task_id)
    } catch (error) {
      console.error('Failed to start generation:', error)
      throw error
    }
  }

  async function pollTaskStatus(taskId: string) {
    if (polling.value) return

    polling.value = true

    const pollInterval = setInterval(async () => {
      try {
        const status = await generationService.getStatus(taskId)
        currentTask.value = status.task

        if (status.task.status === 'completed' || status.task.status === 'failed') {
          clearInterval(pollInterval)
          polling.value = false

          if (status.task.status === 'completed') {
            taskHistory.value.unshift(currentTask.value)
          }
        }
      } catch (error) {
        console.error('Polling error:', error)
        clearInterval(pollInterval)
        polling.value = false
      }
    }, 2000) // Poll every 2 seconds
  }

  async function cancelGeneration(taskId: string) {
    await generationService.cancel(taskId)
    if (currentTask.value?.taskId === taskId) {
      currentTask.value.status = 'cancelled'
    }
    polling.value = false
  }

  function clearCurrentTask() {
    currentTask.value = null
  }

  return {
    // State
    currentTask,
    taskHistory,
    polling,
    // Getters
    isGenerating,
    progress,
    // Actions
    startGeneration,
    pollTaskStatus,
    cancelGeneration,
    clearCurrentTask
  }
})
```

### 3.4 API Service Layer Design

**Centralized API client with typed services:**

```typescript
// services/generation.service.ts
import apiClient from './api'
import type {
  GenerationRequest,
  GenerationResponse,
  TaskStatusResponse
} from '@/types'

class GenerationService {
  async start(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await apiClient.post<GenerationResponse>(
      '/api/generation/start',
      request
    )
    return response.data
  }

  async getStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await apiClient.get<TaskStatusResponse>(
      `/api/generation/${taskId}/status`
    )
    return response.data
  }

  async cancel(taskId: string): Promise<void> {
    await apiClient.delete(`/api/generation/${taskId}`)
  }

  async getResult(taskId: string): Promise<any> {
    const response = await apiClient.get(`/api/generation/${taskId}/result`)
    return response.data
  }
}

export default new GenerationService()
```

### 3.5 Composables (Reusable Logic)

**Composition API allows extracting and reusing logic:**

```typescript
// composables/useProfileGeneration.ts
import { ref, computed } from 'vue'
import { useGenerationStore } from '@/stores/generation'
import { useNotification } from './useNotification'
import type { GenerationRequest } from '@/types'

export function useProfileGeneration() {
  const generationStore = useGenerationStore()
  const { showSuccess, showError } = useNotification()

  const formData = ref<GenerationRequest>({
    department: '',
    position: '',
    employee_name: '',
    temperature: 0.1,
    save_result: true
  })

  const isValid = computed(() =>
    formData.value.department && formData.value.position
  )

  async function startGeneration() {
    if (!isValid.value) {
      showError('Please fill in all required fields')
      return
    }

    try {
      await generationStore.startGeneration(formData.value)
      showSuccess('Profile generation started')
    } catch (error) {
      showError('Failed to start generation')
    }
  }

  function reset() {
    formData.value = {
      department: '',
      position: '',
      employee_name: '',
      temperature: 0.1,
      save_result: true
    }
  }

  return {
    formData,
    isValid,
    startGeneration,
    reset,
    task: computed(() => generationStore.currentTask),
    progress: computed(() => generationStore.progress),
    isGenerating: computed(() => generationStore.isGenerating)
  }
}
```

**Usage in Component:**
```vue
<script setup lang="ts">
import { useProfileGeneration } from '@/composables/useProfileGeneration'

const {
  formData,
  isValid,
  startGeneration,
  reset,
  task,
  progress,
  isGenerating
} = useProfileGeneration()
</script>

<template>
  <v-form @submit.prevent="startGeneration">
    <v-text-field
      v-model="formData.department"
      label="Department"
      required
    />
    <v-text-field
      v-model="formData.position"
      label="Position"
      required
    />
    <v-btn
      type="submit"
      :disabled="!isValid || isGenerating"
      :loading="isGenerating"
    >
      Generate Profile
    </v-btn>

    <v-progress-linear
      v-if="isGenerating"
      :model-value="progress"
      height="25"
    >
      {{ progress }}%
    </v-progress-linear>
  </v-form>
</template>
```

---

## 4. Migration Strategy

### 4.1 Migration Approach

**RECOMMENDED: Gradual Migration (Hybrid Approach)**

**Phase 1: New Vue.js Frontend (Parallel Development)**
- Build new Vue.js frontend alongside existing NiceGUI
- Both frontends connect to same FastAPI backend
- Test and iterate without disrupting current system
- Deploy Vue.js frontend to different port (8034)

**Phase 2: Feature Parity**
- Implement all existing features in Vue.js
- Add improvements and missing functionality
- Run both systems in parallel for testing

**Phase 3: Switch & Deprecate**
- Switch production traffic to Vue.js frontend
- Keep NiceGUI as fallback for 2-4 weeks
- Monitor for issues
- Fully deprecate NiceGUI

**Alternative: Full Rewrite (NOT Recommended)**
- Risk of extended downtime
- All features must be ready before deployment
- Harder to test incrementally

### 4.2 Phase-by-Phase Plan

#### **Phase 1: Setup & Infrastructure (Week 1-2)**

**Goals:**
- Project scaffolding
- Development environment
- CI/CD pipeline
- Core architecture

**Tasks:**
1. Initialize Vue.js project with Vite
2. Setup TypeScript configuration
3. Install and configure dependencies (Vuetify, Pinia, Vue Router, Axios)
4. Create project structure
5. Setup ESLint, Prettier
6. Configure Vitest for testing
7. Create base components (AppLayout, AppHeader, AppButton, etc.)
8. Setup API client and interceptors
9. Configure environment variables (.env files)
10. Docker configuration for Vue.js frontend

**Deliverables:**
- Working Vue.js development environment
- Login page functional
- Basic routing
- API authentication working

#### **Phase 2: Core Components & Routing (Week 3-4)**

**Goals:**
- Implement main pages
- Build reusable components
- Setup state management

**Tasks:**
1. **Authentication Flow**
   - Login view with form validation
   - Auth store (Pinia)
   - Route guards
   - Token management

2. **Dashboard/Home View**
   - Stats cards component
   - Quick actions
   - Navigation

3. **Layout Components**
   - App header with user menu
   - Sidebar navigation
   - Footer

4. **Reusable Components**
   - Buttons, inputs, cards
   - Loading spinners
   - Error boundaries
   - Notifications/toasts

**Deliverables:**
- Complete authentication flow
- Home dashboard
- Navigation between pages
- Reusable component library

#### **Phase 3: Feature Implementation (Week 5-8)**

**Goals:**
- Profile generation interface
- Search functionality
- File management

**Tasks:**
1. **Profile Generator Page**
   - Position search component (4,376 positions)
   - Autocomplete with hierarchical suggestions
   - Generation form
   - Progress tracking
   - Result display

2. **Search Component**
   - Fuzzy search implementation
   - Department/position filtering
   - Contextual display names
   - Selection handling

3. **Generation Management**
   - Start generation
   - Poll task status
   - Cancel generation
   - View results
   - Download files (JSON, MD, DOCX, XLSX)

4. **Profiles List View**
   - Table/grid of all profiles
   - Filtering and sorting
   - Pagination
   - Bulk actions

**Deliverables:**
- Fully functional profile generator
- Search with 4,376 positions
- File download/export
- Profile management

#### **Phase 4: Testing & Optimization (Week 9-10)**

**Goals:**
- Comprehensive testing
- Performance optimization
- Bug fixes

**Tasks:**
1. **Unit Tests**
   - Component tests (Vitest + Vue Test Utils)
   - Store tests
   - Service tests
   - Utility function tests

2. **E2E Tests**
   - User journey tests (Cypress/Playwright)
   - Critical path testing

3. **Performance Optimization**
   - Code splitting
   - Lazy loading routes
   - Image optimization
   - Bundle size analysis
   - Lighthouse audit

4. **Accessibility**
   - WCAG 2.1 AA compliance
   - Keyboard navigation
   - Screen reader testing
   - ARIA labels

**Deliverables:**
- 80%+ test coverage
- Performance score 90+ (Lighthouse)
- Accessibility compliant
- Production-ready build

---

## 5. Technical Challenges & Solutions

### 5.1 Challenge: API Integration Patterns

**Problem:** Current NiceGUI has direct HTTP calls in components

**Solution:** Service Layer Pattern

```typescript
// BAD (NiceGUI pattern)
async def download_profile(profile_id: str):
    headers = api_client.get_auth_headers()
    response = httpx.get(f"{base_url}/api/profiles/{profile_id}/download/md")

// GOOD (Vue.js pattern)
// services/profile.service.ts
class ProfileService {
  async downloadMarkdown(profileId: string): Promise<Blob> {
    const response = await apiClient.get(
      `/api/profiles/${profileId}/download/md`,
      { responseType: 'blob' }
    )
    return response.data
  }
}

// Usage in component
const handleDownload = async (id: string) => {
  try {
    const blob = await profileService.downloadMarkdown(id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `profile-${id}.md`
    link.click()
  } catch (error) {
    showError('Failed to download profile')
  }
}
```

### 5.2 Challenge: File Upload/Download Handling

**Solution: Blob Handling with Progress**

```typescript
// File download with progress
import { ref } from 'vue'

export function useFileDownload() {
  const progress = ref(0)
  const downloading = ref(false)

  async function downloadFile(
    url: string,
    filename: string,
    format: 'json' | 'md' | 'docx' | 'xlsx'
  ) {
    downloading.value = true
    progress.value = 0

    try {
      const response = await apiClient.get(url, {
        responseType: 'blob',
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            progress.value = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
          }
        }
      })

      const blob = new Blob([response.data])
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = `${filename}.${format}`
      link.click()
      window.URL.revokeObjectURL(link.href)
    } finally {
      downloading.value = false
      progress.value = 0
    }
  }

  return { downloadFile, progress, downloading }
}
```

### 5.3 Challenge: Real-time Updates (Task Status Polling)

**Solution: Polling with Auto-cleanup**

```typescript
// composables/useTaskPolling.ts
import { ref, onUnmounted } from 'vue'
import type { GenerationTask } from '@/types'

export function useTaskPolling() {
  const task = ref<GenerationTask | null>(null)
  const polling = ref(false)
  let intervalId: number | null = null

  async function startPolling(
    taskId: string,
    pollFn: (id: string) => Promise<GenerationTask>,
    interval = 2000
  ) {
    if (polling.value) return

    polling.value = true

    intervalId = window.setInterval(async () => {
      try {
        task.value = await pollFn(taskId)

        if (task.value.status === 'completed' || task.value.status === 'failed') {
          stopPolling()
        }
      } catch (error) {
        console.error('Polling error:', error)
        stopPolling()
      }
    }, interval)
  }

  function stopPolling() {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
    polling.value = false
  }

  // Auto-cleanup on component unmount
  onUnmounted(() => {
    stopPolling()
  })

  return { task, polling, startPolling, stopPolling }
}
```

### 5.4 Challenge: Export Functionality (DOCX, XLSX Generation)

**Solution: Client-side and Server-side Options**

**Option 1: Server-side (Current - Keep)**
```typescript
// Let backend handle complex document generation
async function exportProfile(id: string, format: 'docx' | 'xlsx') {
  const response = await apiClient.get(
    `/api/profiles/${id}/export/${format}`,
    { responseType: 'blob' }
  )
  // Download blob
}
```

**Option 2: Client-side (Future Enhancement)**
```typescript
// For simple exports, generate client-side
import { Document, Packer, Paragraph } from 'docx'
import { saveAs } from 'file-saver'

async function generateDocx(profile: Profile) {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        new Paragraph({
          text: profile.position,
          heading: 'Heading1'
        }),
        // ... more content
      ]
    }]
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, `profile-${profile.id}.docx`)
}
```

### 5.5 Challenge: Form Complexity (4,376 Position Search)

**Solution: Virtualized Autocomplete**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCatalogStore } from '@/stores/catalog'

const catalogStore = useCatalogStore()
const searchQuery = ref('')
const selectedPosition = ref(null)

// Fuzzy search with ranking
const filteredPositions = computed(() => {
  if (!searchQuery.value) return catalogStore.recentPositions

  const query = searchQuery.value.toLowerCase()

  return catalogStore.positions
    .filter(pos =>
      pos.name.toLowerCase().includes(query) ||
      pos.department.toLowerCase().includes(query)
    )
    .slice(0, 100) // Limit to 100 results for performance
    .sort((a, b) => {
      // Rank by relevance
      const aScore = a.name.toLowerCase().indexOf(query)
      const bScore = b.name.toLowerCase().indexOf(query)
      return aScore - bScore
    })
})
</script>

<template>
  <v-autocomplete
    v-model="selectedPosition"
    v-model:search="searchQuery"
    :items="filteredPositions"
    item-title="displayName"
    item-value="id"
    label="Search position (4,376 available)"
    placeholder="Start typing department or position name..."
    clearable
    no-filter
    :custom-filter="() => true"
  >
    <template #item="{ props, item }">
      <v-list-item v-bind="props">
        <template #prepend>
          <v-icon>mdi-briefcase</v-icon>
        </template>
        <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ item.raw.department }}</v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>
```

### 5.6 Challenge: Authentication Flow

**Solution: JWT Token Management with Refresh**

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth.service'
import type { User, LoginCredentials } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: LoginCredentials) {
    const response = await authService.login(credentials)

    token.value = response.access_token
    refreshToken.value = response.refresh_token
    user.value = response.user

    localStorage.setItem('token', token.value)
    localStorage.setItem('refreshToken', refreshToken.value)
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      logout()
      return
    }

    try {
      const response = await authService.refresh(refreshToken.value)
      token.value = response.access_token
      localStorage.setItem('token', token.value)
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    refreshAccessToken,
    logout
  }
})

// Auto-refresh on 401
apiClient.interceptors.response.use(
  response => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const authStore = useAuthStore()

      try {
        await authStore.refreshAccessToken()
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        authStore.logout()
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)
```

---

## 6. Development Environment Setup

### 6.1 System Requirements

- **Node.js:** 18.0+ (LTS recommended: 20.x)
- **npm:** 9.0+ or **pnpm:** 8.0+ (faster, recommended)
- **Git:** 2.30+
- **Code Editor:** VS Code (recommended with extensions)

### 6.2 VS Code Extensions

Essential:
- **Volar** (Vue Language Features)
- **TypeScript Vue Plugin (Volar)**
- **ESLint**
- **Prettier - Code formatter**
- **Path Intellisense**

Recommended:
- **Auto Rename Tag**
- **GitLens**
- **Error Lens**
- **Material Icon Theme**

### 6.3 Initial Project Setup

```bash
# Navigate to project root
cd /home/yan/A101/HR

# Create Vue.js frontend directory
mkdir frontend-vue
cd frontend-vue

# Initialize Vue project with Vite
npm create vite@latest . -- --template vue-ts

# Install dependencies
npm install

# Install additional packages
npm install -D @types/node

# Install UI framework (Vuetify)
npm install vuetify@^3.5.0
npm install @mdi/font

# Install router and state management
npm install vue-router@4 pinia

# Install HTTP client
npm install axios

# Install form validation
npm install vee-validate yup
npm install @vee-validate/yup

# Install testing tools
npm install -D vitest @vue/test-utils happy-dom
npm install -D @vitest/ui

# Install linting and formatting
npm install -D eslint @vue/eslint-config-typescript @vue/eslint-config-prettier
npm install -D prettier eslint-plugin-vue

# Install date utilities (optional but useful)
npm install date-fns

# Install file download helpers
npm install file-saver
npm install -D @types/file-saver
```

### 6.4 Environment Configuration

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8022
VITE_APP_TITLE=HR Profile Generator - Development

# .env.production
VITE_API_BASE_URL=https://api.your-domain.com
VITE_APP_TITLE=HR Profile Generator
```

### 6.5 package.json Scripts

```json
{
  "name": "hr-profile-generator-vue",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --port 8034",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "vuetify": "^3.5.0",
    "axios": "^1.6.0",
    "vee-validate": "^4.12.0",
    "yup": "^1.3.0",
    "@mdi/font": "^7.4.0",
    "date-fns": "^3.0.0",
    "file-saver": "^2.0.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.0",
    "@vitest/ui": "^1.0.0",
    "vitest": "^1.0.0",
    "happy-dom": "^12.10.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "vite": "^5.0.0",
    "@types/node": "^20.10.0",
    "@types/file-saver": "^2.0.7",
    "eslint": "^8.55.0",
    "eslint-plugin-vue": "^9.19.0",
    "@vue/eslint-config-typescript": "^12.0.0",
    "@vue/eslint-config-prettier": "^9.0.0",
    "prettier": "^3.1.0"
  }
}
```

### 6.6 Docker Configuration

```dockerfile
# frontend-vue/Dockerfile
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# frontend-vue/nginx.conf
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # API proxy
    location /api {
        proxy_pass http://backend:8022;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```yaml
# docker-compose.yml (add to existing)
services:
  frontend-vue:
    build:
      context: ./frontend-vue
      dockerfile: Dockerfile
    ports:
      - "8034:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:8022
    networks:
      - hr-network
```

---

## 7. Implementation Roadmap

### Week 1-2: Foundation

- [ ] Initialize Vue.js project with Vite
- [ ] Configure TypeScript, ESLint, Prettier
- [ ] Setup Vuetify and theme
- [ ] Create project structure
- [ ] Configure Pinia stores
- [ ] Setup Vue Router with guards
- [ ] Create API client with Axios
- [ ] Implement authentication flow
- [ ] Build base layout components
- [ ] Docker configuration

**Milestone 1:** Login works, basic routing functional

### Week 3-4: Core Features

- [ ] Home dashboard view
- [ ] Stats components
- [ ] Navigation menu
- [ ] User menu and profile
- [ ] Notification system
- [ ] Error handling
- [ ] Loading states

**Milestone 2:** Dashboard complete with navigation

### Week 5-6: Profile Generator

- [ ] Position search component
- [ ] Autocomplete with 4,376 positions
- [ ] Fuzzy search implementation
- [ ] Generation form
- [ ] Form validation
- [ ] Start generation
- [ ] Progress tracking
- [ ] Task status polling

**Milestone 3:** Can generate profiles end-to-end

### Week 7-8: Profile Management

- [ ] Profiles list view
- [ ] Profile card component
- [ ] Filtering and sorting
- [ ] Pagination
- [ ] View profile details
- [ ] Download files (JSON, MD, DOCX, XLSX)
- [ ] Delete profiles
- [ ] Bulk actions

**Milestone 4:** Complete profile management

### Week 9-10: Testing & Polish

- [ ] Unit tests for components
- [ ] Unit tests for stores
- [ ] Unit tests for services
- [ ] E2E tests for critical paths
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Bug fixes
- [ ] Documentation

**Milestone 5:** Production-ready

---

## 8. Code Examples & Patterns

### 8.1 Complete Component Example

```vue
<!-- views/GeneratorView.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useGenerationStore } from '@/stores/generation'
import { useNotification } from '@/composables/useNotification'
import ProfileSearch from '@/components/profile/ProfileSearch.vue'
import GenerationForm from '@/components/profile/GenerationForm.vue'
import GenerationProgress from '@/components/profile/GenerationProgress.vue'
import type { Position, GenerationRequest } from '@/types'

const router = useRouter()
const catalogStore = useCatalogStore()
const generationStore = useGenerationStore()
const { showSuccess, showError } = useNotification()

const selectedPosition = ref<Position | null>(null)
const formData = ref<GenerationRequest>({
  department: '',
  position: '',
  employee_name: '',
  temperature: 0.1,
  save_result: true
})

const isValid = computed(() =>
  formData.value.department && formData.value.position
)

onMounted(async () => {
  if (!catalogStore.isLoaded) {
    await catalogStore.loadCatalog()
  }
})

const handlePositionSelect = (position: Position) => {
  selectedPosition.value = position
  formData.value.department = position.department
  formData.value.position = position.name
}

const handleGenerate = async () => {
  if (!isValid.value) {
    showError('Please select a position')
    return
  }

  try {
    await generationStore.startGeneration(formData.value)
    showSuccess('Profile generation started')
  } catch (error) {
    showError('Failed to start generation')
  }
}

const handleCancel = async () => {
  if (generationStore.currentTask) {
    await generationStore.cancelGeneration(generationStore.currentTask.taskId)
    showSuccess('Generation cancelled')
  }
}

const handleViewResult = () => {
  if (generationStore.currentTask) {
    router.push(`/profiles/${generationStore.currentTask.taskId}`)
  }
}
</script>

<template>
  <div class="generator-view">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Profile Generator</h1>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Search Position</v-card-title>
            <v-card-text>
              <ProfileSearch
                :positions="catalogStore.positions"
                @select="handlePositionSelect"
              />

              <v-divider class="my-4" />

              <GenerationForm
                v-model="formData"
                :disabled="generationStore.isGenerating"
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn
                color="primary"
                :disabled="!isValid || generationStore.isGenerating"
                :loading="generationStore.isGenerating"
                @click="handleGenerate"
              >
                Generate Profile
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <GenerationProgress
            v-if="generationStore.currentTask"
            :task="generationStore.currentTask"
            @cancel="handleCancel"
            @view-result="handleViewResult"
          />

          <v-card v-else>
            <v-card-text class="text-center py-8">
              <v-icon size="64" color="grey">mdi-file-document-outline</v-icon>
              <p class="text-h6 mt-4">No active generation</p>
              <p class="text-body-2 text-grey">
                Select a position and click Generate to start
              </p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped>
.generator-view {
  min-height: calc(100vh - 64px);
  background-color: #f5f5f5;
}
</style>
```

### 8.2 Type Definitions

```typescript
// types/generation.types.ts
export interface GenerationRequest {
  department: string
  position: string
  employee_name?: string
  temperature: number
  save_result: boolean
}

export interface GenerationResponse {
  task_id: string
  status: TaskStatus
  message: string
  estimated_duration?: number
}

export type TaskStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'

export interface GenerationTask {
  taskId: string
  status: TaskStatus
  progress?: number
  createdAt: Date
  startedAt?: Date
  completedAt?: Date
  estimatedDuration?: number
  currentStep?: string
  errorMessage?: string
}

export interface TaskStatusResponse {
  task: GenerationTask
  result?: ProfileResult
}

export interface ProfileResult {
  id: string
  department: string
  position: string
  employee_name?: string
  profile_data: any
  created_at: string
}

// types/catalog.types.ts
export interface Position {
  id: string
  name: string
  department: string
  level: string
  displayName: string
}

export interface Department {
  id: string
  name: string
  parent?: string
}

// types/auth.types.ts
export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface User {
  id: number
  username: string
  fullName: string
  role: UserRole
}

export type UserRole = 'admin' | 'hr' | 'user'
```

### 8.3 Testing Examples

```typescript
// tests/unit/components/ProfileSearch.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import ProfileSearch from '@/components/profile/ProfileSearch.vue'

const vuetify = createVuetify({ components, directives })

describe('ProfileSearch', () => {
  const mockPositions = [
    {
      id: '1',
      name: 'Software Engineer',
      department: 'IT',
      level: 'Middle',
      displayName: 'IT - Software Engineer (Middle)'
    },
    {
      id: '2',
      name: 'HR Manager',
      department: 'HR',
      level: 'Senior',
      displayName: 'HR - HR Manager (Senior)'
    }
  ]

  it('renders search input', () => {
    const wrapper = mount(ProfileSearch, {
      props: { positions: mockPositions },
      global: {
        plugins: [vuetify]
      }
    })

    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('filters positions based on search query', async () => {
    const wrapper = mount(ProfileSearch, {
      props: { positions: mockPositions },
      global: {
        plugins: [vuetify]
      }
    })

    const input = wrapper.find('input')
    await input.setValue('software')

    // Verify filtered results
    expect(wrapper.vm.filteredPositions).toHaveLength(1)
    expect(wrapper.vm.filteredPositions[0].name).toBe('Software Engineer')
  })

  it('emits select event when position is chosen', async () => {
    const wrapper = mount(ProfileSearch, {
      props: { positions: mockPositions },
      global: {
        plugins: [vuetify]
      }
    })

    await wrapper.vm.handleSelect(mockPositions[0])

    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0]).toEqual([mockPositions[0]])
  })
})

// tests/unit/stores/generation.spec.ts
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useGenerationStore } from '@/stores/generation'
import generationService from '@/services/generation.service'

vi.mock('@/services/generation.service')

describe('Generation Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('starts generation successfully', async () => {
    const store = useGenerationStore()
    const mockResponse = {
      task_id: 'test-123',
      status: 'queued',
      message: 'Started'
    }

    vi.mocked(generationService.start).mockResolvedValue(mockResponse)

    await store.startGeneration({
      department: 'IT',
      position: 'Software Engineer',
      temperature: 0.1,
      save_result: true
    })

    expect(store.currentTask).toBeTruthy()
    expect(store.currentTask?.taskId).toBe('test-123')
  })

  it('polls task status until completion', async () => {
    const store = useGenerationStore()

    const mockStatuses = [
      { task: { taskId: '123', status: 'processing', progress: 50 } },
      { task: { taskId: '123', status: 'completed', progress: 100 } }
    ]

    let callCount = 0
    vi.mocked(generationService.getStatus).mockImplementation(async () => {
      return mockStatuses[callCount++]
    })

    await store.pollTaskStatus('123')

    // Wait for polling to complete
    await new Promise(resolve => setTimeout(resolve, 5000))

    expect(store.currentTask?.status).toBe('completed')
    expect(store.polling).toBe(false)
  })
})
```

---

## 9. Testing Strategy

### 9.1 Test Coverage Goals

- **Unit Tests:** 80%+ coverage
- **Integration Tests:** All API services
- **E2E Tests:** Critical user journeys

### 9.2 Testing Pyramid

```
           /\
          /  \         E2E Tests (10%)
         /    \        - User login flow
        /------\       - Generate profile end-to-end
       /        \      - Download profile
      /          \
     /------------\    Integration Tests (20%)
    /              \   - API service tests
   /                \  - Store integration
  /------------------\
 /                    \ Unit Tests (70%)
/______________________\ - Component logic
                        - Utility functions
                        - Composables
```

### 9.3 Vitest Configuration

```typescript
// vitest.config.ts
import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'happy-dom',
      exclude: [...configDefaults.exclude, 'e2e/*'],
      root: fileURLToPath(new URL('./', import.meta.url)),
      coverage: {
        reporter: ['text', 'json', 'html'],
        exclude: [
          'node_modules/',
          'tests/',
          '**/*.spec.ts',
          '**/*.config.ts'
        ]
      }
    }
  })
)
```

### 9.4 E2E Testing with Cypress

```typescript
// cypress/e2e/profile-generation.cy.ts
describe('Profile Generation Flow', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.login('admin', 'password') // Custom command
  })

  it('generates profile successfully', () => {
    // Navigate to generator
    cy.get('[data-cy=nav-generator]').click()
    cy.url().should('include', '/generator')

    // Search and select position
    cy.get('[data-cy=position-search]').type('Software Engineer')
    cy.get('[data-cy=search-result]').first().click()

    // Verify form populated
    cy.get('[data-cy=department-field]').should('have.value', 'IT')
    cy.get('[data-cy=position-field]').should('have.value', 'Software Engineer')

    // Start generation
    cy.get('[data-cy=generate-btn]').click()

    // Wait for completion
    cy.get('[data-cy=progress-bar]', { timeout: 60000 })
      .should('have.attr', 'aria-valuenow', '100')

    // Verify success
    cy.get('[data-cy=success-message]').should('be.visible')

    // Download profile
    cy.get('[data-cy=download-json]').click()

    // Verify file downloaded
    cy.readFile('cypress/downloads/profile.json').should('exist')
  })
})
```

---

## 10. Deployment Considerations

### 10.1 Production Build

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview
```

### 10.2 Environment Variables

```bash
# .env.production
VITE_API_BASE_URL=https://api.production.com
VITE_APP_TITLE=HR Profile Generator
```

### 10.3 Nginx Production Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name hr-profiles.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    root /var/www/hr-frontend/dist;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # API proxy
    location /api {
        proxy_pass http://backend:8022;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Static assets with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 10.4 Performance Optimizations

**Code Splitting:**
```typescript
// router/index.ts - Lazy load routes
const routes = [
  {
    path: '/generator',
    component: () => import('@/views/GeneratorView.vue') // Lazy loaded
  }
]
```

**Tree Shaking:**
```typescript
// Import only what you need
import { ref, computed } from 'vue' // Good
import * as Vue from 'vue' // Bad - imports everything
```

**Bundle Analysis:**
```bash
npm install -D rollup-plugin-visualizer

# Add to vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({ open: true })
  ]
})
```

### 10.5 Docker Multi-stage Build

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## Summary

This migration plan provides a comprehensive roadmap to migrate from NiceGUI to Vue.js 3. The recommended approach:

1. **Use Vue.js 3 with Composition API** for modern, type-safe development
2. **TypeScript** for compile-time safety and better DX
3. **Pinia** for state management (simpler than Vuex)
4. **Vuetify 3** for Material Design components (matches current theme)
5. **Vite** for fast development and optimized builds
6. **Axios** for HTTP with interceptors
7. **VeeValidate** for form validation
8. **Vitest** for unit testing

**Timeline:** 10 weeks to production-ready Vue.js frontend
**Architecture:** Clean separation of concerns with services, stores, and components
**Result:** Maintainable, testable, scalable modern SPA

---

**Next Steps:**
1. Review and approve this plan
2. Initialize Vue.js project
3. Begin Phase 1 implementation
4. Parallel development with NiceGUI
5. Gradual migration and testing

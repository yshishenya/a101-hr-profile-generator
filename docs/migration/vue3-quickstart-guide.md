# Vue.js 3 Quick Start Guide - A101 HR Profile Generator

**Purpose:** Step-by-step guide to start Vue.js 3 development immediately
**Time to First Component:** ~30 minutes
**Prerequisites:** Node.js 18+, npm 9+, Git

---

## Quick Navigation

- [1. Project Initialization (5 min)](#1-project-initialization)
- [2. Install Dependencies (3 min)](#2-install-dependencies)
- [3. Project Structure Setup (5 min)](#3-project-structure-setup)
- [4. Configuration Files (5 min)](#4-configuration-files)
- [5. First Component (10 min)](#5-first-component)
- [6. Run Development Server (2 min)](#6-run-development-server)
- [Next Steps](#next-steps)

---

## 1. Project Initialization

```bash
# Navigate to project root
cd /home/yan/A101/HR

# Create Vue.js frontend directory
mkdir frontend-vue
cd frontend-vue

# Initialize Vue 3 project with TypeScript template
npm create vite@latest . -- --template vue-ts

# Answer prompts:
# - Project name: frontend-vue (already set)
# - Select a framework: Vue
# - Select a variant: TypeScript
```

**What this does:**
- Creates a new Vue 3 + TypeScript project using Vite
- Sets up base configuration files
- Creates initial project structure

---

## 2. Install Dependencies

```bash
# Install base dependencies
npm install

# Install Vue ecosystem
npm install vue-router@4 pinia

# Install Vuetify UI framework
npm install vuetify@^3.5.0 @mdi/font
npm install -D vite-plugin-vuetify

# Install HTTP client
npm install axios

# Install form validation
npm install vee-validate yup
npm install -D @vee-validate/yup

# Install utilities
npm install date-fns file-saver
npm install -D @types/file-saver

# Install testing tools
npm install -D vitest @vue/test-utils happy-dom @vitest/ui

# Install linting tools
npm install -D eslint @vue/eslint-config-typescript @vue/eslint-config-prettier prettier eslint-plugin-vue

# Install development tools
npm install -D @types/node
```

**Time:** ~3 minutes (depending on internet speed)

---

## 3. Project Structure Setup

```bash
# Create directory structure
mkdir -p src/{assets/{images,styles},components/{common,layout,profile},composables,router,services,stores,types,utils,views}

# Create subdirectories
mkdir -p src/components/{common,layout,profile}
mkdir -p tests/{unit,e2e}
```

**Result:**
```
src/
├── assets/
│   ├── images/
│   └── styles/
├── components/
│   ├── common/
│   ├── layout/
│   └── profile/
├── composables/
├── router/
├── services/
├── stores/
├── types/
├── utils/
└── views/
```

---

## 4. Configuration Files

### 4.1 Update `vite.config.ts`

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8034,
    proxy: {
      '/api': {
        target: 'http://localhost:8022',
        changeOrigin: true
      }
    }
  }
})
```

### 4.2 Update `tsconfig.json`

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
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 4.3 Create `.env.development`

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8022
VITE_APP_TITLE=HR Profile Generator - Dev
```

### 4.4 Create `.eslintrc.cjs`

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
    'vue/multi-word-component-names': 'warn'
  }
}
```

### 4.5 Create `.prettierrc.json`

```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "none",
  "arrowParens": "always"
}
```

---

## 5. First Component

### 5.1 Create Main Entry Point

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import vuetify from './plugins/vuetify'
import App from './App.vue'

import './assets/styles/main.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
```

### 5.2 Create Vuetify Plugin

```typescript
// src/plugins/vuetify.ts
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00'
        }
      }
    }
  }
})
```

### 5.3 Create Router

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    }
  ]
})

export default router
```

### 5.4 Create Root App Component

```vue
<!-- src/App.vue -->
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <v-app>
    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>

<style scoped>
/* Add global styles if needed */
</style>
```

### 5.5 Create First View

```vue
<!-- src/views/HomeView.vue -->
<script setup lang="ts">
import { ref } from 'vue'

const message = ref('Welcome to A101 HR Profile Generator')
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="text-center">
        <h1 class="text-h3 mb-4">{{ message }}</h1>

        <v-card class="mx-auto" max-width="600">
          <v-card-title class="text-h5">
            Vue.js 3 + TypeScript + Vuetify
          </v-card-title>

          <v-card-text>
            <p class="text-body-1">
              This is your first Vue 3 component! The project is now running with:
            </p>

            <v-list>
              <v-list-item prepend-icon="mdi-vuejs">
                <v-list-item-title>Vue 3 with Composition API</v-list-item-title>
              </v-list-item>

              <v-list-item prepend-icon="mdi-language-typescript">
                <v-list-item-title>TypeScript for type safety</v-list-item-title>
              </v-list-item>

              <v-list-item prepend-icon="mdi-material-design">
                <v-list-item-title>Vuetify 3 Material Design</v-list-item-title>
              </v-list-item>

              <v-list-item prepend-icon="mdi-router">
                <v-list-item-title>Vue Router 4</v-list-item-title>
              </v-list-item>

              <v-list-item prepend-icon="mdi-database">
                <v-list-item-title>Pinia State Management</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>

          <v-card-actions>
            <v-btn color="primary" block size="large">
              Start Building
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
```

### 5.6 Create Main Styles

```scss
// src/assets/styles/main.scss

// Global styles
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', sans-serif;
}

// Custom utility classes
.text-center {
  text-align: center;
}

.mt-4 {
  margin-top: 1rem;
}

.mb-4 {
  margin-bottom: 1rem;
}
```

---

## 6. Run Development Server

```bash
# Start development server
npm run dev

# Server will start at http://localhost:8034
```

**Expected Output:**
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:8034/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Open browser:** Navigate to `http://localhost:8034`

You should see:
- Welcome message
- A card with project features
- Material Design styling from Vuetify

---

## Next Steps

### Phase 1: Authentication (Week 1)

1. **Create Type Definitions**
   ```typescript
   // src/types/auth.types.ts
   export interface LoginCredentials {
     username: string
     password: string
   }

   export interface User {
     id: number
     username: string
     fullName: string
     role: string
   }

   export interface AuthResponse {
     access_token: string
     refresh_token: string
     user: User
   }
   ```

2. **Create API Client**
   ```typescript
   // src/services/api.ts
   import axios from 'axios'

   const apiClient = axios.create({
     baseURL: import.meta.env.VITE_API_BASE_URL,
     timeout: 30000,
     headers: {
       'Content-Type': 'application/json'
     }
   })

   export default apiClient
   ```

3. **Create Auth Service**
   ```typescript
   // src/services/auth.service.ts
   import apiClient from './api'
   import type { LoginCredentials, AuthResponse } from '@/types/auth.types'

   class AuthService {
     async login(credentials: LoginCredentials): Promise<AuthResponse> {
       const response = await apiClient.post<AuthResponse>(
         '/api/auth/login',
         credentials
       )
       return response.data
     }
   }

   export default new AuthService()
   ```

4. **Create Auth Store**
   ```typescript
   // src/stores/auth.ts
   import { defineStore } from 'pinia'
   import { ref, computed } from 'vue'
   import authService from '@/services/auth.service'
   import type { User, LoginCredentials } from '@/types/auth.types'

   export const useAuthStore = defineStore('auth', () => {
     const user = ref<User | null>(null)
     const token = ref<string | null>(localStorage.getItem('token'))

     const isAuthenticated = computed(() => !!token.value)

     async function login(credentials: LoginCredentials) {
       const response = await authService.login(credentials)
       token.value = response.access_token
       user.value = response.user
       localStorage.setItem('token', token.value)
     }

     function logout() {
       user.value = null
       token.value = null
       localStorage.removeItem('token')
     }

     return { user, token, isAuthenticated, login, logout }
   })
   ```

5. **Create Login View**
   ```vue
   <!-- src/views/LoginView.vue -->
   <script setup lang="ts">
   import { ref } from 'vue'
   import { useRouter } from 'vue-router'
   import { useAuthStore } from '@/stores/auth'

   const router = useRouter()
   const authStore = useAuthStore()

   const username = ref('')
   const password = ref('')
   const loading = ref(false)
   const error = ref('')

   async function handleLogin() {
     loading.value = true
     error.value = ''

     try {
       await authStore.login({ username: username.value, password: password.value })
       router.push('/')
     } catch (err: any) {
       error.value = err.response?.data?.detail || 'Login failed'
     } finally {
       loading.value = false
     }
   }
   </script>

   <template>
     <v-container class="fill-height" fluid>
       <v-row align="center" justify="center">
         <v-col cols="12" sm="8" md="4">
           <v-card>
             <v-card-title class="text-h5 text-center">
               A101 HR Profile Generator
             </v-card-title>

             <v-card-text>
               <v-form @submit.prevent="handleLogin">
                 <v-text-field
                   v-model="username"
                   label="Username"
                   prepend-icon="mdi-account"
                   required
                 />

                 <v-text-field
                   v-model="password"
                   label="Password"
                   type="password"
                   prepend-icon="mdi-lock"
                   required
                 />

                 <v-alert v-if="error" type="error" class="mt-4">
                   {{ error }}
                 </v-alert>

                 <v-btn
                   type="submit"
                   color="primary"
                   block
                   size="large"
                   class="mt-4"
                   :loading="loading"
                 >
                   Login
                 </v-btn>
               </v-form>
             </v-card-text>
           </v-card>
         </v-col>
       </v-row>
     </v-container>
   </template>
   ```

6. **Add Route Guard**
   ```typescript
   // src/router/index.ts
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
       }
     ]
   })

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

### Testing Your Setup

```bash
# Run tests
npm run test

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

---

## Useful Commands Reference

```bash
# Development
npm run dev                 # Start dev server
npm run build              # Build for production
npm run preview            # Preview production build

# Testing
npm run test               # Run tests
npm run test:ui            # Run tests with UI
npm run test:coverage      # Generate coverage report

# Code Quality
npm run lint               # Lint code
npm run format             # Format with Prettier
npm run type-check         # TypeScript type checking

# Dependencies
npm install <package>      # Install package
npm install -D <package>   # Install dev dependency
npm update                 # Update packages
npm outdated              # Check for outdated packages
```

---

## Common Issues & Solutions

### Issue 1: Port Already in Use

```bash
# Error: Port 8034 is already in use

# Solution: Use different port
vite --port 8035

# Or kill process on port 8034
lsof -ti:8034 | xargs kill -9
```

### Issue 2: Module Not Found

```bash
# Error: Cannot find module '@/...'

# Solution: Check tsconfig.json has correct paths
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Issue 3: Vuetify Components Not Working

```bash
# Error: Component not registered

# Solution: Check vite.config.ts has vuetify plugin
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true })
  ]
})
```

---

## Resources

- **Vue 3 Docs:** https://vuejs.org/guide/
- **Vuetify 3 Docs:** https://vuetifyjs.com/
- **Pinia Docs:** https://pinia.vuejs.org/
- **Vue Router Docs:** https://router.vuejs.org/
- **Vite Docs:** https://vitejs.dev/

---

## Summary

You now have:
- ✅ Vue 3 + TypeScript project initialized
- ✅ Vuetify UI framework configured
- ✅ Router and state management setup
- ✅ Development server running
- ✅ First component created
- ✅ Project structure organized

**Next:** Implement authentication flow (estimated 4-6 hours)

---

**Created:** 2025-10-25
**Status:** Ready for Development
**Estimated Setup Time:** 30 minutes

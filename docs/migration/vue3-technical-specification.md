# Vue.js 3 Technical Specification - A101 HR Profile Generator

**Version:** 1.0.0
**Date:** 2025-10-25
**Author:** Frontend Architecture Team

---

## Document Purpose

This technical specification provides detailed implementation patterns, code examples, and architectural decisions for the Vue.js 3 migration. It complements the migration plan with concrete technical guidance.

---

## Table of Contents

1. [API Integration Layer](#1-api-integration-layer)
2. [State Management Architecture](#2-state-management-architecture)
3. [Component Patterns](#3-component-patterns)
4. [Error Handling Strategy](#4-error-handling-strategy)
5. [Performance Optimization](#5-performance-optimization)
6. [Security Implementation](#6-security-implementation)
7. [Accessibility Guidelines](#7-accessibility-guidelines)

---

## 1. API Integration Layer

### 1.1 Complete API Client Implementation

```typescript
// services/api.ts
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Create axios instance with defaults
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false
})

// Request interceptor - add authentication token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()

    // Add auth token if available
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    // Add request ID for tracking
    config.headers['X-Request-ID'] = crypto.randomUUID()

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data
      })
    }

    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API] Response from ${response.config.url}:`, response.data)
    }

    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Handle 401 Unauthorized - try token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const authStore = useAuthStore()
        await authStore.refreshAccessToken()

        // Retry original request with new token
        if (authStore.token) {
          originalRequest.headers.Authorization = `Bearer ${authStore.token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        const authStore = useAuthStore()
        authStore.logout()
        router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
        return Promise.reject(refreshError)
      }
    }

    // Handle network errors
    if (!error.response) {
      console.error('[API] Network error:', error.message)
      // Could show a global network error notification here
    }

    // Handle specific HTTP errors
    if (error.response) {
      const status = error.response.status

      switch (status) {
        case 403:
          console.error('[API] Forbidden:', error.response.data)
          // Show permission denied message
          break
        case 404:
          console.error('[API] Not found:', error.response.data)
          break
        case 422:
          console.error('[API] Validation error:', error.response.data)
          // Handle validation errors
          break
        case 500:
          console.error('[API] Server error:', error.response.data)
          // Show server error message
          break
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

// Export convenience methods
export const api = {
  get: <T = any>(url: string, config = {}) =>
    apiClient.get<T>(url, config),

  post: <T = any>(url: string, data?: any, config = {}) =>
    apiClient.post<T>(url, data, config),

  put: <T = any>(url: string, data?: any, config = {}) =>
    apiClient.put<T>(url, data, config),

  patch: <T = any>(url: string, data?: any, config = {}) =>
    apiClient.patch<T>(url, data, config),

  delete: <T = any>(url: string, config = {}) =>
    apiClient.delete<T>(url, config)
}
```

### 1.2 Service Layer Implementation

```typescript
// services/auth.service.ts
import apiClient from './api'
import type {
  LoginCredentials,
  AuthResponse,
  RefreshTokenResponse,
  User
} from '@/types/auth.types'

class AuthService {
  private readonly BASE_PATH = '/api/auth'

  /**
   * Authenticate user with username and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      `${this.BASE_PATH}/login`,
      credentials
    )
    return response.data
  }

  /**
   * Refresh access token using refresh token
   */
  async refresh(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await apiClient.post<RefreshTokenResponse>(
      `${this.BASE_PATH}/refresh`,
      { refresh_token: refreshToken }
    )
    return response.data
  }

  /**
   * Logout user (invalidate tokens on server)
   */
  async logout(): Promise<void> {
    await apiClient.post(`${this.BASE_PATH}/logout`)
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>(`${this.BASE_PATH}/me`)
    return response.data
  }

  /**
   * Verify token validity
   */
  async verifyToken(token: string): Promise<boolean> {
    try {
      await apiClient.post(`${this.BASE_PATH}/verify`, { token })
      return true
    } catch {
      return false
    }
  }
}

export default new AuthService()

// services/catalog.service.ts
import apiClient from './api'
import type { Position, Department, CatalogStats } from '@/types/catalog.types'

class CatalogService {
  private readonly BASE_PATH = '/api/catalog'

  /**
   * Get all positions (4,376 items)
   */
  async getPositions(): Promise<Position[]> {
    const response = await apiClient.get<Position[]>(`${this.BASE_PATH}/positions`)
    return response.data
  }

  /**
   * Search positions by query
   */
  async searchPositions(query: string, limit = 100): Promise<Position[]> {
    const response = await apiClient.get<Position[]>(
      `${this.BASE_PATH}/positions/search`,
      { params: { q: query, limit } }
    )
    return response.data
  }

  /**
   * Get departments hierarchy
   */
  async getDepartments(): Promise<Department[]> {
    const response = await apiClient.get<Department[]>(`${this.BASE_PATH}/departments`)
    return response.data
  }

  /**
   * Get catalog statistics
   */
  async getStats(): Promise<CatalogStats> {
    const response = await apiClient.get<CatalogStats>(`${this.BASE_PATH}/stats`)
    return response.data
  }
}

export default new CatalogService()

// services/generation.service.ts
import apiClient from './api'
import type {
  GenerationRequest,
  GenerationResponse,
  TaskStatusResponse,
  ProfileResult
} from '@/types/generation.types'

class GenerationService {
  private readonly BASE_PATH = '/api/generation'

  /**
   * Start profile generation
   */
  async start(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await apiClient.post<GenerationResponse>(
      `${this.BASE_PATH}/start`,
      request
    )
    return response.data
  }

  /**
   * Get task status
   */
  async getStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await apiClient.get<TaskStatusResponse>(
      `${this.BASE_PATH}/${taskId}/status`
    )
    return response.data
  }

  /**
   * Get task result
   */
  async getResult(taskId: string): Promise<ProfileResult> {
    const response = await apiClient.get<ProfileResult>(
      `${this.BASE_PATH}/${taskId}/result`
    )
    return response.data
  }

  /**
   * Cancel generation task
   */
  async cancel(taskId: string): Promise<void> {
    await apiClient.delete(`${this.BASE_PATH}/${taskId}`)
  }
}

export default new GenerationService()

// services/profile.service.ts
import apiClient from './api'
import type { Profile, ProfileListResponse, ProfileFilters } from '@/types/profile.types'

class ProfileService {
  private readonly BASE_PATH = '/api/profiles'

  /**
   * Get all profiles with pagination and filtering
   */
  async list(filters: ProfileFilters = {}): Promise<ProfileListResponse> {
    const response = await apiClient.get<ProfileListResponse>(this.BASE_PATH, {
      params: filters
    })
    return response.data
  }

  /**
   * Get profile by ID
   */
  async getById(id: string): Promise<Profile> {
    const response = await apiClient.get<Profile>(`${this.BASE_PATH}/${id}`)
    return response.data
  }

  /**
   * Download profile in specified format
   */
  async download(id: string, format: 'json' | 'md' | 'docx' | 'xlsx'): Promise<Blob> {
    const response = await apiClient.get(
      `${this.BASE_PATH}/${id}/download/${format}`,
      { responseType: 'blob' }
    )
    return response.data
  }

  /**
   * Delete profile
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`${this.BASE_PATH}/${id}`)
  }

  /**
   * Bulk delete profiles
   */
  async bulkDelete(ids: string[]): Promise<void> {
    await apiClient.post(`${this.BASE_PATH}/bulk-delete`, { ids })
  }
}

export default new ProfileService()

// services/dashboard.service.ts
import apiClient from './api'
import type { DashboardStats } from '@/types/dashboard.types'

class DashboardService {
  private readonly BASE_PATH = '/api/dashboard'

  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>(`${this.BASE_PATH}/stats`)
    return response.data
  }
}

export default new DashboardService()
```

---

## 2. State Management Architecture

### 2.1 Complete Store Implementations

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth.service'
import type { User, LoginCredentials } from '@/types/auth.types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value?.fullName || 'Guest')
  const userRole = computed(() => user.value?.role || 'user')
  const isAdmin = computed(() => userRole.value === 'admin')

  // Actions
  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null

    try {
      const response = await authService.login(credentials)

      token.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user

      // Persist to localStorage
      localStorage.setItem('token', token.value)
      localStorage.setItem('refreshToken', refreshToken.value)
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      logout()
      throw new Error('No refresh token available')
    }

    try {
      const response = await authService.refresh(refreshToken.value)
      token.value = response.access_token
      localStorage.setItem('token', token.value)
    } catch (err) {
      logout()
      throw err
    }
  }

  async function logout() {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear state
      user.value = null
      token.value = null
      refreshToken.value = null
      error.value = null

      // Clear localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return

    try {
      user.value = await authService.getCurrentUser()
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (err) {
      console.error('Failed to fetch current user:', err)
      logout()
    }
  }

  // Initialize from localStorage
  function initialize() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('Failed to parse stored user:', err)
      }
    }

    // Verify token is still valid
    if (token.value) {
      fetchCurrentUser()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    userName,
    userRole,
    isAdmin,
    // Actions
    login,
    refreshAccessToken,
    logout,
    fetchCurrentUser,
    initialize
  }
})

// stores/catalog.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import catalogService from '@/services/catalog.service'
import type { Position, Department } from '@/types/catalog.types'

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const positions = ref<Position[]>([])
  const departments = ref<Department[]>([])
  const loading = ref(false)
  const loaded = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const positionCount = computed(() => positions.value.length)
  const departmentCount = computed(() => departments.value.length)

  const positionsByDepartment = computed(() => {
    const grouped = new Map<string, Position[]>()

    positions.value.forEach(pos => {
      if (!grouped.has(pos.department)) {
        grouped.set(pos.department, [])
      }
      grouped.get(pos.department)!.push(pos)
    })

    return grouped
  })

  // Actions
  async function loadCatalog() {
    if (loaded.value) return // Already loaded

    loading.value = true
    error.value = null

    try {
      const [positionsData, departmentsData] = await Promise.all([
        catalogService.getPositions(),
        catalogService.getDepartments()
      ])

      positions.value = positionsData
      departments.value = departmentsData
      loaded.value = true
    } catch (err: any) {
      error.value = err.message || 'Failed to load catalog'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchPositions(query: string, limit = 100) {
    try {
      return await catalogService.searchPositions(query, limit)
    } catch (err: any) {
      error.value = err.message || 'Search failed'
      throw err
    }
  }

  function getPositionById(id: string): Position | undefined {
    return positions.value.find(pos => pos.id === id)
  }

  function getDepartmentById(id: string): Department | undefined {
    return departments.value.find(dept => dept.id === id)
  }

  return {
    // State
    positions,
    departments,
    loading,
    loaded,
    error,
    // Getters
    positionCount,
    departmentCount,
    positionsByDepartment,
    // Actions
    loadCatalog,
    searchPositions,
    getPositionById,
    getDepartmentById
  }
})

// stores/generation.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import generationService from '@/services/generation.service'
import type { GenerationTask, GenerationRequest } from '@/types/generation.types'

export const useGenerationStore = defineStore('generation', () => {
  // State
  const currentTask = ref<GenerationTask | null>(null)
  const taskHistory = ref<GenerationTask[]>([])
  const polling = ref(false)
  const error = ref<string | null>(null)

  // Polling interval ID
  let pollIntervalId: number | null = null

  // Getters
  const isGenerating = computed(() => {
    return (
      currentTask.value?.status === 'processing' ||
      currentTask.value?.status === 'queued'
    )
  })

  const progress = computed(() => currentTask.value?.progress || 0)

  const currentStep = computed(() => currentTask.value?.currentStep || '')

  // Actions
  async function startGeneration(request: GenerationRequest) {
    error.value = null

    try {
      const response = await generationService.start(request)

      currentTask.value = {
        taskId: response.task_id,
        status: response.status,
        progress: 0,
        createdAt: new Date(),
        estimatedDuration: response.estimated_duration
      }

      // Start polling task status
      startPolling(response.task_id)

      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to start generation'
      throw err
    }
  }

  function startPolling(taskId: string, interval = 2000) {
    if (polling.value) return

    polling.value = true

    pollIntervalId = window.setInterval(async () => {
      try {
        const status = await generationService.getStatus(taskId)
        currentTask.value = status.task

        // Stop polling when task is complete or failed
        if (
          status.task.status === 'completed' ||
          status.task.status === 'failed' ||
          status.task.status === 'cancelled'
        ) {
          stopPolling()

          // Add to history if completed
          if (status.task.status === 'completed') {
            taskHistory.value.unshift(currentTask.value)
          }
        }
      } catch (err) {
        console.error('Polling error:', err)
        stopPolling()
        error.value = 'Failed to get task status'
      }
    }, interval)
  }

  function stopPolling() {
    if (pollIntervalId) {
      clearInterval(pollIntervalId)
      pollIntervalId = null
    }
    polling.value = false
  }

  async function cancelGeneration(taskId: string) {
    try {
      await generationService.cancel(taskId)

      if (currentTask.value?.taskId === taskId) {
        currentTask.value.status = 'cancelled'
      }

      stopPolling()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to cancel generation'
      throw err
    }
  }

  async function getTaskResult(taskId: string) {
    try {
      return await generationService.getResult(taskId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to get result'
      throw err
    }
  }

  function clearCurrentTask() {
    currentTask.value = null
    error.value = null
  }

  // Cleanup on store disposal
  function $dispose() {
    stopPolling()
  }

  return {
    // State
    currentTask,
    taskHistory,
    polling,
    error,
    // Getters
    isGenerating,
    progress,
    currentStep,
    // Actions
    startGeneration,
    startPolling,
    stopPolling,
    cancelGeneration,
    getTaskResult,
    clearCurrentTask,
    $dispose
  }
})
```

---

## 3. Component Patterns

### 3.1 Composables for Reusable Logic

```typescript
// composables/useNotification.ts
import { ref } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: string
  type: NotificationType
  message: string
  duration?: number
}

const notifications = ref<Notification[]>([])

export function useNotification() {
  function show(message: string, type: NotificationType = 'info', duration = 3000) {
    const id = crypto.randomUUID()

    const notification: Notification = {
      id,
      type,
      message,
      duration
    }

    notifications.value.push(notification)

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  function showSuccess(message: string, duration = 3000) {
    return show(message, 'success', duration)
  }

  function showError(message: string, duration = 5000) {
    return show(message, 'error', duration)
  }

  function showWarning(message: string, duration = 4000) {
    return show(message, 'warning', duration)
  }

  function showInfo(message: string, duration = 3000) {
    return show(message, 'info', duration)
  }

  function remove(id: string) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clear() {
    notifications.value = []
  }

  return {
    notifications,
    show,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    remove,
    clear
  }
}

// composables/useFileDownload.ts
import { ref } from 'vue'
import { saveAs } from 'file-saver'

export function useFileDownload() {
  const downloading = ref(false)
  const progress = ref(0)
  const error = ref<string | null>(null)

  async function downloadBlob(
    blob: Blob,
    filename: string,
    extension: string
  ) {
    downloading.value = true
    progress.value = 0
    error.value = null

    try {
      saveAs(blob, `${filename}.${extension}`)
      progress.value = 100
    } catch (err: any) {
      error.value = err.message || 'Download failed'
      throw err
    } finally {
      downloading.value = false
      setTimeout(() => {
        progress.value = 0
      }, 1000)
    }
  }

  async function downloadUrl(
    url: string,
    filename: string,
    onProgress?: (progress: number) => void
  ) {
    downloading.value = true
    progress.value = 0
    error.value = null

    try {
      const response = await fetch(url)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const contentLength = response.headers.get('content-length')
      const total = contentLength ? parseInt(contentLength, 10) : 0

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is null')
      }

      const chunks: Uint8Array[] = []
      let receivedLength = 0

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        chunks.push(value)
        receivedLength += value.length

        if (total > 0) {
          const currentProgress = Math.round((receivedLength / total) * 100)
          progress.value = currentProgress

          if (onProgress) {
            onProgress(currentProgress)
          }
        }
      }

      const blob = new Blob(chunks)
      saveAs(blob, filename)

      progress.value = 100
    } catch (err: any) {
      error.value = err.message || 'Download failed'
      throw err
    } finally {
      downloading.value = false
      setTimeout(() => {
        progress.value = 0
      }, 1000)
    }
  }

  return {
    downloading,
    progress,
    error,
    downloadBlob,
    downloadUrl
  }
}

// composables/useDebounce.ts
import { ref, watch } from 'vue'
import type { Ref } from 'vue'

export function useDebounce<T>(value: Ref<T>, delay = 300) {
  const debouncedValue = ref(value.value) as Ref<T>
  let timeoutId: number | null = null

  watch(value, (newValue) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = window.setTimeout(() => {
      debouncedValue.value = newValue
    }, delay)
  })

  return debouncedValue
}

// composables/useLocalStorage.ts
import { ref, watch } from 'vue'
import type { Ref } from 'vue'

export function useLocalStorage<T>(key: string, defaultValue: T): Ref<T> {
  const storedValue = localStorage.getItem(key)

  const value = ref(
    storedValue ? JSON.parse(storedValue) : defaultValue
  ) as Ref<T>

  watch(
    value,
    (newValue) => {
      localStorage.setItem(key, JSON.stringify(newValue))
    },
    { deep: true }
  )

  return value
}

// composables/usePagination.ts
import { ref, computed } from 'vue'

export function usePagination<T>(items: Ref<T[]>, itemsPerPage = 10) {
  const currentPage = ref(1)

  const totalPages = computed(() =>
    Math.ceil(items.value.length / itemsPerPage)
  )

  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage
    const end = start + itemsPerPage
    return items.value.slice(start, end)
  })

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  function nextPage() {
    goToPage(currentPage.value + 1)
  }

  function prevPage() {
    goToPage(currentPage.value - 1)
  }

  function reset() {
    currentPage.value = 1
  }

  return {
    currentPage,
    totalPages,
    paginatedItems,
    goToPage,
    nextPage,
    prevPage,
    reset
  }
}
```

---

## 4. Error Handling Strategy

### 4.1 Global Error Handler

```typescript
// main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { useNotification } from './composables/useNotification'

const app = createApp(App)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('[Global Error]:', err)
  console.error('Component:', instance)
  console.error('Error Info:', info)

  const { showError } = useNotification()

  if (err instanceof Error) {
    showError(err.message)
  } else {
    showError('An unexpected error occurred')
  }
}

// Global warning handler (development only)
if (import.meta.env.DEV) {
  app.config.warnHandler = (msg, instance, trace) => {
    console.warn('[Vue Warning]:', msg)
    console.warn('Trace:', trace)
  }
}

app.mount('#app')
```

### 4.2 Error Boundary Component

```vue
<!-- components/common/ErrorBoundary.vue -->
<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'

const error = ref<Error | null>(null)
const errorInfo = ref<string>('')

onErrorCaptured((err, instance, info) => {
  error.value = err
  errorInfo.value = info

  console.error('Error Boundary caught error:', err)
  console.error('Component:', instance)
  console.error('Info:', info)

  // Return false to prevent error from propagating
  return false
})

function retry() {
  error.value = null
  errorInfo.value = ''
}
</script>

<template>
  <div v-if="error" class="error-boundary">
    <v-alert type="error" prominent>
      <v-alert-title>Something went wrong</v-alert-title>
      <p>{{ error.message }}</p>
      <template #append>
        <v-btn @click="retry">Retry</v-btn>
      </template>
    </v-alert>
  </div>
  <slot v-else />
</template>
```

---

## 5. Performance Optimization

### 5.1 Virtual Scrolling for Large Lists

```vue
<!-- components/profile/ProfileListVirtual.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Profile } from '@/types'

interface Props {
  profiles: Profile[]
  itemHeight?: number
}

const props = withDefaults(defineProps<Props>(), {
  itemHeight: 100
})

const emit = defineEmits<{
  view: [id: string]
  download: [id: string, format: string]
  delete: [id: string]
}>()

const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)

const visibleRange = computed(() => {
  const containerHeight = containerRef.value?.clientHeight || 600
  const start = Math.floor(scrollTop.value / props.itemHeight)
  const end = Math.ceil((scrollTop.value + containerHeight) / props.itemHeight)

  return { start, end }
})

const visibleItems = computed(() => {
  const { start, end } = visibleRange.value
  return props.profiles.slice(start, end).map((profile, index) => ({
    profile,
    index: start + index,
    top: (start + index) * props.itemHeight
  }))
})

const totalHeight = computed(() => props.profiles.length * props.itemHeight)

function handleScroll(event: Event) {
  scrollTop.value = (event.target as HTMLElement).scrollTop
}
</script>

<template>
  <div
    ref="containerRef"
    class="profile-list-virtual"
    @scroll="handleScroll"
  >
    <div :style="{ height: `${totalHeight}px`, position: 'relative' }">
      <div
        v-for="{ profile, index, top } in visibleItems"
        :key="profile.id"
        :style="{ position: 'absolute', top: `${top}px`, left: 0, right: 0 }"
      >
        <ProfileCard
          :profile="profile"
          @view="emit('view', profile.id)"
          @download="emit('download', profile.id, $event)"
          @delete="emit('delete', profile.id)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-list-virtual {
  height: 600px;
  overflow-y: auto;
}
</style>
```

### 5.2 Lazy Loading Images

```vue
<!-- components/common/LazyImage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Props {
  src: string
  alt?: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  placeholder: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"%3E%3Crect width="100" height="100" fill="%23f0f0f0"/%3E%3C/svg%3E'
})

const loaded = ref(false)
const error = ref(false)
const imgRef = ref<HTMLImageElement>()

onMounted(() => {
  if (!imgRef.value) return

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          loadImage()
          observer.disconnect()
        }
      })
    },
    { rootMargin: '50px' }
  )

  observer.observe(imgRef.value)
})

function loadImage() {
  const img = new Image()
  img.src = props.src

  img.onload = () => {
    loaded.value = true
  }

  img.onerror = () => {
    error.value = true
  }
}
</script>

<template>
  <img
    ref="imgRef"
    :src="loaded ? src : placeholder"
    :alt="alt"
    :class="{ loaded, error }"
  />
</template>

<style scoped>
img {
  transition: opacity 0.3s;
  opacity: 0;
}

img.loaded {
  opacity: 1;
}

img.error {
  opacity: 0.5;
}
</style>
```

---

## 6. Security Implementation

### 6.1 XSS Protection

```typescript
// utils/sanitize.ts
import DOMPurify from 'dompurify'

/**
 * Sanitize HTML to prevent XSS attacks
 */
export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target']
  })
}

/**
 * Escape special characters in plain text
 */
export function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * Validate URL to prevent javascript: and data: URIs
 */
export function isSafeUrl(url: string): boolean {
  const pattern = /^(https?:\/\/|\/)/i
  return pattern.test(url)
}
```

### 6.2 CSRF Protection

```typescript
// services/api.ts
// Add CSRF token to requests
apiClient.interceptors.request.use((config) => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')

  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken
  }

  return config
})
```

---

## 7. Accessibility Guidelines

### 7.1 WCAG 2.1 AA Compliance Checklist

- [ ] **Keyboard Navigation:** All interactive elements accessible via keyboard
- [ ] **Focus Indicators:** Visible focus states for all focusable elements
- [ ] **ARIA Labels:** Proper labels for screen readers
- [ ] **Color Contrast:** Minimum 4.5:1 for normal text, 3:1 for large text
- [ ] **Alt Text:** Descriptive alt text for all images
- [ ] **Semantic HTML:** Use proper HTML5 elements (header, nav, main, aside, footer)
- [ ] **Form Labels:** All form inputs have associated labels
- [ ] **Error Messages:** Clear, actionable error messages
- [ ] **Loading States:** Announce loading states to screen readers

### 7.2 Accessible Component Example

```vue
<!-- components/common/AccessibleButton.vue -->
<script setup lang="ts">
interface Props {
  label: string
  ariaLabel?: string
  loading?: boolean
  disabled?: boolean
  variant?: 'primary' | 'secondary' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  variant: 'primary'
})

const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <button
    :aria-label="ariaLabel || label"
    :aria-busy="loading"
    :disabled="disabled || loading"
    :class="['accessible-button', `variant-${variant}`]"
    @click="emit('click')"
  >
    <span v-if="loading" class="sr-only">Loading...</span>
    <v-icon v-if="loading" class="loading-spinner">mdi-loading</v-icon>
    <span>{{ label }}</span>
  </button>
</template>

<style scoped>
.accessible-button {
  position: relative;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.accessible-button:focus-visible {
  outline: 3px solid #005fcc;
  outline-offset: 2px;
}

.accessible-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
```

---

## Conclusion

This technical specification provides detailed implementation patterns for the Vue.js 3 migration. All patterns follow best practices for:

- **Type Safety** with TypeScript
- **Performance** with code splitting and lazy loading
- **Security** with XSS/CSRF protection
- **Accessibility** with WCAG 2.1 AA compliance
- **Maintainability** with clean architecture and reusable composables

---

**Last Updated:** 2025-10-25
**Status:** Ready for Implementation

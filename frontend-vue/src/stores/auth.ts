/**
 * Authentication store
 * Manages user authentication state, tokens, and login/logout operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AxiosError } from 'axios'
import { authService } from '@/services/auth.service'
import type { User, LoginRequest } from '@/types/auth'

const TOKEN_KEY = 'auth_token'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<User | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  /**
   * Login user with credentials
   * @param credentials - Username and password
   * @returns true if login successful, false otherwise
   */
  async function login(credentials: LoginRequest): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const response = await authService.login(credentials)

      if (response.success) {
        // Store token
        token.value = response.access_token
        localStorage.setItem(TOKEN_KEY, response.access_token)

        // Store user info
        user.value = response.user_info

        loading.value = false
        return true
      } else {
        error.value = response.message || 'Login failed'
        loading.value = false
        return false
      }
    } catch (err) {
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || axiosError.message || 'Network error'
      loading.value = false
      return false
    }
  }

  /**
   * Logout current user
   * Clears token and user data
   */
  async function logout(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      // Call backend logout endpoint
      await authService.logout()
    } catch (err) {
      // Log error but continue with local cleanup
      if (import.meta.env.DEV) {
        console.error('Logout error:', err)
      }
    } finally {
      // Clear local state regardless of API result
      token.value = null
      user.value = null
      localStorage.removeItem(TOKEN_KEY)
      loading.value = false
    }
  }

  /**
   * Load current user info
   * Used to restore session on app start if token exists
   */
  async function loadUser(): Promise<void> {
    if (!token.value) {
      return
    }

    loading.value = true
    error.value = null

    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
    } catch (err) {
      // Token might be expired or invalid
      const axiosError = err as AxiosError<{ message?: string }>
      error.value = axiosError.response?.data?.message || 'Failed to load user'

      // Clear invalid token
      token.value = null
      user.value = null
      localStorage.removeItem(TOKEN_KEY)
    } finally {
      loading.value = false
    }
  }

  /**
   * Initialize auth state on app start
   * Loads user if token exists in localStorage
   */
  async function initialize(): Promise<void> {
    if (token.value) {
      await loadUser()
    }
  }

  /**
   * Clear error message
   * Used when user starts typing to dismiss previous errors
   */
  function clearError(): void {
    error.value = null
  }

  return {
    // State
    token,
    user,
    loading,
    error,

    // Computed
    isAuthenticated,

    // Actions
    login,
    logout,
    loadUser,
    initialize,
    clearError,
  }
})

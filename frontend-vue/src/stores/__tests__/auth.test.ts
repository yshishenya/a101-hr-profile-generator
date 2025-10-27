/**
 * Unit tests for auth store
 * Tests authentication state management, login/logout, token handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { authService } from '@/services/auth.service'
import type { LoginRequest, LoginResponse, User } from '@/types/auth'

// Mock dependencies
vi.mock('@/services/auth.service')
vi.mock('@/utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock window.addEventListener
const eventListeners: Record<string, Function[]> = {}

Object.defineProperty(window, 'addEventListener', {
  value: (event: string, callback: Function) => {
    if (!eventListeners[event]) {
      eventListeners[event] = []
    }
    eventListeners[event].push(callback)
  }
})

function dispatchEvent(event: string): void {
  const listeners = eventListeners[event] || []
  listeners.forEach(listener => listener())
}

describe('authStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with null state when no token in localStorage', () => {
      const store = useAuthStore()

      expect(store.token).toBe(null)
      expect(store.user).toBe(null)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.isAuthenticated).toBe(false)
    })

    it('should load token from localStorage on initialization', () => {
      localStorageMock.setItem('auth_token', 'existing-token')

      const store = useAuthStore()

      expect(store.token).toBe('existing-token')
    })
  })

  describe('Computed Properties', () => {
    it('should return false for isAuthenticated when no token', () => {
      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)
    })

    it('should return false for isAuthenticated when token but no user', () => {
      const store = useAuthStore()
      store.token = 'test-token'

      expect(store.isAuthenticated).toBe(false)
    })

    it('should return true for isAuthenticated when both token and user exist', () => {
      const store = useAuthStore()
      store.token = 'test-token'
      store.user = createMockUser()

      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const store = useAuthStore()
      const credentials: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      }

      const mockResponse: LoginResponse = {
        success: true,
        timestamp: new Date().toISOString(),
        message: 'Login successful',
        access_token: 'new-token',
        token_type: 'Bearer',
        expires_in: 3600,
        user_info: createMockUser()
      }

      vi.mocked(authService.login).mockResolvedValue(mockResponse)

      const result = await store.login(credentials)

      expect(result).toBe(true)
      expect(store.token).toBe('new-token')
      expect(store.user).toEqual(mockResponse.user_info)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(localStorageMock.getItem('auth_token')).toBe('new-token')
    })

    it('should handle login failure with error message', async () => {
      const store = useAuthStore()
      const credentials: LoginRequest = {
        username: 'testuser',
        password: 'wrongpassword'
      }

      const mockResponse: LoginResponse = {
        success: false,
        timestamp: new Date().toISOString(),
        message: 'Invalid credentials',
        access_token: '',
        token_type: '',
        expires_in: 0,
        user_info: {} as User
      }

      vi.mocked(authService.login).mockResolvedValue(mockResponse)

      const result = await store.login(credentials)

      expect(result).toBe(false)
      expect(store.error).toBe('Invalid credentials')
      expect(store.token).toBe(null)
      expect(store.user).toBe(null)
    })

    it('should handle network errors during login', async () => {
      const store = useAuthStore()
      const credentials: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      }

      vi.mocked(authService.login).mockRejectedValue({
        response: {
          data: {
            message: 'Network error'
          }
        }
      })

      const result = await store.login(credentials)

      expect(result).toBe(false)
      expect(store.error).toBe('Network error')
    })

    it('should handle errors without response data', async () => {
      const store = useAuthStore()
      const credentials: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      }

      vi.mocked(authService.login).mockRejectedValue({
        message: 'Generic error'
      })

      const result = await store.login(credentials)

      expect(result).toBe(false)
      expect(store.error).toBe('Generic error')
    })

    it('should clear previous errors on new login attempt', async () => {
      const store = useAuthStore()
      store.error = 'Previous error'

      const mockResponse: LoginResponse = {
        success: true,
        timestamp: new Date().toISOString(),
        message: 'Login successful',
        access_token: 'token',
        token_type: 'Bearer',
        expires_in: 3600,
        user_info: createMockUser()
      }

      vi.mocked(authService.login).mockResolvedValue(mockResponse)

      await store.login({ username: 'test', password: 'pass' })

      expect(store.error).toBe(null)
    })

    it('should set loading state during login', async () => {
      const store = useAuthStore()
      let loadingDuringCall = false

      vi.mocked(authService.login).mockImplementation(async () => {
        loadingDuringCall = store.loading
        return {
          success: true,
          timestamp: new Date().toISOString(),
          message: 'Login successful',
          access_token: 'token',
          token_type: 'Bearer',
          expires_in: 3600,
          user_info: createMockUser()
        }
      })

      await store.login({ username: 'test', password: 'pass' })

      expect(loadingDuringCall).toBe(true)
      expect(store.loading).toBe(false)
    })
  })

  describe('logout', () => {
    it('should logout successfully and clear state', async () => {
      const store = useAuthStore()

      // Set initial authenticated state
      store.token = 'test-token'
      store.user = createMockUser()
      localStorageMock.setItem('auth_token', 'test-token')

      vi.mocked(authService.logout).mockResolvedValue({
        success: true,
        timestamp: new Date().toISOString(),
        message: 'Logout successful'
      })

      await store.logout()

      expect(store.token).toBe(null)
      expect(store.user).toBe(null)
      expect(store.loading).toBe(false)
      expect(localStorageMock.getItem('auth_token')).toBe(null)
    })

    it('should clear state even if API call fails', async () => {
      const store = useAuthStore()

      // Set initial authenticated state
      store.token = 'test-token'
      store.user = createMockUser()
      localStorageMock.setItem('auth_token', 'test-token')

      vi.mocked(authService.logout).mockRejectedValue(new Error('API Error'))

      await store.logout()

      expect(store.token).toBe(null)
      expect(store.user).toBe(null)
      expect(localStorageMock.getItem('auth_token')).toBe(null)
    })
  })

  describe('loadUser', () => {
    it('should load user data successfully', async () => {
      const store = useAuthStore()
      const mockUser = createMockUser()

      store.token = 'test-token'
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      await store.loadUser()

      expect(store.user).toEqual(mockUser)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should skip loading if no token present', async () => {
      const store = useAuthStore()

      await store.loadUser()

      expect(authService.getCurrentUser).not.toHaveBeenCalled()
    })

    it('should clear invalid token on load failure', async () => {
      const store = useAuthStore()

      store.token = 'invalid-token'
      localStorageMock.setItem('auth_token', 'invalid-token')

      vi.mocked(authService.getCurrentUser).mockRejectedValue({
        response: {
          data: {
            message: 'Token expired'
          }
        }
      })

      await store.loadUser()

      expect(store.token).toBe(null)
      expect(store.user).toBe(null)
      expect(store.error).toBe('Token expired')
      expect(localStorageMock.getItem('auth_token')).toBe(null)
    })
  })

  describe('initialize', () => {
    it('should initialize and load user if token exists', async () => {
      localStorageMock.setItem('auth_token', 'test-token')

      const store = useAuthStore()
      const mockUser = createMockUser()

      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      await store.initialize()

      expect(store.user).toEqual(mockUser)
      expect(authService.getCurrentUser).toHaveBeenCalled()
    })

    it('should skip initialization if no token', async () => {
      const store = useAuthStore()

      await store.initialize()

      expect(authService.getCurrentUser).not.toHaveBeenCalled()
    })

    it('should skip initialization if user already loaded', async () => {
      localStorageMock.setItem('auth_token', 'test-token')

      const store = useAuthStore()
      store.user = createMockUser()

      await store.initialize()

      expect(authService.getCurrentUser).not.toHaveBeenCalled()
    })

    it('should handle concurrent initialization calls', async () => {
      localStorageMock.setItem('auth_token', 'test-token')

      const store = useAuthStore()
      const mockUser = createMockUser()

      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser)

      // Call initialize multiple times concurrently
      const promises = [
        store.initialize(),
        store.initialize(),
        store.initialize()
      ]

      await Promise.all(promises)

      // Should only call API once
      expect(authService.getCurrentUser).toHaveBeenCalledTimes(1)
      expect(store.user).toEqual(mockUser)
    })
  })

  describe('clearError', () => {
    it('should clear error message', () => {
      const store = useAuthStore()

      store.error = 'Some error'
      store.clearError()

      expect(store.error).toBe(null)
    })
  })

  describe('handleUnauthorized', () => {
    it('should clear auth state on unauthorized event', async () => {
      localStorageMock.setItem('auth_token', 'test-token')

      const store = useAuthStore()
      store.token = 'test-token'
      store.user = createMockUser()

      // Trigger unauthorized event
      dispatchEvent('auth:unauthorized')

      // Wait for event handler
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(store.token).toBe(null)
      expect(store.user).toBe(null)
      expect(localStorageMock.getItem('auth_token')).toBe(null)
    })
  })

  describe('Edge Cases', () => {
    it('should handle malformed user data', async () => {
      const store = useAuthStore()

      store.token = 'test-token'
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      vi.mocked(authService.getCurrentUser).mockResolvedValue(null as any)

      await store.loadUser()

      expect(store.user).toBe(null)
    })

    it('should handle login with remember_me option', async () => {
      const store = useAuthStore()
      const credentials: LoginRequest = {
        username: 'testuser',
        password: 'password123',
        remember_me: true
      }

      const mockResponse: LoginResponse = {
        success: true,
        timestamp: new Date().toISOString(),
        message: 'Login successful',
        access_token: 'token',
        token_type: 'Bearer',
        expires_in: 3600,
        user_info: createMockUser()
      }

      vi.mocked(authService.login).mockResolvedValue(mockResponse)

      const result = await store.login(credentials)

      expect(result).toBe(true)
      expect(authService.login).toHaveBeenCalledWith(credentials)
    })

    it('should handle empty error response', async () => {
      const store = useAuthStore()

      vi.mocked(authService.login).mockRejectedValue({})

      const result = await store.login({ username: 'test', password: 'pass' })

      expect(result).toBe(false)
      expect(store.error).toBe('Network error')
    })
  })

  describe('State Persistence', () => {
    it('should persist token across store recreations', () => {
      localStorageMock.setItem('auth_token', 'persisted-token')

      const store1 = useAuthStore()
      expect(store1.token).toBe('persisted-token')

      // Create new pinia instance to simulate app restart
      setActivePinia(createPinia())

      const store2 = useAuthStore()
      expect(store2.token).toBe('persisted-token')
    })

    it('should not persist user data (only token)', () => {
      localStorageMock.setItem('auth_token', 'test-token')

      const store = useAuthStore()
      store.user = createMockUser()

      expect(store.token).toBe('test-token')
      expect(store.user).not.toBe(null)

      // Create new pinia instance (simulating app restart)
      setActivePinia(createPinia())

      const newStore = useAuthStore()
      expect(newStore.user).toBe(null) // User not persisted
      expect(newStore.token).toBe('test-token') // Token persisted from localStorage
    })
  })

  describe('Loading State Management', () => {
    it('should manage loading state correctly during login', async () => {
      const store = useAuthStore()

      expect(store.loading).toBe(false)

      const loginPromise = store.login({ username: 'test', password: 'pass' })

      // Should be loading during async operation
      expect(store.loading).toBe(true)

      vi.mocked(authService.login).mockResolvedValue({
        success: true,
        timestamp: new Date().toISOString(),
        message: 'Success',
        access_token: 'token',
        token_type: 'Bearer',
        expires_in: 3600,
        user_info: createMockUser()
      })

      await loginPromise

      expect(store.loading).toBe(false)
    })
  })
})

// Helper functions
function createMockUser(): User {
  return {
    id: 1,
    username: 'testuser',
    full_name: 'Test User',
    is_active: true,
    created_at: new Date().toISOString(),
    last_login: new Date().toISOString()
  }
}

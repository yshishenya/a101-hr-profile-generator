/**
 * Authentication service
 * Handles login, logout, token refresh, user info
 */

import api from './api'
import type { LoginRequest, LoginResponse, LogoutResponse, User } from '@/types/auth'

export const authService = {
  /**
   * Authenticate user with username and password
   * On success, returns JWT access token and user information
   *
   * @param credentials - User login credentials
   * @param credentials.username - Username for authentication
   * @param credentials.password - Password for authentication
   * @returns Promise resolving to login response with token and user info
   * @throws {AxiosError} When credentials are invalid or server error occurs
   *
   * @example
   * ```typescript
   * const response = await authService.login({
   *   username: 'admin',
   *   password: 'secret123'
   * })
   * console.log('Token:', response.access_token)
   * console.log('User:', response.user_info.username)
   * ```
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', credentials)
    return response.data
  },

  /**
   * Logout current user and invalidate session
   * Clears server-side session if applicable
   *
   * @returns Promise resolving to logout confirmation
   * @throws {AxiosError} When logout request fails
   *
   * @example
   * ```typescript
   * const response = await authService.logout()
   * if (response.success) {
   *   console.log('Logged out successfully')
   * }
   * ```
   */
  async logout(): Promise<LogoutResponse> {
    const response = await api.post<LogoutResponse>('/api/auth/logout')
    return response.data
  },

  /**
   * Retrieve current authenticated user information
   * Used to restore user session on app initialization
   *
   * @returns Promise resolving to user data
   * @throws {AxiosError} When token is invalid or expired (401)
   *
   * @example
   * ```typescript
   * try {
   *   const user = await authService.getCurrentUser()
   *   console.log('Current user:', user.username)
   * } catch (error) {
   *   // Token expired, redirect to login
   * }
   * ```
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },

  /**
   * Refresh expired JWT access token
   * Obtains new token using refresh token from cookies
   *
   * @returns Promise resolving to new access token and user info
   * @throws {AxiosError} When refresh token is invalid or expired
   *
   * @example
   * ```typescript
   * const response = await authService.refresh()
   * localStorage.setItem('token', response.access_token)
   * ```
   */
  async refresh(): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/refresh')
    return response.data
  },

  /**
   * Validate current JWT token without fetching user data
   * Lightweight check for token validity
   *
   * @returns Promise resolving to true if token is valid, false otherwise
   *
   * @example
   * ```typescript
   * const isValid = await authService.validate()
   * if (!isValid) {
   *   // Redirect to login
   * }
   * ```
   */
  async validate(): Promise<boolean> {
    try {
      await api.get('/api/auth/validate')
      return true
    } catch {
      return false
    }
  }
}

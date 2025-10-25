/**
 * Authentication service
 * Handles login, logout, token refresh, user info
 */

import api from './api'
import type { LoginRequest, LoginResponse, LogoutResponse, User } from '@/types/auth'

export const authService = {
  /**
   * Login user
   * POST /api/auth/login
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/login', credentials)
    return response.data
  },

  /**
   * Logout user
   * POST /api/auth/logout
   */
  async logout(): Promise<LogoutResponse> {
    const response = await api.post<LogoutResponse>('/api/auth/logout')
    return response.data
  },

  /**
   * Get current user info
   * GET /api/auth/me
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },

  /**
   * Refresh JWT token
   * POST /api/auth/refresh
   */
  async refresh(): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/api/auth/refresh')
    return response.data
  },

  /**
   * Validate current token
   * GET /api/auth/validate
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

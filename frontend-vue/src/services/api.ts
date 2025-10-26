/**
 * Axios instance with JWT interceptors
 * Automatically adds token to requests and handles 401 errors
 */

import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { logger } from '@/utils/logger'

// Create axios instance
const api: AxiosInstance = axios.create({
  // Use empty baseURL in development to enable Vite proxy
  // In production, set VITE_API_BASE_URL to the full backend URL
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: Add JWT token to headers
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage (same key as auth store)
    const token = localStorage.getItem('auth_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Development logging
    logger.debug(`→ ${config.method?.toUpperCase()} ${config.url}`, config.data)

    return config
  },
  (error: AxiosError) => {
    logger.error('Request error', error)
    return Promise.reject(error)
  }
)

// Response interceptor: Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => {
    // Development logging
    logger.debug(`← ${response.status} ${response.config.url}`, response.data)
    return response
  },
  (error: AxiosError) => {
    // Development logging
    logger.error(
      `← ${error.response?.status || 'NETWORK_ERROR'} ${error.config?.url}`,
      error.response?.data
    )

    if (error.response?.status === 401) {
      // Token expired or invalid
      // Emit custom event for auth store to handle
      // This maintains separation of concerns - api.ts handles HTTP, store handles state
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))

      // Don't redirect here - let router guard handle it
      // This prevents page reload and maintains SPA navigation
    }

    return Promise.reject(error)
  }
)

export default api

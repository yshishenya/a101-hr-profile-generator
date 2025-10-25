/**
 * Axios instance with JWT interceptors
 * Automatically adds token to requests and handles 401 errors
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8022',
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
    if (import.meta.env.DEV) {
      console.log(`→ ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }

    return config
  },
  (error: AxiosError) => {
    if (import.meta.env.DEV) {
      console.error('← Request error:', error)
    }
    return Promise.reject(error)
  }
)

// Response interceptor: Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => {
    // Development logging
    if (import.meta.env.DEV) {
      console.log(`← ${response.status} ${response.config.url}`, response.data)
    }
    return response
  },
  (error: AxiosError) => {
    // Development logging
    if (import.meta.env.DEV) {
      console.error(`← ${error.response?.status || 'NETWORK_ERROR'} ${error.config?.url}`, error.response?.data)
    }

    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token')

      // Redirect to login (if not already there)
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api

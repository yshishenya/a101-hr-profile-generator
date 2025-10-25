/**
 * Common API types
 */

export interface ApiError {
  message: string
  status?: number
  details?: any
}

export interface ApiResponse<T = any> {
  success: boolean
  timestamp?: string
  message?: string
  data?: T
}

export interface PaginationParams {
  page?: number
  limit?: number
}

export interface FilterParams {
  department?: string
  position?: string
  search?: string
  status?: string
}

export interface DashboardStats {
  positions_count: number
  profiles_count: number
  completion_percentage: number
  active_tasks_count: number
  last_updated?: string
}

export interface HealthCheckResponse {
  status: string
  timestamp: string
  uptime_seconds: number
  version: string
  environment: string
  components: {
    api: string
    core_modules: string
  }
  external_services: {
    openrouter_configured: boolean
    langfuse_configured: boolean
  }
}

/**
 * Common API types
 *
 * ALL backend endpoints now return BaseResponse format:
 * {
 *   "success": true,
 *   "timestamp": "2025-10-26T...",
 *   "message": "Optional message",
 *   ...other fields (task_id, data, etc.)
 * }
 */

export interface ApiError {
  message: string
  status?: number
  details?: Record<string, unknown>
}

/**
 * Base API response structure - all endpoints extend this
 * Backend BaseResponse model ensures consistent format
 */
export interface ApiResponse<T = unknown> {
  success: boolean
  timestamp?: string
  message?: string
  data?: T
}

/**
 * Organization positions response
 * GET /api/organization/positions
 */
export interface OrganizationPositionsResponse extends ApiResponse {
  data: {
    items: Array<{
      position_id: string
      position_name: string
      business_unit_id: string
      business_unit_name: string
      department_id?: string
      department_name?: string
      department_path: string
      profile_exists: boolean
      profile_id?: number
    }>
    total_count: number
    positions_with_profiles: number
    coverage_percentage: number
  }
}

/**
 * Generation start response
 * POST /api/generation/start
 */
export interface GenerationStartResponse extends ApiResponse {
  task_id: string
  status: string
  estimated_duration: number
}

/**
 * Task status response
 * GET /api/generation/{task_id}/status
 */
export interface TaskStatusResponse extends ApiResponse {
  task: {
    task_id: string
    status: 'queued' | 'processing' | 'completed' | 'failed'
    progress?: number
    current_step?: string
    error_message?: string
    created_at?: string
    started_at?: string
    completed_at?: string
  }
  result?: ProfileData
}

/**
 * Profile data structure
 */
export interface ProfileData {
  position_title: string
  department: string
  employee_name?: string
  basic_info: {
    position_title: string
    department: string
    business_unit?: string
    level?: number
    category?: string
  }
  responsibilities: Array<{
    title: string
    description: string
    importance?: string
  }>
  professional_skills: {
    technical?: Array<{ name: string; level?: string; description?: string }>
    management?: Array<{ name: string; level?: string; description?: string }>
    analytical?: Array<{ name: string; level?: string; description?: string }>
    communication?: Array<{ name: string; level?: string; description?: string }>
    other?: Array<{ name: string; level?: string; description?: string }>
  }
  corporate_competencies: string[]
  personal_qualities: string[]
  education_experience: {
    required_education?: string
    preferred_education?: string
    required_experience_years?: number
    preferred_experience?: string
  }
  career_paths: {
    vertical?: string[]
    horizontal?: string[]
    alternative?: string[]
  }
}

/**
 * Generation result response
 * GET /api/generation/{task_id}/result
 */
export interface GenerationResultResponse extends ApiResponse {
  success: boolean
  profile: ProfileData
  metadata: {
    generation_time_seconds: number
    input_tokens: number
    output_tokens: number
    total_tokens: number
    model_name: string
    temperature: number
  }
  errors: string[]
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

/**
 * Backend response structure for dashboard stats
 * Contains nested summary and metadata
 */
export interface DashboardStatsResponse {
  summary: {
    positions_count: number
    profiles_count: number
    completion_percentage: number
    active_tasks_count: number
  }
  metadata: {
    last_updated: string
  }
}

/**
 * Type guard to check if response has nested structure
 */
export function isDashboardStatsResponse(data: unknown): data is DashboardStatsResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'summary' in data &&
    typeof data.summary === 'object' &&
    data.summary !== null &&
    'positions_count' in data.summary
  )
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

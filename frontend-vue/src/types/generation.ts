/**
 * Profile generation types based on actual backend API
 * Backend: POST /api/generation/start, GET /api/generation/{task_id}/status
 */

import type { ProfileData } from './profile'

export interface GenerationRequest {
  department: string
  position: string
  employee_name?: string
  temperature?: number
  save_result?: boolean
}

export type TaskStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'

export interface GenerationTask {
  task_id: string
  status: TaskStatus
  progress: number | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  estimated_duration: number | null
  current_step: string | null
  error_message: string | null
}

export interface GenerationResponse {
  task_id: string
  status: string
  message: string
  estimated_duration: number | null
}

export interface GenerationResult {
  success: boolean
  profile: ProfileData // Full profile content with explicit structure
  metadata: {
    generation: {
      timestamp: string
      duration: number
      temperature: number
    }
    llm: {
      model: string
      tokens: {
        input: number
        output: number
        total: number
      }
    }
  }
}

// For bulk generation (frontend orchestration)
export interface BulkGenerationTask extends GenerationTask {
  position_name: string
  department_name: string
}

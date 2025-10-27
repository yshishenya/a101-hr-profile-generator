/**
 * Profile management types based on actual backend API
 * Backend: GET /api/profiles, GET /api/profiles/{id}
 */

import type { ProfileData as APIProfileData } from './api'

/**
 * Extended ProfileData that supports both API structure and legacy UI structure
 * This allows gradual migration from old to new profile structure
 */
export type ProfileData = APIProfileData & {
  // Legacy fields used by ProfileContent.vue
  competencies?: string[]
  requirements?: string[]
  skills?: {
    technical?: string[]
    soft?: string[]
    management?: string[]
  }
  education?: {
    required?: string
    preferred?: string
  }
  experience?: {
    years?: number
    description?: string
  }
}

/**
 * Generation metadata from backend
 * Matches the structure used in ProfileMetadata.vue component
 */
export interface GenerationMetadata {
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

export interface Position {
  id: string
  name: string
  department: string
  full_path: string
}

export type ProfileStatus = 'completed' | 'archived' | 'in_progress'

export interface Profile {
  profile_id: string
  department: string
  position: string
  employee_name: string | null
  status: ProfileStatus
  validation_score: number
  completeness_score: number
  current_version: number
  version_count: number
  created_at: string
  created_by_username: string
  actions: {
    download_json: string
    download_md: string
    download_docx: string
  }
}

export interface ProfileDetail {
  profile_id: string
  profile: ProfileData // Full profile content with explicit structure
  metadata: GenerationMetadata // Generation metadata with explicit structure
  created_at: string
  created_by_username: string
  actions: {
    download_json: string
    download_md: string
    download_docx: string
  }
}

export interface ProfilesListResponse {
  profiles: Profile[]
  pagination: {
    page: number
    limit: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  filters_applied: {
    department: string | null
    position: string | null
    search: string | null
    status: string | null
  }
}

export interface ProfileUpdateRequest {
  employee_name?: string
  status?: ProfileStatus
  profile_content?: Partial<ProfileData> // For inline editing (Week 7)
}

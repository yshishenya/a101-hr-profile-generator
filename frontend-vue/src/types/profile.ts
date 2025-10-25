/**
 * Profile management types based on actual backend API
 * Backend: GET /api/profiles, GET /api/profiles/{id}
 */

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
  profile: any // Full profile content (flexible structure)
  metadata: any // Generation metadata
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
  profile_content?: any // For inline editing (Week 7)
}

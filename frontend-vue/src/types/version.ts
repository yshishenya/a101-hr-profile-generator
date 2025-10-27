/**
 * Profile versioning types
 * Backend: GET /api/profiles/{id}/versions
 */

import type { ProfileData, GenerationMetadata } from './profile'

/**
 * Version type indicating how the version was created
 */
export type VersionType = 'generated' | 'regenerated' | 'edited'

/**
 * Single version item from versions list
 * Returned by: GET /api/profiles/{id}/versions
 */
export interface ProfileVersion {
  version_number: number
  created_at: string
  created_by_username: string
  version_type: VersionType
  validation_score: number | null
  completeness_score: number | null
  is_current: boolean
}

/**
 * Full version details including profile content
 * Returned by: GET /api/profiles/{id}/versions/{version}
 */
export interface ProfileVersionDetail {
  version_number: number
  profile_content: ProfileData
  generation_metadata: GenerationMetadata | null
  created_at: string
  created_by_username: string
  version_type: VersionType
  validation_score: number | null
  completeness_score: number | null
  is_current: boolean
}

/**
 * Response from GET /api/profiles/{id}/versions
 */
export interface ProfileVersionsResponse {
  versions: ProfileVersion[]
  current_version: number
  total_versions: number
}

/**
 * Request to set a version as active
 * PUT /api/profiles/{id}/versions/{version}/set-active
 */
export interface SetActiveVersionResponse {
  message: string
  profile_id: string
  previous_version: number
  current_version: number
}

/**
 * Response from DELETE /api/profiles/{id}/versions/{version}
 */
export interface DeleteVersionResponse {
  message: string
  profile_id: string
  deleted_version: number
  remaining_versions: number
}

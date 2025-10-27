/**
 * Unified Profiles Interface Types
 * Combines position catalog data with profile status and generation tasks
 */

/**
 * Unified position with profile status
 * Merges catalog position, profile data, and generation task status
 */
export interface UnifiedPosition {
  // Position metadata (from catalog)
  position_id: string
  position_name: string
  business_unit_id: string
  business_unit_name: string
  department_id?: string
  department_name: string
  department_path: string

  // Status (derived from multiple sources)
  status: PositionStatus

  // Profile data (if generated)
  profile_id?: number
  employee_name?: string | null
  current_version?: number
  version_count?: number
  quality_score?: number
  completeness_score?: number
  created_at?: string
  created_by?: string

  // Task data (if generating)
  task_id?: string
  progress?: number
  current_step?: string
  estimated_duration?: number

  // Actions available (computed based on status)
  actions: PositionActions
}

/**
 * Position status enum
 * Note: 'archived' is a profile status but can appear in unified view
 */
export type PositionStatus = 'generated' | 'not_generated' | 'generating' | 'archived'

/**
 * Available actions for a position
 * Computed based on current status
 */
export interface PositionActions {
  canView: boolean       // Can open profile viewer
  canGenerate: boolean   // Can start generation
  canDownload: boolean   // Can download profile
  canEdit: boolean       // Can edit profile metadata
  canDelete: boolean     // Can delete (archive) profile
  canCancel: boolean     // Can cancel generation
  canRegenerate: boolean // Can regenerate profile
}

/**
 * Profile version information
 * Used in version history and comparison
 */
export interface ProfileVersion {
  version_number: number
  created_at: string
  created_by: string
  type: VersionType
  quality_score: number
  completeness_score: number
  changes_summary?: string[]
  is_current: boolean
}

/**
 * Version creation type
 */
export type VersionType = 'generated' | 'regenerated' | 'edited'

/**
 * View mode for profiles page
 */
export type ViewMode = 'table' | 'tree'

/**
 * Filters for profiles list
 */
export interface ProfileFilters {
  search: string
  departments: string[]  // Changed from department (multi-select)
  status: StatusFilter
  dateRange: DateRangeFilter | null
  // qualityRange removed from UI - kept in backend for potential future use
}

/**
 * Status filter options
 */
export type StatusFilter = 'all' | 'generated' | 'not_generated' | 'generating'

/**
 * Date range filter
 */
export interface DateRangeFilter {
  type: 'created' | 'updated'
  from: string | null  // ISO 8601 date string (YYYY-MM-DD)
  to: string | null    // ISO 8601 date string (YYYY-MM-DD)
}

/**
 * Quality score range filter
 */
export interface QualityRangeFilter {
  min: number  // 0-100
  max: number  // 0-100
}

/**
 * Date range preset for quick selection
 */
export type DateRangePreset = 'last_7_days' | 'last_30_days' | 'last_90_days' | 'all_time' | 'custom'

/**
 * Version comparison result
 */
export interface VersionComparison {
  v1: ProfileVersion
  v2: ProfileVersion
  differences: {
    added: string[]
    removed: string[]
    modified: string[]
    summary: ChangeDescription[]
  }
}

/**
 * JSON-like value type for profile changes
 */
export type ProfileValue = string | number | boolean | null | ProfileValue[] | { [key: string]: ProfileValue }

/**
 * Change description for version comparison
 */
export interface ChangeDescription {
  type: 'added' | 'removed' | 'modified'
  field: string
  description: string
  old_value?: ProfileValue
  new_value?: ProfileValue
}

/**
 * Statistics for overview
 */
export interface ProfileStatistics {
  total_positions: number
  generated_count: number
  generating_count: number
  not_generated_count: number
  coverage_percentage: number
  last_updated: string
}

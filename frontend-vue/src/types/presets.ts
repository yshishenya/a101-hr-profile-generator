/**
 * Filter Presets Types
 * Defines types for saving and managing filter presets
 */

import type { ProfileFilters } from './unified'

/**
 * Filter preset
 * Saved combination of filters that can be quickly applied
 */
export interface FilterPreset {
  id: string
  name: string
  filters: ProfileFilters
  created_at: string  // ISO 8601 timestamp
  is_default?: boolean
  icon?: string  // MDI icon name
  color?: string  // Vuetify color name
}

/**
 * Filter presets storage schema
 * Stored in localStorage
 */
export interface FilterPresetsStorage {
  version: number  // Schema version for migrations
  presets: FilterPreset[]
  activePresetId: string | null
  maxPresets: number  // Maximum number of presets (default: 10)
}

/**
 * Preset creation/update data
 * Used when saving a new preset
 */
export interface PresetCreateData {
  name: string
  filters: ProfileFilters
  icon?: string
  color?: string
  is_default?: boolean
}

/**
 * Default preset configurations
 * Built-in presets that are always available
 */
export interface DefaultPreset {
  id: string
  name: string
  description: string
  icon: string
  color: string
  createFilters: () => Partial<ProfileFilters>
}

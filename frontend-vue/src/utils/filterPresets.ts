/**
 * Filter Presets Management Utility
 * Handles saving, loading, and managing filter presets in localStorage
 */

import type { FilterPreset, FilterPresetsStorage, PresetCreateData, DefaultPreset } from '@/types/presets'
import type { ProfileFilters } from '@/types/unified'

// Constants
const STORAGE_KEY = 'hr_filter_presets'
const STORAGE_VERSION = 1
const MAX_PRESETS = 10
const MAX_PRESET_NAME_LENGTH = 50

/**
 * Default preset configurations
 * These are always available and cannot be deleted
 */
export const DEFAULT_PRESETS: DefaultPreset[] = [
  {
    id: 'preset_recently_generated',
    name: 'Недавно сгенерированные',
    description: 'Профили, созданные за последние 7 дней',
    icon: 'mdi-clock-outline',
    color: 'primary',
    createFilters: () => ({
      status: 'generated' as const,
      dateRange: {
        type: 'created' as const,
        from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] as string | null,
        to: new Date().toISOString().split('T')[0] as string | null
      }
    })
  },
  {
    id: 'preset_high_quality',
    name: 'Высокое качество',
    description: 'Профили с качеством выше 80%',
    icon: 'mdi-star',
    color: 'success',
    createFilters: () => ({
      status: 'generated',
      qualityRange: { min: 80, max: 100 }
    })
  },
  {
    id: 'preset_incomplete',
    name: 'Не заполненные',
    description: 'Позиции без профилей',
    icon: 'mdi-alert-circle-outline',
    color: 'warning',
    createFilters: () => ({
      status: 'not_generated'
    })
  }
]

/**
 * Generate unique preset ID
 */
function generatePresetId(): string {
  return `preset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Validate preset data
 * @throws Error if validation fails
 */
function validatePreset(preset: Partial<FilterPreset>): void {
  if (!preset.name || preset.name.trim().length === 0) {
    throw new Error('Preset name is required')
  }

  if (preset.name.length > MAX_PRESET_NAME_LENGTH) {
    throw new Error(`Preset name must be ${MAX_PRESET_NAME_LENGTH} characters or less`)
  }

  if (!preset.filters) {
    throw new Error('Preset filters are required')
  }
}

/**
 * Get default storage structure
 */
function getDefaultStorage(): FilterPresetsStorage {
  return {
    version: STORAGE_VERSION,
    presets: [],
    activePresetId: null,
    maxPresets: MAX_PRESETS
  }
}

/**
 * Load presets from localStorage
 */
export function loadPresets(): FilterPresetsStorage {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) {
      return getDefaultStorage()
    }

    const parsed = JSON.parse(stored) as FilterPresetsStorage

    // Validate version and migrate if needed
    if (parsed.version !== STORAGE_VERSION) {
      return migrateStorage(parsed)
    }

    return parsed
  } catch (error: unknown) {
    console.error('Failed to load filter presets:', error)
    return getDefaultStorage()
  }
}

/**
 * Save presets to localStorage
 */
export function savePresets(storage: FilterPresetsStorage): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(storage))
  } catch (error: unknown) {
    console.error('Failed to save filter presets:', error)
    throw new Error('Failed to save presets. Storage may be full.')
  }
}

/**
 * Migrate storage from old version
 */
function migrateStorage(_oldStorage: FilterPresetsStorage): FilterPresetsStorage {
  // For now, just reset to default if version mismatch
  // In future, implement proper migration logic
  console.warn('Filter presets storage version mismatch. Resetting to defaults.')
  return getDefaultStorage()
}

/**
 * Create new preset
 */
export function createPreset(data: PresetCreateData): FilterPreset {
  validatePreset(data)

  const preset: FilterPreset = {
    id: generatePresetId(),
    name: data.name.trim(),
    filters: data.filters,
    created_at: new Date().toISOString(),
    is_default: data.is_default || false,
    icon: data.icon,
    color: data.color
  }

  return preset
}

/**
 * Add preset to storage
 * @throws Error if max presets reached
 */
export function addPreset(preset: FilterPreset): FilterPresetsStorage {
  const storage = loadPresets()

  if (storage.presets.length >= storage.maxPresets) {
    throw new Error(`Maximum ${storage.maxPresets} presets allowed. Please delete one first.`)
  }

  // Check for duplicate names
  const duplicateName = storage.presets.find(p => p.name === preset.name)
  if (duplicateName) {
    throw new Error(`Preset with name "${preset.name}" already exists`)
  }

  storage.presets.push(preset)
  savePresets(storage)

  return storage
}

/**
 * Update existing preset
 */
export function updatePreset(presetId: string, updates: Partial<FilterPreset>): FilterPresetsStorage {
  const storage = loadPresets()
  const index = storage.presets.findIndex(p => p.id === presetId)

  if (index === -1) {
    throw new Error('Preset not found')
  }

  const preset = storage.presets[index]!
  const updated: FilterPreset = {
    ...preset,
    ...updates,
    id: preset.id, // Prevent ID change
    name: updates.name || preset.name,
    filters: updates.filters || preset.filters,
    created_at: preset.created_at // Prevent creation date change
  }

  validatePreset(updated)
  storage.presets[index] = updated
  savePresets(storage)

  return storage
}

/**
 * Delete preset
 */
export function deletePreset(presetId: string): FilterPresetsStorage {
  const storage = loadPresets()
  const index = storage.presets.findIndex(p => p.id === presetId)

  if (index === -1) {
    throw new Error('Preset not found')
  }

  storage.presets.splice(index, 1)

  // Clear active preset if it was deleted
  if (storage.activePresetId === presetId) {
    storage.activePresetId = null
  }

  savePresets(storage)
  return storage
}

/**
 * Get preset by ID
 */
export function getPreset(presetId: string): FilterPreset | null {
  const storage = loadPresets()
  return storage.presets.find(p => p.id === presetId) || null
}

/**
 * Get all presets (custom + defaults)
 */
export function getAllPresets(): FilterPreset[] {
  const storage = loadPresets()

  // Convert default presets to FilterPreset format
  const defaults: FilterPreset[] = DEFAULT_PRESETS.map(dp => ({
    id: dp.id,
    name: dp.name,
    filters: dp.createFilters() as ProfileFilters,
    created_at: '',
    is_default: true,
    icon: dp.icon,
    color: dp.color
  }))

  return [...defaults, ...storage.presets]
}

/**
 * Set active preset
 */
export function setActivePreset(presetId: string | null): void {
  const storage = loadPresets()
  storage.activePresetId = presetId
  savePresets(storage)
}

/**
 * Get active preset ID
 */
export function getActivePresetId(): string | null {
  const storage = loadPresets()
  return storage.activePresetId
}

/**
 * Clear all custom presets (keeps defaults)
 */
export function clearAllPresets(): void {
  const storage = getDefaultStorage()
  savePresets(storage)
}

/**
 * Check if preset name is available
 */
export function isPresetNameAvailable(name: string, excludeId?: string): boolean {
  const storage = loadPresets()

  // Check against default presets
  const defaultMatch = DEFAULT_PRESETS.find(dp => dp.name === name)
  if (defaultMatch) {
    return false
  }

  // Check against custom presets
  const customMatch = storage.presets.find(p => p.name === name && p.id !== excludeId)
  return !customMatch
}

/**
 * Export presets as JSON string (for backup)
 */
export function exportPresets(): string {
  const storage = loadPresets()
  return JSON.stringify(storage, null, 2)
}

/**
 * Import presets from JSON string (for restore)
 * @throws Error if import fails
 */
export function importPresets(jsonString: string): FilterPresetsStorage {
  try {
    const imported = JSON.parse(jsonString) as FilterPresetsStorage

    // Validate structure
    if (!imported.presets || !Array.isArray(imported.presets)) {
      throw new Error('Invalid presets format')
    }

    // Validate each preset
    imported.presets.forEach(preset => validatePreset(preset))

    // Merge with existing (don't overwrite)
    const storage = loadPresets()
    const existingIds = new Set(storage.presets.map(p => p.id))

    imported.presets.forEach(preset => {
      if (!existingIds.has(preset.id) && storage.presets.length < storage.maxPresets) {
        storage.presets.push(preset)
      }
    })

    savePresets(storage)
    return storage
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(`Failed to import presets: ${error.message}`)
    }
    throw new Error('Failed to import presets: Unknown error')
  }
}

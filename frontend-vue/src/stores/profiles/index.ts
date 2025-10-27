/**
 * Profiles Store - Unified profiles and positions management
 *
 * Main entry point for the profiles store.
 * Handles unified view of all positions with their profile status.
 * Combines catalog data, profile data, and generation tasks.
 *
 * This is a modular store split into:
 * - types.ts: Local types and error classes
 * - state.ts: Reactive state definitions
 * - getters.ts: Computed properties
 * - actions-crud.ts: CRUD operations
 * - actions-filters.ts: Filter and pagination
 * - actions-unified.ts: Unified view logic
 */

import { defineStore } from 'pinia'
import { DEFAULT_PAGE, DEFAULT_PAGE_SIZE } from './types'

// State
import {
  unifiedPositions,
  profiles,
  currentProfile,
  loading,
  error,
  viewMode,
  unifiedFilters,
  pagination,
  filters
} from './state'

// Getters
import {
  totalProfiles,
  currentPage,
  hasMore,
  hasPrevious,
  profilesCount,
  hasActiveFilters,
  filteredPositions,
  statistics,
  departments
} from './getters'

// CRUD Actions
import {
  loadProfiles,
  loadProfile,
  updateProfile,
  updateProfileContent,
  deleteProfile,
  downloadProfile,
  clearError,
  clearCurrentProfile
} from './actions-crud'

// Filter Actions
import {
  setFilters,
  clearFilters,
  goToPage,
  nextPage,
  previousPage
} from './actions-filters'

// Unified Actions
import {
  loadUnifiedData,
  bulkGenerate,
  bulkCancel
} from './actions-unified'

/**
 * Profiles store with unified position management
 *
 * Provides both legacy profile management and new unified interface
 * that combines catalog positions with profile generation status
 */
export const useProfilesStore = defineStore('profiles', () => {
  /**
   * Reset all state to defaults
   */
  function reset(): void {
    profiles.value = []
    currentProfile.value = null
    unifiedPositions.value = []
    loading.value = false
    error.value = null
    pagination.value = {
      page: DEFAULT_PAGE,
      limit: DEFAULT_PAGE_SIZE,
      total: 0,
      total_pages: 0,
      has_next: false,
      has_prev: false
    }
    filters.value = {
      department: undefined,
      position: undefined,
      search: undefined,
      status: undefined
    }
    unifiedFilters.value = {
      search: '',
      departments: [],
      status: 'all',
      dateRange: null
    }
  }

  return {
    // Legacy state (for backward compatibility)
    profiles,
    currentProfile,
    loading,
    error,
    pagination,
    filters,

    // Unified state
    unifiedPositions,
    viewMode,
    unifiedFilters,

    // Legacy computed
    totalProfiles,
    currentPage,
    hasMore,
    hasPrevious,
    profilesCount,
    hasActiveFilters,

    // Unified computed
    filteredPositions,
    statistics,
    departments,

    // Legacy actions
    loadProfiles,
    loadProfile,
    updateProfile,
    updateProfileContent,
    deleteProfile,
    downloadProfile,
    setFilters,
    clearFilters,
    goToPage,
    nextPage,
    previousPage,
    clearError,
    clearCurrentProfile,

    // Unified actions
    loadUnifiedData,
    bulkGenerate,
    bulkCancel,

    reset
  }
})

/**
 * CRUD operations for profiles store
 * Contains create, read, update, delete operations
 */

import type { AxiosError } from 'axios'
import profileService from '@/services/profile.service'
import type {
  ProfilesListResponse,
  ProfileUpdateRequest
} from '@/types/profile'
import type { PaginationParams, FilterParams } from '@/types/api'
import { ProfileError } from './types'
import {
  profiles,
  currentProfile,
  pagination,
  filters,
  loading,
  error
} from './state'

/**
 * Load profiles with pagination and filters
 *
 * @param options - Override pagination/filter options
 * @throws ProfileError if loading fails
 *
 * @example
 * ```typescript
 * await loadProfiles({ page: 2, department: 'IT' })
 * ```
 */
export async function loadProfiles(options?: Partial<PaginationParams & FilterParams>): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const params = {
      page: options?.page ?? pagination.value.page,
      limit: options?.limit ?? pagination.value.limit,
      department: options?.department ?? filters.value.department,
      position: options?.position ?? filters.value.position,
      search: options?.search ?? filters.value.search,
      status: options?.status ?? filters.value.status
    }

    // Remove undefined values
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([_, v]) => v !== undefined)
    )

    const response: ProfilesListResponse = await profileService.listProfiles(cleanParams)

    // Update state
    profiles.value = response.profiles
    pagination.value = response.pagination

    // Store filters that were actually applied
    if (response.filters_applied) {
      filters.value = {
        department: response.filters_applied.department || undefined,
        position: response.filters_applied.position || undefined,
        search: response.filters_applied.search || undefined,
        status: response.filters_applied.status || undefined
      }
    }

    loading.value = false
  } catch (err) {
    const axiosError = err as AxiosError<{ message?: string }>
    error.value = axiosError.response?.data?.message || 'Failed to load profiles'
    loading.value = false

    throw new ProfileError(
      error.value,
      'LOAD_FAILED',
      err
    )
  }
}

/**
 * Load single profile by ID
 *
 * @param id - Profile ID
 * @throws ProfileError if loading fails
 *
 * @example
 * ```typescript
 * await loadProfile('prof_123')
 * console.log(currentProfile.value?.profile)
 * ```
 */
export async function loadProfile(id: string): Promise<void> {
  if (!id?.trim()) {
    throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
  }

  loading.value = true
  error.value = null

  try {
    const profile = await profileService.getProfile(id)
    currentProfile.value = profile
    loading.value = false
  } catch (err) {
    const axiosError = err as AxiosError<{ message?: string }>
    error.value = axiosError.response?.data?.message || 'Failed to load profile'
    loading.value = false

    throw new ProfileError(
      error.value,
      axiosError.response?.status === 404 ? 'NOT_FOUND' : 'LOAD_FAILED',
      err
    )
  }
}

/**
 * Update profile metadata or content
 * Automatically refreshes profile after update
 *
 * @param id - Profile ID
 * @param data - Fields to update
 * @throws ProfileError if update fails
 *
 * @example
 * ```typescript
 * await updateProfile('prof_123', {
 *   employee_name: 'Иван Петров',
 *   status: 'completed'
 * })
 * ```
 */
export async function updateProfile(id: string, data: ProfileUpdateRequest): Promise<void> {
  if (!id?.trim()) {
    throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
  }

  loading.value = true
  error.value = null

  try {
    await profileService.updateProfile(id, data)

    // Refresh the profile if it's currently loaded
    if (currentProfile.value?.profile_id === id) {
      await loadProfile(id)
    }

    // Refresh list if profile is in current page
    const profileIndex = profiles.value.findIndex(p => p.profile_id === id)
    if (profileIndex !== -1) {
      await loadProfiles()
    }

    loading.value = false
  } catch (err) {
    const axiosError = err as AxiosError<{ message?: string }>
    error.value = axiosError.response?.data?.message || 'Failed to update profile'
    loading.value = false

    throw new ProfileError(
      error.value,
      'UPDATE_FAILED',
      err
    )
  }
}

/**
 * Update profile content (full profile_data)
 * Updates all sections of the profile
 * Automatically refreshes profile after update
 *
 * @param id - Profile ID
 * @param profileData - Complete profile_data object with all sections
 * @throws ProfileError if update fails
 *
 * @example
 * ```typescript
 * await updateProfileContent('prof_123', {
 *   responsibility_areas: [...],
 *   professional_skills: [...],
 *   corporate_competencies: [...],
 *   ...
 * })
 * ```
 */
export async function updateProfileContent(id: string, profileData: Record<string, unknown>): Promise<void> {
  if (!id?.trim()) {
    throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
  }

  loading.value = true
  error.value = null

  try {
    await profileService.updateProfileContent(id, profileData)

    // Refresh the profile if it's currently loaded
    if (currentProfile.value?.profile_id === id) {
      await loadProfile(id)
    }

    // Refresh list if profile is in current page
    const profileIndex = profiles.value.findIndex(p => p.profile_id === id)
    if (profileIndex !== -1) {
      await loadProfiles()
    }

    loading.value = false
  } catch (err) {
    const axiosError = err as AxiosError<{ message?: string }>
    error.value = axiosError.response?.data?.message || 'Failed to update profile content'
    loading.value = false

    throw new ProfileError(
      error.value,
      'UPDATE_FAILED',
      err
    )
  }
}

/**
 * Archive (soft delete) a profile
 * Removes profile from list after archiving
 *
 * @param id - Profile ID to archive
 * @throws ProfileError if archiving fails
 *
 * @example
 * ```typescript
 * await deleteProfile('prof_123')
 * ```
 */
export async function deleteProfile(id: string): Promise<void> {
  if (!id?.trim()) {
    throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
  }

  loading.value = true
  error.value = null

  try {
    await profileService.archiveProfile(id)

    // Remove from local state
    profiles.value = profiles.value.filter(p => p.profile_id !== id)

    // Clear current profile if it was deleted
    if (currentProfile.value?.profile_id === id) {
      currentProfile.value = null
    }

    // Update pagination total
    if (pagination.value.total > 0) {
      pagination.value.total--
    }

    loading.value = false
  } catch (err) {
    const axiosError = err as AxiosError<{ message?: string }>
    error.value = axiosError.response?.data?.message || 'Failed to delete profile'
    loading.value = false

    throw new ProfileError(
      error.value,
      'DELETE_FAILED',
      err
    )
  }
}

/**
 * Download profile in specified format
 * Creates temporary download link
 *
 * @param id - Profile ID
 * @param format - Download format (json, md, docx)
 * @throws ProfileError if download fails
 *
 * @example
 * ```typescript
 * await downloadProfile('prof_123', 'json')
 * ```
 */
export async function downloadProfile(id: string, format: 'json' | 'md' | 'docx'): Promise<void> {
  if (!id?.trim()) {
    throw new ProfileError('Profile ID is required', 'VALIDATION_ERROR')
  }

  try {
    let blob: Blob

    switch (format) {
      case 'json':
        blob = await profileService.downloadJSON(id)
        break
      case 'md':
        blob = await profileService.downloadMarkdown(id)
        break
      case 'docx':
        blob = await profileService.downloadDOCX(id)
        break
      default:
        throw new ProfileError(`Unsupported format: ${format}`, 'VALIDATION_ERROR')
    }

    // Create download link
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `profile_${id}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (err) {
    const axiosError = err as AxiosError<{ message?: string }>
    const errorMessage = axiosError.response?.data?.message || `Failed to download ${format.toUpperCase()}`

    throw new ProfileError(
      errorMessage,
      'DOWNLOAD_FAILED',
      err
    )
  }
}

/**
 * Clear any error messages
 */
export function clearError(): void {
  error.value = null
}

/**
 * Reset current profile
 * Used when navigating away from detail view
 */
export function clearCurrentProfile(): void {
  currentProfile.value = null
}

/**
 * Profile Service - Profile management and downloads
 * CRUD operations for generated employee profiles
 */

import api from './api'
import type {
  Profile,
  ProfileDetail,
  ProfilesListResponse,
  ProfileUpdateRequest
} from '@/types/profile'
import type { PaginationParams, FilterParams } from '@/types/api'

/**
 * Parameters for profile listing with pagination and filters
 */
export interface ListProfilesParams extends PaginationParams, FilterParams {}

/**
 * Get paginated list of profiles with optional filters
 *
 * @param params - Pagination and filter parameters
 * @returns Promise<ProfilesListResponse> Profiles list with pagination info
 * @throws AxiosError if request fails
 *
 * @example
 * const response = await profileService.listProfiles({
 *   page: 1,
 *   limit: 20,
 *   department: 'Отдел разработки',
 *   status: 'completed'
 * })
 * console.log(`Found ${response.pagination.total} profiles`)
 */
export async function listProfiles(params?: ListProfilesParams): Promise<ProfilesListResponse> {
  const response = await api.get<ProfilesListResponse>('/api/profiles/', { params })
  return response.data
}

/**
 * Get detailed information about single profile
 * Includes full profile content and metadata
 *
 * @param id - Profile ID
 * @returns Promise<ProfileDetail> Full profile with content
 * @throws AxiosError if request fails (404 if not found)
 *
 * @example
 * const profile = await profileService.getProfile('prof_123')
 * console.log('Profile:', profile.profile)
 */
export async function getProfile(id: string): Promise<ProfileDetail> {
  const response = await api.get<ProfileDetail>(`/api/profiles/${id}`)
  return response.data
}

/**
 * Update profile metadata (name, status, or content)
 *
 * @param id - Profile ID
 * @param data - Fields to update
 * @returns Promise<Profile> Updated profile
 * @throws AxiosError if request fails
 *
 * @example
 * const updated = await profileService.updateProfile('prof_123', {
 *   employee_name: 'Иван Петров',
 *   status: 'completed'
 * })
 */
export async function updateProfile(id: string, data: ProfileUpdateRequest): Promise<Profile> {
  const response = await api.put<Profile>(`/api/profiles/${id}`, data)
  return response.data
}

/**
 * Archive profile (soft delete)
 * Profile can be restored later
 *
 * @param id - Profile ID to archive
 * @returns Promise<void>
 * @throws AxiosError if request fails
 *
 * @example
 * await profileService.archiveProfile('prof_123')
 */
export async function archiveProfile(id: string): Promise<void> {
  await api.delete(`/api/profiles/${id}`)
}

/**
 * Restore archived profile
 * Returns profile to 'completed' status
 *
 * @param id - Profile ID to restore
 * @returns Promise<Profile> Restored profile
 * @throws AxiosError if request fails
 *
 * @example
 * const restored = await profileService.restoreProfile('prof_123')
 */
export async function restoreProfile(id: string): Promise<Profile> {
  const response = await api.post<Profile>(`/api/profiles/${id}/restore`)
  return response.data
}

/**
 * Download profile as JSON file
 * Returns Blob for file download
 *
 * @param id - Profile ID
 * @returns Promise<Blob> JSON file content
 * @throws AxiosError if request fails
 *
 * @example
 * const blob = await profileService.downloadJSON('prof_123')
 * const url = URL.createObjectURL(blob)
 * const link = document.createElement('a')
 * link.href = url
 * link.download = 'profile.json'
 * link.click()
 */
export async function downloadJSON(id: string): Promise<Blob> {
  const response = await api.get<Blob>(`/api/profiles/${id}/download/json`, {
    responseType: 'blob'
  })
  return response.data
}

/**
 * Download profile as Markdown file
 * Returns Blob for file download
 *
 * @param id - Profile ID
 * @returns Promise<Blob> Markdown file content
 * @throws AxiosError if request fails
 *
 * @example
 * const blob = await profileService.downloadMarkdown('prof_123')
 * const url = URL.createObjectURL(blob)
 * const link = document.createElement('a')
 * link.href = url
 * link.download = 'profile.md'
 * link.click()
 */
export async function downloadMarkdown(id: string): Promise<Blob> {
  const response = await api.get<Blob>(`/api/profiles/${id}/download/md`, {
    responseType: 'blob'
  })
  return response.data
}

/**
 * Download profile as DOCX file
 * Returns Blob for file download
 *
 * @param id - Profile ID
 * @returns Promise<Blob> DOCX file content
 * @throws AxiosError if request fails
 *
 * @example
 * const blob = await profileService.downloadDOCX('prof_123')
 * const url = URL.createObjectURL(blob)
 * const link = document.createElement('a')
 * link.href = url
 * link.download = 'profile.docx'
 * link.click()
 */
export async function downloadDOCX(id: string): Promise<Blob> {
  const response = await api.get<Blob>(`/api/profiles/${id}/download/docx`, {
    responseType: 'blob'
  })
  return response.data
}

export default {
  listProfiles,
  getProfile,
  updateProfile,
  archiveProfile,
  restoreProfile,
  downloadJSON,
  downloadMarkdown,
  downloadDOCX
}

/**
 * Profile Versions Management Composable
 *
 * Handles all versions-related logic for profile viewer:
 * - Loading versions list
 * - Setting active version
 * - Downloading specific version
 * - Deleting version
 *
 * @module composables/useProfileVersions
 */

import { ref, watch, type ComputedRef, type Ref } from 'vue'
import { logger } from '@/utils/logger'
import profileService from '@/services/profile.service'
import { useAnalytics } from '@/composables/useAnalytics'
import type { ProfileVersion } from '@/types/version'
import {
  VersionNotFoundError,
  CannotDeleteCurrentVersionError,
  CannotDeleteLastVersionError,
  VersionActivationError,
  VersionsLoadError
} from '@/utils/errors'

/**
 * Snackbar state interface
 */
export interface SnackbarState {
  show: boolean
  message: string
  color: 'success' | 'error' | 'info' | 'warning'
}

/**
 * Composable return type
 */
export interface UseProfileVersionsReturn {
  /** List of all profile versions */
  versions: Ref<ProfileVersion[]>
  /** Loading state for versions */
  versionsLoading: Ref<boolean>
  /** Error message if loading failed */
  versionsError: Ref<string | null>
  /** Snackbar state for user notifications */
  snackbar: Ref<SnackbarState>
  /** Load versions list from API */
  loadVersions: () => Promise<void>
  /** Set specific version as active */
  handleSetActive: (versionNumber: number) => Promise<void>
  /** Download specific version in given format */
  handleVersionDownload: (versionNumber: number, format: 'json' | 'md' | 'docx') => Promise<void>
  /** Delete specific version */
  handleDeleteVersion: (versionNumber: number) => Promise<void>
}

/**
 * Composable for managing profile versions
 *
 * @param profileId - Computed ref with current profile ID
 * @param activeTab - Ref to current active tab (to trigger loading)
 * @param onVersionChanged - Callback to execute after version changes (set active/delete)
 * @returns Versions state and management functions
 *
 * @example
 * ```typescript
 * const profileId = computed(() => props.profile?.profile_id)
 * const {
 *   versions,
 *   versionsLoading,
 *   versionsError,
 *   loadVersions,
 *   handleSetActive,
 *   handleVersionDownload,
 *   handleDeleteVersion
 * } = useProfileVersions(profileId, activeTab, async () => {
 *   await reloadProfile()
 * })
 * ```
 */
export function useProfileVersions(
  profileId: ComputedRef<string | undefined>,
  activeTab: Ref<string>,
  onVersionChanged?: () => Promise<void>
): UseProfileVersionsReturn {
  // State
  const versions = ref<ProfileVersion[]>([])
  const versionsLoading = ref(false)
  const versionsError = ref<string | null>(null)
  const snackbar = ref<SnackbarState>({
    show: false,
    message: '',
    color: 'success'
  })

  // Analytics tracking
  const analytics = useAnalytics()

  /**
   * Show notification to user
   *
   * @param message - Notification message
   * @param color - Notification color/type
   */
  function showNotification(message: string, color: SnackbarState['color'] = 'success'): void {
    snackbar.value = {
      show: true,
      message,
      color
    }
  }

  /**
   * Load versions list from API
   * Sets loading state and handles errors
   *
   * @throws Will not throw, errors are stored in versionsError
   */
  async function loadVersions(): Promise<void> {
    if (!profileId.value) return

    versionsLoading.value = true
    versionsError.value = null

    try {
      const response = await profileService.getProfileVersions(String(profileId.value))
      versions.value = response.versions

      // Track versions list viewed
      analytics.trackVersionListViewed(
        String(profileId.value),
        response.total_versions,
        response.current_version
      )
    } catch (err: unknown) {
      logger.error('Failed to load versions', err)

      let errorMessage = 'Не удалось загрузить версии'

      if (err instanceof VersionNotFoundError) {
        errorMessage = 'Профиль не найден'
      } else if (err instanceof VersionsLoadError) {
        errorMessage = 'Ошибка загрузки версий. Попробуйте позже'
      } else if (err instanceof Error) {
        errorMessage = err.message
      }

      versionsError.value = errorMessage
      showNotification(errorMessage, 'error')
    } finally {
      versionsLoading.value = false
    }
  }

  /**
   * Set specific version as active/current
   * Reloads profile and versions list after success
   *
   * @param versionNumber - Version number to set as active
   * @throws Will not throw, errors are logged
   */
  async function handleSetActive(versionNumber: number): Promise<void> {
    if (!profileId.value) return

    try {
      const response = await profileService.setActiveVersion(String(profileId.value), versionNumber)

      // Track version activation
      analytics.trackVersionActivated(
        String(profileId.value),
        response.previous_version,
        response.current_version
      )

      // Reload profile detail to show new current version
      if (onVersionChanged) {
        await onVersionChanged()
      }

      // Reload versions list to update is_current flags
      await loadVersions()

      // Show success notification
      showNotification(`Версия ${versionNumber} успешно активирована`, 'success')

      // Switch back to content tab to show the activated version
      activeTab.value = 'content'
    } catch (err: unknown) {
      logger.error('Failed to set active version', err)

      let errorMessage = 'Не удалось активировать версию'

      if (err instanceof VersionNotFoundError) {
        errorMessage = `Версия ${versionNumber} не найдена`
      } else if (err instanceof VersionActivationError) {
        errorMessage = `Ошибка активации версии ${versionNumber}. Попробуйте позже`
      } else if (err instanceof Error) {
        errorMessage = err.message
      }

      showNotification(errorMessage, 'error')
    }
  }

  /**
   * Download specific version in given format
   * Opens download URL in new window
   *
   * @param versionNumber - Version number to download
   * @param format - Export format (json, md, or docx)
   * @throws Will not throw, errors are logged
   */
  async function handleVersionDownload(
    versionNumber: number,
    format: 'json' | 'md' | 'docx'
  ): Promise<void> {
    if (!profileId.value) return

    try {
      const url = `/api/profiles/${profileId.value}/download/${format}?version=${versionNumber}`
      window.open(url, '_blank')

      // Track version download
      analytics.trackVersionDownloaded(String(profileId.value), versionNumber, format)

      showNotification(`Версия ${versionNumber} скачивается...`, 'info')
    } catch (err: unknown) {
      logger.error('Failed to download version', err)
      const errorMessage = err instanceof Error ? err.message : 'Не удалось скачать версию'
      showNotification(errorMessage, 'error')
    }
  }

  /**
   * Delete specific version
   * Reloads versions list after success
   *
   * @param versionNumber - Version number to delete
   * @throws Will not throw, errors are logged
   */
  async function handleDeleteVersion(versionNumber: number): Promise<void> {
    if (!profileId.value) return

    try {
      const response = await profileService.deleteVersion(String(profileId.value), versionNumber)

      // Track version deletion
      analytics.trackVersionDeleted(
        String(profileId.value),
        versionNumber,
        response.remaining_versions
      )

      // Show success notification
      showNotification(`Версия ${versionNumber} успешно удалена`, 'success')

      // Reload versions list
      await loadVersions()
    } catch (err: unknown) {
      logger.error('Failed to delete version', err)

      let errorMessage = 'Не удалось удалить версию'

      if (err instanceof CannotDeleteCurrentVersionError) {
        errorMessage = 'Нельзя удалить текущую активную версию'
      } else if (err instanceof CannotDeleteLastVersionError) {
        errorMessage = 'Нельзя удалить последнюю версию профиля'
      } else if (err instanceof VersionNotFoundError) {
        errorMessage = `Версия ${versionNumber} не найдена`
      } else if (err instanceof Error) {
        errorMessage = err.message
      }

      showNotification(errorMessage, 'error')
    }
  }

  // Load versions when switching to versions tab
  watch(activeTab, async (newTab) => {
    if (newTab === 'versions' && profileId.value && versions.value.length === 0) {
      await loadVersions()
    }
  })

  return {
    versions,
    versionsLoading,
    versionsError,
    snackbar,
    loadVersions,
    handleSetActive,
    handleVersionDownload,
    handleDeleteVersion
  }
}

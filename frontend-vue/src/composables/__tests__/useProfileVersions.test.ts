/**
 * Unit tests for useProfileVersions composable
 * Tests versions management, state handling, and user interactions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref, computed, nextTick } from 'vue'
import { useProfileVersions } from '../useProfileVersions'
import type { ProfileVersion } from '@/types/version'
import type { ProfileVersionsResponse, SetActiveVersionResponse, DeleteVersionResponse } from '@/types/version'
import profileService from '@/services/profile.service'
import { logger } from '@/utils/logger'

// Mock dependencies
vi.mock('@/services/profile.service')
vi.mock('@/utils/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn()
  }
}))
vi.mock('@/composables/useAnalytics', () => ({
  useAnalytics: () => ({
    trackVersionListViewed: vi.fn(),
    trackVersionActivated: vi.fn(),
    trackVersionDownloaded: vi.fn(),
    trackVersionDeleted: vi.fn()
  })
}))

// Mock window.open
const mockWindowOpen = vi.fn()
Object.defineProperty(window, 'open', {
  writable: true,
  value: mockWindowOpen
})

describe('useProfileVersions', () => {
  // Helper to create mock version
  const createMockVersion = (versionNumber: number, isCurrent = false): ProfileVersion => ({
    version_number: versionNumber,
    created_at: `2024-01-0${versionNumber}T10:00:00Z`,
    created_by_username: `user${versionNumber}`,
    version_type: 'generated',
    validation_score: 0.85,
    completeness_score: 0.90,
    is_current: isCurrent
  })

  // Test setup
  let profileId: ReturnType<typeof computed<string | undefined>>
  let activeTab: ReturnType<typeof ref<string>>
  let mockOnVersionChanged: ReturnType<typeof vi.fn>

  beforeEach(() => {
    profileId = computed(() => 'test-profile-id')
    activeTab = ref('content')
    mockOnVersionChanged = vi.fn().mockResolvedValue(undefined)
    vi.clearAllMocks()
    mockWindowOpen.mockClear()
  })

  describe('Initial State', () => {
    it('should initialize with empty state', () => {
      const { versions, versionsLoading, versionsError, snackbar } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      expect(versions.value).toEqual([])
      expect(versionsLoading.value).toBe(false)
      expect(versionsError.value).toBe(null)
      expect(snackbar.value).toEqual({
        show: false,
        message: '',
        color: 'success'
      })
    })
  })

  describe('loadVersions', () => {
    it('should load versions successfully', async () => {
      const mockVersions: ProfileVersion[] = [
        createMockVersion(1, true),
        createMockVersion(2, false)
      ]
      const mockResponse: ProfileVersionsResponse = {
        versions: mockVersions,
        current_version: 1,
        total_versions: 2
      }

      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockResponse)

      const { versions, versionsLoading, versionsError, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(versions.value).toEqual(mockVersions)
      expect(versionsLoading.value).toBe(false)
      expect(versionsError.value).toBe(null)
      expect(profileService.getProfileVersions).toHaveBeenCalledWith('test-profile-id')
    })

    it('should set loading state correctly during API call', async () => {
      const mockResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 1,
        total_versions: 0
      }

      let loadingDuringCall = false

      vi.mocked(profileService.getProfileVersions).mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 10))
        return mockResponse
      })

      const { versionsLoading, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      const loadPromise = loadVersions()
      await nextTick()
      loadingDuringCall = versionsLoading.value
      await loadPromise

      expect(loadingDuringCall).toBe(true)
      expect(versionsLoading.value).toBe(false)
    })

    it('should handle errors gracefully', async () => {
      const mockError = new Error('API Error')
      vi.mocked(profileService.getProfileVersions).mockRejectedValue(mockError)

      const { versions, versionsLoading, versionsError, snackbar, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(versions.value).toEqual([])
      expect(versionsLoading.value).toBe(false)
      expect(versionsError.value).toBe('API Error')
      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.color).toBe('error')
      expect(snackbar.value.message).toBe('API Error')
      expect(logger.error).toHaveBeenCalledWith('Failed to load versions', mockError)
    })

    it('should show error notification on failure', async () => {
      vi.mocked(profileService.getProfileVersions).mockRejectedValue(new Error('Network Error'))

      const { snackbar, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Network Error')
      expect(snackbar.value.color).toBe('error')
    })

    it('should handle non-Error exceptions', async () => {
      vi.mocked(profileService.getProfileVersions).mockRejectedValue('String error')

      const { versionsError, snackbar, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(versionsError.value).toBe('Не удалось загрузить версии')
      expect(snackbar.value.message).toBe('Не удалось загрузить версии')
    })

    it('should not load if profileId is undefined', async () => {
      const emptyProfileId = computed(() => undefined)

      const { loadVersions } = useProfileVersions(
        emptyProfileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(profileService.getProfileVersions).not.toHaveBeenCalled()
    })

    it('should convert profileId to string', async () => {
      const mockResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 1,
        total_versions: 0
      }
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockResponse)

      const { loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(profileService.getProfileVersions).toHaveBeenCalledWith('test-profile-id')
    })
  })

  describe('handleSetActive', () => {
    it('should set version as active successfully', async () => {
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(2, true)],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(profileService.setActiveVersion).toHaveBeenCalledWith('test-profile-id', 2)
    })

    it('should reload profile after activation', async () => {
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(mockOnVersionChanged).toHaveBeenCalled()
    })

    it('should reload versions list after activation', async () => {
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(profileService.getProfileVersions).toHaveBeenCalledWith('test-profile-id')
    })

    it('should switch to content tab after activation', async () => {
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      activeTab.value = 'versions'

      const { handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(activeTab.value).toBe('content')
    })

    it('should show success notification', async () => {
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { snackbar, handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Версия 2 успешно активирована')
      expect(snackbar.value.color).toBe('success')
    })

    it('should handle errors gracefully', async () => {
      const mockError = new Error('Failed to set active')
      vi.mocked(profileService.setActiveVersion).mockRejectedValue(mockError)

      const { snackbar, handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Failed to set active')
      expect(snackbar.value.color).toBe('error')
      expect(logger.error).toHaveBeenCalledWith('Failed to set active version', mockError)
    })

    it('should handle non-Error exceptions in set active', async () => {
      vi.mocked(profileService.setActiveVersion).mockRejectedValue('String error')

      const { snackbar, handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(snackbar.value.message).toBe('Не удалось активировать версию')
    })

    it('should not set active if profileId is undefined', async () => {
      const emptyProfileId = computed(() => undefined)

      const { handleSetActive } = useProfileVersions(
        emptyProfileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleSetActive(2)

      expect(profileService.setActiveVersion).not.toHaveBeenCalled()
    })

    it('should work without onVersionChanged callback', async () => {
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { handleSetActive } = useProfileVersions(
        profileId,
        activeTab
        // No callback provided
      )

      await expect(handleSetActive(2)).resolves.not.toThrow()
    })
  })

  describe('handleVersionDownload', () => {
    it('should open download URL for JSON format', async () => {
      const { handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(2, 'json')

      expect(mockWindowOpen).toHaveBeenCalledWith(
        '/api/profiles/test-profile-id/download/json?version=2',
        '_blank'
      )
    })

    it('should open download URL for Markdown format', async () => {
      const { handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(3, 'md')

      expect(mockWindowOpen).toHaveBeenCalledWith(
        '/api/profiles/test-profile-id/download/md?version=3',
        '_blank'
      )
    })

    it('should open download URL for DOCX format', async () => {
      const { handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(1, 'docx')

      expect(mockWindowOpen).toHaveBeenCalledWith(
        '/api/profiles/test-profile-id/download/docx?version=1',
        '_blank'
      )
    })

    it('should show notification on download', async () => {
      const { snackbar, handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(2, 'json')

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Версия 2 скачивается...')
      expect(snackbar.value.color).toBe('info')
    })

    it('should handle errors gracefully', async () => {
      mockWindowOpen.mockImplementation(() => {
        throw new Error('Window open failed')
      })

      const { snackbar, handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(2, 'json')

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Window open failed')
      expect(snackbar.value.color).toBe('error')
      expect(logger.error).toHaveBeenCalledWith('Failed to download version', expect.any(Error))
    })

    it('should handle non-Error exceptions in download', async () => {
      mockWindowOpen.mockImplementation(() => {
        throw 'String error'
      })

      const { snackbar, handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(2, 'json')

      expect(snackbar.value.message).toBe('Не удалось скачать версию')
    })

    it('should not download if profileId is undefined', async () => {
      const emptyProfileId = computed(() => undefined)

      const { handleVersionDownload } = useProfileVersions(
        emptyProfileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(2, 'json')

      expect(mockWindowOpen).not.toHaveBeenCalled()
    })
  })

  describe('handleDeleteVersion', () => {
    it('should delete version successfully', async () => {
      const mockDeleteResponse: DeleteVersionResponse = {
        message: 'Deleted',
        profile_id: 'test-profile-id',
        deleted_version: 2,
        remaining_versions: 1
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true)],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.deleteVersion).mockResolvedValue(mockDeleteResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { handleDeleteVersion } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleDeleteVersion(2)

      expect(profileService.deleteVersion).toHaveBeenCalledWith('test-profile-id', 2)
    })

    it('should reload versions list after deletion', async () => {
      const mockDeleteResponse: DeleteVersionResponse = {
        message: 'Deleted',
        profile_id: 'test-profile-id',
        deleted_version: 2,
        remaining_versions: 1
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true)],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.deleteVersion).mockResolvedValue(mockDeleteResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { versions, handleDeleteVersion } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleDeleteVersion(2)

      expect(profileService.getProfileVersions).toHaveBeenCalledWith('test-profile-id')
      expect(versions.value).toEqual(mockVersionsResponse.versions)
    })

    it('should show success notification', async () => {
      const mockDeleteResponse: DeleteVersionResponse = {
        message: 'Deleted',
        profile_id: 'test-profile-id',
        deleted_version: 2,
        remaining_versions: 1
      }
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.deleteVersion).mockResolvedValue(mockDeleteResponse)
      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { snackbar, handleDeleteVersion } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleDeleteVersion(2)

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Версия 2 успешно удалена')
      expect(snackbar.value.color).toBe('success')
    })

    it('should handle errors gracefully', async () => {
      const mockError = new Error('Cannot delete current version')
      vi.mocked(profileService.deleteVersion).mockRejectedValue(mockError)

      const { snackbar, handleDeleteVersion } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleDeleteVersion(1)

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Cannot delete current version')
      expect(snackbar.value.color).toBe('error')
      expect(logger.error).toHaveBeenCalledWith('Failed to delete version', mockError)
    })

    it('should handle non-Error exceptions in delete', async () => {
      vi.mocked(profileService.deleteVersion).mockRejectedValue('String error')

      const { snackbar, handleDeleteVersion } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleDeleteVersion(2)

      expect(snackbar.value.message).toBe('Не удалось удалить версию')
    })

    it('should not delete if profileId is undefined', async () => {
      const emptyProfileId = computed(() => undefined)

      const { handleDeleteVersion } = useProfileVersions(
        emptyProfileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleDeleteVersion(2)

      expect(profileService.deleteVersion).not.toHaveBeenCalled()
    })
  })

  describe('watch behavior', () => {
    it('should load versions when switching to versions tab', async () => {
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true)],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { versions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Switch to versions tab
      activeTab.value = 'versions'
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      expect(profileService.getProfileVersions).toHaveBeenCalledWith('test-profile-id')
      expect(versions.value).toEqual(mockVersionsResponse.versions)
    })

    it('should not load if versions already loaded', async () => {
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true)],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { versions, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Load versions manually first
      await loadVersions()
      expect(versions.value.length).toBe(1)
      vi.clearAllMocks()

      // Switch to versions tab
      activeTab.value = 'versions'
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      // Should not call API again as versions are already loaded
      expect(profileService.getProfileVersions).not.toHaveBeenCalled()
    })

    it('should not load if profileId is undefined', async () => {
      const emptyProfileId = computed(() => undefined)

      useProfileVersions(
        emptyProfileId,
        activeTab,
        mockOnVersionChanged
      )

      // Switch to versions tab
      activeTab.value = 'versions'
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      expect(profileService.getProfileVersions).not.toHaveBeenCalled()
    })

    it('should not load when switching to non-versions tab', async () => {
      useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Switch to content tab (default, no change)
      activeTab.value = 'metadata'
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      expect(profileService.getProfileVersions).not.toHaveBeenCalled()
    })

    it('should handle errors during watch-triggered load', async () => {
      const mockError = new Error('API Error')
      vi.mocked(profileService.getProfileVersions).mockRejectedValue(mockError)

      const { versionsError, snackbar } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Switch to versions tab
      activeTab.value = 'versions'
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      expect(versionsError.value).toBe('API Error')
      expect(snackbar.value.color).toBe('error')
      expect(logger.error).toHaveBeenCalledWith('Failed to load versions', mockError)
    })
  })

  describe('Snackbar State', () => {
    it('should update snackbar state on success', async () => {
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true)],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { snackbar, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Initially false
      expect(snackbar.value.show).toBe(false)

      await loadVersions()

      // No snackbar on successful load (only on errors or actions)
      expect(snackbar.value.show).toBe(false)
    })

    it('should update snackbar state on error', async () => {
      vi.mocked(profileService.getProfileVersions).mockRejectedValue(new Error('Test Error'))

      const { snackbar, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(snackbar.value.show).toBe(true)
      expect(snackbar.value.message).toBe('Test Error')
      expect(snackbar.value.color).toBe('error')
    })

    it('should support different snackbar colors', async () => {
      // Reset mock to not throw error
      mockWindowOpen.mockImplementation(() => null)

      const { snackbar, handleVersionDownload } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await handleVersionDownload(1, 'json')

      expect(snackbar.value.color).toBe('info')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty versions list', async () => {
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [],
        current_version: 1,
        total_versions: 0
      }

      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      const { versions, loadVersions } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      await loadVersions()

      expect(versions.value).toEqual([])
      expect(versions.value.length).toBe(0)
    })

    it('should handle rapid tab switches', async () => {
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true)],
        current_version: 1,
        total_versions: 1
      }

      vi.mocked(profileService.getProfileVersions).mockResolvedValue(mockVersionsResponse)

      useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Rapid switches
      activeTab.value = 'versions'
      activeTab.value = 'content'
      activeTab.value = 'versions'
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      // Should still load only once due to empty versions check
      expect(profileService.getProfileVersions).toHaveBeenCalledTimes(1)
    })

    it('should maintain state consistency across multiple operations', async () => {
      const mockVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, true), createMockVersion(2, false)],
        current_version: 1,
        total_versions: 2
      }
      const mockSetActiveResponse: SetActiveVersionResponse = {
        message: 'Success',
        profile_id: 'test-profile-id',
        previous_version: 1,
        current_version: 2
      }
      const mockUpdatedVersionsResponse: ProfileVersionsResponse = {
        versions: [createMockVersion(1, false), createMockVersion(2, true)],
        current_version: 2,
        total_versions: 2
      }

      vi.mocked(profileService.getProfileVersions)
        .mockResolvedValueOnce(mockVersionsResponse)
        .mockResolvedValueOnce(mockUpdatedVersionsResponse)
      vi.mocked(profileService.setActiveVersion).mockResolvedValue(mockSetActiveResponse)

      const { versions, loadVersions, handleSetActive } = useProfileVersions(
        profileId,
        activeTab,
        mockOnVersionChanged
      )

      // Load initial versions
      await loadVersions()
      expect(versions.value.length).toBe(2)
      expect(versions.value[0].is_current).toBe(true)

      // Set version 2 as active
      await handleSetActive(2)
      expect(versions.value.length).toBe(2)
      expect(versions.value[1].is_current).toBe(true)
    })
  })
})

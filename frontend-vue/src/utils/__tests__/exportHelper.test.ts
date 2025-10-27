/**
 * Unit tests for exportHelper utility
 *
 * Tests bulk download functionality with JSZip integration
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { bulkDownloadProfiles, downloadProfileAsZip } from '../exportHelper'
import * as profileService from '@/services/profile.service'
import { saveAs } from 'file-saver'

// Mock dependencies
vi.mock('@/services/profile.service')
vi.mock('file-saver', () => ({
  saveAs: vi.fn()
}))
vi.mock('@/utils/logger', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn()
  }
}))

describe('exportHelper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('bulkDownloadProfiles', () => {
    it('should download profiles in all formats', async () => {
      // Arrange
      const profileIds = ['prof_1', 'prof_2']
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadMarkdown).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadDOCX).mockResolvedValue(mockBlob)

      // Act
      const result = await bulkDownloadProfiles({
        profileIds,
        formats: ['json', 'md', 'docx']
      })

      // Assert
      expect(result.successCount).toBe(6) // 2 profiles × 3 formats
      expect(result.errorCount).toBe(0)
      expect(result.totalFiles).toBe(6)
      expect(result.errors).toEqual([])

      // Verify service calls
      expect(profileService.downloadJSON).toHaveBeenCalledTimes(2)
      expect(profileService.downloadMarkdown).toHaveBeenCalledTimes(2)
      expect(profileService.downloadDOCX).toHaveBeenCalledTimes(2)

      // Verify ZIP was saved
      expect(saveAs).toHaveBeenCalledTimes(1)
    })

    it('should download profiles in single format only', async () => {
      // Arrange
      const profileIds = ['prof_1']
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)

      // Act
      const result = await bulkDownloadProfiles({
        profileIds,
        formats: ['json']
      })

      // Assert
      expect(result.successCount).toBe(1)
      expect(result.totalFiles).toBe(1)
      expect(profileService.downloadJSON).toHaveBeenCalledTimes(1)
      expect(profileService.downloadMarkdown).not.toHaveBeenCalled()
      expect(profileService.downloadDOCX).not.toHaveBeenCalled()
    })

    it('should handle partial failures gracefully', async () => {
      // Arrange
      const profileIds = ['prof_1', 'prof_2']
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      // First profile succeeds, second fails
      vi.mocked(profileService.downloadJSON)
        .mockResolvedValueOnce(mockBlob)
        .mockRejectedValueOnce(new Error('Network error'))

      // Act
      const result = await bulkDownloadProfiles({
        profileIds,
        formats: ['json']
      })

      // Assert
      expect(result.successCount).toBe(1)
      expect(result.errorCount).toBe(1)
      expect(result.totalFiles).toBe(2)
      expect(result.errors).toHaveLength(1)
      expect(result.errors[0]).toEqual({
        profileId: 'prof_2',
        format: 'json',
        error: 'Network error'
      })

      // ZIP should still be created with successful files
      expect(saveAs).toHaveBeenCalledTimes(1)
    })

    it('should call progress callback for each file', async () => {
      // Arrange
      const profileIds = ['prof_1']
      const mockBlob = new Blob(['test'], { type: 'application/json' })
      const progressCallback = vi.fn()

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)

      // Act
      await bulkDownloadProfiles({
        profileIds,
        formats: ['json'],
        onProgress: progressCallback
      })

      // Assert
      expect(progressCallback).toHaveBeenCalledTimes(2) // downloading + adding

      // Verify progress callback arguments
      expect(progressCallback).toHaveBeenCalledWith(
        expect.objectContaining({
          current: 1,
          total: 1,
          profileId: 'prof_1',
          format: 'json',
          status: 'downloading'
        })
      )

      expect(progressCallback).toHaveBeenCalledWith(
        expect.objectContaining({
          current: 1,
          total: 1,
          profileId: 'prof_1',
          format: 'json',
          status: 'adding'
        })
      )
    })

    it('should call progress callback on error', async () => {
      // Arrange
      const profileIds = ['prof_1']
      const progressCallback = vi.fn()

      vi.mocked(profileService.downloadJSON).mockRejectedValue(
        new Error('Download failed')
      )

      // Act
      await bulkDownloadProfiles({
        profileIds,
        formats: ['json'],
        onProgress: progressCallback
      })

      // Assert
      expect(progressCallback).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'error',
          error: 'Download failed'
        })
      )
    })

    it('should use custom filename if provided', async () => {
      // Arrange
      const profileIds = ['prof_1']
      const mockBlob = new Blob(['test'], { type: 'application/json' })
      const customFilename = 'my_custom_export'

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)

      // Act
      await bulkDownloadProfiles({
        profileIds,
        formats: ['json'],
        filename: customFilename
      })

      // Assert
      expect(saveAs).toHaveBeenCalledWith(
        expect.any(Blob),
        `${customFilename}.zip`
      )
    })

    it('should generate timestamped filename by default', async () => {
      // Arrange
      const profileIds = ['prof_1']
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)

      // Act
      await bulkDownloadProfiles({
        profileIds,
        formats: ['json']
      })

      // Assert
      expect(saveAs).toHaveBeenCalledWith(
        expect.any(Blob),
        expect.stringMatching(/^profiles_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.zip$/)
      )
    })

    it('should sanitize profile IDs in filenames', async () => {
      // Arrange
      const profileIds = ['prof/with/slashes', 'prof:with:colons']
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)

      // Act
      const result = await bulkDownloadProfiles({
        profileIds,
        formats: ['json']
      })

      // Assert - Filenames should be sanitized (special chars replaced with _)
      expect(result.successCount).toBe(2)
      expect(saveAs).toHaveBeenCalledTimes(1)
    })

    it('should handle empty profile IDs array', async () => {
      // Arrange
      const profileIds: string[] = []

      // Act
      const result = await bulkDownloadProfiles({
        profileIds,
        formats: ['json']
      })

      // Assert
      expect(result.successCount).toBe(0)
      expect(result.totalFiles).toBe(0)
      expect(saveAs).toHaveBeenCalledTimes(1) // Empty ZIP still created
    })

    it('should default to all formats if not specified', async () => {
      // Arrange
      const profileIds = ['prof_1']
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadMarkdown).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadDOCX).mockResolvedValue(mockBlob)

      // Act
      const result = await bulkDownloadProfiles({
        profileIds
        // formats not specified - should default to all
      })

      // Assert
      expect(result.totalFiles).toBe(3) // All 3 formats
      expect(profileService.downloadJSON).toHaveBeenCalled()
      expect(profileService.downloadMarkdown).toHaveBeenCalled()
      expect(profileService.downloadDOCX).toHaveBeenCalled()
    })
  })

  describe('downloadProfileAsZip', () => {
    it('should download single profile in all formats', async () => {
      // Arrange
      const profileId = 'prof_123'
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadMarkdown).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadDOCX).mockResolvedValue(mockBlob)

      // Act
      const result = await downloadProfileAsZip(profileId)

      // Assert
      expect(result.successCount).toBe(3) // All 3 formats
      expect(result.totalFiles).toBe(3)
      expect(profileService.downloadJSON).toHaveBeenCalledWith(profileId)
      expect(profileService.downloadMarkdown).toHaveBeenCalledWith(profileId)
      expect(profileService.downloadDOCX).toHaveBeenCalledWith(profileId)

      // Verify filename contains profile ID
      expect(saveAs).toHaveBeenCalledWith(
        expect.any(Blob),
        expect.stringMatching(/^profile_prof_123_\d+\.zip$/)
      )
    })

    it('should download single profile in specified formats only', async () => {
      // Arrange
      const profileId = 'prof_123'
      const mockBlob = new Blob(['test'], { type: 'application/json' })

      vi.mocked(profileService.downloadJSON).mockResolvedValue(mockBlob)
      vi.mocked(profileService.downloadDOCX).mockResolvedValue(mockBlob)

      // Act
      const result = await downloadProfileAsZip(profileId, ['json', 'docx'])

      // Assert
      expect(result.successCount).toBe(2)
      expect(result.totalFiles).toBe(2)
      expect(profileService.downloadJSON).toHaveBeenCalled()
      expect(profileService.downloadDOCX).toHaveBeenCalled()
      expect(profileService.downloadMarkdown).not.toHaveBeenCalled()
    })
  })
})

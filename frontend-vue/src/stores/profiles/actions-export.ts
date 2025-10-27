/**
 * Export actions for profiles store
 *
 * Handles bulk download operations and format exports
 */

import { ref } from 'vue'
import {
  bulkDownloadProfiles,
  type ExportFormat,
  type BulkDownloadResult,
  type DownloadProgress
} from '@/utils/exportHelper'
import { logger } from '@/utils/logger'

/**
 * Download progress state
 */
export const downloadProgress = ref<DownloadProgress | null>(null)

/**
 * Is download in progress
 */
export const isDownloading = ref(false)

/**
 * Download error message
 */
export const downloadError = ref<string | null>(null)

/**
 * Bulk download selected profiles as ZIP
 *
 * Downloads multiple profiles in specified formats and packs them into ZIP archive.
 * Shows progress indicator and handles errors gracefully.
 *
 * @param profileIds - Array of profile IDs to download
 * @param formats - Export formats to include (default: all)
 * @returns Download result with success/error counts
 * @throws Error if no profiles selected or download fails completely
 *
 * @example
 * ```typescript
 * const profilesStore = useProfilesStore()
 *
 * // Download selected profiles in all formats
 * const result = await profilesStore.bulkDownload(
 *   ['prof_1', 'prof_2'],
 *   ['json', 'docx']
 * )
 *
 * console.log(`Downloaded ${result.successCount} files`)
 * ```
 */
export async function bulkDownload(
  profileIds: string[],
  formats?: ExportFormat[]
): Promise<BulkDownloadResult> {
  if (!profileIds || profileIds.length === 0) {
    throw new Error('No profiles selected for download')
  }

  isDownloading.value = true
  downloadError.value = null
  downloadProgress.value = null

  try {
    logger.info(
      `Starting bulk download: ${profileIds.length} profiles, formats: ${formats?.join(', ') || 'all'}`
    )

    const result = await bulkDownloadProfiles({
      profileIds,
      formats,
      onProgress: (progress) => {
        downloadProgress.value = progress
      }
    })

    // Log summary
    if (result.errorCount > 0) {
      logger.warn(
        `Bulk download completed with errors: ${result.successCount}/${result.totalFiles} files downloaded, ${result.errorCount} errors`
      )

      // Set error message for UI
      downloadError.value = `Загружено ${result.successCount} из ${result.totalFiles} файлов. Ошибок: ${result.errorCount}`
    } else {
      logger.info(
        `Bulk download completed successfully: ${result.successCount}/${result.totalFiles} files`
      )
    }

    return result
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown download error'

    logger.error('Bulk download failed', error)

    downloadError.value = `Ошибка при скачивании: ${errorMessage}`

    throw new Error(errorMessage)
  } finally {
    isDownloading.value = false

    // Clear progress after delay (for UX - let user see "complete" state)
    setTimeout(() => {
      downloadProgress.value = null
    }, 2000)
  }
}

/**
 * Clear download error
 */
export function clearDownloadError(): void {
  downloadError.value = null
}

/**
 * Export utilities for bulk profile downloads
 *
 * Provides functionality to download multiple profiles in various formats
 * and pack them into ZIP archives using JSZip library.
 */

import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import * as profileService from '@/services/profile.service'
import { logger } from './logger'

/**
 * Supported export formats
 */
export type ExportFormat = 'json' | 'md' | 'docx'

/**
 * Progress callback for bulk download operations
 */
export interface DownloadProgress {
  current: number
  total: number
  profileId: string
  format: ExportFormat
  status: 'downloading' | 'adding' | 'complete' | 'error'
  error?: string
}

/**
 * Options for bulk download
 */
export interface BulkDownloadOptions {
  /**
   * Profile IDs to download
   */
  profileIds: string[]

  /**
   * Formats to include in ZIP
   * If not specified, all formats will be included
   */
  formats?: ExportFormat[]

  /**
   * ZIP filename (without extension)
   * Default: 'profiles_{timestamp}'
   */
  filename?: string

  /**
   * Progress callback
   */
  onProgress?: (progress: DownloadProgress) => void
}

/**
 * Result of bulk download operation
 */
export interface BulkDownloadResult {
  /**
   * Number of successfully downloaded files
   */
  successCount: number

  /**
   * Number of failed downloads
   */
  errorCount: number

  /**
   * Total files attempted
   */
  totalFiles: number

  /**
   * List of errors (if any)
   */
  errors: Array<{
    profileId: string
    format: ExportFormat
    error: string
  }>
}

/**
 * Download a single profile in specified format
 *
 * @param profileId - Profile ID
 * @param format - Export format
 * @returns Blob with file content
 * @throws Error if download fails
 */
async function downloadSingleProfile(
  profileId: string,
  format: ExportFormat
): Promise<Blob> {
  switch (format) {
    case 'json':
      return await profileService.downloadJSON(profileId)
    case 'md':
      return await profileService.downloadMarkdown(profileId)
    case 'docx':
      return await profileService.downloadDOCX(profileId)
    default:
      throw new Error(`Unsupported format: ${format}`)
  }
}

/**
 * Get file extension for format
 */
function getFileExtension(format: ExportFormat): string {
  switch (format) {
    case 'json':
      return 'json'
    case 'md':
      return 'md'
    case 'docx':
      return 'docx'
    default:
      return 'txt'
  }
}

/**
 * Generate safe filename from profile ID
 *
 * Removes special characters and ensures filesystem-safe name
 */
function sanitizeFilename(profileId: string): string {
  return profileId.replace(/[^a-zA-Z0-9_-]/g, '_')
}

/**
 * Download multiple profiles and pack into ZIP archive
 *
 * Downloads profiles in parallel (with concurrency limit) and creates
 * organized ZIP structure:
 * ```
 * profiles_YYYYMMDD_HHMMSS.zip
 * ├── json/
 * │   ├── profile_1.json
 * │   └── profile_2.json
 * ├── markdown/
 * │   ├── profile_1.md
 * │   └── profile_2.md
 * └── docx/
 *     ├── profile_1.docx
 *     └── profile_2.docx
 * ```
 *
 * @param options - Bulk download options
 * @returns Result with success/error counts
 *
 * @example
 * ```typescript
 * const result = await bulkDownloadProfiles({
 *   profileIds: ['prof_1', 'prof_2', 'prof_3'],
 *   formats: ['json', 'docx'],
 *   onProgress: (progress) => {
 *     console.log(`Downloading ${progress.current}/${progress.total}`)
 *   }
 * })
 *
 * console.log(`Downloaded ${result.successCount} files`)
 * ```
 */
export async function bulkDownloadProfiles(
  options: BulkDownloadOptions
): Promise<BulkDownloadResult> {
  const { profileIds, formats = ['json', 'md', 'docx'], onProgress } = options

  // Create ZIP instance
  const zip = new JSZip()

  // Create folders for each format
  const folders: Record<ExportFormat, JSZip> = {
    json: zip.folder('json')!,
    md: zip.folder('markdown')!,
    docx: zip.folder('docx')!
  }

  // Track results
  const result: BulkDownloadResult = {
    successCount: 0,
    errorCount: 0,
    totalFiles: profileIds.length * formats.length,
    errors: []
  }

  let currentFile = 0

  // Download each profile in each format
  for (const profileId of profileIds) {
    for (const format of formats) {
      currentFile++

      try {
        // Notify start
        onProgress?.({
          current: currentFile,
          total: result.totalFiles,
          profileId,
          format,
          status: 'downloading'
        })

        // Download file
        const blob = await downloadSingleProfile(profileId, format)

        // Notify adding to ZIP
        onProgress?.({
          current: currentFile,
          total: result.totalFiles,
          profileId,
          format,
          status: 'adding'
        })

        // Add to appropriate folder
        const filename = `${sanitizeFilename(profileId)}.${getFileExtension(format)}`
        folders[format].file(filename, blob)

        result.successCount++

        logger.info(
          `Added ${profileId} (${format}) to ZIP: ${filename}`
        )
      } catch (error: unknown) {
        result.errorCount++

        const errorMessage = error instanceof Error ? error.message : 'Unknown error'

        result.errors.push({
          profileId,
          format,
          error: errorMessage
        })

        logger.error(
          `Failed to download ${profileId} (${format}): ${errorMessage}`,
          error
        )

        // Notify error
        onProgress?.({
          current: currentFile,
          total: result.totalFiles,
          profileId,
          format,
          status: 'error',
          error: errorMessage
        })
      }
    }
  }

  // Generate ZIP file
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
    const filename = options.filename || `profiles_${timestamp}`

    const zipBlob = await zip.generateAsync({
      type: 'blob',
      compression: 'DEFLATE',
      compressionOptions: {
        level: 6
      }
    })

    // Download ZIP
    saveAs(zipBlob, `${filename}.zip`)

    logger.info(
      `Bulk download complete: ${result.successCount}/${result.totalFiles} files in ${filename}.zip`
    )
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to generate ZIP'
    logger.error('Failed to generate ZIP file', error)
    throw new Error(errorMessage)
  }

  return result
}

/**
 * Download single profile in multiple formats as ZIP
 *
 * Convenience function for downloading one profile in all formats.
 *
 * @param profileId - Profile ID
 * @param formats - Formats to include (default: all)
 * @returns Download result
 *
 * @example
 * ```typescript
 * await downloadProfileAsZip('prof_123', ['json', 'docx'])
 * // Downloads: profile_123_YYYYMMDD_HHMMSS.zip
 * ```
 */
export async function downloadProfileAsZip(
  profileId: string,
  formats?: ExportFormat[]
): Promise<BulkDownloadResult> {
  const filename = `profile_${sanitizeFilename(profileId)}_${Date.now()}`

  return await bulkDownloadProfiles({
    profileIds: [profileId],
    formats,
    filename
  })
}

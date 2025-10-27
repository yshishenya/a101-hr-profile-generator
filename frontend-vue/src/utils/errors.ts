/**
 * Utilities for error handling and message extraction
 */

/**
 * Structure of an axios error response
 */
interface AxiosErrorResponse {
  response?: {
    data?: {
      detail?: string
    }
    status?: number
  }
  message?: string
}

/**
 * Base error class for profile version operations
 */
export class VersionError extends Error {
  constructor(
    message: string,
    public code: string,
    public cause?: unknown
  ) {
    super(message)
    this.name = 'VersionError'
  }
}

/**
 * Error thrown when a requested version is not found
 */
export class VersionNotFoundError extends VersionError {
  constructor(
    public profileId: string,
    public versionNumber: number,
    cause?: unknown
  ) {
    super(
      `Version ${versionNumber} not found for profile ${profileId}`,
      'VERSION_NOT_FOUND',
      cause
    )
    this.name = 'VersionNotFoundError'
  }
}

/**
 * Error thrown when attempting to delete the current active version
 */
export class CannotDeleteCurrentVersionError extends VersionError {
  constructor(
    public versionNumber: number,
    cause?: unknown
  ) {
    super(
      `Cannot delete current active version ${versionNumber}`,
      'CANNOT_DELETE_CURRENT',
      cause
    )
    this.name = 'CannotDeleteCurrentVersionError'
  }
}

/**
 * Error thrown when attempting to delete the last remaining version
 */
export class CannotDeleteLastVersionError extends VersionError {
  constructor(
    public profileId: string,
    cause?: unknown
  ) {
    super(
      `Cannot delete the last remaining version of profile ${profileId}`,
      'CANNOT_DELETE_LAST',
      cause
    )
    this.name = 'CannotDeleteLastVersionError'
  }
}

/**
 * Error thrown when version activation fails
 */
export class VersionActivationError extends VersionError {
  constructor(
    public profileId: string,
    public versionNumber: number,
    cause?: unknown
  ) {
    super(
      `Failed to activate version ${versionNumber} for profile ${profileId}`,
      'VERSION_ACTIVATION_FAILED',
      cause
    )
    this.name = 'VersionActivationError'
  }
}

/**
 * Error thrown when loading versions list fails
 */
export class VersionsLoadError extends VersionError {
  constructor(
    public profileId: string,
    cause?: unknown
  ) {
    super(
      `Failed to load versions for profile ${profileId}`,
      'VERSIONS_LOAD_FAILED',
      cause
    )
    this.name = 'VersionsLoadError'
  }
}

/**
 * Type guard to check if error is axios-like error
 */
function isAxiosError(error: unknown): error is AxiosErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    ('response' in error || 'message' in error)
  )
}

/**
 * Extract error message from unknown error object
 * Handles axios errors, Error objects, and other types
 *
 * @param error - Unknown error object
 * @param fallback - Fallback message if extraction fails
 * @returns Extracted error message
 */
export function getErrorMessage(error: unknown, fallback = 'Unknown error'): string {
  if (isAxiosError(error)) {
    return error.response?.data?.detail || error.message || fallback
  }

  if (error instanceof Error) {
    return error.message
  }

  if (typeof error === 'string') {
    return error
  }

  return fallback
}

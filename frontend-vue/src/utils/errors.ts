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
  }
  message?: string
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

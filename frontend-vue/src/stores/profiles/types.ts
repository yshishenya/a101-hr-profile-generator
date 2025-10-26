/**
 * Local types for profiles store
 * Contains custom error classes and helper types
 */

/**
 * Custom error class for profile operations
 * Provides structured error handling with error codes
 *
 * @example
 * ```typescript
 * throw new ProfileError('Profile not found', 'NOT_FOUND')
 * ```
 */
export class ProfileError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly originalError?: unknown
  ) {
    super(message)
    this.name = 'ProfileError'
  }
}

/**
 * Constants used throughout the profiles store
 */
export const DEFAULT_PAGE_SIZE = 20
export const DEFAULT_PAGE = 1

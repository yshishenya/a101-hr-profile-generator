/* eslint-disable no-console */
/**
 * Conditional logging utility
 * Logs only in development mode to avoid cluttering production console
 */

/**
 * Log level enum
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error'
}

/**
 * Check if we're in development mode
 */
const isDevelopment = import.meta.env.DEV

/**
 * Logger class with conditional logging based on environment
 */
class Logger {
  /**
   * Log debug information (only in development)
   * @param message - Message to log
   * @param data - Optional data to log
   */
  debug(message: string, ...data: unknown[]): void {
    if (isDevelopment) {
      console.log(`[DEBUG] ${message}`, ...data)
    }
  }

  /**
   * Log informational message (only in development)
   * @param message - Message to log
   * @param data - Optional data to log
   */
  info(message: string, ...data: unknown[]): void {
    if (isDevelopment) {
      console.info(`[INFO] ${message}`, ...data)
    }
  }

  /**
   * Log warning message (always logged)
   * @param message - Message to log
   * @param data - Optional data to log
   */
  warn(message: string, ...data: unknown[]): void {
    console.warn(`[WARN] ${message}`, ...data)
  }

  /**
   * Log error message (always logged)
   * @param message - Message to log
   * @param error - Optional error object
   * @param data - Optional additional data
   */
  error(message: string, error?: Error | unknown, ...data: unknown[]): void {
    console.error(`[ERROR] ${message}`, error, ...data)
  }

  /**
   * Log with custom level
   * @param level - Log level
   * @param message - Message to log
   * @param data - Optional data to log
   */
  log(level: LogLevel, message: string, ...data: unknown[]): void {
    switch (level) {
      case LogLevel.DEBUG:
        this.debug(message, ...data)
        break
      case LogLevel.INFO:
        this.info(message, ...data)
        break
      case LogLevel.WARN:
        this.warn(message, ...data)
        break
      case LogLevel.ERROR:
        this.error(message, ...data)
        break
    }
  }
}

/**
 * Singleton logger instance
 * @example
 * import { logger } from '@/utils/logger'
 *
 * logger.debug('User action', { userId: 123 })
 * logger.info('Data loaded successfully')
 * logger.warn('Deprecated API used')
 * logger.error('Failed to save data', error)
 */
export const logger = new Logger()

/**
 * Legacy function for simple conditional logging
 * @deprecated Use logger.debug() instead
 */
export function logDev(message: string, ...data: unknown[]): void {
  if (isDevelopment) {
    console.log(message, ...data)
  }
}

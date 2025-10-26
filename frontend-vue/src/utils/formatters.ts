/**
 * Formatting utilities for dates, numbers, and durations
 * Centralized formatting functions to ensure consistency across the application
 */

// Time conversion constants
const SECONDS_PER_MINUTE = 60
const SECONDS_PER_HOUR = 3600
const MINUTES_PER_HOUR = 60
const HOURS_PER_DAY = 24
const DAYS_PER_WEEK = 7

// File size constants
const BYTES_PER_KB = 1024

/**
 * Format a date string or Date object to a localized Russian date string
 * @param date - Date string or Date object to format
 * @returns Formatted date string (e.g., "26 окт. 2025, 14:30")
 * @example
 * formatDate('2025-10-26T14:30:00Z') // "26 окт. 2025, 14:30"
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return 'Н/Д'

  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (isNaN(dateObj.getTime())) return 'Н/Д'

  return new Intl.DateTimeFormat('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(dateObj)
}

/**
 * Format duration in seconds to human-readable Russian string
 * @param seconds - Duration in seconds
 * @returns Formatted duration string (e.g., "2 мин 30 сек", "1 ч 15 мин")
 * @example
 * formatDuration(150) // "2 мин 30 сек"
 * formatDuration(4500) // "1 ч 15 мин"
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return 'Н/Д'

  const hours = Math.floor(seconds / SECONDS_PER_HOUR)
  const minutes = Math.floor((seconds % SECONDS_PER_HOUR) / SECONDS_PER_MINUTE)
  const remainingSeconds = Math.floor(seconds % SECONDS_PER_MINUTE)

  const parts: string[] = []

  if (hours > 0) {
    parts.push(`${hours} ч`)
  }

  if (minutes > 0) {
    parts.push(`${minutes} мин`)
  }

  if (remainingSeconds > 0 || parts.length === 0) {
    parts.push(`${remainingSeconds} сек`)
  }

  return parts.join(' ')
}

/**
 * Format a number with thousands separators
 * @param value - Number to format
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted number string (e.g., "1 234 567")
 * @example
 * formatNumber(1234567) // "1 234 567"
 * formatNumber(1234.5678, 2) // "1 234.57"
 */
export function formatNumber(
  value: number | null | undefined,
  decimals: number = 0
): string {
  if (value === null || value === undefined) return 'Н/Д'

  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value)
}

/**
 * Format a percentage value
 * @param value - Percentage value (0-100)
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted percentage string (e.g., "85%", "12.5%")
 * @example
 * formatPercentage(85) // "85%"
 * formatPercentage(12.5, 1) // "12.5%"
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 0
): string {
  if (value === null || value === undefined) return 'Н/Д'

  return `${formatNumber(value, decimals)}%`
}

/**
 * Format file size in bytes to human-readable string
 * @param bytes - File size in bytes
 * @returns Formatted file size string (e.g., "1.5 MB", "500 KB")
 * @example
 * formatFileSize(1536000) // "1.46 MB"
 * formatFileSize(512000) // "500 KB"
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined) return 'Н/Д'

  const units = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']
  let size = bytes
  let unitIndex = 0

  while (size >= BYTES_PER_KB && unitIndex < units.length - 1) {
    size /= BYTES_PER_KB
    unitIndex++
  }

  return `${formatNumber(size, unitIndex > 0 ? 2 : 0)} ${units[unitIndex]}`
}

/**
 * Format relative time (e.g., "2 minutes ago", "in 5 hours")
 * @param date - Date string or Date object
 * @returns Formatted relative time string
 * @example
 * formatRelativeTime(new Date(Date.now() - 120000)) // "2 минуты назад"
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return 'Н/Д'

  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (isNaN(dateObj.getTime())) return 'Н/Д'

  const now = new Date()
  const diffMs = now.getTime() - dateObj.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / SECONDS_PER_MINUTE)
  const diffHours = Math.floor(diffMinutes / MINUTES_PER_HOUR)
  const diffDays = Math.floor(diffHours / HOURS_PER_DAY)

  if (diffSeconds < SECONDS_PER_MINUTE) {
    return 'только что'
  } else if (diffMinutes < MINUTES_PER_HOUR) {
    return `${diffMinutes} ${pluralize(diffMinutes, 'минуту', 'минуты', 'минут')} назад`
  } else if (diffHours < HOURS_PER_DAY) {
    return `${diffHours} ${pluralize(diffHours, 'час', 'часа', 'часов')} назад`
  } else if (diffDays < DAYS_PER_WEEK) {
    return `${diffDays} ${pluralize(diffDays, 'день', 'дня', 'дней')} назад`
  } else {
    return formatDate(dateObj)
  }
}

/**
 * Russian pluralization helper
 * @param count - Number to pluralize for
 * @param one - Form for 1 (e.g., "минута")
 * @param few - Form for 2-4 (e.g., "минуты")
 * @param many - Form for 5+ (e.g., "минут")
 * @returns Correct plural form
 * @example
 * pluralize(1, 'файл', 'файла', 'файлов') // "файл"
 * pluralize(3, 'файл', 'файла', 'файлов') // "файла"
 * pluralize(10, 'файл', 'файла', 'файлов') // "файлов"
 */
export function pluralize(
  count: number,
  one: string,
  few: string,
  many: string
): string {
  const mod10 = count % 10
  const mod100 = count % 100

  if (mod10 === 1 && mod100 !== 11) {
    return one
  } else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return few
  } else {
    return many
  }
}

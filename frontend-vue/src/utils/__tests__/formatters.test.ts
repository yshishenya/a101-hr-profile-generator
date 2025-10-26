import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  formatDate,
  formatDuration,
  formatNumber,
  formatPercentage,
  formatFileSize,
  formatRelativeTime,
  pluralize
} from '../formatters'

describe('formatters', () => {
  describe('formatDate', () => {
    it('should format valid ISO date string', () => {
      const result = formatDate('2025-10-26T14:30:00Z')
      expect(result).toContain('26')
      expect(result).toContain('окт')
      expect(result).toContain('2025')
    })

    it('should format Date object', () => {
      const date = new Date('2025-10-26T14:30:00Z')
      const result = formatDate(date)
      expect(result).toContain('26')
      expect(result).toContain('окт')
    })

    it('should return "Н/Д" for null', () => {
      expect(formatDate(null)).toBe('Н/Д')
    })

    it('should return "Н/Д" for undefined', () => {
      expect(formatDate(undefined)).toBe('Н/Д')
    })

    it('should return "Н/Д" for invalid date string', () => {
      expect(formatDate('invalid-date')).toBe('Н/Д')
    })

    it('should return "Н/Д" for empty string', () => {
      expect(formatDate('')).toBe('Н/Д')
    })

    it('should handle date with time correctly', () => {
      const result = formatDate('2025-12-31T12:00:00Z')
      expect(result).toContain('31')
      expect(result).toContain('дек')
      expect(result).toContain('2025')
    })
  })

  describe('formatDuration', () => {
    it('should format 0 seconds', () => {
      expect(formatDuration(0)).toBe('0 сек')
    })

    it('should format seconds only', () => {
      expect(formatDuration(45)).toBe('45 сек')
    })

    it('should format minutes and seconds', () => {
      expect(formatDuration(150)).toBe('2 мин 30 сек')
    })

    it('should format minutes without seconds', () => {
      expect(formatDuration(120)).toBe('2 мин')
    })

    it('should format hours and minutes', () => {
      expect(formatDuration(4500)).toBe('1 ч 15 мин')
    })

    it('should format hours only', () => {
      expect(formatDuration(3600)).toBe('1 ч')
    })

    it('should format hours, minutes, and seconds', () => {
      expect(formatDuration(3665)).toBe('1 ч 1 мин 5 сек')
    })

    it('should format large durations', () => {
      const result = formatDuration(86400) // 24 hours
      expect(result).toBe('24 ч')
    })

    it('should return "Н/Д" for null', () => {
      expect(formatDuration(null)).toBe('Н/Д')
    })

    it('should return "Н/Д" for undefined', () => {
      expect(formatDuration(undefined)).toBe('Н/Д')
    })

    it('should handle fractional seconds by flooring', () => {
      expect(formatDuration(90.7)).toBe('1 мин 30 сек')
    })

    it('should handle negative numbers', () => {
      // Negative durations are treated as 0
      expect(formatDuration(-10)).toBe('-10 сек')
    })
  })

  describe('formatNumber', () => {
    it('should format integer with thousands separator', () => {
      const result = formatNumber(1234567)
      // Russian locale uses non-breaking space as thousands separator
      expect(result).toMatch(/1[\s\u00A0]234[\s\u00A0]567/)
    })

    it('should format small numbers', () => {
      expect(formatNumber(123)).toBe('123')
    })

    it('should format zero', () => {
      expect(formatNumber(0)).toBe('0')
    })

    it('should format with decimal places', () => {
      const result = formatNumber(1234.5678, 2)
      // Russian locale uses comma as decimal separator and non-breaking space for thousands
      expect(result).toMatch(/1[\s\u00A0]234,57/)
    })

    it('should format with custom decimal places', () => {
      const result = formatNumber(1234.5678, 3)
      expect(result).toMatch(/1[\s\u00A0]234,568/)
    })

    it('should pad decimals if needed', () => {
      const result = formatNumber(1234, 2)
      expect(result).toMatch(/1[\s\u00A0]234,00/)
    })

    it('should return "Н/Д" for null', () => {
      expect(formatNumber(null)).toBe('Н/Д')
    })

    it('should return "Н/Д" for undefined', () => {
      expect(formatNumber(undefined)).toBe('Н/Д')
    })

    it('should handle negative numbers', () => {
      const result = formatNumber(-1234567)
      expect(result).toMatch(/-1[\s\u00A0]234[\s\u00A0]567/)
    })

    it('should handle very large numbers', () => {
      const result = formatNumber(1234567890123)
      expect(result).toMatch(/1[\s\u00A0]234[\s\u00A0]567[\s\u00A0]890[\s\u00A0]123/)
    })
  })

  describe('formatPercentage', () => {
    it('should format integer percentage', () => {
      expect(formatPercentage(85)).toBe('85%')
    })

    it('should format with decimal places', () => {
      expect(formatPercentage(12.5, 1)).toBe('12,5%')
    })

    it('should format with multiple decimal places', () => {
      expect(formatPercentage(33.333, 2)).toBe('33,33%')
    })

    it('should format zero', () => {
      expect(formatPercentage(0)).toBe('0%')
    })

    it('should format 100', () => {
      expect(formatPercentage(100)).toBe('100%')
    })

    it('should return "Н/Д" for null', () => {
      expect(formatPercentage(null)).toBe('Н/Д')
    })

    it('should return "Н/Д" for undefined', () => {
      expect(formatPercentage(undefined)).toBe('Н/Д')
    })

    it('should handle values over 100', () => {
      expect(formatPercentage(150)).toBe('150%')
    })

    it('should handle negative percentages', () => {
      expect(formatPercentage(-5)).toBe('-5%')
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes', () => {
      expect(formatFileSize(500)).toBe('500 Б')
    })

    it('should format kilobytes', () => {
      expect(formatFileSize(1024)).toBe('1,00 КБ')
    })

    it('should format kilobytes with decimals', () => {
      expect(formatFileSize(1536)).toBe('1,50 КБ')
    })

    it('should format megabytes', () => {
      expect(formatFileSize(1048576)).toBe('1,00 МБ')
    })

    it('should format megabytes with decimals', () => {
      expect(formatFileSize(1572864)).toBe('1,50 МБ')
    })

    it('should format gigabytes', () => {
      expect(formatFileSize(1073741824)).toBe('1,00 ГБ')
    })

    it('should format terabytes', () => {
      expect(formatFileSize(1099511627776)).toBe('1,00 ТБ')
    })

    it('should format zero bytes', () => {
      expect(formatFileSize(0)).toBe('0 Б')
    })

    it('should return "Н/Д" for null', () => {
      expect(formatFileSize(null)).toBe('Н/Д')
    })

    it('should return "Н/Д" for undefined', () => {
      expect(formatFileSize(undefined)).toBe('Н/Д')
    })

    it('should handle large file sizes', () => {
      const result = formatFileSize(512000)
      expect(result).toContain('КБ')
    })

    it('should not exceed terabytes unit', () => {
      const result = formatFileSize(1099511627776 * 1024) // 1024 TB
      expect(result).toContain('ТБ')
    })
  })

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      // Mock current time to 2025-10-26T12:00:00Z
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2025-10-26T12:00:00Z'))
    })

    it('should return "только что" for recent time (< 1 minute)', () => {
      const date = new Date('2025-10-26T11:59:30Z')
      expect(formatRelativeTime(date)).toBe('только что')
    })

    it('should format minutes ago', () => {
      const date = new Date('2025-10-26T11:58:00Z')
      expect(formatRelativeTime(date)).toBe('2 минуты назад')
    })

    it('should format singular minute', () => {
      const date = new Date('2025-10-26T11:59:00Z')
      expect(formatRelativeTime(date)).toBe('1 минуту назад')
    })

    it('should format hours ago', () => {
      const date = new Date('2025-10-26T10:00:00Z')
      expect(formatRelativeTime(date)).toBe('2 часа назад')
    })

    it('should format singular hour', () => {
      const date = new Date('2025-10-26T11:00:00Z')
      expect(formatRelativeTime(date)).toBe('1 час назад')
    })

    it('should format days ago', () => {
      const date = new Date('2025-10-24T12:00:00Z')
      expect(formatRelativeTime(date)).toBe('2 дня назад')
    })

    it('should format singular day', () => {
      const date = new Date('2025-10-25T12:00:00Z')
      expect(formatRelativeTime(date)).toBe('1 день назад')
    })

    it('should format full date for dates older than 7 days', () => {
      const date = new Date('2025-10-10T12:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('10')
      expect(result).toContain('окт')
    })

    it('should return "Н/Д" for null', () => {
      expect(formatRelativeTime(null)).toBe('Н/Д')
    })

    it('should return "Н/Д" for undefined', () => {
      expect(formatRelativeTime(undefined)).toBe('Н/Д')
    })

    it('should return "Н/Д" for invalid date string', () => {
      expect(formatRelativeTime('invalid')).toBe('Н/Д')
    })

    it('should handle string dates', () => {
      const dateStr = '2025-10-26T11:58:00Z'
      expect(formatRelativeTime(dateStr)).toBe('2 минуты назад')
    })

    it('should handle edge case at 60 minutes', () => {
      const date = new Date('2025-10-26T11:00:00Z')
      expect(formatRelativeTime(date)).toBe('1 час назад')
    })

    it('should handle edge case at 24 hours', () => {
      const date = new Date('2025-10-25T12:00:00Z')
      expect(formatRelativeTime(date)).toBe('1 день назад')
    })

    it('should handle edge case at 7 days', () => {
      const date = new Date('2025-10-19T12:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('19')
    })
  })

  describe('pluralize', () => {
    describe('ones (1, 21, 31, etc.)', () => {
      it('should return "one" form for 1', () => {
        expect(pluralize(1, 'файл', 'файла', 'файлов')).toBe('файл')
      })

      it('should return "one" form for 21', () => {
        expect(pluralize(21, 'файл', 'файла', 'файлов')).toBe('файл')
      })

      it('should return "one" form for 31', () => {
        expect(pluralize(31, 'файл', 'файла', 'файлов')).toBe('файл')
      })

      it('should return "one" form for 101', () => {
        expect(pluralize(101, 'файл', 'файла', 'файлов')).toBe('файл')
      })
    })

    describe('few (2-4, 22-24, etc.)', () => {
      it('should return "few" form for 2', () => {
        expect(pluralize(2, 'файл', 'файла', 'файлов')).toBe('файла')
      })

      it('should return "few" form for 3', () => {
        expect(pluralize(3, 'файл', 'файла', 'файлов')).toBe('файла')
      })

      it('should return "few" form for 4', () => {
        expect(pluralize(4, 'файл', 'файла', 'файлов')).toBe('файла')
      })

      it('should return "few" form for 22', () => {
        expect(pluralize(22, 'файл', 'файла', 'файлов')).toBe('файла')
      })

      it('should return "few" form for 23', () => {
        expect(pluralize(23, 'файл', 'файла', 'файлов')).toBe('файла')
      })

      it('should return "few" form for 24', () => {
        expect(pluralize(24, 'файл', 'файла', 'файлов')).toBe('файла')
      })
    })

    describe('many (0, 5-20, 25-30, etc.)', () => {
      it('should return "many" form for 0', () => {
        expect(pluralize(0, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 5', () => {
        expect(pluralize(5, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 10', () => {
        expect(pluralize(10, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 11', () => {
        expect(pluralize(11, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 12', () => {
        expect(pluralize(12, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 13', () => {
        expect(pluralize(13, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 14', () => {
        expect(pluralize(14, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 20', () => {
        expect(pluralize(20, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 25', () => {
        expect(pluralize(25, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 100', () => {
        expect(pluralize(100, 'файл', 'файла', 'файлов')).toBe('файлов')
      })
    })

    describe('special cases for 11-14', () => {
      it('should return "many" form for 111', () => {
        expect(pluralize(111, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 112', () => {
        expect(pluralize(112, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 113', () => {
        expect(pluralize(113, 'файл', 'файла', 'файлов')).toBe('файлов')
      })

      it('should return "many" form for 114', () => {
        expect(pluralize(114, 'файл', 'файла', 'файлов')).toBe('файлов')
      })
    })

    it('should work with different word forms', () => {
      expect(pluralize(1, 'минута', 'минуты', 'минут')).toBe('минута')
      expect(pluralize(2, 'минута', 'минуты', 'минут')).toBe('минуты')
      expect(pluralize(5, 'минута', 'минуты', 'минут')).toBe('минут')
    })
  })
})

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { logger, logDev, LogLevel } from '../logger'

describe('logger', () => {
  // Mock console methods
  const originalConsole = {
    log: console.log,
    info: console.info,
    warn: console.warn,
    error: console.error
  }

  beforeEach(() => {
    // Mock all console methods
    console.log = vi.fn()
    console.info = vi.fn()
    console.warn = vi.fn()
    console.error = vi.fn()
  })

  afterEach(() => {
    // Restore original console methods
    console.log = originalConsole.log
    console.info = originalConsole.info
    console.warn = originalConsole.warn
    console.error = originalConsole.error
    vi.restoreAllMocks()
  })

  describe('debug', () => {
    it('should log debug message with prefix in development', () => {
      logger.debug('Test debug message')

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('[DEBUG] Test debug message')
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should log debug message with data', () => {
      const data = { userId: 123, action: 'click' }
      logger.debug('User action', data)

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('[DEBUG] User action', data)
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should log debug message with multiple data arguments', () => {
      logger.debug('Multiple data', 'arg1', 42, { key: 'value' })

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith(
          '[DEBUG] Multiple data',
          'arg1',
          42,
          { key: 'value' }
        )
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should handle empty message', () => {
      logger.debug('')

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('[DEBUG] ')
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should handle special characters in message', () => {
      logger.debug('Test with специальные символы and émojis 🚀')

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('[DEBUG] Test with специальные символы and émojis 🚀')
      }
    })
  })

  describe('info', () => {
    it('should log info message with prefix in development', () => {
      logger.info('Test info message')

      if (import.meta.env.DEV) {
        expect(console.info).toHaveBeenCalledWith('[INFO] Test info message')
      } else {
        expect(console.info).not.toHaveBeenCalled()
      }
    })

    it('should log info message with data', () => {
      const data = { status: 'success', count: 10 }
      logger.info('Operation completed', data)

      if (import.meta.env.DEV) {
        expect(console.info).toHaveBeenCalledWith('[INFO] Operation completed', data)
      } else {
        expect(console.info).not.toHaveBeenCalled()
      }
    })

    it('should log info message with multiple data arguments', () => {
      logger.info('Info with data', 'string', 123, true, null)

      if (import.meta.env.DEV) {
        expect(console.info).toHaveBeenCalledWith(
          '[INFO] Info with data',
          'string',
          123,
          true,
          null
        )
      } else {
        expect(console.info).not.toHaveBeenCalled()
      }
    })

    it('should handle undefined data', () => {
      logger.info('Message', undefined)

      if (import.meta.env.DEV) {
        expect(console.info).toHaveBeenCalledWith('[INFO] Message', undefined)
      }
    })
  })

  describe('warn', () => {
    it('should always log warning message with prefix', () => {
      logger.warn('Test warning message')
      expect(console.warn).toHaveBeenCalledWith('[WARN] Test warning message')
    })

    it('should log warning with data in any environment', () => {
      const data = { deprecated: true, alternative: 'newMethod' }
      logger.warn('Deprecated API used', data)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Deprecated API used', data)
    })

    it('should log warning with multiple data arguments', () => {
      logger.warn('Warning', 'arg1', 'arg2', 42)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Warning', 'arg1', 'arg2', 42)
    })

    it('should handle arrays in data', () => {
      const array = [1, 2, 3]
      logger.warn('Array warning', array)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Array warning', array)
    })
  })

  describe('error', () => {
    it('should always log error message with prefix', () => {
      logger.error('Test error message')
      expect(console.error).toHaveBeenCalledWith('[ERROR] Test error message', undefined)
    })

    it('should log error with Error object', () => {
      const error = new Error('Something went wrong')
      logger.error('Operation failed', error)
      expect(console.error).toHaveBeenCalledWith('[ERROR] Operation failed', error)
    })

    it('should log error with additional data', () => {
      const error = new Error('Network error')
      const context = { url: '/api/users', status: 500 }
      logger.error('API call failed', error, context)
      expect(console.error).toHaveBeenCalledWith('[ERROR] API call failed', error, context)
    })

    it('should handle non-Error objects', () => {
      const errorObj = { code: 'ERR001', message: 'Custom error' }
      logger.error('Custom error occurred', errorObj)
      expect(console.error).toHaveBeenCalledWith('[ERROR] Custom error occurred', errorObj)
    })

    it('should handle string error', () => {
      logger.error('Error occurred', 'string error')
      expect(console.error).toHaveBeenCalledWith('[ERROR] Error occurred', 'string error')
    })

    it('should handle null error', () => {
      logger.error('Null error', null)
      expect(console.error).toHaveBeenCalledWith('[ERROR] Null error', null)
    })

    it('should handle undefined error', () => {
      logger.error('Undefined error')
      expect(console.error).toHaveBeenCalledWith('[ERROR] Undefined error', undefined)
    })

    it('should log error with multiple additional data arguments', () => {
      const error = new Error('Test')
      logger.error('Multiple data', error, 'data1', 'data2', { key: 'value' })
      expect(console.error).toHaveBeenCalledWith(
        '[ERROR] Multiple data',
        error,
        'data1',
        'data2',
        { key: 'value' }
      )
    })
  })

  describe('log', () => {
    it('should call debug for LogLevel.DEBUG', () => {
      logger.log(LogLevel.DEBUG, 'Debug message')

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('[DEBUG] Debug message')
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should call info for LogLevel.INFO', () => {
      logger.log(LogLevel.INFO, 'Info message')

      if (import.meta.env.DEV) {
        expect(console.info).toHaveBeenCalledWith('[INFO] Info message')
      } else {
        expect(console.info).not.toHaveBeenCalled()
      }
    })

    it('should call warn for LogLevel.WARN', () => {
      logger.log(LogLevel.WARN, 'Warning message')
      expect(console.warn).toHaveBeenCalledWith('[WARN] Warning message')
    })

    it('should call error for LogLevel.ERROR', () => {
      logger.log(LogLevel.ERROR, 'Error message')
      expect(console.error).toHaveBeenCalledWith('[ERROR] Error message', undefined)
    })

    it('should pass data to debug level', () => {
      logger.log(LogLevel.DEBUG, 'Message', { data: 'test' })

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('[DEBUG] Message', { data: 'test' })
      }
    })

    it('should pass data to info level', () => {
      logger.log(LogLevel.INFO, 'Message', { data: 'test' })

      if (import.meta.env.DEV) {
        expect(console.info).toHaveBeenCalledWith('[INFO] Message', { data: 'test' })
      }
    })

    it('should pass data to warn level', () => {
      logger.log(LogLevel.WARN, 'Message', { data: 'test' })
      expect(console.warn).toHaveBeenCalledWith('[WARN] Message', { data: 'test' })
    })

    it('should pass multiple data arguments', () => {
      logger.log(LogLevel.WARN, 'Message', 'arg1', 'arg2', 123)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Message', 'arg1', 'arg2', 123)
    })
  })

  describe('LogLevel enum', () => {
    it('should have DEBUG level', () => {
      expect(LogLevel.DEBUG).toBe('debug')
    })

    it('should have INFO level', () => {
      expect(LogLevel.INFO).toBe('info')
    })

    it('should have WARN level', () => {
      expect(LogLevel.WARN).toBe('warn')
    })

    it('should have ERROR level', () => {
      expect(LogLevel.ERROR).toBe('error')
    })

    it('should be usable in switch statements', () => {
      const level: LogLevel = LogLevel.INFO
      let result = ''

      switch (level) {
        case LogLevel.DEBUG:
          result = 'debug'
          break
        case LogLevel.INFO:
          result = 'info'
          break
        case LogLevel.WARN:
          result = 'warn'
          break
        case LogLevel.ERROR:
          result = 'error'
          break
      }

      expect(result).toBe('info')
    })
  })

  describe('logDev (legacy function)', () => {
    it('should log message in development mode', () => {
      logDev('Legacy log message')

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('Legacy log message')
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should log message with data in development', () => {
      const data = { test: 'value' }
      logDev('Message', data)

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('Message', data)
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should log message with multiple data arguments', () => {
      logDev('Multiple', 'arg1', 42, true, { key: 'val' })

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('Multiple', 'arg1', 42, true, { key: 'val' })
      } else {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should not log in production', () => {
      // This test documents the expected behavior
      // Actual behavior depends on import.meta.env.DEV at runtime
      logDev('Production test')

      if (!import.meta.env.DEV) {
        expect(console.log).not.toHaveBeenCalled()
      }
    })

    it('should handle empty message', () => {
      logDev('')

      if (import.meta.env.DEV) {
        expect(console.log).toHaveBeenCalledWith('')
      }
    })
  })

  describe('logger singleton', () => {
    it('should be an instance of Logger class', () => {
      expect(logger).toBeDefined()
      expect(logger.debug).toBeTypeOf('function')
      expect(logger.info).toBeTypeOf('function')
      expect(logger.warn).toBeTypeOf('function')
      expect(logger.error).toBeTypeOf('function')
      expect(logger.log).toBeTypeOf('function')
    })

    it('should maintain state across multiple calls', () => {
      logger.warn('First call')
      logger.warn('Second call')

      expect(console.warn).toHaveBeenCalledTimes(2)
      expect(console.warn).toHaveBeenNthCalledWith(1, '[WARN] First call')
      expect(console.warn).toHaveBeenNthCalledWith(2, '[WARN] Second call')
    })
  })

  describe('edge cases', () => {
    it('should handle very long messages', () => {
      const longMessage = 'A'.repeat(10000)
      logger.warn(longMessage)
      expect(console.warn).toHaveBeenCalledWith(`[WARN] ${longMessage}`)
    })

    it('should handle objects with circular references', () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const obj: any = { name: 'test' }
      obj.self = obj

      logger.warn('Circular object', obj)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Circular object', obj)
    })

    it('should handle null and undefined in data', () => {
      logger.warn('Null and undefined', null, undefined)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Null and undefined', null, undefined)
    })

    it('should handle arrays of mixed types', () => {
      const mixedArray = [1, 'string', null, undefined, { key: 'value' }, [1, 2, 3]]
      logger.warn('Mixed array', mixedArray)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Mixed array', mixedArray)
    })

    it('should handle Symbol values', () => {
      const symbol = Symbol('test')
      logger.warn('Symbol value', symbol)
      expect(console.warn).toHaveBeenCalledWith('[WARN] Symbol value', symbol)
    })

    it('should handle BigInt values', () => {
      const bigInt = BigInt(9007199254740991)
      logger.warn('BigInt value', bigInt)
      expect(console.warn).toHaveBeenCalledWith('[WARN] BigInt value', bigInt)
    })
  })
})

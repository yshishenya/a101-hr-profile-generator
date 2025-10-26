/**
 * Theme toggle composable
 * Manages light/dark theme switching with localStorage persistence
 */

import { computed, type WritableComputedRef } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'

/**
 * Valid theme names supported by the application
 */
const VALID_THEMES = ['dark', 'light'] as const
type ThemeName = typeof VALID_THEMES[number]

/**
 * localStorage key for theme persistence
 */
const THEME_STORAGE_KEY = 'theme' as const

/**
 * Type guard to validate theme name from localStorage
 */
function isValidTheme(value: string | null): value is ThemeName {
  return value !== null && VALID_THEMES.includes(value as ThemeName)
}

/**
 * Composable for managing application theme (light/dark mode)
 *
 * @returns Theme management interface with reactive state and controls
 */
export function useTheme(): {
  isDark: WritableComputedRef<boolean>
  toggleTheme: () => void
  initTheme: () => void
} {
  const theme = useVuetifyTheme()

  const isDark = computed({
    get: () => theme.global.current.value.dark,
    set: (value: boolean) => {
      const themeName: ThemeName = value ? 'dark' : 'light'

      try {
        theme.change(themeName)
        localStorage.setItem(THEME_STORAGE_KEY, themeName)
      } catch (error) {
        console.error('Failed to change theme:', error)
      }
    }
  })

  /**
   * Toggle between light and dark themes
   * Persists selection to localStorage
   */
  function toggleTheme(): void {
    isDark.value = !isDark.value
  }

  /**
   * Initialize theme from localStorage on app startup
   * Falls back to system/default theme if no saved preference or invalid value
   */
  function initTheme(): void {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY)

    // Validate saved theme before applying
    if (isValidTheme(savedTheme)) {
      try {
        theme.change(savedTheme)
      } catch (error) {
        console.error('Failed to initialize theme:', error)
      }
    }
  }

  return { isDark, toggleTheme, initTheme }
}

/**
 * Theme toggle composable
 * Manages light/dark theme switching with localStorage persistence
 */

import { computed } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'

export function useTheme() {
  const theme = useVuetifyTheme()

  const isDark = computed({
    get: () => theme.global.current.value.dark,
    set: (value: boolean) => {
      theme.global.name.value = value ? 'dark' : 'light'
      localStorage.setItem('theme', value ? 'dark' : 'light')
    }
  })

  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      theme.global.name.value = savedTheme
    }
  }

  return { isDark, toggleTheme, initTheme }
}

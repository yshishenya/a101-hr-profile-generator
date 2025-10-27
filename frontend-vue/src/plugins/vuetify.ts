/**
 * Vuetify plugin configuration
 * Material Design component framework
 */

import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Import Vuetify styles
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,

  // Material Design Icons configuration
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },

  // Theme configuration
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#1976D2',    // A101 blue
          secondary: '#424242',  // Dark grey
          accent: '#82B1FF',     // Light blue accent
          error: '#FF5252',      // Red for errors
          success: '#4CAF50',    // Green for success
          warning: '#FFC107',    // Amber for warnings
          info: '#2196F3',       // Blue for info
          background: '#FFFFFF', // White background
          surface: '#FFFFFF',    // White surface
          'surface-variant': '#F5F5F5', // Light grey for headers/accents
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#1976D2',    // Same blue, works well on dark
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          success: '#4CAF50',
          warning: '#FFC107',
          info: '#2196F3',
          background: '#121212', // Dark background
          surface: '#1E1E1E',    // Dark surface for cards
          'surface-variant': '#2C2C2C', // Slightly lighter for headers
        },
      },
    },
  },

  // Display configuration
  display: {
    mobileBreakpoint: 'sm',
    thresholds: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },

  // Default component props
  defaults: {
    VBtn: {
      color: 'primary',
      variant: 'elevated',
    },
    VCard: {
      elevation: 2,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VDialog: {
      scrim: 'rgba(0, 0, 0, 0.5)',
    },
  },
})

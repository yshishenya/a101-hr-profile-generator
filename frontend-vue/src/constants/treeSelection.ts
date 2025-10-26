/**
 * Tree Selection Constants
 *
 * This file contains all constants related to organization tree selection UI.
 * Extracted for i18n preparation and maintainability.
 */

/**
 * Breakpoint display classes for Vuetify responsive design
 *
 * Vuetify Breakpoints:
 * - xs: <600px (extra small - mobile)
 * - sm: 600-959px (small - tablet)
 * - md: 960-1279px (medium - small desktop)
 * - lg: 1280-1919px (large - desktop)
 * - xl: ≥1920px (extra large)
 */
export const BREAKPOINT_CLASSES = {
  /** Desktop only: ≥960px (md+) - shows icons + full text */
  DESKTOP: 'd-none d-lg-inline-flex',

  /** Tablet only: 600-959px (sm) - shows text without icons */
  TABLET: 'd-none d-sm-inline-flex d-lg-none',

  /** Mobile only: <600px (xs) - shows compact text */
  MOBILE: 'd-inline-flex d-sm-none'
} as const

/**
 * Button configuration for selection actions
 */
export const BUTTON_CONFIG = {
  SIZE: 'x-small',
  VARIANT: 'outlined',
  COLOR: 'grey-darken-1'
} as const

/**
 * UI text strings for tree selection
 * TODO(i18n): Move to vue-i18n locale files when implementing multilingual support
 */
export const TREE_SELECTION_TEXT = {
  /** Button labels */
  BUTTON_DIRECT_FULL: 'Direct',
  BUTTON_DIRECT_COMPACT: 'Dir:',
  BUTTON_ALL_FULL: 'All',
  BUTTON_ALL_COMPACT: 'All:',

  /** Tooltip texts */
  TOOLTIP_DIRECT: 'Select only positions directly under this unit',
  TOOLTIP_ALL: 'Select all positions including nested units',

  /** Accessibility labels */
  ARIA_LABEL_DIRECT: 'Select direct positions only',
  ARIA_LABEL_ALL: 'Select all nested positions'
} as const

/**
 * Icon names for Material Design Icons (mdi)
 */
export const TREE_ICONS = {
  DIRECT_POSITIONS: 'mdi-file-document-outline',
  ALL_NESTED: 'mdi-file-tree'
} as const

/**
 * Type for button selection mode
 */
export type SelectionMode = 'direct' | 'all'

/**
 * Type for responsive breakpoint
 */
export type Breakpoint = 'desktop' | 'tablet' | 'mobile'

/**
 * Get button text based on mode and breakpoint
 */
export function getButtonText(mode: SelectionMode, breakpoint: Breakpoint, count: number): string {
  if (breakpoint === 'mobile') {
    const prefix = mode === 'direct'
      ? TREE_SELECTION_TEXT.BUTTON_DIRECT_COMPACT
      : TREE_SELECTION_TEXT.BUTTON_ALL_COMPACT
    return `${prefix} ${count}`
  }

  const label = mode === 'direct'
    ? TREE_SELECTION_TEXT.BUTTON_DIRECT_FULL
    : TREE_SELECTION_TEXT.BUTTON_ALL_FULL
  return `${label} (${count})`
}

/**
 * Get tooltip text based on selection mode
 */
export function getTooltipText(mode: SelectionMode): string {
  return mode === 'direct'
    ? TREE_SELECTION_TEXT.TOOLTIP_DIRECT
    : TREE_SELECTION_TEXT.TOOLTIP_ALL
}

/**
 * Get icon name based on selection mode
 */
export function getIconName(mode: SelectionMode): string {
  return mode === 'direct'
    ? TREE_ICONS.DIRECT_POSITIONS
    : TREE_ICONS.ALL_NESTED
}

/**
 * Get breakpoint class for Vuetify
 */
export function getBreakpointClass(breakpoint: Breakpoint): string {
  switch (breakpoint) {
    case 'desktop':
      return BREAKPOINT_CLASSES.DESKTOP
    case 'tablet':
      return BREAKPOINT_CLASSES.TABLET
    case 'mobile':
      return BREAKPOINT_CLASSES.MOBILE
  }
}

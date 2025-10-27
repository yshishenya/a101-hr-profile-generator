/**
 * Composable for task status utilities
 * Provides color and icon mappings for generation task statuses
 */

import type { GenerationTask } from '@/stores/generator'

interface TaskStatusComposable {
  getTaskStatusColor: (status: GenerationTask['status']) => string
  getTaskStatusIcon: (status: GenerationTask['status']) => string
}

export function useTaskStatus(): TaskStatusComposable {
  /**
   * Get Vuetify color for task status
   *
   * @param status - Current task status
   * @returns Vuetify color name
   */
  function getTaskStatusColor(status: GenerationTask['status']): string {
    switch (status) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      case 'processing':
        return 'primary'
      case 'queued':
        return 'info'
      default:
        return 'grey'
    }
  }

  /**
   * Get Material Design Icon name for task status
   *
   * @param status - Current task status
   * @returns MDI icon name
   */
  function getTaskStatusIcon(status: GenerationTask['status']): string {
    switch (status) {
      case 'completed':
        return 'mdi-check-circle'
      case 'failed':
        return 'mdi-alert-circle'
      case 'processing':
        return 'mdi-loading mdi-spin'
      case 'queued':
        return 'mdi-clock-outline'
      default:
        return 'mdi-help-circle'
    }
  }

  return {
    getTaskStatusColor,
    getTaskStatusIcon
  }
}

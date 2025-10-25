import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import api from '@/services/api'
import type { SearchableItem } from './catalog'

// Constants
const MAX_CONCURRENT_GENERATIONS = 5
const DEFAULT_TEMPERATURE = 0.7

// Types
export interface GenerationResult {
  profile_id: number
  content: string
  metadata: {
    position_id: string
    position_name: string
    business_unit_name: string
    generated_at: string
  }
}

export interface GenerationTask {
  task_id: string
  position_id: string
  position_name: string
  business_unit_name: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress?: number
  current_step?: string
  estimated_duration?: number
  result?: GenerationResult
  error?: string
  created_at: Date
}

export interface GenerationRequest {
  position_id: string
  position_name: string
  business_unit_name: string
  temperature?: number
  employee_name?: string
}

export interface GenerationConfig {
  temperature: number
  employee_name: string
}

class GenerationError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly originalError?: unknown
  ) {
    super(message)
    this.name = 'GenerationError'
  }
}

export const useGeneratorStore = defineStore('generator', () => {
  // State
  const activeTasks: Ref<Map<string, GenerationTask>> = ref(new Map())
  const selectedPosition: Ref<SearchableItem | null> = ref(null)
  const generationConfig: Ref<GenerationConfig> = ref({
    temperature: DEFAULT_TEMPERATURE,
    employee_name: ''
  })

  // Computed
  const hasPendingTasks = computed(() => {
    return Array.from(activeTasks.value.values()).some(
      task => task.status === 'queued' || task.status === 'processing'
    )
  })

  const completedCount = computed(() => {
    return Array.from(activeTasks.value.values()).filter(
      task => task.status === 'completed'
    ).length
  })

  const failedCount = computed(() => {
    return Array.from(activeTasks.value.values()).filter(
      task => task.status === 'failed'
    ).length
  })

  const totalCount = computed(() => activeTasks.value.size)

  const progressPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return Math.round((completedCount.value / totalCount.value) * 100)
  })

  // Actions
  /**
   * Start asynchronous profile generation for a position
   *
   * @param request - Generation parameters including position ID, name, and optional config
   * @returns Task ID for tracking generation progress
   * @throws GenerationError if validation fails or generation cannot be started
   *
   * @example
   * ```typescript
   * const taskId = await startGeneration({
   *   position_id: 'pos-123',
   *   position_name: 'Software Engineer',
   *   business_unit_name: 'Engineering',
   *   temperature: 0.7
   * })
   * ```
   */
  async function startGeneration(request: GenerationRequest): Promise<string> {
    // Validate input
    if (!request.position_id?.trim()) {
      throw new GenerationError(
        'Position ID is required',
        'VALIDATION_ERROR'
      )
    }

    if (!request.position_name?.trim()) {
      throw new GenerationError(
        'Position name is required',
        'VALIDATION_ERROR'
      )
    }

    if (!request.business_unit_name?.trim()) {
      throw new GenerationError(
        'Business unit name is required',
        'VALIDATION_ERROR'
      )
    }

    if (request.temperature !== undefined &&
        (request.temperature < 0.3 || request.temperature > 1.0)) {
      throw new GenerationError(
        'Temperature must be between 0.3 and 1.0',
        'VALIDATION_ERROR'
      )
    }

    try {
      const response = await api.post('/api/generation/start', {
        position_id: request.position_id,
        position_name: request.position_name,
        business_unit_name: request.business_unit_name,
        temperature: request.temperature ?? generationConfig.value.temperature,
        employee_name: request.employee_name ?? generationConfig.value.employee_name
      })

      const { task_id, estimated_duration } = response.data.data

      const task: GenerationTask = {
        task_id,
        position_id: request.position_id,
        position_name: request.position_name,
        business_unit_name: request.business_unit_name,
        status: 'queued',
        progress: 0,
        estimated_duration,
        created_at: new Date()
      }

      activeTasks.value.set(task_id, task)
      return task_id
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error('Failed to start generation:', error)
      }

      throw new GenerationError(
        (error as any).response?.data?.detail || 'Failed to start generation',
        'API_ERROR',
        error
      )
    }
  }

  /**
   * Poll the status of a generation task
   * Updates the task state in the store with current progress
   *
   * @param taskId - Unique identifier for the generation task
   * @throws GenerationError if polling fails
   */
  async function pollTaskStatus(taskId: string): Promise<void> {
    if (!taskId?.trim()) {
      throw new GenerationError(
        'Task ID is required',
        'VALIDATION_ERROR'
      )
    }

    try {
      const response = await api.get(`/api/generation/${taskId}/status`)
      const statusData = response.data.data

      const existingTask = activeTasks.value.get(taskId)
      if (!existingTask) return

      const updatedTask: GenerationTask = {
        ...existingTask,
        status: statusData.status,
        progress: statusData.progress,
        current_step: statusData.current_step,
        error: statusData.error
      }

      activeTasks.value.set(taskId, updatedTask)

      // If completed, fetch result
      if (statusData.status === 'completed') {
        await getTaskResult(taskId)
      }
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error(`Failed to poll task ${taskId}:`, error)
      }

      const existingTask = activeTasks.value.get(taskId)
      if (existingTask) {
        activeTasks.value.set(taskId, {
          ...existingTask,
          status: 'failed',
          error: (error as any).response?.data?.detail || 'Failed to check status'
        })
      }
    }
  }

  /**
   * Retrieve the result of a completed generation task
   *
   * @param taskId - Unique identifier for the generation task
   * @returns The generated profile result
   * @throws GenerationError if result cannot be retrieved
   */
  async function getTaskResult(taskId: string): Promise<GenerationResult> {
    if (!taskId?.trim()) {
      throw new GenerationError(
        'Task ID is required',
        'VALIDATION_ERROR'
      )
    }

    try {
      const response = await api.get(`/api/generation/${taskId}/result`)
      const result: GenerationResult = response.data.data

      const existingTask = activeTasks.value.get(taskId)
      if (existingTask) {
        activeTasks.value.set(taskId, {
          ...existingTask,
          result,
          status: 'completed',
          progress: 100
        })
      }

      return result
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error(`Failed to get result for task ${taskId}:`, error)
      }

      throw new GenerationError(
        'Failed to retrieve generation result',
        'API_ERROR',
        error
      )
    }
  }

  /**
   * Cancel a running or queued generation task
   *
   * @param taskId - Unique identifier for the generation task
   * @throws GenerationError if cancellation fails
   */
  async function cancelTask(taskId: string): Promise<void> {
    if (!taskId?.trim()) {
      throw new GenerationError(
        'Task ID is required',
        'VALIDATION_ERROR'
      )
    }

    try {
      await api.delete(`/api/generation/${taskId}`)
      activeTasks.value.delete(taskId)
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error(`Failed to cancel task ${taskId}:`, error)
      }

      throw new GenerationError(
        'Failed to cancel generation task',
        'API_ERROR',
        error
      )
    }
  }

  /**
   * Remove all completed and failed tasks from the active tasks list
   */
  function clearCompleted(): void {
    const tasks = Array.from(activeTasks.value.entries())
    tasks.forEach(([taskId, task]) => {
      if (task.status === 'completed' || task.status === 'failed') {
        activeTasks.value.delete(taskId)
      }
    })
  }

  /**
   * Set the currently selected position for generation
   *
   * @param position - The position to select, or null to clear selection
   */
  function setSelectedPosition(position: SearchableItem | null): void {
    selectedPosition.value = position
  }

  /**
   * Update generation configuration settings
   *
   * @param config - Partial configuration to merge with current settings
   */
  function updateConfig(config: Partial<GenerationConfig>): void {
    generationConfig.value = {
      ...generationConfig.value,
      ...config
    }
  }

  /**
   * Start bulk profile generation for multiple positions
   * Processes positions with controlled concurrency to prevent API overload
   *
   * @param positions - Array of positions to generate profiles for
   * @returns Array of task IDs for tracking progress
   *
   * @example
   * ```typescript
   * const taskIds = await startBulkGeneration([
   *   { position_id: '1', position_name: 'Developer', business_unit_name: 'Engineering' },
   *   { position_id: '2', position_name: 'Designer', business_unit_name: 'Product' }
   * ])
   * ```
   */
  async function startBulkGeneration(positions: SearchableItem[]): Promise<string[]> {
    if (!Array.isArray(positions) || positions.length === 0) {
      throw new GenerationError(
        'At least one position is required',
        'VALIDATION_ERROR'
      )
    }

    const taskIds: string[] = []
    const queue = [...positions]

    async function processNext(): Promise<void> {
      if (queue.length === 0) return

      const position = queue.shift()!
      try {
        const taskId = await startGeneration({
          position_id: position.position_id,
          position_name: position.position_name,
          business_unit_name: position.business_unit_name
        })
        taskIds.push(taskId)
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error(`Failed to start generation for ${position.position_name}:`, error)
        }
      }

      await processNext()
    }

    // Start processing with concurrency limit
    const workers = Array(Math.min(MAX_CONCURRENT_GENERATIONS, positions.length))
      .fill(null)
      .map(() => processNext())

    await Promise.all(workers)
    return taskIds
  }

  return {
    // State
    activeTasks,
    selectedPosition,
    generationConfig,

    // Computed
    hasPendingTasks,
    completedCount,
    failedCount,
    totalCount,
    progressPercentage,

    // Actions
    startGeneration,
    pollTaskStatus,
    getTaskResult,
    cancelTask,
    clearCompleted,
    setSelectedPosition,
    updateConfig,
    startBulkGeneration
  }
})

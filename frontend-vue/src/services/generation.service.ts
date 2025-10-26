/**
 * Generation Service - Profile generation and task management
 * Handles AI-powered profile generation workflow
 */

import api from './api'
import type {
  GenerationRequest,
  GenerationResponse,
  GenerationResult,
  GenerationTask
} from '@/types/generation'
import type { TaskStatusResponse } from '@/types/api'

/**
 * Start new profile generation task
 *
 * @param request - Generation parameters (department, position, optional employee_name)
 * @returns Promise<GenerationResponse> Task info with task_id for polling
 * @throws AxiosError if request fails
 *
 * @example
 * const response = await generationService.startGeneration({
 *   department: 'Отдел разработки',
 *   position: 'Senior Developer',
 *   employee_name: 'Иван Петров',
 *   temperature: 0.7,
 *   save_result: true
 * })
 * console.log(`Task started: ${response.task_id}`)
 */
export async function startGeneration(request: GenerationRequest): Promise<GenerationResponse> {
  const response = await api.post<GenerationResponse>('/api/generation/start', request)
  // Backend returns: { success, timestamp, message, task_id, status, estimated_duration }
  // Fields are at root level, not nested in data
  return response.data
}

/**
 * Get current status of generation task
 * Use for polling until status becomes 'completed' or 'failed'
 *
 * @param taskId - Task ID from startGeneration response
 * @returns Promise<TaskStatusResponse> Current task status with optional result
 * @throws AxiosError if request fails
 *
 * @example
 * const status = await generationService.getTaskStatus(taskId)
 * if (status.task.status === 'completed') {
 *   console.log('Generation completed:', status.result)
 * }
 */
export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const response = await api.get<TaskStatusResponse>(`/api/generation/${taskId}/status`)
  // Backend returns: { success, timestamp, task: {...}, result: {...} }
  // Task data is nested under 'task' field
  return response.data
}

/**
 * Get result of completed generation task
 * Only available after task status is 'completed'
 *
 * @param taskId - Task ID from startGeneration response
 * @returns Promise<GenerationResult> Generated profile with metadata
 * @throws AxiosError if request fails (404 if not completed)
 *
 * @example
 * const result = await generationService.getTaskResult(taskId)
 * console.log('Profile:', result.profile)
 * console.log('Tokens used:', result.metadata.llm.tokens.total)
 */
export async function getTaskResult(taskId: string): Promise<GenerationResult> {
  const response = await api.get<GenerationResult>(`/api/generation/${taskId}/result`)
  // Backend returns raw result object directly (not wrapped in BaseResponse)
  return response.data
}

/**
 * Cancel running or queued generation task
 *
 * @param taskId - Task ID to cancel
 * @returns Promise<void>
 * @throws AxiosError if request fails
 *
 * @example
 * await generationService.cancelTask(taskId)
 * console.log('Task cancelled')
 */
export async function cancelTask(taskId: string): Promise<void> {
  await api.delete(`/api/generation/${taskId}`)
}

/**
 * Get list of all active (queued or processing) tasks
 * Useful for monitoring and preventing duplicate generations
 *
 * @returns Promise<GenerationTask[]> Array of active tasks
 * @throws AxiosError if request fails
 *
 * @example
 * const activeTasks = await generationService.getActiveTasks()
 * console.log(`${activeTasks.length} tasks in progress`)
 */
export async function getActiveTasks(): Promise<GenerationTask[]> {
  const response = await api.get<GenerationTask[]>('/api/generation/tasks/active')
  // Backend returns array directly (not wrapped in BaseResponse for this endpoint)
  return response.data
}

export default {
  startGeneration,
  getTaskStatus,
  getTaskResult,
  cancelTask,
  getActiveTasks
}

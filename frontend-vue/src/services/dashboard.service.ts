/**
 * Dashboard Service - Statistics and activity monitoring
 * Provides real-time metrics for dashboard views
 */

import api from './api'
import type { DashboardStats } from '@/types/api'

/**
 * Activity statistics for recent generation tasks
 */
export interface ActivityStats {
  recent_tasks: Array<{
    task_id: string
    status: string
    position: string
    department: string
    created_at: string
  }>
  hourly_stats: Array<{
    hour: string
    completed: number
    failed: number
  }>
}

/**
 * Minimal stats response for lightweight polling
 */
export interface MinimalStats {
  active_tasks_count: number
  last_updated: string
}

/**
 * Get comprehensive dashboard statistics
 * Includes all metrics: positions, profiles, completion rate, active tasks
 *
 * @returns Promise<DashboardStats> Full dashboard metrics
 * @throws AxiosError if request fails
 *
 * @example
 * const stats = await dashboardService.getStats()
 * console.log(`${stats.profiles_count} profiles generated`)
 * console.log(`${stats.completion_percentage}% complete`)
 */
export async function getStats(): Promise<DashboardStats> {
  const response = await api.get<DashboardStats>('/api/dashboard/stats')
  // Backend returns nested structure: { success, timestamp, summary: {...}, metadata: {...} }
  // The DashboardView component handles flattening this structure
  return response.data
}

/**
 * Get minimal statistics for lightweight polling
 * Only returns active tasks count for real-time monitoring
 *
 * @returns Promise<MinimalStats> Active tasks count only
 * @throws AxiosError if request fails
 *
 * @example
 * const stats = await dashboardService.getMinimalStats()
 * console.log(`${stats.active_tasks_count} tasks in progress`)
 */
export async function getMinimalStats(): Promise<MinimalStats> {
  const response = await api.get<MinimalStats>('/api/dashboard/stats/minimal')
  // Backend returns: { success, timestamp, active_tasks_count, last_updated }
  return response.data
}

/**
 * Get recent activity and generation history
 * Useful for activity feed and analytics
 *
 * @returns Promise<ActivityStats> Recent tasks and hourly statistics
 * @throws AxiosError if request fails
 *
 * @example
 * const activity = await dashboardService.getActivity()
 * console.log(`Last ${activity.recent_tasks.length} tasks:`)
 * activity.recent_tasks.forEach(task => {
 *   console.log(`- ${task.position}: ${task.status}`)
 * })
 */
export async function getActivity(): Promise<ActivityStats> {
  const response = await api.get<ActivityStats>('/api/dashboard/stats/activity')
  // Backend returns: { success, timestamp, data: { recent_tasks, hourly_stats } }
  return response.data
}

export default {
  getStats,
  getMinimalStats,
  getActivity
}

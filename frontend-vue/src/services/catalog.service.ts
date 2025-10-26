/**
 * Catalog Service - Organization structure and positions
 * Provides access to positions catalog from backend
 */

import api from './api'
import type { Position } from '@/types/profile'

/**
 * Get all available positions from organization structure
 * Returns 1689 positions with department hierarchy
 *
 * NOTE: This endpoint is deprecated - use /api/organization/positions instead
 * which returns the correct BaseResponse format
 *
 * @returns Promise<Position[]> Array of all positions
 * @throws AxiosError if request fails
 *
 * @example
 * const positions = await catalogService.getPositions()
 * console.log(`Loaded ${positions.length} positions`)
 */
export async function getPositions(): Promise<Position[]> {
  const response = await api.get<{ success: boolean; data: { items: Position[] } }>('/api/organization/search-items')
  // Backend returns: { success, timestamp, message, data: { items, total_count } }
  return response.data.data.items
}

export default {
  getPositions
}

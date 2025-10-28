/**
 * Utilities for extracting section data from profile
 */

import type { ProfileData } from '@/types/profile'
import { SECTION_FIELD_MAP } from '../constants/profileSections'

/**
 * Extracts section-specific data from full profile data
 */
export function extractSectionData(sectionId: string, profileData: ProfileData): unknown {
  // For basic_info, return the basic_info object directly
  if (sectionId === 'basic_info') {
    return profileData.basic_info
  }

  // For other sections, use the field map
  const field = SECTION_FIELD_MAP[sectionId]
  if (!field) return null

  // Use type-safe property access
  return profileData[field as keyof ProfileData]
}

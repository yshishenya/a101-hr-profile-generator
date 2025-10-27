/**
 * Utilities for extracting section data from profile
 */

import type { ProfileData } from '@/types/profile'
import { SECTION_FIELD_MAP } from '../constants/profileSections'

/**
 * Extracts section-specific data from full profile data
 */
export function extractSectionData(sectionId: string, profileData: ProfileData): unknown {
  // For basic_info, extract only the fields that BasicInfoEditor handles
  if (sectionId === 'basic_info') {
    return {
      direct_manager: (profileData as Record<string, unknown>).direct_manager as string,
      primary_activity_type: (profileData as Record<string, unknown>)
        .primary_activity_type as string,
    }
  }

  // For other sections, use the field map
  const field = SECTION_FIELD_MAP[sectionId]
  if (!field) return null

  return (profileData as Record<string, unknown>)[field]
}

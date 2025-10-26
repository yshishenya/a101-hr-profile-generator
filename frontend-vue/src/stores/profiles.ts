/**
 * Profiles Store - Legacy Entry Point
 *
 * This file maintains backward compatibility by re-exporting
 * from the new modular profiles store structure.
 *
 * All new code should import from '@/stores/profiles' (this file)
 * The implementation has been split into smaller modules in profiles/
 */

export { useProfilesStore } from './profiles/index'
export { ProfileError } from './profiles/types'

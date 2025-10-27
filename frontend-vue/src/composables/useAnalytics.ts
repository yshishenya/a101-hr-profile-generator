/**
 * Analytics Tracking Composable
 *
 * Provides analytics tracking functionality for user interactions and events.
 * Currently logs events to console in development, ready to be extended
 * with analytics platforms (Google Analytics, Mixpanel, Plausible, etc.).
 *
 * @module composables/useAnalytics
 *
 * @example
 * ```typescript
 * import { useAnalytics } from '@/composables/useAnalytics'
 *
 * const analytics = useAnalytics()
 *
 * // Track version viewed
 * analytics.trackVersionListViewed('prof_123', 5, 3)
 *
 * // Track version activated
 * analytics.trackVersionActivated('prof_123', 2, 3)
 * ```
 */

import { logger } from '@/utils/logger'
import type {
  VersionListViewedEvent,
  VersionActivatedEvent,
  VersionDownloadedEvent,
  VersionDeletedEvent,
  DownloadFormat
} from '@/types/analytics'

/**
 * Analytics composable interface
 */
export interface UseAnalyticsReturn {
  /** Track when versions list is viewed */
  trackVersionListViewed: (
    profileId: string,
    totalVersions: number,
    currentVersion: number
  ) => void
  /** Track when version is activated */
  trackVersionActivated: (
    profileId: string,
    previousVersion: number,
    newVersion: number
  ) => void
  /** Track when version is downloaded */
  trackVersionDownloaded: (
    profileId: string,
    versionNumber: number,
    format: DownloadFormat
  ) => void
  /** Track when version is deleted */
  trackVersionDeleted: (
    profileId: string,
    versionNumber: number,
    remainingVersions: number
  ) => void
}

/**
 * Check if analytics is enabled
 * Can be controlled via environment variable
 *
 * @returns True if analytics is enabled
 */
function isAnalyticsEnabled(): boolean {
  // In production, check environment variable
  // For now, always enabled in development
  return import.meta.env.DEV || import.meta.env.VITE_ANALYTICS_ENABLED === 'true'
}

/**
 * Send event to analytics platform
 * Currently logs to console, ready to be extended with real analytics
 *
 * @param event - Analytics event to send
 */
function sendAnalyticsEvent(
  event: VersionListViewedEvent | VersionActivatedEvent | VersionDownloadedEvent | VersionDeletedEvent
): void {
  if (!isAnalyticsEnabled()) {
    return
  }

  // Log event in development for debugging
  if (import.meta.env.DEV) {
    logger.info(`[Analytics] ${event.event}`, event.properties)
  }

  // TODO: Integrate with analytics platform
  // Example integrations:
  //
  // Google Analytics 4:
  // gtag('event', event.event, event.properties)
  //
  // Mixpanel:
  // mixpanel.track(event.event, event.properties)
  //
  // Plausible:
  // plausible(event.event, { props: event.properties })
  //
  // Custom endpoint:
  // fetch('/api/analytics', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(event)
  // })
}

/**
 * Analytics tracking composable
 *
 * Provides methods to track version-related user interactions.
 * Events are currently logged to console in development mode.
 * Ready to be extended with analytics platforms (GA4, Mixpanel, etc.).
 *
 * @returns Analytics tracking methods
 *
 * @example
 * ```typescript
 * const analytics = useAnalytics()
 *
 * // Track versions tab opened
 * analytics.trackVersionListViewed('prof_123', 5, 3)
 *
 * // Track version activation
 * analytics.trackVersionActivated('prof_123', 2, 3)
 *
 * // Track version download
 * analytics.trackVersionDownloaded('prof_123', 2, 'json')
 *
 * // Track version deletion
 * analytics.trackVersionDeleted('prof_123', 2, 4)
 * ```
 */
export function useAnalytics(): UseAnalyticsReturn {
  /**
   * Track when user views versions list
   *
   * @param profileId - Profile ID
   * @param totalVersions - Total number of versions
   * @param currentVersion - Current active version number
   */
  function trackVersionListViewed(
    profileId: string,
    totalVersions: number,
    currentVersion: number
  ): void {
    const event: VersionListViewedEvent = {
      event: 'version_list_viewed',
      timestamp: new Date(),
      properties: {
        profile_id: profileId,
        total_versions: totalVersions,
        current_version: currentVersion
      }
    }
    sendAnalyticsEvent(event)
  }

  /**
   * Track when user activates a version
   *
   * @param profileId - Profile ID
   * @param previousVersion - Previous active version number
   * @param newVersion - New active version number
   */
  function trackVersionActivated(
    profileId: string,
    previousVersion: number,
    newVersion: number
  ): void {
    const event: VersionActivatedEvent = {
      event: 'version_activated',
      timestamp: new Date(),
      properties: {
        profile_id: profileId,
        previous_version: previousVersion,
        new_version: newVersion
      }
    }
    sendAnalyticsEvent(event)
  }

  /**
   * Track when user downloads a version
   *
   * @param profileId - Profile ID
   * @param versionNumber - Version number being downloaded
   * @param format - Download format (json, md, or docx)
   */
  function trackVersionDownloaded(
    profileId: string,
    versionNumber: number,
    format: DownloadFormat
  ): void {
    const event: VersionDownloadedEvent = {
      event: 'version_downloaded',
      timestamp: new Date(),
      properties: {
        profile_id: profileId,
        version_number: versionNumber,
        format
      }
    }
    sendAnalyticsEvent(event)
  }

  /**
   * Track when user deletes a version
   *
   * @param profileId - Profile ID
   * @param versionNumber - Version number being deleted
   * @param remainingVersions - Number of versions remaining after deletion
   */
  function trackVersionDeleted(
    profileId: string,
    versionNumber: number,
    remainingVersions: number
  ): void {
    const event: VersionDeletedEvent = {
      event: 'version_deleted',
      timestamp: new Date(),
      properties: {
        profile_id: profileId,
        version_number: versionNumber,
        remaining_versions: remainingVersions
      }
    }
    sendAnalyticsEvent(event)
  }

  return {
    trackVersionListViewed,
    trackVersionActivated,
    trackVersionDownloaded,
    trackVersionDeleted
  }
}

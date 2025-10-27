/**
 * Analytics event types and interfaces
 *
 * This module defines all analytics events for tracking user interactions
 * and system events throughout the application.
 *
 * @module types/analytics
 */

/**
 * Version operation event types
 */
export type VersionEventType =
  | 'version_list_viewed'
  | 'version_activated'
  | 'version_downloaded'
  | 'version_deleted'

/**
 * Download format types
 */
export type DownloadFormat = 'json' | 'md' | 'docx'

/**
 * Base analytics event interface
 */
export interface AnalyticsEvent {
  /** Event type identifier */
  event: string
  /** Timestamp when event occurred */
  timestamp: Date
  /** Optional additional properties */
  properties?: Record<string, unknown>
}

/**
 * Version list viewed event
 * Triggered when user switches to versions tab
 */
export interface VersionListViewedEvent extends AnalyticsEvent {
  event: 'version_list_viewed'
  properties: {
    profile_id: string
    total_versions: number
    current_version: number
  }
}

/**
 * Version activated event
 * Triggered when user sets a version as active
 */
export interface VersionActivatedEvent extends AnalyticsEvent {
  event: 'version_activated'
  properties: {
    profile_id: string
    previous_version: number
    new_version: number
  }
}

/**
 * Version downloaded event
 * Triggered when user downloads a specific version
 */
export interface VersionDownloadedEvent extends AnalyticsEvent {
  event: 'version_downloaded'
  properties: {
    profile_id: string
    version_number: number
    format: DownloadFormat
  }
}

/**
 * Version deleted event
 * Triggered when user deletes a version
 */
export interface VersionDeletedEvent extends AnalyticsEvent {
  event: 'version_deleted'
  properties: {
    profile_id: string
    version_number: number
    remaining_versions: number
  }
}

/**
 * Union type of all version events
 */
export type VersionAnalyticsEvent =
  | VersionListViewedEvent
  | VersionActivatedEvent
  | VersionDownloadedEvent
  | VersionDeletedEvent

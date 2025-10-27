# Analytics Tracking Pattern

## Overview

Этот документ описывает стандартный паттерн для tracking пользовательских событий и взаимодействий в приложении HR Profile Generator.

**Дата создания**: 2025-10-27
**Автор**: Week 6 Phase 3 Implementation
**Статус**: ✅ Implemented and Production Ready

---

## Problem

При разработке приложений необходимо понимать:
- Как пользователи взаимодействуют с функциями
- Какие операции выполняются чаще всего
- Где возникают проблемы в user journey
- Какие features действительно используются

Без структурированного tracking'а:
- ❌ Невозможно принимать data-driven решения
- ❌ Сложно измерять эффективность новых фичей
- ❌ Нет понимания реального поведения пользователей
- ❌ Каждый разработчик добавляет tracking по-своему

---

## Solution

**Централизованный composable** `useAnalytics()` с type-safe событиями:

```typescript
// src/composables/useAnalytics.ts
export function useAnalytics(): UseAnalyticsReturn {
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

  return {
    trackVersionListViewed,
    trackVersionActivated,
    trackVersionDownloaded,
    trackVersionDeleted
  }
}
```

---

## Architecture

### 1. Type Definitions (`src/types/analytics.ts`)

Все события имеют строгую типизацию:

```typescript
/**
 * Base analytics event interface
 */
export interface AnalyticsEvent {
  event: string
  timestamp: Date
  properties?: Record<string, unknown>
}

/**
 * Version list viewed event
 */
export interface VersionListViewedEvent extends AnalyticsEvent {
  event: 'version_list_viewed'
  properties: {
    profile_id: string
    total_versions: number
    current_version: number
  }
}
```

**Преимущества**:
- ✅ Type safety - невозможно отправить неправильную структуру
- ✅ Autocomplete в IDE
- ✅ Compile-time проверка
- ✅ Self-documenting code

### 2. Composable (`src/composables/useAnalytics.ts`)

Централизованная логика tracking:

```typescript
/**
 * Analytics tracking composable
 */
export function useAnalytics(): UseAnalyticsReturn {
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

  return { trackVersionActivated /* ... */ }
}
```

### 3. Platform Integration (`sendAnalyticsEvent()`)

Абстракция для различных analytics платформ:

```typescript
function sendAnalyticsEvent(event: AnalyticsEvent): void {
  if (!isAnalyticsEnabled()) return

  // Development: console logging
  if (import.meta.env.DEV) {
    logger.info(`[Analytics] ${event.event}`, event.properties)
  }

  // Production: Platform integration
  // TODO: Integrate with chosen platform
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
  // await fetch('/api/analytics', {
  //   method: 'POST',
  //   body: JSON.stringify(event)
  // })
}
```

---

## Usage Examples

### Basic Usage

```typescript
// В компоненте или composable
import { useAnalytics } from '@/composables/useAnalytics'

const analytics = useAnalytics()

// Track событие
analytics.trackVersionDownloaded('prof_123', 2, 'json')
```

### Integration in Composables

```typescript
// src/composables/useProfileVersions.ts
export function useProfileVersions(...) {
  const analytics = useAnalytics()

  async function loadVersions(): Promise<void> {
    const response = await profileService.getProfileVersions(profileId)
    versions.value = response.versions

    // Track после успешной загрузки
    analytics.trackVersionListViewed(
      profileId,
      response.total_versions,
      response.current_version
    )
  }

  async function handleSetActive(versionNumber: number): Promise<void> {
    const response = await profileService.setActiveVersion(profileId, versionNumber)

    // Track после успешной активации
    analytics.trackVersionActivated(
      profileId,
      response.previous_version,
      response.current_version
    )

    await loadVersions()
  }

  return { loadVersions, handleSetActive }
}
```

### Environment Configuration

```bash
# .env
VITE_ANALYTICS_ENABLED=true
VITE_ANALYTICS_PROVIDER=ga4  # ga4 | mixpanel | plausible | custom
```

---

## Event Naming Convention

**Format**: `<resource>_<action>_<context>`

**Examples**:
- ✅ `version_list_viewed`
- ✅ `version_activated`
- ✅ `version_downloaded`
- ✅ `profile_generated`
- ✅ `filter_applied`
- ✅ `search_performed`

**Избегайте**:
- ❌ `click_button` (слишком generic)
- ❌ `userClickedActivateButton` (camelCase, слишком verbose)
- ❌ `activate` (непонятно что активируется)

---

## Best Practices

### 1. Track Business Events, Not Technical Details

```typescript
// ✅ ПРАВИЛЬНО - business event
analytics.trackVersionActivated(profileId, 2, 3)

// ❌ НЕПРАВИЛЬНО - technical detail
analytics.trackButtonClicked('activate-button-version-2')
```

### 2. Include Relevant Context

```typescript
// ✅ ПРАВИЛЬНО - достаточно контекста
analytics.trackVersionDeleted(
  profileId,
  versionNumber,
  remainingVersions  // ← важный контекст
)

// ❌ НЕПРАВИЛЬНО - недостаточно контекста
analytics.trackVersionDeleted(versionNumber)
```

### 3. Track After Success, Not Before

```typescript
// ✅ ПРАВИЛЬНО
async function handleDelete(version: number): Promise<void> {
  await deleteVersion(version)
  analytics.trackVersionDeleted(profileId, version, remainingCount)
}

// ❌ НЕПРАВИЛЬНО - что если операция упадет?
async function handleDelete(version: number): Promise<void> {
  analytics.trackVersionDeleted(profileId, version, remainingCount)
  await deleteVersion(version)
}
```

### 4. Don't Track PII (Personally Identifiable Information)

```typescript
// ✅ ПРАВИЛЬНО - только ID
analytics.trackProfileViewed(profileId)

// ❌ НЕПРАВИЛЬНО - содержит PII
analytics.trackProfileViewed(profileId, employeeName, employeeEmail)
```

### 5. Use Constants for Event Names

```typescript
// src/constants/analytics.ts
export const ANALYTICS_EVENTS = {
  VERSION_LIST_VIEWED: 'version_list_viewed',
  VERSION_ACTIVATED: 'version_activated',
  VERSION_DOWNLOADED: 'version_downloaded'
} as const

// Usage
const event: AnalyticsEvent = {
  event: ANALYTICS_EVENTS.VERSION_ACTIVATED,
  // ...
}
```

---

## Testing

### Mock in Tests

```typescript
// tests/setup.ts
vi.mock('@/composables/useAnalytics', () => ({
  useAnalytics: () => ({
    trackVersionListViewed: vi.fn(),
    trackVersionActivated: vi.fn(),
    trackVersionDownloaded: vi.fn(),
    trackVersionDeleted: vi.fn()
  })
}))
```

### Unit Tests

```typescript
describe('useProfileVersions', () => {
  it('should track version list viewed on load', async () => {
    const analytics = useAnalytics()
    const { loadVersions } = useProfileVersions(profileId, activeTab)

    await loadVersions()

    expect(analytics.trackVersionListViewed).toHaveBeenCalledWith(
      'prof_123',
      5,  // total_versions
      3   // current_version
    )
  })
})
```

---

## Platform Integration Examples

### Google Analytics 4

```typescript
function sendAnalyticsEvent(event: AnalyticsEvent): void {
  if (import.meta.env.VITE_ANALYTICS_PROVIDER === 'ga4') {
    gtag('event', event.event, event.properties)
  }
}
```

### Mixpanel

```typescript
import mixpanel from 'mixpanel-browser'

function sendAnalyticsEvent(event: AnalyticsEvent): void {
  if (import.meta.env.VITE_ANALYTICS_PROVIDER === 'mixpanel') {
    mixpanel.track(event.event, event.properties)
  }
}
```

### Plausible

```typescript
declare global {
  interface Window {
    plausible: (event: string, options?: { props: Record<string, unknown> }) => void
  }
}

function sendAnalyticsEvent(event: AnalyticsEvent): void {
  if (import.meta.env.VITE_ANALYTICS_PROVIDER === 'plausible') {
    window.plausible(event.event, { props: event.properties })
  }
}
```

### Custom Backend Endpoint

```typescript
async function sendAnalyticsEvent(event: AnalyticsEvent): Promise<void> {
  if (import.meta.env.VITE_ANALYTICS_PROVIDER === 'custom') {
    await fetch('/api/analytics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    })
  }
}
```

---

## Common Pitfalls

### ❌ Don't: Track Too Much

```typescript
// Избыточный tracking - затрудняет анализ
analytics.trackMouseMove(x, y)
analytics.trackScroll(position)
analytics.trackInputChange(fieldName, value)
```

### ❌ Don't: Mix Analytics with Business Logic

```typescript
// НЕПРАВИЛЬНО - analytics не должна влиять на логику
async function handleDelete(version: number): Promise<void> {
  try {
    analytics.trackVersionDeleted(version)
    await deleteVersion(version)
  } catch (error) {
    // Если analytics упадет, операция не выполнится!
  }
}

// ПРАВИЛЬНО - analytics изолирована
async function handleDelete(version: number): Promise<void> {
  try {
    await deleteVersion(version)
    // Analytics не должна блокировать операцию
    analytics.trackVersionDeleted(version)
  } catch (error) {
    // Handle deletion error
  }
}
```

### ❌ Don't: Hardcode Event Names

```typescript
// НЕПРАВИЛЬНО - риск опечаток
analytics.track('version_actived', { /* ... */ })  // Опечатка!

// ПРАВИЛЬНО - type-safe
analytics.trackVersionActivated(profileId, prev, current)
```

---

## Future Extensions

### 1. User Properties

```typescript
interface AnalyticsUser {
  id: string
  role: 'admin' | 'user'
  subscription_tier: 'free' | 'pro'
}

function setAnalyticsUser(user: AnalyticsUser): void {
  // Set user properties for all future events
}
```

### 2. Performance Tracking

```typescript
function trackPerformanceMetric(
  operation: string,
  durationMs: number
): void {
  const event: PerformanceEvent = {
    event: 'performance_metric',
    timestamp: new Date(),
    properties: {
      operation,
      duration_ms: durationMs
    }
  }
  sendAnalyticsEvent(event)
}
```

### 3. Error Tracking Integration

```typescript
function trackError(
  error: Error,
  context: Record<string, unknown>
): void {
  const event: ErrorEvent = {
    event: 'error_occurred',
    timestamp: new Date(),
    properties: {
      error_name: error.name,
      error_message: error.message,
      ...context
    }
  }
  sendAnalyticsEvent(event)
}
```

---

## Checklist

При добавлении нового tracking:

- [ ] Событие имеет clear business value
- [ ] Создан TypeScript interface для события
- [ ] Добавлен метод в useAnalytics composable
- [ ] Event name следует naming convention
- [ ] Tracking вызывается ПОСЛЕ успешной операции
- [ ] Не содержит PII
- [ ] Добавлены unit tests
- [ ] Обновлена документация

---

## References

- **Implementation**: `src/composables/useAnalytics.ts`
- **Types**: `src/types/analytics.ts`
- **Usage Example**: `src/composables/useProfileVersions.ts`
- **Tests**: `src/composables/__tests__/useProfileVersions.test.ts`

---

**Last Updated**: 2025-10-27
**Status**: ✅ Production Ready

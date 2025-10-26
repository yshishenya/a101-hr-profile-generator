# BaseCard Component Test Plan

**Component:** BaseCard.vue
**Location:** `frontend-vue/src/components/common/BaseCard.vue`
**Date:** 2025-10-26
**Status:** Ready for testing (when Vitest is integrated)

## Test Coverage Goals

- **Unit Tests:** 100% code coverage
- **Integration Tests:** All use cases in views
- **Visual Tests:** Snapshot tests for all prop variations
- **Accessibility Tests:** WCAG AA compliance

## 1. Unit Tests (Vitest + @vue/test-utils)

### 1.1 Props Testing

```typescript
// src/components/common/__tests__/BaseCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { vuetify } from '@/plugins/vuetify'
import BaseCard from '../BaseCard.vue'

describe('BaseCard Props', () => {
  it('should render with default elevation (2)', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('elevation')).toBe(2)
  })

  it('should accept custom elevation prop', () => {
    const wrapper = mount(BaseCard, {
      props: { elevation: 4 },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('elevation')).toBe(4)
  })

  it('should render with default rounded (lg)', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('rounded')).toBe('lg')
  })

  it('should accept custom rounded prop', () => {
    const wrapper = mount(BaseCard, {
      props: { rounded: 'xl' },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('rounded')).toBe('xl')
  })

  it('should accept boolean rounded prop', () => {
    const wrapper = mount(BaseCard, {
      props: { rounded: true },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('rounded')).toBe(true)
  })
})
```

### 1.2 Slot Testing

```typescript
describe('BaseCard Slots', () => {
  it('should render default slot content', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] },
      slots: {
        default: '<div class="test-content">Test Content</div>'
      }
    })

    expect(wrapper.find('.test-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Content')
  })

  it('should render complex slot content', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] },
      slots: {
        default: `
          <v-card-title>Title</v-card-title>
          <v-card-text>Content</v-card-text>
          <v-card-actions>Actions</v-card-actions>
        `
      }
    })

    expect(wrapper.text()).toContain('Title')
    expect(wrapper.text()).toContain('Content')
    expect(wrapper.text()).toContain('Actions')
  })
})
```

### 1.3 Class Binding Testing

```typescript
describe('BaseCard Class Binding', () => {
  it('should apply custom classes', () => {
    const wrapper = mount(BaseCard, {
      props: { class: 'mb-4 pa-6' },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.classes()).toContain('mb-4')
    expect(vCard.classes()).toContain('pa-6')
  })

  it('should handle multiple class formats', () => {
    const wrapper = mount(BaseCard, {
      props: { class: ['mb-4', 'pa-6'] },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.classes()).toContain('mb-4')
    expect(vCard.classes()).toContain('pa-6')
  })
})
```

### 1.4 Attribute Inheritance Testing

```typescript
describe('BaseCard Attribute Inheritance', () => {
  it('should inherit v-bind attributes', () => {
    const wrapper = mount(BaseCard, {
      attrs: {
        'data-test': 'custom-card',
        'aria-label': 'Test Card'
      },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.attributes('data-test')).toBe('custom-card')
    expect(vCard.attributes('aria-label')).toBe('Test Card')
  })
})
```

## 2. Snapshot Tests

### 2.1 Default Rendering

```typescript
describe('BaseCard Snapshots', () => {
  it('should match snapshot with default props', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] },
      slots: { default: '<v-card-text>Content</v-card-text>' }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })

  it('should match snapshot with custom elevation', () => {
    const wrapper = mount(BaseCard, {
      props: { elevation: 8 },
      global: { plugins: [vuetify] },
      slots: { default: '<v-card-text>Content</v-card-text>' }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })

  it('should match snapshot with custom rounded', () => {
    const wrapper = mount(BaseCard, {
      props: { rounded: 'xl' },
      global: { plugins: [vuetify] },
      slots: { default: '<v-card-text>Content</v-card-text>' }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })
})
```

## 3. Integration Tests

### 3.1 Usage in Views

```typescript
// Test BaseCard integration in DashboardView
describe('DashboardView BaseCard Integration', () => {
  it('should render all BaseCard components', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [vuetify, pinia],
        stubs: ['router-link']
      }
    })

    const baseCards = wrapper.findAllComponents(BaseCard)
    expect(baseCards.length).toBeGreaterThan(0)
  })

  it('should apply correct classes to stat cards', () => {
    const wrapper = mount(DashboardView, {
      global: { plugins: [vuetify, pinia] }
    })

    const statCards = wrapper.findAllComponents(BaseCard)
      .filter(w => w.classes().includes('pa-4'))

    expect(statCards.length).toBe(4) // 4 stat cards
  })
})
```

### 3.2 Theme Compatibility

```typescript
describe('BaseCard Theme Compatibility', () => {
  it('should render correctly in light theme', () => {
    const wrapper = mount(BaseCard, {
      global: {
        plugins: [vuetify],
        provide: { theme: 'light' }
      },
      slots: { default: '<v-card-text>Content</v-card-text>' }
    })

    expect(wrapper.exists()).toBe(true)
    // Additional theme-specific assertions
  })

  it('should render correctly in dark theme', () => {
    const wrapper = mount(BaseCard, {
      global: {
        plugins: [vuetify],
        provide: { theme: 'dark' }
      },
      slots: { default: '<v-card-text>Content</v-card-text>' }
    })

    expect(wrapper.exists()).toBe(true)
    // Additional theme-specific assertions
  })
})
```

## 4. Visual Regression Tests (Playwright)

### 4.1 Desktop Visual Tests

```typescript
// tests/e2e/visual/base-card.spec.ts
import { test, expect } from '@playwright/test'

test.describe('BaseCard Visual Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard')
  })

  test('should render cards with correct elevation in light theme', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('theme', 'light')
    })
    await page.reload()

    const card = page.locator('.v-card').first()
    await expect(card).toHaveScreenshot('basecard-light-elevation.png')
  })

  test('should render cards with correct elevation in dark theme', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('theme', 'dark')
    })
    await page.reload()

    const card = page.locator('.v-card').first()
    await expect(card).toHaveScreenshot('basecard-dark-elevation.png')
  })

  test('should render consistently across different pages', async ({ page }) => {
    // Dashboard
    await page.goto('/dashboard')
    await expect(page.locator('.v-card').first()).toHaveScreenshot('dashboard-card.png')

    // Generator
    await page.goto('/generator')
    await expect(page.locator('.v-card').first()).toHaveScreenshot('generator-card.png')
  })
})
```

### 4.2 Responsive Visual Tests

```typescript
test.describe('BaseCard Responsive Tests', () => {
  test('should render correctly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/dashboard')

    await expect(page).toHaveScreenshot('basecard-mobile.png', {
      fullPage: true
    })
  })

  test('should render correctly on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('/dashboard')

    await expect(page).toHaveScreenshot('basecard-tablet.png', {
      fullPage: true
    })
  })
})
```

## 5. Accessibility Tests

### 5.1 Semantic HTML

```typescript
describe('BaseCard Accessibility', () => {
  it('should render semantic HTML structure', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] },
      slots: {
        default: `
          <v-card-title>Title</v-card-title>
          <v-card-text>Content</v-card-text>
        `
      }
    })

    // Vuetify v-card renders as <div> by default
    expect(wrapper.element.tagName).toBe('DIV')
    expect(wrapper.classes()).toContain('v-card')
  })

  it('should support ARIA attributes', () => {
    const wrapper = mount(BaseCard, {
      attrs: {
        'aria-label': 'Statistics Card',
        'role': 'region'
      },
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.attributes('aria-label')).toBe('Statistics Card')
    expect(vCard.attributes('role')).toBe('region')
  })
})
```

### 5.2 Keyboard Navigation

```typescript
test.describe('BaseCard Keyboard Accessibility', () => {
  test('should be accessible via keyboard navigation', async ({ page }) => {
    await page.goto('/dashboard')

    // Tab through cards
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')

    // Verify focus is visible
    const focused = page.locator(':focus')
    await expect(focused).toBeVisible()
  })
})
```

## 6. Performance Tests

### 6.1 Rendering Performance

```typescript
describe('BaseCard Performance', () => {
  it('should render quickly', () => {
    const start = performance.now()

    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] },
      slots: { default: '<v-card-text>Content</v-card-text>' }
    })

    const end = performance.now()
    const renderTime = end - start

    expect(renderTime).toBeLessThan(50) // Should render in less than 50ms
  })

  it('should handle multiple instances efficiently', () => {
    const start = performance.now()

    for (let i = 0; i < 100; i++) {
      mount(BaseCard, {
        global: { plugins: [vuetify] },
        slots: { default: '<v-card-text>Content</v-card-text>' }
      })
    }

    const end = performance.now()
    const totalTime = end - start

    expect(totalTime).toBeLessThan(1000) // 100 renders in less than 1 second
  })
})
```

## 7. Edge Cases

### 7.1 Empty Content

```typescript
describe('BaseCard Edge Cases', () => {
  it('should render without content', () => {
    const wrapper = mount(BaseCard, {
      global: { plugins: [vuetify] }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.html()).toContain('v-card')
  })

  it('should handle null/undefined props gracefully', () => {
    const wrapper = mount(BaseCard, {
      props: {
        elevation: undefined,
        rounded: null
      },
      global: { plugins: [vuetify] }
    })

    // Should use defaults
    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('elevation')).toBe(2)
    expect(vCard.props('rounded')).toBe('lg')
  })
})
```

### 7.2 Extreme Values

```typescript
describe('BaseCard Extreme Values', () => {
  it('should handle maximum elevation', () => {
    const wrapper = mount(BaseCard, {
      props: { elevation: 24 }, // Vuetify max
      global: { plugins: [vuetify] }
    })

    const vCard = wrapper.findComponent({ name: 'VCard' })
    expect(vCard.props('elevation')).toBe(24)
  })

  it('should handle very long class names', () => {
    const longClass = 'mb-4 pa-6 ma-2 elevation-2 rounded-lg text-center d-flex align-center justify-center'
    const wrapper = mount(BaseCard, {
      props: { class: longClass },
      global: { plugins: [vuetify] }
    })

    expect(wrapper.exists()).toBe(true)
  })
})
```

## 8. Test Execution Plan

### Phase 1: Setup (Week 1)
- [ ] Install Vitest and dependencies
- [ ] Configure Vitest with Vuetify
- [ ] Set up test utilities and helpers
- [ ] Create test file structure

### Phase 2: Unit Tests (Week 2)
- [ ] Write prop tests
- [ ] Write slot tests
- [ ] Write class binding tests
- [ ] Write attribute inheritance tests
- [ ] Achieve 100% code coverage

### Phase 3: Integration Tests (Week 3)
- [ ] Test integration in DashboardView
- [ ] Test integration in GeneratorView
- [ ] Test integration in BrowseTreeTab
- [ ] Test theme compatibility

### Phase 4: Visual & E2E Tests (Week 4)
- [ ] Set up Playwright
- [ ] Write visual regression tests
- [ ] Write responsive tests
- [ ] Write accessibility tests

### Phase 5: CI/CD Integration (Week 5)
- [ ] Add tests to CI pipeline
- [ ] Set up coverage reporting
- [ ] Configure visual regression service
- [ ] Document test process

## 9. Success Criteria

✅ **Unit Tests**
- 100% code coverage
- All prop variations tested
- All edge cases covered

✅ **Integration Tests**
- All view integrations tested
- Theme compatibility verified
- No regressions in existing functionality

✅ **Visual Tests**
- Snapshot tests for all variations
- E2E tests for all breakpoints
- Visual regression tests pass

✅ **Accessibility Tests**
- WCAG AA compliance
- Keyboard navigation works
- Screen reader compatible

✅ **Performance**
- Render time < 50ms
- No memory leaks
- Bundle size impact minimal

## 10. Maintenance

### Regular Tasks
- Update tests when component changes
- Update snapshots when visual changes are intentional
- Review and update test coverage quarterly
- Keep testing dependencies up to date

### When to Update Tests
- Adding new props
- Changing default values
- Modifying component behavior
- Refactoring component structure

---

**Test Owner:** Frontend Team
**Created:** 2025-10-26
**Status:** Ready for implementation
**Priority:** P1 (High - foundational component)

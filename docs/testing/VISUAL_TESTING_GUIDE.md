# Visual Testing Guide for Frontend Changes

**Version:** 1.0
**Date:** 2025-10-26
**Applies to:** Vue.js Frontend (frontend-vue/)

## Purpose

This guide provides standards and procedures for testing visual changes in the frontend to ensure consistency, prevent regressions, and maintain design system compliance.

## When Visual Testing is Required

Visual testing is **required** for:

✅ **UI Component Changes**
- New components
- Modified component styling
- Component refactoring (like BaseCard)
- Theme-related changes

✅ **Layout Changes**
- Page layout modifications
- Responsive design updates
- Grid/flex changes

✅ **Color/Theme Changes**
- Dark/light theme modifications
- Color palette updates
- Contrast adjustments

✅ **Typography Changes**
- Font size/weight modifications
- Line height adjustments
- Text styling changes

## Manual Visual Testing Checklist

### 1. Desktop Testing

Test in the following browsers:

- [ ] **Chrome** (latest version)
- [ ] **Firefox** (latest version)
- [ ] **Safari** (latest version, macOS only)
- [ ] **Edge** (latest version)

**Screen Resolutions:**
- [ ] 1920x1080 (Full HD)
- [ ] 1366x768 (Common laptop)
- [ ] 2560x1440 (2K)

### 2. Mobile Testing

Test responsive behavior:

- [ ] **Mobile Portrait** (375x667 - iPhone SE)
- [ ] **Mobile Landscape** (667x375)
- [ ] **Tablet Portrait** (768x1024 - iPad)
- [ ] **Tablet Landscape** (1024x768)

### 3. Theme Testing

Test both theme modes:

- [ ] **Light Theme**
  - All colors render correctly
  - Text contrast meets WCAG AA standards
  - Shadows/elevations visible

- [ ] **Dark Theme**
  - Background colors appropriate
  - Text readable (sufficient contrast)
  - No "light leak" (unwanted light colors)
  - Cards/surfaces distinguishable from background

### 4. Component-Specific Tests

For card components (like BaseCard):

- [ ] **Elevation (Shadow)**
  - Shadow visible but not overwhelming
  - Shadow depth appropriate for hierarchy
  - Shadow color matches theme

- [ ] **Border Radius**
  - Corners rounded consistently
  - Matches design system (lg = 12px)
  - No visual artifacts

- [ ] **Spacing**
  - Padding/margin consistent
  - Responsive spacing works
  - No content overflow

- [ ] **Interactive States**
  - Hover effects (if applicable)
  - Focus states visible
  - Active/pressed states appropriate

### 5. Cross-Page Consistency

Verify consistency across pages:

- [ ] Dashboard page
- [ ] Generator page
- [ ] Profile pages (when implemented)
- [ ] Settings pages (when implemented)

## Screenshot Documentation

### When to Take Screenshots

Take before/after screenshots for:
1. Bug fixes affecting visual appearance
2. New component implementations
3. Design system changes
4. Theme modifications

### Screenshot Requirements

**Format:** PNG (lossless)
**Naming Convention:** `{page}_{component}_{theme}_{state}.png`

**Examples:**
- `dashboard_stats_cards_dark_default.png`
- `generator_coverage_card_light_default.png`
- `browse_tree_dialog_dark_hover.png`

### Storage Location

```
docs/screenshots/
├── before/
│   ├── {date}_{issue_number}/
│   └── ...
└── after/
    ├── {date}_{issue_number}/
    └── ...
```

**Example for BUG-08:**
```
docs/screenshots/
├── before/
│   └── 2025-10-26_BUG-08/
│       ├── generator_stats_card_dark.png
│       └── generator_stats_card_light.png
└── after/
    └── 2025-10-26_BUG-08/
        ├── generator_stats_card_dark_fixed.png
        └── generator_stats_card_light_fixed.png
```

## Automated Visual Testing (Future)

### Recommended Tools

When test infrastructure is ready:

1. **Vitest + @vue/test-utils**
   - Component unit tests
   - Snapshot testing

2. **Playwright** or **Cypress**
   - E2E visual regression tests
   - Cross-browser testing

3. **Percy** or **Chromatic**
   - Cloud-based visual regression
   - Automated screenshot comparison
   - Pull request integration

### Example Vitest Snapshot Test

```typescript
// src/components/common/__tests__/BaseCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseCard from '../BaseCard.vue'

describe('BaseCard', () => {
  it('renders with default props', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        default: '<div>Test Content</div>'
      }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })

  it('renders with custom elevation', () => {
    const wrapper = mount(BaseCard, {
      props: { elevation: 4 },
      slots: { default: '<div>Test</div>' }
    })

    expect(wrapper.html()).toMatchSnapshot()
  })
})
```

### Example Playwright Visual Test

```typescript
// tests/e2e/visual/dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Dashboard Visual Tests', () => {
  test('dashboard cards render correctly in dark theme', async ({ page }) => {
    await page.goto('/dashboard')

    // Set dark theme
    await page.evaluate(() => {
      localStorage.setItem('theme', 'dark')
    })
    await page.reload()

    // Take screenshot
    await expect(page).toHaveScreenshot('dashboard-dark.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })
})
```

## Verification Process

### Before Committing

1. [ ] Run build: `npm run build`
2. [ ] Check TypeScript: `vue-tsc -b`
3. [ ] Test locally in dev mode: `npm run dev`
4. [ ] Manual visual testing (checklist above)
5. [ ] Take screenshots (if applicable)
6. [ ] Document changes in commit message

### Before Merging

1. [ ] Code review completed
2. [ ] Visual changes reviewed (screenshots)
3. [ ] Theme compatibility verified
4. [ ] Responsive behavior tested
5. [ ] Browser compatibility checked
6. [ ] No console errors/warnings

## Common Visual Issues

### Issue: Cards Not Visible in Dark Theme

**Symptom:** Cards blend into background
**Cause:** Using `surface-variant` or wrong surface color
**Solution:** Use default surface color or BaseCard component

```vue
<!-- Bad -->
<v-card color="surface-variant">...</v-card>

<!-- Good -->
<BaseCard>...</BaseCard>
```

### Issue: Inconsistent Elevation

**Symptom:** Cards have different shadow depths
**Cause:** Hardcoded elevation values
**Solution:** Use BaseCard with consistent defaults

```vue
<!-- Bad -->
<v-card elevation="1">...</v-card>
<v-card elevation="3">...</v-card>

<!-- Good -->
<BaseCard>...</BaseCard> <!-- Always elevation="2" -->
```

### Issue: Rounded Corners Inconsistent

**Symptom:** Some cards more rounded than others
**Cause:** Mixed `rounded` values
**Solution:** Use BaseCard for consistency

```vue
<!-- Bad -->
<v-card rounded>...</v-card>
<v-card rounded="lg">...</v-card>
<v-card rounded="xl">...</v-card>

<!-- Good -->
<BaseCard>...</BaseCard> <!-- Always rounded="lg" -->
```

## Design System Reference

### Card Styling Standards

| Property | Value | Reason |
|----------|-------|--------|
| Elevation | `2` | Subtle depth without overwhelming |
| Rounded | `lg` (12px) | Modern, friendly appearance |
| Background | `surface` | Theme-aware, adapts to dark/light |

### Color Contrast Requirements

**WCAG AA Standards:**
- Normal text: 4.5:1 minimum contrast ratio
- Large text: 3:1 minimum contrast ratio
- UI components: 3:1 minimum contrast ratio

**Tools for Testing:**
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools: Lighthouse accessibility audit
- Firefox DevTools: Accessibility inspector

## Accessibility Testing

Visual testing should include accessibility checks:

- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast sufficient
- [ ] Screen reader friendly (semantic HTML)
- [ ] ARIA labels present where needed

## Documentation Requirements

For visual changes, document:

1. **What Changed**
   - Component/page affected
   - Visual differences

2. **Why Changed**
   - Bug fix, enhancement, refactoring
   - Design system compliance

3. **Testing Done**
   - Browsers tested
   - Themes tested
   - Responsive breakpoints tested

4. **Screenshots**
   - Before/after images
   - Different themes
   - Different screen sizes

## Example: BUG-08 Visual Testing

### Issue
Profile Generator page cards had light gray background in dark theme

### Testing Performed

**Manual Testing:**
- ✅ Chrome 120 (1920x1080)
- ✅ Firefox 121 (1920x1080)
- ✅ Mobile responsive (375x667)
- ✅ Dark theme tested
- ✅ Light theme tested

**Components Tested:**
- ✅ Coverage stats card
- ✅ Loading state card
- ✅ Tabs card
- ✅ Bulk progress dialog

**Verification:**
- ✅ Cards visible in dark theme
- ✅ Elevation consistent
- ✅ Rounded corners consistent
- ✅ No color bleeding
- ✅ Matches Dashboard design

### Result
All visual tests passed. Design consistency achieved.

## Future Enhancements

### Short Term
- [ ] Set up Vitest for component tests
- [ ] Add snapshot tests for components
- [ ] Create screenshot comparison workflow

### Medium Term
- [ ] Integrate Playwright for E2E tests
- [ ] Set up Percy or Chromatic for automated visual regression
- [ ] Add visual testing to CI/CD pipeline

### Long Term
- [ ] Automated visual regression on every PR
- [ ] Cross-browser automated testing
- [ ] Visual testing dashboard

## Resources

- [Vuetify Design System](https://vuetifyjs.com/en/styles/colors/)
- [Material Design Guidelines](https://material.io/design)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [Vitest Snapshot Testing](https://vitest.dev/guide/snapshot.html)

---

**Maintained by:** Frontend Team
**Last Updated:** 2025-10-26
**Next Review:** When Vitest is integrated

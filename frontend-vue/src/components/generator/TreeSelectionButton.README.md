# TreeSelectionButton Component

## Overview

Reusable button component for organization tree selection actions. Supports responsive design with three breakpoints (Desktop/Tablet/Mobile) and two selection modes (Direct/All).

## Purpose

Eliminates code duplication from OrganizationTree component where 6 nearly identical button+tooltip blocks were repeated. Now a single component handles all variations.

## Features

- **Responsive Design**: Automatically adapts to 3 breakpoints
  - Desktop (≥960px): Shows icon + full text
  - Tablet (600-959px): Shows text only
  - Mobile (<600px): Shows compact text
- **Two Selection Modes**:
  - `direct`: Select only positions directly under a node
  - `all`: Select all positions including nested children (recursive)
- **Accessibility**: Includes tooltips and ARIA labels
- **Type Safety**: Full TypeScript support
- **i18n Ready**: All strings extracted to constants

## Usage

```vue
<template>
  <TreeSelectionButton
    mode="direct"
    breakpoint="desktop"
    :count="5"
    @click="handleClick"
  />
</template>

<script setup lang="ts">
import TreeSelectionButton from './TreeSelectionButton.vue'

function handleClick() {
  console.log('Button clicked!')
}
</script>
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `mode` | `'direct' \| 'all'` | Yes | Selection mode: 'direct' for direct positions only, 'all' for recursive selection |
| `breakpoint` | `'desktop' \| 'tablet' \| 'mobile'` | Yes | Responsive breakpoint determining button appearance |
| `count` | `number` | Yes | Number of positions that will be selected when button is clicked |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `click` | `void` | Emitted when button is clicked (use with `.stop` modifier to prevent event bubbling) |

## Examples

### Desktop - Direct Positions
```vue
<TreeSelectionButton
  mode="direct"
  breakpoint="desktop"
  :count="5"
  @click="selectDirectPositions(node)"
/>
```
Renders: `[📄 Direct (5)]`

### Tablet - All Nested
```vue
<TreeSelectionButton
  mode="all"
  breakpoint="tablet"
  :count="25"
  @click="selectAllNestedPositions(node)"
/>
```
Renders: `[All (25)]`

### Mobile - Direct Positions
```vue
<TreeSelectionButton
  mode="direct"
  breakpoint="mobile"
  :count="3"
  @click="selectDirectPositions(node)"
/>
```
Renders: `[Dir: 3]`

## Integration with OrganizationTree

```vue
<template>
  <!-- Direct positions buttons (3 breakpoints) -->
  <template v-if="item.positions && item.positions.length > 0">
    <TreeSelectionButton
      v-for="breakpoint in ['desktop', 'tablet', 'mobile']"
      :key="`direct-${breakpoint}`"
      mode="direct"
      :breakpoint="breakpoint"
      :count="item.positions.length"
      @click="selectDirectPositions(item)"
    />
  </template>

  <!-- All nested positions buttons (3 breakpoints) -->
  <template v-if="item.total_positions && item.total_positions > 0">
    <TreeSelectionButton
      v-for="breakpoint in ['desktop', 'tablet', 'mobile']"
      :key="`all-${breakpoint}`"
      mode="all"
      :breakpoint="breakpoint"
      :count="item.total_positions"
      @click="selectAllNestedPositions(item)"
    />
  </template>
</template>
```

## Styling

Button appearance is controlled by Vuetify and breakpoint classes:
- **Variant**: `outlined` (consistent visual weight for both modes)
- **Color**: `grey-darken-1`
- **Size**: `x-small`

Responsive visibility handled via Vuetify display classes:
- Desktop: `.d-none .d-lg-inline-flex`
- Tablet: `.d-none .d-sm-inline-flex .d-lg-none`
- Mobile: `.d-inline-flex .d-sm-none`

## Constants Used

All text and configuration imported from `@/constants/treeSelection`:
- `BUTTON_CONFIG`: Button styling configuration
- `getButtonText()`: Get text based on mode and breakpoint
- `getTooltipText()`: Get tooltip text based on mode
- `getIconName()`: Get Material Design icon name
- `getBreakpointClass()`: Get Vuetify display class

## Accessibility

- **Tooltips**: Explains what the button does
- **ARIA Labels**: Descriptive labels for screen readers
  - Example: "Select only positions directly under this unit (5 positions)"
- **Click Event**: Use with `.stop` modifier to prevent event bubbling

## Type Safety

Component is fully typed with TypeScript:
```typescript
interface Props {
  mode: SelectionMode // 'direct' | 'all'
  breakpoint: Breakpoint // 'desktop' | 'tablet' | 'mobile'
  count: number
}
```

## i18n Preparation

All user-facing strings are extracted to `@/constants/treeSelection` for easy translation:
- Button labels: "Direct", "All", "Dir:", "All:"
- Tooltips: Descriptive text for each mode

When implementing i18n:
1. Move strings from constants to `locales/en.json`
2. Replace constant references with `$t()` calls
3. Add translations to other locale files

## Testing

Unit tests available in `tests/components/OrganizationTree.spec.ts`:
- Component integration tests
- Prop validation tests
- Event emission tests
- Responsive behavior tests

## Files

- **Component**: `src/components/generator/TreeSelectionButton.vue`
- **Constants**: `src/constants/treeSelection.ts`
- **Tests**: `tests/components/OrganizationTree.spec.ts`
- **Usage**: `src/components/generator/OrganizationTree.vue`

## Benefits

1. **DRY Principle**: Eliminates 100+ lines of repetitive code
2. **Maintainability**: Single source of truth for button behavior
3. **Consistency**: Ensures all buttons look and behave identically
4. **Type Safety**: Full TypeScript support prevents errors
5. **Scalability**: Easy to add new breakpoints or modes
6. **i18n Ready**: Prepared for multilingual support

## Related

- **Parent Component**: [OrganizationTree.vue](./OrganizationTree.vue)
- **Constants**: [treeSelection.ts](../../constants/treeSelection.ts)
- **Tests**: [OrganizationTree.spec.ts](../../../tests/components/OrganizationTree.spec.ts)

---

**Created**: 2025-10-26
**Part of**: UX-11 Implementation (Dual selection buttons)
**Code Review**: Approved ✅

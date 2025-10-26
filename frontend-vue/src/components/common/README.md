# Common Components

This directory contains reusable UI components used throughout the application.

## BaseCard

A reusable card component that provides consistent styling across the application. It wraps Vuetify's `v-card` with default elevation and rounded properties.

### Purpose

- **Consistency**: Ensures all cards follow the same visual design pattern
- **Maintainability**: Centralizes card styling configuration in one place
- **DRY Principle**: Eliminates repeated `elevation="2" rounded="lg"` attributes

### Usage

#### Basic Usage

```vue
<template>
  <BaseCard class="mb-4">
    <v-card-text>
      Your content here
    </v-card-text>
  </BaseCard>
</template>

<script setup lang="ts">
import BaseCard from '@/components/common/BaseCard.vue'
</script>
```

#### With Custom Elevation

```vue
<BaseCard :elevation="4">
  <v-card-title>Higher elevation card</v-card-title>
</BaseCard>
```

#### With Different Rounding

```vue
<BaseCard rounded="xl">
  <v-card-text>Extra large rounded corners</v-card-text>
</BaseCard>
```

#### With Additional Classes

```vue
<BaseCard class="pa-4 mb-6">
  <v-card-title>Padded card with margin</v-card-title>
</BaseCard>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `elevation` | `string \| number` | `2` | Card shadow depth (0-24) |
| `rounded` | `string \| boolean` | `"lg"` | Border radius (sm, md, lg, xl, or boolean) |
| `class` | `string` | - | Additional CSS classes |

### Design System

The default values (`elevation="2"` and `rounded="lg"`) match the application's design system:

- **Elevation 2**: Subtle shadow that creates visual hierarchy without being overwhelming
- **Rounded "lg"**: Large border radius (12px) for a modern, friendly appearance

### When NOT to Use BaseCard

**Use regular `v-card` when you need:**

1. **Special Colors**: Cards with semantic colors (e.g., `color="info"`, `color="error"`)
   ```vue
   <!-- Use v-card for colored cards -->
   <v-card color="info">
     <v-card-text>Information message</v-card-text>
   </v-card>
   ```

2. **Flat Cards**: Nested cards that should have no elevation
   ```vue
   <!-- Use v-card flat for nested cards -->
   <v-card flat>
     <v-card-text>Nested content</v-card-text>
   </v-card>
   ```

3. **Custom Styling**: Cards requiring unique elevation or rounded values different from defaults

### Migration from v-card

**Before:**
```vue
<v-card elevation="2" rounded="lg" class="mb-4">
  <v-card-text>Content</v-card-text>
</v-card>
```

**After:**
```vue
<BaseCard class="mb-4">
  <v-card-text>Content</v-card-text>
</BaseCard>
```

### Files Using BaseCard

- `src/views/DashboardView.vue` - All stat cards and content cards
- `src/views/GeneratorView.vue` - Coverage stats, loading state, and tabs card
- `src/components/generator/BrowseTreeTab.vue` - Bulk progress dialog

### Implementation Details

The component uses:
- Vue 3 Composition API with `<script setup>`
- TypeScript for type safety
- `v-bind="$attrs"` for attribute inheritance
- Computed property for class merging

### Testing

**Visual Testing:**
1. Verify cards render with consistent elevation and rounded corners
2. Check dark theme compatibility
3. Ensure no visual regressions across different screen sizes

**Future Enhancement:**
- Add Vitest component tests when testing infrastructure is set up
- Consider snapshot tests for visual regression detection

### Related Documentation

- [Vuetify Card API](https://vuetifyjs.com/en/components/cards/)
- [Design System Guidelines](../../../docs/ux-design/COMPLETE_UX_ANALYSIS.md)

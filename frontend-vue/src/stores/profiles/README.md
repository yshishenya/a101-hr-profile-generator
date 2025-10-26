# Profiles Store - Modular Architecture

## Overview

The profiles store has been refactored from a monolithic 835-line file into a modular architecture with clear separation of concerns. This improves maintainability, testability, and developer experience.

## Architecture

```
profiles/
├── index.ts              # Store entry point & composition
├── types.ts              # Local types & error classes
├── state.ts              # Reactive state definitions
├── getters.ts            # Computed properties
├── actions-crud.ts       # CRUD operations
├── actions-filters.ts    # Filter & pagination logic
└── actions-unified.ts    # Unified view operations
```

## Module Responsibilities

### `types.ts` (30 lines)
- `ProfileError` class for structured error handling
- Constants: `DEFAULT_PAGE_SIZE`, `DEFAULT_PAGE`
- Local helper types

### `state.ts` (72 lines)
All reactive state definitions:
- `unifiedPositions` - Combined catalog + profile + task data
- `profiles` - Legacy profile list
- `currentProfile` - Currently loaded profile detail
- `loading`, `error` - Operation status
- `viewMode` - UI view mode (table/cards)
- `filters`, `unifiedFilters` - Filter state
- `pagination` - Pagination metadata

### `getters.ts` (108 lines)
Computed properties organized by purpose:
- **Legacy getters**: `totalProfiles`, `currentPage`, `hasMore`, etc.
- **Unified getters**: `filteredPositions`, `statistics`, `departments`
- All getters are pure functions of state

### `actions-crud.ts` (290 lines)
Profile CRUD operations:
- `loadProfiles()` - Fetch profiles with pagination/filters
- `loadProfile(id)` - Fetch single profile detail
- `updateProfile(id, data)` - Update profile metadata/content
- `deleteProfile(id)` - Archive profile (soft delete)
- `downloadProfile(id, format)` - Download in JSON/MD/DOCX
- Helper actions: `clearError()`, `clearCurrentProfile()`

### `actions-filters.ts` (82 lines)
Filter and pagination management:
- `setFilters(filters)` - Apply filters and reload
- `clearFilters()` - Reset all filters
- `goToPage(page)` - Navigate to specific page
- `nextPage()`, `previousPage()` - Page navigation

### `actions-unified.ts` (244 lines)
Unified view operations:
- `loadUnifiedData()` - Main method to combine all data sources
- `determinePositionStatus()` - Calculate position status
- `computeActions()` - Determine available actions per status
- `bulkGenerate(ids)` - Start bulk profile generation
- `bulkCancel(ids)` - Cancel bulk generation tasks

### `index.ts` (158 lines)
Store composition and export:
- Imports all modules
- Defines `reset()` function
- Returns complete store API
- Maintains backward compatibility

## Usage

### Import the Store
```typescript
import { useProfilesStore } from '@/stores/profiles'

const profilesStore = useProfilesStore()
```

### Import Error Class
```typescript
import { ProfileError } from '@/stores/profiles'

try {
  await profilesStore.loadProfile(id)
} catch (err) {
  if (err instanceof ProfileError) {
    console.error(`Error [${err.code}]:`, err.message)
  }
}
```

### Example: Load and Filter Profiles
```typescript
const store = useProfilesStore()

// Load first page
await store.loadProfiles()

// Apply filters
await store.setFilters({
  department: 'IT',
  status: 'completed'
})

// Navigate pages
await store.nextPage()
```

### Example: Unified View
```typescript
const store = useProfilesStore()

// Load all positions with status
await store.loadUnifiedData()

// Access filtered positions
console.log(store.filteredPositions)

// Check statistics
console.log(store.statistics.coverage_percentage)

// Bulk generate profiles
const selectedIds = ['pos_1', 'pos_2']
const taskIds = await store.bulkGenerate(selectedIds)
```

## Benefits of Modular Architecture

### 1. **Better Organization**
- Each file has single, clear responsibility
- Easy to locate specific functionality
- Reduced cognitive load when reading code

### 2. **Easier Testing**
- Can import and test individual modules
- Mock dependencies more easily
- Focused unit tests per module

### 3. **Improved Maintainability**
- Changes isolated to relevant module
- Less risk of unintended side effects
- Clear module boundaries

### 4. **Better Collaboration**
- Multiple developers can work on different modules
- Reduced merge conflicts
- Clear ownership of functionality

### 5. **Enhanced Documentation**
- Each module has focused JSDoc
- README explains architecture
- Easier to onboard new developers

## Backward Compatibility

The legacy entry point (`/home/yan/A101/HR/frontend-vue/src/stores/profiles.ts`) re-exports everything:

```typescript
export { useProfilesStore } from './profiles/index'
export { ProfileError } from './profiles/types'
```

All existing imports continue to work without changes:
```typescript
import { useProfilesStore } from '@/stores/profiles'  // ✓ Works
```

## Migration Notes

No migration required! The refactoring maintains 100% API compatibility:
- All state variables available
- All computed properties available
- All actions available
- Same function signatures
- Same return types

## Development Guidelines

### Adding New State
1. Add to `state.ts`
2. Export from module
3. Import in `index.ts`
4. Add to return statement

### Adding New Getters
1. Add to `getters.ts`
2. Export from module
3. Import in `index.ts`
4. Add to return statement

### Adding New Actions
1. Determine which module (crud/filters/unified)
2. Add function to appropriate module
3. Export from module
4. Import in `index.ts`
5. Add to return statement

### Creating New Module
If a module grows too large (>300 lines), split it:
1. Create new file in `profiles/`
2. Move related functionality
3. Update imports in `index.ts`
4. Update this README

## Testing

Run type checking:
```bash
cd frontend-vue
npx vue-tsc --noEmit
```

Run build:
```bash
cd frontend-vue
npm run build
```

## Performance Considerations

- State is reactive but modules are static
- Getters are memoized by Vue's computed()
- No performance impact from modular structure
- Bundle size unchanged (tree-shaking works)

## Future Improvements

1. **Extract Types**: Move to separate `@/types/profiles/` package
2. **Add Unit Tests**: Create `__tests__/` for each module
3. **Error Boundaries**: Enhance ProfileError with recovery strategies
4. **Optimistic Updates**: Add optimistic state mutations
5. **Cache Layer**: Add intelligent caching for repeated queries

## Related Documentation

- [Pinia Store Documentation](https://pinia.vuejs.org/)
- [Vue 3 Composition API](https://vuejs.org/api/composition-api.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Last Updated**: 2025-10-26
**Refactored By**: Claude (TypeScript Expert Agent)
**Original Size**: 835 lines → **Modular Size**: 7 files (984 total lines, max 290 per file)

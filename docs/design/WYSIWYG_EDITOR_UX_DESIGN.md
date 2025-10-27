# WYSIWYG Profile Editor - UX/UI Design

## Концепция: "Единый Документ"

### Философия Дизайна
Редактирование профиля должно ощущаться как работа с **профессиональным документом** (Word, Google Docs), а не как заполнение формы в базе данных.

**Ключевые принципы:**
- 📄 **Document-centric**: Одна страница, естественный скролл
- ✏️ **Inline editing**: Редактирование прямо в контексте
- 🎨 **WYSIWYG**: Что видишь, то и получаешь
- 🧭 **Easy navigation**: Outline слева для быстрой навигации
- 💾 **Forgiving UX**: Auto-save, undo/redo, подтверждение при выходе

---

## Визуальная Структура

```
┌──────────────────────────────────────────────────────────────────────┐
│  [📝 Профиль: Frontend Developer] │ [👁️ Preview] [💾 Save] [✖️ Cancel]  │ ← Sticky Top Bar
├─────────────────┬────────────────────────────────────────────────────┤
│                 │                                                    │
│  OUTLINE        │   DOCUMENT AREA                                    │
│  ───────        │   ════════════                                     │
│                 │                                                    │
│  📌 Позиция     │   # Название позиции                               │
│  🧠 Компетенции │   **Frontend Developer** [editable inline]         │
│  📋 Обязанности │                                                    │
│  🛠️ Навыки      │   ─────────────────────────────────────────────   │
│  🎓 Образование │                                                    │
│  💼 Опыт работы │   ## 🧠 Компетенции                                │
│  📊 Показатели  │                                                    │
│                 │   ### Технические компетенции                      │
│  [Collapse ▲]   │   [💡 Click to edit]                               │
│                 │   • Vue.js, React, TypeScript                      │
│                 │   • HTML5, CSS3, Responsive Design                 │
│                 │   • REST API, GraphQL, WebSockets                  │
│                 │   [+ Add skill]                                    │
│                 │                                                    │
│                 │   ### Управленческие компетенции                   │
│                 │   [TipTap rich text editor area]                   │
│                 │   • Планирование и приоритизация задач             │
│                 │   • Код-ревью и менторство                         │
│                 │                                                    │
│                 │   ─────────────────────────────────────────────   │
│                 │                                                    │
│                 │   ## 📋 Обязанности и зоны ответственности         │
│                 │                                                    │
│                 │   [TipTap editor - rich text formatting]          │
│                 │   Разработка пользовательских интерфейсов...       │
│                 │                                                    │
│                 │   [Formatting toolbar appears on text selection]  │
│                 │                                                    │
│                 │   ─────────────────────────────────────────────   │
│                 │                                                    │
│                 │   ## 🛠️ Профессиональные навыки                    │
│                 │                                                    │
│                 │   ### Hard Skills                                  │
│                 │   [Chip editor with drag handles]                 │
│                 │   [Vue.js ✖️] [TypeScript ✖️] [Vuetify ✖️]          │
│                 │   [☰ Drag to reorder] [+ Add skill]               │
│                 │                                                    │
│                 │   ### Soft Skills                                  │
│                 │   [Communication ✖️] [Teamwork ✖️]                  │
│                 │                                                    │
│                 │   ─────────────────────────────────────────────   │
│                 │                                                    │
│  [Save draft]   │   [Content continues with natural scroll...]      │
│  [Auto-saved •] │                                                    │
│                 │                                                    │
└─────────────────┴────────────────────────────────────────────────────┘
```

---

## Компоненты UI

### 1. Sticky Top Bar
**Расположение:** Всегда видна при скролле
**Содержимое:**
- Название профиля (редактируемое inline)
- Кнопка "Preview" (показать как будет выглядеть в DOCX)
- Кнопка "Save" (с индикатором unsaved changes: 💾 → 💾•)
- Кнопка "Cancel" (с подтверждением при unsaved changes)

**Состояния:**
```typescript
// Unsaved changes indicator
<v-btn color="primary" :variant="hasUnsavedChanges ? 'elevated' : 'tonal'">
  <v-icon>mdi-content-save</v-icon>
  Save
  <v-badge v-if="hasUnsavedChanges" dot color="warning" />
</v-btn>
```

### 2. Left Sidebar - Document Outline
**Назначение:** Навигация по секциям (как в Google Docs)
**Поведение:**
- Секция подсвечивается при скролле (active section)
- Клик → плавный скролл к секции
- Показывает структуру документа
- Collapsible (можно свернуть для больше места)

**Прогресс-индикаторы:**
```
📌 Позиция ✓ (заполнена)
🧠 Компетенции ⚠️ (требует внимания - пустое поле)
📋 Обязанности ✓
🛠️ Навыки ⏳ (редактируется сейчас)
```

### 3. Document Area - Main Content
**Принцип:** Непрерывный поток контента, как в документе

#### 3.1 Section Headers
```vue
<div class="section-header" @click="scrollToSection('competencies')">
  <v-icon>mdi-brain</v-icon>
  <h2>Компетенции</h2>
  <v-chip v-if="isSectionValid('competencies')" size="small" color="success">
    <v-icon>mdi-check</v-icon>
  </v-chip>
</div>
```

#### 3.2 Editable Sections - Типы

**A) Rich Text Sections** (Обязанности, Описания)
- **Technology:** TipTap WYSIWYG editor
- **Trigger:** Click в текстовую область
- **Toolbar:** Floating toolbar появляется при выделении текста
- **Features:**
  - Bold, Italic, Underline
  - Bullet lists, Numbered lists
  - Headings (H3, H4)
  - Undo/Redo

```vue
<!-- Rich Text Section -->
<div class="editable-section" :class="{ 'is-editing': isEditing }">
  <div v-if="!isEditing" @click="startEditing" class="preview-content">
    <div v-html="sanitizedContent"></div>
    <div class="edit-hint">💡 Click to edit</div>
  </div>
  <TipTapEditor
    v-else
    v-model="content"
    @blur="saveContent"
    :placeholder="'Введите обязанности...'"
  />
</div>
```

**B) List Sections** (Навыки, Качества, Компетенции)
- **Technology:** Vuetify chips + vue-draggable-next
- **Trigger:** Hover → показать [+ Add], [✖️ Remove]
- **Features:**
  - Drag & drop для переупорядочивания
  - Add/Remove items
  - Quick edit on double-click

```vue
<!-- List Section with Chips -->
<div class="chip-list-section">
  <Draggable v-model="skills" item-key="id" handle=".drag-handle">
    <template #item="{ element }">
      <v-chip
        closable
        @click:close="removeSkill(element.id)"
        class="ma-1"
      >
        <v-icon class="drag-handle">mdi-drag-vertical</v-icon>
        {{ element.name }}
      </v-chip>
    </template>
  </Draggable>

  <v-text-field
    v-model="newSkill"
    @keyup.enter="addSkill"
    placeholder="+ Add skill..."
    variant="plain"
    density="compact"
  />
</div>
```

**C) Table Sections** (Опыт работы, Образование)
- **Technology:** Vuetify v-data-table с inline editing
- **Trigger:** Double-click на ячейку
- **Features:**
  - Inline cell editing
  - Add/Remove rows
  - Column sorting

```vue
<!-- Editable Table Section -->
<v-data-table
  :headers="experienceHeaders"
  :items="experienceItems"
  @dblclick:row="editRow"
>
  <template #item.years="{ item }">
    <v-text-field
      v-if="editingRow === item.id"
      v-model="item.years"
      density="compact"
      variant="plain"
    />
    <span v-else>{{ item.years }}</span>
  </template>
</v-data-table>
```

**D) Nested Sections** (Зоны ответственности с подзадачами)
- **Technology:** v-expansion-panels с редактируемым содержимым
- **Trigger:** Expand panel → edit inline
- **Features:**
  - Collapsible subsections
  - Add/Remove subsections
  - Nested item editing

```vue
<!-- Nested Section -->
<v-expansion-panels>
  <v-expansion-panel
    v-for="area in responsibilityAreas"
    :key="area.id"
  >
    <v-expansion-panel-title>
      <v-text-field
        v-model="area.title"
        @click.stop
        variant="plain"
        placeholder="Area title..."
      />
    </v-expansion-panel-title>

    <v-expansion-panel-text>
      <ListEditor v-model="area.tasks" />
      <v-btn @click="addTask(area.id)" size="small">
        + Add task
      </v-btn>
    </v-expansion-panel-text>
  </v-expansion-panel>
</v-expansion-panels>
```

---

## Интерактивность и Feedback

### 1. Hover States
```css
.editable-section {
  position: relative;
  border-radius: 8px;
  padding: 16px;
  transition: background-color 0.2s;
}

.editable-section:hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
  cursor: text;
}

.editable-section:hover .edit-hint {
  opacity: 1;
}

.edit-hint {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  color: var(--v-theme-on-surface-variant);
  font-size: 12px;
}
```

### 2. Focus States
- Активная секция: border color primary
- TipTap editor: показать formatting toolbar
- Chip input: autofocus при клике на [+ Add]

### 3. Validation Feedback
```vue
<!-- Inline validation -->
<div class="section-wrapper" :class="{ 'has-error': hasValidationError }">
  <TextEditor v-model="content" />

  <v-alert
    v-if="validationError"
    type="error"
    density="compact"
    closable
  >
    {{ validationError }}
  </v-alert>
</div>
```

### 4. Auto-save Indicator
```vue
<!-- Bottom-left corner indicator -->
<div class="autosave-status">
  <v-chip
    v-if="isSaving"
    size="small"
    color="info"
  >
    <v-progress-circular indeterminate size="16" class="mr-2" />
    Saving draft...
  </v-chip>

  <v-chip
    v-else-if="lastSaved"
    size="small"
    color="success"
  >
    <v-icon size="16">mdi-check</v-icon>
    Saved {{ formatTimeAgo(lastSaved) }}
  </v-chip>
</div>
```

---

## User Flows

### Flow 1: Редактирование текстовой секции
```
1. User scrolls to "Обязанности" section
2. Section highlights on hover (subtle background)
3. "💡 Click to edit" hint appears
4. User clicks → TipTap editor activates
5. User types/formats text
6. Formatting toolbar appears when text selected
7. User clicks outside OR presses Ctrl+S
8. Content auto-saves (indicator shows "Saving...")
9. Editor stays active (can continue editing)
10. Click on another section OR scroll away → editor deactivates
```

### Flow 2: Добавление навыков (chips)
```
1. User scrolls to "Навыки" section
2. Hovers over chip list → [+ Add skill] appears
3. Clicks [+ Add] OR just starts typing
4. Input field appears/focuses
5. User types skill name
6. Presses Enter → chip added to list
7. Can drag chips to reorder (handles appear on hover)
8. Click [X] on chip → confirmation → remove
9. Auto-save triggers after each change
```

### Flow 3: Быстрая навигация через Outline
```
1. User wants to edit "Образование" section
2. Clicks "🎓 Образование" in left outline
3. Smooth scroll to section (highlighted briefly)
4. Section already in edit mode (or becomes editable)
5. User makes changes
6. Clicks "💼 Опыт работы" in outline
7. Smooth scroll + previous section auto-saves
```

### Flow 4: Сохранение с валидацией
```
1. User clicks "Save" button (top bar)
2. Validation runs on all sections
3a. If errors:
    - Scroll to first error
    - Highlight section with error
    - Show inline error message
    - Save button disabled until fixed
3b. If no errors:
    - Show loading spinner
    - API call PUT /api/profiles/{id}/content
    - Success toast notification
    - Option: "View profile" or "Continue editing"
```

### Flow 5: Выход с несохраненными изменениями
```
1. User has unsaved changes (auto-save draft exists)
2. Clicks [X Cancel] or browser back
3. Confirmation dialog appears:

   "У вас есть несохраненные изменения"
   [Сохранить] [Выйти без сохранения] [Отмена]

4a. User clicks "Сохранить":
    - Run save flow
    - Exit on success
4b. User clicks "Выйти без сохранения":
    - Discard draft
    - Exit immediately
4c. User clicks "Отмена":
    - Stay in editor
```

---

## Accessibility (a11y)

### Keyboard Navigation
```
Tab        - Move to next editable section
Shift+Tab  - Move to previous section
Ctrl+S     - Save changes
Ctrl+Z     - Undo
Ctrl+Y     - Redo
Esc        - Exit current editor, deactivate section
```

### Screen Reader Support
```vue
<!-- ARIA labels -->
<div
  role="region"
  aria-label="Competencies section"
  :aria-invalid="hasError"
>
  <h2 id="competencies-heading">Компетенции</h2>
  <div aria-describedby="competencies-heading">
    <!-- Editable content -->
  </div>
</div>

<!-- Status announcements -->
<div role="status" aria-live="polite" class="sr-only">
  {{ saveStatus }}
</div>
```

### Focus Management
```typescript
// After section save, move focus to next section
function onSectionSave(sectionId: string) {
  const nextSection = getNextSection(sectionId)
  if (nextSection) {
    focusSection(nextSection)
  }
}

// Trap focus within modal
useFocusTrap(editorModalRef)
```

---

## Responsiveness

### Desktop (≥1280px)
- Outline sidebar: 240px width
- Document area: Flexible (max-width: 900px for readability)
- Sticky top bar: Full width

### Tablet (768px - 1279px)
- Outline sidebar: Collapsible (hamburger menu)
- Document area: Full width (max 100%)
- Sticky top bar: Compact buttons

### Mobile (< 768px)
- Outline: Bottom sheet (swipe up)
- Document area: Full width, larger touch targets
- Sticky top bar: Icon-only buttons
- Simplified editors (mobile-optimized)

---

## Performance Considerations

### 1. Lazy Loading Sections
```typescript
// Only render sections in viewport + 1 above/below
const { visibleSections } = useVirtualScroll({
  items: profileSections,
  itemHeight: 300,
  buffer: 1
})
```

### 2. Debounced Auto-save
```typescript
import { useDebounceFn } from '@vueuse/core'

const debouncedSave = useDebounceFn(async () => {
  await profileStore.saveDraft(formData.value)
}, 30000) // 30 seconds

watch(formData, () => {
  hasUnsavedChanges.value = true
  debouncedSave()
}, { deep: true })
```

### 3. Optimistic UI Updates
```typescript
async function saveProfile() {
  // Update UI immediately
  profileStore.updateProfile(formData.value)

  try {
    // API call in background
    await api.updateProfileContent(profileId, formData.value)
    toast.success('Profile saved!')
  } catch (error) {
    // Revert on error
    profileStore.revertProfile()
    toast.error('Failed to save')
  }
}
```

---

## Comparison: Before vs After

### Before (ProfileEditModal.vue)
```
❌ Form-centric: Fields in form groups
❌ Limited editing: Only metadata (name, status)
❌ Separate modal: Disconnected from viewing
❌ No content editing: "Available in Week 8"
❌ No navigation: Linear form flow
```

### After (ProfileEditorModal.vue)
```
✅ Document-centric: Flowing content with natural scroll
✅ Full editing: All 50+ fields editable inline
✅ Seamless transition: View mode → Edit mode
✅ WYSIWYG: Rich text, drag & drop, inline tables
✅ Smart navigation: Outline sidebar + smooth scroll
✅ Auto-save: Never lose work
✅ Contextual tools: Formatting appears when needed
✅ Validation: Inline errors, guidance
```

---

## Technical Implementation Summary

### Component Architecture
```
ProfileEditorModal.vue (main container, full-screen)
├── EditorTopBar.vue
│   ├── ProfileTitle (inline editable)
│   ├── PreviewButton
│   ├── SaveButton (with unsaved indicator)
│   └── CancelButton
├── DocumentOutline.vue (left sidebar)
│   ├── OutlineSection (clickable, scrolls to section)
│   └── CollapseButton
├── ProfileDocument.vue (main content area)
│   ├── SectionHeader.vue
│   ├── RichTextSection.vue (TipTap)
│   ├── ListSection.vue (chips + drag)
│   ├── TableSection.vue (editable table)
│   └── NestedSection.vue (expansion panels)
├── UnsavedChangesDialog.vue
└── PreviewDialog.vue (shows DOCX preview)
```

### State Management (Pinia)
```typescript
// profileStore.ts
export const useProfileStore = defineStore('profiles', () => {
  const editingProfile = ref<Profile | null>(null)
  const draftChanges = ref<Partial<ProfileData>>({})
  const hasUnsavedChanges = ref(false)
  const validationErrors = ref<Record<string, string>>({})

  async function saveDraft(data: Partial<ProfileData>) {
    draftChanges.value = { ...draftChanges.value, ...data }
    // Save to localStorage for recovery
    localStorage.setItem('profile-draft', JSON.stringify(draftChanges.value))
  }

  async function saveProfile(profileId: string) {
    const response = await api.put(`/api/profiles/${profileId}/content`, {
      profile_data: draftChanges.value
    })
    hasUnsavedChanges.value = false
    localStorage.removeItem('profile-draft')
    return response
  }

  return {
    editingProfile,
    draftChanges,
    hasUnsavedChanges,
    saveDraft,
    saveProfile
  }
})
```

### Backend API (New Endpoint Needed)
```python
# backend/api/profiles.py

@router.put("/profiles/{profile_id}/content")
async def update_profile_content(
    profile_id: str,
    content: ProfileContentUpdate,
    db: Session = Depends(get_db)
) -> Profile:
    """Update profile content (full JSON data)."""
    profile = db.query(ProfileModel).filter_by(id=profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    # Validate content structure
    validate_profile_content(content.profile_data)

    # Update profile_data JSON field
    profile.profile_data = json.dumps(content.profile_data)
    profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)

    return profile
```

---

## Estimation

### MVP Implementation (4 key sections)
- **12-16 hours** total
- Sections: Competencies, Responsibilities, Skills, Requirements
- Editors: TipTap + Chips + Basic validation
- Features: Auto-save, Outline, Basic navigation

### Full Implementation (all sections)
- **20-25 hours** total
- All 10+ sections editable
- Advanced features: Drag & drop, Tables, Nested editing
- Full validation, Preview, Keyboard shortcuts
- Polish: Animations, Loading states, Error recovery

---

**Next Step:** Получить подтверждение от пользователя на этот UX/UI дизайн, затем начать имплементацию с MVP варианта.

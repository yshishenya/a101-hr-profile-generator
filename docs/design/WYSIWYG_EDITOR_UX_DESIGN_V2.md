# WYSIWYG Profile Editor - UX/UI Design V2 (УЛУЧШЕННАЯ ВЕРСИЯ)

## 🚨 Критический анализ первоначального дизайна

### ❌ Проблемы Version 1:

1. **Outline слева противоречит системе**
   - В ProfileViewerModal metadata sidebar находится **СПРАВА**
   - Outline слева будет нелогичным и непривычным для пользователя

2. **Full-screen modal слишком радикально**
   - Текущая система: `max-width="1400px"` (не full-screen!)
   - Full-screen нарушит consistency UI

3. **"Единый документ" противоречит существующему паттерну**
   - ProfileContent использует **отдельные v-card для каждой секции**
   - Пользователи привыкли к визуально разделенным секциям

4. **TipTap и сложные зависимости**
   - Система использует ТОЛЬКО Vuetify (простые нативные компоненты)
   - TipTap = новая зависимость 20KB+, сложность, обучение
   - vue-draggable-next = еще одна зависимость

5. **Новый компонент вместо расширения существующего**
   - Уже есть ProfileEditModal.vue!
   - Нужно **расширить**, а не создавать новый ProfileEditorModal

6. **Переход View → Edit слишком сложный**
   - Система использует **отдельные модалки** для разных действий
   - Не нужны "плавные трансформации"

---

## ✅ Новая философия: "Section-Based Editing" (как Notion)

### Главная идея:

**НЕ "единый документ" (как Word)**
**А "структурированные секции" (как Notion, Confluence)**

- Сохранить паттерн отдельных v-card для секций ✓
- Добавить inline редактирование внутри секций ✓
- Использовать ТОЛЬКО Vuetify компоненты ✓
- Следовать существующему layout (9/3 split, sidebar справа) ✓
- Расширить ProfileEditModal, а не создавать новый компонент ✓

---

## Визуальная Структура (соответствует системе)

```
┌──────────────────────────────────────────────────────────────────────┐
│  [📝 Редактирование: Frontend Developer]  [💾 Save] [✗ Cancel]        │ ← Header (v-sheet)
├──────────────────────────────────────┬───────────────────────────────┤
│                                      │                               │
│  CONTENT AREA (col-9)                │  METADATA SIDEBAR (col-3)     │
│  ─────────────────                   │  ──────────────────           │
│                                      │                               │
│  ┌────────────────────────────────┐  │  📍 Позиция                   │
│  │ v-card                         │  │  Frontend Developer           │
│  ├────────────────────────────────┤  │  (read-only)                  │
│  │ 🧠 Компетенции                 │  │                               │
│  │ [режим: просмотр]              │  │  📊 Департамент               │
│  ├────────────────────────────────┤  │  IT / Development             │
│  │ Технические:                   │  │  (read-only)                  │
│  │ [Vue.js] [React] [TypeScript]  │  │                               │
│  │                                │  │  ─────────────                │
│  │ Управленческие:                │  │                               │
│  │ [Планирование] [Менторство]    │  │  🧭 Быстрая навигация         │
│  │                                │  │  (Sticky при скролле)         │
│  │ [✏️ Edit Section]              │  │                               │
│  └────────────────────────────────┘  │  → 🧠 Компетенции             │
│                                      │  → 📋 Обязанности ⚠️          │
│  ┌────────────────────────────────┐  │  → 🛠️ Навыки                  │
│  │ v-card (EDIT MODE ACTIVE)      │  │  → 🎓 Образование             │
│  ├────────────────────────────────┤  │  → 💼 Опыт работы             │
│  │ 📋 Обязанности                 │  │  → 📊 Показатели              │
│  │ [режим: редактирование] ✏️     │  │                               │
│  ├────────────────────────────────┤  │  ⚠️ = есть несохраненные     │
│  │                                │  │       изменения               │
│  │ [v-textarea]                   │  │                               │
│  │ ┌────────────────────────────┐ │  │  ─────────────                │
│  │ │Разработка пользовательских│ │  │                               │
│  │ │интерфейсов с использованием│ │  │  💡 Tips                      │
│  │ │Vue 3 и TypeScript.         │ │  │                               │
│  │ │                            │ │  │  • Ctrl+S - сохранить         │
│  │ │Код-ревью и менторство...   │ │  │  • Esc - отменить             │
│  │ └────────────────────────────┘ │  │  • Tab - след. секция         │
│  │                                │  │                               │
│  │ [✓ Save] [✗ Cancel]            │  │  ─────────────                │
│  └────────────────────────────────┘  │                               │
│                                      │  📈 Validation Status          │
│  ┌────────────────────────────────┐  │                               │
│  │ v-card                         │  │  ✓ Компетенции (заполнено)    │
│  ├────────────────────────────────┤  │  ✓ Обязанности (заполнено)    │
│  │ 🛠️ Навыки                       │  │  ⚠️ Навыки (требует внимания) │
│  │ [режим: просмотр]              │  │  ✓ Образование (заполнено)    │
│  ├────────────────────────────────┤  │                               │
│  │ Hard Skills:                   │  │  ─────────────                │
│  │ [v-combobox для редактирования]│  │                               │
│  │ ┌────────────────────────────┐ │  │  Auto-save: OFF               │
│  │ │ [Vue.js ✖] [TypeScript ✖]  │ │  │  (Manual save only)           │
│  │ │ [+ Add skill...]           │ │  │                               │
│  │ └────────────────────────────┘ │  │                               │
│  │                                │  │                               │
│  │ Soft Skills:                   │  │                               │
│  │ [Communication] [Teamwork]     │  │                               │
│  │                                │  │                               │
│  │ [✏️ Edit Section]              │  │                               │
│  └────────────────────────────────┘  │                               │
│                                      │                               │
│  [Scroll continues...]               │                               │
│                                      │                               │
└──────────────────────────────────────┴───────────────────────────────┘
```

---

## Ключевые принципы дизайна

### 1. ✅ Следуем существующим паттернам

**ProfileViewerModal** (текущий просмотр):
- max-width="1400px" ✓
- Layout: 9/3 split (content/metadata) ✓
- Metadata sidebar СПРАВА ✓
- v-card для каждой секции ✓
- v-sheet bg-color="surface-variant" для headers ✓

**Мы сохраняем все это!**

### 2. ✅ Только Vuetify компоненты (NO new dependencies!)

❌ TipTap → ✅ `v-textarea` (native Vuetify)
❌ vue-draggable-next → ✅ `v-combobox` (already in system!)
❌ Custom WYSIWYG → ✅ Simple text editing

**Преимущества:**
- Zero new dependencies = меньше bundle size
- Пользователи уже знают Vuetify компоненты
- Единый стиль с остальной системой
- Проще поддержка и тестирование

### 3. ✅ Расширяем ProfileEditModal, не создаем новый

**Текущий ProfileEditModal.vue:**
- Редактирует: employee_name, status (metadata only)
- max-width="600px"
- Alert: "Редактирование содержимого профиля будет доступно в Week 8"

**Наше решение:**
- Создать **ProfileContentEditor.vue** (отдельный компонент для content)
- ProfileEditModal → использует ProfileContentEditor внутри
- Или: создать **FullProfileEditModal.vue** (полное редактирование)
- ProfileEditModal остается для metadata (backward compatibility)

### 4. ✅ Section-by-section editing (как Notion)

**Два режима для каждой секции:**

**A) View Mode (default):**
```vue
<v-card>
  <v-sheet bg-color="surface-variant" class="pa-4">
    <div class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon class="mr-2">mdi-brain</v-icon>
        <span class="text-h6">Компетенции</span>
        <v-chip size="small" color="success" class="ml-2">✓</v-chip>
      </div>
      <v-btn
        icon="mdi-pencil"
        variant="text"
        size="small"
        @click="activateEditMode('competencies')"
      />
    </div>
  </v-sheet>

  <v-card-text class="pa-4">
    <!-- Read-only display (chips, text, etc) -->
    <v-chip v-for="skill in skills" class="ma-1">{{ skill }}</v-chip>
  </v-card-text>
</v-card>
```

**B) Edit Mode (activated):**
```vue
<v-card :color="isEditing ? 'primary-lighten-5' : undefined">
  <v-sheet bg-color="surface-variant" class="pa-4">
    <div class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon class="mr-2">mdi-brain</v-icon>
        <span class="text-h6">Компетенции</span>
        <v-chip size="small" color="warning">⚠️ Editing</v-chip>
      </div>
      <div>
        <v-btn icon="mdi-check" variant="text" size="small" color="success" @click="saveSection" />
        <v-btn icon="mdi-close" variant="text" size="small" color="error" @click="cancelEdit" />
      </div>
    </div>
  </v-sheet>

  <v-card-text class="pa-4">
    <!-- Editable inputs (v-combobox, v-textarea, etc) -->
    <v-combobox
      v-model="editableSkills"
      chips
      multiple
      closable-chips
      label="Добавьте навыки"
    />
  </v-card-text>

  <v-card-actions class="pa-4">
    <v-spacer />
    <v-btn variant="text" @click="cancelEdit">Отмена</v-btn>
    <v-btn color="success" @click="saveSection">Сохранить секцию</v-btn>
  </v-card-actions>
</v-card>
```

---

## Типы секций и редакторы (ТОЛЬКО Vuetify)

### 1. Text Sections (Обязанности, Описания)

**View Mode:**
```vue
<div class="text-body-1" v-html="formattedText"></div>
```

**Edit Mode:**
```vue
<v-textarea
  v-model="editableText"
  variant="outlined"
  rows="8"
  auto-grow
  counter="2000"
  :rules="[v => v.length <= 2000 || 'Максимум 2000 символов']"
  label="Обязанности и зоны ответственности"
  hint="Опишите основные обязанности. Используйте абзацы для структуры."
  persistent-hint
>
  <template #prepend-inner>
    <v-icon>mdi-text</v-icon>
  </template>
</v-textarea>

<!-- Simple formatting helper (optional) -->
<div class="text-caption text-medium-emphasis mt-2">
  💡 Tip: Используйте пустые строки для разделения параграфов
</div>
```

**Преимущества vs TipTap:**
- ✅ Native Vuetify = 0 KB overhead
- ✅ Простота = меньше bugs
- ✅ Быстрота = instant load
- ❌ Нет rich formatting (bold, italic) - но это для профилей не критично!

### 2. List Sections (Навыки, Компетенции, Качества)

**View Mode:**
```vue
<v-chip
  v-for="item in items"
  :key="item.id"
  class="ma-1"
  variant="outlined"
>
  {{ item.name }}
</v-chip>
```

**Edit Mode:**
```vue
<v-combobox
  v-model="editableItems"
  chips
  closable-chips
  multiple
  variant="outlined"
  label="Навыки"
  hint="Нажмите Enter для добавления нового навыка"
  persistent-hint
  :items="suggestedSkills"
>
  <template #chip="{ props: chipProps, item }">
    <v-chip
      v-bind="chipProps"
      closable
      @click:close="removeItem(item)"
    >
      {{ item }}
    </v-chip>
  </template>
</v-combobox>

<!-- Example: autocomplete from existing skills in system -->
<div class="text-caption mt-2">
  💡 Популярные навыки: Vue.js, React, TypeScript, Python, Docker...
</div>
```

**Преимущества:**
- ✅ v-combobox уже используется в системе (PositionSearchAutocomplete)
- ✅ Поддерживает autocomplete из существующих навыков
- ✅ Drag to reorder - можно добавить через simple CSS/JS (без библиотеки!)

### 3. Table Sections (Опыт работы, Образование)

**View Mode:**
```vue
<v-table density="comfortable">
  <tbody>
    <tr v-for="row in rows" :key="row.id">
      <td class="font-weight-bold" style="width: 30%">{{ row.label }}</td>
      <td>{{ row.value }}</td>
    </tr>
  </tbody>
</v-table>
```

**Edit Mode:**
```vue
<v-data-table
  :headers="headers"
  :items="editableRows"
  density="comfortable"
  :items-per-page="-1"
  hide-default-footer
>
  <!-- Inline editing cells -->
  <template #item.label="{ item }">
    <v-text-field
      v-model="item.label"
      variant="plain"
      density="compact"
      hide-details
    />
  </template>

  <template #item.value="{ item }">
    <v-text-field
      v-model="item.value"
      variant="plain"
      density="compact"
      hide-details
    />
  </template>

  <template #item.actions="{ item }">
    <v-btn
      icon="mdi-delete"
      variant="text"
      size="small"
      color="error"
      @click="removeRow(item)"
    />
  </template>
</v-data-table>

<v-btn
  prepend-icon="mdi-plus"
  variant="outlined"
  size="small"
  class="mt-2"
  @click="addRow"
>
  Добавить строку
</v-btn>
```

### 4. Nested Sections (Зоны ответственности с подзадачами)

**View Mode:**
```vue
<v-expansion-panels variant="accordion">
  <v-expansion-panel v-for="area in areas" :key="area.id">
    <v-expansion-panel-title>{{ area.title }}</v-expansion-panel-title>
    <v-expansion-panel-text>
      <v-chip v-for="task in area.tasks" class="ma-1">{{ task }}</v-chip>
    </v-expansion-panel-text>
  </v-expansion-panel>
</v-expansion-panels>
```

**Edit Mode:**
```vue
<v-expansion-panels variant="accordion" multiple>
  <v-expansion-panel v-for="area in editableAreas" :key="area.id">
    <!-- Editable title -->
    <v-expansion-panel-title>
      <v-text-field
        v-model="area.title"
        variant="plain"
        density="compact"
        @click.stop
      />
      <v-btn
        icon="mdi-delete"
        variant="text"
        size="small"
        @click.stop="removeArea(area.id)"
      />
    </v-expansion-panel-title>

    <!-- Editable tasks -->
    <v-expansion-panel-text>
      <v-combobox
        v-model="area.tasks"
        chips
        closable-chips
        multiple
        variant="outlined"
        label="Задачи в этой области"
      />
    </v-expansion-panel-text>
  </v-expansion-panel>
</v-expansion-panels>

<v-btn
  prepend-icon="mdi-plus"
  variant="outlined"
  size="small"
  class="mt-2"
  @click="addArea"
>
  Добавить зону ответственности
</v-btn>
```

---

## Metadata Sidebar (справа, как в системе)

### Содержимое:

```vue
<div class="metadata-sidebar pa-4">
  <!-- Position Info (read-only) -->
  <div class="mb-6">
    <div class="text-subtitle-2 text-medium-emphasis mb-1">Позиция</div>
    <div class="text-body-1 font-weight-medium">{{ profile.position_name }}</div>
  </div>

  <div class="mb-6">
    <div class="text-subtitle-2 text-medium-emphasis mb-1">Департамент</div>
    <div class="text-body-1">{{ profile.department_name }}</div>
  </div>

  <v-divider class="my-4" />

  <!-- Quick Navigation (sticky при скролле) -->
  <div class="quick-nav mb-6">
    <div class="text-subtitle-2 mb-2">Быстрая навигация</div>
    <v-list density="compact" nav>
      <v-list-item
        v-for="section in sections"
        :key="section.id"
        :active="activeSection === section.id"
        @click="scrollToSection(section.id)"
      >
        <template #prepend>
          <v-icon :icon="section.icon" size="small" />
          <v-badge
            v-if="section.hasChanges"
            dot
            color="warning"
            offset-x="-8"
            offset-y="8"
          />
        </template>
        <v-list-item-title>{{ section.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </div>

  <v-divider class="my-4" />

  <!-- Validation Status -->
  <div class="validation-status mb-6">
    <div class="text-subtitle-2 mb-2">Статус заполнения</div>
    <div v-for="section in sections" :key="section.id" class="d-flex align-center mb-2">
      <v-icon
        :icon="section.isValid ? 'mdi-check-circle' : 'mdi-alert-circle'"
        :color="section.isValid ? 'success' : 'warning'"
        size="small"
        class="mr-2"
      />
      <span class="text-caption">{{ section.title }}</span>
    </div>
  </div>

  <v-divider class="my-4" />

  <!-- Keyboard Shortcuts -->
  <div class="shortcuts">
    <div class="text-subtitle-2 mb-2">💡 Горячие клавиши</div>
    <div class="text-caption text-medium-emphasis">
      <div><kbd>Ctrl+S</kbd> Сохранить</div>
      <div><kbd>Esc</kbd> Отменить редактирование</div>
      <div><kbd>Tab</kbd> Следующая секция</div>
    </div>
  </div>
</div>
```

---

## User Flows (упрощенные)

### Flow 1: Открытие редактора

```
1. User просматривает профиль в ProfileViewerModal
2. Нажимает кнопку [Edit] (в header рядом с download)
3. Modal закрывается → открывается FullProfileEditModal
   - Тот же max-width="1400px"
   - Тот же 9/3 layout
   - Все секции в view mode
4. User видит знакомую структуру, но с кнопками [Edit Section]
```

### Flow 2: Редактирование секции

```
1. User scrolls to "Навыки" section
2. Нажимает [✏️ Edit Section] в header секции
3. Секция переходит в edit mode:
   - Background становится light primary
   - Chips → v-combobox
   - Появляются [Save] [Cancel] кнопки
4. User добавляет/удаляет навыки
5. Нажимает [Save] → валидация → сохранение
6. Секция возвращается в view mode
7. ⚠️ Badge появляется в navigation (unsaved changes)
```

### Flow 3: Сохранение изменений

```
1. User отредактировал 3 секции (unsaved changes)
2. Нажимает [💾 Save All] в top bar
3. Валидация всех измененных секций:
   - If errors: показать inline в секциях + scroll to first error
   - If no errors: proceed
4. Показать progress indicator
5. API call PUT /api/profiles/{id}/content
6. Success:
   - Toast notification "Профиль сохранен"
   - Clear unsaved changes badges
   - Option: stay in edit mode OR close modal
7. Error:
   - Toast notification "Ошибка сохранения"
   - Keep edit mode, retry available
```

### Flow 4: Выход без сохранения

```
1. User has unsaved changes (⚠️ badges visible)
2. Нажимает [✗ Cancel] OR browser back
3. Confirmation dialog (уже есть в системе!):

   ┌─────────────────────────────────────┐
   │ ⚠️ Несохраненные изменения          │
   ├─────────────────────────────────────┤
   │ У вас есть несохраненные изменения  │
   │ в 3 секциях. Сохранить перед        │
   │ выходом?                            │
   │                                     │
   │ [Отмена] [Не сохранять] [Сохранить] │
   └─────────────────────────────────────┘

4a. [Сохранить]: run save flow → close
4b. [Не сохранять]: discard changes → close
4c. [Отмена]: stay in edit mode
```

---

## Component Architecture (расширяем существующее)

### Вариант A: Расширить ProfileEditModal

```
ProfileEditModal.vue (ENHANCED)
├── Metadata editing (employee_name, status) [existing]
├── NEW: Content editing section
│   └── ProfileContentEditor.vue
│       ├── SectionCard.vue (wrapper with view/edit modes)
│       │   ├── TextSectionEditor.vue (v-textarea)
│       │   ├── ListSectionEditor.vue (v-combobox)
│       │   ├── TableSectionEditor.vue (v-data-table)
│       │   └── NestedSectionEditor.vue (v-expansion-panels)
│       └── MetadataSidebar.vue (quick nav, validation status)
└── UnsavedChangesDialog.vue (confirmation)
```

**Проблема:** ProfileEditModal имеет max-width="600px" (слишком узко для content)

### Вариант B: Новый FullProfileEditModal (RECOMMENDED)

```
FullProfileEditModal.vue (NEW - для content)
├── Header (position name, Save All, Cancel)
├── v-row (9/3 split как ProfileViewerModal)
│   ├── v-col (cols="9") - Content Area
│   │   └── ProfileContentEditor.vue
│   │       └── SectionCard.vue (для каждой секции)
│   │           ├── View Mode: display + [Edit] button
│   │           └── Edit Mode: inputs + [Save] [Cancel]
│   │
│   └── v-col (cols="3") - Metadata Sidebar
│       ├── Position info (read-only)
│       ├── Quick navigation (clickable section links)
│       ├── Validation status indicators
│       └── Keyboard shortcuts help
│
└── UnsavedChangesDialog.vue

ProfileEditModal.vue (EXISTING - для metadata)
└── Keep for backward compatibility
    └── Only edits: employee_name, status
```

**Преимущества Варианта B:**
- ✅ Не ломает существующий ProfileEditModal
- ✅ max-width="1400px" как ProfileViewerModal (consistency)
- ✅ Можно использовать оба: быстрый edit metadata vs полное редактирование
- ✅ Проще тестирование (изолированные компоненты)

---

## State Management (Pinia)

### profilesStore.ts (расширить)

```typescript
export const useProfilesStore = defineStore('profiles', () => {
  // Existing state...
  const currentProfile = ref<Profile | null>(null)

  // NEW: editing state
  const editingProfile = ref<Profile | null>(null)
  const editingSections = ref<Record<string, boolean>>({})
  const draftChanges = ref<Record<string, unknown>>({})
  const hasUnsavedChanges = ref(false)
  const validationErrors = ref<Record<string, string>>({})

  // NEW: editing actions
  function startEditing(profile: Profile) {
    editingProfile.value = { ...profile }
    draftChanges.value = {}
    hasUnsavedChanges.value = false
    editingSections.value = {}
    validationErrors.value = {}
  }

  function editSection(sectionId: string) {
    editingSections.value[sectionId] = true
  }

  function updateSectionData(sectionId: string, data: unknown) {
    draftChanges.value[sectionId] = data
    hasUnsavedChanges.value = true
  }

  function cancelSectionEdit(sectionId: string) {
    delete draftChanges.value[sectionId]
    editingSections.value[sectionId] = false

    // Check if any changes remain
    hasUnsavedChanges.value = Object.keys(draftChanges.value).length > 0
  }

  async function saveSectionChanges(sectionId: string) {
    // Validate section
    const errors = validateSection(sectionId, draftChanges.value[sectionId])
    if (errors.length > 0) {
      validationErrors.value[sectionId] = errors[0]
      return false
    }

    // Update editing profile with changes
    if (editingProfile.value) {
      // Merge changes into editingProfile
      // This is in-memory only, not saved to backend yet
      updateProfileSection(editingProfile.value, sectionId, draftChanges.value[sectionId])
    }

    // Exit edit mode for this section
    editingSections.value[sectionId] = false
    delete validationErrors.value[sectionId]

    return true
  }

  async function saveAllChanges(profileId: string) {
    // Validate all sections with changes
    const allErrors: Record<string, string> = {}
    for (const [sectionId, data] of Object.entries(draftChanges.value)) {
      const errors = validateSection(sectionId, data)
      if (errors.length > 0) {
        allErrors[sectionId] = errors[0]
      }
    }

    if (Object.keys(allErrors).length > 0) {
      validationErrors.value = allErrors
      return false
    }

    // Save to backend
    try {
      const response = await api.put(`/api/profiles/${profileId}/content`, {
        profile_data: editingProfile.value?.profile_data
      })

      // Update current profile
      currentProfile.value = response.data

      // Clear editing state
      draftChanges.value = {}
      hasUnsavedChanges.value = false
      editingSections.value = {}
      validationErrors.value = {}

      return true
    } catch (error: unknown) {
      logger.error('Failed to save profile changes', error)
      throw error
    }
  }

  function discardChanges() {
    draftChanges.value = {}
    hasUnsavedChanges.value = false
    editingSections.value = {}
    validationErrors.value = {}
    editingProfile.value = null
  }

  return {
    // Existing...
    currentProfile,
    // NEW
    editingProfile,
    editingSections,
    draftChanges,
    hasUnsavedChanges,
    validationErrors,
    startEditing,
    editSection,
    updateSectionData,
    cancelSectionEdit,
    saveSectionChanges,
    saveAllChanges,
    discardChanges
  }
})
```

---

## Backend API (новый endpoint)

### PUT /api/profiles/{profile_id}/content

```python
# backend/api/profiles.py

from pydantic import BaseModel, Field
from typing import Dict, Any

class ProfileContentUpdate(BaseModel):
    """Profile content update payload."""
    profile_data: Dict[str, Any] = Field(
        ...,
        description="Full profile data JSON"
    )

@router.put("/profiles/{profile_id}/content", response_model=ProfileResponse)
async def update_profile_content(
    profile_id: str,
    content: ProfileContentUpdate,
    db: Session = Depends(get_db)
) -> ProfileResponse:
    """
    Update profile content (full JSON data).

    This endpoint replaces the entire profile_data field.
    Use PUT /api/profiles/{id} for metadata updates only.
    """
    # Get profile
    profile = db.query(ProfileModel).filter_by(id=profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")

    # Validate content structure
    try:
        validate_profile_structure(content.profile_data)
    except ValidationError as e:
        raise HTTPException(400, f"Invalid profile structure: {e}")

    # Update profile_data JSON field
    profile.profile_data = json.dumps(content.profile_data, ensure_ascii=False)
    profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)

    return ProfileResponse.from_orm(profile)


def validate_profile_structure(data: Dict[str, Any]) -> None:
    """
    Validate profile data structure.

    Raises ValidationError if structure is invalid.
    """
    required_sections = [
        'competencies',
        'responsibilities',
        'skills',
        'education',
        'experience'
    ]

    for section in required_sections:
        if section not in data:
            raise ValueError(f"Missing required section: {section}")

    # Additional validation rules...
    # - competencies must be dict or list
    # - responsibilities must be list or string
    # - etc.
```

---

## Validation Rules (frontend)

```typescript
// utils/profileValidation.ts

export interface ValidationRule {
  validate: (value: unknown) => boolean
  message: string
}

export const sectionValidationRules: Record<string, ValidationRule[]> = {
  competencies: [
    {
      validate: (v) => !!v && Object.keys(v as Record<string, unknown>).length > 0,
      message: 'Добавьте хотя бы одну категорию компетенций'
    }
  ],
  responsibilities: [
    {
      validate: (v) => !!v && (v as string).trim().length >= 50,
      message: 'Описание обязанностей должно быть не менее 50 символов'
    },
    {
      validate: (v) => (v as string).length <= 2000,
      message: 'Максимум 2000 символов'
    }
  ],
  skills: [
    {
      validate: (v) => Array.isArray(v) && v.length >= 3,
      message: 'Добавьте минимум 3 навыка'
    },
    {
      validate: (v) => Array.isArray(v) && v.length <= 50,
      message: 'Максимум 50 навыков'
    }
  ],
  education: [
    {
      validate: (v) => !!v && (v as string).trim().length >= 20,
      message: 'Укажите минимальные требования к образованию (мин. 20 символов)'
    }
  ],
  experience: [
    {
      validate: (v) => !!v,
      message: 'Укажите требования к опыту работы'
    }
  ]
}

export function validateSection(sectionId: string, value: unknown): string[] {
  const rules = sectionValidationRules[sectionId]
  if (!rules) return []

  const errors: string[] = []
  for (const rule of rules) {
    if (!rule.validate(value)) {
      errors.push(rule.message)
    }
  }

  return errors
}

export function validateAllSections(profileData: Record<string, unknown>): Record<string, string[]> {
  const allErrors: Record<string, string[]> = {}

  for (const [sectionId, value] of Object.entries(profileData)) {
    const errors = validateSection(sectionId, value)
    if (errors.length > 0) {
      allErrors[sectionId] = errors
    }
  }

  return allErrors
}
```

---

## Keyboard Shortcuts

```typescript
// composables/useProfileEditorShortcuts.ts

import { onMounted, onUnmounted } from 'vue'

export function useProfileEditorShortcuts(callbacks: {
  onSave: () => void
  onCancel: () => void
  onNextSection: () => void
  onPrevSection: () => void
}) {
  function handleKeydown(event: KeyboardEvent) {
    // Ctrl+S / Cmd+S - Save
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault()
      callbacks.onSave()
    }

    // Esc - Cancel editing
    if (event.key === 'Escape') {
      event.preventDefault()
      callbacks.onCancel()
    }

    // Tab - Next section (when not in input)
    if (event.key === 'Tab' && !(event.target as HTMLElement).matches('input, textarea')) {
      event.preventDefault()
      if (event.shiftKey) {
        callbacks.onPrevSection()
      } else {
        callbacks.onNextSection()
      }
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}
```

---

## Comparison: Before vs After

### Before (ProfileEditModal.vue - EXISTING)
```
✅ max-width="600px"
✅ Edits: employee_name, status (metadata only)
❌ Content editing: "Available in Week 8"
❌ No validation for content
❌ Simple form layout
```

### After (FullProfileEditModal.vue - NEW)
```
✅ max-width="1400px" (like ProfileViewerModal)
✅ 9/3 layout with sidebar (consistent with system)
✅ Section-by-section editing (like Notion)
✅ ONLY Vuetify components (zero new dependencies)
✅ Inline validation with helpful messages
✅ Quick navigation in sidebar
✅ Unsaved changes protection
✅ Keyboard shortcuts
✅ Validation status indicators
✅ Follows existing color scheme and patterns
```

---

## Estimation (REALISTIC)

### MVP Implementation (4 core sections)
**Sections:** Competencies, Responsibilities, Skills, Requirements

**Components to create:**
- FullProfileEditModal.vue (main container)
- ProfileContentEditor.vue (content area)
- SectionCard.vue (view/edit mode switcher)
- TextSectionEditor.vue (v-textarea)
- ListSectionEditor.vue (v-combobox)
- MetadataSidebar.vue (navigation)
- UnsavedChangesDialog.vue (reuse existing ConfirmDeleteDialog pattern)

**Backend:**
- Add PUT /api/profiles/{id}/content endpoint (2-3 hours)
- Add validation function (1 hour)

**Frontend:**
- Components (8-10 hours)
- Store methods (2-3 hours)
- Validation rules (1-2 hours)
- Keyboard shortcuts (1 hour)
- Testing (3-4 hours)

**Total: 18-23 hours**

### Full Implementation (all sections + polish)
**Additional sections:** Education, Experience, Performance Metrics, etc.

**Additional features:**
- Drag & drop for chips (vanilla JS, no library)
- Editable tables with add/remove rows
- Nested section editing with subsections
- Autocomplete suggestions from existing profiles
- Preview before save
- Undo/redo (browser history API)
- Field-level auto-save to localStorage (draft recovery)

**Additional time: +8-12 hours**

**Total: 26-35 hours**

---

## Next Steps

1. **Get approval on this design** from user
2. **Choose implementation variant:**
   - Variant A: Extend ProfileEditModal (simpler, breaks existing UI)
   - Variant B: New FullProfileEditModal (recommended, keeps compatibility)
3. **Start with MVP:**
   - Backend endpoint first (can test with Postman)
   - Then FullProfileEditModal skeleton
   - Then SectionCard with view/edit modes
   - Then individual editors (text, list, table)
   - Then sidebar navigation
4. **Iterate based on feedback**

---

## Key Decisions Changelog

### Version 1 → Version 2 changes:

| Aspect | V1 (Wrong) | V2 (Correct) |
|--------|-----------|--------------|
| Layout | Full-screen | max-width="1400px" ✓ |
| Outline | Left sidebar | Right sidebar (metadata) ✓ |
| Document type | Single flowing doc | Separate section cards ✓ |
| Rich text editor | TipTap (20KB+) | v-textarea (native) ✓ |
| List editor | vue-draggable-next | v-combobox (native) ✓ |
| Component name | ProfileEditorModal | FullProfileEditModal ✓ |
| Edit approach | Transform viewer | New edit modal ✓ |
| Dependencies | +2 libraries | Zero new deps ✓ |
| Complexity | High (WYSIWYG) | Medium (structured forms) ✓ |

---

**Summary:** Version 2 следует существующим паттернам системы, использует только Vuetify, проще в реализации и поддержке, более интуитивен для пользователей, которые уже знакомы с UI приложения.

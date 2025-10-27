# Component Library

## Полный каталог переиспользуемых компонентов

**⚠️ КРИТИЧНО**: Читайте этот документ ПЕРЕД созданием любого нового компонента!

Этот документ содержит **полный список** всех переиспользуемых компонентов в проекте. Прежде чем создавать новый компонент, **ОБЯЗАТЕЛЬНО** проверьте, не существует ли уже подходящего.

---

## Содержание

1. [Common Components](#1-common-components-базовые) - Базовые UI компоненты
   - 1.1 BaseCard - Универсальная карточка
   - 1.2 StatsCard - Карточка статистики
   - 1.3 ConfirmDeleteDialog - Диалог подтверждения удаления
   - 1.4 **BaseThemedDialog** - Базовый диалог с темизацией (NEW - Week 6 Phase 1!)
2. [Generator Components](#2-generator-components-генератор) - Компоненты генератора
3. [Profiles Components](#3-profiles-components-профили) - Компоненты управления профилями
   - 3.1 PositionsTable
   - 3.2 ProfileContent
   - 3.3 ProfileViewerModal
   - 3.4 ProfileEditModal
   - 3.5 FilterBar
   - 3.6 **ProfileVersionsPanel** - Панель истории версий профиля (NEW - Week 6 Phase 3!)
   - 3.7 **DateRangeFilter** - Фильтр по диапазону дат (Week 6 Phase 2)
   - 3.8 **FilterPresets** - ⚠️ Управление пресетами (сохранен но НЕ используется после UX ревью)
4. [Layout Components](#4-layout-components-layout) - Layout компоненты
5. [Composables](#5-composables-переиспользуемая-логика) - Переиспользуемая логика
   - 5.1 useTaskStatus - Polling механизм
   - 5.2 **useProfileVersions** - Управление версиями профиля (NEW - Week 6 Phase 3!)
   - 5.3 **useAnalytics** - Tracking пользовательских событий (NEW - Week 6 Phase 3!)
6. [Utilities](#6-utilities-утилиты) - Переиспользуемые утилиты
   - 6.1 **filterPresets.ts** - Управление пресетами фильтров (Week 6 Phase 2)
7. [When to Create New Component](#7-когда-создавать-новый-компонент) - Руководство

---

## 1. Common Components (Базовые)

### 1.1 BaseCard

**Файл**: [src/components/common/BaseCard.vue](../../frontend-vue/src/components/common/BaseCard.vue)

**Назначение**: Унифицированная карточка с заголовком, подзаголовком и слотом для действий.

**Props**:
```typescript
interface Props {
  title?: string
  subtitle?: string
  elevation?: number | string  // Vuetify elevation (0-24)
  loading?: boolean
  class?: string
}
```

**Slots**:
```typescript
{
  default: () => void        // Основное содержимое
  actions: () => void        // Кнопки/действия в header
  'subtitle-append': () => void  // Дополнение к subtitle
}
```

**Примеры использования**:

```vue
<!-- Простая карточка -->
<BaseCard title="Статистика" subtitle="Текущие данные">
  <p>Содержимое карточки</p>
</BaseCard>

<!-- С действиями -->
<BaseCard title="Профили" subtitle="Управление">
  <template #actions>
    <v-btn @click="handleRefresh">Обновить</v-btn>
  </template>
  <PositionsTable :items="items" />
</BaseCard>

<!-- С loading состоянием -->
<BaseCard
  title="Загрузка данных"
  :loading="isLoading"
  elevation="2"
>
  <v-skeleton-loader type="table" />
</BaseCard>
```

**Когда использовать**:
- ✅ Любой контент, который нужно обернуть в карточку
- ✅ Секции на dashboard
- ✅ Модальные окна с заголовком
- ✅ Панели с действиями

**Когда НЕ использовать**:
- ❌ Для простого текста без заголовка
- ❌ Когда нужна custom структура header

---

### 1.2 StatsCard

**Файл**: [src/components/common/StatsCard.vue](../../frontend-vue/src/components/common/StatsCard.vue)

**Назначение**: Унифицированная карточка статистики с иконкой, значением, меткой и опциональным прогресс-баром.

**⚠️ Используется в 3 views**: DashboardView (4x), GeneratorView (4x), UnifiedProfilesView (через StatsOverview)

**Props**:
```typescript
interface Props {
  icon?: string              // Material Design icon (mdi-*)
  iconColor?: string         // Цвет иконки: 'primary' | 'success' | 'warning' | 'info' | 'error'
  label: string              // Метка (например, "Total Positions")
  value: number | string     // Значение (число или строка)
  progressValue?: number     // Значение прогресс-бара (0-100)
  progressColor?: string     // Переопределить цвет прогресс-бара
  lastUpdated?: string       // ISO 8601 timestamp для "обновлено X назад"
  decimals?: number          // Количество десятичных знаков для чисел (default: 0)
}
```

**Стандартизированные значения**:
- **Typography**: Value 24px (weight 600), Label 12px (uppercase, weight 500)
- **Icon container**: 56x56px (desktop), 48x48px (tablet), border-radius 12px
- **Progress bar**: Height 4px, rounded
- **Gap**: 12px between icon and content
- **Responsive**: 3 breakpoints (desktop, tablet ≤960px, mobile ≤600px)

**Примеры использования**:

```vue
<!-- Базовая карточка -->
<StatsCard
  icon="mdi-briefcase-outline"
  icon-color="primary"
  label="Total Positions"
  :value="1234"
/>

<!-- С прогресс-баром -->
<StatsCard
  icon="mdi-account-check-outline"
  icon-color="success"
  label="Profiles Generated"
  :value="856"
  :progress-value="69.5"
/>

<!-- С процентами и timestamp -->
<StatsCard
  icon="mdi-chart-arc"
  icon-color="info"
  label="Completion"
  value="69.5%"
  :progress-value="69.5"
  last-updated="2025-10-26T15:30:00Z"
/>

<!-- С десятичными знаками -->
<StatsCard
  icon="mdi-chart-line"
  icon-color="success"
  label="Average Quality"
  :value="87.6542"
  :decimals="2"
/>
```

**Семантические цвета** (следовать этим правилам!):
- `primary` - Общие/итоговые метрики (Total, General)
- `success` - Завершенные/положительные метрики (Completed, Generated)
- `warning` - Активные задачи/внимание (Active, Pending)
- `info` - Покрытие/прогресс (Coverage, Completion)
- `error` - Ошибки/проблемы (Errors, Failed)

**Когда использовать**:
- ✅ **ВСЕГДА** для отображения числовой статистики
- ✅ Dashboard metrics
- ✅ Overview статистики
- ✅ KPI карточки
- ✅ Coverage/Progress metrics

**Когда НЕ использовать**:
- ❌ Для сложной статистики с графиками (используйте custom компонент)
- ❌ Для текстовой информации без числовых данных
- ❌ Если нужна custom структура (не icon + value + label)

**Особенности**:
- Автоматическое форматирование чисел с разделителями тысяч
- Адаптивный layout (column на мобильных)
- Dark theme support через CSS variables
- Семантические размеры иконок (`x-large`)
- Опциональный timestamp с относительным временем ("5 мин назад")

**Миграция со старого кода**:
```vue
<!-- ❌ Старый способ (ИЗБЕГАТЬ) -->
<BaseCard class="pa-4">
  <div class="d-flex align-center mb-3">
    <v-icon size="40" color="primary">mdi-briefcase</v-icon>
    <div>
      <div class="text-h4">{{ value }}</div>
      <div class="text-subtitle-2">Label</div>
    </div>
  </div>
  <v-progress-linear :model-value="progress" height="4" />
</BaseCard>

<!-- ✅ Новый способ (РЕКОМЕНДУЕТСЯ) -->
<StatsCard
  icon="mdi-briefcase"
  icon-color="primary"
  label="Label"
  :value="value"
  :progress-value="progress"
/>
```

**См. также**:
- [STATS_UNIFICATION_SUMMARY.md](../../docs/implementation/STATS_UNIFICATION_SUMMARY.md) - Детальная документация
- [STATS_QUICK_REFERENCE.md](../../frontend-vue/STATS_QUICK_REFERENCE.md) - Быстрый справочник

---

### 1.3 ConfirmDeleteDialog

**Файл**: [src/components/common/ConfirmDeleteDialog.vue](../../frontend-vue/src/components/common/ConfirmDeleteDialog.vue)

**Назначение**: Универсальный диалог подтверждения удаления с поддержкой одиночного и массового удаления.

**⚠️ Week 6 Phase 1**: Создан для CRUD операций с профилями

**Props**:
```typescript
interface Props {
  modelValue: boolean                // v-model для открытия/закрытия
  items: UnifiedPosition[] | null    // Элементы для удаления
  requireConfirmation?: boolean      // Требовать checkbox подтверждения (default: false)
  maxDisplayItems?: number           // Макс. элементов в списке (default: 5)
}
```

**Events**:
```typescript
{
  'update:modelValue': [value: boolean]
  'delete': []  // Parent обрабатывает фактическое удаление
}
```

**Примеры использования**:

```vue
<!-- Одиночное удаление -->
<ConfirmDeleteDialog
  v-model="showDialog"
  :items="[selectedProfile]"
  @delete="handleDelete"
/>

<!-- Массовое удаление с обязательным подтверждением -->
<ConfirmDeleteDialog
  v-model="showDialog"
  :items="selectedProfiles"
  :require-confirmation="selectedProfiles.length > 1"
  @delete="handleBulkDelete"
/>

<!-- С ограничением отображаемых элементов -->
<ConfirmDeleteDialog
  v-model="showDialog"
  :items="manyItems"
  :max-display-items="3"
  @delete="handleDelete"
/>
```

**Особенности**:
- ✅ Поддержка одиночного и массового удаления
- ✅ Отображение деталей удаляемых элементов (название, департамент, сотрудник)
- ✅ Опциональный checkbox подтверждения для массовых операций
- ✅ Информация о soft delete (архивирование)
- ✅ Превью списка с ограничением количества
- ✅ Disabled кнопок во время удаления
- ✅ Адаптивный текст (1 профиль / N профилей)

**Когда использовать**:
- ✅ **ВСЕГДА** для подтверждения деструктивных действий
- ✅ Удаление профилей, позиций, записей
- ✅ Bulk операции с подтверждением
- ✅ Архивирование данных

**Когда НЕ использовать**:
- ❌ Для simple confirmations (используйте `v-dialog` с кнопками)
- ❌ Для non-destructive действий
- ❌ Когда нужна custom структура dialog

**UI/UX Guidelines**:
- Красный header с иконкой предупреждения
- Warning icon (64px) в центре
- Информация об архивировании (может быть восстановлено)
- Checkbox подтверждения для массовых операций (>1 элемент)
- Показывать максимум 5 элементов, остальные "и еще N..."

**Технические детали**:
- Блокировка закрытия во время удаления (`persistent + disabled`)
- Auto-reset состояния при закрытии (confirmed, deleting)
- Parent отвечает за фактическое удаление через event
- Null-safe отображение данных (`items[0]?.position_name`)

---

### 1.4 BaseThemedDialog

**Файл**: [src/components/common/BaseThemedDialog.vue](../../frontend-vue/src/components/common/BaseThemedDialog.vue)

**Назначение**: Базовый wrapper для Vuetify v-dialog с автоматической поддержкой тем (light/dark mode).

**⚠️ Week 6 Phase 1**: Создан для решения проблемы teleportation в Vuetify 3, где диалоги теряют контекст темы.

**Props**:
```typescript
interface Props {
  modelValue: boolean                // v-model для открытия/закрытия
}

// + все props от v-dialog (через $attrs)
```

**Events**:
```typescript
{
  'update:modelValue': [value: boolean]
}
```

**Slots**:
```typescript
{
  default: () => void        // Содержимое диалога (обычно v-card)
}
```

**Примеры использования**:

```vue
<!-- Простой диалог -->
<BaseThemedDialog v-model="showDialog" max-width="600px">
  <v-card>
    <v-card-title>Мой диалог</v-card-title>
    <v-card-text>Содержимое</v-card-text>
  </v-card>
</BaseThemedDialog>

<!-- С persistent и другими v-dialog props -->
<BaseThemedDialog
  v-model="showDialog"
  max-width="800px"
  persistent
  scrollable
>
  <v-card>
    <v-card-title>Важный диалог</v-card-title>
    <v-card-text>Нельзя закрыть кликом вне</v-card-text>
    <v-card-actions>
      <v-btn @click="showDialog = false">Закрыть</v-btn>
    </v-card-actions>
  </v-card>
</BaseThemedDialog>

<!-- Вместо прямого использования v-dialog -->
<!-- ❌ СТАРЫЙ способ (без темы) -->
<v-dialog v-model="showDialog">
  <v-card>Content</v-card>
</v-dialog>

<!-- ✅ НОВЫЙ способ (с темой) -->
<BaseThemedDialog v-model="showDialog">
  <v-card>Content</v-card>
</BaseThemedDialog>
```

**Проблема, которую решает**:
В Vuetify 3 диалоги используют телепортацию и рендерятся вне основного DOM дерева приложения. Это приводит к потере контекста темы из Vue's provide/inject. В результате:
- Диалоги не реагируют на смену темы (light ↔ dark)
- CSS классы вроде `bg-surface-variant` не работают реактивно
- Цвета могут быть неправильными

**Решение**:
Компонент явно передает текущую тему через `:theme="theme.global.name.value"` prop, обеспечивая реактивное обновление при смене темы.

**Технические детали**:
```typescript
// Внутренняя реализация
import { useTheme } from 'vuetify'

const theme = useTheme()

// Binding: :theme="theme.global.name.value"
// Это обеспечивает reactivity при смене темы
```

**Когда использовать**:
- ✅ **ВСЕГДА** вместо прямого `v-dialog` для новых компонентов
- ✅ При рефакторинге существующих диалогов
- ✅ Когда диалог должен поддерживать обе темы
- ✅ Для модальных окон с формами, контентом, подтверждениями

**Когда НЕ использовать**:
- ❌ Для non-modal overlays (используйте `v-menu`, `v-tooltip`)
- ❌ Если диалог уже правильно работает с темами (но лучше мигрировать для единообразия)

**Архитектурный паттерн**:
Этот компонент инкапсулирует паттерн темизации, устраняя необходимость дублировать `useTheme()` + `:theme` в каждом диалоге. Следует принципу DRY (Don't Repeat Yourself).

**Миграция существующих диалогов**:
1. Заменить `<v-dialog>` на `<BaseThemedDialog>`
2. Удалить `const theme = useTheme()` из <script setup>
3. Удалить `:theme="theme.global.name.value"` из template
4. Убедиться что v-model и другие props работают (передаются через $attrs)

**См. также**:
- `.memory_bank/patterns/theme_dialog_pattern.md` - Детали паттерна темизации
- [ProfileViewerModal.vue](../../frontend-vue/src/components/profiles/ProfileViewerModal.vue) - Пример использования (TODO: мигрировать)
- [ProfileEditModal.vue](../../frontend-vue/src/components/profiles/ProfileEditModal.vue) - Пример использования (TODO: мигрировать)

---

## 2. Generator Components (Генератор)

### 2.1 OrganizationTree

**Файл**: [src/components/generator/OrganizationTree.vue](../../frontend-vue/src/components/generator/OrganizationTree.vue)

**Назначение**: Интерактивное дерево организационной структуры с поддержкой выбора позиций.

**Props**:
```typescript
interface Props {
  items: TreeItem[]             // Иерархия подразделений
  modelValue: SearchableItem[]  // v-model для выбранных позиций
  loading?: boolean
  showSelection?: boolean       // Показывать чекбоксы
  activatable?: boolean         // Разрешить активацию (клик)
  openAll?: boolean             // Раскрыть все узлы
}

interface TreeItem {
  id: string
  name: string
  type: 'division' | 'block' | 'department' | 'unit'
  positions?: SearchableItem[]
  children?: TreeItem[]
  profile_count?: number
  total_positions?: number
}
```

**Events**:
```typescript
{
  'update:modelValue': [items: SearchableItem[]]
  'select': [items: SearchableItem[]]
  'activate': [node: TreeItem]
}
```

**Примеры использования**:

```vue
<!-- Выбор нескольких позиций -->
<OrganizationTree
  v-model="selectedPositions"
  :items="treeItems"
  :loading="loading"
  show-selection
  @select="handleSelection"
/>

<!-- Просмотр структуры (без выбора) -->
<OrganizationTree
  :items="treeItems"
  :show-selection="false"
  activatable
  @activate="handleNodeClick"
/>

<!-- Все узлы раскрыты -->
<OrganizationTree
  v-model="selected"
  :items="treeItems"
  open-all
/>
```

**Особенности**:
- ✅ Поддержка v-model для двустороннего биндинга
- ✅ Множественный выбор чекбоксами
- ✅ Показывает количество профилей (`profile_count`)
- ✅ Icons для разных типов узлов
- ✅ BUG-10 Fix: Предотвращает infinite reactive loop

**Когда использовать**:
- ✅ Выбор подразделений/позиций из оргструктуры
- ✅ Навигация по иерархии организации
- ✅ Bulk операции с позициями
- ✅ Просмотр структуры компании

**Когда НЕ использовать**:
- ❌ Для простых списков (используйте `v-select`)
- ❌ Когда нужен flat список без иерархии

---

### 2.2 PositionSearchAutocomplete

**Файл**: [src/components/generator/PositionSearchAutocomplete.vue](../../frontend-vue/src/components/generator/PositionSearchAutocomplete.vue)

**Назначение**: Умный поиск позиций с fuzzy matching и приоритизацией результатов.

**Props**:
```typescript
interface Props {
  modelValue: SearchableItem | null  // v-model
  disabled?: boolean
  maxResults?: number  // default: 50
}

interface SearchableItem {
  position_id: string
  position_name: string
  department_name: string
  department_path: string  // "Блок > Отдел > Юнит"
  block?: string
  business_unit?: string
  profile_exists: boolean
}
```

**Events**:
```typescript
{
  'update:modelValue': [item: SearchableItem | null]
  'select': [item: SearchableItem]
}
```

**Примеры использования**:

```vue
<!-- Базовый поиск -->
<PositionSearchAutocomplete
  v-model="selectedPosition"
  @select="handleSelect"
/>

<!-- С ограничением результатов -->
<PositionSearchAutocomplete
  v-model="position"
  :max-results="10"
/>

<!-- Disabled состояние -->
<PositionSearchAutocomplete
  v-model="position"
  :disabled="isLoading"
/>
```

**Особенности**:
- ✅ **Fuzzy search** через Fuse.js
- ✅ **Debounce** 300ms для оптимизации
- ✅ **Weighted search**:
  - Название позиции (вес 2.0)
  - Business unit (вес 1.5)
  - Department path (вес 1.0)
- ✅ Показывает индикатор наличия профиля
- ✅ Показывает полный путь подразделения
- ✅ Минимум 2 символа для поиска

**Когда использовать**:
- ✅ Быстрый поиск одной позиции
- ✅ Формы с выбором позиции
- ✅ Фильтры по позициям

**Когда НЕ использовать**:
- ❌ Множественный выбор (используйте `OrganizationTree`)
- ❌ Когда нужен выбор по иерархии

---

### 2.3 GenerationProgressTracker

**Файл**: [src/components/generator/GenerationProgressTracker.vue](../../frontend-vue/src/components/generator/GenerationProgressTracker.vue)

**Назначение**: Отображение прогресса текущих задач генерации.

**Props**:
```typescript
interface Props {
  tasks: Map<string, TaskState>
  maxVisible?: number  // default: 5
}

interface TaskState {
  task_id: string
  position_name: string
  department: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number  // 0-100
  result?: GenerationResult
  error?: string
}
```

**Events**:
```typescript
{
  'view-result': [taskId: string]
  'retry': [taskId: string]
  'dismiss': [taskId: string]
}
```

**Примеры использования**:

```vue
<GenerationProgressTracker
  :tasks="generatorStore.activeTasks"
  :max-visible="3"
  @view-result="handleViewResult"
  @retry="handleRetry"
/>
```

**Особенности**:
- ✅ Показывает прогресс-бар для running задач
- ✅ Разные цвета для статусов
- ✅ Автоматический dismiss для completed
- ✅ Кнопка retry для failed

**Когда использовать**:
- ✅ Tracking долгих асинхронных операций
- ✅ Показ прогресса генерации профилей
- ✅ Batch операции

---

### 2.4 BrowseTreeTab

**Файл**: [src/components/generator/BrowseTreeTab.vue](../../frontend-vue/src/components/generator/BrowseTreeTab.vue)

**Назначение**: Tab для выбора позиций через дерево организации.

**Внутренние компоненты**:
- `OrganizationTree` - Дерево выбора
- Кнопки управления (Очистить, Генерировать)

**Когда использовать**:
- ✅ В составе `GeneratorView` как tab
- ⚠️ НЕ переиспользуйте отдельно - используйте `OrganizationTree` напрямую

---

### 2.5 QuickSearchTab

**Файл**: [src/components/generator/QuickSearchTab.vue](../../frontend-vue/src/components/generator/QuickSearchTab.vue)

**Назначение**: Tab для быстрого поиска и генерации одной позиции.

**Внутренние компоненты**:
- `PositionSearchAutocomplete` - Поиск
- Кнопка генерации

**Когда использовать**:
- ✅ В составе `GeneratorView` как tab
- ⚠️ НЕ переиспользуйте отдельно - используйте `PositionSearchAutocomplete` напрямую

---

## 3. Profiles Components (Профили)

### 3.1 PositionsTable

**Файл**: [src/components/profiles/PositionsTable.vue](../../frontend-vue/src/components/profiles/PositionsTable.vue)

**Назначение**: Таблица позиций с профилями, поддержкой фильтрации и сортировки.

**Props**:
```typescript
interface Props {
  positions: PositionWithProfile[]
  loading?: boolean
  selectable?: boolean
}

interface PositionWithProfile {
  position_id: string
  position_name: string
  department_name: string
  profile_exists: boolean
  profile_count?: number
  latest_profile?: ProfileData
  created_at?: string
}
```

**Events**:
```typescript
{
  'view-profile': [positionId: string, profileId: string]
  'select': [positionIds: string[]]
  'generate': [positionId: string]
}
```

**Особенности**:
- ✅ Vuetify data-table с пагинацией
- ✅ Сортировка по колонкам
- ✅ Фильтрация (поиск)
- ✅ Badge для количества версий профиля
- ✅ Кнопки действий (View, Generate)

**Примеры использования**:

```vue
<PositionsTable
  :positions="profilesStore.positions"
  :loading="profilesStore.isLoading"
  selectable
  @view-profile="handleView"
  @generate="handleGenerate"
/>
```

**Когда использовать**:
- ✅ Списки позиций с профилями
- ✅ Управление профилями (CRUD)
- ✅ Bulk операции над профилями

**Тестирование** (Week 6.5 Phase 1):
- ✅ **Unit tests**: [tests/components/PositionsTable.spec.ts](../../frontend-vue/tests/components/PositionsTable.spec.ts)
- ✅ **37 tests** covering data logic, permissions, state validation
- ✅ **Focus**: Type safety, business logic, store integration
- ⚠️ **Note**: Tests avoid Vuetify rendering to prevent test environment issues

---

### 3.2 ProfileContent

**Файл**: [src/components/profiles/ProfileContent.vue](../../frontend-vue/src/components/profiles/ProfileContent.vue)

**Назначение**: Красивое отображение содержимого профиля должности.

**Props**:
```typescript
interface Props {
  profile: ProfileData
  loading?: boolean
}

interface ProfileData {
  position_name: string
  department: string
  description?: string
  responsibilities?: Responsibility[]
  competencies?: Competency[]
  requirements?: Requirements
  skills?: Skills
  education?: Education
  experience?: Experience
}
```

**Особенности**:
- ✅ Адаптивная структура секций
- ✅ Icons для каждой секции
- ✅ Nested списки для компетенций
- ✅ HTML content support (v-html)

**Примеры использования**:

```vue
<!-- В модальном окне -->
<v-dialog v-model="dialog">
  <ProfileContent
    :profile="selectedProfile"
    :loading="loading"
  />
</v-dialog>

<!-- В карточке -->
<BaseCard title="Профиль должности">
  <ProfileContent :profile="profile" />
</BaseCard>
```

**Когда использовать**:
- ✅ Просмотр полного профиля
- ✅ Модальные окна с профилем
- ✅ Печать профилей

---

### 3.3 ProfileViewerModal

**Файл**: [src/components/profiles/ProfileViewerModal.vue](../../frontend-vue/src/components/profiles/ProfileViewerModal.vue)

**Назначение**: Полноэкранное модальное окно для просмотра профиля.

**Props**:
```typescript
interface Props {
  modelValue: boolean  // v-model для открытия/закрытия
  positionId: string | null
  profileId: string | null
}
```

**Events**:
```typescript
{
  'update:modelValue': [value: boolean]
  'close': []
}
```

**Внутренние компоненты**:
- `ProfileContent` - Отображение содержимого
- Toolbar с кнопками (Закрыть, Печать, Export)

**Примеры использования**:

```vue
<ProfileViewerModal
  v-model="showModal"
  :position-id="selectedPositionId"
  :profile-id="selectedProfileId"
  @close="handleClose"
/>
```

**Когда использовать**:
- ✅ Просмотр профиля из списка
- ✅ Когда нужна fullscreen view

**Когда НЕ использовать**:
- ❌ Встроенный просмотр (используйте `ProfileContent`)

---

### 3.4 DateRangeFilter

**Файл**: [src/components/profiles/DateRangeFilter.vue](../../frontend-vue/src/components/profiles/DateRangeFilter.vue)

**Назначение**: Компонент для выбора диапазона дат с быстрыми пресетами.

**⚠️ Week 6 Phase 2**: Создан для расширенной фильтрации профилей

**Props**:
```typescript
interface Props {
  modelValue: DateRangeFilter | null  // v-model для двустороннего биндинга
}

interface DateRangeFilter {
  type: 'created' | 'updated'  // Тип даты (создание или обновление)
  from: string | null          // ISO 8601 дата (YYYY-MM-DD)
  to: string | null            // ISO 8601 дата (YYYY-MM-DD)
}
```

**Events**:
```typescript
{
  'update:modelValue': [value: DateRangeFilter | null]
}
```

**Примеры использования**:
```vue
<!-- Базовое использование -->
<DateRangeFilter
  v-model="dateRange"
  @update:model-value="handleDateChange"
/>

<!-- В составе FilterBar -->
<DateRangeFilter
  v-model="localFilters.dateRange"
  @update:model-value="onFilterChange"
/>
```

**Особенности**:
- ✅ Быстрые пресеты: Последние 7/30/90 дней, Все время, Произвольный
- ✅ Выбор типа даты (создание/обновление) через toggle buttons
- ✅ Native HTML5 date inputs для выбора дат
- ✅ Отображение выбранного периода в читаемом формате (DD.MM.YYYY)
- ✅ Dark theme support через CSS variables
- ✅ Автоматический расчет дат для пресетов
- ✅ Валидация диапазона (from ≤ to)

**Когда использовать**:
- ✅ Фильтрация по дате создания
- ✅ Фильтрация по дате обновления
- ✅ Любые временные диапазоны
- ✅ Формы с датами

**Когда НЕ использовать**:
- ❌ Для выбора одной даты (используйте v-text-field с type="date")
- ❌ Для времени (компонент работает только с датами)

**Технические детали**:
- Размер файла: 298 строк (под лимит 300 ✅)
- Использует Vuetify v-menu для dropdown
- ISO 8601 формат для дат (YYYY-MM-DD)
- Автоматический clear при выборе "Все время"

---

### 3.5 FilterPresets ❌ DELETED

**Файл**: ~~[src/components/profiles/FilterPresets.vue](../../frontend-vue/src/components/profiles/FilterPresets.vue)~~ (DELETED)

**Статус**: ❌ **DELETED** - Удалено в Week 6.5 Phase 1 (2025-10-27)

**Назначение**: Управление пресетами фильтров (сохранение, загрузка, удаление).

**⚠️ Week 6 Phase 2**: Создан для быстрого применения часто используемых фильтров
**⚠️ UX Simplification**: Удален из UI по feedback пользователя ("странная функция", "не нужна")

**User Feedback** (2025-10-27):
> "Выбрать пресет выбирается из стиля. И вообще странная функция. Давай ее удалим. Не нужна она."

**Props**: Нет (работает напрямую с store)

**Events**: Нет (изменяет store напрямую)

**Примеры использования**:
```vue
<!-- REMOVED FROM UI - Code preserved for potential future use -->
<!-- В составе FilterBar (больше НЕ используется) -->
<FilterPresets />
```

**Особенности**:
- ✅ **Готовые пресеты**:
  - "Недавно сгенерированные" (последние 7 дней)
  - "Высокое качество" (>80%)
  - "Не заполненные" (без профилей)
- ✅ **Пользовательские пресеты** (макс. 10):
  - Сохранение текущих фильтров
  - Редактирование названия
  - Выбор иконки и цвета
  - Удаление
- ✅ Индикатор активного пресета
- ✅ Хранение в localStorage
- ✅ Валидация названий (уникальность, длина ≤50)

**Deletion Details (Week 6.5 Phase 1)**:
- ❌ **Удалено**: FilterPresets.vue (432 строки)
- ❌ **Удалено**: utils/filterPresets.ts (345 строк)
- ❌ **Удалено**: types/presets.ts (56 строк)
- 📊 **Итого удалено**: 833 строки мертвого кода

**Если потребуется в будущем**:
- ✅ Добавить в меню настроек
- ✅ Добавить в sidebar
- ✅ Использовать URL query params вместо localStorage
- ✅ Показывать активный preset в header FilterBar

**Когда НЕ использовать** (причины удаления):
- ❌ Плохая discoverability (спрятано в dropdown)
- ❌ Излишняя сложность для простых фильтров
- ❌ Дублирует quick presets в DateRangeFilter
- ❌ Не соответствует стилю остального UI

**Технические детали**:
- Размер файла: 299 строк (под лимит 300 ✅)
- localStorage ключ: `hr_filter_presets`
- Версионирование схемы для миграций
- Максимум 10 пользовательских пресетов
- Готовые пресеты нельзя удалить

**UI/UX Guidelines**:
- Dropdown меню с двумя секциями (готовые/пользовательские)
- Иконки и цвета для визуального различия
- Диалог сохранения с preview выбранных иконки и цвета
- Подтверждение удаления для безопасности

---

### 3.6 ProfileEditModal

**Файл**: [src/components/profiles/ProfileEditModal.vue](../../frontend-vue/src/components/profiles/ProfileEditModal.vue)

**Назначение**: Модальное окно для редактирования метаданных профиля (employee_name, status).

**⚠️ Week 6 Phase 1**: Создан для CRUD операций

**Props**:
```typescript
interface Props {
  modelValue: boolean               // v-model для открытия/закрытия
  profile: UnifiedPosition | null   // Профиль для редактирования
}
```

**Events**:
```typescript
{
  'update:modelValue': [value: boolean]
  save: [data: { employee_name?: string; status?: PositionStatus }]
}
```

**Примеры использования**:

```vue
<!-- Редактирование профиля -->
<ProfileEditModal
  v-model="showEditDialog"
  :profile="selectedPosition"
  @save="handleSaveProfile"
/>

<!-- С автоматическим закрытием после сохранения -->
<template>
  <ProfileEditModal
    v-model="editDialog"
    :profile="currentProfile"
    @save="async (data) => {
      await updateProfile(data)
      editDialog = false
    }"
  />
</template>
```

**Особенности**:
- ✅ Редактируемые поля: employee_name (текст), status (select)
- ✅ Read-only отображение: position_name, department_name
- ✅ Валидация employee_name (кириллица, пробелы, дефисы, макс 200 символов)
- ✅ Disabled кнопка Сохранить при отсутствии изменений
- ✅ Loading state во время сохранения
- ✅ Блокировка закрытия во время сохранения (`persistent`)
- ✅ Auto-reset формы при открытии/закрытии
- ✅ Информационное сообщение о Week 8 inline editing

**Доступные статусы**:
```typescript
[
  { label: 'Сгенерирован', value: 'generated', icon: 'mdi-check-circle', color: 'success' },
  { label: 'Генерация', value: 'generating', icon: 'mdi-progress-clock', color: 'warning' },
  { label: 'Архивирован', value: 'archived', icon: 'mdi-archive', color: 'grey' }
]
```

**Validation Rules**:
```typescript
// Employee Name
- Optional field (можно оставить пустым)
- Только кириллица, пробелы и дефисы: /^[А-Яа-яЁё\s-]+$/
- Максимум 200 символов

// Status
- Required field
- Один из: generated, generating, archived
```

**Когда использовать**:
- ✅ Редактирование метаданных профиля
- ✅ Изменение имени сотрудника
- ✅ Смена статуса профиля (архивация, восстановление)

**Когда НЕ использовать**:
- ❌ Для редактирования содержимого профиля (используйте inline editing в Week 8)
- ❌ Для массового редактирования (добавить в Week 6 Phase 4)
- ❌ Для создания нового профиля (другой компонент)

**Технические детали**:
- Использует `v-form` с валидацией
- Отправляет только измененные поля (partial update)
- Parent обрабатывает сохранение и маппинг статусов (PositionStatus → ProfileStatus)
- Watch на `modelValue` и `profile` для синхронизации

---

### 3.5 FilterBar

**Файл**: [src/components/profiles/FilterBar.vue](../../frontend-vue/src/components/profiles/FilterBar.vue)

**Назначение**: Панель фильтров для списка профилей.

**Props**:
```typescript
interface Props {
  departments: string[]
  statuses: ProfileStatus[]
  modelValue: FilterState
}

interface FilterState {
  search: string
  departments: string[]
  statuses: ProfileStatus[]
  dateRange: [string, string] | null
}
```

**Events**:
```typescript
{
  'update:modelValue': [filters: FilterState]
  'reset': []
}
```

**Примеры использования**:

```vue
<FilterBar
  v-model="filters"
  :departments="availableDepartments"
  :statuses="['active', 'draft']"
  @reset="handleReset"
/>
```

**Когда использовать**:
- ✅ Фильтрация списков
- ✅ Поиск с множественными критериями

---

### 3.6 ProfileVersionsPanel

**Файл**: [src/components/profiles/ProfileVersionsPanel.vue](../../frontend-vue/src/components/profiles/ProfileVersionsPanel.vue)

**Назначение**: Панель для отображения истории версий профиля с timeline UI.

**⚠️ Week 6 Phase 3**: Создан для управления версиями профилей

**Props**:
```typescript
interface Props {
  versions: ProfileVersion[]  // Список версий профиля
  loading?: boolean           // Состояние загрузки
  error?: string | null       // Сообщение об ошибке
}

interface ProfileVersion {
  version_number: number
  created_at: string
  created_by_username: string
  version_type: 'generated' | 'regenerated' | 'edited'
  validation_score: number | null
  completeness_score: number | null
  is_current: boolean
}
```

**Events**:
```typescript
{
  'set-active': [versionNumber: number]                          // Активировать версию
  'download': [versionNumber: number, format: 'json' | 'md' | 'docx']  // Скачать версию
  'delete': [versionNumber: number]                              // Удалить версию
  'retry': []                                                     // Повторить загрузку
}
```

**Примеры использования**:

```vue
<!-- Базовое использование -->
<ProfileVersionsPanel
  :versions="versions"
  :loading="versionsLoading"
  :error="versionsError"
  @set-active="handleSetActive"
  @download="handleDownload"
  @delete="handleDelete"
  @retry="loadVersions"
/>

<!-- С состоянием загрузки (skeleton loaders) -->
<ProfileVersionsPanel
  :versions="[]"
  :loading="true"
/>

<!-- С ошибкой -->
<ProfileVersionsPanel
  :versions="[]"
  :error="'Не удалось загрузить версии'"
  @retry="retryLoad"
/>
```

**Особенности**:
- ✅ **v-timeline** UI для визуализации истории
- ✅ **Skeleton loaders** вместо спиннера при загрузке
- ✅ Показывает текущую активную версию с badge "Текущая"
- ✅ Показывает оригинальную версию (v1) с badge "Оригинал"
- ✅ Иконки по типу версии:
  - `mdi-magic-staff` - Сгенерирована
  - `mdi-refresh` - Регенерирована
  - `mdi-pencil` - Отредактирована
- ✅ Прогресс-бары для качества и полноты профиля:
  - Зеленый ≥ 80%
  - Оранжевый 60-79%
  - Красный < 60%
- ✅ Dropdown меню с действиями:
  - Сделать текущей (только для неактивных версий)
  - Скачать (JSON, Markdown, Word)
  - Удалить (только если не текущая и не последняя)
- ✅ Форматирование даты: "DD.MM.YYYY HH:mm"
- ✅ Dark theme support
- ✅ Responsive design

**Когда использовать**:
- ✅ В ProfileViewerModal на вкладке "Версии"
- ✅ Везде где нужна история изменений профиля
- ✅ Audit trail для профилей

**Когда НЕ использовать**:
- ❌ Для истории других сущностей (создайте специализированный компонент)
- ❌ Если не нужны действия с версиями (используйте простой v-timeline)

**Технические детали**:
- Размер файла: 262 строки (под лимит 300 ✅)
- Использует Vuetify v-timeline для временной шкалы
- v-skeleton-loader для loading state (3 элемента)
- Parent отвечает за API вызовы через события
- Все действия делегируются в parent через events

**UI/UX Guidelines**:
- Timeline всегда слева (align="start")
- Версии отсортированы от новых к старым (desc)
- Compact density для экономии места
- Номер версии в левой колонке (opposite slot)
- Tonal variant для текущей версии (выделение)
- Иконка и цвет точки соответствуют типу версии

---

## 4. Layout Components (Layout)

### 4.1 AppLayout

**Файл**: [src/components/layout/AppLayout.vue](../../frontend-vue/src/components/layout/AppLayout.vue)

**Назначение**: Главный layout приложения с навигацией.

**Структура**:
```
v-app
  AppHeader
  v-main
    v-container
      <router-view>  <!-- Контент страниц -->
```

**Когда использовать**:
- ✅ Автоматически используется роутером для authenticated страниц
- ⚠️ НЕ используйте вручную

---

### 4.2 AppHeader

**Файл**: [src/components/layout/AppHeader.vue](../../frontend-vue/src/components/layout/AppHeader.vue)

**Назначение**: Шапка приложения с навигацией и user menu.

**Особенности**:
- ✅ Responsive drawer menu
- ✅ User menu с logout
- ✅ Active route highlighting

**Когда использовать**:
- ✅ Автоматически используется в `AppLayout`
- ⚠️ НЕ используйте отдельно

---

## 5. Composables (Переиспользуемая логика)

### 5.1 useTaskStatus

**Файл**: [src/composables/useTaskStatus.ts](../../frontend-vue/src/composables/useTaskStatus.ts)

**Назначение**: Polling механизм для отслеживания статуса задач.

**API**:
```typescript
interface UseTaskStatus {
  startPolling: (taskId: string, onUpdate: (status: TaskStatus) => void) => void
  stopPolling: (taskId: string) => void
  stopAll: () => void
}

const { startPolling, stopPolling, stopAll } = useTaskStatus()
```

**Примеры использования**:

```typescript
// В store или компоненте
const { startPolling, stopPolling } = useTaskStatus()

// Запуск polling
startPolling(taskId, async (status) => {
  if (status.state === 'completed') {
    await loadResult(taskId)
    stopPolling(taskId)
  }
})

// Остановка при unmount
onBeforeUnmount(() => {
  stopAll()
})
```

**Особенности**:
- ✅ Автоматический polling с интервалом
- ✅ Управление lifecycle (start/stop)
- ✅ Cleanup при unmount

**Когда использовать**:
- ✅ Долгие асинхронные операции
- ✅ Background tasks
- ✅ Real-time updates

---

### 5.2 useProfileVersions

**Файл**: [src/composables/useProfileVersions.ts](../../frontend-vue/src/composables/useProfileVersions.ts)

**Назначение**: Управление версиями профиля (загрузка, активация, скачивание, удаление).

**⚠️ Week 6 Phase 3**: Создан для функционала версионирования профилей

**API**:
```typescript
interface UseProfileVersionsReturn {
  versions: Ref<ProfileVersion[]>
  versionsLoading: Ref<boolean>
  versionsError: Ref<string | null>
  snackbar: Ref<SnackbarState>
  loadVersions: () => Promise<void>
  handleSetActive: (versionNumber: number) => Promise<void>
  handleVersionDownload: (versionNumber: number, format: 'json' | 'md' | 'docx') => Promise<void>
  handleDeleteVersion: (versionNumber: number) => Promise<void>
}

const {
  versions,
  versionsLoading,
  versionsError,
  snackbar,
  loadVersions,
  handleSetActive,
  handleVersionDownload,
  handleDeleteVersion
} = useProfileVersions(
  profileId,      // ComputedRef<string | undefined>
  activeTab,      // Ref<string>
  onVersionChanged // Optional callback
)
```

**Примеры использования**:

```typescript
// В компоненте ProfileViewerModal
const profileId = computed(() => props.profile?.id)
const activeTab = ref('content')

const {
  versions,
  versionsLoading,
  versionsError,
  snackbar,
  loadVersions,
  handleSetActive,
  handleVersionDownload,
  handleDeleteVersion
} = useProfileVersions(profileId, activeTab, async () => {
  await reloadProfile()
})

// Автоматическая загрузка при переключении на вкладку "versions"
watch(activeTab, (newTab) => {
  if (newTab === 'versions' && profileId.value) {
    loadVersions()
  }
})
```

**Особенности**:
- ✅ Реактивное state management (versions, loading, error)
- ✅ Интегрированный snackbar для уведомлений
- ✅ Автоматический reload профиля после активации версии
- ✅ Автоматический reload списка версий после удаления
- ✅ Специфичная обработка ошибок (VersionNotFoundError, etc.)
- ✅ **Analytics tracking** для всех операций
- ✅ Watch механизм для lazy loading при переключении вкладок
- ✅ Переключение на вкладку "content" после активации версии

**Когда использовать**:
- ✅ В ProfileViewerModal для управления версиями
- ✅ Везде где нужна работа с версиями профилей
- ✅ Для инкапсуляции версионной логики из компонентов

**Когда НЕ использовать**:
- ❌ Если нужна только часть функционала (используйте profile.service напрямую)
- ❌ Для других сущностей (создайте специализированный composable)

**Технические детали**:
- Размер: 295 строк (под лимит 500 ✅)
- Использует специфичные error классы для типобезопасной обработки
- Интегрируется с useAnalytics для tracking
- 100% test coverage (41 unit tests)

---

### 5.3 useAnalytics

**Файл**: [src/composables/useAnalytics.ts](../../frontend-vue/src/composables/useAnalytics.ts)

**Назначение**: Tracking пользовательских событий и взаимодействий.

**⚠️ Week 6 Phase 3**: Создан для analytics версионных операций, готов для расширения

**API**:
```typescript
interface UseAnalyticsReturn {
  trackVersionListViewed: (profileId: string, totalVersions: number, currentVersion: number) => void
  trackVersionActivated: (profileId: string, previousVersion: number, newVersion: number) => void
  trackVersionDownloaded: (profileId: string, versionNumber: number, format: DownloadFormat) => void
  trackVersionDeleted: (profileId: string, versionNumber: number, remainingVersions: number) => void
}

const analytics = useAnalytics()
```

**Примеры использования**:

```typescript
// Track версий
analytics.trackVersionListViewed('prof_123', 5, 3)

// Track активации
analytics.trackVersionActivated('prof_123', 2, 3)

// Track скачивания
analytics.trackVersionDownloaded('prof_123', 2, 'json')

// Track удаления
analytics.trackVersionDeleted('prof_123', 2, 4)
```

**Особенности**:
- ✅ **Extensible design** - готов для интеграции с GA4, Mixpanel, Plausible
- ✅ Development mode: логирует события в console
- ✅ Production ready: комментарии с примерами интеграции
- ✅ Environment-aware: проверяет `VITE_ANALYTICS_ENABLED`
- ✅ Type-safe события через TypeScript interfaces
- ✅ Timestamp для каждого события
- ✅ Structured event properties

**Когда использовать**:
- ✅ Tracking user interactions
- ✅ Monitoring feature usage
- ✅ A/B testing metrics
- ✅ Product analytics

**Когда НЕ использовать**:
- ❌ Для error tracking (используйте logger)
- ❌ Для server-side analytics (используйте backend)

**Технические детали**:
- Размер: 242 строки (под лимит 500 ✅)
- Использует типы из `types/analytics.ts`
- TODO markers для platform integration:
  ```typescript
  // Google Analytics 4:
  // gtag('event', event.event, event.properties)

  // Mixpanel:
  // mixpanel.track(event.event, event.properties)

  // Plausible:
  // plausible(event.event, { props: event.properties })
  ```

**Будущие расширения**:
- Добавить tracking для profile generation
- Добавить tracking для dashboard interactions
- Добавить tracking для filter usage
- Интегрировать с выбранной analytics платформой

---

## 6. Utilities (Утилиты)

### 6.1 filterPresets.ts

**Файл**: [src/utils/filterPresets.ts](../../frontend-vue/src/utils/filterPresets.ts)

**Назначение**: Управление пресетами фильтров в localStorage (сохранение, загрузка, валидация).

**⚠️ Week 6 Phase 2**: Создан для backend пресетов FilterPresets компонента

**Основные функции**:
```typescript
// Загрузка пресетов
function loadPresets(): FilterPresetsStorage

// Сохранение пресетов
function savePresets(storage: FilterPresetsStorage): void

// Создание нового пресета
function createPreset(data: PresetCreateData): FilterPreset

// Добавление пресета
function addPreset(preset: FilterPreset): FilterPresetsStorage

// Обновление пресета
function updatePreset(presetId: string, updates: Partial<FilterPreset>): FilterPresetsStorage

// Удаление пресета
function deletePreset(presetId: string): FilterPresetsStorage

// Получить все пресеты (готовые + пользовательские)
function getAllPresets(): FilterPreset[]

// Получить пресет по ID
function getPreset(presetId: string): FilterPreset | null

// Установить активный пресет
function setActivePreset(presetId: string | null): void

// Получить ID активного пресета
function getActivePresetId(): string | null

// Проверка доступности названия
function isPresetNameAvailable(name: string, excludeId?: string): boolean

// Экспорт пресетов (для бэкапа)
function exportPresets(): string

// Импорт пресетов (для восстановления)
function importPresets(jsonString: string): FilterPresetsStorage

// Очистить все пользовательские пресеты
function clearAllPresets(): void
```

**Готовые пресеты**:
```typescript
export const DEFAULT_PRESETS: DefaultPreset[] = [
  {
    id: 'preset_recently_generated',
    name: 'Недавно сгенерированные',
    description: 'Профили, созданные за последние 7 дней',
    icon: 'mdi-clock-outline',
    color: 'primary',
    createFilters: () => ({ ... })
  },
  {
    id: 'preset_high_quality',
    name: 'Высокое качество',
    description: 'Профили с качеством выше 80%',
    icon: 'mdi-star',
    color: 'success',
    createFilters: () => ({ ... })
  },
  {
    id: 'preset_incomplete',
    name: 'Не заполненные',
    description: 'Позиции без профилей',
    icon: 'mdi-alert-circle-outline',
    color: 'warning',
    createFilters: () => ({ ... })
  }
]
```

**Схема хранения**:
```typescript
interface FilterPresetsStorage {
  version: number              // Версия схемы (для миграций)
  presets: FilterPreset[]      // Пользовательские пресеты
  activePresetId: string | null // ID активного пресета
  maxPresets: number           // Максимум пресетов (10)
}

interface FilterPreset {
  id: string
  name: string
  filters: ProfileFilters
  created_at: string
  is_default?: boolean
  icon?: string
  color?: string
}
```

**Особенности**:
- ✅ Версионирование схемы для миграций
- ✅ Валидация данных (название, уникальность, лимит)
- ✅ Error handling с понятными сообщениями
- ✅ 3 готовых пресета (нельзя удалить)
- ✅ Максимум 10 пользовательских пресетов
- ✅ Экспорт/импорт для бэкапа
- ✅ TypeScript strict mode (0 `any` types)

**Использование**:
```typescript
import {
  loadPresets,
  createPreset,
  addPreset,
  getAllPresets
} from '@/utils/filterPresets'

// Загрузить все пресеты
const allPresets = getAllPresets()
console.log(allPresets) // [default presets + custom presets]

// Создать новый пресет
const preset = createPreset({
  name: 'IT отдел',
  filters: {
    departments: ['IT Development', 'IT Support'],
    status: 'generated'
  },
  icon: 'mdi-laptop',
  color: 'primary'
})

// Добавить в хранилище
addPreset(preset)
```

**Когда использовать**:
- ✅ Работа с пресетами фильтров
- ✅ Сохранение пользовательских настроек
- ✅ localStorage persistence
- ✅ Бэкап и восстановление настроек

**Когда НЕ использовать**:
- ❌ Для других типов данных (создайте отдельную утилиту)
- ❌ Для серверного хранения (это только для localStorage)

---

## 7. Когда создавать новый компонент?

### 6.1 Чеклист перед созданием

**ОБЯЗАТЕЛЬНО выполните все пункты**:

1. ✅ Проверили ли вы [Component Library](#содержание)?
2. ✅ Проверили ли вы `src/components/common/`?
3. ✅ Может ли существующий компонент решить задачу с минимальными изменениями?
4. ✅ Используется ли логика в 3+ местах? (Правило трёх)
5. ✅ Можно ли композировать из существующих компонентов?

### 6.2 Правило трёх

**НЕ создавайте компонент если**:
- ❌ Используется только в 1 месте
- ❌ Специфичная логика для конкретного view

**СОЗДАЙТЕ компонент если**:
- ✅ Используется в 3+ местах
- ✅ Сложная переиспользуемая логика
- ✅ Может быть полезен в будущем

### 6.3 Где создавать новый компонент?

**`src/components/common/`**:
- ✅ Базовые UI компоненты (buttons, inputs, cards)
- ✅ Используется в разных фичах
- ✅ Не зависит от бизнес-логики

**`src/components/{feature}/`**:
- ✅ Специфичные для фичи компоненты
- ✅ Используется только в рамках одной фичи
- ✅ Имеет бизнес-логику

**`src/views/`**:
- ✅ Компоненты-страницы (роуты)
- ⚠️ НЕ переиспользуются

### 6.4 Template для нового компонента

```vue
<template>
  <div class="component-name">
    <!-- Template -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// Constants
const DEFAULT_VALUE = 10

// Props
interface Props {
  value: string
  disabled?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

// Emits
const emit = defineEmits<{
  'update:value': [value: string]
  'change': [value: string]
}>()

// State
const internalValue = ref(props.value)

// Computed
const isValid = computed(() => internalValue.value.length > 0)

// Functions
function handleChange(): void {
  emit('update:value', internalValue.value)
  emit('change', internalValue.value)
}
</script>

<style scoped>
.component-name {
  /* Styles */
}
</style>
```

---

## 7. Обновление этого документа

**Когда обновлять Component Library**:

- ✅ После создания нового переиспользуемого компонента
- ✅ После добавления новых props к существующему компоненту
- ✅ После рефакторинга компонента
- ✅ После удаления/deprecated компонента

**Формат записи**:

```markdown
### X.Y ComponentName

**Файл**: [relative/path](../../actual/path)

**Назначение**: Краткое описание

**Props**:
<!-- TypeScript interface -->

**Events**:
<!-- Event definitions -->

**Примеры использования**:
<!-- Code examples -->

**Особенности**:
- ✅ Feature 1
- ✅ Feature 2

**Когда использовать**:
- ✅ Use case 1
- ✅ Use case 2

**Когда НЕ использовать**:
- ❌ Anti-pattern 1
```

---

## 8. Code Review Checklist

**При review PR с новым компонентом**:

- [ ] Проверен ли Component Library на дубликаты?
- [ ] Следует ли [Coding Standards](../guides/frontend_coding_standards.md)?
- [ ] Есть ли TypeScript типы для всех props/events?
- [ ] Есть ли JSDoc документация?
- [ ] Есть ли примеры использования?
- [ ] Компонент добавлен в Component Library?
- [ ] Размер файла < 300 строк?
- [ ] Есть ли тесты (если компонент в common/)?

---

## 📚 Связанные документы

- **[Frontend Architecture](./frontend_architecture.md)** - Архитектура приложения
- **[Frontend Coding Standards](../guides/frontend_coding_standards.md)** - Правила кода
- **[Testing Strategy](../guides/testing_strategy.md)** - Стратегия тестирования

---

**Последнее обновление**: 2025-10-27
**Версия**: 1.2
**Компонентов**: 16 переиспользуемых + 1 composable + 1 utility

**Изменения Week 6 Phase 2**:
- ✅ Добавлен `DateRangeFilter` (profiles) - Фильтр по диапазону дат
- ✅ Добавлен `FilterPresets` (profiles) - Управление пресетами фильтров
- ✅ Добавлен `filterPresets.ts` (utils) - Утилита для работы с пресетами
- ✅ Обновлен `FilterBar` (добавлены: date range, multi-select departments, quality range, presets)

**Изменения Week 6 Phase 1**:
- ✅ Добавлен `ConfirmDeleteDialog` (common)
- ✅ Добавлен `ProfileEditModal` (profiles)
- ✅ Обновлен `PositionsTable` (добавлены edit/delete/restore actions)

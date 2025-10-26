# Component Library

## Полный каталог переиспользуемых компонентов

**⚠️ КРИТИЧНО**: Читайте этот документ ПЕРЕД созданием любого нового компонента!

Этот документ содержит **полный список** всех переиспользуемых компонентов в проекте. Прежде чем создавать новый компонент, **ОБЯЗАТЕЛЬНО** проверьте, не существует ли уже подходящего.

---

## Содержание

1. [Common Components](#1-common-components-базовые) - Базовые UI компоненты
   - 1.1 BaseCard - Универсальная карточка
   - 1.2 **StatsCard** - Карточка статистики (NEW!)
2. [Generator Components](#2-generator-components-генератор) - Компоненты генератора
3. [Profiles Components](#3-profiles-components-профили) - Компоненты управления профилями
4. [Layout Components](#4-layout-components-layout) - Layout компоненты
5. [Composables](#5-composables-переиспользуемая-логика) - Переиспользуемая логика
6. [When to Create New Component](#6-когда-создавать-новый-компонент) - Руководство

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

### 3.4 FilterBar

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

## 6. Когда создавать новый компонент?

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

**Последнее обновление**: 2025-10-26
**Версия**: 1.0
**Компонентов**: 12 переиспользуемых + 1 composable

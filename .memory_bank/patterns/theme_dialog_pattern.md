# Theme Dialog Pattern - Vuetify 3 Dialog Theming

## Проблема

В Vuetify 3 компоненты `v-dialog` используют телепортацию (teleportation) для рендеринга модальных окон. Это означает, что диалоги рендерятся вне основного DOM дерева приложения (`<div id="app">`) в специальный контейнер для overlays.

### Последствия телепортации:

1. **Потеря контекста темы**: Vue's provide/inject не работает через границу телепортации
2. **CSS классы не реактивны**: Utility классы вроде `bg-surface-variant` генерируются статически и не обновляются при смене темы
3. **Некорректные цвета**: Диалоги могут отображаться в light mode даже когда приложение в dark mode

## Решение

### Паттерн 1: Explicit Theme Binding (Recommended)

Использовать `BaseThemedDialog` компонент, который инкапсулирует логику темизации:

```vue
<template>
  <BaseThemedDialog v-model="showDialog" max-width="600px">
    <v-card>
      <v-card-title>Мой диалог</v-card-title>
      <v-card-text>Содержимое автоматически получает правильную тему</v-card-text>
    </v-card>
  </BaseThemedDialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseThemedDialog from '@/components/common/BaseThemedDialog.vue'

const showDialog = ref(false)
</script>
```

**Преимущества**:
- ✅ Нет дублирования кода
- ✅ Следует принципу DRY
- ✅ Централизованная логика темизации
- ✅ Проще в поддержке

### Паттерн 2: Manual Theme Binding (Legacy)

Если по какой-то причине нельзя использовать `BaseThemedDialog`:

```vue
<template>
  <v-dialog
    :model-value="modelValue"
    :theme="theme.global.name.value"
    max-width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <!-- Dialog content -->
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useTheme } from 'vuetify'

const theme = useTheme()
</script>
```

**Недостатки**:
- ❌ Дублирование кода в каждом диалоге
- ❌ Легко забыть добавить `:theme` prop
- ❌ Больше boilerplate кода

## Reactive Styling Patterns

### ❌ ИЗБЕГАТЬ: Static CSS Classes

```vue
<!-- НЕ РАБОТАЕТ реактивно -->
<div class="bg-surface-variant">
  Этот цвет не обновится при смене темы
</div>
```

**Проблема**: Vuetify генерирует CSS классы статически во время сборки. Они не обновляются динамически при смене темы.

### ✅ ИСПОЛЬЗОВАТЬ: Vuetify Props

```vue
<!-- Работает реактивно -->
<v-sheet bg-color="surface-variant">
  Этот цвет правильно обновится при смене темы
</v-sheet>
```

**Преимущества**:
- Реактивное обновление
- Type-safe (TypeScript)
- Vuetify-native way
- Меньше кода

### ✅ ИСПОЛЬЗОВАТЬ: CSS Variables

```vue
<!-- Работает реактивно -->
<div :style="{ backgroundColor: 'rgb(var(--v-theme-surface-variant))' }">
  Этот цвет правильно обновится при смене темы
</div>
```

**Когда использовать**:
- Когда Vuetify компонент не поддерживает нужный prop
- Для кастомных элементов (div, span, etc.)

## Theme Configuration

### Всегда определяйте цвета для обеих тем

```typescript
// frontend-vue/src/plugins/vuetify.ts

themes: {
  light: {
    dark: false,
    colors: {
      primary: '#1976D2',
      secondary: '#424242',
      // ... other colors
      'surface-variant': '#F5F5F5',  // Светло-серый для light theme
    },
  },
  dark: {
    dark: true,
    colors: {
      primary: '#1976D2',
      secondary: '#424242',
      // ... other colors
      'surface-variant': '#2C2C2C',  // Темно-серый для dark theme
    },
  },
}
```

**Важно**: Если цвет определен только в одной теме, Vuetify использует дефолтное значение, которое может быть некорректным.

## Checklist для новых диалогов

При создании нового диалога убедитесь:

- [ ] Используете `BaseThemedDialog` вместо прямого `v-dialog`
- [ ] Для styled элементов используете `bg-color` prop или CSS variables
- [ ] НЕ используете static CSS classes для тематических цветов
- [ ] Цвета определены в обеих темах (light и dark) в vuetify.ts
- [ ] Проверили работу в обеих темах (light/dark)
- [ ] Проверили переключение темы во время открытого диалога

## Migration Guide

### Шаг 1: Заменить v-dialog на BaseThemedDialog

```vue
<!-- До -->
<v-dialog
  :model-value="modelValue"
  :theme="theme.global.name.value"
  max-width="600px"
  @update:model-value="$emit('update:modelValue', $event)"
>
  <v-card>Content</v-card>
</v-dialog>

<!-- После -->
<BaseThemedDialog
  :model-value="modelValue"
  max-width="600px"
  @update:model-value="$emit('update:modelValue', $event)"
>
  <v-card>Content</v-card>
</BaseThemedDialog>
```

### Шаг 2: Удалить useTheme composable

```typescript
// До
import { useTheme } from 'vuetify'
const theme = useTheme()

// После
// Удалить эти строки - BaseThemedDialog сам управляет темой
```

### Шаг 3: Заменить CSS classes на Vuetify props

```vue
<!-- До -->
<v-card-title class="bg-surface-variant">
  Header
</v-card-title>

<!-- После -->
<v-sheet bg-color="surface-variant" class="pa-4">
  <div class="text-h6">Header</div>
</v-sheet>
```

### Шаг 4: Заменить inline styles на CSS variables

```vue
<!-- До -->
<div class="pa-3 rounded" style="background-color: rgb(var(--v-theme-surface-variant))">
  Content
</div>

<!-- После -->
<v-sheet bg-color="surface-variant" class="pa-3 rounded">
  Content
</v-sheet>
```

## Examples

### Example 1: Simple Dialog

```vue
<template>
  <BaseThemedDialog v-model="showDialog" max-width="500px">
    <v-card>
      <v-sheet bg-color="surface-variant" class="pa-4">
        <div class="d-flex align-center justify-space-between">
          <span class="text-h6">Заголовок</span>
          <v-btn icon="mdi-close" variant="text" @click="showDialog = false" />
        </div>
      </v-sheet>

      <v-card-text class="pa-6">
        <p>Содержимое диалога</p>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" @click="showDialog = false">Отмена</v-btn>
        <v-btn color="primary" variant="elevated" @click="handleSave">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </BaseThemedDialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseThemedDialog from '@/components/common/BaseThemedDialog.vue'

const showDialog = ref(false)

function handleSave() {
  // Save logic
  showDialog.value = false
}
</script>
```

### Example 2: Form Dialog with Validation

```vue
<template>
  <BaseThemedDialog v-model="showDialog" max-width="600px" persistent>
    <v-card>
      <v-sheet bg-color="surface-variant" class="pa-4">
        <div class="d-flex align-center gap-3">
          <v-icon color="primary">mdi-pencil</v-icon>
          <span class="text-h6">Редактирование</span>
        </div>
      </v-sheet>

      <v-card-text class="pa-6">
        <v-form ref="formRef" v-model="formValid" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="formData.name"
            label="Название"
            variant="outlined"
            :rules="[v => !!v || 'Обязательное поле']"
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn variant="text" :disabled="saving" @click="handleClose">Отмена</v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="saving"
          :disabled="!formValid"
          @click="handleSubmit"
        >
          Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </BaseThemedDialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseThemedDialog from '@/components/common/BaseThemedDialog.vue'

const showDialog = ref(false)
const formRef = ref()
const formValid = ref(false)
const saving = ref(false)
const formData = ref({ name: '' })

async function handleSubmit() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    // Save logic
    showDialog.value = false
  } finally {
    saving.value = false
  }
}

function handleClose() {
  if (!saving.value) {
    showDialog.value = false
  }
}
</script>
```

## Testing

При тестировании диалогов убедитесь:

```typescript
// Example unit test
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import MyDialog from '@/components/MyDialog.vue'

describe('MyDialog theme support', () => {
  it('should render with correct theme', () => {
    const vuetify = createVuetify()
    const wrapper = mount(MyDialog, {
      global: {
        plugins: [vuetify]
      },
      props: {
        modelValue: true
      }
    })

    // Check that BaseThemedDialog is used
    expect(wrapper.findComponent({ name: 'BaseThemedDialog' }).exists()).toBe(true)
  })

  it('should switch theme reactively', async () => {
    const vuetify = createVuetify()
    const wrapper = mount(MyDialog, {
      global: {
        plugins: [vuetify]
      },
      props: {
        modelValue: true
      }
    })

    // Switch theme
    vuetify.theme.global.name.value = 'dark'
    await wrapper.vm.$nextTick()

    // Check that dialog updates
    // (implementation depends on your test setup)
  })
})
```

## Performance Considerations

1. **Theme composable**: `useTheme()` в `BaseThemedDialog` вызывается один раз и переиспользуется
2. **Reactivity**: `.value` доступ к `theme.global.name` минимален - только один computed binding
3. **CSS Variables**: Использование CSS variables (`rgb(var(--v-theme-*))`) не влияет на performance

## Common Mistakes

### ❌ Mistake 1: Забыть :theme prop

```vue
<!-- Не работает! -->
<v-dialog v-model="showDialog">
  <v-card>Content</v-card>
</v-dialog>
```

**Fix**: Используйте `BaseThemedDialog`

### ❌ Mistake 2: Static CSS classes

```vue
<!-- Не реактивно! -->
<div class="bg-surface-variant">Content</div>
```

**Fix**: Используйте `bg-color` prop или CSS variables

### ❌ Mistake 3: Неполная конфигурация темы

```typescript
// Только light theme
themes: {
  light: {
    colors: {
      'surface-variant': '#F5F5F5'
    }
  }
  // dark theme пропущена - будет использован дефолт!
}
```

**Fix**: Определите цвета в обеих темах

## Related Documentation

- [Component Library - BaseThemedDialog](../architecture/component_library.md#14-basethemeddialog)
- [Vuetify 3 Theme Documentation](https://vuetifyjs.com/en/features/theme/)
- [Vue 3 Teleport](https://vuejs.org/guide/built-ins/teleport.html)

## Version History

- **2025-10-27**: Создан паттерн после Week 6 Phase 1 implementation
- **Issue discovered**: Week 6 Phase 1 - Dark theme не работал в диалогах
- **Solution implemented**: Explicit theme binding pattern + BaseThemedDialog component

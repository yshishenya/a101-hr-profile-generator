# 🛠️ Линней - Implementation Guide

**Версия**: 1.0
**Дата**: 2025-10-28
**Для**: Разработчиков Frontend & Backend
**Prerequisite**: Прочитать [LINNEY_BRAND_GUIDE.md](./LINNEY_BRAND_GUIDE.md)

---

## 📋 Содержание

1. [Overview](#overview)
2. [Phase 1: Assets Preparation](#phase-1-assets-preparation)
3. [Phase 2: Core Branding](#phase-2-core-branding)
4. [Phase 3: Color System](#phase-3-color-system)
5. [Phase 4: Typography](#phase-4-typography)
6. [Phase 5: Testing](#phase-5-testing)
7. [Code Examples](#code-examples)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### Цель

Интегрировать бренд **Линней** в существующий Vue 3 + Vuetify 3 frontend с минимальными breaking changes.

### Scope

Обновить следующие компоненты:
- ✅ HTML meta (favicon, title)
- ✅ AppHeader (logo + название)
- ✅ AppLayout Drawer (logo + название)
- ✅ LoginView (logo + название)
- ✅ Vuetify theme (colors)
- ⚠️ Опционально: кастомная типографика

### Timeline

- **Минимальная интеграция**: 2-3 часа
- **Полная интеграция**: 4-6 часов (с assets creation + testing)

---

## 📦 Phase 1: Assets Preparation

### Шаг 1.1: Создание SVG логотипов

Нужно создать 4 SVG файла:

#### 1. `linney-logo.svg` - Full Logo (Light Theme)
**Размер**: 120x40px (примерно)
**Элементы**: Icon (ботаническое древо) + Text "Линней HR"
**Цвета**:
- Icon: `#2E7D32` (Forest Green)
- Text: `#212121` (Dark Grey)

```svg
<!-- Пример структуры (упрощенный) -->
<svg width="120" height="40" viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg">
  <!-- Botanical tree icon -->
  <g id="icon">
    <path d="..." fill="#2E7D32"/>
  </g>

  <!-- Text -->
  <text x="48" y="24" font-family="Roboto" font-size="18" font-weight="700" fill="#212121">
    Линней HR
  </text>
</svg>
```

---

#### 2. `linney-logo-dark.svg` - Full Logo (Dark Theme)
**Идентичен** `linney-logo.svg`, но с другими цветами:
- Icon: `#66BB6A` (Light Green)
- Text: `#FFFFFF` (White)

---

#### 3. `linney-icon.svg` - Icon Only
**Размер**: 40x40px
**Элементы**: Только icon (ботаническое древо)
**Цвет**: `#2E7D32` (или `currentColor` для flexibility)

```svg
<svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
  <g id="tree">
    <!-- Simplified botanical tree -->
    <path d="M20 5 L20 35" stroke="currentColor" stroke-width="2"/>
    <path d="M20 15 L10 10" stroke="currentColor" stroke-width="2"/>
    <path d="M20 15 L30 10" stroke="currentColor" stroke-width="2"/>
    <path d="M20 25 L12 22" stroke="currentColor" stroke-width="2"/>
    <path d="M20 25 L28 22" stroke="currentColor" stroke-width="2"/>
    <circle cx="10" cy="10" r="2" fill="currentColor"/>
    <circle cx="30" cy="10" r="2" fill="currentColor"/>
    <circle cx="12" cy="22" r="2" fill="currentColor"/>
    <circle cx="28" cy="22" r="2" fill="currentColor"/>
  </g>
</svg>
```

---

#### 4. `linney-favicon.svg` - Favicon
**Размер**: 32x32px (или 16x16px)
**Элементы**: Simplified icon (максимально упрощенное древо)
**Цвет**: `#2E7D32`

```svg
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <!-- Super simplified tree for favicon -->
  <rect x="14" y="4" width="4" height="24" fill="#2E7D32" rx="2"/>
  <circle cx="10" cy="10" r="3" fill="#2E7D32"/>
  <circle cx="22" cy="10" r="3" fill="#2E7D32"/>
  <circle cx="10" cy="20" r="3" fill="#2E7D32"/>
  <circle cx="22" cy="20" r="3" fill="#2E7D32"/>
</svg>
```

---

### Шаг 1.2: Оптимизация SVG

Используй [SVGOMG](https://jakearchibald.github.io/svgomg/) для оптимизации:

1. Upload SVG file
2. Enable options:
   - ✅ Remove comments
   - ✅ Remove metadata
   - ✅ Remove unnecessary whitespace
   - ✅ Merge paths (where possible)
   - ❌ Disable "Prettify markup" (smaller size)
3. Download optimized SVG

**Цель**: Каждый файл < 5KB

---

### Шаг 1.3: Размещение файлов

```bash
# Создать директорию для ассетов (если нет)
mkdir -p /home/yan/A101/HR/frontend-vue/public/images

# Скопировать файлы
cp linney-logo.svg /home/yan/A101/HR/frontend-vue/public/images/
cp linney-logo-dark.svg /home/yan/A101/HR/frontend-vue/public/images/
cp linney-icon.svg /home/yan/A101/HR/frontend-vue/public/images/
cp linney-favicon.svg /home/yan/A101/HR/frontend-vue/public/
```

**Структура:**
```
frontend-vue/public/
├── linney-favicon.svg           # Фавикон (корень для HTML)
└── images/
    ├── linney-logo.svg          # Полный логотип (light)
    ├── linney-logo-dark.svg     # Полный логотип (dark)
    └── linney-icon.svg          # Иконка
```

---

## 🎨 Phase 2: Core Branding

### Шаг 2.1: Обновить HTML Meta

**Файл**: `/home/yan/A101/HR/frontend-vue/index.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <!-- ✅ ОБНОВИТЬ: Фавикон -->
  <link rel="icon" type="image/svg+xml" href="/linney-favicon.svg" />

  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- ✅ ОБНОВИТЬ: Title -->
  <title>Линней HR - Генератор профилей должностей</title>

  <!-- ✅ ДОБАВИТЬ: Meta description -->
  <meta name="description" content="Линней HR - AI-система для автоматической генерации детальных профилей должностей с использованием Gemini 2.5 Flash" />

  <!-- ✅ ДОБАВИТЬ: Theme color -->
  <meta name="theme-color" content="#2E7D32" />
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

**Изменения:**
- Фавикон: `vite.svg` → `linney-favicon.svg`
- Title: `frontend-vue` → `Линней HR - Генератор профилей должностей`
- Добавлены meta tags

---

### Шаг 2.2: Обновить AppHeader

**Файл**: `/home/yan/A101/HR/frontend-vue/src/components/layout/AppHeader.vue`

**Текущий код** (строки 6-10):
```vue
<v-app-bar elevation="1" color="primary" density="comfortable">
  <v-toolbar-title class="text-h6 font-weight-bold">
    A101 HR Profile Generator
  </v-toolbar-title>

  <!-- ... rest ... -->
</v-app-bar>
```

**Новый код:**
```vue
<v-app-bar elevation="1" color="primary" density="comfortable">
  <v-toolbar-title>
    <div class="d-flex align-center">
      <!-- Logo (динамически меняется в зависимости от темы) -->
      <v-img
        :src="logoSrc"
        height="32"
        width="auto"
        max-width="140"
        contain
        class="mr-2"
        alt="Линней HR"
      />
    </div>
  </v-toolbar-title>

  <!-- ... rest (user chip, theme toggle, logout) ... -->
</v-app-bar>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from 'vuetify'

const theme = useTheme()

// Выбираем логотип в зависимости от темы
const logoSrc = computed(() => {
  return theme.global.current.value.dark
    ? '/images/linney-logo-dark.svg'
    : '/images/linney-logo.svg'
})
</script>
```

**Что изменилось:**
- Добавлен `<v-img>` с логотипом
- Логотип реактивно меняется при переключении темы
- Убран текстовый title (теперь в логотипе)
- Сохранена вся функциональность (user, theme toggle, logout)

---

### Шаг 2.3: Обновить AppLayout Drawer

**Файл**: `/home/yan/A101/HR/frontend-vue/src/components/layout/AppLayout.vue`

**Текущий код** (строки 16-26):
```vue
<v-list-item>
  <template #prepend>
    <v-avatar color="primary" size="40">
      <v-icon size="24">mdi-account-box</v-icon>
    </v-avatar>
  </template>
  <v-list-item-title class="font-weight-bold">
    A101 HR
  </v-list-item-title>
  <v-list-item-subtitle class="text-caption">
    Profile Generator
  </v-list-item-subtitle>
</v-list-item>
```

**Новый код:**
```vue
<v-list-item class="py-4">
  <template #prepend>
    <v-img
      src="/images/linney-icon.svg"
      height="48"
      width="48"
      contain
      class="mr-3"
      alt="Линней HR"
    />
  </template>
  <v-list-item-title class="text-h6 font-weight-bold">
    Линней HR
  </v-list-item-title>
  <v-list-item-subtitle class="text-caption">
    Генератор профилей должностей
  </v-list-item-subtitle>
</v-list-item>
```

**Что изменилось:**
- MDI иконка заменена на брендовый icon (`linney-icon.svg`)
- Размер иконки: 40px → 48px (более заметно)
- Название: "A101 HR" → "Линней HR"
- Подзаголовок на русском: "Profile Generator" → "Генератор профилей должностей"
- Добавлен padding (`py-4`) для breathing space

---

### Шаг 2.4: Обновить LoginView

**Файл**: `/home/yan/A101/HR/frontend-vue/src/views/LoginView.vue`

**Текущий код** (строки 14-22):
```vue
<v-icon size="48" color="primary" class="mb-4">
  mdi-office-building
</v-icon>
<h1 class="text-h5 font-weight-bold mb-2">
  A101 HR Profile Generator
</h1>
<p class="text-body-2 text-medium-emphasis mb-6">
  Sign in to continue
</p>
```

**Новый код:**
```vue
<!-- Logo -->
<v-img
  src="/images/linney-icon.svg"
  height="80"
  width="80"
  contain
  class="mx-auto mb-4"
  alt="Линней HR"
/>

<!-- Title -->
<h1 class="text-h4 font-weight-bold mb-2">
  Линней HR
</h1>

<!-- Subtitle -->
<p class="text-body-1 mb-2">
  Генератор профилей должностей
</p>

<!-- Call to action -->
<p class="text-body-2 text-medium-emphasis mb-6">
  Войдите, чтобы продолжить
</p>
```

**Что изменилось:**
- MDI иконка заменена на брендовый логотип (80x80px - крупнее для impact)
- Название: "A101 HR Profile Generator" → "Линней HR"
- Добавлен подзаголовок на русском
- CTA на русском: "Sign in to continue" → "Войдите, чтобы продолжить"
- Title size: `text-h5` → `text-h4` (больше и заметнее)

---

## 🎨 Phase 3: Color System

### Шаг 3.1: Обновить Vuetify Theme

**Файл**: `/home/yan/A101/HR/frontend-vue/src/plugins/vuetify.ts`

**Текущий код** (строки 32-60):
```typescript
const themes = {
  light: {
    colors: {
      primary: '#1976D2',      // A101 blue
      secondary: '#424242',
      accent: '#82B1FF',
      // ...
    }
  },
  dark: {
    colors: {
      primary: '#1976D2',
      // ...
    }
  }
}
```

**Новый код:**
```typescript
const themes = {
  light: {
    colors: {
      // ✅ LINNEY BRAND COLORS
      primary: '#2E7D32',        // Forest Green (Linney Primary)
      secondary: '#1565C0',      // Deep Blue (Linney Secondary)
      accent: '#66BB6A',         // Light Green (Linney Accent)

      // ✅ FUNCTIONAL COLORS (не меняем - Material Design standard)
      error: '#FF5252',          // Red
      success: '#4CAF50',        // Green
      warning: '#FFC107',        // Amber
      info: '#2196F3',           // Blue

      // ✅ SURFACE COLORS
      background: '#FFFFFF',
      surface: '#FFFFFF',
      'surface-variant': '#F1F8E9',  // Light Green 50 (subtle accent)

      // ✅ ON-COLORS (текст на цветных фонах)
      'on-primary': '#FFFFFF',
      'on-secondary': '#FFFFFF',
      'on-surface': '#212121',
      'on-background': '#212121',
    },
  },
  dark: {
    colors: {
      // ✅ LINNEY BRAND COLORS (darker shades for dark theme)
      primary: '#2E7D32',        // Same green (works on dark)
      secondary: '#1565C0',      // Same blue
      accent: '#81C784',         // Slightly lighter green for better contrast

      // ✅ FUNCTIONAL COLORS
      error: '#FF5252',
      success: '#4CAF50',
      warning: '#FFC107',
      info: '#2196F3',

      // ✅ SURFACE COLORS (Material Design Dark baseline)
      background: '#121212',
      surface: '#1E1E1E',
      'surface-variant': '#1B5E20',  // Green 900 (subtle accent on dark)

      // ✅ ON-COLORS
      'on-primary': '#FFFFFF',
      'on-secondary': '#FFFFFF',
      'on-surface': '#FFFFFF',
      'on-background': '#FFFFFF',
    },
  },
}
```

**Что изменилось:**
- **Primary**: `#1976D2` (A101 blue) → `#2E7D32` (Forest Green)
- **Secondary**: `#424242` (grey) → `#1565C0` (Deep Blue)
- **Accent**: `#82B1FF` (light blue) → `#66BB6A` (Light Green)
- **Surface-variant**: `#F5F5F5` (grey) → `#F1F8E9` (Light Green 50)
- Functional colors (success, error, warning, info) **не меняются** - standard

---

### Шаг 3.2: Проверка контрастности

После изменения цветов, **обязательно проверь контрастность**:

#### Primary Green (#2E7D32) на белом фоне
- **Текст**: Dark Grey (#212121)
- **Контраст**: 6.8:1 ✅ (WCAG AA pass)

#### White text на Primary Green (#2E7D32)
- **Текст**: White (#FFFFFF)
- **Контраст**: 5.2:1 ✅ (WCAG AA pass)

**Инструмент**: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

Если контраст < 4.5:1, нужно:
- Затемнить primary color ИЛИ
- Использовать более тёмный text color

---

### Шаг 3.3: CSS Variables (автоматически)

Vuetify 3 автоматически генерирует CSS variables:

```css
:root {
  --v-theme-primary: 46, 125, 50;        /* #2E7D32 в RGB */
  --v-theme-secondary: 21, 101, 192;     /* #1565C0 */
  --v-theme-accent: 102, 187, 106;       /* #66BB6A */
  /* ... */
}

.v-theme--dark {
  --v-theme-surface: 30, 30, 30;         /* #1E1E1E */
  --v-theme-background: 18, 18, 18;      /* #121212 */
  /* ... */
}
```

**Использование в кастомных стилях:**
```vue
<style scoped>
.custom-element {
  /* Используй rgb() + CSS variable */
  background-color: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
}

.custom-border {
  border: 2px solid rgb(var(--v-theme-primary));
}
</style>
```

---

## ✍️ Phase 4: Typography (Опционально)

**NOTE**: Roboto уже используется. Этот шаг нужен только если есть кастомный шрифт Линней.

### Шаг 4.1: Подключить кастомный шрифт

**Файл**: `/home/yan/A101/HR/frontend-vue/src/style.css`

```css
/* Если используется Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=CustomFont:wght@400;500;700&display=swap');

/* Обновить font stack */
body {
  font-family: 'CustomFont', 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Сохранить Roboto как fallback */
h1, h2, h3, h4, h5, h6 {
  font-family: 'CustomFont', 'Roboto', sans-serif;
}
```

### Шаг 4.2: Тестирование

Проверь:
- ✅ Кириллица отображается корректно
- ✅ Читаемость на small sizes (12px-14px)
- ✅ Font weights загружаются (400, 500, 700)
- ✅ Performance (шрифт < 100KB per weight)

---

## ✅ Phase 5: Testing

### Шаг 5.1: Visual Testing

**Checklist:**

#### Light Theme
- [ ] AppHeader: логотип виден, правильный цвет фона (#2E7D32)
- [ ] AppHeader: белый текст читается на зелёном фоне
- [ ] Navigation Drawer: иконка отображается, название читается
- [ ] LoginView: логотип центрирован, видим
- [ ] Buttons: primary buttons зелёного цвета
- [ ] StatsCard: иконки primary color (#2E7D32)
- [ ] Cards: subtle green tint на surface-variant

#### Dark Theme
- [ ] AppHeader: dark logo variant загружается
- [ ] Фон: тёмный (#121212), не pure black
- [ ] Текст: белый, читаемый
- [ ] Primary green работает на dark background
- [ ] Icons: видимы, достаточный контраст

---

### Шаг 5.2: Responsive Testing

Тестируй на разных breakpoints:

```
Mobile (xs):     < 600px
Tablet (sm-md):  600px - 960px
Desktop (lg+):   > 960px
```

**Checklist:**
- [ ] Mobile: логотип не обрезается
- [ ] Mobile: navigation drawer работает (temporary)
- [ ] Tablet: всё читается, нет overlap
- [ ] Desktop: логотип в optimal size
- [ ] Desktop: navigation drawer permanent

---

### Шаг 5.3: Accessibility Testing

#### Контрастность
```bash
# Используй browser DevTools
# Chrome: Inspect → Lighthouse → Accessibility
# Firefox: Inspect → Accessibility Inspector
```

**Проверь:**
- [ ] Primary color на white: контраст ≥ 4.5:1
- [ ] White text на primary: контраст ≥ 4.5:1
- [ ] All text: минимум WCAG AA (4.5:1 для текста, 3:1 для UI)

#### Keyboard Navigation
- [ ] Tab через все элементы работает
- [ ] Focus indicators видимы
- [ ] Можно открыть меню с клавиатуры
- [ ] Можно logout с клавиатуры

#### Screen Reader
- [ ] Логотип имеет `alt` text
- [ ] Buttons имеют labels
- [ ] Icons имеют `aria-label` (где нет текста)

---

### Шаг 5.4: Browser Testing

Тестируй в:
- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)
- [ ] Edge (Chromium-based)

**Особое внимание:**
- SVG rendering (может отличаться)
- CSS variables support (IE11 не поддерживает, но мы не таргетим)
- Favicon в tab bar

---

## 💻 Code Examples

### Example 1: Использование Primary Color в Component

```vue
<template>
  <v-card>
    <v-card-title class="bg-primary text-white">
      Заголовок
    </v-card-title>
    <v-card-text>
      <p>Контент карточки</p>

      <!-- Primary button -->
      <v-btn color="primary">
        Действие
      </v-btn>

      <!-- Primary icon -->
      <v-icon color="primary" size="32">
        mdi-check-circle
      </v-icon>
    </v-card-text>
  </v-card>
</template>

<style scoped>
/* Кастомный элемент с primary color */
.custom-badge {
  background-color: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  padding: 4px 8px;
  border-radius: 4px;
}
</style>
```

---

### Example 2: Динамический логотип (light/dark)

```vue
<template>
  <v-img
    :src="logoSrc"
    :alt="logoAlt"
    height="40"
    width="auto"
    contain
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from 'vuetify'

const theme = useTheme()

const logoSrc = computed(() => {
  return theme.global.current.value.dark
    ? '/images/linney-logo-dark.svg'
    : '/images/linney-logo.svg'
})

const logoAlt = computed(() => 'Линней HR')
</script>
```

---

### Example 3: Кастомный ботанический паттерн (опционально)

```vue
<template>
  <div class="botanical-card">
    <div class="botanical-pattern"></div>
    <div class="card-content">
      <!-- Контент -->
    </div>
  </div>
</template>

<style scoped>
.botanical-card {
  position: relative;
  padding: 24px;
  background: rgb(var(--v-theme-surface));
  border-radius: 8px;
  overflow: hidden;
}

.botanical-pattern {
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  background-image: url('/images/botanical-pattern.svg');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.05; /* Very subtle */
  pointer-events: none;
}

.card-content {
  position: relative;
  z-index: 1;
}
</style>
```

---

## 🐛 Troubleshooting

### Проблема 1: Логотип не отображается

**Симптомы:**
- Broken image icon в AppHeader
- 404 error в console

**Решение:**
```bash
# Проверь путь к файлу
ls -la /home/yan/A101/HR/frontend-vue/public/images/

# Проверь, что пути в коде правильные
# ПРАВИЛЬНО: /images/linney-logo.svg (абсолютный от public/)
# НЕПРАВИЛЬНО: ./images/linney-logo.svg (относительный)
# НЕПРАВИЛЬНО: images/linney-logo.svg (без слэша в начале)

# Перезапусти dev server
npm run dev
```

---

### Проблема 2: Цвета не применяются

**Симптомы:**
- Buttons остаются синими
- Primary color не изменился

**Решение:**
```bash
# 1. Проверь, что vuetify.ts сохранен
# 2. Перезапусти dev server (hard reload)
npm run dev

# 3. Проверь browser cache
# Ctrl+Shift+R (Windows/Linux) или Cmd+Shift+R (Mac)

# 4. Проверь devtools console на ошибки
# Может быть syntax error в vuetify.ts
```

---

### Проблема 3: Dark theme логотип не меняется

**Симптомы:**
- Light logo отображается на dark background

**Решение:**
```vue
<!-- Проверь computed property -->
<script setup lang="ts">
import { useTheme } from 'vuetify'

const theme = useTheme()

// Убедись что используешь .current.value.dark
const logoSrc = computed(() => {
  const isDark = theme.global.current.value.dark
  console.log('Is Dark Theme:', isDark) // Debug
  return isDark
    ? '/images/linney-logo-dark.svg'
    : '/images/linney-logo.svg'
})
</script>
```

---

### Проблема 4: Контраст недостаточный

**Симптомы:**
- Текст плохо читается
- Lighthouse показывает accessibility errors

**Решение:**
```typescript
// Затемни primary color
// БЫЛО:
primary: '#2E7D32',  // Contrast ratio: 5.2:1

// СТАЛО (если нужно больше контраста):
primary: '#1B5E20',  // Green 900, Contrast ratio: 8.1:1

// ИЛИ используй более тёмный text color:
'on-primary': '#F5F5F5',  // Slight off-white
```

---

### Проблема 5: SVG не масштабируется

**Симптомы:**
- Логотип обрезается или pixelated

**Решение:**
```vue
<v-img
  src="/images/linney-logo.svg"
  height="40"
  width="auto"     <!-- ✅ Auto width -->
  contain          <!-- ✅ Preserve aspect ratio -->
  max-width="200"  <!-- ✅ Limit max size -->
/>

<!-- НЕ используй fixed width если SVG не square -->
```

---

## 📚 Additional Resources

### Files to Modify (Summary)

```
frontend-vue/
├── index.html                                    # Meta, favicon, title
├── public/
│   ├── linney-favicon.svg                        # NEW
│   └── images/
│       ├── linney-logo.svg                       # NEW
│       ├── linney-logo-dark.svg                  # NEW
│       └── linney-icon.svg                       # NEW
├── src/
│   ├── plugins/
│   │   └── vuetify.ts                            # Colors
│   ├── components/
│   │   └── layout/
│   │       ├── AppHeader.vue                     # Logo в toolbar
│   │       └── AppLayout.vue                     # Logo в drawer
│   └── views/
│       └── LoginView.vue                         # Logo на странице входа
```

### Commands

```bash
# Development
npm run dev

# Type check
npm run type-check

# Build (проверка перед prod)
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

---

## ✅ Verification Checklist

После завершения всех шагов, проверь:

### Assets
- [ ] 4 SVG файла созданы и оптимизированы
- [ ] SVG файлы размещены в `public/` и `public/images/`
- [ ] Размеры файлов < 5KB каждый

### HTML
- [ ] `index.html`: favicon обновлён
- [ ] `index.html`: title обновлён
- [ ] `index.html`: meta tags добавлены

### Components
- [ ] `AppHeader.vue`: логотип добавлен
- [ ] `AppHeader.vue`: динамическая смена light/dark работает
- [ ] `AppLayout.vue`: иконка и название обновлены
- [ ] `LoginView.vue`: логотип и тексты обновлены

### Theme
- [ ] `vuetify.ts`: primary, secondary, accent обновлены
- [ ] `vuetify.ts`: surface-variant обновлён
- [ ] Light theme: цвета корректны
- [ ] Dark theme: цвета корректны

### Testing
- [ ] Visual: всё выглядит правильно в обеих темах
- [ ] Responsive: работает на mobile/tablet/desktop
- [ ] Accessibility: контраст ≥ 4.5:1, keyboard navigation
- [ ] Cross-browser: Chrome, Firefox, Safari, Edge

### Documentation
- [ ] README обновлён (если нужно)
- [ ] Component Library обновлён (если есть)
- [ ] Changelog создан (если ведётся)

---

## 🎉 Done!

После прохождения всех шагов, бренд **Линней** полностью интегрирован в приложение!

**Next Steps:**
- Создать PR с изменениями
- Code review
- Testing на staging
- Deploy to production

**Reference Documents:**
- [LINNEY_BRAND_GUIDE.md](./LINNEY_BRAND_GUIDE.md) - Полный brand guide
- [LINNEY_QUICK_START.md](./LINNEY_QUICK_START.md) - TL;DR версия

---

**🌿 Линней HR - Систематизируем ваши должности с научной точностью**

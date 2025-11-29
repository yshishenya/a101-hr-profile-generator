# ⚡ Линней - Quick Start Guide

**Время на интеграцию**: 2-3 часа
**Для**: Занятых разработчиков
**Версия**: 1.0

---

## 🎯 TL;DR

**Линней** = Карл Линней (создатель системы классификации) → Наш инструмент систематизирует должности.

**Что меняем:**
- Логотипы (ботаническое древо)
- Primary color: синий → зелёный
- Название: "A101 HR" → "Линней HR"

---

## 🎨 Brand Colors

```css
/* Замени в vuetify.ts */
primary: '#2E7D32'        /* Forest Green (было #1976D2) */
secondary: '#1565C0'      /* Deep Blue (было #424242) */
accent: '#66BB6A'         /* Light Green (было #82B1FF) */
surface-variant: '#F1F8E9' /* Light Green 50 (было #F5F5F5) */
```

**Dark theme:**
```css
surface-variant: '#1B5E20' /* Green 900 (было #2C2C2C) */
```

---

## 📦 Нужны 4 SVG файла

Создай и положи в `frontend-vue/public/`:

### 1. `linney-favicon.svg` (32x32px)
Упрощённое ботаническое древо, цвет `#2E7D32`

### 2. `images/linney-logo.svg` (120x40px)
Icon + Text "Линней HR", для light theme

### 3. `images/linney-logo-dark.svg` (120x40px)
То же, но для dark theme (светлые цвета)

### 4. `images/linney-icon.svg` (40x40px)
Только icon, без текста

**Temporary placeholder** (пока нет дизайна):
```bash
# Можешь использовать MDI icon как placeholder
# Скачай: https://pictogrammers.com/library/mdi/icon/file-tree/
```

---

## ✏️ Изменения в коде

### 1. HTML Meta
**Файл**: `frontend-vue/index.html`

```html
<!-- ЗАМЕНИТЬ -->
<link rel="icon" type="image/svg+xml" href="/linney-favicon.svg" />
<title>Линней HR - Генератор профилей должностей</title>
<meta name="theme-color" content="#2E7D32" />
```

---

### 2. Vuetify Theme
**Файл**: `frontend-vue/src/plugins/vuetify.ts`

```typescript
// Строки 32-45 (light theme)
const themes = {
  light: {
    colors: {
      primary: '#2E7D32',         // ⬅️ ИЗМЕНИТЬ
      secondary: '#1565C0',        // ⬅️ ИЗМЕНИТЬ
      accent: '#66BB6A',           // ⬅️ ИЗМЕНИТЬ
      // ... остальное не трогаем
      'surface-variant': '#F1F8E9', // ⬅️ ИЗМЕНИТЬ
    }
  },
  dark: {
    colors: {
      primary: '#2E7D32',          // ⬅️ ИЗМЕНИТЬ
      secondary: '#1565C0',         // ⬅️ ИЗМЕНИТЬ
      accent: '#81C784',            // ⬅️ ИЗМЕНИТЬ
      'surface-variant': '#1B5E20', // ⬅️ ИЗМЕНИТЬ
    }
  }
}
```

---

### 3. AppHeader (Toolbar)
**Файл**: `frontend-vue/src/components/layout/AppHeader.vue`

**БЫЛО** (строка 7):
```vue
<v-toolbar-title class="text-h6 font-weight-bold">
  A101 HR Profile Generator
</v-toolbar-title>
```

**СТАЛО**:
```vue
<v-toolbar-title>
  <div class="d-flex align-center">
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

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from 'vuetify'

const theme = useTheme()

const logoSrc = computed(() => {
  return theme.global.current.value.dark
    ? '/images/linney-logo-dark.svg'
    : '/images/linney-logo.svg'
})
</script>
```

---

### 4. Navigation Drawer
**Файл**: `frontend-vue/src/components/layout/AppLayout.vue`

**БЫЛО** (строки 17-26):
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

**СТАЛО**:
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

---

### 5. Login Page
**Файл**: `frontend-vue/src/views/LoginView.vue`

**БЫЛО** (строки 15-20):
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

**СТАЛО**:
```vue
<v-img
  src="/images/linney-icon.svg"
  height="80"
  width="80"
  contain
  class="mx-auto mb-4"
  alt="Линней HR"
/>
<h1 class="text-h4 font-weight-bold mb-2">
  Линней HR
</h1>
<p class="text-body-1 mb-2">
  Генератор профилей должностей
</p>
<p class="text-body-2 text-medium-emphasis mb-6">
  Войдите, чтобы продолжить
</p>
```

---

## ✅ Verification Checklist

После изменений, проверь:

### Visual (5 минут)
- [ ] AppHeader: логотип виден и правильный цвет (зелёный)
- [ ] Navigation drawer: иконка и название "Линней HR"
- [ ] LoginView: большой логотип по центру
- [ ] Primary buttons: зелёные (не синие)
- [ ] Dark theme: логотип меняется на dark variant

### Functional (5 минут)
- [ ] Theme toggle работает (light/dark)
- [ ] Навигация работает
- [ ] Login работает
- [ ] Нет console errors

### Responsive (5 минут)
- [ ] Mobile (< 600px): логотип не обрезается
- [ ] Tablet (600-960px): всё читается
- [ ] Desktop (> 960px): оптимальные размеры

---

## 🐛 Common Issues

### "Logo not showing"
```bash
# Проверь пути
ls frontend-vue/public/images/

# Путь должен быть АБСОЛЮТНЫЙ от public/
src="/images/linney-logo.svg"  # ✅ Правильно
src="./images/linney-logo.svg" # ❌ Неправильно
```

### "Colors not applying"
```bash
# Перезапусти dev server + hard reload
npm run dev
# Ctrl+Shift+R (Windows) или Cmd+Shift+R (Mac)
```

### "Dark logo not switching"
```typescript
// Проверь что импортирован useTheme
import { useTheme } from 'vuetify'
const theme = useTheme()

// Debug:
console.log('Is dark:', theme.global.current.value.dark)
```

---

## 📚 More Details

**Нужно больше информации?**
- Comprehensive guide: [LINNEY_BRAND_GUIDE.md](./LINNEY_BRAND_GUIDE.md)
- Step-by-step: [LINNEY_IMPLEMENTATION.md](./LINNEY_IMPLEMENTATION.md)
- Visual references: [mood-board.md](./visual-references/mood-board.md)

---

## 🚀 Deploy

**Before production:**
```bash
# Type check
npm run type-check

# Build
npm run build

# Test build
npm run preview
```

**Checklist:**
- [ ] All tests passing
- [ ] Type check passing
- [ ] Build successful
- [ ] Visual review on staging
- [ ] Accessibility check (WCAG AA)

---

## 📝 Notes

**What NOT to change:**
- ✅ Functional colors (success, error, warning, info) - keep Material Design
- ✅ Typography (Roboto) - works great, no need to change
- ✅ Component structure - only visual changes
- ✅ Vuetify defaults - already optimized

**Estimated time:**
- Assets creation: 30-60 min (if designing from scratch)
- Code changes: 30-45 min
- Testing: 30-45 min
- **Total: 2-3 hours**

---

**🌿 Линней HR - Систематизируем ваши должности с научной точностью**

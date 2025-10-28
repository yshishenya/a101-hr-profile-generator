# Week 1-2: Foundation & Authentication - Детальный UX/UI план

**Цель:** Создать прочный фундамент с продуманным UX/UI
**Принцип:** Простота, интуитивность, современность

---

## 🎨 UX/UI Design Philosophy

### Принципы дизайна:
1. **Clarity First** - Понятность > Красота
2. **Consistency** - Единый язык UI во всем приложении
3. **Feedback** - Мгновенная обратная связь на каждое действие
4. **Forgiveness** - Пользователь может легко исправить ошибку
5. **Efficiency** - Минимум кликов для достижения цели

### Vuetify Material Design:
- **Elevation** - Карточки с тенями для визуальной иерархии
- **Spacing** - 8px grid system (4, 8, 16, 24, 32)
- **Typography** - Roboto font, четкая иерархия заголовков
- **Icons** - Material Design Icons (mdi)
- **Colors** - Осмысленное использование цветов (primary для действий, error для ошибок)

---

## 🎯 User Flows (Week 1-2)

### Flow 1: First Time User - Login
```
1. User открывает http://localhost:5173
   ↓
2. Видит редирект (visual feedback: loading spinner)
   ↓
3. Попадает на /login
   ↓ Visual State:
   - Центрированная карточка (max-width: 400px)
   - Логотип A101 (48px icon)
   - Заголовок "HR Profile Generator"
   - 2 поля: Username, Password
   - Кнопка "Войти"
   - Нет лишних элементов!
   ↓
4. Вводит username
   ↓ UX feedback:
   - Поле подсвечивается (focus blue outline)
   - Нет валидации на лету (не раздражаем)
   ↓
5. Вводит password
   ↓ UX feedback:
   - Иконка глаза для show/hide пароля
   - Нет валидации на лету
   ↓
6. Нажимает "Войти"
   ↓ UX feedback (критично!):
   - Кнопка показывает loading (spinner)
   - Кнопка disabled
   - Форма disabled
   ↓
7a. Success:
   - ✅ Зеленая snackbar "Добро пожаловать, {name}!" (2 сек)
   - Плавный редирект на dashboard (500ms delay)
   ↓
7b. Error (неверный пароль):
   - ❌ Красный alert над формой
   - Текст: "Неверное имя пользователя или пароль"
   - Поле password очищается
   - Focus возвращается на password
   - Можно сразу повторить
```

### Flow 2: Returning User - Auto Login
```
1. User открывает сайт
   ↓
2. Token в localStorage валидный
   ↓
3. Автоматический редирект на /
   ↓
4. Показывает dashboard
   (НЕ показываем login screen!)
```

### Flow 3: Theme Toggle
```
1. User кликает на иконку theme в header
   ↓ UX feedback:
   - Мгновенное переключение темы (без задержки!)
   - Иконка меняется: ☀️ → 🌙 или наоборот
   - Все компоненты адаптируются
   ↓
2. Preference сохраняется в localStorage
   ↓
3. При следующем визите тема применяется автоматически
```

### Flow 4: Logout
```
1. User кликает на свое имя в header
   ↓
2. Открывается dropdown menu
   ↓
3. Видит пункт "Logout" с иконкой
   ↓
4. Кликает "Logout"
   ↓ UX feedback:
   - Мгновенный редирект на /login
   - Token удаляется
   - Snackbar "Вы вышли из системы"
```

---

## 📐 Wireframes (Детальные)

### 1. Login Page (Desktop)

```
┌────────────────────────────────────────────────┐
│                                                │
│                                                │
│                                                │
│            ┌──────────────────────┐            │
│            │                      │            │
│            │   [A101 Icon 48px]   │            │
│            │                      │            │
│            │  HR Profile          │            │
│            │  Generator           │            │
│            │  ─────────────       │            │
│            │                      │            │
│            │  ┌────────────────┐  │            │
│            │  │ Username       │  │            │
│            │  │ [👤 icon]      │  │            │
│            │  └────────────────┘  │            │
│            │                      │            │
│            │  ┌────────────────┐  │            │
│            │  │ Password  [👁] │  │            │
│            │  │ [🔒 icon]      │  │            │
│            │  └────────────────┘  │            │
│            │                      │            │
│            │  ┌────────────────┐  │            │
│            │  │     ВОЙТИ      │  │            │
│            │  │   (primary)    │  │            │
│            │  └────────────────┘  │            │
│            │                      │            │
│            └──────────────────────┘            │
│                                                │
│                                                │
└────────────────────────────────────────────────┘

Colors:
- Background: White (light) / #121212 (dark)
- Card: Elevation 8, rounded corners
- Primary button: #1976D2 (blue)
- Icons: Gray (#757575)
- Focus: Blue outline
```

### 2. Login Page - Error State

```
┌────────────────────────────────────────────────┐
│            ┌──────────────────────┐            │
│            │                      │            │
│            │   [A101 Icon 48px]   │            │
│            │  HR Profile Generator│            │
│            │                      │            │
│            │  ╔══════════════════╗ │  ← Red alert
│            │  ║ ⚠️ Неверное имя  ║ │
│            │  ║ пользователя или ║ │
│            │  ║ пароль           ║ │
│            │  ╚══════════════════╝ │
│            │                      │
│            │  ┌────────────────┐  │
│            │  │ admin          │  │  ← Value kept
│            │  └────────────────┘  │
│            │                      │
│            │  ┌────────────────┐  │
│            │  │ [empty]        │  │  ← Cleared!
│            │  │ [focus here]   │  │  ← Auto focus
│            │  └────────────────┘  │
│            │                      │
│            │  ┌────────────────┐  │
│            │  │     ВОЙТИ      │  │  ← Re-enabled
│            │  └────────────────┘  │
│            └──────────────────────┘            │
└────────────────────────────────────────────────┘
```

### 3. Login Page - Loading State

```
┌────────────────────────────────────────────────┐
│            ┌──────────────────────┐            │
│            │   [A101 Icon]        │            │
│            │  HR Profile Generator│            │
│            │                      │            │
│            │  ┌────────────────┐  │
│            │  │ admin          │  │  ← Disabled
│            │  └────────────────┘  │
│            │                      │
│            │  ┌────────────────┐  │
│            │  │ ••••••••       │  │  ← Disabled
│            │  └────────────────┘  │
│            │                      │
│            │  ┌────────────────┐  │
│            │  │ [🔄] Вход...   │  │  ← Loading!
│            │  │   (disabled)   │  │
│            │  └────────────────┘  │
│            └──────────────────────┘            │
└────────────────────────────────────────────────┘
```

### 4. App Layout (After Login)

```
┌────────────────────────────────────────────────────────┐
│ [A101] HR Profile Generator    [☀️] Admin ▾  Logout   │  ← AppHeader
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │                                                  │ │
│  │             PAGE CONTENT HERE                    │ │
│  │          (Dashboard, Generator, etc)             │ │
│  │                                                  │ │
│  │                                                  │ │
│  │                                                  │ │
│  │                                                  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘

Header breakdown:
┌────────────────────────────────────────────────────────┐
│ Logo | Title     [Nav Links]     [Theme] [User Menu]  │
│      │                                                 │
│ [🏢] │ HR Profile │ Dashboard │ Generator │ ☀️ │ 👤▾  │
│      │ Generator  │ (active)  │ Profiles  │    │      │
└────────────────────────────────────────────────────────┘

Active nav link: Blue underline
Theme toggle: Icon-only button (sun/moon)
User menu: Dropdown with logout
```

### 5. Dark Theme

```
Light Theme:                    Dark Theme:
────────────────               ────────────────
Background: #FFFFFF            Background: #121212
Surface: #FFFFFF               Surface: #1E1E1E
Card: #FFFFFF                  Card: #2D2D2D
Text: #000000                  Text: #FFFFFF
Primary: #1976D2               Primary: #82B1FF
```

---

## 🎨 Component Design Specs

### LoginView.vue

**Visual Hierarchy:**
```
1. Logo (48px) - визуальный якорь
2. Title (text-h5) - идентификация
3. Error alert (если есть) - критично заметить
4. Form fields - последовательно
5. Submit button - четкий призыв к действию
```

**Spacing:**
```
Card padding: 32px (pa-8)
Between logo and title: 16px (mb-4)
Between title and form: 24px (mb-6)
Between fields: 16px (mb-4)
Between password and button: 24px (mt-6)
```

**Interactive States:**
```css
Input field:
  - Default: Gray outline
  - Focus: Blue outline (2px)
  - Filled: Black text
  - Error: Red outline + red text below

Button:
  - Default: Blue, white text
  - Hover: Darker blue
  - Loading: Blue + spinner + disabled
  - Disabled: Gray, can't click
```

### AppHeader.vue

**Structure:**
```
Left side:                Right side:
- Logo (32px icon)       - Navigation links
- App title              - Theme toggle
                         - User menu

Total height: 64px (dense toolbar)
```

**Navigation Links:**
```
State       Visual
─────       ──────
Active:     Blue text + blue underline (3px)
Inactive:   White text (light) / Gray text (dark)
Hover:      Slight opacity change
```

**Theme Toggle:**
```
Light mode: ☀️ sun icon
Dark mode:  🌙 moon icon
Hover: Slight scale up (1.1x)
Click: Instant theme switch + icon change
```

**User Menu:**
```
Trigger: "Admin ▾"
Dropdown:
  ┌─────────────────┐
  │ 🚪 Logout       │
  └─────────────────┘

Future expansion:
  ┌─────────────────┐
  │ 👤 Profile      │
  │ ⚙️ Settings     │
  │ ─────────────   │
  │ 🚪 Logout       │
  └─────────────────┘
```

---

## 📱 Responsive Behavior

### Breakpoints (Vuetify):
- xs: <600px (mobile) - НЕ оптимизируем в MVP
- sm: 600-960px (tablet) - минимальная поддержка
- md: 960-1264px (small desktop) - полная поддержка
- lg: 1264-1904px (desktop) - полная поддержка
- xl: >1904px (large desktop) - полная поддержка

### Login Page:
```
Desktop (md+):
- Card width: 400px
- Centered vertically and horizontally

Tablet (sm):
- Card width: 90%
- Max-width: 400px
- Still centered

Mobile (xs):
- Card width: 100%
- No side padding
- Still works (not optimized)
```

### AppHeader:
```
Desktop (md+):
- All items visible
- Navigation links horizontal

Tablet (sm):
- Logo + title compressed
- Nav links still horizontal
- Might need smaller font

Mobile (xs):
- Hamburger menu (not in MVP Week 1-2)
- Just logo + user menu for now
```

---

## ⚡ Performance Considerations

### Initial Load:
```
Target: <2 seconds

Optimizations:
1. Vite code splitting (automatic)
2. Vuetify component lazy loading
3. No heavy images on login page
4. Minimal JavaScript on first load
```

### Route Transitions:
```
Target: <300ms

Optimizations:
1. Prefetch routes on hover
2. Vuetify built-in transitions
3. Keep transitions subtle (fade)
```

### Theme Switch:
```
Target: Instant (<50ms)

Implementation:
1. Vuetify reactive theme system
2. No full re-render
3. CSS variables change
4. localStorage write (async)
```

---

## 🧪 Testing Checklist (Week 1-2)

### Manual Testing:

#### Login Flow:
- [ ] Empty form shows validation (on submit)
- [ ] Wrong credentials show error
- [ ] Correct credentials redirect to dashboard
- [ ] Error message is clear
- [ ] Password field clears on error
- [ ] Focus returns to password on error
- [ ] Loading state shows correctly
- [ ] Can't double-submit during loading

#### Theme Toggle:
- [ ] Light theme is default
- [ ] Click toggles to dark
- [ ] All components adapt correctly
- [ ] Preference persists on reload
- [ ] Icon changes correctly
- [ ] No visual glitches during switch

#### Navigation:
- [ ] Unauthenticated redirects to /login
- [ ] Authenticated redirects to /
- [ ] Logout works and redirects
- [ ] Active nav link highlights
- [ ] All links clickable

#### Responsive:
- [ ] Works at 1920x1080 (desktop)
- [ ] Works at 1366x768 (laptop)
- [ ] Works at 768x1024 (tablet)
- [ ] Looks OK at 375x667 (mobile)

#### Browser Compatibility:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest) - if on Mac

---

## 📝 Code Quality Standards

### TypeScript:
```typescript
// GOOD: Explicit types
const token = ref<string | null>(null)
const user = ref<User | null>(null)

// BAD: Implicit any
const token = ref(null)  // type is Ref<null>
```

### Composables:
```typescript
// Pattern: use{Feature}
export function useAuth() {
  // Return reactive state + methods
  return {
    isAuthenticated,  // ComputedRef<boolean>
    login,           // (credentials) => Promise<boolean>
    logout           // () => Promise<void>
  }
}
```

### Error Handling:
```typescript
// ALWAYS handle errors gracefully
try {
  await api.post('/endpoint')
} catch (error: any) {
  // User-friendly message
  showError(error.response?.data?.message || 'Что-то пошло не так')
  // Log for debugging
  console.error('API Error:', error)
}
```

---

## 🚀 Implementation Order (Step-by-step)

### Step 1: Project Init (5 min)
```bash
npm create vite@latest frontend-vue -- --template vue-ts
cd frontend-vue
npm install
```

### Step 2: Dependencies (3 min)
```bash
npm install vuetify @mdi/font pinia vue-router axios
npm install file-saver jszip
npm install -D @types/node sass
```

### Step 3: Project Structure (2 min)
Create all folders and placeholder files

### Step 4: Configuration (10 min)
- vite.config.ts
- tsconfig.json
- .env.example
- ESLint, Prettier

### Step 5: TypeScript Types (15 min)
All types based on real API responses

### Step 6: API Services (20 min)
- api.ts (Axios instance)
- auth.service.ts

### Step 7: Pinia Stores (20 min)
- auth.ts store
- catalog.ts store (placeholder)

### Step 8: Vuetify Setup (15 min)
- plugins/vuetify.ts
- Light + Dark themes
- Configure colors

### Step 9: Routing (15 min)
- router/index.ts
- Route guards
- Auth check

### Step 10: App Layout (30 min)
- App.vue
- AppLayout.vue
- AppHeader.vue with theme toggle

### Step 11: Login Page (45 min)
- LoginView.vue
- Form validation
- Error handling
- Loading states

### Step 12: Testing (30 min)
- Manual testing all flows
- Fix bugs
- Polish UI

### Step 13: Commit (5 min)
```bash
git add .
git commit -m "feat(foundation): Week 1-2 foundation complete

- Vue 3 + TypeScript + Vite setup
- Vuetify with light/dark themes
- Authentication flow (login/logout)
- API services layer with JWT interceptors
- Pinia stores (auth, catalog)
- Routing with guards
- AppLayout + AppHeader
- LoginView with UX polish
- Theme persistence

Tested:
- Login flow (success + error states)
- Theme toggle
- JWT token management
- Navigation guards
- Responsive (desktop + tablet)

🚀 Ready for Week 3: Dashboard implementation"
```

---

## 🎯 Success Criteria (Week 1-2)

### Functional:
- ✅ User can login with username/password
- ✅ Invalid credentials show clear error
- ✅ Successful login redirects to dashboard
- ✅ User can toggle theme (light/dark)
- ✅ Theme preference persists
- ✅ User can logout
- ✅ Unauthenticated users redirect to login
- ✅ JWT token is managed correctly

### UX:
- ✅ Loading states are clear
- ✅ Error messages are helpful
- ✅ No UI glitches
- ✅ Theme switch is instant
- ✅ Navigation is intuitive
- ✅ Login form is clean and simple

### Technical:
- ✅ TypeScript without errors
- ✅ ESLint passes
- ✅ Code is organized
- ✅ Services layer is clean
- ✅ Stores are simple
- ✅ No console errors

### Performance:
- ✅ Initial load <2 seconds
- ✅ Login response <500ms (network dependent)
- ✅ Theme switch instant
- ✅ No janky animations

---

**Ready to start automatic implementation!** 🚀

Каждый шаг будет сопровождаться:
1. Объяснением "что делаем и зачем"
2. Созданием файлов
3. Тестированием
4. Промежуточным коммитом (если логично)

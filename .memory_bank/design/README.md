# 🌿 Линней Brand Guide - Documentation Index

**Версия**: 1.0
**Дата**: 2025-10-28
**Статус**: ✅ Ready for Implementation

---

## 📚 Документация

Comprehensive brand guide для **Линней HR** - AI-системы для генерации профилей должностей.

### Структура документов

```
.memory_bank/design/
├── README.md                           # ← Вы здесь (навигация)
├── LINNEY_BRAND_GUIDE.md              # Полный brand guide
├── LINNEY_IMPLEMENTATION.md           # Технический implementation guide
├── LINNEY_QUICK_START.md              # Быстрый старт (TL;DR)
└── visual-references/
    └── mood-board.md                  # Визуальные референсы
```

---

## 🎯 Выбери свой путь

### Для дизайнеров
👉 Начни с: **[LINNEY_BRAND_GUIDE.md](./LINNEY_BRAND_GUIDE.md)**

Comprehensive guide включающий:
- Brand identity и легенда
- Цветовая палитра (primary, secondary, accent)
- Типографика и font system
- Логотип (спецификации, варианты, правила)
- Иконография
- UI components guidelines
- Tone of voice
- Do's and Don'ts

**Время чтения**: 30-40 минут
**Объём**: ~15,000 слов

---

### Для разработчиков
👉 Начни с: **[LINNEY_IMPLEMENTATION.md](./LINNEY_IMPLEMENTATION.md)**

Пошаговый технический guide:
- Assets preparation (SVG логотипы)
- Code changes (Vue/Vuetify компоненты)
- Color system integration
- Testing checklist
- Troubleshooting common issues
- Ready-to-use code snippets

**Время на интеграцию**: 2-3 часа
**Объём**: ~7,000 слов

---

### Для занятых (Quick Start)
👉 Начни с: **[LINNEY_QUICK_START.md](./LINNEY_QUICK_START.md)**

TL;DR версия для быстрого старта:
- 3 главных цвета (hex коды)
- 5 файлов для изменения
- Minimal code snippets
- Verification checklist

**Время**: 10 минут чтение + 2-3 часа implementation
**Объём**: ~2,000 слов

---

### Для вдохновения
👉 Смотри: **[visual-references/mood-board.md](./visual-references/mood-board.md)**

Визуальные референсы и inspiration:
- Historical context (Карл Линней)
- Visual inspiration (ботаника + tech)
- Color mood и ассоциации
- Icon & illustration style
- Competitor analysis
- Real-world applications

**Время**: 15-20 минут
**Объём**: ~5,000 слов

---

## 🚀 Quick Links

### Brand Essentials

| Что нужно | Где найти |
|-----------|-----------|
| **Цвета** (hex коды) | [Brand Guide → Color Palette](./LINNEY_BRAND_GUIDE.md#color-palette) |
| **Логотип** (specs) | [Brand Guide → Logo System](./LINNEY_BRAND_GUIDE.md#logo-system) |
| **Шрифты** | [Brand Guide → Typography](./LINNEY_BRAND_GUIDE.md#typography) |
| **Tone of Voice** | [Brand Guide → Tone of Voice](./LINNEY_BRAND_GUIDE.md#tone-of-voice) |

### Implementation

| Что делаем | Где инструкции |
|------------|----------------|
| **SVG логотипы** (создание) | [Implementation → Phase 1](./LINNEY_IMPLEMENTATION.md#phase-1-assets-preparation) |
| **Vuetify colors** (обновление) | [Implementation → Phase 3](./LINNEY_IMPLEMENTATION.md#phase-3-color-system) |
| **AppHeader** (код) | [Quick Start → AppHeader](./LINNEY_QUICK_START.md#3-appheader-toolbar) |
| **LoginView** (код) | [Quick Start → Login Page](./LINNEY_QUICK_START.md#5-login-page) |

---

## 🎨 Brand Summary (One-Pager)

### Название
**Линней HR**
Генератор профилей должностей

### Легенда
Назван в честь **Карла Линнея** (1707-1778) - шведского натуралиста, создавшего универсальную систему классификации живых организмов. Как Линней систематизировал природу, так наш инструмент систематизирует должности компании.

### Цветовая палитра
```css
Primary:   #2E7D32  /* Forest Green - природа, классификация */
Secondary: #1565C0  /* Deep Blue - наука, структура */
Accent:    #66BB6A  /* Light Green - рост, прогресс */
```

### Шрифт
**Roboto** (Material Design standard)
Weights: Regular (400), Medium (500), Bold (700)

### Визуальный стиль
Ботаническая элегантность + Современная функциональность
Material Design 3 + botanical accents

### Tone of Voice
Профессиональный, но дружелюбный
Точный, но не сухой
Helpful, but not condescending

---

## 📋 Implementation Checklist

### Минимальная интеграция (MVP)
- [ ] Создать 4 SVG логотипа (favicon, full logo, icon)
- [ ] Обновить `index.html` (favicon, title, meta)
- [ ] Обновить `vuetify.ts` (primary, secondary, accent colors)
- [ ] Обновить `AppHeader.vue` (добавить логотип)
- [ ] Обновить `LoginView.vue` (добавить логотип)

**Timeline**: 2-3 часа

---

### Полная интеграция
- [ ] Всё из MVP
- [ ] Обновить `AppLayout.vue` (logo в navigation drawer)
- [ ] Dark theme logo variants
- [ ] Обновить все упоминания "A101 HR" → "Линней HR"
- [ ] Testing (visual, responsive, accessibility)
- [ ] Documentation updates

**Timeline**: 4-6 часов

---

## 🎓 Brand Education

### Для новых членов команды

**Обязательно прочитать:**
1. [Brand Identity](./LINNEY_BRAND_GUIDE.md#brand-identity) (10 мин)
2. [Visual System](./LINNEY_BRAND_GUIDE.md#visual-system) (5 мин)
3. [Tone of Voice](./LINNEY_BRAND_GUIDE.md#tone-of-voice) (5 мин)

**Рекомендуется:**
4. [Historical References](./visual-references/mood-board.md#historical-references) (5 мин)
5. [Do's and Don'ts](./LINNEY_BRAND_GUIDE.md#dos-and-donts) (5 мин)

**Total**: 30 минут для полного onboarding

---

## 🔧 Maintenance

### Когда обновлять Brand Guide

- ✅ При добавлении новых UI компонентов
- ✅ При изменении цветовой палитры
- ✅ При создании новых визуальных элементов
- ✅ При изменении tone of voice

### Version Control

```
v1.0 (2025-10-28) - Initial brand guide creation
v1.1 (TBD)        - Post-implementation updates
v2.0 (TBD)        - Major brand refresh (if needed)
```

---

## 📞 Contact & Questions

**Questions about brand?**
- Design lead: [Назначить ответственного]
- Product owner: [Назначить ответственного]

**Found an issue?**
- Create issue in project tracker
- Tag: `design`, `brand`, `documentation`

**Want to contribute?**
- Read [CONTRIBUTING.md](../../CONTRIBUTING.md)
- Follow brand guidelines
- Submit PR with updates

---

## 🌐 External Resources

### Design Systems (Inspiration)
- [Material Design 3](https://m3.material.io/)
- [IBM Carbon](https://carbondesignsystem.com/)
- [Atlassian Design System](https://atlassian.design/)

### Tools
- [Figma](https://figma.com) - UI design
- [Vuetify](https://vuetifyjs.com/) - Component library
- [WebAIM](https://webaim.org/resources/contrastchecker/) - Accessibility

### Learning
- [Refactoring UI](https://www.refactoringui.com/) - Design tips
- [Laws of UX](https://lawsofux.com/) - UX principles
- [Material Design Color Tool](https://material.io/resources/color/) - Color system

---

## 📊 Metrics & Success

### Brand Consistency Score

После implementation, оцени:
- [ ] Logo visible on all pages (5/5)
- [ ] Primary color used consistently (5/5)
- [ ] Typography hierarchy clear (5/5)
- [ ] Tone of voice maintained (5/5)
- [ ] Accessibility WCAG AA (5/5)

**Target**: 23/25 points (92%+)

---

## 🎉 Status

### Current State: ✅ READY FOR IMPLEMENTATION

**Completed:**
- ✅ Brand guide documentation (comprehensive)
- ✅ Implementation guide (step-by-step)
- ✅ Quick start guide (TL;DR)
- ✅ Visual references (inspiration)

**Next Steps:**
1. Review brand guide with team
2. Create SVG assets (logo, icons)
3. Implement code changes
4. Testing (visual, responsive, accessibility)
5. Deploy to staging
6. Gather feedback
7. Deploy to production

**Estimated timeline to production**: 1-2 weeks

---

## 📝 Document Metadata

| Property | Value |
|----------|-------|
| **Created** | 2025-10-28 |
| **Version** | 1.0 |
| **Status** | Production Ready |
| **Pages** | 4 documents (~29,000 words total) |
| **Last Updated** | 2025-10-28 |
| **Contributors** | Claude (AI), Design Team |

---

**🌿 Линней HR - Систематизируем ваши должности с научной точностью**

*"Как Карл Линней внёс порядок в хаос природы, так наш Линней систематизирует ваши HR-процессы."*

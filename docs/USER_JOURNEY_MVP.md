# 🎯 **USER JOURNEY - MVP СИСТЕМА ГЕНЕРАЦИИ ПРОФИЛЕЙ НА NICEGUI**

## 👤 **ЦЕЛЕВОЙ ПОЛЬЗОВАТЕЛЬ**
**HR-менеджер компании А101** - создает профили должностей для всех 3,098 сотрудников

## 🗺️ **ПОЛЬЗОВАТЕЛЬСКИЙ ПУТЬ - ЕДИНАЯ СТРАНИЦА**

### **УПРОЩЕННЫЙ FLOW:**
```
[Форма выбора] → [Генерация] → [Результат в реальном времени] → [Экспорт]
```

### **ЕДИНСТВЕННАЯ СТРАНИЦА - ВСЕ В ОДНОМ МЕСТЕ** 🎯
```
Пользователь открывает приложение:

┌─ ЛЕВАЯ ПАНЕЛЬ (30%) ──────────────────────┐
│ 📋 Генератор профилей А101                │
│                                           │
│ Блок:        [Dropdown ▼]                 │
│ Департамент: [Dropdown ▼] (реактивно)     │
│                                           │
│ [🚀 Сгенерировать профиль]               │
│                                           │
│ ⏳ Прогресс-бар (при генерации)           │
└───────────────────────────────────────────┘

┌─ ПРАВАЯ ПАНЕЛЬ (70%) ─────────────────────┐
│ 📋  │
│                                           │
│ Список должностей                         │
│ Должность 1   [Весия 1]                              │
│ Должность 2                                │
│ Должность 3                                │
│ Должность N                                │                              │
                                   │
│ [📄 JSON] [📊 Excel] [📝 MD]              │
└───────────────────────────────────────────┘
```

### **ПРОЦЕСС ГЕНЕРАЦИИ С УВЕДОМЛЕНИЯМИ** ⚡
```
Real-time feedback:
├─ 💫 "Загрузка данных компании..."
├─ 🔍 "Поиск релевантных KPI..."
├─ 🏗️ "Анализ примеров профилей..."
├─ 🤖 "Генерация через LLM..."
├─ ✨ "Форматирование результата..."
└─ ✅ "Профиль готов!" (зеленое уведомление)
```

## 🎨 **ДИЗАЙН ИНТЕРФЕЙСА NICEGUI**

### **Главная и единственная страница:**
```python
from nicegui import ui
import asyncio

@ui.page('/')
def main_page():
    # Material Design заголовок
    with ui.header(elevated=True).classes('items-center'):
        ui.label('🏢 Генератор профилей должностей А101').classes('text-h5')

    # Разделитель панелей (30% / 70%)
    with ui.splitter(value=30).classes('w-full h-full'):

        # ========== ЛЕВАЯ ПАНЕЛЬ - ФОРМА ==========
        with ui.splitter().before:
            with ui.card().classes('w-full'):
                ui.label('Параметры генерации').classes('text-h6 q-mb-md')

                # Реактивные селекты
                department_select = ui.select(
                    options=get_departments(),
                    label='Департамент',
                    value=None
                ).classes('w-full q-mb-sm')

                position_select = ui.select(
                    options=[],
                    label='Должность',
                    value=None
                ).classes('w-full q-mb-sm')

                employee_input = ui.input(
                    label='ФИО сотрудника (опционально)',
                    placeholder='Иванов Иван Иванович'
                ).classes('w-full q-mb-md')

                # Кнопка генерации
                generate_btn = ui.button(
                    '🚀 Сгенерировать профиль',
                    color='primary'
                ).classes('w-full')

                # Прогресс-бар
                progress = ui.linear_progress(value=0).classes('q-mt-md')
                progress.visible = False

        # ========== ПРАВАЯ ПАНЕЛЬ - РЕЗУЛЬТАТ ==========
        with ui.splitter().after:
            with ui.card().classes('w-full h-full'):

                # Табы результатов
                with ui.tabs().classes('w-full') as tabs:
                    tab1 = ui.tab('📋 Основное')
                    tab2 = ui.tab('🎯 Обязанности')
                    tab3 = ui.tab('🛠 Навыки')
                    tab4 = ui.tab('📊 KPI')

                with ui.tab_panels(tabs, value=tab1).classes('w-full'):
                    # Основная информация
                    with ui.tab_panel(tab1):
                        basic_info_json = ui.json_editor({}).classes('w-full')

                    # Обязанности
                    with ui.tab_panel(tab2):
                        with ui.scroll_area().classes('w-full h-96'):
                            responsibilities_md = ui.markdown('')

                    # Навыки
                    with ui.tab_panel(tab3):
                        skills_table = ui.table(
                            columns=[
                                {'name': 'category', 'label': 'Категория'},
                                {'name': 'skills', 'label': 'Навыки'},
                                {'name': 'level', 'label': 'Уровень'}
                            ],
                            rows=[]
                        ).classes('w-full')

                    # KPI
                    with ui.tab_panel(tab4):
                        with ui.scroll_area().classes('w-full h-96'):
                            kpi_md = ui.markdown('')

                # Кнопки экспорта
                with ui.card_actions():
                    with ui.row().classes('w-full justify-end'):
                        json_btn = ui.button('📄 JSON', color='grey-7')
                        excel_btn = ui.button('📊 Excel', color='green')
                        md_btn = ui.button('📝 Markdown', color='blue')

    # ========== EVENT HANDLERS ==========
    async def generate_profile_async():
        progress.visible = True
        progress.value = 0

        steps = [
            "💫 Загрузка данных компании...",
            "🔍 Поиск релевантных KPI...",
            "🏗️ Анализ примеров профилей...",
            "🤖 Генерация через LLM...",
            "✨ Форматирование результата..."
        ]

        for i, step in enumerate(steps):
            ui.notify(step, position='top-right')
            progress.value = (i + 1) / len(steps)
            await asyncio.sleep(0.8)

        # Обновление результатов
        await update_all_tabs()
        progress.visible = False
        ui.notify('✅ Профиль готов!', color='positive')

    department_select.on('update:model-value',
                        lambda e: update_positions(e.args))
    generate_btn.on('click', generate_profile_async)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Генератор профилей А101', port=8080)
```

## 🔄 **УПРОЩЕННЫЙ FLOW**

```
[Единая страница открыта]
        ↓
[Выбор департамента] → [Реактивное обновление должностей]
        ↓
[Выбор должности] → [Превью доступных данных]
        ↓
[Ввод ФИО (опц.)] → [Активация кнопки генерации]
        ↓
[🚀 Нажатие "Генерировать"] → [Асинхронная генерация]
        ↓
[Прогресс + Уведомления] → [Real-time обновление табов]
        ↓
[Результат готов] → [Кнопки экспорта активны]
```

## 🎨 **МАТЕРИАЛЬНЫЙ ДИЗАЙН ОСОБЕННОСТИ**

### **NiceGUI Material Design 3:**
- ✨ **Elevated cards** с тенями
- 🎯 **Material селекты** с анимациями
- 🔄 **Splitter панели** для адаптивности
- 💫 **Linear progress** с плавной анимацией
- 🔔 **Toast notifications** в углу экрана
- 📋 **JSON editor** с подсветкой синтаксиса

### **Реактивность:**
- **Департамент → Должности** автообновление
- **Real-time прогресс** с уведомлениями
- **Асинхронная генерация** без блокировки UI
- **Instant табы переключение**

## ⚡ **ТЕХНИЧЕСКИЕ ДЕТАЛИ**

### **Структура проекта:**
```
/prototype/
├── app.py                 # Главный Streamlit app
├── components/            # UI компоненты
│   ├── form.py           # Форма выбора
│   ├── result.py         # Показ результата
│   └── export.py         # Экспорт данных
├── core/                 # Бизнес-логика
│   ├── generator.py      # Генератор профилей
│   ├── data_loader.py    # Загрузчик данных
│   └── llm_client.py     # LLM интерфейс
└── assets/               # Статичные файлы
    └── a101_logo.png
```

### **State management:**
```python
# Session state для сохранения данных между запросами
if 'generated_profile' not in st.session_state:
    st.session_state.generated_profile = None

if 'selected_department' not in st.session_state:
    st.session_state.selected_department = None
```

## 🎯 **MVP FEATURES**

### **Must Have:**
- ✅ Выбор департамента/должности
- ✅ Генерация профиля через LLM
- ✅ Просмотр результата в табах
- ✅ Экспорт в JSON/Excel

### **Nice to Have:**
- 📊 Статистика созданных профилей
- ⚙️ Настройки LLM параметров
- ✏️ Режим редактирования результата
- 📱 Мобильная адаптация

## 🚀 **ПЛАН РЕАЛИЗАЦИИ С NICEGUI**

### **День 1: NiceGUI Setup + Backend**
1. ✅ Установка и настройка NiceGUI
2. ✅ Создание базового UI layout (splitter панели)
3. ✅ Реализация data_loader.py
4. ✅ Интеграция с LLM API (OpenAI/Claude)

### **День 2: UI Components + Logic**
1. ✅ Реактивные селекты (департамент → должности)
2. ✅ Табы с результатами (JSON editor, таблицы, markdown)
3. ✅ Асинхронная генерация с прогресс-баром
4. ✅ Toast уведомления и экспорт кнопки

### **День 3: Polish + Testing**
1. ✅ Material Design стилизация
2. ✅ Error handling и валидация
3. ✅ Тестирование на разных должностях
4. ✅ Документация и деплой

## 🎯 **КРИТЕРИИ УСПЕХА MVP**

- ✅ **Единая страница UI** - без лишних переходов
- ✅ **Генерирует профили** для 10+ должностей
- ✅ **Время генерации** < 30 секунд
- ✅ **Заполненность профиля** > 85%
- ✅ **JSON Schema** соответствие 100%
- ✅ **Material Design** профессиональный вид
- ✅ **Реактивность** - instant UI обновления
- ✅ **Экспорт** в 3 форматах (JSON/Excel/MD)

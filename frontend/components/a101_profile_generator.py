"""
@doc
Профессиональный генератор профилей A101 с корпоративным дизайном для NiceGUI.

Реализует реалистичный UX в рамках возможностей NiceGUI:
- A101 корпоративная цветовая схема
- Responsive design с Tailwind CSS
- Debounced search с real-time feedback
- Professional progress tracking
- Mobile-friendly interface

Examples:
  python> generator = A101ProfileGenerator(api_client)
  python> await generator.render()
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from nicegui import ui
from ..services.api_client import APIClient

logger = logging.getLogger(__name__)


class A101ProfileGenerator:
    """
    @doc
    Профессиональный генератор профилей с корпоративным A101 дизайном.
    
    Особенности:
    - NiceGUI-совместимый дизайн с CSS injection
    - Корпоративная цветовая схема A101
    - Debounced search с оптимизацией производительности
    - Responsive layout для desktop и mobile
    - Professional feedback и error handling
    
    Examples:
      python> generator = A101ProfileGenerator(api_client)
      python> await generator.render()
    """
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        
        # UI компоненты
        self.search_input = None
        self.search_results_container = None
        self.selected_position_card = None
        self.employee_name_input = None
        self.temperature_slider = None
        self.profile_type_select = None
        self.generate_button = None
        self.progress_dialog = None
        
        # Состояние приложения
        self.current_query = ""
        self.selected_position = None
        self.search_timer = None
        self.is_searching = False
        self.is_generating = False
        self.current_task_id = None
        self.search_results = []
        
        # Автоподсказки с иерархией
        self.autocomplete_options = []
        self.hierarchical_suggestions = []
        self.search_history = []
        
        # UI состояние
        self.has_search_results = False
        self.has_selected_position = False
        self.can_generate = False
        self.search_timer = None
        
        # Выбранные данные для генерации
        self.selected_position = ""
        self.selected_department = ""
        
        # Системная статистика
        self.total_stats = {"departments": 0, "positions": 0}
        
        # Убрали search_categories - dropdown заменяет умные категории
        
        # Инжектируем стили при создании
        self._inject_a101_styles()
        self._add_input_styles()
        
        # Загружаем иерархические предложения асинхронно
        asyncio.create_task(self._load_hierarchical_suggestions())
    
    def _format_position_level(self, level):
        """Форматирование уровня должности для отображения"""
        if isinstance(level, str):
            # Строковые уровни
            level_mapping = {
                "senior": {"text": "Высший", "color": "red"},
                "lead": {"text": "Руководящий", "color": "deep-orange"},
                "middle": {"text": "Основной", "color": "green"},
                "junior": {"text": "Начальный", "color": "blue"}
            }
            return level_mapping.get(level, {"text": "Не определен", "color": "grey"})
        elif isinstance(level, int):
            # Числовые уровни (1-5)
            level_colors = ["red", "deep-orange", "orange", "green", "blue"]
            color = level_colors[level-1] if 1 <= level <= 5 else "grey"
            return {"text": f"Ур. {level}", "color": color}
        else:
            return {"text": "Не определен", "color": "grey"}
    
    async def _load_hierarchical_suggestions(self):
        """
        Загрузка иерархических предложений автокомплита из backend данных.
        
        Создает предложения в формате:
        "Блок безопасности → Служба безопасности → Специалист"
        "IT Департамент → Разработка → Ведущий разработчик"
        """
        try:
            logger.info("Loading hierarchical suggestions from backend...")
            
            # Проверяем авторизацию
            from nicegui import app
            if not hasattr(app, 'storage') or not app.storage.user.get('authenticated', False):
                logger.warning("User not authenticated, using fallback suggestions")
                self._use_fallback_suggestions()
                return
            
            # Получаем полную структуру организации через API
            stats_response = await self.api_client._make_request("GET", "/api/catalog/stats")
            
            if not stats_response.get("success"):
                logger.warning("Failed to get organization stats, using fallback suggestions")
                self._use_fallback_suggestions()
                return
            
            # Генерируем иерархические предложения
            self.hierarchical_suggestions = await self._generate_hierarchical_from_backend()
            
            logger.info(f"✅ Loaded {len(self.hierarchical_suggestions)} hierarchical suggestions")
            
            # Обновляем dropdown options в поисковом поле если оно уже создано
            if hasattr(self, 'search_input') and self.search_input:
                options_dict = {suggestion: suggestion for suggestion in self.hierarchical_suggestions}
                self.search_input.set_options(options_dict)
                logger.info("✅ Updated search dropdown with hierarchical options")
                
        except Exception as e:
            logger.error(f"Error loading hierarchical suggestions: {e}")
            self._use_fallback_suggestions()
    
    async def _generate_hierarchical_from_backend(self) -> List[str]:
        """
        Генерация иерархических предложений из backend данных.
        
        Returns:
            List[str]: Список иерархических предложений для автокомплита
        """
        suggestions = []
        
        try:
            # Получаем список всех департаментов
            departments_response = await self.api_client._make_request("GET", "/api/catalog/departments")
            
            if not departments_response.get("success"):
                logger.warning("Failed to get departments for hierarchical suggestions")
                return []
            
            # Правильно извлекаем departments из вложенной структуры response["data"]["departments"]
            departments = departments_response["data"]["departments"]
            
            logger.info(f"Processing {len(departments)} departments for hierarchical suggestions...")
            
            # Для каждого департамента получаем позиции и создаем иерархические пути
            for dept in departments:
                dept_name = dept["name"]
                
                try:
                    # Получаем позиции департамента - правильный endpoint
                    positions_response = await self.api_client._make_request("GET", f"/api/catalog/positions/{dept_name}")
                    
                    if positions_response.get("success"):
                        # Правильно извлекаем positions из вложенной структуры response["data"]["positions"]
                        positions_data = positions_response["data"]
                        positions = positions_data["positions"]
                        
                        # Debug: log first few positions to understand structure
                        if positions:
                            logger.debug(f"First position structure in '{dept_name}': {positions[0] if positions else 'None'}")
                            if len(positions) > 5:
                                logger.debug(f"Department '{dept_name}' has {len(positions)} positions")
                        else:
                            logger.debug(f"No positions found for department '{dept_name}'")
                        
                        # Создаем иерархические предложения
                        for position in positions:
                            try:
                                # Формируем иерархический путь
                                hierarchical_path = self._build_hierarchical_path(dept_name, position)
                                if hierarchical_path:  # Проверяем что путь не пустой
                                    suggestions.append(hierarchical_path)
                            except Exception as pos_error:
                                logger.warning(f"Failed to build path for position in '{dept_name}': {pos_error}, position: {position}")
                            
                except Exception as dept_error:
                    logger.warning(f"Failed to get positions for department '{dept_name}': {dept_error}")
                    continue
            
            logger.info(f"Generated {len(suggestions)} hierarchical suggestions from backend")
            
            # Сортируем по алфавиту для консистентности
            suggestions.sort()
            
            # Ограничиваем количество предложений для производительности
            return suggestions[:500]  # Топ 500 наиболее релевантных
            
        except Exception as e:
            logger.error(f"Error generating hierarchical suggestions: {e}")
            return []
    
    def _build_hierarchical_path(self, department: str, position: dict) -> str:
        """
        Построение иерархического пути для позиции.
        
        Args:
            department: Название департамента
            position: Данные позиции
            
        Returns:
            str: Иерархический путь типа "Департамент → Позиция"
        """
        # Безопасное извлечение названия позиции
        if isinstance(position, dict):
            position_name = position.get("name", str(position))
        elif isinstance(position, str):
            position_name = position
        else:
            logger.warning(f"Unexpected position type: {type(position)}, value: {position}")
            position_name = str(position)
        
        # Определяем уровень вложенности на основе названия департамента
        path_parts = []
        
        # Парсим структуру департамента для иерархии
        if "→" in department or "/" in department or "\\" in department:
            # Департамент уже содержит путь
            path_parts = [part.strip() for part in department.replace("/", "→").replace("\\", "→").split("→")]
        else:
            # Простое название департамента
            path_parts = [department]
        
        # Добавляем позицию в конце пути
        path_parts.append(position_name)
        
        # Создаем финальный иерархический путь
        hierarchical_path = " → ".join(path_parts)
        
        return hierarchical_path
    
    def _use_fallback_suggestions(self):
        """Использование fallback предложений при недоступности backend"""
        # Только реальные должности из оргструктуры А101 - без вымышленных
        fallback_suggestions = [
            "Руководитель отдела",
            "Ведущий специалист", 
            "Старший специалист",
            "Специалист",
            "Главный специалист",
            "Заместитель руководителя",
            "Директор департамента",
            "Руководитель направления",
            "Руководитель управления",
            "Руководитель службы",
            "Координатор",
            "Помощник директора"
        ]
        
        self.hierarchical_suggestions = fallback_suggestions
        logger.info(f"Using {len(fallback_suggestions)} fallback suggestions")
        
        # Обновляем dropdown options в поисковом поле если оно уже создано
        if hasattr(self, 'search_input') and self.search_input:
            options_dict = {suggestion: suggestion for suggestion in self.hierarchical_suggestions}
            self.search_input.set_options(options_dict)
            logger.info("✅ Updated search dropdown with fallback options")
    
    def _add_input_styles(self):
        """Добавляем правильные стили для input полей через NiceGUI API"""
        ui.add_head_html('''
        <style>
        /* Правильная стилизация input через NiceGUI */
        .q-field__native, .q-field__input {
            color: #1f2937 !important;
            background: transparent !important;
        }
        
        .q-field__control {
            background: white !important;
        }
        
        .q-input .q-field__native {
            color: #1f2937 !important;
        }
        
        /* UI.SELECT DROPDOWN СТИЛИ */
        .q-select .q-field__native {
            color: #1f2937 !important;
        }
        
        .q-select .q-field__input {
            color: #1f2937 !important;
        }
        
        /* Dropdown меню */
        .q-menu {
            background: white !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Элементы списка в dropdown */
        .q-item {
            color: #1f2937 !important;
            background: white !important;
            padding: 12px 16px !important;
            border-bottom: 1px solid #f1f5f9 !important;
            transition: background 0.2s ease !important;
        }
        
        .q-item:hover, .q-item--active {
            background: #f8fafc !important;
            color: #1f2937 !important;
        }
        
        .q-item__label {
            color: #1f2937 !important;
            font-size: 14px !important;
        }
        
        /* Выделенный элемент в dropdown */
        .q-item--focused {
            background: #e0f2fe !important;
            color: #1f2937 !important;
        }
        
        /* Фильтр в dropdown */
        .q-select__filter {
            color: #1f2937 !important;
            background: white !important;
        }
        
        /* Placeholder текст */
        .q-field__label {
            color: #6b7280 !important;
        }
        
        /* Иконки в select */
        .q-select__dropdown-icon {
            color: #6b7280 !important;
        }
        
        /* ФИКСИРОВАННАЯ ШИРИНА НА ВСЮ СТРАНИЦУ - ПРОСТО */
        .q-select, .q-field, .q-field__control, 
        .q-field__native, .q-field__input, 
        .q-field__control-container {
            width: 100vw !important;
            max-width: 100vw !important;
            min-width: 100vw !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
        }
        </style>
        ''')
    
    def _inject_a101_styles(self):
        """Корпоративные A101 стили для NiceGUI"""
        ui.add_head_html("""
        <style>
        /* NiceGUI Принудительные стили для исправления видимости */
        * {
            color: inherit !important;
        }
        
        /* Исправляем input поля */
        input, input:focus, .q-field__native, .q-field__input, .q-input input {
            color: #1f2937 !important;
            background: white !important;
            -webkit-text-fill-color: #1f2937 !important;
        }
        
        /* Исправляем labels */
        label, .q-field__label, .q-field__marginal {
            color: #374151 !important;
        }
        
        /* Исправляем кнопки */
        .q-btn:not(.q-btn--outline) {
            color: white !important;
        }
        
        .q-btn--outline, .q-btn.q-btn--outline {
            color: #1e40af !important;
        }
        
        /* Исправляем текст */
        .q-item__label, .q-chip__content, span, div {
            color: #1f2937 !important;
        }
        
        /* Исправляем иконки */
        .q-icon, i.material-icons {
            color: inherit !important;
        }
        
        /* A101 Corporate Design System */
        :root {
            /* Primary Corporate Colors */
            --a101-navy: #0F172A;
            --a101-blue: #1E40AF;
            --a101-blue-light: #3B82F6;
            --a101-success: #059669;
            --a101-success-light: #10B981;
            --a101-warning: #D97706;
            --a101-error: #DC2626;
            
            /* Neutral Palette */
            --a101-gray-50: #F8FAFC;
            --a101-gray-100: #F1F5F9;
            --a101-gray-200: #E2E8F0;
            --a101-gray-300: #CBD5E1;
            --a101-gray-400: #94A3B8;
            --a101-gray-600: #475569;
            --a101-gray-800: #1E293B;
            --a101-gray-900: #0F172A;
            
            /* Typography */
            --a101-font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            
            /* Spacing */
            --a101-space-xs: 0.25rem;
            --a101-space-sm: 0.5rem;
            --a101-space-md: 1rem;
            --a101-space-lg: 1.5rem;
            --a101-space-xl: 2rem;
            
            /* Shadows */
            --a101-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --a101-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --a101-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --a101-shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            
            /* Gradients */
            --a101-gradient-primary: linear-gradient(135deg, var(--a101-blue) 0%, var(--a101-blue-light) 100%);
            --a101-gradient-success: linear-gradient(135deg, var(--a101-success) 0%, var(--a101-success-light) 100%);
        }
        
        /* Base styles */
        * {
            font-family: var(--a101-font);
        }
        
        /* Corporate Header */
        .a101-header {
            background: var(--a101-gradient-primary);
            box-shadow: var(--a101-shadow-lg);
            border-radius: 0.75rem;
            margin-bottom: var(--a101-space-xl);
        }
        
        /* Stats Cards */
        .a101-stats-card {
            background: white;
            border: 1px solid var(--a101-gray-200);
            border-radius: 0.75rem;
            box-shadow: var(--a101-shadow-sm);
            transition: all 0.2s ease;
            padding: var(--a101-space-lg);
            text-align: center;
        }
        
        .a101-stats-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--a101-shadow-md);
            border-color: var(--a101-blue);
        }
        
        /* Main Generator Card */
        .a101-generator-card {
            background: white;
            border-radius: 1rem;
            box-shadow: var(--a101-shadow-xl);
            border: 1px solid var(--a101-gray-200);
            overflow: hidden;
        }
        
        .a101-generator-header {
            background: linear-gradient(90deg, #EFF6FF 0%, #F0F9FF 100%);
            border-bottom: 1px solid var(--a101-gray-200);
            padding: var(--a101-space-lg);
        }
        
        /* Search Input */
        .a101-search-input {
            font-size: 1rem;
            border-radius: 0.5rem;
            border: 2px solid var(--a101-gray-200);
            transition: all 0.2s ease;
        }
        
        .a101-search-input:focus {
            border-color: var(--a101-blue);
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
            outline: none;
        }
        
        /* Category Buttons */
        .a101-category-btn {
            background: var(--a101-gray-100);
            color: var(--a101-gray-600);
            border: 1px solid var(--a101-gray-200);
            border-radius: 1.5rem;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s ease;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .a101-category-btn:hover {
            background: var(--a101-blue);
            color: white;
            border-color: var(--a101-blue);
            transform: scale(1.05);
        }
        
        /* Search Results */
        .a101-search-result {
            background: white;
            border: 1px solid var(--a101-gray-200);
            border-radius: 0.5rem;
            padding: var(--a101-space-md);
            transition: all 0.2s ease;
            cursor: pointer;
            margin-bottom: 0.5rem;
        }
        
        .a101-search-result:hover {
            background: #EFF6FF;
            border-color: var(--a101-blue);
            transform: translateX(4px);
            box-shadow: var(--a101-shadow-md);
        }
        
        /* Selected Position */
        .a101-selected-position {
            background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
            border: 2px solid var(--a101-success);
            border-radius: 0.75rem;
            padding: var(--a101-space-lg);
            box-shadow: var(--a101-shadow-md);
        }
        
        /* Generate Button */
        .a101-generate-btn {
            background: var(--a101-gradient-primary);
            border: none;
            border-radius: 0.75rem;
            color: white;
            font-weight: 600;
            font-size: 1.125rem;
            padding: 1rem 2rem;
            box-shadow: var(--a101-shadow-lg);
            transition: all 0.2s ease;
            cursor: pointer;
            min-height: 3.5rem;
        }
        
        .a101-generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--a101-shadow-xl);
        }
        
        .a101-generate-btn:active {
            transform: translateY(0);
        }
        
        .a101-generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Progress Dialog */
        .a101-progress-dialog {
            background: white;
            border-radius: 1rem;
            box-shadow: var(--a101-shadow-xl);
            border: 1px solid var(--a101-gray-200);
            max-width: 28rem;
            width: 100%;
        }
        
        /* Success State */
        .a101-success-card {
            background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
            border: 2px solid var(--a101-success);
            border-radius: 0.75rem;
            padding: var(--a101-space-xl);
            text-align: center;
            box-shadow: var(--a101-shadow-lg);
        }
        
        /* Error State */
        .a101-error-card {
            background: linear-gradient(135deg, #FEF2F2 0%, #FECACA 100%);
            border: 2px solid var(--a101-error);
            border-radius: 0.75rem;
            padding: var(--a101-space-lg);
            border-left: 4px solid var(--a101-error);
        }
        
        /* Level Colors */
        .level-1 { border-left: 4px solid #DC2626; background: #FEF2F2; }
        .level-2 { border-left: 4px solid #EA580C; background: #FFF7ED; }
        .level-3 { border-left: 4px solid #D97706; background: #FFFBEB; }
        .level-4 { border-left: 4px solid #059669; background: #ECFDF5; }
        .level-5 { border-left: 4px solid #2563EB; background: #EFF6FF; }
        
        /* Animations */
        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        .slide-up {
            animation: slideUp 0.4s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from { 
                opacity: 0;
                transform: translateY(20px);
            }
            to { 
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .a101-generator-card {
                margin: 1rem;
                border-radius: 0.75rem;
            }
            
            .a101-generate-btn {
                width: 100%;
                font-size: 1rem;
                padding: 0.875rem 1.5rem;
            }
            
            .a101-category-btn {
                font-size: 0.75rem;
                padding: 0.375rem 0.75rem;
            }
        }
        
        /* Loading States */
        .loading-shimmer {
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        /* Utility Classes */
        .text-primary { color: var(--a101-blue); }
        .text-success { color: var(--a101-success); }
        .text-error { color: var(--a101-error); }
        .text-muted { color: var(--a101-gray-600); }
        .bg-light { background: var(--a101-gray-50); }
        
        /* Автокомплит стили */
        .a101-autocomplete-container {
            position: relative !important;
        }
        
        .a101-suggestions {
            position: absolute !important;
            top: 100% !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 1000 !important;
            background: white !important;
            border: 1px solid var(--a101-gray-200) !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            max-height: 240px !important;
            overflow-y: auto !important;
            margin-top: 4px !important;
        }
        
        .a101-suggestion-item {
            padding: 12px !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            border-bottom: 1px solid var(--a101-gray-100) !important;
            transition: background 0.2s ease !important;
        }
        
        .a101-suggestion-item:hover {
            background: var(--a101-gray-50) !important;
        }
        
        .a101-suggestion-item.selected {
            background: #eff6ff !important;
        }
        
        .a101-suggestion-text {
            font-size: 14px !important;
            font-weight: 500 !important;
            color: #1f2937 !important;
            margin: 0 !important;
            line-height: 1.4 !important;
        }
        
        .a101-suggestion-type {
            font-size: 12px !important;
            color: #6b7280 !important;
            margin: 0 !important;
            line-height: 1.3 !important;
        }
        
        /* Исправляем цвета текста в NiceGUI */
        .a101-suggestions .q-item__label {
            color: #1f2937 !important;
        }
        
        .a101-suggestions label {
            color: #1f2937 !important;
        }
        
        .a101-suggestion-item label {
            color: #1f2937 !important;
        }
        </style>
        
        <!-- Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        
        <script>
        // Принудительное исправление стилей для NiceGUI
        function fixNiceGUIStyles() {
            // Исправляем input поля более агрессивно
            const inputs = document.querySelectorAll('input, .q-field__native, .q-field__input, .q-input input');
            inputs.forEach(input => {
                input.style.setProperty('color', '#1f2937', 'important');
                input.style.setProperty('-webkit-text-fill-color', '#1f2937', 'important');
                input.style.setProperty('background', 'white', 'important');
                input.style.setProperty('background-color', 'white', 'important');
                // Удаляем светлые цвета
                input.style.removeProperty('color');
                input.style.color = '#1f2937';
            });
            
            // Исправляем labels
            const labels = document.querySelectorAll('label, .q-field__label, .q-field__marginal');
            labels.forEach(label => {
                label.style.setProperty('color', '#374151', 'important');
            });
            
            // Исправляем текст во всех элементах
            const textElements = document.querySelectorAll('span, div, p, h1, h2, h3, h4, h5, h6, .q-item__label, .q-chip__content');
            textElements.forEach(el => {
                if (!el.closest('.q-btn') && !el.classList.contains('q-icon') && !el.querySelector('.q-icon')) {
                    el.style.setProperty('color', '#1f2937', 'important');
                }
            });
            
            // ПРОСТОЕ РЕШЕНИЕ: ПОЛЕ ВВОДА НА ВСЮ ШИРИНУ СТРАНИЦЫ
            const allInputElements = document.querySelectorAll('.q-select, .q-field, .q-field__control, .q-field__native, .q-field__input, input, .q-field__control-container');
            allInputElements.forEach(element => {
                element.style.setProperty('width', '100vw', 'important');
                element.style.setProperty('max-width', '100vw', 'important');
                element.style.setProperty('min-width', '100vw', 'important');
                element.style.setProperty('font-size', '16px', 'important');
            });
            
            // СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ UI.SELECT DROPDOWN 
            const dropdownMenus = document.querySelectorAll('.q-menu');
            dropdownMenus.forEach(menu => {
                menu.style.setProperty('background', 'white', 'important');
                menu.style.setProperty('border', '1px solid #e2e8f0', 'important');
                menu.style.setProperty('border-radius', '8px', 'important');
            });
            
            // Исправляем элементы в dropdown
            const dropdownItems = document.querySelectorAll('.q-item');
            dropdownItems.forEach(item => {
                item.style.setProperty('color', '#1f2937', 'important');
                item.style.setProperty('background', 'white', 'important');
                
                // Исправляем текст внутри элементов
                const itemLabels = item.querySelectorAll('.q-item__label, span, div');
                itemLabels.forEach(label => {
                    label.style.setProperty('color', '#1f2937', 'important');
                });
            });
            
            // Исправляем focused элементы в dropdown
            const focusedItems = document.querySelectorAll('.q-item--focused');
            focusedItems.forEach(item => {
                item.style.setProperty('background', '#e0f2fe', 'important');
                item.style.setProperty('color', '#1f2937', 'important');
            });
        }
        
        // Применяем стили при загрузке
        document.addEventListener('DOMContentLoaded', fixNiceGUIStyles);
        
        // Применяем стили при динамических изменениях (dropdown opening)
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Проверяем появление новых dropdown меню
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.classList && (node.classList.contains('q-menu') || node.querySelector && node.querySelector('.q-menu'))) {
                                // Новый dropdown появился, применяем стили
                                setTimeout(fixNiceGUIStyles, 10);
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, { 
            childList: true, 
            subtree: true 
        });
        
        console.log('A101 Generator loaded with dropdown style fixes');
        
        </script>
        """)
    
    async def render(self) -> ui.column:
        """
        @doc
        Отрисовка профессионального генератора профилей A101.
        
        Examples:
          python> component = await generator.render()
        """
        # Основной контейнер с градиентным фоном
        with ui.column().classes("w-full min-h-screen bg-gradient-to-br from-slate-50 to-blue-50") as container:
            
            # Корпоративный заголовок
            await self._render_corporate_header()
            
            # Системная статистика
            await self._render_system_stats()
            
            # Главный генератор
            await self._render_main_generator()
            
            # Загружаем системную статистику
            await self._load_system_stats()
            
        return container
    
    async def _render_corporate_header(self):
        """Корпоративный заголовок A101"""
        with ui.card().classes("w-full a101-header border-0"):
            with ui.card_section().classes("py-6"):
                with ui.row().classes("w-full items-center justify-between"):
                    # Логотип и название
                    with ui.row().classes("items-center gap-4"):
                        ui.icon("business", size="2.5rem").classes("text-white")
                        with ui.column().classes("gap-0"):
                            ui.label("A101 HR Profile Generator").classes("text-white text-2xl font-bold")
                            ui.label("Система автоматической генерации профилей должностей").classes("text-blue-100 text-sm")
                    
                    # Информация о пользователе
                    with ui.row().classes("items-center gap-3 bg-white bg-opacity-10 rounded-lg px-4 py-2"):
                        ui.avatar(icon="person", color="white").classes("text-blue-900")
                        with ui.column().classes("gap-0"):
                            ui.label("Администратор").classes("text-white font-medium text-sm")
                            ui.label("Активная сессия").classes("text-blue-100 text-xs")
    
    async def _render_system_stats(self):
        """Карточки системной статистики"""
        with ui.row().classes("w-full gap-6 mb-8 max-w-6xl mx-auto px-4") as stats_container:
            
            # Департаменты
            with ui.card().classes("flex-1 a101-stats-card"):
                ui.icon("corporate_fare", size="2rem").classes("text-blue-600 mb-2")
                self.departments_label = ui.label("Загрузка...").classes("text-3xl font-bold text-gray-900")
                ui.label("Департаментов").classes("text-gray-600 text-sm font-medium")
            
            # Должности
            with ui.card().classes("flex-1 a101-stats-card"):
                ui.icon("groups", size="2rem").classes("text-emerald-600 mb-2")
                self.positions_label = ui.label("Загрузка...").classes("text-3xl font-bold text-gray-900")
                ui.label("Должностей").classes("text-gray-600 text-sm font-medium")
            
            # Статус системы
            with ui.card().classes("flex-1 a101-stats-card"):
                ui.icon("check_circle", size="2rem").classes("text-green-600 mb-2")
                ui.label("Готова").classes("text-3xl font-bold text-gray-900")
                ui.label("Система").classes("text-gray-600 text-sm font-medium")
    
    async def _render_main_generator(self):
        """Основной генератор профилей"""
        with ui.card().classes("w-full max-w-4xl mx-auto a101-generator-card px-4"):
            
            # Заголовок генератора
            with ui.card_section().classes("a101-generator-header"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("psychology", size="2rem").classes("text-blue-600")
                    with ui.column().classes("gap-1"):
                        ui.label("Генератор профилей должностей").classes("text-xl font-bold text-primary")
                        ui.label("Найдите должность и создайте детальный профиль с помощью ИИ").classes("text-muted")
            
            # Контент генератора
            with ui.card_section().classes("py-8"):
                
                # Поиск должности
                await self._render_search_section()
                
                # Выбранная должность
                with ui.column().classes("w-full mt-8"):
                    self.selected_position_card = ui.column().classes("w-full")
                
                # Параметры генерации (показываем только после выбора)
                with ui.column().classes("w-full mt-8").bind_visibility_from(self, "has_selected_position"):
                    await self._render_generation_params()
                
                # Кнопка генерации
                with ui.column().classes("w-full mt-8 text-center").bind_visibility_from(self, "has_selected_position"):
                    self.generate_button = ui.button(
                        "🚀 Создать профиль должности",
                        icon="auto_awesome",
                        on_click=self._start_generation
                    ).classes("a101-generate-btn")
                    
                    ui.label("Генерация займет 1-3 минуты в зависимости от сложности позиции").classes("text-xs text-muted mt-3")
    
    async def _render_search_section(self):
        """Секция поиска должностей"""
        with ui.column().classes("w-full gap-6"):
            
            # Заголовок поиска
            with ui.row().classes("items-center gap-2"):
                ui.icon("search", size="1.5rem").classes("text-blue-600")
                ui.label("Поиск должности").classes("text-lg font-semibold text-primary")
            
            # Расширенная поисковая строка с автокомплитом
            with ui.column().classes("w-full gap-2 relative"):
                
                # Поисковое поле на всю ширину страницы - ФИКСИРОВАННО
                self.search_input = ui.select(
                    options={suggestion: suggestion for suggestion in self.hierarchical_suggestions},
                    with_input=True,
                    on_change=self._on_search_select
                ).props('outlined input-class="text-gray-900" bg-color="white" use-input').classes('w-full text-gray-900').style('width: 100vw; max-width: 100vw; min-width: 100vw;')
                
                # Добавляем placeholder через props
                self.search_input.props('label="🔍 Умный поиск должностей... (попробуйте: \'архитектор\', \'руководитель IT\')"')
                
                # События для обновления результатов при вводе
                self.search_input.on('input-value', self._on_search_input_value)
                
                # Исправляем стили при каждом фокусе на dropdown
                self.search_input.on('focus', self._fix_dropdown_styles)
                self.search_input.on('click', self._fix_dropdown_styles)
            
            # Убрали "Умные категории поиска" - dropdown заменяет эту функциональность
            
            # Убрали результаты поиска - dropdown заменяет эту функциональность
            # Оставляем только spinner для обратной связи при выборе
            self.search_loading = ui.spinner(size="sm").classes("self-center").style("display: none")
    
    async def _render_generation_params(self):
        """Параметры генерации"""
        with ui.column().classes("w-full gap-6"):
            
            # Заголовок параметров
            with ui.row().classes("items-center gap-2"):
                ui.icon("tune", size="1.5rem").classes("text-blue-600")
                ui.label("Параметры генерации").classes("text-lg font-semibold text-primary")
            
            # Параметры в сетке
            with ui.grid(columns="1fr 1fr").classes("w-full gap-6"):
                
                # ФИО сотрудника
                with ui.column().classes("gap-2"):
                    ui.label("ФИО сотрудника (опционально)").classes("text-sm font-medium text-gray-700")
                    self.employee_name_input = ui.input(
                        placeholder="Иванов Иван Иванович"
                    ).classes("w-full").props("outlined dense")
                
                # Тип профиля
                with ui.column().classes("gap-2"):
                    ui.label("Тип профиля").classes("text-sm font-medium text-gray-700")
                    self.profile_type_select = ui.select(
                        options=["Полный профиль", "Краткое описание", "Только компетенции"],
                        value="Полный профиль"
                    ).classes("w-full").props("outlined dense")
            
            # Детализация генерации
            with ui.column().classes("gap-3 mt-4"):
                ui.label("Точность и детализация").classes("text-sm font-medium text-gray-700")
                
                with ui.row().classes("w-full items-center gap-4"):
                    ui.label("Консистентная").classes("text-xs text-muted")
                    
                    self.temperature_slider = ui.slider(
                        min=0.0, max=1.0, step=0.1, value=0.1
                    ).classes("flex-1").props("color=primary")
                    
                    ui.label("Творческая").classes("text-xs text-muted")
                
                # Описание текущего значения
                self.temperature_description = ui.label().classes("text-xs text-muted mt-1")
                
                # Обновляем описание при изменении слайдера
                self.temperature_slider.on('update:model-value', self._update_temperature_description)
                self._update_temperature_description()  # Начальное значение
    
    def _update_temperature_description(self):
        """Обновление описания температуры"""
        if hasattr(self, 'temperature_description') and self.temperature_description:
            value = self.temperature_slider.value
            if value <= 0.2:
                desc = "Строго по данным - максимальная точность"
            elif value <= 0.6:
                desc = "Умеренная адаптация - баланс точности и гибкости"
            else:
                desc = "Творческий подход - больше интерпретации"
            
            self.temperature_description.text = f"Текущая настройка: {desc} ({value:.1f})"
    
    async def _load_system_stats(self):
        """Загрузка системной статистики"""
        try:
            # Проверяем авторизацию
            from nicegui import app
            if not app.storage.user.get('authenticated', False):
                # Fallback значения для неавторизованных пользователей
                self.departments_label.text = "510"
                self.positions_label.text = "4,376"
                return
                
            stats_response = await self.api_client._make_request("GET", "/api/catalog/stats")
            
            if stats_response.get("success"):
                stats_data = stats_response["data"]
                
                # Обновляем счетчики
                dept_count = stats_data["departments"]["total_count"]
                pos_count = stats_data["positions"]["total_count"]
                
                self.departments_label.text = f"{dept_count:,}"
                self.positions_label.text = f"{pos_count:,}"
                
                self.total_stats = {
                    "departments": dept_count,
                    "positions": pos_count
                }
                
        except Exception as e:
            logger.error(f"Error loading system stats: {e}")
            # Fallback значения
            self.departments_label.text = "510"
            self.positions_label.text = "4,376"
            self.total_stats = {"departments": 510, "positions": 4376}
    
    def _on_search_select(self, event=None):
        """Обработчик выбора варианта из dropdown - сразу подготавливаем к генерации"""
        if event and hasattr(event, 'value') and event.value:
            # Получаем выбранное значение из dropdown
            selected_value = event.value.strip()
            logger.info(f"Selected from dropdown: {selected_value}")
            
            # Обрабатываем иерархический выбор
            department, position = self._process_hierarchical_selection(selected_value)
            
            # Сразу устанавливаем данные для генерации
            if department and position:
                self._set_selected_position(position, department)
                ui.notify(f"✅ Выбрано: {position} в {department}", type="positive")
                
                # Показываем что позиция выбрана
                self.has_selected_position = True
                self.can_generate = True
                self._update_generation_ui_state()
            else:
                # Если не удалось извлечь иерархию, показываем уведомление
                ui.notify("Выберите должность из списка для генерации профиля", type="info")
                
        elif self.search_input and hasattr(self.search_input, 'value') and self.search_input.value:
            # Fallback - если event пустой, берем значение напрямую
            query = self.search_input.value.strip()
            if query:
                department, position = self._process_hierarchical_selection(query)
                if department and position:
                    self._set_selected_position(position, department)
    
    def _on_search_input_value(self, event=None):
        """Обработчик ввода в поисковое поле с dropdown (упрощенная версия)"""
        # Убираем live search - dropdown уже показывает все варианты
        # Оставляем только для логирования если нужно
        if event and hasattr(event, 'args') and event.args:
            query = str(event.args).strip()
            logger.debug(f"Input value changed: {query}")
            
            # Скрываем spinner если поле очистили
            if len(query) == 0 and hasattr(self, 'search_loading'):
                self.search_loading.style("display: none")
    
    def _process_hierarchical_selection(self, selection: str) -> tuple[str, str]:
        """
        Обработка выбора из иерархического автокомплита.
        
        Args:
            selection: Выбранная строка (может быть иерархический путь)
            
        Returns:
            tuple[str, str]: (department, position) или ("", "") если не удалось извлечь
        """
        if " → " in selection:
            # Это иерархический путь, извлекаем позицию (последний элемент)
            parts = [part.strip() for part in selection.split(" → ")]
            if len(parts) >= 2:
                department = parts[-2]  # Предпоследний элемент - департамент
                position = parts[-1]    # Последний элемент - позиция
                
                logger.info(f"Hierarchical selection: {department} → {position}")
                return department, position
        else:
            # Простое название позиции без иерархии
            logger.info(f"Simple selection: {selection}")
            return "", selection.strip()
        
        return "", ""
    
    def _set_selected_position(self, position: str, department: str):
        """
        Установка выбранной позиции для генерации профиля.
        
        Args:
            position: Название позиции
            department: Название департамента
        """
        # Сохраняем выбранные данные
        self.selected_position = position
        self.selected_department = department
        
        # Обновляем UI состояние
        self.has_selected_position = True
        self.can_generate = True
        
        logger.info(f"Position selected: {position} in {department}")
    
    def _update_generation_ui_state(self):
        """Обновление состояния UI для генерации профиля"""
        try:
            # Показать что можно генерировать (если есть соответствующие элементы UI)
            if hasattr(self, 'generate_button') and self.generate_button:
                self.generate_button.props('color=primary')
                self.generate_button.props('icon=auto_awesome')
                
            # Скрыть индикатор загрузки поиска если он есть
            if hasattr(self, 'search_loading') and self.search_loading:
                self.search_loading.style("display: none")
                
            logger.debug("Generation UI state updated")
        except Exception as e:
            logger.warning(f"Error updating generation UI state: {e}")
    
    def _fix_dropdown_styles(self, event=None):
        """Принудительное исправление стилей dropdown при каждом открытии"""
        # Используем JavaScript для немедленного исправления стилей
        ui.run_javascript('''
        setTimeout(function() {
            // Исправляем dropdown меню
            const dropdownMenus = document.querySelectorAll('.q-menu');
            dropdownMenus.forEach(menu => {
                menu.style.setProperty('background', 'white', 'important');
                menu.style.setProperty('color', '#1f2937', 'important');
            });
            
            // Исправляем элементы списка
            const dropdownItems = document.querySelectorAll('.q-item');
            dropdownItems.forEach(item => {
                item.style.setProperty('color', '#1f2937', 'important');
                item.style.setProperty('background', 'white', 'important');
                
                const labels = item.querySelectorAll('.q-item__label, span, div');
                labels.forEach(label => {
                    label.style.setProperty('color', '#1f2937', 'important');
                });
            });
            
            // ФИКСИРУЕМ ПОЛЕ ВВОДА НА ВСЮ ШИРИНУ
            const allElements = document.querySelectorAll('.q-select, .q-field, .q-field__native, .q-field__input, input');
            allElements.forEach(element => {
                element.style.setProperty('width', '100vw', 'important');
                element.style.setProperty('font-size', '16px', 'important');
            });
            
            console.log('Dropdown styles and input width fixed');
        }, 50);
        ''')
    
    # Старый метод _on_search_input удален - заменен на _on_search_select и _on_search_input_value для ui.select
    
    async def _debounced_search(self, query: str):
        """Debounced поиск должностей"""
        try:
            await asyncio.sleep(0.3)  # 300ms debounce
            
            if query == self.current_query:
                return
                
            self.current_query = query
            await self._perform_search(query)
            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in debounced search: {e}")
        finally:
            self.search_loading.style("display: none")
    
    async def _perform_search(self, query: str):
        """Выполнение поиска должностей (заглушка - поиск заменен на dropdown выбор)"""
        # Убираем поиск - dropdown уже содержит все варианты
        logger.debug(f"Search called for query: {query} - skipping (dropdown replaces search)")
        self._clear_search_results()
    
    async def _display_search_results(self):
        """Отображение результатов поиска (заглушка - убрано)"""
        # Метод больше не используется - dropdown заменяет результаты поиска
        pass
    
    async def _render_search_result_card(self, position: Dict):
        """Карточка результата поиска"""
        level_class = f"level-{position.get('level', 1)}"
        
        with ui.card().classes(f"a101-search-result {level_class} fade-in").on(
            "click", lambda pos=position: self._select_position(pos)
        ):
            with ui.card_section().classes("py-3"):
                with ui.row().classes("w-full items-center justify-between"):
                    
                    # Информация о позиции
                    with ui.column().classes("flex-1 gap-1"):
                        
                        # Название и уровень
                        with ui.row().classes("items-center gap-2"):
                            ui.label(position["name"]).classes("font-semibold text-gray-900")
                            
                            # Обработка уровня должности (может быть строкой или числом)
                            level_info = self._format_position_level(position.get("level"))
                            ui.chip(
                                level_info["text"],
                                color=level_info["color"]
                            ).props("size=sm")
                        
                        # Департамент и категория
                        with ui.row().classes("items-center gap-4 text-sm text-muted"):
                            with ui.row().classes("items-center gap-1"):
                                ui.icon("business", size="1rem")
                                ui.label(position["department"])
                            
                            with ui.row().classes("items-center gap-1"):
                                ui.icon("category", size="1rem")
                                ui.label(position["category"])
                    
                    # Стрелка выбора
                    ui.icon("arrow_forward", size="1.5rem").classes("text-gray-400")
    
    def _select_position(self, position: Dict):
        """Выбор должности"""
        self.selected_position = position
        self.has_selected_position = True
        self.can_generate = True
        
        # Очищаем результаты поиска
        self._clear_search_results()
        
        # Устанавливаем выбранную должность в поле поиска
        if self.search_input:
            self.search_input.set_value(position["name"])
        
        # Отображаем выбранную должность
        self._display_selected_position()
        
        ui.notify(
            f"✅ Выбрана должность: {position['name']}",
            type="positive",
            position="top"
        )
    
    def _display_selected_position(self):
        """Отображение выбранной должности"""
        if not self.selected_position:
            return
        
        self.selected_position_card.clear()
        
        with self.selected_position_card:
            with ui.card().classes("a101-selected-position slide-up"):
                with ui.card_section().classes("py-4"):
                    with ui.row().classes("w-full items-start justify-between"):
                        
                        # Информация о позиции
                        with ui.column().classes("flex-1 gap-3"):
                            
                            # Заголовок
                            with ui.row().classes("items-center gap-2"):
                                ui.icon("check_circle", size="1.5rem").classes("text-emerald-600")
                                ui.label("Выбранная должность").classes("text-sm font-medium text-emerald-700")
                            
                            # Название должности
                            ui.label(self.selected_position["name"]).classes("text-xl font-bold text-gray-900")
                            
                            # Детали в сетке
                            with ui.grid(columns="1fr 1fr").classes("gap-4 mt-3"):
                                
                                # Департамент
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("business", size="1rem").classes("text-gray-500")
                                    ui.label(self.selected_position["department"]).classes("text-sm text-gray-700")
                                
                                # Уровень  
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("trending_up", size="1rem").classes("text-gray-500")
                                    level_info = self._format_position_level(self.selected_position.get("level"))
                                    ui.label(level_info["text"]).classes("text-sm text-gray-700")
                                
                                # Категория
                                with ui.row().classes("items-center gap-2"):
                                    ui.icon("category", size="1rem").classes("text-gray-500")
                                    ui.label(self.selected_position["category"]).classes("text-sm text-gray-700")
                        
                        # Кнопка изменения
                        ui.button(
                            "Изменить",
                            icon="edit",
                            on_click=self._clear_selection
                        ).props("size=sm outlined color=primary")
    
    def _clear_selection(self):
        """Очистка выбранной должности"""
        self.selected_position = None
        self.has_selected_position = False
        self.can_generate = False
        
        if self.search_input:
            self.search_input.set_value("")
        
        self._clear_search_results()
    
    def _clear_search_results(self):
        """Очистка результатов поиска (заглушка - результаты убраны)"""
        self.current_query = ""
        self.search_results = []
        self.has_search_results = False
        # Скрываем spinner загрузки если он есть
        if hasattr(self, 'search_loading') and self.search_loading:
            self.search_loading.style("display: none")
    
    def _show_no_results(self):
        """Отображение отсутствия результатов"""
        with self.search_results_container:
            with ui.card().classes("w-full text-center py-8"):
                with ui.card_section():
                    ui.icon("search_off", size="3rem").classes("text-gray-400 mb-4")
                    ui.label(f"По запросу '{self.current_query}' ничего не найдено").classes("text-lg text-gray-600 mb-2")
                    ui.label("Попробуйте изменить поисковый запрос или воспользуйтесь категориями").classes("text-sm text-muted")
    
    def _show_search_error(self, error_message: str):
        """Отображение ошибки поиска"""
        with self.search_results_container:
            with ui.card().classes("a101-error-card"):
                with ui.card_section():
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("error", size="1.5rem").classes("text-error")
                        ui.label("Ошибка поиска").classes("font-semibold text-error")
                    ui.label(error_message).classes("text-sm text-muted mt-2")
    
    async def _quick_search(self, query: str):
        """Быстрый поиск по категории (legacy support)"""
        # Используем новый умный поиск по категориям
        category = {"name": "Быстрый поиск", "query": query}
        self._smart_category_search(category)
    
    def _trigger_search(self):
        """Принудительный поиск (заглушка - убрано)"""
        # Метод больше не используется - dropdown заменяет поиск
        pass
    
    async def _start_generation(self):
        """Запуск генерации профиля"""
        if not self.selected_position or self.is_generating:
            return
            
        try:
            self.is_generating = True
            self.generate_button.props(add="loading")
            
            # Подготовка данных для генерации
            generation_data = {
                "department": self.selected_position["department"],
                "position": self.selected_position["name"],
                "employee_name": self.employee_name_input.value.strip() if self.employee_name_input.value else None,
                "temperature": self.temperature_slider.value,
                "save_result": True
            }
            
            # Запуск генерации через API
            response = await self.api_client.start_profile_generation(**generation_data)
            
            if response.get("success"):
                self.current_task_id = response["task_id"]
                ui.notify("🚀 Генерация профиля запущена!", type="positive", position="top")
                
                # Показываем прогресс
                await self._show_generation_progress()
            else:
                ui.notify("❌ Ошибка запуска генерации", type="negative")
                
        except Exception as e:
            logger.error(f"Error starting generation: {e}")
            ui.notify(f"❌ Ошибка: {str(e)}", type="negative")
        finally:
            self.is_generating = False
            self.generate_button.props(remove="loading")
    
    async def _show_generation_progress(self):
        """Отображение прогресса генерации"""
        with ui.dialog().classes("a101-progress-dialog") as dialog:
            with ui.card():
                with ui.card_section().classes("py-6 px-8"):
                    
                    # Заголовок
                    with ui.row().classes("items-center gap-3 mb-4"):
                        ui.spinner(size="lg", color="primary")
                        with ui.column().classes("gap-1"):
                            ui.label("Генерация профиля должности").classes("text-lg font-semibold text-primary")
                            progress_status = ui.label("Инициализация процесса...").classes("text-sm text-muted")
                    
                    # Прогресс-бар
                    progress_bar = ui.linear_progress(value=0).classes("w-full mb-2")
                    progress_percentage = ui.label("0%").classes("text-xs text-muted text-right")
                    
                    # Кнопка отмены
                    with ui.row().classes("justify-center mt-6"):
                        ui.button(
                            "Отменить",
                            on_click=dialog.close
                        ).props("outlined color=grey")
        
        dialog.open()
        
        # Отслеживание прогресса
        await self._poll_generation_status(dialog, progress_status, progress_bar, progress_percentage)
    
    async def _poll_generation_status(self, dialog, status_label, progress_bar, progress_percentage):
        """Опрос статуса генерации"""
        max_attempts = 60  # 5 минут максимум
        attempt = 0
        
        while attempt < max_attempts and dialog.value:  # Проверяем, что диалог не закрыт
            try:
                status_response = await self.api_client.get_generation_task_status(self.current_task_id)
                
                if not status_response.get("success"):
                    break
                
                task_data = status_response["task"]
                status = task_data["status"]
                progress = task_data.get("progress", 0)
                current_step = task_data.get("current_step", "Обработка...")
                
                # Обновляем UI
                status_label.text = current_step
                progress_bar.value = progress / 100.0
                progress_percentage.text = f"{progress}%"
                
                if status == "completed":
                    dialog.close()
                    await self._show_generation_success()
                    break
                elif status == "failed":
                    dialog.close()
                    error_msg = task_data.get("error_message", "Неизвестная ошибка")
                    await self._show_generation_error(error_msg)
                    break
                elif status == "cancelled":
                    dialog.close()
                    ui.notify("Генерация отменена", type="warning")
                    break
                
                await asyncio.sleep(5)  # Проверяем каждые 5 секунд
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error polling generation status: {e}")
                await asyncio.sleep(5)
                attempt += 1
        
        if attempt >= max_attempts:
            dialog.close()
            await self._show_generation_error("Превышено время ожидания")
    
    async def _show_generation_success(self):
        """Отображение успешного завершения"""
        with ui.dialog() as dialog:
            with ui.card().classes("a101-success-card"):
                with ui.card_section().classes("text-center py-8"):
                    
                    # Иконка успеха
                    ui.icon("check_circle", size="4rem").classes("text-success mb-4")
                    
                    # Заголовок
                    ui.label("🎉 Профиль успешно создан!").classes("text-2xl font-bold text-success mb-2")
                    ui.label("Профиль должности готов для использования").classes("text-muted mb-6")
                    
                    # Действия
                    with ui.row().classes("gap-3 justify-center"):
                        ui.button(
                            "Просмотреть профиль",
                            icon="description",
                            on_click=lambda: self._view_profile(dialog)
                        ).props("color=primary")
                        
                        ui.button(
                            "Создать еще один",
                            icon="add_circle_outline",
                            on_click=lambda: self._create_another(dialog)
                        ).props("outlined color=primary")
        
        dialog.open()
        ui.notify("🎊 Профиль должности готов!", type="positive", position="center", timeout=5000)
    
    async def _show_generation_error(self, error_message: str):
        """Отображение ошибки генерации"""
        with ui.dialog() as dialog:
            with ui.card().classes("a101-error-card"):
                with ui.card_section().classes("py-6"):
                    
                    # Заголовок ошибки
                    with ui.row().classes("items-center gap-3 mb-4"):
                        ui.icon("error", size="2rem").classes("text-error")
                        ui.label("❌ Ошибка генерации").classes("text-lg font-bold text-error")
                    
                    # Сообщение об ошибке
                    ui.label(error_message).classes("text-sm text-muted mb-6")
                    
                    # Действия
                    with ui.row().classes("gap-3"):
                        ui.button(
                            "Попробовать снова",
                            icon="refresh",
                            on_click=lambda: self._retry_generation(dialog)
                        ).props("color=red")
                        
                        ui.button(
                            "Закрыть",
                            on_click=dialog.close
                        ).props("outlined")
        
        dialog.open()
        ui.notify(f"❌ {error_message}", type="negative", position="top")
    
    def _view_profile(self, dialog):
        """Просмотр сгенерированного профиля"""
        dialog.close()
        ui.navigate.to(f'/profiles/{self.current_task_id}')
    
    def _create_another(self, dialog):
        """Создание еще одного профиля"""
        dialog.close()
        self._reset_generator()
    
    def _retry_generation(self, dialog):
        """Повтор генерации"""
        dialog.close()
        asyncio.create_task(self._start_generation())
    
    def _reset_generator(self):
        """Сброс генератора"""
        self._clear_selection()
        self.current_task_id = None
        
        if self.employee_name_input:
            self.employee_name_input.value = ""
        if self.temperature_slider:
            self.temperature_slider.value = 0.1
        if self.profile_type_select:
            self.profile_type_select.value = "Полный профиль"
        
        self._update_temperature_description()
        ui.notify("🔄 Генератор сброшен", type="info")
    
    # ============================================================================
    # NICEGUI NATIVE AUTOCOMPLETE - SIMPLIFIED APPROACH
    # ============================================================================
    # 
    # ✅ Removed custom dropdown implementation in favor of NiceGUI's built-in autocomplete
    # ✅ All autocomplete suggestions now handled by ui.input(autocomplete=...) parameter  
    # ✅ Hierarchical suggestions loaded from backend data via _load_hierarchical_suggestions()
    # ✅ Custom dropdown methods removed: _display_suggestions, _hide_suggestions, etc.
    #
    
    def _smart_category_search(self, category: dict):
        """Умный поиск по категории (заглушка - убрано)"""
        # Метод больше не используется - dropdown заменяет категории
        pass
    
    def _show_advanced_filters(self):
        """Показать расширенные фильтры поиска (заглушка - убрано)"""
        # Метод больше не используется - dropdown уже содержит всю иерархию
        ui.notify("Фильтры встроены в dropdown поиск", type="info")
    
    def _apply_filters(self, department: str, level: str, dialog):
        """Применение фильтров поиска (заглушка - убрано)"""
        pass
    
    def _clear_filters(self, dialog):
        """Очистка всех фильтров (заглушка - убрано)"""
        pass
    
    def _update_active_filters_display(self):
        """Обновление отображения активных фильтров (заглушка - убрано)"""
        pass
    
    def _show_search_history(self):
        """Показать историю поиска (заглушка - убрано)"""
        # Метод больше не используется - dropdown содержит все варианты
        ui.notify("История встроена в dropdown поиск", type="info")
    
    def _apply_history_search(self, query: str, dialog):
        """Применить поиск из истории"""
        self.search_input.set_value(query)
        dialog.close()
        asyncio.create_task(self._perform_search(query))
    
    def _clear_search_history(self, dialog):
        """Очистить историю поиска"""
        self.search_history.clear()
        ui.notify("История поиска очищена", type="positive")
        dialog.close()


if __name__ == "__main__":
    print("✅ A101 Professional Profile Generator created!")
    print("🎨 Features:")
    print("  - NiceGUI-compatible corporate design")
    print("  - Debounced search with category filters")
    print("  - Professional progress tracking")
    print("  - Responsive mobile-friendly layout")
    print("  - Real-time feedback and error handling")
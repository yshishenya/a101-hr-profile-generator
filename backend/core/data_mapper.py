"""
Детерминированные компоненты маппинга данных для системы генерации профилей А101.

Модуль содержит классы для:
- OrganizationMapper: Извлечение релевантной организационной структуры
- KPIMapper: Маппинг департаментов к KPI файлам
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class OrganizationMapper:
    """Детерминированное извлечение релевантной организационной структуры"""
    
    def __init__(self, org_structure_path: str = "/home/yan/A101/HR/org_structure/structure.json"):
        self.org_structure_path = Path(org_structure_path)
        self._org_data = None
        self._department_index = {}
        
    def _load_org_structure(self) -> dict:
        """Загрузка организационной структуры с кешированием"""
        if self._org_data is None:
            try:
                with open(self.org_structure_path, 'r', encoding='utf-8') as f:
                    self._org_data = json.load(f)
                self._build_department_index()
                logger.info(f"Loaded organization structure: {len(self._department_index)} departments")
            except Exception as e:
                logger.error(f"Error loading org structure: {e}")
                self._org_data = {}
        
        return self._org_data
    
    def _build_department_index(self):
        """Построение индекса для быстрого поиска департаментов"""
        def index_node(node: dict, path: str = ""):
            if isinstance(node, dict):
                name = node.get('name', '')
                if name:
                    full_path = f"{path}/{name}" if path else name
                    self._department_index[name] = {
                        'path': full_path,
                        'node': node,
                        'level': len([p for p in full_path.split('/') if p])
                    }
                
                # Рекурсивно обходим детей
                children = node.get('children', [])
                if isinstance(children, list):
                    for child in children:
                        index_node(child, full_path if name else path)
        
        self._load_org_structure()
        if self._org_data:
            index_node(self._org_data)
    
    def find_department_path(self, department_name: str) -> str:
        """Находит полный путь департамента в иерархии"""
        if not self._org_data:
            self._load_org_structure()
        
        # Точное соответствие
        if department_name in self._department_index:
            return self._department_index[department_name]['path']
        
        # Нечеткий поиск
        for indexed_name, info in self._department_index.items():
            if department_name.lower() in indexed_name.lower() or indexed_name.lower() in department_name.lower():
                logger.info(f"Fuzzy match: '{department_name}' -> '{indexed_name}'")
                return info['path']
        
        logger.warning(f"Department not found: {department_name}")
        return department_name
    
    def extract_relevant_structure(self, department_name: str, levels_up: int = 1, levels_down: int = 2) -> dict:
        """
        Извлекает релевантную структуру с контекстом вверх/вниз по иерархии
        
        Args:
            department_name: Название целевого департамента
            levels_up: Сколько уровней вверх включить (родительские)
            levels_down: Сколько уровней вниз включить (дочерние)
        
        Returns:
            Оптимизированная структура с релевантными подразделениями
        """
        if not self._org_data:
            self._load_org_structure()
        
        if department_name not in self._department_index:
            # Пытаемся найти нечетким поиском
            found = False
            for indexed_name in self._department_index:
                if department_name.lower() in indexed_name.lower():
                    department_name = indexed_name
                    found = True
                    break
            
            if not found:
                logger.warning(f"Department not found for extraction: {department_name}")
                return {"error": f"Department '{department_name}' not found"}
        
        target_info = self._department_index[department_name]
        target_path = target_info['path']
        target_level = target_info['level']
        
        def extract_node(node: dict, current_path: str = "", current_level: int = 0) -> Optional[dict]:
            """Рекурсивное извлечение релевантных узлов"""
            if not isinstance(node, dict):
                return None
                
            name = node.get('name', '')
            if not name:
                return None
            
            node_path = f"{current_path}/{name}" if current_path else name
            node_level = len([p for p in node_path.split('/') if p])
            
            # Проверяем релевантность узла
            is_target = node_path == target_path
            is_parent = target_path.startswith(node_path + "/") and (target_level - node_level <= levels_up)
            is_child = node_path.startswith(target_path + "/") and (node_level - target_level <= levels_down)
            is_sibling = (node_path != target_path and 
                         len(node_path.split('/')) == len(target_path.split('/')) and
                         '/'.join(node_path.split('/')[:-1]) == '/'.join(target_path.split('/')[:-1]))
            
            if not (is_target or is_parent or is_child or is_sibling):
                return None
            
            # Создаем копию узла
            extracted = {
                'name': name,
                'level': node.get('level'),
                'employees_count': node.get('employees_count', 0),
                'children': []
            }
            
            # Добавляем метку для целевого узла
            if is_target:
                extracted['is_target'] = True
            
            # Рекурсивно обрабатываем детей
            children = node.get('children', [])
            if isinstance(children, list):
                for child in children:
                    extracted_child = extract_node(child, node_path, current_level + 1)
                    if extracted_child:
                        extracted['children'].append(extracted_child)
            
            return extracted
        
        # Извлекаем релевантную структуру
        result = extract_node(self._org_data)
        
        return {
            'department_path': target_path,
            'target_department': department_name,
            'extraction_params': {
                'levels_up': levels_up,
                'levels_down': levels_down
            },
            'structure': result
        }


class KPIMapper:
    """Детерминированное определение KPI файлов по департаментам"""
    
    def __init__(self, kpi_dir: str = "/home/yan/A101/HR/KPI/md_converted"):
        self.kpi_dir = Path(kpi_dir)
        
        # Точные соответствия названий департаментов
        self.kpi_mapping = {
            "ДИТ": "КПЭ 2025_ДИТ (Сложеникин А)+_structured.md",
            "Департамент информационных технологий": "КПЭ 2025_ДИТ (Сложеникин А)+_structured.md",
            "Блок ДИТ": "КПЭ 2025_ДИТ (Сложеникин А)+_structured.md",
            
            "Коммерческий департамент": "КПЭ 2025_ТОП_финал__structured.md",
            "Департамент маркетинга": "КПЭ 2025_ТОП_финал__structured.md",
            "Отдел продаж": "КПЭ 2025_ТОП_финал__structured.md",
            
            "Финансовый департамент": "КПЭ 2025_ТОП_финал__structured.md",
            "Департамент финансов": "КПЭ 2025_ТОП_финал__structured.md",
            "Финансы": "КПЭ 2025_ТОП_финал__structured.md",
            
            "Юридический департамент": "КПЭ 2025_ТОП_финал__structured.md",
            "Правовой департамент": "КПЭ 2025_ТОП_финал__structured.md",
            
            "HR": "КПЭ 2025_ТОП_финал__structured.md",
            "Кадры": "КПЭ 2025_ТОП_финал__structured.md",
            "Управление персоналом": "КПЭ 2025_ТОП_финал__structured.md"
        }
        
        # Регулярные выражения для нечеткого поиска
        self.kpi_patterns = [
            (r".*[Ии][Тт].*|.*информационн.*|.*цифр.*|.*технолог.*", 
             "КПЭ 2025_ДИТ (Сложеникин А)+_structured.md"),
            
            (r".*коммерч.*|.*продаж.*|.*маркетинг.*|.*реклам.*", 
             "КПЭ 2025_ТОП_финал__structured.md"),
            
            (r".*финанс.*|.*бухгалт.*|.*казначейств.*|.*контролл.*", 
             "КПЭ 2025_ТОП_финал__structured.md"),
            
            (r".*юридич.*|.*правов.*|.*комплаенс.*|.*безопасност.*", 
             "КПЭ 2025_ТОП_финал__structured.md"),
            
            (r".*[Кк]адр.*|.*[Hh][Rr].*|.*персонал.*|.*сотрудник.*", 
             "КПЭ 2025_ТОП_финал__structured.md")
        ]
        
        # Fallback файл для неопознанных департаментов
        self.fallback_file = "КПЭ 2025_ТОП_финал__structured.md"
    
    def find_kpi_file(self, department: str) -> str:
        """
        Детерминированный алгоритм поиска KPI файла:
        1. Точное соответствие названия
        2. Нечеткое соответствие по регулярным выражениям  
        3. Fallback на общие корпоративные KPI
        """
        if not department:
            return self.fallback_file
        
        # Нормализация входного названия
        department_clean = department.strip()
        
        # 1. Точное соответствие
        if department_clean in self.kpi_mapping:
            logger.info(f"Exact match for '{department}' -> {self.kpi_mapping[department_clean]}")
            return self.kpi_mapping[department_clean]
        
        # 2. Нечеткое соответствие по паттернам
        for pattern, kpi_file in self.kpi_patterns:
            if re.search(pattern, department_clean, re.IGNORECASE):
                logger.info(f"Pattern match for '{department}' -> {kpi_file}")
                return kpi_file
        
        # 3. Fallback
        logger.warning(f"No KPI match found for '{department}', using fallback: {self.fallback_file}")
        return self.fallback_file
    
    def load_kpi_content(self, department: str) -> str:
        """Загрузка и автоматическая очистка KPI контента"""
        kpi_filename = self.find_kpi_file(department)
        kpi_path = self.kpi_dir / kpi_filename
        
        try:
            if not kpi_path.exists():
                logger.error(f"KPI file not found: {kpi_path}")
                return f"# KPI данные для {department}\n\nДанные KPI недоступны."
            
            with open(kpi_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Очистка контента
            content = self._clean_kpi_content(content)
            
            logger.info(f"Loaded KPI content for '{department}': {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"Error loading KPI file {kpi_path}: {e}")
            return f"# KPI данные для {department}\n\nОшибка загрузки KPI данных: {str(e)}"
    
    def _clean_kpi_content(self, content: str) -> str:
        """Автоматическая очистка KPI контента"""
        # Удаляем избыточные переносы строк (больше 2 подряд)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Удаляем лишние пробелы в конце строк
        content = re.sub(r' +\n', '\n', content)
        
        # Нормализуем таблицы - убираем пустые строки внутри таблиц
        content = re.sub(r'\|\s*\|\s*\|\n\n\|', '|\n|', content)
        
        # Ограничиваем длину контента (максимум 15000 токенов ≈ 45000 символов)
        if len(content) > 45000:
            content = content[:45000] + "\n\n[...контент обрезан для оптимизации токенов...]"
            logger.warning("KPI content truncated due to length")
        
        return content.strip()
    
    def get_available_kpi_files(self) -> List[str]:
        """Получение списка доступных KPI файлов"""
        if not self.kpi_dir.exists():
            return []
        
        return [f.name for f in self.kpi_dir.glob("*.md")]
    
    def validate_kpi_mappings(self) -> Dict[str, bool]:
        """Проверка существования всех маппированных KPI файлов"""
        results = {}
        all_files = set(self.kpi_mapping.values())
        all_files.add(self.fallback_file)
        
        for filename in all_files:
            file_path = self.kpi_dir / filename
            results[filename] = file_path.exists()
            
        return results


if __name__ == "__main__":
    # Тестирование компонентов
    logging.basicConfig(level=logging.INFO)
    
    print("=== Тестирование OrganizationMapper ===")
    org_mapper = OrganizationMapper()
    
    test_departments = ["ДИТ", "Коммерческий департамент", "Несуществующий департамент"]
    for dept in test_departments:
        path = org_mapper.find_department_path(dept)
        print(f"Путь для '{dept}': {path}")
        
        structure = org_mapper.extract_relevant_structure(dept)
        print(f"Структура для '{dept}': {structure.get('department_path', 'не найдено')}")
    
    print("\n=== Тестирование KPIMapper ===")
    kpi_mapper = KPIMapper()
    
    # Проверка маппингов
    validation = kpi_mapper.validate_kpi_mappings()
    print("Валидация KPI файлов:", validation)
    
    # Тестирование поиска файлов
    for dept in test_departments:
        kpi_file = kpi_mapper.find_kpi_file(dept)
        print(f"KPI файл для '{dept}': {kpi_file}")
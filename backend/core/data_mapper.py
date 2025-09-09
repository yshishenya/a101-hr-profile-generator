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
    
    def __init__(self, org_structure_path: str = "data/structure.json"):
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
        def index_node(node: dict, path: str = "", parent_name: str = ""):
            if isinstance(node, dict):
                # В нашей структуре имена департаментов - это ключи объекта
                for dept_name, dept_data in node.items():
                    if isinstance(dept_data, dict) and dept_name not in ["organization"]:
                        # Создаем полный путь
                        full_path = f"{path}/{dept_name}" if path else dept_name
                        
                        # Добавляем в индекс
                        self._department_index[dept_name] = {
                            'path': full_path,
                            'node': dept_data,
                            'level': len([p for p in full_path.split('/') if p])
                        }
                        
                        # Рекурсивно обходим детей если есть
                        children = dept_data.get('children', {})
                        if isinstance(children, dict) and children:
                            index_node(children, full_path, dept_name)
        
        self._load_org_structure()
        if self._org_data:
            # Начинаем с organization если он есть
            if "organization" in self._org_data:
                index_node(self._org_data["organization"])
            else:
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
    
    def get_positions_for_department(self, department_name: str) -> List[str]:
        """Retrieves a list of positions for the specified department from the
        organizational structure.
        
        This function first checks if the organizational data is loaded; if not, it
        loads the data.  It then attempts to find an exact match for the department
        name in the department index.  If no exact match is found, it performs a fuzzy
        search to find similar department names.  The function returns the list of
        positions associated with the matched department or logs a warning if no
        positions are found.
        
        Args:
            department_name: The name of the department to retrieve positions for.
        """
        if not self._org_data:
            self._load_org_structure()
        
        # Точное соответствие
        if department_name in self._department_index:
            dept_node = self._department_index[department_name]['node']
            positions = dept_node.get('positions', [])
            if positions:
                logger.debug(f"Found {len(positions)} positions in '{department_name}': {positions}")
                return positions
        
        # Нечеткий поиск
        for indexed_name, info in self._department_index.items():
            if department_name.lower() in indexed_name.lower() or indexed_name.lower() in department_name.lower():
                logger.info(f"Fuzzy match for positions: '{department_name}' -> '{indexed_name}'")
                dept_node = info['node']
                positions = dept_node.get('positions', [])
                if positions:
                    return positions
        
        logger.warning(f"No positions found for department: {department_name}")
        return []
    
    def extract_relevant_structure(self, department_name: str, levels_up: int = 1, levels_down: int = 2) -> dict:
        """Extract relevant organizational structure based on department hierarchy.
        
        This function retrieves a structured representation of a department and its
        relevant parent and child nodes within a specified hierarchy. It first checks
        if the department exists in the index, attempting a fuzzy search if not found.
        The extraction is performed recursively, considering the specified levels up
        and down from the target department, and includes relevant sibling nodes.
        
        Args:
            department_name (str): The name of the target department.
            levels_up (int?): The number of levels to include upwards (parent nodes). Defaults to 1.
            levels_down (int?): The number of levels to include downwards (child nodes). Defaults to 2.
        
        Returns:
            dict: An optimized structure containing relevant departments.
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
    
    def __init__(self, kpi_dir: str = "data/KPI"):
        self.kpi_dir = Path(kpi_dir)
        
        # Единственный доступный KPI файл - используем для всех департаментов
        self.kpi_file = "KPI_DIT.md"
        
        # Логгинг для отслеживания маппинга
        self.mappings_log = []
    
    def find_kpi_file(self, department: str) -> str:
        """
        Возвращает единственный доступный KPI файл для любого департамента.
        В MVP версии используем KPI_DIT.md для всех департаментов.
        """
        # Логируем для отслеживания
        mapping_entry = {
            "department": department,
            "kpi_file": self.kpi_file,
            "method": "single_file_fallback"
        }
        self.mappings_log.append(mapping_entry)
        
        logger.info(f"KPI mapping: '{department}' -> '{self.kpi_file}' (MVP single file mode)")
        
        return self.kpi_file
    
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
        """Проверка существования KPI файла"""
        file_path = self.kpi_dir / self.kpi_file
        return {
            self.kpi_file: file_path.exists()
        }


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
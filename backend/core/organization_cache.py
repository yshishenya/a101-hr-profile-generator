"""
Централизованный кеш организационной структуры для системы генерации профилей А101.

Обеспечивает:
- Единственное место загрузки structure.json
- Thread-safe Singleton pattern
- Быстрый доступ к департаментам и иерархии
- Автоматическая индексация для поиска
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class OrganizationCacheManager:
    """
    Thread-safe Singleton для кеширования организационной структуры.
    
    Загружает structure.json один раз при первом обращении и хранит в памяти.
    Предоставляет оптимизированные методы для поиска департаментов и построения путей.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Данные организационной структуры
        self._org_data = None
        # НОВАЯ path-based индексация вместо name-based
        self._path_index = {}  # full_path → unit_data
        self._name_to_paths = defaultdict(list)  # name → [all_paths] для дубликатов
        # Старый индекс оставляем для совместимости
        self._department_index = {}
        self._structure_path = Path("data/structure.json")
        
        # Загружаем структуру при инициализации
        self._load_organization_structure()
        self._initialized = True
    
    def _load_organization_structure(self):
        """Загрузка организационной структуры из файла"""
        try:
            if not self._structure_path.exists():
                logger.error(f"❌ Organization structure file not found: {self._structure_path}")
                self._org_data = {}
                return
            
            with open(self._structure_path, "r", encoding="utf-8") as f:
                self._org_data = json.load(f)
            
            # Построение path-based индекса (НОВОЕ) + старый для совместимости
            self._build_path_index()
            self._build_department_index()  # Оставляем для совместимости
            
            logger.info(f"✅ Organization structure loaded: {len(self._path_index)} business units, {len(self._department_index)} departments (legacy)")
            
        except Exception as e:
            logger.error(f"❌ Error loading organization structure: {e}")
            self._org_data = {}
            self._path_index = {}
            self._name_to_paths = defaultdict(list)
            self._department_index = {}
    
    def _build_department_index(self):
        """Построение индекса департаментов для быстрого поиска"""
        self._department_index = {}
        
        def index_node(node: dict, path: str = ""):
            if isinstance(node, dict):
                for dept_name, dept_data in node.items():
                    if isinstance(dept_data, dict) and dept_name not in ["organization"]:
                        # Создаем полный путь
                        full_path = f"{path}/{dept_name}" if path else dept_name
                        
                        # Добавляем в индекс
                        self._department_index[dept_name] = {
                            "path": full_path,
                            "node": dept_data,
                            "level": len([p for p in full_path.split("/") if p]),
                        }
                        
                        # Рекурсивно обходим детей если есть
                        children = dept_data.get("children", {})
                        if isinstance(children, dict) and children:
                            index_node(children, full_path)
        
        if self._org_data:
            # Начинаем с organization если он есть
            organization = self._org_data.get("organization", {})
            if organization:
                index_node(organization)
            else:
                index_node(self._org_data)

    def _build_path_index(self):
        """
        НОВЫЙ метод: Построение path-based индекса для всех 567 бизнес-единиц
        Исправляет потерю данных из-за дубликатов имен в _build_department_index
        """
        self._path_index = {}
        self._name_to_paths = defaultdict(list)
        
        def index_by_path(node: dict, path: str = ""):
            if isinstance(node, dict):
                for name, data in node.items():
                    if name == "organization" or not isinstance(data, dict):
                        continue
                        
                    current_path = f"{path}/{name}" if path else name
                    
                    # Path-based индексация (НЕТ ПОТЕРЬ!)
                    self._path_index[current_path] = {
                        "name": name,
                        "path": current_path,
                        "data": data,
                        "level": len(current_path.split("/")) - 1,
                        "positions": data.get("positions", [])
                    }
                    
                    # Отслеживание дубликатов имен для поиска
                    self._name_to_paths[name].append(current_path)
                    
                    # Рекурсивно индексируем детей
                    children = data.get("children", {})
                    if children:
                        index_by_path(children, current_path)
        
        # Запускаем path-based индексацию
        if self._org_data:
            organization = self._org_data.get("organization", {})
            if organization:
                index_by_path(organization)
            else:
                index_by_path(self._org_data)
    
    def get_full_structure(self) -> Dict[str, Any]:
        """Получение полной организационной структуры"""
        return self._org_data if self._org_data is not None else {}
    
    def get_organization_root(self) -> Dict[str, Any]:
        """Получение корня организационной структуры"""
        return self._org_data.get("organization", {}) if self._org_data else {}
    
    def get_department_index(self) -> Dict[str, Dict[str, Any]]:
        """Получение индекса всех департаментов"""
        return self._department_index
    
    def find_department(self, department_name: str) -> Optional[Dict[str, Any]]:
        """
        Поиск департамента по имени
        
        Args:
            department_name: Название департамента
            
        Returns:
            Словарь с данными департамента или None
        """
        return self._department_index.get(department_name)
    
    def get_department_positions(self, department_name: str) -> List[str]:
        """
        Получение списка должностей для департамента
        
        Args:
            department_name: Название департамента
            
        Returns:
            Список должностей
        """
        dept_info = self.find_department(department_name)
        if dept_info:
            return dept_info["node"].get("positions", [])
        return []
    
    def get_all_departments(self) -> List[str]:
        """Получение списка всех департаментов"""
        return list(self._department_index.keys())
    
    def find_department_path(self, department_name: str) -> Optional[List[str]]:
        """
        Поиск полного пути к департаменту в иерархии
        
        Args:
            department_name: Название департамента
            
        Returns:
            Список элементов пути от корня к департаменту
        """
        dept_info = self.find_department(department_name)
        if dept_info:
            path_str = dept_info["path"]
            return [p.strip() for p in path_str.split("/") if p.strip()]
        return None
    
    def is_loaded(self) -> bool:
        """Проверка, загружена ли организационная структура"""
        return self._org_data is not None and len(self._department_index) > 0
    
    def reload(self):
        """Принудительная перезагрузка организационной структуры"""
        logger.info("🔄 Reloading organization structure...")
        self._load_organization_structure()

    # НОВЫЕ методы для path-based индексации
    def get_all_business_units_with_paths(self) -> Dict[str, Dict[str, Any]]:
        """
        @doc
        Получение всех 567 бизнес-единиц с path-based индексацией.
        
        Исправляет потерю данных из-за дубликатов имен в name-based индексе.
        Каждый элемент содержит полный путь, уровень, и должности.
        
        Returns:
            Dict[str, Dict[str, Any]]: {full_path: unit_data}
            
        Examples:
            python> units = cache.get_all_business_units_with_paths()
            python> # {'Блок ТД/Департамент строительства/Управление ЖК': {...}, ...}
        """
        return self._path_index.copy()

    def find_unit_by_path(self, full_path: str) -> Optional[Dict[str, Any]]:
        """
        @doc  
        Поиск бизнес-единицы по полному пути.
        
        Args:
            full_path: Полный путь в формате "Блок/Департамент/Управление/Группа"
            
        Returns:
            Optional[Dict[str, Any]]: Данные бизнес-единицы или None
            
        Examples:
            python> unit = cache.find_unit_by_path("Блок ТД/Департамент строительства")
            python> # {'name': 'Департамент строительства', 'positions': [...], ...}
        """
        return self._path_index.get(full_path)

    def find_all_paths_for_name(self, name: str) -> List[str]:
        """
        @doc
        Поиск всех путей для департамента с дублирующимся именем.
        
        Args:
            name: Название департамента (может иметь дубликаты)
            
        Returns:
            List[str]: Список всех путей где встречается это имя
            
        Examples:
            python> paths = cache.find_all_paths_for_name("Группа проектирования") 
            python> # ['Блок ТД/.../Группа проектирования', 'Блок КД/.../Группа проектирования']
        """
        return self._name_to_paths.get(name, [])

    def get_structure_with_target_highlighted(self, target_path: str) -> Dict[str, Any]:
        """
        @doc
        Получение полной оргструктуры с выделением целевой позиции для LLM анализа.
        
        Добавляет метку is_target=True к указанному пути и всем его родителям
        для контекстного понимания иерархии при анализе карьерных путей.
        
        Args:
            target_path: Полный путь к целевой бизнес-единице
            
        Returns:
            Dict[str, Any]: Полная структура с выделенной целью
            
        Examples:
            python> structure = cache.get_structure_with_target_highlighted("Блок ТД/ДИТ")
            python> # Вся оргструктура, где ДИТ и его родители помечены is_target=True
        """
        def mark_target_path(node: dict, current_path: str = "", target: str = target_path) -> dict:
            """Рекурсивно помечает целевой путь и всех родителей"""
            if not isinstance(node, dict):
                return {}
                
            result = {}
            for name, data in node.items():
                if name == "organization" or not isinstance(data, dict):
                    result[name] = data
                    continue
                    
                node_path = f"{current_path}/{name}" if current_path else name
                
                # Копируем узел
                node_copy = {
                    "name": name,
                    "positions": data.get("positions", []),
                    "children": {}
                }
                
                # Проверяем, является ли этот узел частью целевого пути
                if target.startswith(node_path):
                    node_copy["is_target"] = True
                    if node_path == target:
                        node_copy["is_target_exact"] = True
                
                # Рекурсивно обрабатываем детей
                children = data.get("children", {})
                if children:
                    node_copy["children"] = mark_target_path(children, node_path, target)
                
                result[name] = node_copy
                
            return result
        
        # Получаем полную структуру и помечаем целевой путь
        full_structure = self.get_full_structure()
        if "organization" in full_structure:
            marked_structure = {
                "organization": mark_target_path(full_structure["organization"], "", target_path)
            }
        else:
            marked_structure = mark_target_path(full_structure, "", target_path)
            
        return {
            "target_path": target_path,
            "total_business_units": len(self._path_index),
            "structure": marked_structure
        }

    def get_searchable_items(self) -> List[Dict[str, Any]]:
        """
        @doc
        Получение всех элементов для поиска во frontend dropdown.
        
        Создает плоский список всех бизнес-единиц с метаданными для поиска:
        - Полное имя с иерархией для отображения
        - Путь для API запросов  
        - Количество позиций
        - Уровень в иерархии
        
        Returns:
            List[Dict[str, Any]]: Список элементов для dropdown поиска
            
        Examples:
            python> items = cache.get_searchable_items()
            python> # [{'display_name': 'ДИТ (Блок ОД)', 'path': 'Блок ОД/ДИТ', ...}, ...]
        """
        searchable_items = []
        
        for full_path, unit_data in self._path_index.items():
            path_parts = full_path.split("/")
            name = unit_data["name"]
            positions_count = len(unit_data["positions"])
            level = unit_data["level"]
            
            # Создаем отображаемое имя с контекстом
            if level == 0:  # Блок
                display_name = name
            elif level == 1:  # Департамент  
                display_name = f"{name} ({path_parts[0]})"
            else:  # Более глубокие уровни
                # Показываем последние 2 уровня для контекста
                context = " → ".join(path_parts[-2:]) if len(path_parts) > 1 else name
                display_name = context
            
            searchable_items.append({
                "display_name": display_name,
                "full_path": full_path,
                "name": name,
                "positions_count": positions_count,
                "level": level,
                "hierarchy": " → ".join(path_parts),
                "positions": unit_data["positions"]  # Включаем позиции для frontend
            })
        
        # Сортируем по уровню, затем по имени
        searchable_items.sort(key=lambda x: (x["level"], x["name"]))
        
        return searchable_items


# Глобальный экземпляр кеша (Singleton)
organization_cache = OrganizationCacheManager()
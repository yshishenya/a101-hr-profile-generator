"""
Сервис каталога департаментов и должностей для системы генерации профилей А101.

Обеспечивает:
- Получение списка всех доступных департаментов
- Получение должностей для конкретного департамента
- Кеширование результатов для быстрых повторных запросов
- Интеграция с OrganizationMapper и DataLoader
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..core.data_loader import DataLoader
from ..models.database import db_manager

logger = logging.getLogger(__name__)


class CatalogService:
    """Сервис для работы с каталогом департаментов и должностей"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.db = db_manager
        
        # Настройки кеширования
        self._departments_cache = None
        self._positions_cache = {}
        self._cache_ttl = timedelta(hours=1)  # TTL кеша - 1 час
        self._last_departments_update = None
        self._positions_last_update = {}
    
    def get_departments(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Получение списка всех доступных департаментов с использованием оптимизированной загрузки.
        
        Args:
            force_refresh: Принудительное обновление кеша
            
        Returns:
            List[Dict] с информацией о департаментах
        """
        try:
            start_time = datetime.now()
            
            # Проверяем кеш
            if not force_refresh and self._is_departments_cache_valid():
                logger.info("Using cached departments data")
                return self._departments_cache
            
            logger.info("Loading departments using optimized full structure method")
            
            # Очистить кеш DataLoader если принудительное обновление
            if force_refresh:
                self.data_loader.clear_cache()
            
            # Загружаем полную структуру за один запрос
            full_structure = self.data_loader.load_full_organization_structure()
            
            # Преобразуем в формат для API
            departments_info = []
            for dept_name, dept_data in full_structure["departments"].items():
                dept_info = {
                    "name": dept_name,
                    "display_name": dept_name,
                    "path": dept_data["path"],
                    "positions_count": dept_data["positions_count"],
                    "last_updated": datetime.now().isoformat()
                }
                departments_info.append(dept_info)
            
            # Сортируем по названию для консистентности
            departments_info.sort(key=lambda x: x["name"])
            
            # Обновляем кеш
            self._departments_cache = departments_info
            self._last_departments_update = datetime.now()
            
            # Сохраняем в БД кеш для персистентности
            self._save_departments_to_cache(departments_info)
            
            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Loaded {len(departments_info)} departments in {load_time:.3f}s "
                       f"(total positions: {full_structure['metadata']['total_positions']})")
            return departments_info
            
        except Exception as e:
            logger.error(f"Error getting departments: {e}")
            
            # Пытаемся вернуть из БД кеша
            cached_data = self._load_departments_from_cache()
            if cached_data:
                logger.warning("Returning cached departments from database")
                return cached_data
            
            # Последний fallback - пустой список
            return []
    
    def get_positions(self, department: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Получение списка должностей для конкретного департамента с использованием оптимизированной загрузки.
        
        Args:
            department: Название департамента
            force_refresh: Принудительное обновление кеша
            
        Returns:
            List[Dict] с информацией о должностях
        """
        try:
            start_time = datetime.now()
            
            # Проверяем кеш для этого департамента
            cache_key = department
            
            if not force_refresh and self._is_positions_cache_valid(cache_key):
                logger.info(f"Using cached positions data for {department}")
                return self._positions_cache[cache_key]
            
            logger.info(f"Loading positions for department using optimized method: {department}")
            
            # Получаем данные из полной структуры DataLoader (уже оптимизировано)
            full_structure = self.data_loader.load_full_organization_structure()
            
            # Получаем позиции для департамента из кешированной структуры
            positions_info = []
            if department in full_structure["departments"]:
                dept_positions = full_structure["departments"][department]["positions"]
                
                for pos_data in dept_positions:
                    pos_info = {
                        "name": pos_data["name"],
                        "department": department,
                        "display_name": pos_data["name"],
                        "level": pos_data["level"],
                        "category": pos_data["category"],
                        "last_updated": datetime.now().isoformat()
                    }
                    positions_info.append(pos_info)
                
                # Сортируем должности по уровню и названию
                positions_info.sort(key=lambda x: (x["level"], x["name"]))
            else:
                logger.warning(f"Department '{department}' not found in organization structure")
            
            # Обновляем кеш
            self._positions_cache[cache_key] = positions_info
            self._positions_last_update[cache_key] = datetime.now()
            
            # Сохраняем в БД кеш
            self._save_positions_to_cache(department, positions_info)
            
            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Loaded {len(positions_info)} positions for {department} in {load_time:.3f}s")
            return positions_info
            
        except Exception as e:
            logger.error(f"Error getting positions for {department}: {e}")
            
            # Пытаемся вернуть из БД кеша
            cached_data = self._load_positions_from_cache(department)
            if cached_data:
                logger.warning(f"Returning cached positions from database for {department}")
                return cached_data
            
            # Последний fallback - пустой список
            return []
    
    def search_departments(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск департаментов по запросу.
        
        Args:
            query: Поисковой запрос
            
        Returns:
            List[Dict] с отфильтрованными департаментами
        """
        try:
            all_departments = self.get_departments()
            
            if not query or not query.strip():
                return all_departments
            
            query_lower = query.strip().lower()
            
            # Фильтруем департаменты по названию и пути
            filtered_departments = []
            for dept in all_departments:
                if (query_lower in dept["name"].lower() or 
                    query_lower in dept["path"].lower()):
                    filtered_departments.append(dept)
            
            logger.info(f"Search '{query}' found {len(filtered_departments)} departments")
            return filtered_departments
            
        except Exception as e:
            logger.error(f"Error searching departments with query '{query}': {e}")
            return []
    
    def get_department_details(self, department_name: str) -> Optional[Dict[str, Any]]:
        """
        Получение детальной информации о департаменте.
        
        Args:
            department_name: Название департамента
            
        Returns:
            Dict с детальной информацией или None
        """
        try:
            # Получаем базовую информацию
            departments = self.get_departments()
            department_info = None
            
            for dept in departments:
                if dept["name"] == department_name:
                    department_info = dept.copy()
                    break
            
            if not department_info:
                logger.warning(f"Department not found: {department_name}")
                return None
            
            # Добавляем расширенную информацию
            positions = self.get_positions(department_name)
            organization_structure = self.data_loader.org_mapper.extract_relevant_structure(
                department_name, levels_up=1, levels_down=2
            )
            
            department_info.update({
                "positions": positions,
                "organization_structure": organization_structure,
                "total_positions": len(positions),
                "position_levels": list(set(pos["level"] for pos in positions)),
                "position_categories": list(set(pos["category"] for pos in positions))
            })
            
            return department_info
            
        except Exception as e:
            logger.error(f"Error getting department details for {department_name}: {e}")
            return None
    
    def _determine_position_level(self, position_name: str) -> int:
        """Определение уровня должности (1 - высший, 5 - младший)"""
        position_lower = position_name.lower()
        
        if "руководитель" in position_lower or "директор" in position_lower:
            return 1
        elif "заместитель" in position_lower or "зам" in position_lower:
            return 2  
        elif "ведущий" in position_lower:
            return 3
        elif "старший" in position_lower:
            return 4
        else:
            return 5  # Обычный специалист
    
    def _determine_position_category(self, position_name: str) -> str:
        """Определение категории должности"""
        position_lower = position_name.lower()
        
        if "руководитель" in position_lower or "директор" in position_lower:
            return "management"
        elif "аналитик" in position_lower:
            return "analytics"
        elif "инженер" in position_lower or "разработчик" in position_lower:
            return "technical"
        elif "менеджер" in position_lower:
            return "management"
        else:
            return "specialist"
    
    def _is_departments_cache_valid(self) -> bool:
        """Проверка валидности кеша департаментов"""
        if not self._departments_cache or not self._last_departments_update:
            return False
        
        return datetime.now() - self._last_departments_update < self._cache_ttl
    
    def _is_positions_cache_valid(self, cache_key: str) -> bool:
        """Проверка валидности кеша должностей"""
        if (cache_key not in self._positions_cache or 
            cache_key not in self._positions_last_update):
            return False
        
        return datetime.now() - self._positions_last_update[cache_key] < self._cache_ttl
    
    def _save_departments_to_cache(self, departments: List[Dict]):
        """Сохранение департаментов в БД кеш"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Очищаем старый кеш департаментов
            cursor.execute("DELETE FROM organization_cache WHERE cache_type = 'departments'")
            
            # Сохраняем новые данные
            cursor.execute("""
                INSERT INTO organization_cache (cache_type, cache_key, data_json, expires_at)
                VALUES ('departments', 'all', ?, datetime('now', '+1 hour'))
            """, (str(departments),))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving departments to cache: {e}")
    
    def _load_departments_from_cache(self) -> Optional[List[Dict]]:
        """Загрузка департаментов из БД кеша"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data_json FROM organization_cache 
                WHERE cache_type = 'departments' AND cache_key = 'all' 
                AND expires_at > datetime('now')
            """)
            
            row = cursor.fetchone()
            if row:
                import ast
                return ast.literal_eval(row["data_json"])
            
        except Exception as e:
            logger.error(f"Error loading departments from cache: {e}")
        
        return None
    
    def _save_positions_to_cache(self, department: str, positions: List[Dict]):
        """Сохранение должностей в БД кеш"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Удаляем старый кеш для этого департамента
            cursor.execute("""
                DELETE FROM organization_cache 
                WHERE cache_type = 'positions' AND cache_key = ?
            """, (department,))
            
            # Сохраняем новые данные
            cursor.execute("""
                INSERT INTO organization_cache (cache_type, cache_key, data_json, expires_at)
                VALUES ('positions', ?, ?, datetime('now', '+1 hour'))
            """, (department, str(positions)))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving positions to cache for {department}: {e}")
    
    def _load_positions_from_cache(self, department: str) -> Optional[List[Dict]]:
        """Загрузка должностей из БД кеша"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data_json FROM organization_cache 
                WHERE cache_type = 'positions' AND cache_key = ? 
                AND expires_at > datetime('now')
            """, (department,))
            
            row = cursor.fetchone()
            if row:
                import ast
                return ast.literal_eval(row["data_json"])
            
        except Exception as e:
            logger.error(f"Error loading positions from cache for {department}: {e}")
        
        return None
    
    def clear_cache(self, cache_type: Optional[str] = None):
        """
        Очистка кеша.
        
        Args:
            cache_type: Тип кеша ('departments', 'positions', или None для всех)
        """
        try:
            # Очищаем память кеш
            if cache_type == "departments" or cache_type is None:
                self._departments_cache = None
                self._last_departments_update = None
            
            if cache_type == "positions" or cache_type is None:
                self._positions_cache.clear()
                self._positions_last_update.clear()
            
            # Очищаем БД кеш
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if cache_type:
                cursor.execute("DELETE FROM organization_cache WHERE cache_type = ?", (cache_type,))
            else:
                cursor.execute("DELETE FROM organization_cache")
            
            conn.commit()
            logger.info(f"Cache cleared: {cache_type or 'all'}")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Глобальный экземпляр сервиса каталога
catalog_service = CatalogService()


if __name__ == "__main__":
    # Тестирование сервиса каталога
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def test_catalog_service():
        print("📂 Тестирование CatalogService...")
        
        # Тест получения департаментов
        departments = catalog_service.get_departments()
        print(f"✅ Найдено департаментов: {len(departments)}")
        
        if departments:
            first_dept = departments[0]
            print(f"📋 Первый департамент: {first_dept['name']}")
            
            # Тест получения должностей
            positions = catalog_service.get_positions(first_dept['name'])
            print(f"✅ Должности в '{first_dept['name']}': {len(positions)}")
            
            # Тест поиска
            search_results = catalog_service.search_departments("IT")
            print(f"✅ Поиск 'IT': {len(search_results)} результатов")
            
            # Тест детальной информации
            details = catalog_service.get_department_details(first_dept['name'])
            if details:
                print(f"✅ Детали департамента: {len(details.get('positions', []))} должностей")
        
        print("🎉 Тестирование завершено!")
    
    # Запуск тестов
    asyncio.run(test_catalog_service())
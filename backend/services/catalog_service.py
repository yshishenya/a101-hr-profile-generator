"""
Сервис каталога департаментов и должностей для системы генерации профилей А101.

Обеспечивает:
- Получение списка всех доступных департаментов
- Получение должностей для конкретного департамента
- Кеширование результатов для быстрых повторных запросов
- Интеграция с OrganizationMapper и DataLoader
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.database import db_manager
from ..core.organization_cache import organization_cache

logger = logging.getLogger(__name__)


class CatalogService:
    """Сервис для работы с каталогом департаментов и должностей"""

    def __init__(self):
        self.db = db_manager
        self.organization_cache = organization_cache  # Добавляем ссылку для новых endpoints
        # Removed DataLoader - using organization_cache directly
        # Removed local caching infrastructure - using centralized cache

    def get_departments(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Получение списка всех доступных департаментов из централизованного кеша.

        Args:
            force_refresh: Параметр для совместимости (игнорируется)

        Returns:
            List[Dict] с информацией о департаментах
        """
        try:
            start_time = datetime.now()
            logger.info("Loading departments from centralized organization cache")

            # Получаем все департаменты из централизованного кеша
            all_departments = organization_cache.get_all_departments()
            
            # Преобразуем в API формат
            departments_info = []
            for dept_name in all_departments:
                # Получаем количество позиций для департамента
                positions = organization_cache.get_department_positions(dept_name)
                positions_count = len(positions) if positions else 0
                
                # Получаем путь департамента
                path_list = organization_cache.find_department_path(dept_name)
                path = " → ".join(path_list) if path_list else dept_name
                
                dept_info = {
                    "name": dept_name,
                    "display_name": dept_name,
                    "path": path,
                    "positions_count": positions_count,
                    "last_updated": datetime.now().isoformat(),
                }
                departments_info.append(dept_info)

            # Сортируем по названию для консистентности
            departments_info.sort(key=lambda x: x["name"])

            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Loaded {len(departments_info)} departments in {load_time:.3f}s from centralized cache")
            
            return departments_info

        except Exception as e:
            logger.error(f"Error getting departments from centralized cache: {e}")
            return []

    def get_positions(
        self, department: str, force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Получение списка должностей для конкретного департамента из централизованного кеша.

        Args:
            department: Название департамента
            force_refresh: Параметр для совместимости (игнорируется)

        Returns:
            List[Dict] с информацией о должностях
        """
        try:
            start_time = datetime.now()
            logger.info(f"Loading positions for {department} from centralized cache")

            # Получаем позиции из централизованного кеша  
            positions = organization_cache.get_department_positions(department)
            
            # Преобразуем в API формат
            positions_info = []
            for position in positions:
                # Определяем уровень и категорию должности
                level = self._determine_position_level(position)
                category = self._determine_position_category(position)
                
                pos_info = {
                    "name": position,
                    "department": department,
                    "display_name": position,
                    "level": level,
                    "category": category,
                    "last_updated": datetime.now().isoformat(),
                }
                positions_info.append(pos_info)

            # Сортируем должности по уровню и названию
            positions_info.sort(key=lambda x: (x["level"], x["name"]))

            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Loaded {len(positions_info)} positions for {department} in {load_time:.3f}s from centralized cache")
            
            return positions_info

        except Exception as e:
            logger.error(f"Error getting positions for {department} from centralized cache: {e}")
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
                if (
                    query_lower in dept["name"].lower()
                    or query_lower in dept["path"].lower()
                ):
                    filtered_departments.append(dept)

            logger.info(
                f"Search '{query}' found {len(filtered_departments)} departments"
            )
            return filtered_departments

        except Exception as e:
            logger.error(f"Error searching departments with query '{query}': {e}")
            return []

    def search_positions(
        self, query: str, department_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск должностей по запросу с опциональной фильтрацией по департаменту.

        Args:
            query: Поисковой запрос
            department_filter: Фильтр по департаменту (опционально)

        Returns:
            List[Dict] с отфильтрованными должностями
        """
        try:
            # Получаем все департаменты для поиска должностей
            all_departments = self.get_departments()
            all_positions = []

            # Определяем список департаментов для поиска
            departments_to_search = []
            if department_filter:
                # Фильтр по конкретному департаменту
                departments_to_search = [
                    dept
                    for dept in all_departments
                    if department_filter.lower() in dept["name"].lower()
                ]
            else:
                # Поиск по всем департаментам
                departments_to_search = all_departments

            # Собираем должности из выбранных департаментов
            for dept in departments_to_search:
                dept_positions = self.get_positions(dept["name"])
                all_positions.extend(dept_positions)

            # Если нет поискового запроса, возвращаем все должности
            if not query or not query.strip():
                logger.info(f"Returning all positions: {len(all_positions)} positions")
                return all_positions

            query_lower = query.strip().lower()

            # Фильтруем должности по названию, департаменту, уровню и категории
            filtered_positions = []
            for pos in all_positions:
                if (
                    query_lower in pos["name"].lower()
                    or query_lower in pos["department"].lower()
                    or query_lower in str(pos["level"]).lower()
                    or query_lower in pos["category"].lower()
                ):
                    filtered_positions.append(pos)

            logger.info(
                f"Position search '{query}' found {len(filtered_positions)} positions"
            )
            return filtered_positions

        except Exception as e:
            logger.error(f"Error searching positions with query '{query}': {e}")
            return []

    def get_department_details(self, department_name: str) -> Optional[Dict[str, Any]]:
        """
        Получение детальной информации о департаменте из централизованного кеша.

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
            
            # Получаем организационную структуру из централизованного кеша
            organization_structure = {
                "target_department": department_name,
                "department_path": " → ".join(organization_cache.find_department_path(department_name) or [department_name]),
                "structure": organization_cache.find_department(department_name)
            }

            department_info.update(
                {
                    "positions": positions,
                    "organization_structure": organization_structure,
                    "total_positions": len(positions),
                    "position_levels": list(set(pos["level"] for pos in positions)),
                    "position_categories": list(
                        set(pos["category"] for pos in positions)
                    ),
                }
            )

            return department_info

        except Exception as e:
            logger.error(f"Error getting department details for {department_name}: {e}")
            return None

    def _determine_position_level(self, position_name: str) -> int:
        """Определение уровня должности (1 - высший, 5 - младший)"""
        from ..utils.position_utils import determine_position_level
        return determine_position_level(position_name, "number")

    def _determine_position_category(self, position_name: str) -> str:
        """Определение категории должности"""
        from ..utils.position_utils import determine_position_category
        return determine_position_category(position_name)

    def clear_cache(self, cache_type: Optional[str] = None):
        """
        Очистка кеша - пустая реализация для совместимости с API.
        
        Централизованный кеш управляется напрямую через organization_cache.

        Args:
            cache_type: Параметр для совместимости (игнорируется)
        """
        logger.info(f"Cache clear requested: {cache_type or 'all'} - using centralized cache, no action needed")

    # НОВЫЕ методы для path-based поддержки и LLM интеграции
    def get_searchable_items(self) -> List[Dict[str, Any]]:
        """
        @doc
        Получение всех элементов для frontend поиска с path-based индексацией.
        
        Использует новую path-based систему для получения всех 567 бизнес-единиц
        без потерь данных из-за дублирующихся имен.
        
        Returns:
            List[Dict[str, Any]]: Элементы для dropdown с полной иерархией
            
        Examples:
            python> items = catalog_service.get_searchable_items()
            python> # [{'display_name': 'ДИТ (Блок ОД)', 'full_path': '...', ...}]
        """
        try:
            start_time = time.time()
            
            # Используем новый path-based метод из organization_cache
            searchable_items = self.organization_cache.get_searchable_items()
            
            execution_time = time.time() - start_time
            logger.info(
                f"✅ Retrieved {len(searchable_items)} searchable items in {execution_time:.4f}s (path-based)"
            )
            
            return searchable_items

        except Exception as e:
            logger.error(f"❌ Error getting searchable items: {e}")
            return []

    def get_organization_structure_with_target(
        self, target_path: str
    ) -> Dict[str, Any]:
        """
        @doc
        Получение полной организационной структуры с выделенной целевой позицией.
        
        Для LLM анализа карьерных путей - возвращает всю оргструктуру
        с подсвеченным целевым элементом и его родительскими узлами.
        
        Args:
            target_path: Полный путь к целевой бизнес-единице
            
        Returns:
            Dict[str, Any]: Полная структура с выделенной целью
            
        Examples:
            python> structure = catalog_service.get_organization_structure_with_target("Блок ОД/ДИТ")
            python> # Полная оргструктура с ДИТ и родителями помеченными is_target=True
        """
        try:
            start_time = time.time()
            
            # Проверяем существование целевого пути
            target_unit = self.organization_cache.find_unit_by_path(target_path)
            if not target_unit:
                logger.warning(f"Target path not found: {target_path}")
                return {
                    "error": f"Business unit at path '{target_path}' not found",
                    "available_paths": list(self.organization_cache.get_all_business_units_with_paths().keys())[:10]  # Первые 10 для примера
                }
            
            # Получаем структуру с подсвеченной целью
            highlighted_structure = self.organization_cache.get_structure_with_target_highlighted(target_path)
            
            # Добавляем метаданные для LLM
            highlighted_structure["target_unit_info"] = {
                "name": target_unit["name"],
                "full_path": target_path,
                "positions_count": len(target_unit["positions"]),
                "positions": target_unit["positions"],
                "hierarchy_level": target_unit["level"]
            }
            
            execution_time = time.time() - start_time
            logger.info(
                f"✅ Generated highlighted structure for '{target_path}' in {execution_time:.4f}s"
            )
            
            return highlighted_structure

        except Exception as e:
            logger.error(f"❌ Error generating highlighted structure for '{target_path}': {e}")
            return {
                "error": f"Failed to generate structure: {str(e)}",
                "target_path": target_path
            }

    def find_business_unit_by_path(self, full_path: str) -> Optional[Dict[str, Any]]:
        """
        @doc
        Поиск бизнес-единицы по полному пути с дополнительными метаданными.
        
        Args:
            full_path: Полный путь в формате "Блок/Департамент/Управление/Группа"
            
        Returns:
            Optional[Dict[str, Any]]: Расширенные данные бизнес-единицы
            
        Examples:
            python> unit = catalog_service.find_business_unit_by_path("Блок ОД/ДИТ")
            python> # {'name': 'ДИТ', 'positions': [...], 'hierarchy': [...], ...}
        """
        try:
            unit_data = self.organization_cache.find_unit_by_path(full_path)
            if not unit_data:
                return None
                
            # Добавляем расширенные метаданные
            path_parts = full_path.split("/")
            
            enhanced_unit = {
                **unit_data,
                "hierarchy_path": path_parts,
                "parent_path": "/".join(path_parts[:-1]) if len(path_parts) > 1 else None,
                "enriched_positions": []
            }
            
            # Обогащаем информацию о позициях
            for position in unit_data.get("positions", []):
                enriched_position = {
                    "name": position,
                    "level": self._determine_position_level(position),
                    "category": self._determine_position_category(position),
                    "department": unit_data["name"],
                    "full_path": full_path,
                    "last_updated": datetime.now().isoformat()
                }
                enhanced_unit["enriched_positions"].append(enriched_position)
            
            logger.info(f"✅ Found business unit '{full_path}' with {len(enhanced_unit['enriched_positions'])} positions")
            return enhanced_unit
            
        except Exception as e:
            logger.error(f"❌ Error finding business unit by path '{full_path}': {e}")
            return None


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
            positions = catalog_service.get_positions(first_dept["name"])
            print(f"✅ Должности в '{first_dept['name']}': {len(positions)}")

            # Тест поиска
            search_results = catalog_service.search_departments("IT")
            print(f"✅ Поиск 'IT': {len(search_results)} результатов")

            # Тест детальной информации
            details = catalog_service.get_department_details(first_dept["name"])
            if details:
                print(
                    f"✅ Детали департамента: {len(details.get('positions', []))} должностей"
                )

        print("🎉 Тестирование завершено!")

    # Запуск тестов
    asyncio.run(test_catalog_service())

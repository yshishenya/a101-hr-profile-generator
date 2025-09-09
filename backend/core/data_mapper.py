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

from .organization_cache import organization_cache

logger = logging.getLogger(__name__)


class OrganizationMapper:
    """Детерминированное извлечение релевантной организационной структуры"""

    def __init__(self, org_structure_path: str = "data/structure.json"):
        # Параметр оставляем для обратной совместимости, но не используем
        # Все данные теперь берем из централизованного кеша
        pass

    @property
    def _org_data(self) -> dict:
        """Получение данных из централизованного кеша"""
        return organization_cache.get_full_structure()

    @property 
    def _department_index(self) -> Dict[str, Dict[str, any]]:
        """Получение индекса департаментов из централизованного кеша"""
        return organization_cache.get_department_index()

    def find_department_path(self, department_name: str) -> str:
        """Находит полный путь департамента в иерархии"""
        # Используем централизованный кеш
        path_list = organization_cache.find_department_path(department_name)
        if path_list:
            return " → ".join(path_list)

        # Точное соответствие через кеш
        if department_name in self._department_index:
            return self._department_index[department_name]["path"]

        # Нечеткий поиск
        for indexed_name, info in self._department_index.items():
            if (
                department_name.lower() in indexed_name.lower()
                or indexed_name.lower() in department_name.lower()
            ):
                logger.info(f"Fuzzy match: '{department_name}' -> '{indexed_name}'")
                return info["path"]

        logger.warning(f"Department not found: {department_name}")
        return department_name

    def get_positions_for_department(self, department_name: str) -> List[str]:
        """
        Извлекает список должностей для указанного департамента из централизованного кеша.

        Args:
            department_name: Название департамента

        Returns:
            List[str]: Список должностей из structure.json
        """
        # Используем централизованный кеш вместо прямого доступа к файлам
        positions = organization_cache.get_department_positions(department_name)
        
        if positions:
            logger.debug(
                f"Found {len(positions)} positions in '{department_name}': {positions}"
            )
        else:
            logger.warning(f"No positions found for department: {department_name}")
        
        return positions

    def extract_relevant_structure(
        self, department_name: str, levels_up: int = 1, levels_down: int = 2
    ) -> dict:
        """
        Извлекает релевантную структуру с контекстом вверх/вниз по иерархии

        Args:
            department_name: Название целевого департамента
            levels_up: Сколько уровней вверх включить (родительские)
            levels_down: Сколько уровней вниз включить (дочерние)

        Returns:
            Оптимизированная структура с релевантными подразделениями
        """

        if department_name not in self._department_index:
            # Пытаемся найти нечетким поиском
            found = False
            for indexed_name in self._department_index:
                if department_name.lower() in indexed_name.lower():
                    department_name = indexed_name
                    found = True
                    break

            if not found:
                logger.warning(
                    f"Department not found for extraction: {department_name}"
                )
                return {"error": f"Department '{department_name}' not found"}

        target_info = self._department_index[department_name]
        target_path = target_info["path"]
        target_level = target_info["level"]

        def extract_node(
            node: dict, current_path: str = "", current_level: int = 0
        ) -> Optional[dict]:
            """Рекурсивное извлечение релевантных узлов"""
            if not isinstance(node, dict):
                return None

            name = node.get("name", "")
            if not name:
                return None

            node_path = f"{current_path}/{name}" if current_path else name
            node_level = len([p for p in node_path.split("/") if p])

            # Проверяем релевантность узла
            is_target = node_path == target_path
            is_parent = target_path.startswith(node_path + "/") and (
                target_level - node_level <= levels_up
            )
            is_child = node_path.startswith(target_path + "/") and (
                node_level - target_level <= levels_down
            )
            is_sibling = (
                node_path != target_path
                and len(node_path.split("/")) == len(target_path.split("/"))
                and "/".join(node_path.split("/")[:-1])
                == "/".join(target_path.split("/")[:-1])
            )

            if not (is_target or is_parent or is_child or is_sibling):
                return None

            # Создаем копию узла
            extracted = {
                "name": name,
                "level": node.get("level"),
                "employees_count": node.get("employees_count", 0),
                "children": [],
            }

            # Добавляем метку для целевого узла
            if is_target:
                extracted["is_target"] = True

            # Рекурсивно обрабатываем детей
            children = node.get("children", [])
            if isinstance(children, list):
                for child in children:
                    extracted_child = extract_node(child, node_path, current_level + 1)
                    if extracted_child:
                        extracted["children"].append(extracted_child)

            return extracted

        # Извлекаем релевантную структуру
        result = extract_node(self._org_data)

        return {
            "department_path": target_path,
            "target_department": department_name,
            "extraction_params": {"levels_up": levels_up, "levels_down": levels_down},
            "structure": result,
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
            "method": "single_file_fallback",
        }
        self.mappings_log.append(mapping_entry)

        logger.info(
            f"KPI mapping: '{department}' -> '{self.kpi_file}' (MVP single file mode)"
        )

        return self.kpi_file

    def load_kpi_content(self, department: str) -> str:
        """Загрузка и автоматическая очистка KPI контента"""
        kpi_filename = self.find_kpi_file(department)
        kpi_path = self.kpi_dir / kpi_filename

        try:
            if not kpi_path.exists():
                logger.error(f"KPI file not found: {kpi_path}")
                return f"# KPI данные для {department}\n\nДанные KPI недоступны."

            with open(kpi_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Очистка контента
            content = self._clean_kpi_content(content)

            logger.info(f"Loaded KPI content for '{department}': {len(content)} chars")
            return content

        except Exception as e:
            logger.error(f"Error loading KPI file {kpi_path}: {e}")
            return (
                f"# KPI данные для {department}\n\nОшибка загрузки KPI данных: {str(e)}"
            )

    def _clean_kpi_content(self, content: str) -> str:
        """Автоматическая очистка KPI контента"""
        # Удаляем избыточные переносы строк (больше 2 подряд)
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Удаляем лишние пробелы в конце строк
        content = re.sub(r" +\n", "\n", content)

        # Нормализуем таблицы - убираем пустые строки внутри таблиц
        content = re.sub(r"\|\s*\|\s*\|\n\n\|", "|\n|", content)

        # Ограничиваем длину контента (максимум 15000 токенов ≈ 45000 символов)
        if len(content) > 45000:
            content = (
                content[:45000] + "\n\n[...контент обрезан для оптимизации токенов...]"
            )
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
        return {self.kpi_file: file_path.exists()}


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
        print(
            f"Структура для '{dept}': {structure.get('department_path', 'не найдено')}"
        )

    print("\n=== Тестирование KPIMapper ===")
    kpi_mapper = KPIMapper()

    # Проверка маппингов
    validation = kpi_mapper.validate_kpi_mappings()
    print("Валидация KPI файлов:", validation)

    # Тестирование поиска файлов
    for dept in test_departments:
        kpi_file = kpi_mapper.find_kpi_file(dept)
        print(f"KPI файл для '{dept}': {kpi_file}")

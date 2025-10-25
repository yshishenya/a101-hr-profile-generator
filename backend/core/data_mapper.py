"""
Детерминированные компоненты маппинга данных для системы генерации профилей А101.

Модуль содержит классы для:
- OrganizationMapper: Извлечение релевантной организационной структуры
- KPIMapper: Маппинг департаментов к KPI файлам
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import aiofiles

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
    def _department_index(self) -> Dict[str, Dict[str, Any]]:
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

    def get_department_headcount(self, department_name: str) -> Optional[int]:
        """
        Получение численности департамента для расчета количества подчиненных.

        Args:
            department_name: Название департамента

        Returns:
            Optional[int]: Численность или None если данных нет
        """
        headcount = organization_cache.get_department_headcount(department_name)
        
        if headcount is not None:
            logger.debug(f"Headcount for '{department_name}': {headcount} people")
        else:
            logger.debug(f"No headcount data for department: {department_name}")

        return headcount

    def calculate_subordinates_count(self, department_name: str, position_title: str) -> Dict[str, int]:
        """
        Рассчитывает количество подчиненных на основе реальных данных о численности.
        
        Args:
            department_name: Название департамента
            position_title: Название должности
            
        Returns:
            Dict[str, int]: {
                "departments": количество подчиненных подразделений,
                "direct_reports": количество прямых подчиненных
            }
        """
        # Определяем уровень руководства по названию должности
        position_lower = position_title.lower()
        
        # Получаем численность департамента
        dept_headcount = self.get_department_headcount(department_name)
        
        if dept_headcount is None:
            # Если нет данных, используем старую логику по количеству позиций
            positions = self.get_positions_for_department(department_name)
            estimated_headcount = len(positions) * 2  # Приблизительная оценка
            logger.warning(f"No headcount data for '{department_name}', using estimate: {estimated_headcount}")
        else:
            estimated_headcount = dept_headcount
            logger.debug(f"Using real headcount for '{department_name}': {estimated_headcount}")

        # Логика расчета на основе уровня должности
        if any(keyword in position_lower for keyword in [
            "генеральный директор", "исполнительный директор", "операционный директор"
        ]):
            # Топ-менеджмент: управляет несколькими блоками/департаментами
            return {"departments": min(estimated_headcount // 50, 8), "direct_reports": min(estimated_headcount // 20, 15)}
            
        elif any(keyword in position_lower for keyword in [
            "директор по", "директор департамента", "коммерческий директор"
        ]):
            # Директора блоков/департаментов
            return {"departments": min(estimated_headcount // 25, 5), "direct_reports": min(estimated_headcount // 10, 12)}
            
        elif any(keyword in position_lower for keyword in [
            "руководитель департамента", "руководитель управления", "начальник отдела"
        ]):
            # Средний менеджмент
            return {"departments": min(estimated_headcount // 15, 3), "direct_reports": min(estimated_headcount // 5, 8)}
            
        elif any(keyword in position_lower for keyword in [
            "руководитель отдела", "руководитель группы", "лид"
        ]):
            # Линейный менеджмент
            return {"departments": 0, "direct_reports": min(estimated_headcount // 3, 6)}
            
        else:
            # Специалисты без подчиненных
            return {"departments": 0, "direct_reports": 0}

    def get_headcount_info(self, department_name: str) -> Dict[str, Any]:
        """
        Получение полной информации о численности департамента.

        Args:
            department_name: Название департамента

        Returns:
            Dict с данными о численности, источнике и метаданных
        """
        dept_info = organization_cache.find_department(department_name)
        
        if not dept_info:
            return {
                "headcount": None,
                "headcount_source": None,
                "headcount_department": None,
                "has_data": False
            }
            
        dept_data = dept_info["node"]
        return {
            "headcount": dept_data.get("headcount"),
            "headcount_source": dept_data.get("headcount_source"),
            "headcount_department": dept_data.get("headcount_department"),
            "has_data": dept_data.get("headcount") is not None
        }

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
    """
    Детерминированное определение KPI файлов по департаментам.
    Использует умный маппинг через KPIDepartmentMapper с fallback на templates.

    Coverage improvement:
    - Before: 1.7% (9/545 departments with specific files)
    - After: 100% (545/545 departments with specific files or templates)
    """

    def __init__(self, kpi_dir: str = "data/KPI"):
        self.kpi_dir = Path(kpi_dir)
        self.default_kpi_file = "KPI_DIT.md"  # Fallback for legacy code

        # Импортируем mapper
        try:
            from backend.core.kpi_department_mapping import KPIDepartmentMapper
            self.dept_mapper = KPIDepartmentMapper()
        except ImportError:
            logger.warning("KPIDepartmentMapper not available, using fallback")
            self.dept_mapper = None

        # Импортируем KPI templates для 100% coverage
        try:
            import sys
            sys.path.insert(0, str(self.kpi_dir))
            from templates import detect_department_type, get_kpi_template, KPI_TEMPLATES
            self.detect_department_type = detect_department_type
            self.get_kpi_template = get_kpi_template
            self.kpi_templates = KPI_TEMPLATES
            self.templates_available = True
            logger.info(f"KPI templates loaded: {len(KPI_TEMPLATES)} types available")
        except ImportError as e:
            logger.warning(f"KPI templates not available: {e}")
            self.templates_available = False
            self.detect_department_type = None
            self.get_kpi_template = None
            self.kpi_templates = {}

        # Логгинг для отслеживания маппинга
        self.mappings_log = []

    def find_kpi_file(self, department: str) -> str:
        """
        Находит подходящий KPI файл для департамента.

        Использует умный маппинг через KPIDepartmentMapper:
        - Сначала пытается найти точное соответствие
        - Затем частичное совпадение
        - Fallback на KPI_DIT.md если ничего не найдено

        Args:
            department: Название департамента

        Returns:
            Имя KPI файла (например, "KPI_ДИТ.md")
        """
        if not self.dept_mapper:
            # Fallback если mapper не доступен
            self.mappings_log.append({
                "department": department,
                "kpi_file": self.default_kpi_file,
                "method": "fallback_no_mapper",
            })
            return self.default_kpi_file

        # Используем умный маппинг
        match_result = self.dept_mapper.find_best_match(department)

        if match_result:
            kpi_file = match_result["filename"]
            kpi_path = self.kpi_dir / kpi_file

            # Проверяем что файл существует
            if kpi_path.exists():
                self.mappings_log.append({
                    "department": department,
                    "kpi_file": kpi_file,
                    "kpi_code": match_result["kpi_code"],
                    "confidence": match_result["confidence"],
                    "method": "smart_mapping",
                })

                logger.info(
                    f"KPI mapping: '{department}' -> '{kpi_file}' "
                    f"(confidence: {match_result['confidence']})"
                )

                return kpi_file
            else:
                logger.warning(
                    f"KPI file '{kpi_file}' not found for '{department}', "
                    f"using fallback"
                )

        # Fallback на default если не нашли или файл не существует
        self.mappings_log.append({
            "department": department,
            "kpi_file": self.default_kpi_file,
            "method": "fallback_no_match",
        })

        logger.info(
            f"KPI mapping fallback: '{department}' -> '{self.default_kpi_file}'"
        )

        return self.default_kpi_file

    def load_kpi_content(self, department: str) -> str:
        """
        Загрузка и автоматическая очистка KPI контента с 3-уровневым fallback.

        Priority (3-tier fallback system):
        1. Specific KPI file (if exists) - highest priority, most accurate
        2. Generic template by department type - good coverage, relevant
        3. Default generic template - universal fallback

        This ensures 100% coverage: ALL 545 departments get KPI data.

        Args:
            department: Название департамента

        Returns:
            Очищенный текст KPI контента (always non-empty, 100% coverage)

        Examples:
            >>> # Department with specific file (9 departments)
            >>> content = mapper.load_kpi_content("ДИТ")
            >>> # Returns: content from KPI_ДИТ.md

            >>> # Department without file (536 departments)
            >>> content = mapper.load_kpi_content("Департамент строительства объектов")
            >>> # Returns: CONSTRUCTION template

            >>> # Unknown department type
            >>> content = mapper.load_kpi_content("Неизвестный отдел")
            >>> # Returns: GENERIC template
        """
        # STEP 1: Try specific KPI file first (current 9 departments)
        kpi_filename = self.find_kpi_file(department)
        kpi_path = self.kpi_dir / kpi_filename

        try:
            if kpi_path.exists():
                # Синхронное чтение файла
                with open(kpi_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Очистка контента
                content = self._clean_kpi_content(content)

                logger.info(
                    f"✅ Loaded SPECIFIC KPI file for '{department}': "
                    f"{kpi_filename} ({len(content)} chars)"
                )
                return content

        except Exception as e:
            logger.warning(
                f"Failed to load specific KPI file {kpi_path}: {e}, "
                f"falling back to template"
            )

        # STEP 2: Fallback to generic template (536 departments)
        if self.templates_available:
            dept_type = self.detect_department_type(department)
            template_content = self.get_kpi_template(department)

            # Очистка шаблона (хотя он уже чистый, но для консистентности)
            template_content = self._clean_kpi_content(template_content)

            logger.info(
                f"✅ Using {dept_type} TEMPLATE for '{department}' "
                f"({len(template_content)} chars, no specific file found)"
            )

            return template_content

        # STEP 3: Last resort fallback (if templates not loaded)
        logger.error(
            f"❌ No specific file and no templates available for '{department}', "
            f"returning minimal fallback"
        )
        return f"""---
department: {department}
description: Minimal KPI fallback (templates not loaded)
---

# KPI для {department}

## Корпоративные КПЭ (40%)
- Продажи/Выручка компании: согласно годовому плану
- Ввод в эксплуатацию ЖК: согласно годовому плану
- Стратегические инициативы: выполнение плана

## Личные КПЭ департамента (60%)

### Выполнение ключевых задач (30%)
- Целевое значение: ≥ 90% задач в срок
- Источник: Отчеты руководителя

### Качество работы (30%)
- Целевое значение: ≥ 85% работ без переделок
- Источник: Обратная связь заказчиков

⚠️ **ВНИМАНИЕ**: Используется минимальный fallback. Необходимо создать специфичные KPI.
"""

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
        """Проверка существования всех KPI файлов"""
        result = {}
        for kpi_file in self.get_available_kpi_files():
            file_path = self.kpi_dir / kpi_file
            result[kpi_file] = file_path.exists()
        return result if result else {self.default_kpi_file: (self.kpi_dir / self.default_kpi_file).exists()}


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

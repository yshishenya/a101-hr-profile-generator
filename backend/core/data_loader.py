"""
DataLoader с детерминированной логикой для системы генерации профилей А101.

Основной компонент для подготовки всех данных с детерминированной логикой маппинга
для передачи в Langfuse в качестве переменных промпта.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from .data_mapper import OrganizationMapper, KPIMapper
from .organization_cache import organization_cache

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Главный загрузчик данных с детерминированной логикой маппинга.
    Подготавливает все переменные для Langfuse промптов.
    """

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)

        # Инициализация маппинговых компонентов
        self.org_mapper = OrganizationMapper("data/structure.json")
        self.kpi_mapper = KPIMapper("data/KPI")

        # Кеш для статических данных
        self._cache = {}

        # Пути к статическим файлам - все в ./data
        self.paths = {
            "company_map": Path("data") / "Карта Компании А101.md",
            "org_structure": Path("data") / "structure.json",
            "it_systems": Path("data") / "anonymized_digitization_map.md",
            "json_schema": Path("templates") / "job_profile_schema.json",
        }

    def prepare_langfuse_variables(
        self, department: str, position: str, employee_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Подготовка всех данных с детерминированной логикой маппинга для Langfuse.

        Args:
            department: Название департамента
            position: Название должности
            employee_name: ФИО сотрудника (опционально)

        Returns:
            Словарь переменных для Langfuse промпта
        """
        logger.info(f"Preparing variables for {department} - {position}")

        try:
            # 🎯 ДЕТЕРМИНИРОВАННОЕ ИЗВЛЕЧЕНИЕ СТРУКТУРЫ
            org_structure = self._load_org_structure_for_department(department)
            department_path = org_structure.get("department_path", department)

            # 🎯 ДЕТЕРМИНИРОВАННЫЙ ВЫБОР KPI ФАЙЛА
            kpi_content = self.kpi_mapper.load_kpi_content(department)
            
            # 🎯 ИЗВЛЕЧЕНИЕ ДАННЫХ О ЧИСЛЕННОСТИ
            headcount_info = self.org_mapper.get_headcount_info(department)
            subordinates_count = self.org_mapper.calculate_subordinates_count(department, position)

            # Подготовка всех переменных
            variables = {
                # ОСНОВНОЙ КОНТЕКСТ (кешируется)
                "company_map": self._load_company_map_cached(),  # ~110K символов
                "json_schema": self._load_profile_schema_cached(),  # ~1K токенов (нужна для промпта)
                # РЕЛЕВАНТНАЯ СТРУКТУРА (детерминированно извлеченная)
                "org_structure": json.dumps(
                    org_structure, ensure_ascii=False, indent=2
                ),  # ~5K токенов
                "department_path": department_path,
                # ПОЛНАЯ ОРГАНИЗАЦИОННАЯ СТРУКТУРА с выделением цели
                "OrgStructure": json.dumps(
                    self._get_organization_structure_with_target(
                        f"{department}/{position}"
                    ),
                    ensure_ascii=False,
                    indent=2,
                ),  # ~229K символов - полная структура с выделением
                # ПОЗИЦИОННЫЕ ДАННЫЕ
                "position": position,
                "department": department,
                "employee_name": employee_name or "",
                # ДИНАМИЧЕСКИЙ КОНТЕКСТ (детерминированно найденный)
                "kpi_data": kpi_content,  # 0-15K токенов
                "it_systems": self._load_it_systems_cached(),  # ~15K токенов
                # ДАННЫЕ О ЧИСЛЕННОСТИ И ПОДЧИНЕННЫХ (НОВОЕ!)
                "headcount_info": headcount_info,  # Полная информация о численности департамента
                "subordinates_calculation": subordinates_count,  # Расчет подчиненных на основе реальных данных
                "department_headcount": headcount_info.get("headcount"),  # Прямое значение для удобства
                "headcount_source": headcount_info.get("headcount_source"),  # Источник данных о численности
                # МЕТАДАННЫЕ
                "generation_timestamp": datetime.now().isoformat(),
                "data_version": "v1.1",  # Увеличена версия из-за добавления данных о численности
            }

            # Подсчет токенов для мониторинга
            estimated_tokens = self._estimate_tokens(variables)
            variables["estimated_input_tokens"] = estimated_tokens

            logger.info(
                f"Variables prepared successfully. Estimated tokens: {estimated_tokens}"
            )
            return variables

        except Exception as e:
            logger.error(f"Error preparing Langfuse variables: {e}")
            raise

    def _load_company_map_cached(self) -> str:
        """Загрузка карты компании А101 с кешированием"""
        cache_key = "company_map"

        if cache_key not in self._cache:
            try:
                with open(self.paths["company_map"], "r", encoding="utf-8") as f:
                    content = f.read()

                self._cache[cache_key] = content
                logger.info(f"Company map loaded: {len(content)} chars")

            except Exception as e:
                logger.error(f"Error loading company map: {e}")
                self._cache[cache_key] = (
                    "# Карта компании недоступна\n\nОшибка загрузки данных."
                )

        return self._cache[cache_key]
    
    def _get_organization_structure_with_target(self, target_path: str) -> Dict[str, Any]:
        """
        Получение полной организационной структуры с выделенной целевой позицией.
        
        Интегрированная версия логики из CatalogService для устранения зависимости.
        Напрямую использует organization_cache.
        
        Args:
            target_path: Полный путь к целевой бизнес-единице (department/position)
        
        Returns:
            Dict[str, Any]: Полная структура с выделенной целью
        """
        try:
            # Проверяем существование целевого пути  
            target_unit = organization_cache.find_unit_by_path(target_path)
            if not target_unit:
                logger.warning(f"Target path not found: {target_path}")
                return {
                    "error": f"Business unit at path '{target_path}' not found",
                    "available_paths": list(
                        organization_cache.get_all_business_units_with_paths().keys()
                    )[:10],  # Первые 10 для примера
                }

            # Получаем структуру с подсвеченной целью
            highlighted_structure = organization_cache.get_structure_with_target_highlighted(
                target_path
            )

            # Добавляем метаданные для LLM (копия логики из CatalogService)
            highlighted_structure["target_unit_info"] = {
                "name": target_unit["name"],
                "full_path": target_path,
                "positions_count": len(target_unit["positions"]),
                "positions": target_unit["positions"],
                "hierarchy_level": target_unit["level"],
            }

            logger.debug(f"✅ Generated structure with target: {target_path}")
            return highlighted_structure

        except Exception as e:
            logger.error(f"❌ Error getting organization structure with target: {e}")
            return {
                "error": f"Failed to retrieve organization structure: {str(e)}",
                "target_path": target_path,
            }

    def _load_org_structure_for_department(self, department: str) -> dict:
        """Загрузка организационной структуры для департамента из централизованного кеша"""
        try:
            # Используем централизованный кеш вместо прямого чтения файла
            dept_info = organization_cache.find_department(department)

            if dept_info:
                dept_node = dept_info["node"]
                return {
                    "department_path": dept_info["path"],
                    "structure": {
                        "name": department,
                        "number": dept_node.get("number"),
                        "positions": dept_node.get("positions", []),
                        "children": dept_node.get("children", {}),
                    },
                    "found": True,
                }
            else:
                logger.warning(f"Department not found in cache: {department}")
                return {
                    "department_path": department,
                    "structure": {"name": department, "positions": []},
                    "found": False,
                }

        except Exception as e:
            logger.error(f"Error loading organization structure from cache: {e}")
            return {
                "department_path": department,
                "structure": {"name": department, "positions": []},
                "found": False,
                "error": str(e),
            }

    def _load_it_systems_cached(self) -> str:
        """Загрузка IT систем из anonymized_digitization_map.md с кешированием"""
        cache_key = "it_systems"

        if cache_key not in self._cache:
            try:
                with open(self.paths["it_systems"], "r", encoding="utf-8") as f:
                    content = f.read()

                self._cache[cache_key] = content
                logger.info(f"IT systems loaded: {len(content)} chars")

            except Exception as e:
                logger.error(f"Error loading IT systems: {e}")
                self._cache[cache_key] = (
                    "# IT системы недоступны\n\nОшибка загрузки данных об IT системах."
                )

        return self._cache[cache_key]

    def _load_architect_examples_cached(self) -> str:
        """Загрузка примеров профилей архитекторов с кешированием"""
        cache_key = "architect_examples"

        if cache_key not in self._cache:
            # Поскольку это Excel файл, мы не можем просто прочитать его как текст
            # В реальной реализации здесь будет pandas для чтения Excel
            # Пока возвращаем placeholder
            self._cache[
                cache_key
            ] = """# Примеры профилей архитекторов

Данные примеры профилей служат эталоном качества и детализации для генерации новых профилей.

[PLACEHOLDER: Здесь будут загружаться детальные профили архитекторов из Excel файла]

Ключевые характеристики эталонных профилей:
- Детальные области ответственности (3-7 задач каждая)
- Профессиональные навыки с четкими уровнями
- Конкретные корпоративные компетенции А101
- Реалистичные карьерные пути
- Специфичные технические требования
"""
            logger.warning(
                "Architect examples placeholder loaded (Excel parsing not implemented)"
            )

        return self._cache[cache_key]

    def _load_profile_schema_cached(self) -> str:
        """Загрузка JSON схемы профиля с кешированием"""
        cache_key = "profile_schema"

        if cache_key not in self._cache:
            try:
                with open(self.paths["json_schema"], "r", encoding="utf-8") as f:
                    schema_data = json.load(f)

                # Возвращаем читабельную JSON строку
                self._cache[cache_key] = json.dumps(
                    schema_data, ensure_ascii=False, indent=2
                )
                logger.info("Profile JSON schema loaded")

            except Exception as e:
                logger.error(f"Error loading profile schema: {e}")
                self._cache[cache_key] = '{"error": "Schema not available"}'

        return self._cache[cache_key]

    def _load_relevant_it_systems(self, department: str) -> str:
        """Загрузка релевантных IT систем для департамента"""
        it_systems_dir = self.paths["it_systems_dir"]

        if not it_systems_dir.exists():
            return "# IT системы недоступны\n\nДанные об IT системах не найдены."

        # Детерминированный поиск релевантного файла IT систем
        relevant_files = []

        # Ищем файлы, содержащие название департамента
        for file_path in it_systems_dir.glob("*.md"):
            filename = file_path.name.lower()
            dept_lower = department.lower()

            # Проверяем соответствие названия файла департаменту
            if any(
                keyword in filename
                for keyword in [
                    dept_lower,
                    dept_lower.replace(" ", "_"),
                    dept_lower.replace("департамент", "dept"),
                    (
                        "общий"
                        if "финанс" in dept_lower or "коммерч" in dept_lower
                        else ""
                    ),
                ]
            ):
                relevant_files.append(file_path)

        # Если не нашли конкретных файлов, ищем общие
        if not relevant_files:
            for file_path in it_systems_dir.glob("*.md"):
                filename = file_path.name.lower()
                if any(
                    keyword in filename
                    for keyword in ["general", "общий", "corporate", "корпоративн"]
                ):
                    relevant_files.append(file_path)

        # Загружаем и объединяем содержимое
        combined_content = []

        for file_path in relevant_files[:3]:  # Максимум 3 файла для контроля токенов
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                combined_content.append(f"## {file_path.stem}\n\n{content}")

            except Exception as e:
                logger.error(f"Error loading IT systems file {file_path}: {e}")

        if not combined_content:
            return f"# IT системы для {department}\n\nСпецифичные данные по IT системам департамента недоступны."

        result = "\n\n---\n\n".join(combined_content)

        # Ограничиваем длину (максимум 20K токенов ≈ 60K символов)
        if len(result) > 60000:
            result = (
                result[:60000] + "\n\n[...контент обрезан для оптимизации токенов...]"
            )
            logger.warning("IT systems content truncated due to length")

        logger.info(
            f"IT systems loaded for '{department}': {len(relevant_files)} files, {len(result)} chars"
        )
        return result

    def _estimate_tokens(self, variables: Dict[str, Any]) -> int:
        """Приблизительная оценка количества токенов"""
        total_chars = 0

        for key, value in variables.items():
            if isinstance(value, str):
                total_chars += len(value)
            elif isinstance(value, (dict, list)):
                total_chars += len(json.dumps(value, ensure_ascii=False))

        # Приблизительная формула: 1 токен ≈ 3.5 символа для русского текста
        estimated_tokens = int(total_chars / 3.5)

        return estimated_tokens

    def load_full_organization_structure(self) -> Dict[str, Any]:
        """
        Загрузка полной структуры организации за один запрос с кешированием.

        Returns:
            Dict с полной структурой департаментов и позиций
        """
        cache_key = "full_org_structure"

        if cache_key not in self._cache:
            start_time = datetime.now()
            logger.info("Loading full organization structure...")

            # Данные теперь всегда доступны через централизованный кеш
            # Проверка не нужна, так как кеш загружается при старте приложения

            # Загружаем всю структуру за один проход
            full_structure = {
                "departments": {},
                "metadata": {
                    "total_departments": 0,
                    "total_positions": 0,
                    "loaded_at": start_time.isoformat(),
                },
            }

            # Получаем все департаменты
            all_departments = (
                list(self.org_mapper._department_index.keys())
                if self.org_mapper._department_index
                else []
            )

            for dept_name in all_departments:
                # Получаем позиции для каждого департамента
                positions = self._get_positions_for_department_internal(dept_name)

                # Определяем путь департамента
                dept_path = self.org_mapper.find_department_path(dept_name)

                # Собираем информацию о департаменте
                dept_info = {
                    "name": dept_name,
                    "path": dept_path,
                    "positions": [
                        {
                            "name": pos_name,
                            "level": self._determine_position_level(pos_name),
                            "category": self._determine_position_category(pos_name),
                        }
                        for pos_name in positions
                    ],
                    "positions_count": len(positions),
                }

                full_structure["departments"][dept_name] = dept_info
                full_structure["metadata"]["total_positions"] += len(positions)

            full_structure["metadata"]["total_departments"] = len(all_departments)

            # Кеширование результата
            self._cache[cache_key] = full_structure

            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"✅ Full organization structure loaded in {load_time:.3f}s: "
                f"{full_structure['metadata']['total_departments']} departments, "
                f"{full_structure['metadata']['total_positions']} positions"
            )

        return self._cache[cache_key]

    def get_available_departments(self) -> List[str]:
        """Получение списка всех доступных департаментов"""
        # Используем оптимизированный метод
        full_structure = self.load_full_organization_structure()
        return list(full_structure["departments"].keys())

    def _get_positions_for_department_internal(self, department: str) -> List[str]:
        """Внутренний метод для получения позиций департамента из реальной оргструктуры"""
        try:
            # Загружаем позиции из реальной структуры через OrganizationMapper
            real_positions = self.org_mapper.get_positions_for_department(department)

            if real_positions:
                logger.debug(
                    f"Found {len(real_positions)} real positions for '{department}' in org structure"
                )
                return real_positions
            else:
                logger.warning(
                    f"No positions found in org structure for '{department}', using fallback"
                )
                # Только минимальный fallback из общих должностей
                return ["Специалист", "Ведущий специалист", "Руководитель"]

        except Exception as e:
            logger.error(f"Error getting positions for {department}: {e}")
            return ["Специалист"]  # Минимальный fallback

    def _determine_position_level(self, position_name: str) -> str:
        """Определение уровня должности по названию"""
        from ..utils.position_utils import determine_position_level

        return determine_position_level(position_name, "string")

    def _determine_position_category(self, position_name: str) -> str:
        """Определение категории должности"""
        from ..utils.position_utils import determine_position_category

        return determine_position_category(position_name)

    def get_positions_for_department(self, department: str) -> List[str]:
        """
        Получение списка должностей для конкретного департамента.
        Использует кешированную полную структуру для быстрого доступа.
        """
        try:
            # Получаем данные из кешированной полной структуры
            full_structure = self.load_full_organization_structure()

            if department in full_structure["departments"]:
                # Возвращаем имена позиций из кешированной структуры
                positions = [
                    pos["name"]
                    for pos in full_structure["departments"][department]["positions"]
                ]
                return positions
            else:
                logger.warning(
                    f"Department '{department}' not found in organization structure"
                )
                return []

        except Exception as e:
            logger.error(f"Error getting positions for department '{department}': {e}")
            # Fallback to internal method
            return self._get_positions_for_department_internal(department)

    def clear_cache(self):
        """Очистка кеша (полезно для тестирования)"""
        self._cache.clear()
        logger.info("Cache cleared")

    def validate_data_sources(self) -> Dict[str, bool]:
        """Проверка доступности всех источников данных"""
        validation = {
            "company_map": self.paths["company_map"].exists(),
            "json_schema": self.paths["json_schema"].exists(),
            "it_systems": self.paths["it_systems"].exists(),
            "org_structure": self.paths["org_structure"].exists(),
            "kpi_file": Path("data/KPI/KPI_DIT.md").exists(),
        }

        # Проверяем KPI файлы
        kpi_validation = self.kpi_mapper.validate_kpi_mappings()
        validation["kpi_files"] = all(kpi_validation.values())

        return validation


if __name__ == "__main__":
    # Тестирование DataLoader
    logging.basicConfig(level=logging.INFO)

    print("=== Тестирование DataLoader ===")
    loader = DataLoader()

    # Проверка источников данных
    validation = loader.validate_data_sources()
    print("Валидация источников данных:")
    for source, status in validation.items():
        print(f"  {source}: {'✅' if status else '❌'}")

    print("\n=== Тест подготовки переменных ===")
    try:
        variables = loader.prepare_langfuse_variables(
            department="ДИТ",
            position="Архитектор решений",
            employee_name="Иванов Иван Иванович",
        )

        print(f"Переменные подготовлены:")
        print(f"  - Департамент: {variables['department']}")
        print(f"  - Путь в структуре: {variables['department_path']}")
        print(f"  - Должность: {variables['position']}")
        print(f"  - Оценка токенов: {variables['estimated_input_tokens']}")
        print(f"  - Размер карты компании: {len(variables['company_map'])} символов")
        print(f"  - Размер KPI данных: {len(variables['kpi_data'])} символов")

    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

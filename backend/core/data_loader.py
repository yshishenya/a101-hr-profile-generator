"""
DataLoader с детерминированной логикой для системы генерации профилей А101.

Основной компонент для подготовки всех данных с детерминированной логикой маппинга
для передачи в Langfuse в качестве переменных промпта.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

from .data_mapper import OrganizationMapper, KPIMapper
from .organization_cache import organization_cache

logger = logging.getLogger(__name__)


class PositionType(Enum):
    """Position type for IT systems relevance categorization."""

    IT_TECHNICAL = "it_technical"  # Full 15K tokens - technical roles
    IT_MANAGEMENT = "it_management"  # 3K tokens - IT leadership
    BUSINESS_TECHNICAL = "business_technical"  # 5K tokens - product/project roles
    BUSINESS_GENERAL = "business_general"  # 1K tokens - general business roles
    SUPPORT = "support"  # 1K tokens - administrative/support roles


# Position keywords mapping for categorization
POSITION_KEYWORDS = {
    PositionType.IT_TECHNICAL: [
        r"программист",
        r"разработчик",
        r"developer",
        r"архитектор",
        r"engineer",
        r"инженер",
        r"devops",
        r"администратор",
        r"тестировщик",
        r"qa",
        r"аналитик.*данных",
        r"data",
        r"backend",
        r"frontend",
        r"fullstack",
        r"системн.*инженер",
        r"сетев.*инженер",
    ],
    PositionType.IT_MANAGEMENT: [
        r"руководитель.*ит",
        r"директор.*технолог",
        r"директор.*ит",
        r"cto",
        r"cio",
        r"начальник.*разработки",
        r"руководитель.*информац",
        r"руководитель.*цифров",
        r"начальник.*информац",
    ],
    PositionType.BUSINESS_TECHNICAL: [
        r"продукт",
        r"product",
        r"owner",
        r"менеджер.*проект",
        r"project.*manager",
        r"scrum.*master",
        r"agile",
        r"бизнес.*аналитик",
    ],
    PositionType.BUSINESS_GENERAL: [
        r"менеджер",
        r"специалист",
        r"координатор",
        r"директор",
        r"руководитель",
        r"начальник",
    ],
    PositionType.SUPPORT: [
        r"ассистент",
        r"секретарь",
        r"помощник",
        r"стажер",
        r"junior",
        r"делопроизводител",
    ],
}


def detect_position_type(position: str, department: str) -> PositionType:
    """
    Detect position type for IT systems relevance.

    Logic:
    1. Check position keywords (most specific)
    2. Check if department is IT-related
    3. Default to BUSINESS_GENERAL

    Args:
        position: Position name
        department: Department name

    Returns:
        PositionType enum value
    """
    pos_lower = position.lower()
    dept_lower = department.lower()

    # Check position keywords by priority (most specific first)
    for pos_type in [
        PositionType.IT_TECHNICAL,
        PositionType.IT_MANAGEMENT,
        PositionType.BUSINESS_TECHNICAL,
        PositionType.SUPPORT,
        PositionType.BUSINESS_GENERAL,
    ]:
        keywords = POSITION_KEYWORDS[pos_type]
        if any(re.search(keyword, pos_lower) for keyword in keywords):
            logger.debug(f"Position '{position}' classified as {pos_type.value} by keyword match")
            return pos_type

    # Department-based fallback for IT departments
    it_dept_keywords = [r"ит", r"информационн", r"цифров", r"данных", r"digital"]
    if any(re.search(kw, dept_lower) for kw in it_dept_keywords):
        logger.debug(f"Position '{position}' in IT dept '{department}' classified as IT_MANAGEMENT")
        return PositionType.IT_MANAGEMENT

    logger.debug(f"Position '{position}' defaulted to BUSINESS_GENERAL")
    return PositionType.BUSINESS_GENERAL


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
            # 🔥 FIX: Извлекаем короткое имя департамента для методов, которые его ожидают
            if "/" in department:
                department_parts = [p.strip() for p in department.split("/") if p.strip()]
                department_short_name = department_parts[-1]  # Последний элемент
                logger.info(
                    f"Extracted short department name '{department_short_name}' from path '{department}'"
                )
            else:
                department_short_name = department

            # 🎯 ДЕТЕРМИНИРОВАННОЕ ИЗВЛЕЧЕНИЕ СТРУКТУРЫ (использует короткое имя)
            org_structure = self._load_org_structure_for_department(department_short_name)

            # 🎯 НОВОЕ: ИЗВЛЕЧЕНИЕ ПОЛНОЙ ИЕРАРХИИ ДО ПОЗИЦИИ (принимает полный путь или короткое имя)
            hierarchy_info = self._extract_full_position_path(department, position)
            department_path = hierarchy_info.get("department_path_legacy", department)

            # 🎯 ДЕТЕРМИНИРОВАННЫЙ ВЫБОР KPI ФАЙЛА (использует короткое имя)
            kpi_content = self.kpi_mapper.load_kpi_content(department_short_name)

            # 🆕 METADATA: Track KPI source (specific file vs template)
            kpi_metadata = self._detect_kpi_source(department_short_name)

            # 🎯 ИЗВЛЕЧЕНИЕ ДАННЫХ О ЧИСЛЕННОСТИ (использует короткое имя)
            headcount_info = self.org_mapper.get_headcount_info(department_short_name)
            subordinates_count = self.org_mapper.calculate_subordinates_count(
                department_short_name, position
            )

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
                    self._get_organization_structure_with_target(f"{department}/{position}"),
                    ensure_ascii=False,
                    indent=2,
                ),  # ~229K символов - полная структура с выделением
                # ПОЗИЦИОННЫЕ ДАННЫЕ
                "position": position,
                "department": department,  # Полный путь (как передано генератором)
                "department_name": department_short_name,  # Короткое имя для логики в промпте
                "employee_name": employee_name or "",
                # ДИНАМИЧЕСКИЙ КОНТЕКСТ (детерминированно найденный)
                "kpi_data": kpi_content,  # 0-15K токенов
                "kpi_source": kpi_metadata["source"],  # NEW: "specific" or "template"
                "kpi_type": kpi_metadata["dept_type"],  # NEW: "IT", "SALES", "GENERIC" etc
                "it_systems": self._load_it_systems_conditional(
                    position, department_short_name
                ),  # 1K-15K токенов (conditional)
                "it_systems_detail_level": detect_position_type(
                    position, department_short_name
                ).value,  # metadata
                # ДАННЫЕ О ЧИСЛЕННОСТИ И ПОДЧИНЕННЫХ
                "headcount_info": headcount_info,  # Полная информация о численности департамента
                "subordinates_calculation": subordinates_count,  # Расчет подчиненных на основе реальных данных
                "department_headcount": headcount_info.get(
                    "headcount"
                ),  # Прямое значение для удобства
                "headcount_source": headcount_info.get(
                    "headcount_source"
                ),  # Источник данных о численности
                # ПЛОСКИЕ ПЕРЕМЕННЫЕ ДЛЯ ПОДЧИНЕННОСТИ (без точек для Langfuse)
                "subordinates_departments": subordinates_count.get("departments", 0),
                "subordinates_direct_reports": subordinates_count.get("direct_reports", 0),
                # НОВЫЕ ПЕРЕМЕННЫЕ ИЕРАРХИИ (Блок-Департамент-Управление-Отдел-ПодОтдел-Группа)
                "business_block": hierarchy_info.get("business_block", ""),  # Уровень 1: Блок
                "department_unit": hierarchy_info.get(
                    "department_unit", ""
                ),  # Уровень 2: Департамент
                "section_unit": hierarchy_info.get(
                    "section_unit", ""
                ),  # Уровень 3: Управление/Отдел
                "group_unit": hierarchy_info.get("group_unit", ""),  # Уровень 4: Отдел
                "sub_section_unit": hierarchy_info.get(
                    "sub_section_unit", ""
                ),  # Уровень 5: Под-отдел
                "final_group_unit": hierarchy_info.get("final_group_unit", ""),  # Уровень 6: Группа
                "hierarchy_level": hierarchy_info.get(
                    "hierarchy_level", 1
                ),  # Номер уровня в иерархии
                "full_hierarchy_path": hierarchy_info.get(
                    "full_hierarchy_path", department
                ),  # Полный путь с разделителями
                # РАЗЛОЖЕНИЕ ИЕРАРХИИ (плоские переменные для Langfuse)
                "hierarchy_levels_list": ", ".join(
                    hierarchy_info.get("full_path_parts", [department])
                ),
                "hierarchy_current_level": hierarchy_info.get("hierarchy_level", 1),
                "hierarchy_final_unit": hierarchy_info.get("final_unit", department),
                "position_location": f"{hierarchy_info.get('final_unit', department)}/{position}",
                # МЕТАДАННЫЕ
                "generation_timestamp": datetime.now().isoformat(),
                "data_version": "v1.3",  # v1.3: Added KPI templates for 100% coverage + metadata tracking
            }

            # Подсчет токенов для мониторинга
            estimated_tokens = self._estimate_tokens(variables)
            variables["estimated_input_tokens"] = estimated_tokens

            logger.info(f"Variables prepared successfully. Estimated tokens: {estimated_tokens}")
            return variables

        except Exception as e:
            logger.error(f"Error preparing Langfuse variables: {e}")
            raise

    def _detect_kpi_source(self, department: str) -> Dict[str, str]:
        """
        Detect KPI source: specific file or generic template.

        Args:
            department: Department name

        Returns:
            Dict with 'source' and 'dept_type' metadata
        """
        # Check if specific KPI file exists
        kpi_filename = self.kpi_mapper.find_kpi_file(department)

        # Handle None case (no KPI file found - 71.2% of departments)
        if kpi_filename is None:
            # Using template if available
            if self.kpi_mapper.templates_available:
                dept_type = self.kpi_mapper.detect_department_type(department)
                return {"source": "template", "dept_type": dept_type, "kpi_file": None}

            # No KPI and no template
            return {"source": "none", "dept_type": "N/A", "kpi_file": None}

        # KPI filename found, check if file exists
        kpi_path = self.kpi_mapper.kpi_dir / kpi_filename

        if kpi_path.exists():
            return {
                "source": "specific",
                "dept_type": "N/A",  # Specific file, no template type
                "kpi_file": kpi_filename,
            }

        # KPI filename exists but file not found - fallback to template
        if self.kpi_mapper.templates_available:
            dept_type = self.kpi_mapper.detect_department_type(department)
            return {"source": "template", "dept_type": dept_type, "kpi_file": None}

        # Last resort fallback
        return {"source": "fallback", "dept_type": "GENERIC", "kpi_file": None}

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
                self._cache[cache_key] = "# Карта компании недоступна\n\nОшибка загрузки данных."

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
                    )[
                        :10
                    ],  # Первые 10 для примера
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

    def _load_it_systems_conditional(self, position: str, department: str) -> str:
        """
        Load IT systems with conditional complexity based on position type.

        Args:
            position: Position name
            department: Department name

        Returns:
            IT systems content tailored to position type
        """
        # Detect position type
        pos_type = detect_position_type(position, department)

        # Load full content
        full_content = self._load_it_systems_cached()

        # Apply compression based on type
        if pos_type == PositionType.IT_TECHNICAL:
            # Full content (~15K tokens)
            tokens = len(full_content) / 3.5
            logger.info(f"IT_TECHNICAL: Loading full IT systems (~{tokens:.0f} tokens)")
            return full_content

        elif pos_type == PositionType.IT_MANAGEMENT:
            # Summary + key systems (~3K tokens)
            compressed = self._compress_it_systems_for_management(full_content)
            tokens = len(compressed) / 3.5
            logger.info(f"IT_MANAGEMENT: Loading compressed IT systems (~{tokens:.0f} tokens)")
            return compressed

        elif pos_type == PositionType.BUSINESS_TECHNICAL:
            # Business systems only (~5K tokens)
            business_only = self._extract_business_systems(full_content)
            tokens = len(business_only) / 3.5
            logger.info(f"BUSINESS_TECHNICAL: Loading business systems (~{tokens:.0f} tokens)")
            return business_only

        else:  # BUSINESS_GENERAL or SUPPORT
            # High-level overview (~1K tokens)
            minimal = self._compress_it_systems_minimal(full_content)
            tokens = len(minimal) / 3.5
            logger.info(f"{pos_type.value}: Loading minimal IT systems (~{tokens:.0f} tokens)")
            return minimal

    def _parse_markdown_sections(self, content: str) -> Dict[str, str]:
        """
        Parse markdown content into sections by headers.

        Args:
            content: Markdown content

        Returns:
            Dict mapping header to section content
        """
        sections = {}
        current_header = None
        current_content = []

        for line in content.split("\n"):
            if line.startswith("#"):
                if current_header:
                    sections[current_header] = "\n".join(current_content)
                current_header = line
                current_content = []
            else:
                current_content.append(line)

        if current_header:
            sections[current_header] = "\n".join(current_content)

        return sections

    def _compress_it_systems_for_management(self, full_content: str) -> str:
        """
        Compress IT systems for management roles.

        Include:
        - Overview section
        - Key strategic systems (first 3 items from each category)
        Omit:
        - Detailed system lists beyond first 3 items

        Target: ~3K tokens (10K chars)

        Args:
            full_content: Full IT systems content

        Returns:
            Compressed content for management
        """
        lines = full_content.split("\n")
        compressed = []
        current_category = None
        items_in_category = 0
        max_items_per_category = 3

        for line in lines:
            # Keep headers and warnings
            if line.startswith("#") or line.startswith(">"):
                compressed.append(line)
                if line.startswith("###"):
                    current_category = line
                    items_in_category = 0
            # Keep first N items per category
            elif line.startswith("-") and current_category:
                if items_in_category < max_items_per_category:
                    compressed.append(line)
                    items_in_category += 1
                elif items_in_category == max_items_per_category:
                    compressed.append(
                        f"- *...и другие системы категории {current_category.replace('###', '').strip()}*"
                    )
                    items_in_category += 1  # Increment to prevent repeated ellipsis
            elif not line.strip():
                compressed.append(line)

        result = "\n".join(compressed)

        # Ensure target size (~10K chars)
        if len(result) > 10000:
            result = (
                result[:10000] + "\n\n*[...сокращено для релевантности руководящей позиции...]*"
            )

        return result

    def _extract_business_systems(self, full_content: str) -> str:
        """
        Extract only business-facing systems.

        Include categories:
        - Маркетинг и продажи
        - Персонал и HR
        - Документооборот и делопроизводство
        - Бюджетирование и финансы
        - Передача и эксплуатация

        Omit:
        - Информационные технологии (infrastructure)
        - Deep technical details

        Target: ~5K tokens (15K chars)

        Args:
            full_content: Full IT systems content

        Returns:
            Business-oriented systems content
        """
        business_categories = [
            "Маркетинг и продажи",
            "Персонал и HR",
            "Документооборот и делопроизводство",
            "Бюджетирование и финансы",
            "Передача и эксплуатация",
            "Закупки и снабжение",
            "Планирование и отчетность",
        ]

        lines = full_content.split("\n")
        business_lines = []
        in_business_section = False
        current_section = None

        for line in lines:
            # Check if we're entering a business category
            if line.startswith("###"):
                section_name = (
                    line.replace("###", "").strip().split(".")[1].strip() if "." in line else ""
                )
                if any(cat in section_name for cat in business_categories):
                    in_business_section = True
                    current_section = section_name
                    business_lines.append(line)
                else:
                    in_business_section = False

            elif in_business_section:
                business_lines.append(line)

        if not business_lines:
            # Fallback to minimal if no business sections found
            return self._compress_it_systems_minimal(full_content)

        result = "# IT-системы (бизнес-ориентированные)\n\n"
        result += "> Фокус на системах, непосредственно используемых в бизнес-процессах\n\n"
        result += "\n".join(business_lines)

        # Limit to ~15K chars
        if len(result) > 15000:
            result = result[:15000] + "\n\n*[...сокращено для фокуса на бизнес-системах...]*"

        return result

    def _compress_it_systems_minimal(self, full_content: str) -> str:
        """
        Minimal IT systems overview for non-technical roles.

        Just key systems overview with 3-5 bullet points per category.
        Target: ~1K tokens (3K chars)

        Args:
            full_content: Full IT systems content (unused, for consistency)

        Returns:
            Minimal overview
        """
        return """# IT-системы компании (обзор)

> Общий обзор ключевых корпоративных систем

## Основные категории систем

### Управление бизнес-процессами
- **ERP-система** — планирование ресурсов, учет, финансы
- **ECM-система** — управление корпоративным контентом и документооборотом
- **CRM-система** — управление продажами и взаимоотношениями с клиентами

### Проектная деятельность
- **Система управления проектами** — планирование и контроль проектов
- **CAD/BIM-системы** — проектирование и моделирование
- **Система контроля строительства** — надзор за объектами

### Коммуникации и совместная работа
- **Корпоративная почта** — электронная почта и календари
- **Корпоративный мессенджер** — внутренние коммуникации
- **ВКС-платформа** — видеоконференции и онлайн-встречи

### HR и кадры
- **Корпоративный портал** — внутренний портал сотрудников
- **Система зарплаты и кадров** — расчет зарплаты и кадровый учет
- **Система обучения** — корпоративное обучение

**Для работы предоставляется доступ к релевантным системам согласно должностным обязанностям.**
"""

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
            logger.warning("Architect examples placeholder loaded (Excel parsing not implemented)")

        return self._cache[cache_key]

    def _load_profile_schema_cached(self) -> str:
        """Загрузка JSON схемы профиля с кешированием"""
        cache_key = "profile_schema"

        if cache_key not in self._cache:
            try:
                with open(self.paths["json_schema"], "r", encoding="utf-8") as f:
                    schema_data = json.load(f)

                # Возвращаем читабельную JSON строку
                self._cache[cache_key] = json.dumps(schema_data, ensure_ascii=False, indent=2)
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
                    ("общий" if "финанс" in dept_lower or "коммерч" in dept_lower else ""),
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
            result = result[:60000] + "\n\n[...контент обрезан для оптимизации токенов...]"
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
                    pos["name"] for pos in full_structure["departments"][department]["positions"]
                ]
                return positions
            else:
                logger.warning(f"Department '{department}' not found in organization structure")
                return []

        except Exception as e:
            logger.error(f"Error getting positions for department '{department}': {e}")
            # Fallback to internal method
            return self._get_positions_for_department_internal(department)

    def _extract_full_position_path(self, department: str, position: str) -> Dict[str, Any]:
        """
        Извлечение полного пути до позиции включая все уровни иерархии.

        Args:
            department: Название департамента (может быть полный путь или короткое имя)
            position: Название должности

        Returns:
            Dict с полным путем и разложением по уровням
        """
        try:
            # 🔥 FIX: Если передан полный путь, извлекаем последний элемент как имя департамента
            if "/" in department:
                department_parts = [p.strip() for p in department.split("/") if p.strip()]
                department_name = department_parts[-1]  # Последний элемент = имя департамента
                logger.info(
                    f"Extracted department name '{department_name}' from full path '{department}'"
                )
            else:
                department_name = department

            # Сначала находим департамент по короткому имени
            dept_info = organization_cache.find_department(department_name)
            if not dept_info:
                logger.warning(f"Department not found: {department_name}")
                return self._create_fallback_hierarchy_info(department_name, position)

            # Получаем базовый путь департамента
            dept_path = dept_info["path"]
            path_parts = [p.strip() for p in dept_path.split("/") if p.strip()]

            # Проверяем, есть ли позиция в детях департамента
            dept_node = dept_info["node"]
            positions_in_dept = dept_node.get("positions", [])

            # Если позиция найдена прямо в департаменте
            if position in positions_in_dept:
                full_path_parts = path_parts
                final_unit = department
            else:
                # Ищем позицию в дочерних подразделениях
                position_unit, position_path = self._find_position_in_children(
                    dept_node, position, dept_path
                )
                if position_unit:
                    full_path_parts = [p.strip() for p in position_path.split("/") if p.strip()]
                    final_unit = position_unit
                else:
                    # Позиция не найдена, используем департамент
                    logger.warning(
                        f"Position '{position}' not found in structure, using department level"
                    )
                    full_path_parts = path_parts
                    final_unit = department

            return self._build_hierarchy_info(full_path_parts, final_unit, position)

        except Exception as e:
            logger.error(f"Error extracting full position path: {e}")
            return self._create_fallback_hierarchy_info(department, position)

    def _find_position_in_children(
        self, node: dict, target_position: str, current_path: str
    ) -> tuple:
        """
        Рекурсивный поиск позиции в дочерних подразделениях.

        Returns:
            tuple: (unit_name, full_path) или (None, None)
        """
        children = node.get("children", {})
        for child_name, child_data in children.items():
            child_path = f"{current_path}/{child_name}"
            child_positions = child_data.get("positions", [])

            # Проверяем позиции в текущем дочернем подразделении
            if target_position in child_positions:
                return child_name, child_path

            # Рекурсивно ищем в детях
            found_unit, found_path = self._find_position_in_children(
                child_data, target_position, child_path
            )
            if found_unit:
                return found_unit, found_path

        return None, None

    def _build_hierarchy_info(
        self, path_parts: List[str], final_unit: str, position: str
    ) -> Dict[str, Any]:
        """Создание структурированной информации об иерархии (поддержка до 6 уровней)"""
        return {
            "full_path_parts": path_parts,
            "hierarchy_level": len(path_parts),
            "business_block": path_parts[0] if len(path_parts) > 0 else "",
            "department_unit": (
                path_parts[1] if len(path_parts) > 1 else path_parts[0] if path_parts else ""
            ),
            "section_unit": path_parts[2] if len(path_parts) > 2 else "",
            "group_unit": path_parts[3] if len(path_parts) > 3 else "",
            "sub_section_unit": path_parts[4] if len(path_parts) > 4 else "",  # Уровень 5
            "final_group_unit": path_parts[5] if len(path_parts) > 5 else "",  # Уровень 6
            "final_unit": final_unit,
            "position": position,
            "full_hierarchy_path": " → ".join(path_parts),
            "department_path_legacy": "/".join(path_parts),  # Для обратной совместимости
        }

    def _create_fallback_hierarchy_info(self, department: str, position: str) -> Dict[str, Any]:
        """
        Создание fallback информации при ошибках (поддержка до 6 уровней).

        Если department содержит полный путь, разбираем его.
        """
        # 🔥 FIX: Если передан полный путь, разбираем его
        if "/" in department:
            path_parts = [p.strip() for p in department.split("/") if p.strip()]
            return self._build_hierarchy_info(path_parts, path_parts[-1], position)

        # Иначе простой fallback
        return {
            "full_path_parts": [department],
            "hierarchy_level": 1,
            "business_block": "",
            "department_unit": department,
            "section_unit": "",
            "group_unit": "",
            "sub_section_unit": "",  # Уровень 5
            "final_group_unit": "",  # Уровень 6
            "final_unit": department,
            "position": position,
            "full_hierarchy_path": department,
            "department_path_legacy": department,
        }

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

        print("Переменные подготовлены:")
        print(f"  - Департамент: {variables['department']}")
        print(f"  - Путь в структуре: {variables['department_path']}")
        print(f"  - Должность: {variables['position']}")
        print(f"  - Оценка токенов: {variables['estimated_input_tokens']}")
        print(f"  - Размер карты компании: {len(variables['company_map'])} символов")
        print(f"  - Размер KPI данных: {len(variables['kpi_data'])} символов")

    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

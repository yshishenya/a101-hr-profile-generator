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

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Главный загрузчик данных с детерминированной логикой маппинга.
    Подготавливает все переменные для Langfuse промптов.
    """
    
    def __init__(self, base_path: str = "/home/yan/A101/HR"):
        self.base_path = Path(base_path)
        
        # Инициализация маппинговых компонентов
        self.org_mapper = OrganizationMapper(
            str(self.base_path / "org_structure" / "structure.json")
        )
        self.kpi_mapper = KPIMapper(
            str(self.base_path / "KPI" / "md_converted")
        )
        
        # Кеш для статических данных
        self._cache = {}
        
        # Пути к статическим файлам
        self.paths = {
            "company_map": self.base_path / "Карта Компании А101.md",
            "profile_examples": self.base_path / "Profiles" / "Профили архитекторы.xlsx",
            "json_schema": self.base_path / "Profiles" / "job_profile_schema.json",
            "it_systems_dir": self.base_path / "IT systems"
        }
    
    def prepare_langfuse_variables(self, department: str, position: str, employee_name: Optional[str] = None) -> Dict[str, Any]:
        """Prepare variables for Langfuse based on department and position."""
        logger.info(f"Preparing variables for {department} - {position}")
        
        try:
            # 🎯 ДЕТЕРМИНИРОВАННОЕ ИЗВЛЕЧЕНИЕ СТРУКТУРЫ
            org_structure = self.org_mapper.extract_relevant_structure(department)
            department_path = org_structure.get("department_path", department)
            
            # 🎯 ДЕТЕРМИНИРОВАННЫЙ ВЫБОР KPI ФАЙЛА  
            kpi_content = self.kpi_mapper.load_kpi_content(department)
            
            # Подготовка всех переменных
            variables = {
                # ОСНОВНОЙ КОНТЕКСТ (кешируется)
                "company_map": self._load_company_map_cached(),           # ~47K токенов
                "profile_examples": self._load_architect_examples_cached(), # ~30K токенов
                "json_schema": self._load_profile_schema_cached(),        # ~1K токенов
                
                # РЕЛЕВАНТНАЯ СТРУКТУРА (детерминированно извлеченная)
                "org_structure": json.dumps(org_structure, ensure_ascii=False, indent=2), # ~5K токенов
                "department_path": department_path,
                
                # ПОЗИЦИОННЫЕ ДАННЫЕ
                "position": position,
                "department": department,
                "employee_name": employee_name or "",
                
                # ДИНАМИЧЕСКИЙ КОНТЕКСТ (детерминированно найденный)
                "kpi_data": kpi_content,                                 # 0-15K токенов
                "it_systems": self._load_relevant_it_systems(department), # 5-20K токенов
                
                # МЕТАДАННЫЕ
                "generation_timestamp": datetime.now().isoformat(),
                "data_version": "v1.0"
            }
            
            # Подсчет токенов для мониторинга
            estimated_tokens = self._estimate_tokens(variables)
            variables["estimated_input_tokens"] = estimated_tokens
            
            logger.info(f"Variables prepared successfully. Estimated tokens: {estimated_tokens}")
            return variables
            
        except Exception as e:
            logger.error(f"Error preparing Langfuse variables: {e}")
            raise
    
    def _load_company_map_cached(self) -> str:
        """Load the company map with caching."""
        cache_key = "company_map"
        
        if cache_key not in self._cache:
            try:
                with open(self.paths["company_map"], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._cache[cache_key] = content
                logger.info(f"Company map loaded: {len(content)} chars")
                
            except Exception as e:
                logger.error(f"Error loading company map: {e}")
                self._cache[cache_key] = "# Карта компании недоступна\n\nОшибка загрузки данных."
        
        return self._cache[cache_key]
    
    def _load_architect_examples_cached(self) -> str:
        """Load architect profile examples with caching."""
        cache_key = "architect_examples"
        
        if cache_key not in self._cache:
            # Поскольку это Excel файл, мы не можем просто прочитать его как текст
            # В реальной реализации здесь будет pandas для чтения Excel
            # Пока возвращаем placeholder
            self._cache[cache_key] = """# Примеры профилей архитекторов

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
        """Load the profile JSON schema with caching."""
        cache_key = "profile_schema"
        
        if cache_key not in self._cache:
            try:
                with open(self.paths["json_schema"], 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                
                # Возвращаем читабельную JSON строку
                self._cache[cache_key] = json.dumps(schema_data, ensure_ascii=False, indent=2)
                logger.info("Profile JSON schema loaded")
                
            except Exception as e:
                logger.error(f"Error loading profile schema: {e}")
                self._cache[cache_key] = '{"error": "Schema not available"}'
        
        return self._cache[cache_key]
    
    def _load_relevant_it_systems(self, department: str) -> str:
        """Load relevant IT systems for a given department.
        
        This function searches for Markdown files in the specified IT systems directory
        that match the department name or related keywords. It first checks for
        specific files related to the department and, if none are found, looks for
        general files. The contents of up to three relevant files are then loaded and
        combined, with a character limit enforced to optimize token usage. If no
        relevant content is found, an appropriate message is returned.
        
        Args:
            department (str): The name of the department for which to load IT systems.
        
        Returns:
            str: A formatted string containing the relevant IT systems information or a message
                indicating unavailability.
        """
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
            if any(keyword in filename for keyword in [
                dept_lower, 
                dept_lower.replace(' ', '_'),
                dept_lower.replace('департамент', 'dept'),
                'общий' if 'финанс' in dept_lower or 'коммерч' in dept_lower else ''
            ]):
                relevant_files.append(file_path)
        
        # Если не нашли конкретных файлов, ищем общие
        if not relevant_files:
            for file_path in it_systems_dir.glob("*.md"):
                filename = file_path.name.lower()
                if any(keyword in filename for keyword in ['general', 'общий', 'corporate', 'корпоративн']):
                    relevant_files.append(file_path)
        
        # Загружаем и объединяем содержимое
        combined_content = []
        
        for file_path in relevant_files[:3]:  # Максимум 3 файла для контроля токенов
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
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
        
        logger.info(f"IT systems loaded for '{department}': {len(relevant_files)} files, {len(result)} chars")
        return result
    
    def _estimate_tokens(self, variables: Dict[str, Any]) -> int:
        """Estimate the number of tokens based on the provided variables."""
        total_chars = 0
        
        for key, value in variables.items():
            if isinstance(value, str):
                total_chars += len(value)
            elif isinstance(value, (dict, list)):
                total_chars += len(json.dumps(value, ensure_ascii=False))
        
        # Приблизительная формула: 1 токен ≈ 3.5 символа для русского текста
        estimated_tokens = int(total_chars / 3.5)
        
        return estimated_tokens
    
    def get_available_departments(self) -> List[str]:
        """Retrieve a list of all available departments."""
        return list(self.org_mapper._department_index.keys()) if self.org_mapper._department_index else []
    
    def get_positions_for_department(self, department: str) -> List[str]:
        # В реальной реализации это будет извлекаться из структуры
        """def get_positions_for_department(self, department: str) -> List[str]:
        Retrieve a list of positions for a specific department.  This function returns
        a list of typical positions associated with a  given department. It starts with
        a predefined set of common positions  and then appends specialized roles based
        on the department's focus,  such as IT, sales, or finance. The final list is
        returned in a sorted  and unique format.
        
        Args:
            department (str): The name of the department for which to retrieve"""
        common_positions = [
            "Руководитель департамента",
            "Заместитель руководителя",
            "Ведущий специалист", 
            "Старший специалист",
            "Специалист",
            "Младший специалист",
            "Аналитик",
            "Менеджер",
            "Координатор"
        ]
        
        # Добавляем специализированные должности в зависимости от департамента
        if "ит" in department.lower() or "информац" in department.lower():
            common_positions.extend([
                "Архитектор решений",
                "Системный архитектор",
                "Разработчик",
                "DevOps инженер",
                "Системный администратор",
                "Аналитик данных"
            ])
        elif "коммерч" in department.lower() or "продаж" in department.lower():
            common_positions.extend([
                "Менеджер по продажам",
                "Коммерческий директор",
                "Менеджер по работе с клиентами"
            ])
        elif "финанс" in department.lower():
            common_positions.extend([
                "Финансовый аналитик",
                "Контролер",
                "Казначей"
            ])
        
        return sorted(list(set(common_positions)))
    
    def clear_cache(self):
        """Clear the cache."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def validate_data_sources(self) -> Dict[str, bool]:
        """Check the availability of all data sources."""
        validation = {
            "company_map": self.paths["company_map"].exists(),
            "profile_examples": self.paths["profile_examples"].exists(), 
            "json_schema": self.paths["json_schema"].exists(),
            "it_systems_dir": self.paths["it_systems_dir"].exists(),
            "org_structure": (self.base_path / "org_structure" / "structure.json").exists(),
            "kpi_dir": (self.base_path / "KPI" / "md_converted").exists()
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
            employee_name="Иванов Иван Иванович"
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
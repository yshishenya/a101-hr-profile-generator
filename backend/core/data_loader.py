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
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
        # Инициализация маппинговых компонентов
        self.org_mapper = OrganizationMapper("data/structure.json")
        self.kpi_mapper = KPIMapper("data/KPI")
        
        # Кеш для статических данных
        self._cache = {}
        
        # Пути к статическим файлам
        self.paths = {
            "company_map": self.base_path / "data" / "anonymized_digitization_map.md",
            "profile_examples": self.base_path / "templates" / "profile_examples.xlsx",
            "json_schema": self.base_path / "templates" / "job_profile_schema.json",
            "it_systems_dir": self.base_path / "data" / "it_systems"
        }
    
    def prepare_langfuse_variables(self, department: str, position: str, employee_name: Optional[str] = None) -> Dict[str, Any]:
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
        """Загрузка карты компании А101 с кешированием"""
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
        """Загрузка примеров профилей архитекторов с кешированием"""
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
        """Загрузка JSON схемы профиля с кешированием"""
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
            
            # Убеждаемся, что данные загружены
            if not self.org_mapper._department_index:
                self.org_mapper._load_org_structure()
            
            # Загружаем всю структуру за один проход
            full_structure = {
                "departments": {},
                "metadata": {
                    "total_departments": 0,
                    "total_positions": 0,
                    "loaded_at": start_time.isoformat()
                }
            }
            
            # Получаем все департаменты
            all_departments = list(self.org_mapper._department_index.keys()) if self.org_mapper._department_index else []
            
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
                            "category": self._determine_position_category(pos_name)
                        }
                        for pos_name in positions
                    ],
                    "positions_count": len(positions)
                }
                
                full_structure["departments"][dept_name] = dept_info
                full_structure["metadata"]["total_positions"] += len(positions)
            
            full_structure["metadata"]["total_departments"] = len(all_departments)
            
            # Кеширование результата
            self._cache[cache_key] = full_structure
            
            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Full organization structure loaded in {load_time:.3f}s: "
                       f"{full_structure['metadata']['total_departments']} departments, "
                       f"{full_structure['metadata']['total_positions']} positions")
        
        return self._cache[cache_key]
    
    def get_available_departments(self) -> List[str]:
        """Получение списка всех доступных департаментов"""
        # Используем оптимизированный метод
        full_structure = self.load_full_organization_structure()
        return list(full_structure["departments"].keys())
    
    def _get_positions_for_department_internal(self, department: str) -> List[str]:
        """Внутренний метод для получения позиций департамента без дополнительной обработки"""
        try:
            # Генерируем типичные должности для департамента на основе его названия
            base_positions = [
                "Руководитель департамента",
                "Заместитель руководителя", 
                "Ведущий специалист",
                "Старший специалист",
                "Специалист",
                "Аналитик",
                "Менеджер"
            ]
            
            # Добавляем специализированные должности в зависимости от департамента
            dept_lower = department.lower()
            specialized_positions = []
            
            if any(keyword in dept_lower for keyword in ['ит', 'информац', 'цифр', 'разработ']):
                specialized_positions.extend([
                    "Системный архитектор", 
                    "Архитектор решений",
                    "Разработчик",
                    "DevOps инженер",
                    "Системный администратор"
                ])
            elif any(keyword in dept_lower for keyword in ['коммерч', 'продаж', 'реализац']):
                specialized_positions.extend([
                    "Менеджер по продажам",
                    "Коммерческий директор",
                    "Менеджер по работе с клиентами",
                    "Специалист по продажам"
                ])
            elif any(keyword in dept_lower for keyword in ['финанс', 'бухгалт', 'экономич']):
                specialized_positions.extend([
                    "Финансовый аналитик",
                    "Контролер", 
                    "Экономист",
                    "Бухгалтер"
                ])
            elif any(keyword in dept_lower for keyword in ['безопасн', 'охран']):
                specialized_positions.extend([
                    "Специалист по безопасности",
                    "Инженер по охране труда"
                ])
            
            # Объединяем базовые и специализированные должности
            all_positions = base_positions + specialized_positions
            return sorted(list(set(all_positions)))
            
        except Exception as e:
            logger.error(f"Error getting positions for {department}: {e}")
            return ["Специалист", "Менеджер", "Аналитик"]  # Fallback
    
    def _determine_position_level(self, position_name: str) -> str:
        """Определение уровня должности по названию"""
        position_lower = position_name.lower()
        
        if any(keyword in position_lower for keyword in ['руководитель', 'директор', 'управляющий', 'начальник']):
            return "senior"
        elif any(keyword in position_lower for keyword in ['ведущий', 'главный', 'старший']):
            return "lead"  
        elif any(keyword in position_lower for keyword in ['специалист', 'аналитик', 'консультант']):
            return "middle"
        elif any(keyword in position_lower for keyword in ['младший', 'помощник', 'стажер']):
            return "junior"
        else:
            return "middle"  # По умолчанию
    
    def _determine_position_category(self, position_name: str) -> str:
        """Определение категории должности"""
        position_lower = position_name.lower()
        
        if any(keyword in position_lower for keyword in ['руководитель', 'директор', 'управляющий', 'начальник']):
            return "management"
        elif any(keyword in position_lower for keyword in ['архитектор', 'разработчик', 'программист', 'техник']):
            return "technical"
        elif any(keyword in position_lower for keyword in ['аналитик', 'исследователь']):
            return "analytical"
        elif any(keyword in position_lower for keyword in ['продаж', 'менеджер', 'коммерческий']):
            return "sales"
        elif any(keyword in position_lower for keyword in ['бухгалтер', 'финансовый', 'экономист']):
            return "financial"
        elif any(keyword in position_lower for keyword in ['hr', 'кадр', 'персонал']):
            return "hr"
        else:
            return "operational"  # По умолчанию

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
                positions = [pos["name"] for pos in full_structure["departments"][department]["positions"]]
                return positions
            else:
                logger.warning(f"Department '{department}' not found in organization structure")
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
            "profile_examples": self.paths["profile_examples"].exists(), 
            "json_schema": self.paths["json_schema"].exists(),
            "it_systems_dir": self.paths["it_systems_dir"].exists(),
            "org_structure": (self.base_path / "data" / "structure.json").exists(),
            "kpi_file": (self.base_path / "data" / "KPI" / "KPI_DIT.md").exists()
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
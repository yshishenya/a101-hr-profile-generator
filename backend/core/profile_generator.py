"""
Главный генератор профилей должностей А101.

Оркестрирует все компоненты системы:
- DataLoader для подготовки данных
- LLMClient для генерации через Gemini 2.5 Flash
- Валидация и пост-обработка результатов
- Интеграция с Langfuse для мониторинга
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .data_loader import DataLoader
from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """
    Главный класс для генерации профилей должностей А101.
    
    Интегрирует все компоненты системы и обеспечивает единый интерфейс
    для генерации профилей с полным мониторингом через Langfuse.
    """
    
    def __init__(self, 
                 openrouter_api_key: str,
                 langfuse_public_key: Optional[str] = None,
                 langfuse_secret_key: Optional[str] = None,
                 base_data_path: str = "/home/yan/A101/HR"):
        """
        Инициализация генератора профилей
        
        Args:
            openrouter_api_key: API ключ для OpenRouter
            langfuse_public_key: Публичный ключ Langfuse (опционально)
            langfuse_secret_key: Секретный ключ Langfuse (опционально)
            base_data_path: Базовый путь к данным А101
        """
        self.base_data_path = Path(base_data_path)
        
        # Инициализируем компоненты
        self.data_loader = DataLoader(str(self.base_data_path))
        self.llm_client = LLMClient(
            api_key=openrouter_api_key,
            model="google/gemini-2.0-flash-exp:free"
        )
        
        # Langfuse интеграция (опционально)
        self.langfuse_enabled = bool(langfuse_public_key and langfuse_secret_key)
        if self.langfuse_enabled:
            try:
                from langfuse import Langfuse
                self.langfuse = Langfuse(
                    public_key=langfuse_public_key,
                    secret_key=langfuse_secret_key
                )
                logger.info("Langfuse integration enabled")
            except ImportError:
                logger.warning("Langfuse not installed, monitoring disabled")
                self.langfuse_enabled = False
        
        # Загружаем промпт шаблон
        self.prompt_template = self._load_prompt_template()
        
        logger.info("ProfileGenerator initialized successfully")
    
    async def generate_profile(self, 
                             department: str, 
                             position: str,
                             employee_name: Optional[str] = None,
                             temperature: float = 0.1,
                             save_result: bool = True) -> Dict[str, Any]:
        """
        Генерация профиля должности
        
        Args:
            department: Название департамента
            position: Название должности  
            employee_name: ФИО сотрудника (опционально)
            temperature: Температура генерации LLM
            save_result: Сохранять ли результат в файл
            
        Returns:
            Полный результат генерации с метаданными
        """
        generation_start = datetime.now()
        
        # Создаем trace в Langfuse если доступен
        trace = None
        if self.langfuse_enabled:
            trace = self.langfuse.trace(
                name="profile_generation",
                input={
                    "department": department,
                    "position": position,
                    "employee_name": employee_name
                }
            )
        
        try:
            logger.info(f"Starting profile generation: {department} - {position}")
            
            # 1. Подготовка данных через DataLoader
            logger.info("📊 Preparing data with deterministic logic...")
            variables = self.data_loader.prepare_langfuse_variables(
                department=department,
                position=position,
                employee_name=employee_name
            )
            
            # 2. Генерация через LLM
            logger.info("🤖 Generating profile through LLM...")
            llm_result = await self.llm_client.generate_profile(
                prompt=self.prompt_template,
                variables=variables,
                temperature=temperature
            )
            
            # 3. Валидация результата
            logger.info("✅ Validating generated profile...")
            validation_result = self._validate_and_enhance_profile(llm_result)
            
            # 4. Подготовка финального результата
            final_result = {
                "success": validation_result["success"],
                "profile": validation_result["profile"],
                "metadata": {
                    "generation": {
                        "department": department,
                        "position": position,
                        "employee_name": employee_name,
                        "timestamp": generation_start.isoformat(),
                        "duration": (datetime.now() - generation_start).total_seconds(),
                        "temperature": temperature
                    },
                    "llm": llm_result["metadata"],
                    "validation": validation_result["validation"],
                    "data_sources": variables.get("estimated_input_tokens", 0)
                },
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", [])
            }
            
            # 5. Сохранение результата
            if save_result and final_result["success"]:
                saved_path = self._save_result(final_result, department, position)
                final_result["metadata"]["saved_path"] = str(saved_path)
                logger.info(f"💾 Result saved to: {saved_path}")
            
            # 6. Отправка в Langfuse
            if trace:
                trace.update(
                    output=final_result,
                    metadata=final_result["metadata"]
                )
            
            duration = final_result["metadata"]["generation"]["duration"]
            success_emoji = "✅" if final_result["success"] else "❌"
            
            logger.info(f"{success_emoji} Profile generation completed in {duration:.2f}s")
            
            return final_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "profile": None,
                "metadata": {
                    "generation": {
                        "department": department,
                        "position": position,
                        "employee_name": employee_name,
                        "timestamp": generation_start.isoformat(),
                        "duration": (datetime.now() - generation_start).total_seconds(),
                        "error": str(e)
                    }
                },
                "errors": [f"Generation failed: {str(e)}"],
                "warnings": []
            }
            
            if trace:
                trace.update(
                    output=error_result,
                    level="ERROR"
                )
            
            logger.error(f"❌ Profile generation failed: {e}")
            return error_result
    
    def _load_prompt_template(self) -> str:
        """Загрузка шаблона промпта"""
        # В реальной реализации это будет загружаться из Langfuse или файла
        # Пока используем упрощенную версию из стратегии промптинга
        
        return """Ты опытный HR-эксперт компании А101 — одного из крупнейших девелоперов России, входящего в ПФГ "САФМАР" и перечень системообразующих предприятий экономики России.

# КОНТЕКСТ КОМПАНИИ А101

{{company_map}}

# ОРГАНИЗАЦИОННАЯ СТРУКТУРА

Организационная структура компании (релевантная часть):
```json
{{org_structure}}
```

Создаваемая должность находится в иерархии: **{{department_path}}**

# ЦЕЛЕВАЯ ДОЛЖНОСТЬ

**Департамент:** {{department}}
**Должность:** {{position}}
**ФИО:** {{employee_name}}
**Дата генерации:** {{generation_timestamp}}

# KPI И ПОКАЗАТЕЛИ ДЕПАРТАМЕНТА

{{kpi_data}}

# IT СИСТЕМЫ И ТЕХНОЛОГИЧЕСКИЙ СТЕК ДЕПАРТАМЕНТА

{{it_systems}}

---

# 🎯 ЗАДАЧА

Создай **детальный профиль должности "{{position}}"** в департаменте "{{department}}" компании А101.

## КРИТЕРИИ КАЧЕСТВА:

### 1. **СООТВЕТСТВИЕ РЕАЛЬНОСТИ А101**
- Используй ТОЛЬКО данные компании А101 из предоставленного контекста
- Ссылайся на конкретные бизнес-процессы, IT системы и OKR компании
- Применяй корпоративную терминологию А101

### 2. **ГЛУБИНА И ДЕТАЛИЗАЦИЯ**
- Каждая область ответственности должна содержать 3-7 конкретных задач
- Профессиональные навыки с четким указанием целевого уровня
- Избегай общих фраз, используй специфичные формулировки

### 3. **КОНТЕКСТНОСТЬ И ЛОГИЧНОСТЬ**
- Учитывай место должности в организационной иерархии
- Используй релевантные KPI департамента
- Указывай конкретные IT системы, с которыми работает должность
- Обеспечь логичные карьерные пути (донорские и целевые позиции)

### 4. **СТРУКТУРНАЯ ТОЧНОСТЬ**
- Строго следуй предоставленной JSON схеме
- Заполни ВСЕ обязательные поля
- Используй ТОЛЬКО допустимые значения из enum полей

## ОБЯЗАТЕЛЬНЫЕ ЭЛЕМЕНТЫ ПРОФИЛЯ:

- **Области ответственности**: Минимум 3-5 областей с детальными задачами
- **Профессиональные навыки**: Сгруппированы по категориям с целевыми уровнями
- **Корпоративные компетенции**: Выбери 3-5 наиболее релевантных из списка А101
- **Личностные качества**: 5-8 качеств, критичных для успеха в роли
- **Образование и опыт**: Реалистичные требования для позиции
- **Карьерные пути**: Логичные донорские и целевые позиции внутри А101
- **Технические требования**: Конкретные IT системы и инструменты

---

# 📋 СХЕМА ВЫХОДНОГО JSON

{{json_schema}}

---

**Предоставь результат ТОЛЬКО в формате JSON, строго соответствующий схеме выше.**"""
    
    def _validate_and_enhance_profile(self, llm_result: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация и улучшение сгенерированного профиля"""
        
        if not llm_result["metadata"]["success"]:
            return {
                "success": False,
                "profile": None,
                "validation": {"is_valid": False, "errors": ["LLM generation failed"]},
                "errors": [llm_result["metadata"].get("error", "Unknown LLM error")]
            }
        
        profile = llm_result["profile"]
        
        if not profile or "error" in profile:
            return {
                "success": False,
                "profile": profile,
                "validation": {"is_valid": False, "errors": ["Invalid profile structure"]},
                "errors": ["Failed to parse valid profile from LLM response"]
            }
        
        # Валидация через LLM клиент
        validation = self.llm_client.validate_profile_structure(profile)
        
        # Дополнительная обработка и улучшения
        enhanced_profile = self._enhance_profile_data(profile)
        
        return {
            "success": validation["is_valid"] and validation["completeness_score"] > 0.7,
            "profile": enhanced_profile,
            "validation": validation,
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", [])
        }
    
    def _enhance_profile_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Дополнительная обработка и улучшение данных профиля"""
        enhanced = profile.copy()
        
        # Добавляем метаданные генерации
        if "metadata" not in enhanced:
            enhanced["metadata"] = {}
        
        enhanced["metadata"].update({
            "generated_by": "A101 HR Profile Generator v1.0",
            "generation_method": "LLM + Deterministic Logic",
            "data_version": "v1.0",
            "last_updated": datetime.now().isoformat()
        })
        
        # Нормализация данных
        if "basic_info" in enhanced and isinstance(enhanced["basic_info"], dict):
            basic_info = enhanced["basic_info"]
            
            # Убеждаемся, что есть все основные поля
            if "employment_type" not in basic_info:
                basic_info["employment_type"] = "Полная занятость"
            
            if "salary_range" not in basic_info and "salary_from" in basic_info:
                salary_from = basic_info.get("salary_from", 0)
                salary_to = basic_info.get("salary_to", salary_from * 1.3)
                basic_info["salary_range"] = f"{salary_from:,.0f} - {salary_to:,.0f} руб."
        
        return enhanced
    
    def _save_result(self, result: Dict[str, Any], department: str, position: str) -> Path:
        """Сохранение результата генерации в файл"""
        
        # Создаем папку для результатов если не существует
        results_dir = self.base_data_path / "generated_profiles"
        results_dir.mkdir(exist_ok=True)
        
        # Создаем подпапку по департаментам
        dept_dir = results_dir / self._sanitize_filename(department)
        dept_dir.mkdir(exist_ok=True)
        
        # Формируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._sanitize_filename(position)}_{timestamp}.json"
        
        file_path = dept_dir / filename
        
        # Сохраняем результат
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def _sanitize_filename(self, name: str) -> str:
        """Санитизация имени файла"""
        # Заменяем проблемные символы
        sanitized = name.replace(" ", "_")
        sanitized = sanitized.replace("/", "_")
        sanitized = sanitized.replace("\\", "_")
        sanitized = sanitized.replace(":", "_")
        sanitized = sanitized.replace("*", "_")
        sanitized = sanitized.replace("?", "_")
        sanitized = sanitized.replace("<", "_")
        sanitized = sanitized.replace(">", "_")
        sanitized = sanitized.replace("|", "_")
        
        return sanitized
    
    def get_available_departments(self) -> List[str]:
        """Получение списка доступных департаментов"""
        return self.data_loader.get_available_departments()
    
    def get_positions_for_department(self, department: str) -> List[str]:
        """Получение списка должностей для департамента"""
        return self.data_loader.get_positions_for_department(department)
    
    async def validate_system(self) -> Dict[str, Any]:
        """Полная валидация системы"""
        validation_result = {
            "system_ready": True,
            "components": {},
            "warnings": [],
            "errors": []
        }
        
        # 1. Проверка источников данных
        data_sources = self.data_loader.validate_data_sources()
        validation_result["components"]["data_sources"] = data_sources
        
        missing_sources = [name for name, status in data_sources.items() if not status]
        if missing_sources:
            validation_result["errors"].extend([f"Missing data source: {source}" for source in missing_sources])
            validation_result["system_ready"] = False
        
        # 2. Проверка LLM подключения
        try:
            llm_test = await self.llm_client.test_connection()
            validation_result["components"]["llm_connection"] = llm_test
            
            if not llm_test["success"]:
                validation_result["errors"].append(f"LLM connection failed: {llm_test['error']}")
                validation_result["system_ready"] = False
        except Exception as e:
            validation_result["components"]["llm_connection"] = {"success": False, "error": str(e)}
            validation_result["errors"].append(f"LLM connection test failed: {e}")
            validation_result["system_ready"] = False
        
        # 3. Проверка Langfuse
        validation_result["components"]["langfuse"] = {"enabled": self.langfuse_enabled}
        if not self.langfuse_enabled:
            validation_result["warnings"].append("Langfuse monitoring not configured")
        
        return validation_result


if __name__ == "__main__":
    # Тестирование ProfileGenerator
    import os
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def test_profile_generator():
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            print("❌ OPENROUTER_API_KEY not set")
            return
        
        generator = ProfileGenerator(openrouter_api_key=api_key)
        
        print("=== Валидация системы ===")
        validation = await generator.validate_system()
        
        print(f"Система готова: {'✅' if validation['system_ready'] else '❌'}")
        
        for component, status in validation["components"].items():
            if isinstance(status, dict) and "success" in status:
                emoji = "✅" if status["success"] else "❌"
                print(f"  {component}: {emoji}")
            else:
                print(f"  {component}: {status}")
        
        if validation["errors"]:
            print("Ошибки:")
            for error in validation["errors"]:
                print(f"  ❌ {error}")
        
        if validation["warnings"]:
            print("Предупреждения:")
            for warning in validation["warnings"]:
                print(f"  ⚠️ {warning}")
        
        if validation["system_ready"]:
            print("\n=== Тест генерации профиля ===")
            result = await generator.generate_profile(
                department="ДИТ",
                position="Системный архитектор",
                employee_name="Тестов Тест Тестович"
            )
            
            if result["success"]:
                print("✅ Профиль сгенерирован успешно")
                print(f"⏱️ Время генерации: {result['metadata']['generation']['duration']:.2f}s")
                print(f"📊 Полнота профиля: {result['metadata']['validation']['completeness_score']:.2%}")
            else:
                print("❌ Ошибка генерации профиля")
                for error in result["errors"]:
                    print(f"  {error}")
    
    # asyncio.run(test_profile_generator())
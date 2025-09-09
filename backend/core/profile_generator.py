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
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from .data_loader import DataLoader
from .llm_client import LLMClient
from .prompt_manager import PromptManager
from .config import config
from ..services.profile_markdown_generator import ProfileMarkdownGenerator
from ..services.profile_storage_service import ProfileStorageService

# from langfuse.decorators import observe  # Временно убрали из-за проблем с версией

logger = logging.getLogger(__name__)


class ProfileGenerator:
    """
    Главный класс для генерации профилей должностей А101.

    Интегрирует все компоненты системы и обеспечивает единый интерфейс
    для генерации профилей с полным мониторингом через Langfuse.
    """

    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        langfuse_public_key: Optional[str] = None,
        langfuse_secret_key: Optional[str] = None,
        base_data_path: Optional[str] = None,
    ):
        """
        Инициализация генератора профилей.
        Использует config для получения настроек из .env

        Args:
            openrouter_api_key: API ключ для OpenRouter (или из config)
            langfuse_public_key: Публичный ключ Langfuse (или из config)
            langfuse_secret_key: Секретный ключ Langfuse (или из config)
            base_data_path: Базовый путь к данным А101 (или из config)
        """
        # Получаем настройки из config если не переданы
        self.base_data_path = Path(base_data_path or config.BASE_DATA_PATH)

        # Инициализируем компоненты
        self.data_loader = DataLoader(str(self.base_data_path))
        self.md_generator = ProfileMarkdownGenerator()
        self.storage_service = ProfileStorageService(str(self.base_data_path / "generated_profiles"))

        # Инициализируем LLMClient (он сам получит настройки из config)
        try:
            self.llm_client = LLMClient(
                openrouter_api_key=openrouter_api_key,
                langfuse_public_key=langfuse_public_key,
                langfuse_secret_key=langfuse_secret_key,
            )
            self.langfuse_enabled = bool(self.llm_client.langfuse)
            logger.info("✅ LLMClient initialized from config")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLMClient: {e}")
            self.llm_client = None
            self.langfuse_enabled = False

        logger.info("✅ ProfileGenerator initialized successfully")

    # @observe(name="generate_profile", capture_input=True, capture_output=True)  # Временно убрали
    async def generate_profile(
        self,
        department: str,
        position: str,
        employee_name: Optional[str] = None,
        temperature: float = 0.1,
        save_result: bool = True,
        profile_id: Optional[str] = None,
    ) -> Dict[str, Any]:
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

        # LLMClient теперь сам создает traces в Langfuse

        try:
            logger.info(f"Starting profile generation: {department} - {position}")

            # 1. Подготовка данных через DataLoader
            logger.info("📊 Preparing data with deterministic logic...")
            variables = self.data_loader.prepare_langfuse_variables(
                department=department, position=position, employee_name=employee_name
            )

            # 2. Данные готовы, переходим к генерации через LLM
            logger.info("🤖 Generating profile through Langfuse LLM client...")

            # 3. Генерация через LLMClient с полной Langfuse интеграцией
            if not self.llm_client:
                raise ValueError(
                    "LLMClient not initialized - Langfuse credentials required"
                )

            llm_result = self.llm_client.generate_profile_from_langfuse(
                prompt_name="a101-hr-profile-gemini-v3-simple",
                variables=variables,
                user_id=employee_name or f"user_{department}_{position}",
                session_id=f"session_{generation_start.timestamp()}",
            )

            # 4. Валидация результата
            logger.info("✅ Validating generated profile...")
            validation_result = self._validate_and_enhance_profile(llm_result)

            # 5. Подготовка финального результата
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
                        "temperature": temperature,
                    },
                    "llm": llm_result["metadata"],
                    "validation": validation_result["validation"],
                    "data_sources": variables.get("estimated_input_tokens", 0),
                },
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
            }

            # 6. Сохранение результата
            if save_result and final_result["success"]:
                saved_path = self._save_result(final_result, department, position, profile_id)
                final_result["metadata"]["saved_path"] = str(saved_path)
                logger.info(f"💾 Result saved to: {saved_path}")

            # 7. Трейсинг уже выполнен в LLMClient

            duration = final_result["metadata"]["generation"]["duration"]
            success_emoji = "✅" if final_result["success"] else "❌"

            logger.info(
                f"{success_emoji} Profile generation completed in {duration:.2f}s"
            )

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
                        "error": str(e),
                    }
                },
                "errors": [f"Generation failed: {str(e)}"],
                "warnings": [],
            }

            # trace handling removed as it's not available in this context

            logger.error(f"❌ Profile generation failed: {e}")
            return error_result

    def _validate_and_enhance_profile(
        self, llm_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Валидация и улучшение сгенерированного профиля"""

        if not llm_result["metadata"]["success"]:
            return {
                "success": False,
                "profile": None,
                "validation": {"is_valid": False, "errors": ["LLM generation failed"]},
                "errors": [llm_result["metadata"].get("error", "Unknown LLM error")],
            }

        profile = llm_result["profile"]

        if not profile or "error" in profile:
            return {
                "success": False,
                "profile": profile,
                "validation": {
                    "is_valid": False,
                    "errors": ["Invalid profile structure"],
                },
                "errors": ["Failed to parse valid profile from LLM response"],
            }

        # Валидация через LLM клиент
        validation = self.llm_client.validate_profile_structure(profile)

        # Дополнительная обработка и улучшения
        enhanced_profile = self._enhance_profile_data(profile)

        return {
            "success": validation["completeness_score"] >= 0.7,
            "profile": enhanced_profile,
            "validation": validation,
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", []),
        }

    def _enhance_profile_data(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Дополнительная обработка и улучшение данных профиля"""
        enhanced = profile.copy()

        # Добавляем метаданные генерации
        if "metadata" not in enhanced:
            enhanced["metadata"] = {}

        enhanced["metadata"].update(
            {
                "generated_by": "A101 HR Profile Generator v1.0",
                "generation_method": "LLM + Deterministic Logic",
                "data_version": "v1.0",
                "last_updated": datetime.now().isoformat(),
            }
        )

        # Нормализация данных
        if "basic_info" in enhanced and isinstance(enhanced["basic_info"], dict):
            basic_info = enhanced["basic_info"]

            # Убеждаемся, что есть все основные поля
            if "employment_type" not in basic_info:
                basic_info["employment_type"] = "Полная занятость"

            if "salary_range" not in basic_info and "salary_from" in basic_info:
                salary_from = basic_info.get("salary_from", 0)
                salary_to = basic_info.get("salary_to", salary_from * 1.3)
                basic_info["salary_range"] = (
                    f"{salary_from:,.0f} - {salary_to:,.0f} руб."
                )

        return enhanced

    def _save_result(
        self, result: Dict[str, Any], department: str, position: str, profile_id: str
    ) -> Path:
        """
        Сохранение результата генерации в новую иерархическую структуру файлов.
        
        Создает полную структуру: Блок/Департамент/Отдел/Группа/Должность/Экземпляр/
        """
        generation_timestamp = datetime.now()
        
        try:
            logger.info(f"💾 Creating hierarchical directory structure for: {department} -> {position}")
            
            # 1. Создаем иерархическую структуру папок
            profile_dir = self.storage_service.create_profile_directory(
                department=department,
                position=position,
                timestamp=generation_timestamp,
                profile_id=profile_id
            )
            
            # 2. Генерируем MD файл
            logger.info("📝 Auto-generating Markdown profile...")
            md_content = self.md_generator.generate_from_json(result)
            
            # 3. Сохраняем JSON и MD файлы в одну папку
            json_path, md_path = self.storage_service.save_profile_files(
                directory=profile_dir,
                json_content=result,
                md_content=md_content,
                profile_id=profile_id
            )
            
            logger.info(f"✅ Profile saved to hierarchical structure:")
            logger.info(f"  📁 Directory: {profile_dir}")
            logger.info(f"  📄 JSON: {json_path.name}")
            logger.info(f"  📝 MD: {md_path.name}")
            
            return json_path  # Возвращаем путь к JSON файлу для обратной совместимости
            
        except Exception as e:
            logger.error(f"❌ Error saving profile to hierarchical structure: {e}")
            
            # Fallback к старой системе в случае ошибки
            logger.warning("⚠️ Falling back to legacy file structure...")
            return self._save_result_legacy(result, department, position)
    
    def _save_result_legacy(
        self, result: Dict[str, Any], department: str, position: str
    ) -> Path:
        """Fallback к старой системе сохранения файлов"""
        
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
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Legacy save completed: {file_path}")
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

    def get_prompt_analytics(
        self, prompt_name: str = "profile_generation"
    ) -> Dict[str, Any]:
        """
        @doc Получение аналитики по использованию промпта

        Examples:
            python>
            generator = ProfileGenerator(api_key)
            analytics = generator.get_prompt_analytics()
            print(f"Cache status: {analytics['cache_status']}")
        """
        return self.prompt_manager.get_prompt_analytics(prompt_name)

    def validate_prompt_template(
        self, template: str, prompt_name: str = "profile_generation"
    ) -> Dict[str, Any]:
        """
        @doc Валидация шаблона промпта

        Examples:
            python>
            generator = ProfileGenerator(api_key)
            validation = generator.validate_prompt_template(new_template)
            if validation["valid"]:
                print("Template is valid!")
        """
        return self.prompt_manager.validate_prompt_template(template, prompt_name)

    async def validate_system(self) -> Dict[str, Any]:
        """Полная валидация системы"""
        validation_result = {
            "system_ready": True,
            "components": {},
            "warnings": [],
            "errors": [],
        }

        # 1. Проверка источников данных
        data_sources = self.data_loader.validate_data_sources()
        validation_result["components"]["data_sources"] = data_sources

        missing_sources = [name for name, status in data_sources.items() if not status]
        if missing_sources:
            validation_result["errors"].extend(
                [f"Missing data source: {source}" for source in missing_sources]
            )
            validation_result["system_ready"] = False

        # 2. Проверка LLM подключения
        if self.llm_client:
            try:
                llm_test = self.llm_client.test_connection()
                validation_result["components"]["llm_connection"] = llm_test

                if not llm_test["success"]:
                    validation_result["errors"].append(
                        f"LLM connection failed: {llm_test['error']}"
                    )
                    validation_result["system_ready"] = False
            except Exception as e:
                validation_result["components"]["llm_connection"] = {
                    "success": False,
                    "error": str(e),
                }
                validation_result["errors"].append(f"LLM connection test failed: {e}")
                validation_result["system_ready"] = False
        else:
            validation_result["errors"].append(
                "LLM client not initialized - requires Langfuse credentials"
            )
            validation_result["system_ready"] = False

        # 3. Проверка Langfuse
        validation_result["components"]["langfuse"] = {"enabled": self.langfuse_enabled}
        if not self.langfuse_enabled:
            validation_result["warnings"].append("Langfuse monitoring not configured")

        # 4. Проверка Langfuse Prompt Management
        if self.langfuse_enabled and self.llm_client:
            try:
                # Тестируем получение промпта из Langfuse
                validation_result["components"]["langfuse_prompts"] = {
                    "success": True,
                    "message": "Prompts managed via Langfuse",
                }
            except Exception as e:
                validation_result["components"]["langfuse_prompts"] = {
                    "success": False,
                    "error": str(e),
                }
                validation_result["errors"].append(f"Langfuse prompt test failed: {e}")
                validation_result["system_ready"] = False
        else:
            validation_result["warnings"].append(
                "Langfuse prompt management not available"
            )

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
                employee_name="Тестов Тест Тестович",
            )

            if result["success"]:
                print("✅ Профиль сгенерирован успешно")
                print(
                    f"⏱️ Время генерации: {result['metadata']['generation']['duration']:.2f}s"
                )
                print(
                    f"📊 Полнота профиля: {result['metadata']['validation']['completeness_score']:.2%}"
                )
            else:
                print("❌ Ошибка генерации профиля")
                for error in result["errors"]:
                    print(f"  {error}")

    # asyncio.run(test_profile_generator())

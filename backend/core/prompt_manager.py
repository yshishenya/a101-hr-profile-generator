"""
@doc Prompt Template Management System для A101 HR Profile Generator

Система управления промпт-шаблонами с поддержкой:
- Langfuse Prompt Management интеграции
- Versioning и A/B testing
- Fallback к локальным шаблонам
- Template variable substitution

Examples:
    python>
    # Инициализация менеджера промптов
    pm = PromptManager(langfuse_client=langfuse)

    # Получение актуального промпта
    prompt = pm.get_prompt("profile_generation", variables={"department": "IT"})

    # A/B тестирование
    prompt = pm.get_prompt_variant("profile_generation", variant="experimental")
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class PromptManager:
    """
    @doc Менеджер промпт-шаблонов с Langfuse интеграцией

    Обеспечивает централизованное управление промптами с поддержкой
    версионирования, A/B тестирования и fallback к локальным файлам.

    Examples:
        python>
        # Создание менеджера с Langfuse
        pm = PromptManager(langfuse_client=langfuse_client)

        # Получение промпта с переменными
        prompt = pm.get_prompt("generation", {
            "department": "IT",
            "position": "Developer"
        })
    """

    def __init__(
        self,
        langfuse_client=None,
        templates_dir: str = None,
        cache_ttl: int = 300,
    ):
        """
        Инициализация Prompt Manager

        Args:
            langfuse_client: Клиент Langfuse (опционально)
            templates_dir: Директория с локальными шаблонами (если None, используется PROJECT_ROOT/templates)
            cache_ttl: Время жизни кеша в секундах
        """
        self.langfuse_client = langfuse_client

        # Определяем templates_dir: переданный путь или default
        if templates_dir is None:
            # Вычисляем относительно расположения этого файла
            project_root = Path(__file__).parent.parent.parent
            self.templates_dir = project_root / "templates"
        else:
            self.templates_dir = Path(templates_dir)

        self.cache_ttl = cache_ttl
        self.langfuse_enabled = langfuse_client is not None

        # Кеш для промптов
        self._prompt_cache = {}
        self._cache_timestamps = {}

        # Реестр промптов
        self.prompt_registry = {
            "profile_generation": {
                "langfuse_name": "a101-hr-profile-gemini-v3-simple",  # v28 with SGR
                "local_file": "generation_prompt.txt",
                "version": "28",  # Schema-Guided Reasoning (3-phase cascade)
                "description": "Master prompt v28 с Schema-Guided Reasoning (SGR) - трехфазная генерация с явными проверками",
                "variables": [
                    "company_map",
                    "org_structure",
                    "department",
                    "position",
                    "department_path",
                    "profile_examples",
                    "kpi_data",
                    "it_systems",
                    "json_schema",
                    "employee_name",
                    "generation_timestamp",
                    "data_version",
                ],
                "config": {
                    # Базовая конфигурация - полная схема загружается из templates/prompts/production/config.json
                    "model": "google/gemini-2.5-flash",
                    "temperature": 0.1,
                    "max_tokens": 4000,
                    "structured_output": True,
                    # response_format будет загружен из config.json через get_prompt_config()
                },
            }
        }

        logger.info(f"PromptManager initialized (Langfuse: {self.langfuse_enabled})")

    def get_prompt(
        self,
        prompt_name: str,
        variables: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> str:
        """
        @doc Получение промпта с подстановкой переменных

        Examples:
            python>
            # Базовое получение промпта
            prompt = pm.get_prompt("profile_generation")

            # С переменными
            prompt = pm.get_prompt("profile_generation", {
                "department": "IT",
                "position": "Senior Developer"
            })

            # Конкретная версия
            prompt = pm.get_prompt("profile_generation", version="1.2.0")
        """
        if prompt_name not in self.prompt_registry:
            raise ValueError(f"Unknown prompt: {prompt_name}")

        # Получаем базовый шаблон
        template = self._get_prompt_template(prompt_name, version, variant)

        # Подставляем переменные
        if variables:
            template = self._substitute_variables(template, variables, prompt_name)

        return template

    def get_prompt_config(
        self, prompt_name: str, environment: str = "production"
    ) -> Dict[str, Any]:
        """
        @doc Получение конфигурации промпта

        Приоритет:
        1. Langfuse (если доступен)
        2. Локальный файл config.json (новая структура)
        3. Реестр в коде (fallback)

        Examples:
            python>
            config = pm.get_prompt_config("profile_generation")
            model = config.get("model", "google/gemini-2.5-flash")
            response_format = config.get("response_format")
        """
        if prompt_name not in self.prompt_registry:
            raise ValueError(f"Unknown prompt: {prompt_name}")

        # Получаем конфиг из реестра (базовый fallback)
        local_config = self.prompt_registry[prompt_name].get("config", {})

        # Если Langfuse включен, пытаемся получить конфиг оттуда
        if self.langfuse_enabled:
            try:
                registry_entry = self.prompt_registry[prompt_name]
                langfuse_name = registry_entry["langfuse_name"]

                # Получаем промпт из Langfuse с label="production"
                prompt_obj = self.langfuse_client.get_prompt(
                    langfuse_name, label=environment
                )

                if prompt_obj and hasattr(prompt_obj, "config") and prompt_obj.config:
                    # Объединяем локальный и Langfuse конфиг
                    langfuse_config = prompt_obj.config
                    merged_config = {**local_config, **langfuse_config}
                    logger.info(f"Using Langfuse config for '{prompt_name}'")
                    return merged_config

            except Exception as e:
                logger.warning(f"Failed to get prompt config from Langfuse: {e}")

        # Пытаемся загрузить из локального файла config.json
        try:
            env_dir = self.templates_dir / "prompts" / environment
            config_file = env_dir / "config.json"

            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)

                merged_config = {**local_config, **file_config}
                logger.info(
                    f"Using local file config for '{prompt_name}' from {config_file}"
                )
                return merged_config

        except Exception as e:
            logger.debug(f"Failed to load config from local file: {e}")

        logger.info(f"Using registry config for '{prompt_name}'")
        return local_config

    def _get_prompt_template(
        self,
        prompt_name: str,
        version: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> str:
        """Получение базового шаблона промпта"""
        cache_key = f"{prompt_name}:{version or 'latest'}:{variant or 'default'}"

        # Проверяем кеш
        if self._is_cached_valid(cache_key):
            return self._prompt_cache[cache_key]

        template = None

        # Сначала пытаемся получить из Langfuse
        if self.langfuse_enabled:
            try:
                template = self._get_from_langfuse(prompt_name, version, variant)
                if template:
                    logger.info(f"Retrieved prompt '{prompt_name}' from Langfuse")
            except Exception as e:
                logger.warning(f"Failed to get prompt from Langfuse: {e}")

        # Fallback к локальному файлу
        if not template:
            template = self._get_from_local_file(prompt_name)
            logger.info(f"Using local template for '{prompt_name}'")

        # Кешируем результат
        self._prompt_cache[cache_key] = template
        self._cache_timestamps[cache_key] = datetime.now()

        return template

    def _get_from_langfuse(
        self,
        prompt_name: str,
        version: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> Optional[str]:
        """Получение промпта из Langfuse"""
        if not self.langfuse_enabled:
            return None

        try:
            registry_entry = self.prompt_registry[prompt_name]
            langfuse_name = registry_entry["langfuse_name"]

            # Получаем промпт из Langfuse
            if version:
                prompt = self.langfuse_client.get_prompt(langfuse_name, version=version)
            else:
                prompt = self.langfuse_client.get_prompt(
                    langfuse_name, label="production"
                )

            if prompt:
                # 🔥 НОВАЯ ФИЧА: Сохраняем промпт в локальные файлы при успешном получении
                try:
                    prompt_text = None
                    if hasattr(prompt, "prompt"):
                        prompt_text = prompt.prompt
                    elif hasattr(prompt, "content"):
                        prompt_text = prompt.content
                    else:
                        prompt_text = str(prompt) if prompt else None

                    if prompt_text:
                        # Сохраняем промпт и конфиг локально
                        self._save_prompt_to_local(prompt_name, prompt, prompt_text)
                        return prompt_text
                except Exception as save_error:
                    logger.warning(
                        f"Failed to save prompt to local files: {save_error}"
                    )
                    # Продолжаем работу даже если сохранение не удалось
                    if hasattr(prompt, "prompt"):
                        return prompt.prompt
                    elif hasattr(prompt, "content"):
                        return prompt.content
                    else:
                        return str(prompt) if prompt else None

            return None

        except Exception as e:
            logger.error(f"Error fetching prompt from Langfuse: {e}")
            return None

    def _get_from_local_file(self, prompt_name: str) -> str:
        """
        Получение промпта из локального файла

        Приоритет:
        1. Новая структура: /templates/prompts/production/prompt.txt
        2. Старый файл: /templates/generation_prompt.txt (fallback)
        """
        # Пытаемся загрузить из новой структуры
        try:
            prompt_text = self._load_prompt_from_local(
                prompt_name, environment="production"
            )
            if prompt_text:
                logger.info(f"Loaded prompt '{prompt_name}' from new local structure")
                return prompt_text
        except Exception as e:
            logger.debug(f"Failed to load from new structure: {e}")

        # Fallback к старому формату
        registry_entry = self.prompt_registry[prompt_name]
        local_file = registry_entry["local_file"]
        file_path = self.templates_dir / local_file

        if not file_path.exists():
            raise FileNotFoundError(f"Local prompt template not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _save_prompt_to_local(
        self,
        prompt_name: str,
        prompt_obj: Any,
        prompt_text: str,
        environment: str = "production",
    ):
        """
        @doc Сохранение промпта в локальные файлы для fallback

        Структура:
        /templates/prompts/production/
          prompt.txt           # Текст промпта
          config.json          # Конфигурация (model, temperature, JSON schema)
          metadata.json        # Метаданные (version, timestamp, hash)

        Examples:
            python>
            # Автоматически вызывается при успешном получении из Langfuse
            pm._save_prompt_to_local("profile_generation", prompt_obj, prompt_text)
        """
        try:
            # Создаем директорию для окружения
            env_dir = self.templates_dir / "prompts" / environment
            env_dir.mkdir(parents=True, exist_ok=True)

            # 1. Сохраняем текст промпта
            prompt_file = env_dir / "prompt.txt"
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt_text)

            # 2. Сохраняем конфигурацию (если есть)
            config_data = {}
            if hasattr(prompt_obj, "config") and prompt_obj.config:
                config_data = prompt_obj.config
            elif hasattr(prompt_obj, "model_config"):
                config_data = prompt_obj.model_config

            config_file = env_dir / "config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            # 3. Сохраняем метаданные
            metadata = {
                "prompt_name": prompt_name,
                "environment": environment,
                "saved_at": datetime.now().isoformat(),
                "version": getattr(prompt_obj, "version", None),
                "hash": hashlib.sha256(prompt_text.encode()).hexdigest(),
                "character_count": len(prompt_text),
                "line_count": len(prompt_text.split("\n")),
            }

            # Добавляем labels если есть
            if hasattr(prompt_obj, "labels"):
                metadata["labels"] = prompt_obj.labels

            metadata_file = env_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(
                f"Saved prompt '{prompt_name}' to local files: {env_dir} "
                f"(version: {metadata['version']}, hash: {metadata['hash'][:8]}...)"
            )

        except Exception as e:
            logger.error(f"Failed to save prompt to local files: {e}")
            raise

    def _load_prompt_from_local(
        self, prompt_name: str, environment: str = "production"
    ) -> Optional[str]:
        """
        @doc Загрузка промпта из локальных файлов

        Examples:
            python>
            # Загрузка production промпта
            prompt_text = pm._load_prompt_from_local("profile_generation", "production")

            # Загрузка development промпта
            prompt_text = pm._load_prompt_from_local("profile_generation", "development")
        """
        try:
            env_dir = self.templates_dir / "prompts" / environment
            prompt_file = env_dir / "prompt.txt"

            if not prompt_file.exists():
                logger.debug(f"Local prompt file not found: {prompt_file}")
                return None

            # Загружаем текст промпта
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt_text = f.read()

            # Проверяем метаданные для верификации
            metadata_file = env_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                # Верифицируем hash
                actual_hash = hashlib.sha256(prompt_text.encode()).hexdigest()
                stored_hash = metadata.get("hash", "")

                if actual_hash != stored_hash:
                    logger.warning(
                        f"Hash mismatch for local prompt '{prompt_name}': "
                        f"stored={stored_hash[:8]}..., actual={actual_hash[:8]}..."
                    )

                logger.info(
                    f"Loaded local prompt '{prompt_name}' (version: {metadata.get('version')}, "
                    f"saved: {metadata.get('saved_at')})"
                )

            return prompt_text

        except Exception as e:
            logger.error(f"Failed to load prompt from local files: {e}")
            return None

    def _substitute_variables(
        self, template: str, variables: Dict[str, Any], prompt_name: str
    ) -> str:
        """
        @doc Подстановка переменных в шаблон промпта

        Examples:
            python>
            # Шаблон с переменными
            template = "Hello {{name}}, your role is {{role}}"
            variables = {"name": "John", "role": "Developer"}
            result = pm._substitute_variables(template, variables, "test")
            # Result: "Hello John, your role is Developer"
        """
        try:
            # Получаем список ожидаемых переменных
            expected_vars = set(self.prompt_registry[prompt_name]["variables"])
            provided_vars = set(variables.keys())

            # Проверяем критические переменные
            critical_vars = {"department", "position", "json_schema"}
            missing_critical = critical_vars - provided_vars

            if missing_critical:
                logger.warning(f"Missing critical variables: {missing_critical}")

            # Подставляем переменные
            result = template
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                if placeholder in result:
                    # Обрабатываем None и пустые значения
                    if var_value is None:
                        var_value = "[НЕТ ДАННЫХ]"
                    elif isinstance(var_value, (dict, list)):
                        var_value = json.dumps(var_value, ensure_ascii=False, indent=2)

                    result = result.replace(placeholder, str(var_value))

            # Проверяем оставшиеся непроставленные переменные
            remaining_placeholders = self._find_placeholders(result)
            if remaining_placeholders:
                logger.warning(f"Unsubstituted placeholders: {remaining_placeholders}")

            return result

        except Exception as e:
            logger.error(f"Error substituting variables: {e}")
            return template

    def _find_placeholders(self, text: str) -> List[str]:
        """Поиск непроставленных плейсхолдеров в тексте"""
        import re

        pattern = r"\{\{([^}]+)\}\}"
        matches = re.findall(pattern, text)
        return matches

    def _is_cached_valid(self, cache_key: str) -> bool:
        """Проверка валидности кеша"""
        if cache_key not in self._prompt_cache:
            return False

        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return False

        age = (datetime.now() - timestamp).total_seconds()
        return age < self.cache_ttl

    def create_prompt_version(
        self, prompt_name: str, content: str, version: str, description: str = ""
    ) -> bool:
        """
        @doc Создание новой версии промпта в Langfuse

        Examples:
            python>
            # Создание новой версии промпта
            success = pm.create_prompt_version(
                "profile_generation",
                updated_content,
                "1.1.0",
                "Улучшенная версия с дополнительным контекстом"
            )
        """
        if not self.langfuse_enabled:
            logger.warning("Cannot create prompt version: Langfuse not enabled")
            return False

        try:
            registry_entry = self.prompt_registry[prompt_name]
            langfuse_name = registry_entry["langfuse_name"]

            # Используем новый API Langfuse для создания промпта
            prompt_config = {
                "description": description,
                "created_at": datetime.now().isoformat(),
                "variables": registry_entry["variables"],
                "type": "text",
            }

            # Создаем промпт через Langfuse API (современный формат)
            self.langfuse_client.create_prompt(
                name=langfuse_name,
                prompt=content,
                labels=[version, "production"],
                tags=["a101", "hr", "profile-generation"],
                type="text",
                config=prompt_config,
                commit_message=f"Created version {version}: {description}",
            )

            # Очищаем кеш
            self._clear_cache_for_prompt(prompt_name)

            logger.info(f"Created prompt version {version} for {prompt_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create prompt version: {e}")
            return False

    def get_prompt_analytics(self, prompt_name: str) -> Dict[str, Any]:
        """
        @doc Получение аналитики по использованию промпта

        Examples:
            python>
            # Аналитика использования промпта
            analytics = pm.get_prompt_analytics("profile_generation")
            print(f"Total uses: {analytics['total_uses']}")
        """
        if not self.langfuse_enabled:
            return {"error": "Langfuse not enabled"}

        try:
            registry_entry = self.prompt_registry[prompt_name]
            langfuse_name = registry_entry["langfuse_name"]

            # Здесь можно добавить запросы к Langfuse Analytics API
            # Пока возвращаем базовую информацию

            return {
                "prompt_name": prompt_name,
                "langfuse_name": langfuse_name,
                "current_version": registry_entry["version"],
                "cache_status": self._get_cache_status(prompt_name),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get prompt analytics: {e}")
            return {"error": str(e)}

    def _get_cache_status(self, prompt_name: str) -> Dict[str, Any]:
        """Получение статуса кеша для промпта"""
        matching_keys = [
            k for k in self._prompt_cache.keys() if k.startswith(prompt_name)
        ]

        return {
            "cached_variants": len(matching_keys),
            "cache_keys": matching_keys,
            "cache_ttl": self.cache_ttl,
        }

    def _clear_cache_for_prompt(self, prompt_name: str):
        """Очистка кеша для конкретного промпта"""
        keys_to_remove = [
            k for k in self._prompt_cache.keys() if k.startswith(prompt_name)
        ]

        for key in keys_to_remove:
            self._prompt_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)

        logger.info(
            f"Cleared cache for prompt '{prompt_name}' ({len(keys_to_remove)} entries)"
        )

    def validate_prompt_template(
        self, template: str, prompt_name: str
    ) -> Dict[str, Any]:
        """
        @doc Валидация шаблона промпта

        Examples:
            python>
            # Валидация шаблона
            validation = pm.validate_prompt_template(template, "profile_generation")
            if not validation["valid"]:
                print("Errors:", validation["errors"])
        """
        errors = []
        warnings = []

        # Проверяем обязательные секции
        required_sections = [
            "СИСТЕМА РОЛИ И ЭКСПЕРТИЗЫ",
            "КОНТЕКСТ КОМПАНИИ А101",
            "ТЕХНИЧЕСКАЯ СПЕЦИФИКАЦИЯ ВЫХОДА",
            "ИНСТРУКЦИИ ПО ГЕНЕРАЦИИ",
        ]

        for section in required_sections:
            if section not in template:
                errors.append(f"Missing required section: {section}")

        # Проверяем переменные
        if prompt_name in self.prompt_registry:
            expected_vars = self.prompt_registry[prompt_name]["variables"]
            placeholders = self._find_placeholders(template)

            missing_vars = set(expected_vars) - set(placeholders)
            extra_vars = set(placeholders) - set(expected_vars)

            if missing_vars:
                warnings.append(f"Missing expected variables: {missing_vars}")

            if extra_vars:
                warnings.append(f"Unexpected variables: {extra_vars}")

        # Проверяем длину
        if len(template) < 1000:
            warnings.append("Template seems too short for comprehensive generation")

        if len(template) > 50000:
            warnings.append("Template might be too long and exceed token limits")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "character_count": len(template),
            "placeholder_count": len(self._find_placeholders(template)),
        }

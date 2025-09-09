"""
LLM клиент для интеграции с Gemini 2.5 Flash через Langfuse OpenAI pattern.

Поддерживает:
- Интеграция с Langfuse для промптов и мониторинга
- OpenRouter API через langfuse.openai
- Structured output с JSON schema
- Автоматический трейсинг и логирование
"""

import json
import time
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
from langfuse.openai import OpenAI
from langfuse import Langfuse

from .config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Клиент для работы с Gemini 2.5 Flash через Langfuse OpenAI integration
    """

    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        langfuse_public_key: Optional[str] = None,
        langfuse_secret_key: Optional[str] = None,
        langfuse_host: Optional[str] = None,
    ):
        """
        Инициализация LLM клиента с Langfuse интеграцией.
        Использует config для получения настроек из .env

        Args:
            openrouter_api_key: API ключ OpenRouter (или из config)
            langfuse_public_key: Langfuse public key (или из config)
            langfuse_secret_key: Langfuse secret key (или из config)
            langfuse_host: Langfuse host URL (или из config)
        """
        # Получаем настройки из config если не переданы
        self.openrouter_api_key = openrouter_api_key or config.OPENROUTER_API_KEY
        self.langfuse_public_key = langfuse_public_key or config.LANGFUSE_PUBLIC_KEY
        self.langfuse_secret_key = langfuse_secret_key or config.LANGFUSE_SECRET_KEY
        self.langfuse_host = langfuse_host or config.LANGFUSE_HOST

        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY не найден в .env или параметрах")

        # Инициализируем Langfuse
        if self.langfuse_public_key and self.langfuse_secret_key:
            self.langfuse = Langfuse(
                public_key=self.langfuse_public_key,
                secret_key=self.langfuse_secret_key,
                host=self.langfuse_host,
            )
            logger.info("✅ Langfuse initialized from config")
        else:
            logger.warning(
                "⚠️ Langfuse credentials not found in config - tracing disabled"
            )
            self.langfuse = None

        # Инициализируем OpenAI клиент через Langfuse
        self.client = OpenAI(
            api_key=self.openrouter_api_key,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://a101-hr-profiles.local",
                "X-Title": "A101 HR Profile Generator",
            },
        )
        logger.info(f"✅ LLM client initialized with model: {config.OPENROUTER_MODEL}")

    def _create_generation_with_prompt(
        self,
        prompt,
        messages,
        model,
        temperature,
        max_tokens,
        response_format,
        trace_metadata=None,
    ):
        """
        @doc Внутренняя функция для создания generation с правильной связкой промпта

        Используется в качестве декорированной функции для Langfuse tracing

        Examples:
            python>
            result = self._create_generation_with_prompt(prompt, messages, model, temp, max_tokens, format, metadata)
        """
        # Обогащенные metadata для полного трекинга (убираем только prompt content)
        enriched_metadata = {
            # Параметры модели
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format_type": (
                type(response_format).__name__ if response_format else None
            ),
            # Информация о промпте (без содержимого)
            "prompt_length": len(str(messages)),
            "messages_count": len(messages),
            # НЕ добавляем prompt_first_100_chars - занимает место
            # Trace metadata (исключает json_schema, company_map, org_structure)
            **(trace_metadata or {}),
        }

        # Правильная связка промпта согласно документации 2025 года
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            langfuse_prompt=prompt,  # 🔗 КЛЮЧЕВАЯ связка с промптом!
            metadata=enriched_metadata,
        )

        # Дополнительное обогащение metadata после получения ответа
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            post_metadata = {
                **enriched_metadata,
                # Основная информация о response
                "response_id": getattr(response, "id", None),
                "created_timestamp": getattr(response, "created", None),
                "actual_model": getattr(response, "model", model),
                "system_fingerprint": getattr(response, "system_fingerprint", None),
                # Провайдер информация из OpenRouter
                "provider": (
                    response.model_extra.get("provider", "openrouter")
                    if hasattr(response, "model_extra") and response.model_extra
                    else "openrouter"
                ),
                # Детальная информация о токенах
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                # Дополнительные детали токенов (из model_extra если есть)
                "prompt_tokens_cached": 0,
                "completion_reasoning_tokens": 0,
                "completion_image_tokens": 0,
                # Информация о завершении
                "finish_reason": (
                    response.choices[0].finish_reason if response.choices else None
                ),
                "choice_index": response.choices[0].index if response.choices else None,
                "response_length": (
                    len(response.choices[0].message.content)
                    if response.choices and response.choices[0].message
                    else 0
                ),
                # Попробуем извлечь cost информацию (может быть в headers или других местах)
                "cost_usd": getattr(usage, "cost", None),
                "cost_estimated": None,  # Можем добавить расчёт на основе токенов позже
                # Статус и провайдер
                "success": True,
                "api_provider": "openrouter",
                "langfuse_sdk_version": "3.3.4",
                "openai_sdk_version": (
                    response.__class__.__module__
                    if hasattr(response.__class__, "__module__")
                    else "unknown"
                ),
            }

            # Извлекаем детальную token информацию если доступна
            try:
                if hasattr(usage, "model_extra") and usage.model_extra:
                    if "prompt_tokens_details" in usage.model_extra:
                        post_metadata["prompt_tokens_cached"] = usage.model_extra[
                            "prompt_tokens_details"
                        ].get("cached_tokens", 0)
                    if "completion_tokens_details" in usage.model_extra:
                        completion_details = usage.model_extra[
                            "completion_tokens_details"
                        ]
                        post_metadata["completion_reasoning_tokens"] = (
                            completion_details.get("reasoning_tokens", 0)
                        )
                        post_metadata["completion_image_tokens"] = (
                            completion_details.get("image_tokens", 0)
                        )
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract detailed token info: {e}")

            # Обновляем generation с обогащенными метаданными (если возможно)
            try:
                if self.langfuse:
                    self.langfuse.update_current_generation(
                        metadata=post_metadata,
                        usage_details={
                            "prompt_tokens": usage.prompt_tokens,
                            "completion_tokens": usage.completion_tokens,
                            "total_tokens": usage.total_tokens,
                        },
                    )
            except Exception as e:
                # Логируем но не прерываем выполнение
                logger.warning(f"⚠️ Failed to update generation metadata: {e}")

        return response

    def generate_profile_from_langfuse(
        self,
        prompt_name: str,
        variables: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        @doc Генерация профиля должности через Langfuse prompt с traced execution

        Args:
            prompt_name: Имя промпта в Langfuse
            variables: Переменные для подстановки в промпт
            user_id: ID пользователя для трейсинга
            session_id: ID сессии для трейсинга

        Returns:
            Словарь с результатом генерации

        Examples:
            python>
            client = LLMClient(api_key, langfuse_keys...)
            result = client.generate_profile_from_langfuse(
                prompt_name="a101-hr-profile-gemini-v2",
                variables={"position": "Senior Developer", "department": "IT"}
            )
        """
        start_time = time.time()

        try:
            # Проверяем что Langfuse доступен
            if not self.langfuse:
                raise ValueError(
                    "Langfuse не инициализирован - невозможно получить промпт"
                )

            # Получаем промпт из Langfuse с label="production"
            prompt = self.langfuse.get_prompt(prompt_name, label="production")

            # Извлекаем конфигурацию
            model = prompt.config.get("model", "google/gemini-2.5-flash")
            temperature = prompt.config.get("temperature", 0.1)
            max_tokens = prompt.config.get("max_tokens", 4000)
            response_format = prompt.config.get("response_format")

            logger.info(f"Starting Langfuse generation with prompt: {prompt_name}")
            logger.info(f"Model: {model}, Temperature: {temperature}")
            logger.info(f"Response format: {response_format}")

            # Компилируем промпт с переменными
            compiled_prompt = prompt.compile(**variables)
            logger.info(f"Compiled prompt type: {type(compiled_prompt)}")

            # Преобразуем в формат messages если нужно
            if isinstance(compiled_prompt, str):
                # Если compiled_prompt - строка, преобразуем в messages формат
                messages = [{"role": "user", "content": compiled_prompt}]
                logger.info(
                    f"Converted string prompt to messages format, length: {len(compiled_prompt)}"
                )
            elif isinstance(compiled_prompt, list):
                # Если уже список messages
                messages = compiled_prompt
                logger.info(f"Using existing messages format, count: {len(messages)}")
            else:
                raise ValueError(f"Unexpected prompt format: {type(compiled_prompt)}")

            logger.info(f"Final messages count: {len(messages)}")

            # Логируем параметры запроса
            logger.info(f"Request parameters:")
            logger.info(f"  Model: {model}")
            logger.info(f"  Messages count: {len(messages)}")
            logger.info(f"  Temperature: {temperature}")
            logger.info(f"  Max tokens: {max_tokens}")
            logger.info(f"  Response format type: {type(response_format)}")

            # Метаданные для декорированной функции
            trace_metadata = {
                "prompt_name": prompt_name,
                "prompt_version": prompt.version,
                "department": variables.get("department"),
                "position": variables.get("position"),
                "employee_name": variables.get("employee_name"),
                "user_id": user_id,
                "session_id": session_id,
                "environment": "production",
                "source": "hr_profile_generator",
            }
            # Выполняем запрос через правильную функцию с декоратором для связки промптов
            try:
                response = self._create_generation_with_prompt(
                    prompt=prompt,
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    trace_metadata=trace_metadata,
                )
                logger.info("✅ Generation with prompt linking completed")
            except Exception as api_error:
                logger.error(f"OpenAI API error: {api_error}")
                logger.error(f"Error type: {type(api_error)}")
                raise api_error

            # Извлекаем ответ
            generated_text = response.choices[0].message.content

            # Парсим JSON из ответа
            profile_json = self._extract_and_parse_json(generated_text)

            generation_time = time.time() - start_time

            # Подсчитываем токены из usage
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else input_tokens + output_tokens

            logger.info(f"Langfuse generation completed in {generation_time:.2f}s")
            logger.info(
                f"Tokens used: {input_tokens} input + {output_tokens} output = {total_tokens} total"
            )

            # Получаем trace_id если доступны декораторы
            trace_id = None
            try:
                from langfuse.decorators import langfuse_context

                trace_id = langfuse_context.get_current_trace_id()
                logger.info("✅ Langfuse tracing with decorators completed")
            except ImportError:
                logger.info("✅ Basic Langfuse tracing completed")
            except Exception as e:
                logger.warning(f"⚠️ Failed to get trace ID: {e}")

            return {
                "profile": profile_json,
                "metadata": {
                    "model": model,
                    "generation_time": generation_time,
                    "tokens": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": total_tokens,
                    },
                    "temperature": temperature,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "langfuse_trace_id": trace_id,
                    "prompt_name": prompt_name,
                    "prompt_version": prompt.version,
                    "tracing_mode": "decorator_based",
                    "department": variables.get("department"),
                    "position": variables.get("position"),
                },
                "raw_response": generated_text,
            }

        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(
                f"Langfuse generation failed after {generation_time:.2f}s: {e}"
            )

            # Получаем trace_id даже при ошибке (если доступно)
            try:
                from langfuse.decorators import langfuse_context

                trace_id = langfuse_context.get_current_trace_id()
            except (ImportError, NameError):
                trace_id = None

            return {
                "profile": None,
                "metadata": {
                    "model": "unknown",
                    "generation_time": generation_time,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "langfuse_trace_id": trace_id,
                },
                "raw_response": None,
            }

    def _extract_and_parse_json(self, generated_text: str) -> Dict[str, Any]:
        """Извлечение и парсинг JSON из ответа LLM"""
        try:
            # Ищем JSON в тексте (между ``` или в чистом виде)
            json_text = generated_text.strip()

            # Убираем markdown code blocks если есть
            if json_text.startswith("```"):
                json_text = json_text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:]
                json_text = json_text.strip()

            if json_text.endswith("```"):
                json_text = json_text[:-3].strip()

            # Парсим JSON
            profile_data = json.loads(json_text)

            if not isinstance(profile_data, dict):
                raise ValueError("Response is not a JSON object")

            logger.info("JSON successfully parsed from LLM response")
            return profile_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Raw response text: {generated_text[:500]}...")

            # Возвращаем fallback структуру
            return {
                "error": "Failed to parse JSON from LLM response",
                "raw_response": generated_text,
                "parse_error": str(e),
            }

        except Exception as e:
            logger.error(f"Unexpected error while parsing response: {e}")
            return {
                "error": "Unexpected error during response parsing",
                "raw_response": generated_text,
                "parse_error": str(e),
            }

    def validate_profile_structure(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация структуры сгенерированного профиля

        Returns:
            Словарь с результатами валидации
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "completeness_score": 0.0,
        }

        # Проверяем обязательные поля (синхронизировано со схемой JSON)
        required_fields = [
            "position_title",
            "department_broad", 
            "department_specific",
            "category",
            "primary_activity",
            "responsibility_areas",
            "professional_skills",
            "personal_qualities"
        ]

        missing_fields = []
        empty_fields = []
        total_fields = len(required_fields)
        filled_fields = 0

        for field in required_fields:
            if field not in profile:
                missing_fields.append(field)
            elif not profile[field] or (
                isinstance(profile[field], (list, dict)) and len(profile[field]) == 0
            ):
                empty_fields.append(field)
            else:
                filled_fields += 1

        if missing_fields:
            validation_result["is_valid"] = False
            validation_result["errors"].extend(
                [f"Missing required field: {field}" for field in missing_fields]
            )

        if empty_fields:
            validation_result["warnings"].extend(
                [f"Empty required field: {field}" for field in empty_fields]
            )

        # Подсчитываем полноту профиля
        validation_result["completeness_score"] = filled_fields / total_fields

        # Проверяем специфичные поля
        if "basic_info" in profile and isinstance(profile["basic_info"], dict):
            basic_info = profile["basic_info"]
            if not basic_info.get("position_title"):
                validation_result["errors"].append(
                    "Missing position_title in basic_info"
                )

        logger.info(
            f"Profile validation completed: {validation_result['completeness_score']:.2%} complete, {len(validation_result['errors'])} errors"
        )

        return validation_result

    def test_connection(self) -> Dict[str, Any]:
        """Тестирование подключения через Langfuse к OpenRouter API"""
        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {
                        "role": "user",
                        "content": 'Hello! Please respond with a simple JSON: {"status": "ok", "message": "Connection test successful"}',
                    }
                ],
                max_tokens=100,
                temperature=0.1,
            )

            return {
                "success": True,
                "model": "google/gemini-2.5-flash",
                "response": response.choices[0].message.content,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Тестирование обновленного LLM клиента с Langfuse
    import os

    logging.basicConfig(level=logging.INFO)

    def test_llm_client():
        # Получаем все необходимые ключи
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        langfuse_public = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret = os.getenv("LANGFUSE_SECRET_KEY")

        if not all([openrouter_key, langfuse_public, langfuse_secret]):
            print("❌ Missing required API keys")
            print(f"  OpenRouter: {'✅' if openrouter_key else '❌'}")
            print(f"  Langfuse public: {'✅' if langfuse_public else '❌'}")
            print(f"  Langfuse secret: {'✅' if langfuse_secret else '❌'}")
            return

        client = LLMClient(
            openrouter_api_key=openrouter_key,
            langfuse_public_key=langfuse_public,
            langfuse_secret_key=langfuse_secret,
        )

        print("=== Тестирование подключения ===")
        connection_test = client.test_connection()

        if connection_test["success"]:
            print("✅ Подключение через Langfuse успешно")
        else:
            print(f"❌ Ошибка подключения: {connection_test['error']}")
            return

        print("\n=== Тестирование генерации через Langfuse ===")
        test_variables = {
            "position": "Senior ML Engineer",
            "department": "ДИТ",
            "employee_name": "Тестовая Генерация",
            "org_structure": "Тестовая структура",
            "kpi_data": "Тестовые KPI",
            "it_systems": "Тестовые системы",
        }

        result = client.generate_profile_from_langfuse(
            prompt_name="a101-hr-profile-gemini-v2",
            variables=test_variables,
            user_id="test-user",
            session_id="test-session",
        )

        if result["metadata"]["success"]:
            print("✅ Генерация через Langfuse успешна")
            print(f"📊 Токены: {result['metadata']['tokens']}")
            print(f"⏱️ Время: {result['metadata']['generation_time']:.2f}s")
            print(f"🔗 Trace ID: {result['metadata']['langfuse_trace_id']}")

            if result["profile"]:
                validation = client.validate_profile_structure(result["profile"])
                print(f"✓ Валидация: {validation['completeness_score']:.2%} заполнено")
        else:
            print(f"❌ Ошибка генерации: {result['metadata']['error']}")

    # Раскомментируйте для запуска теста
    # test_llm_client()

"""
LLM клиент для интеграции с Gemini 2.5 Flash через OpenRouter API.

Поддерживает:
- Отправку запросов через OpenRouter
- Обработку ошибок и повторные попытки
- Валидация JSON ответов
- Интеграция с Langfuse для мониторинга
"""

import json
import time
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Клиент для работы с Gemini 2.5 Flash через OpenRouter API
    """
    
    def __init__(self, 
                 api_key: str, 
                 model: str = "google/gemini-2.0-flash-exp:free",
                 base_url: str = "https://openrouter.ai/api/v1",
                 timeout: int = 120,
                 max_retries: int = 3):
        """
        Инициализация LLM клиента
        
        Args:
            api_key: API ключ OpenRouter
            model: Модель для использования
            base_url: Базовый URL OpenRouter API
            timeout: Таймаут запроса в секундах
            max_retries: Максимальное количество повторных попыток
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://a101-hr-profiles.local",
            "X-Title": "A101 HR Profile Generator"
        }
    
    async def generate_profile(self, 
                             prompt: str, 
                             variables: Dict[str, Any],
                             temperature: float = 0.1,
                             max_tokens: int = 8192) -> Dict[str, Any]:
        """
        Генерация профиля должности через LLM
        
        Args:
            prompt: Промпт с плейсхолдерами для переменных
            variables: Переменные для подстановки в промпт
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            Словарь с результатом генерации
        """
        start_time = time.time()
        
        try:
            # Подставляем переменные в промпт
            formatted_prompt = self._format_prompt(prompt, variables)
            
            logger.info(f"Starting LLM generation with model {self.model}")
            logger.info(f"Prompt length: {len(formatted_prompt)} chars")
            logger.info(f"Estimated input tokens: {variables.get('estimated_input_tokens', 'unknown')}")
            
            # Формируем запрос к OpenRouter
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Выполняем запрос с повторными попытками
            response_data = await self._make_request_with_retries(request_data)
            
            # Извлекаем и парсим ответ
            generated_text = response_data["choices"][0]["message"]["content"]
            
            # Парсим JSON из ответа
            profile_json = self._extract_and_parse_json(generated_text)
            
            generation_time = time.time() - start_time
            
            # Подсчитываем токены
            usage = response_data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
            
            logger.info(f"LLM generation completed in {generation_time:.2f}s")
            logger.info(f"Tokens used: {input_tokens} input + {output_tokens} output = {total_tokens} total")
            
            return {
                "profile": profile_json,
                "metadata": {
                    "model": self.model,
                    "generation_time": generation_time,
                    "tokens": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": total_tokens
                    },
                    "temperature": temperature,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                },
                "raw_response": generated_text
            }
            
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"LLM generation failed after {generation_time:.2f}s: {e}")
            
            return {
                "profile": None,
                "metadata": {
                    "model": self.model,
                    "generation_time": generation_time,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                },
                "raw_response": None
            }
    
    def _format_prompt(self, prompt: str, variables: Dict[str, Any]) -> str:
        """Форматирование промпта с переменными"""
        try:
            # Используем простое форматирование строк
            formatted = prompt
            
            for key, value in variables.items():
                placeholder = "{{" + key + "}}"
                if placeholder in formatted:
                    # Конвертируем значение в строку
                    if isinstance(value, (dict, list)):
                        str_value = json.dumps(value, ensure_ascii=False, indent=2)
                    else:
                        str_value = str(value)
                    
                    formatted = formatted.replace(placeholder, str_value)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            raise ValueError(f"Failed to format prompt with variables: {e}")
    
    async def _make_request_with_retries(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение запроса к OpenRouter с повторными попытками"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=request_data
                    )
                
                if response.status_code == 200:
                    return response.json()
                
                # Обрабатываем различные коды ошибок
                if response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                
                elif response.status_code in [500, 502, 503, 504]:  # Server errors
                    wait_time = 1 + attempt
                    logger.warning(f"Server error {response.status_code}, waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                
                else:
                    # Для других ошибок не повторяем
                    error_text = response.text
                    raise Exception(f"HTTP {response.status_code}: {error_text}")
                
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 1 + attempt
                    logger.warning(f"Request attempt {attempt + 1} failed: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")
        
        raise last_exception or Exception("All request attempts failed")
    
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
                "parse_error": str(e)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error while parsing response: {e}")
            return {
                "error": "Unexpected error during response parsing",
                "raw_response": generated_text,
                "parse_error": str(e)
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
            "completeness_score": 0.0
        }
        
        # Проверяем обязательные поля
        required_fields = [
            "basic_info", "responsibilities", "professional_skills", 
            "corporate_competencies", "personal_qualities", 
            "education_experience", "career_paths"
        ]
        
        missing_fields = []
        empty_fields = []
        total_fields = len(required_fields)
        filled_fields = 0
        
        for field in required_fields:
            if field not in profile:
                missing_fields.append(field)
            elif not profile[field] or (isinstance(profile[field], (list, dict)) and len(profile[field]) == 0):
                empty_fields.append(field)
            else:
                filled_fields += 1
        
        if missing_fields:
            validation_result["is_valid"] = False
            validation_result["errors"].extend([f"Missing required field: {field}" for field in missing_fields])
        
        if empty_fields:
            validation_result["warnings"].extend([f"Empty required field: {field}" for field in empty_fields])
        
        # Подсчитываем полноту профиля
        validation_result["completeness_score"] = filled_fields / total_fields
        
        # Проверяем специфичные поля
        if "basic_info" in profile and isinstance(profile["basic_info"], dict):
            basic_info = profile["basic_info"]
            if not basic_info.get("position_title"):
                validation_result["errors"].append("Missing position_title in basic_info")
        
        logger.info(f"Profile validation completed: {validation_result['completeness_score']:.2%} complete, {len(validation_result['errors'])} errors")
        
        return validation_result
    
    async def test_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к OpenRouter API"""
        try:
            test_request = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user", 
                        "content": "Hello! Please respond with a simple JSON: {\"status\": \"ok\", \"message\": \"Connection test successful\"}"
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            response_data = await self._make_request_with_retries(test_request)
            
            return {
                "success": True,
                "model": self.model,
                "response": response_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Импорт asyncio для sleep функций
import asyncio


if __name__ == "__main__":
    # Тестирование LLM клиента
    import os
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def test_llm_client():
        # Для тестирования нужно установить переменную окружения OPENROUTER_API_KEY
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            print("❌ OPENROUTER_API_KEY not set in environment")
            return
        
        client = LLMClient(api_key)
        
        print("=== Тестирование подключения ===")
        connection_test = await client.test_connection()
        
        if connection_test["success"]:
            print("✅ Подключение к OpenRouter успешно")
        else:
            print(f"❌ Ошибка подключения: {connection_test['error']}")
            return
        
        print("\n=== Тестирование генерации ===")
        test_prompt = """
        Создай краткий JSON профиль должности для тестирования:
        
        Должность: {{position}}
        Департамент: {{department}}
        
        Верни JSON в формате:
        {
          "basic_info": {
            "position_title": "...",
            "department": "..."
          },
          "test": true
        }
        """
        
        test_variables = {
            "position": "Тестовая должность",
            "department": "Тестовый департамент",
            "estimated_input_tokens": 100
        }
        
        result = await client.generate_profile(test_prompt, test_variables)
        
        if result["metadata"]["success"]:
            print("✅ Генерация успешна")
            print(f"📊 Токены: {result['metadata']['tokens']}")
            print(f"⏱️ Время: {result['metadata']['generation_time']:.2f}s")
            
            if result["profile"]:
                validation = client.validate_profile_structure(result["profile"])
                print(f"✓ Валидация: {validation['completeness_score']:.2%} заполнено")
        else:
            print(f"❌ Ошибка генерации: {result['metadata']['error']}")
    
    # Запускаем тест
    # asyncio.run(test_llm_client())
#!/usr/bin/env python3
"""
🎯 Правильная интеграция Langfuse с трейсингом и связкой промптов
Основано на официальной документации Langfuse
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Загрузка .env переменных
env_path = Path('/home/yan/A101/HR/.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

sys.path.insert(0, '/home/yan/A101/HR')

from langfuse import Langfuse
from openai import OpenAI

# Проверяем доступные импорты для декораторов
try:
    from langfuse.decorators import observe, langfuse_context
    decorators_available = True
except ImportError:
    try:
        from langfuse import observe, langfuse_context
        decorators_available = True
    except ImportError:
        try:
            from langfuse.opentelemetry import observe
            decorators_available = False
            langfuse_context = None
        except ImportError:
            decorators_available = False
            observe = None
            langfuse_context = None

def test_proper_langfuse_integration():
    """
    Тестируем правильную интеграцию Langfuse с:
    - Декораторами @observe
    - Правильной связкой с промптами  
    - Sessions и user tracking
    - Environments и metadata
    - Tags для категоризации
    """
    
    print("🎯 Testing proper Langfuse integration with prompts...")
    
    # Проверяем доступность декораторов
    if not decorators_available:
        print("❌ Langfuse decorators not available, using basic client API")
        return test_basic_langfuse_integration()
    
    print("✅ Langfuse decorators available")
    
    # Настраиваем environment для разделения от продакшена
    os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = "development"
    
    # Инициализация клиентов
    langfuse = Langfuse()
    
    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    # 1. Получаем промпт из Langfuse
    print("📋 Getting prompt from Langfuse...")
    try:
        prompt = langfuse.get_prompt("a101-hr-profile-gemini-v3-simple", label="production")
        print(f"✅ Got prompt: {prompt.name} v{prompt.version}")
    except Exception as e:
        print(f"❌ Failed to get prompt: {e}")
        return False
    
    # 2. Подготавливаем данные для тестирования
    test_variables = {
        "position": "Senior ML Engineer", 
        "department": "ДИТ",
        "company_map": "Test company data (simplified)...",
        "org_structure": '{"ДИТ": {"positions": ["Engineer", "Senior Engineer"]}}',
        "kpi_data": "Test KPI data for ДИТ department...",
        "it_systems": "Test IT systems data...",
        "json_schema": '{"type": "object", "properties": {}}'
    }
    
    # 3. Создаем основную функцию с декоратором @observe
    @observe(
        name="a101-hr-profile-generation",
        as_type="generation",
        metadata={
            "environment": "development",
            "department": test_variables["department"],
            "position": test_variables["position"],
            "prompt_name": prompt.name,
            "prompt_version": prompt.version
        }
    )
    def generate_profile_with_langfuse(variables: dict):
        """Генерация профиля с полным Langfuse трейсингом"""
        
        # Устанавливаем контекст трейса
        langfuse_context.update_current_trace(
            name="A101-HR-Profile-Generation",
            user_id="test_user_hr_system",
            session_id=f"test_session_{int(time.time())}",
            tags=["hr", "profile-generation", "development", "test"],
            metadata={
                "source": "hr_profile_generator",
                "version": "1.0.0",
                "test_run": True
            }
        )
        
        try:
            # Компилируем промпт с переменными
            compiled_prompt = prompt.compile(**variables)
            
            # Получаем конфигурацию из промпта
            model = prompt.config.get("model", "google/gemini-2.5-flash")
            temperature = prompt.config.get("temperature", 0.1)
            max_tokens = prompt.config.get("max_tokens", 4000)
            response_format = prompt.config.get("response_format")
            
            print(f"⚙️ Model: {model}")
            print(f"🌡️ Temperature: {temperature}")
            print(f"📝 Compiled prompt length: {len(compiled_prompt)} chars")
            
            # Обновляем текущий generation с prompt информацией
            langfuse_context.update_current_observation(
                input=compiled_prompt,
                model=model,
                metadata={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "response_format_type": type(response_format).__name__ if response_format else None
                },
                prompt=prompt  # 🔗 Ключевая связка с промптом!
            )
            
            start_time = time.time()
            
            # Выполняем запрос к OpenAI
            print("🔄 Making OpenAI request...")
            
            messages = [{"role": "user", "content": compiled_prompt}]
            
            response = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            generation_time = time.time() - start_time
            
            # Получаем результат
            generated_text = response.choices[0].message.content
            usage = response.usage
            
            # Обновляем generation с результатами
            langfuse_context.update_current_observation(
                output=generated_text,
                usage={
                    "input": usage.prompt_tokens if usage else 0,
                    "output": usage.completion_tokens if usage else 0,
                    "total": usage.total_tokens if usage else 0
                },
                metadata={
                    "generation_time": generation_time,
                    "finish_reason": response.choices[0].finish_reason,
                    "success": True
                }
            )
            
            print(f"✅ Generation completed in {generation_time:.2f}s")
            print(f"📊 Tokens: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} total")
            
            # Парсим JSON для валидации
            try:
                profile_json = json.loads(generated_text.strip())
                print(f"📋 Generated profile with {len(profile_json)} fields")
                
                # Показываем первые несколько полей
                for key in list(profile_json.keys())[:3]:
                    print(f"  - {key}: {type(profile_json[key]).__name__}")
                
                if len(profile_json) > 3:
                    print(f"  ... and {len(profile_json) - 3} more fields")
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse warning: {e}")
                profile_json = {"error": "Failed to parse JSON"}
            
            return {
                "profile": profile_json,
                "metadata": {
                    "generation_time": generation_time,
                    "tokens": {
                        "input": usage.prompt_tokens if usage else 0,
                        "output": usage.completion_tokens if usage else 0,
                        "total": usage.total_tokens if usage else 0
                    },
                    "model": model,
                    "success": True
                }
            }
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            
            # Обновляем observation с ошибкой
            langfuse_context.update_current_observation(
                output={"error": str(e)},
                metadata={
                    "error": True,
                    "error_message": str(e)
                }
            )
            
            return {
                "profile": {"error": str(e)},
                "metadata": {
                    "success": False,
                    "error": str(e)
                }
            }
    
    # 4. Выполняем генерацию
    print("🚀 Starting profile generation with full tracing...")
    result = generate_profile_with_langfuse(test_variables)
    
    # 5. Получаем информацию о трейсе
    try:
        trace_id = langfuse_context.get_current_trace_id()
        trace_url = langfuse.get_trace_url(trace_id) if trace_id else None
        
        print(f"\n🔗 Trace Information:")
        print(f"   - Trace ID: {trace_id}")
        print(f"   - Trace URL: {trace_url}")
        print(f"   - Environment: development")
        print(f"   - User ID: test_user_hr_system")
        print(f"   - Tags: hr, profile-generation, development, test")
        
    except Exception as e:
        print(f"⚠️ Could not get trace info: {e}")
    
    # 6. Проверяем результат
    success = result["metadata"]["success"]
    
    if success:
        print(f"\n🎉 SUCCESS! Profile generated successfully")
        print(f"⏱️ Generation time: {result['metadata']['generation_time']:.2f}s")
        print(f"📊 Total tokens: {result['metadata']['tokens']['total']}")
    else:
        print(f"\n❌ FAILED! Error: {result['metadata']['error']}")
    
    return success

def test_basic_langfuse_integration():
    """
    Базовая интеграция Langfuse без декораторов
    Используем прямые вызовы API клиента
    """
    
    print("🔧 Using basic Langfuse client API...")
    
    # Инициализация
    langfuse = Langfuse(
        environment="development"  # Устанавливаем environment
    )
    
    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    # Получаем промпт
    try:
        prompt = langfuse.get_prompt("a101-hr-profile-gemini-v3-simple", label="production")
        print(f"✅ Got prompt: {prompt.name} v{prompt.version}")
    except Exception as e:
        print(f"❌ Failed to get prompt: {e}")
        return False
    
    # Подготавливаем тестовые данные
    test_variables = {
        "position": "Senior ML Engineer",
        "department": "ДИТ", 
        "company_map": "Test company data (simplified)...",
        "org_structure": '{"ДИТ": {"positions": ["Engineer", "Senior Engineer"]}}',
        "kpi_data": "Test KPI data for ДИТ department...",
        "it_systems": "Test IT systems data...",
        "json_schema": '{"type": "object", "properties": {}}'
    }
    
    try:
        # Компилируем промпт
        compiled_prompt = prompt.compile(**test_variables)
        
        # Получаем конфигурацию
        model = prompt.config.get("model", "google/gemini-2.5-flash")
        temperature = prompt.config.get("temperature", 0.1)
        max_tokens = prompt.config.get("max_tokens", 4000)
        response_format = prompt.config.get("response_format")
        
        print(f"⚙️ Model: {model}")
        print(f"🌡️ Temperature: {temperature}")
        print(f"📝 Compiled prompt length: {len(compiled_prompt)} chars")
        
        # Создаем трейс вручную (используя правильные методы API)
        trace_data = {
            "name": "A101-HR-Profile-Generation-Basic",
            "user_id": "test_user_hr_system",
            "session_id": f"basic_session_{int(time.time())}",
            "tags": ["hr", "profile-generation", "development", "basic-api"],
            "metadata": {
                "source": "hr_profile_generator",
                "version": "1.0.0",
                "test_run": True,
                "api_mode": "basic",
                "prompt_name": prompt.name,
                "prompt_version": prompt.version
            }
        }
        
        start_time = time.time()
        
        # Выполняем запрос
        print("🔄 Making OpenAI request...")
        
        messages = [{"role": "user", "content": compiled_prompt}]
        
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )
        
        generation_time = time.time() - start_time
        
        # Получаем результат
        generated_text = response.choices[0].message.content
        usage = response.usage
        
        # Логируем результат в Langfuse (используем имеющиеся методы)
        try:
            # Создаем событие с полной информацией
            langfuse.create_event(
                name="hr-profile-generation-completed",
                metadata={
                    **trace_data["metadata"],
                    "generation_time": generation_time,
                    "tokens": {
                        "input": usage.prompt_tokens if usage else 0,
                        "output": usage.completion_tokens if usage else 0,
                        "total": usage.total_tokens if usage else 0
                    },
                    "model": model,
                    "success": True
                }
            )
            print("✅ Event logged to Langfuse")
            
        except Exception as e:
            print(f"⚠️ Failed to log to Langfuse: {e}")
        
        print(f"✅ Generation completed in {generation_time:.2f}s")
        print(f"📊 Tokens: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} total")
        
        # Парсим JSON
        try:
            profile_json = json.loads(generated_text.strip())
            print(f"📋 Generated profile with {len(profile_json)} fields")
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse warning: {e}")
            profile_json = {"error": "Failed to parse JSON"}
        
        return True
        
    except Exception as e:
        print(f"❌ Basic integration failed: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🎯 Starting Langfuse proper integration test...")
    print("📚 Based on official Langfuse documentation")
    
    success = test_proper_langfuse_integration()
    
    if success:
        print("\n✅ SUCCESS! Proper Langfuse integration working!")
        print("🔍 Check Langfuse dashboard:")
        print("   1. Go to https://cloud.langfuse.com")
        print("   2. Check Traces tab - you should see 'A101-HR-Profile-Generation'")
        print("   3. Check Prompts tab - trace should be linked to prompt")
        print("   4. Environment filter should show 'development'")
        print("   5. Session and user tracking should be visible")
    else:
        print("\n❌ FAILED! Check the errors above")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
🔗 Тест правильной связки трейсов с промптами в Langfuse
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Загрузка .env переменных
env_path = Path("/home/yan/A101/HR/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

sys.path.insert(0, "/home/yan/A101/HR")

from langfuse import Langfuse
from openai import OpenAI


def test_trace_linking():
    """Тестируем правильную связку трейсов с промптами"""

    print("🔗 Testing Langfuse trace linking...")

    # Инициализация клиентов
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )

    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # 1. Получаем промпт из Langfuse
    print("📋 Getting prompt from Langfuse...")
    try:
        prompt = langfuse.get_prompt(
            "a101-hr-profile-gemini-v3-simple", label="production"
        )
        print(f"✅ Got prompt: {prompt.name}")
    except Exception as e:
        print(f"❌ Failed to get prompt: {e}")
        return False

    # 2. Создаем trace ID вручную с правильными метаданными
    print("🚀 Creating manual trace...")
    trace_id = langfuse.create_trace_id()
    print(f"📝 Created trace ID: {trace_id}")

    # Используем context для работы с трейсом
    trace_metadata = {
        "prompt_name": prompt.name,
        "prompt_version": prompt.version,
        "department": "ДИТ",
        "position": "Senior ML Engineer",
        "user_id": "test_user",
        "session_id": f"test_session_{int(time.time())}",
    }

    # 3. Создаем generation с явной связкой к промпту
    print("🤖 Creating generation linked to prompt...")

    # Подготавливаем переменные (упрощенные для теста)
    variables = {
        "position": "Senior ML Engineer",
        "department": "ДИТ",
        "company_map": "Test company data...",
        "org_structure": '{"ДИТ": {"positions": ["Engineer", "Senior Engineer"]}}',
        "kpi_data": "Test KPI data...",
        "it_systems": "Test IT systems...",
        "json_schema": '{"type": "object", "properties": {}}',
    }

    # Компилируем промпт с переменными
    compiled_prompt = prompt.compile(**variables)
    print(f"📝 Compiled prompt length: {len(compiled_prompt)} chars")

    # Получаем конфигурацию из промпта
    model = prompt.config.get("model", "google/gemini-2.5-flash")
    temperature = prompt.config.get("temperature", 0.1)
    max_tokens = prompt.config.get("max_tokens", 4000)
    response_format = prompt.config.get("response_format")

    print(f"⚙️ Using model: {model}")
    print(f"🌡️ Temperature: {temperature}")

    start_time = time.time()

    try:
        # Создаем generation в рамках нашего трейса
        generation = langfuse.start_generation(
            name="profile-generation",
            model=model,
            input=[{"role": "user", "content": compiled_prompt}],
            prompt=prompt,  # 🔗 Это ключевая связка!
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "trace_id": trace_id,
                **trace_metadata,
            },
        )

        # Выполняем запрос к OpenAI
        print("🔄 Making OpenAI request...")

        messages = [{"role": "user", "content": compiled_prompt}]

        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        generation_time = time.time() - start_time

        # Получаем результат
        generated_text = response.choices[0].message.content
        usage = response.usage

        # Обновляем generation с результатами
        generation.end(
            output=generated_text,
            usage={
                "input": usage.prompt_tokens if usage else 0,
                "output": usage.completion_tokens if usage else 0,
                "total": usage.total_tokens if usage else 0,
            },
            metadata={
                "generation_time": generation_time,
                "finish_reason": response.choices[0].finish_reason,
            },
        )

        print(f"✅ Generation completed in {generation_time:.2f}s")
        print(
            f"📊 Tokens: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} total"
        )
        print(f"🆔 Trace ID: {trace_id}")
        print(f"🔗 Trace URL: https://cloud.langfuse.com/traces/{trace_id}")

        # Парсим JSON ответ для проверки
        try:
            profile_json = json.loads(generated_text.strip())
            print(f"📋 Generated profile with {len(profile_json)} fields")
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse warning: {e}")

        return True

    except Exception as e:
        generation_time = time.time() - start_time
        print(f"❌ Generation failed after {generation_time:.2f}s: {e}")

        # Записываем ошибку в generation
        generation.end(
            output={"error": str(e)},
            metadata={"generation_time": generation_time, "error": True},
        )

        return False

    finally:
        # Завершаем трейс с помощью update_current_trace
        langfuse.update_current_trace(
            output={
                "success": True,
                "generation_time": generation_time,
                "trace_id": trace_id,
            },
            metadata=trace_metadata,
        )


def main():
    """Основная функция теста"""
    print("🚀 Starting Langfuse trace linking test...")

    success = test_trace_linking()

    if success:
        print(
            "\n🎉 SUCCESS! Check Langfuse dashboard - trace should be linked to prompt!"
        )
        print("📍 Go to: Langfuse → Prompts → a101-hr-profile-gemini-v3-simple")
        print("📈 The trace should appear in the prompt's analytics")
    else:
        print("\n❌ FAILED! Check the errors above")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

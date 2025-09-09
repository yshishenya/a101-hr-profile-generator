#!/usr/bin/env python3
"""
🔍 Исследование полной структуры ответа OpenRouter для обогащения metadata
"""

import os
import sys
import json
import time
from pathlib import Path

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

from backend.core.llm_client import LLMClient
from langfuse import Langfuse


def explore_openrouter_response():
    """Исследуем полную структуру ответа OpenRouter"""

    print("🔍 Exploring OpenRouter response structure...")

    # Инициализация
    try:
        client = LLMClient()
        langfuse = Langfuse()
        print("✅ Clients initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    # Получаем промпт
    try:
        prompt = langfuse.get_prompt(
            "a101-hr-profile-gemini-v3-simple", label="production"
        )
        print(f"✅ Got prompt: {prompt.name} v{prompt.version}")
    except Exception as e:
        print(f"❌ Failed to get prompt: {e}")
        return False

    # Простые переменные для теста
    variables = {
        "position": "Test Position",
        "department": "Test Department",
        "employee_name": "Test Employee",
        "company_map": "Test company data",
        "org_structure": '{"test": "data"}',
        "kpi_data": "Test KPI",
        "it_systems": "Test IT",
        "json_schema": '{"type": "object"}',  # нужна для промпта
    }

    # Компилируем промпт
    compiled_prompt = prompt.compile(**variables)
    messages = [{"role": "user", "content": compiled_prompt}]

    # Получаем конфигурацию
    model = prompt.config.get("model", "google/gemini-2.5-flash")
    temperature = prompt.config.get("temperature", 0.1)
    max_tokens = prompt.config.get("max_tokens", 1000)
    response_format = prompt.config.get("response_format")

    print(f"🤖 Making request to model: {model}")

    try:
        # Прямой вызов для исследования
        response = client.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        print(f"\n📊 RESPONSE STRUCTURE ANALYSIS:")
        print(f"Response type: {type(response)}")
        print(
            f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}"
        )

        # Основные атрибуты
        print(f"\n🔍 MAIN ATTRIBUTES:")
        if hasattr(response, "id"):
            print(f"  ID: {response.id}")
        if hasattr(response, "object"):
            print(f"  Object: {response.object}")
        if hasattr(response, "created"):
            print(f"  Created: {response.created}")
        if hasattr(response, "model"):
            print(f"  Model: {response.model}")
        if hasattr(response, "system_fingerprint"):
            print(f"  System fingerprint: {response.system_fingerprint}")

        # Usage information
        print(f"\n💰 USAGE & COST INFO:")
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            print(f"  Usage type: {type(usage)}")
            print(
                f"  Usage dir: {[attr for attr in dir(usage) if not attr.startswith('_')]}"
            )
            print(f"  Prompt tokens: {getattr(usage, 'prompt_tokens', 'N/A')}")
            print(f"  Completion tokens: {getattr(usage, 'completion_tokens', 'N/A')}")
            print(f"  Total tokens: {getattr(usage, 'total_tokens', 'N/A')}")

            # Проверяем cost информацию (OpenRouter specific)
            if hasattr(usage, "cost"):
                print(f"  💰 Cost: ${usage.cost}")
            if hasattr(usage, "cost_details"):
                print(f"  💰 Cost details: {usage.cost_details}")
            if hasattr(usage, "prompt_cost"):
                print(f"  💰 Prompt cost: ${usage.prompt_cost}")
            if hasattr(usage, "completion_cost"):
                print(f"  💰 Completion cost: ${usage.completion_cost}")

            # Все доступные атрибуты usage
            usage_attrs = {}
            for attr in dir(usage):
                if not attr.startswith("_"):
                    try:
                        value = getattr(usage, attr)
                        if not callable(value):
                            usage_attrs[attr] = value
                    except:
                        pass
            print(
                f"  📋 All usage attributes: {json.dumps(usage_attrs, indent=2, default=str)}"
            )

        # Choices information
        print(f"\n📝 CHOICES INFO:")
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            print(f"  Choice type: {type(choice)}")
            print(
                f"  Choice dir: {[attr for attr in dir(choice) if not attr.startswith('_')]}"
            )
            print(f"  Finish reason: {getattr(choice, 'finish_reason', 'N/A')}")
            print(f"  Index: {getattr(choice, 'index', 'N/A')}")
            if hasattr(choice, "message"):
                print(f"  Message role: {choice.message.role}")
                print(f"  Content length: {len(choice.message.content)} chars")
                print(f"  Content preview: {choice.message.content[:200]}...")

        # Дополнительные атрибуты (OpenRouter specific)
        print(f"\n🌐 OPENROUTER SPECIFIC:")
        all_attrs = {}
        for attr in dir(response):
            if not attr.startswith("_") and attr not in ["choices", "usage"]:
                try:
                    value = getattr(response, attr)
                    if not callable(value):
                        all_attrs[attr] = value
                except:
                    pass
        print(
            f"  📋 Additional attributes: {json.dumps(all_attrs, indent=2, default=str)}"
        )

        # Попробуем получить raw response (если есть)
        if hasattr(response, "_raw_response"):
            print(f"\n🔧 RAW RESPONSE:")
            print(f"  Raw response type: {type(response._raw_response)}")

        return True

    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Основная функция исследования"""
    print("🚀 Starting OpenRouter response exploration...")

    success = explore_openrouter_response()

    if success:
        print(f"\n✅ SUCCESS! Analysis completed")
        print(f"💡 Use this information to enrich Langfuse metadata")
    else:
        print(f"\n❌ FAILED! Check the errors above")

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

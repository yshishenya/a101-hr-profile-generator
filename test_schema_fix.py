#!/usr/bin/env python3
"""
Тест для проверки исправления JSON schema:
- Загрузка конфигурации из templates/prompts/production/config.json
- Проверка наличия 'professional_skills_reasoning' в required
"""

import sys
sys.path.append('.')

from backend.core.prompt_manager import PromptManager
import json

def test_schema_fix():
    """Проверка исправления JSON schema"""

    print("🧪 Тест исправления JSON schema\n")
    print("=" * 60)

    # Инициализируем PromptManager
    pm = PromptManager()
    print("✅ PromptManager initialized\n")

    # Получаем конфигурацию
    config = pm.get_prompt_config('profile_generation', environment='production')
    print("✅ Config loaded from templates/prompts/production/config.json\n")

    # Проверяем основные параметры
    print(f"Model: {config.get('model')}")
    print(f"Temperature: {config.get('temperature')}")
    print(f"Max tokens: {config.get('max_tokens')}\n")

    # Проверяем response_format
    response_format = config.get('response_format')
    if not response_format:
        print("❌ FAILED: response_format not found in config")
        return False

    print(f"✅ response_format found: type={response_format.get('type')}\n")

    # Проверяем json_schema
    json_schema = response_format.get('json_schema', {})
    schema = json_schema.get('schema', {})

    print(f"Schema name: {json_schema.get('name')}")
    print(f"Strict mode: {json_schema.get('strict')}\n")

    # Проверяем required array
    required = schema.get('required', [])
    properties = list(schema.get('properties', {}).keys())

    print(f"Properties count: {len(properties)}")
    print(f"Required fields count: {len(required)}\n")

    # Ключевая проверка - наличие professional_skills_reasoning
    if 'professional_skills_reasoning' in required:
        print("✅ SUCCESS: 'professional_skills_reasoning' IS in required array")

        # Проверяем, что все properties в required
        missing = set(properties) - set(required)
        if missing:
            print(f"⚠️  WARNING: Some properties not in required: {missing}")
            return True  # Тест пройден, но есть предупреждения
        else:
            print("✅ All properties are in required array")
            return True
    else:
        print("❌ FAILED: 'professional_skills_reasoning' NOT in required array")
        print(f"\nRequired fields: {required}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  ТЕСТ ИСПРАВЛЕНИЯ BUG: JSON Schema Validation")
    print("="*60 + "\n")

    success = test_schema_fix()

    print("\n" + "="*60)
    if success:
        print("  ✅ ТЕ СТ ПРОЙДЕН УСПЕШНО!")
    else:
        print("  ❌ ТЕСТ НЕ ПРОЙДЕН!")
    print("="*60 + "\n")

    sys.exit(0 if success else 1)

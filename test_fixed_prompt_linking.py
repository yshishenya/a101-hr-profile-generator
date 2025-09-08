#!/usr/bin/env python3
"""
🔗 Тест исправленной связки промптов с @observe декоратором
Основано на официальной документации Langfuse
"""

import os
import sys
import json
import time
from pathlib import Path

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

from backend.core.llm_client import LLMClient

def test_fixed_prompt_linking():
    """Тестируем исправленную связку промптов"""
    
    print("🔗 Testing FIXED prompt linking with @observe decorator...")
    
    # Инициализация клиента
    try:
        client = LLMClient()
        print("✅ LLMClient initialized")
    except Exception as e:
        print(f"❌ Failed to initialize LLMClient: {e}")
        return False
    
    # Подготавливаем тестовые данные
    test_variables = {
        "position": "Senior ML Engineer",
        "department": "ДИТ",
        "employee_name": "Тестовый Сотрудник",
        "company_map": "Test company data (simplified)...",
        "org_structure": '{"ДИТ": {"positions": ["Engineer", "Senior Engineer"]}}',
        "kpi_data": "Test KPI data for ДИТ department...",
        "it_systems": "Test IT systems data...",
        "json_schema": '{"type": "object", "properties": {}}'  # нужна для промпта
    }
    
    print("🚀 Starting profile generation...")
    start_time = time.time()
    
    try:
        # Вызываем генерацию с правильной связкой
        result = client.generate_profile_from_langfuse(
            prompt_name="a101-hr-profile-gemini-v3-simple",
            variables=test_variables,
            user_id="test_user_fixed",
            session_id=f"fixed_session_{int(time.time())}"
        )
        
        generation_time = time.time() - start_time
        
        print(f"✅ Generation completed in {generation_time:.2f}s")
        print(f"🎯 Success: {result['metadata']['success']}")
        print(f"📊 Tokens: {result['metadata']['tokens']['total']}")
        print(f"🔗 Trace ID: {result['metadata'].get('langfuse_trace_id', 'N/A')}")
        print(f"📋 Profile fields: {len(result['profile']) if isinstance(result['profile'], dict) else 'N/A'}")
        
        # Показываем первые несколько полей профиля
        if isinstance(result['profile'], dict):
            print(f"\n📝 Generated profile preview:")
            for i, (key, value) in enumerate(list(result['profile'].items())[:3]):
                print(f"  - {key}: {type(value).__name__}")
                if i >= 2:
                    break
            if len(result['profile']) > 3:
                print(f"  ... and {len(result['profile']) - 3} more fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("🎯 Testing FIXED Langfuse prompt linking...")
    print("📚 Using @observe decorator for proper trace linking")
    
    success = test_fixed_prompt_linking()
    
    if success:
        print(f"\n🎉 SUCCESS! Fixed prompt linking is working!")
        print(f"🔍 Now check Langfuse dashboard:")
        print(f"   1. Go to https://cloud.langfuse.com")
        print(f"   2. Check Traces tab for recent trace")
        print(f"   3. Go to Prompts → a101-hr-profile-gemini-v3-simple")
        print(f"   4. Look for 'Linked Generations' section")
        print(f"   5. Should see the generation with @observe decorator!")
    else:
        print(f"\n❌ FAILED! Check the errors above")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
🔗 Прямое тестирование связки промптов с generations в Langfuse
"""

import os
import sys
import json
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

from langfuse import Langfuse
from langfuse.openai import OpenAI

def test_direct_prompt_linking():
    """Тестируем прямую связку промптов с generations"""
    
    print("🔗 Testing direct prompt linking...")
    
    # Инициализация Langfuse
    langfuse = Langfuse()
    
    # Создаем Langfuse OpenAI клиента
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        langfuse_host=os.getenv("LANGFUSE_HOST")
    )
    
    # Получаем промпт
    try:
        prompt = langfuse.get_prompt("a101-hr-profile-gemini-v3-simple", label="production")
        print(f"✅ Got prompt: {prompt.name} v{prompt.version}")
    except Exception as e:
        print(f"❌ Failed to get prompt: {e}")
        return False
    
    # Простые переменные для теста
    variables = {
        "position": "Test Position",
        "department": "Test Department", 
        "company_map": "Test company data",
        "org_structure": '{"test": "data"}',
        "kpi_data": "Test KPI",
        "it_systems": "Test IT",
        "json_schema": '{"type": "object"}'
    }
    
    try:
        # Компилируем промпт
        compiled_prompt = prompt.compile(**variables)
        messages = [{"role": "user", "content": compiled_prompt}]
        
        # Получаем конфигурацию
        config = prompt.config or {}
        model = config.get("model", "google/gemini-2.5-flash")
        temperature = config.get("temperature", 0.1)
        max_tokens = config.get("max_tokens", 1000)
        response_format = config.get("response_format")
        
        print(f"🤖 Testing with model: {model}")
        print(f"📝 Prompt length: {len(compiled_prompt)}")
        
        # Метод 1: langfuse_prompt параметр
        print("\n🔗 Method 1: Using langfuse_prompt parameter")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                langfuse_prompt=prompt  # Прямая связка
            )
            
            print("✅ Method 1 successful!")
            print(f"📊 Response tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
            
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Метод 2: metadata
        print("\n🔗 Method 2: Using metadata")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                metadata={"langfuse_prompt": prompt}  # Связка через метаданные
            )
            
            print("✅ Method 2 successful!")
            print(f"📊 Response tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
            
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Метод 3: Только метаданные с информацией о промпте
        print("\n🔗 Method 3: Using prompt info in metadata")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                metadata={
                    "prompt_name": prompt.name,
                    "prompt_version": prompt.version,
                    "prompt_id": prompt.id if hasattr(prompt, 'id') else None
                }
            )
            
            print("✅ Method 3 successful!")
            print(f"📊 Response tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
            
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
        
        print(f"\n🎯 Now check Langfuse dashboard:")
        print(f"   - Go to Prompts → {prompt.name}")
        print(f"   - Look for 'Linked Generations' section")
        print(f"   - Should see recent test generations")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Testing direct prompt linking methods...")
    
    success = test_direct_prompt_linking()
    
    if success:
        print("\n✅ SUCCESS! Check Langfuse for linked generations")
    else:
        print("\n❌ FAILED! Check errors above")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
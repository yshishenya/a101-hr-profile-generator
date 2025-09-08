#!/usr/bin/env python3
"""
📝 Создание промпта в Langfuse с правильной конфигурацией

Создает промпт в Langfuse с:
1. Системными и пользовательскими сообщениями
2. Конфигурацией модели (google/gemini-2.5-flash)
3. JSON схемой для structured output
4. Всеми параметрами генерации
"""

import os
import sys
import json
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

def create_langfuse_prompt():
    """Создание промпта в Langfuse с полной конфигурацией"""
    
    print("📝 Creating A101 HR Profile Generator Prompt in Langfuse")
    print("=" * 60)
    
    # Инициализация Langfuse
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY')
    
    if not public_key or not secret_key:
        print("❌ Langfuse credentials not found")
        return False
    
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host="https://cloud.langfuse.com"
    )
    
    # Читаем основной промпт-шаблон
    template_path = Path("/home/yan/A101/HR/templates/generation_prompt.txt")
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        print(f"✅ Loaded prompt template ({len(system_prompt)} chars)")
    else:
        print("❌ Template file not found")
        return False
    
    # Определяем JSON схему для structured output
    job_profile_schema = {
        "type": "object",
        "properties": {
            "position_title": {
                "type": "string",
                "description": "Точное название должности"
            },
            "department_broad": {
                "type": "string", 
                "description": "Подразделение укрупненно"
            },
            "department_specific": {
                "type": "string",
                "description": "Конкретное подразделение"
            },
            "category": {
                "type": "string",
                "description": "Категория должности",
                "enum": [
                    "Специалист",
                    "Линейный руководитель (группа, направление)",
                    "Руководитель среднего уровня (отдел, управление)",
                    "Руководитель высшего уровня (департамент)"
                ]
            },
            "direct_manager": {
                "type": "string",
                "description": "Должность непосредственного руководителя"
            },
            "subordinates": {
                "type": "object",
                "properties": {
                    "departments": {"type": "integer"},
                    "people": {"type": "string"}
                }
            },
            "primary_activity": {
                "type": "string",
                "description": "Профильная/обеспечивающая деятельность"
            },
            "responsibility_areas": {
                "type": "array",
                "description": "Области ответственности с детальными задачами",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "tasks": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["title", "tasks"]
                },
                "minItems": 3
            },
            "professional_skills": {
                "type": "array",
                "description": "Профессиональные навыки по категориям",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "skills": {
                            "type": "array", 
                            "items": {"type": "string"}
                        },
                        "target_level": {
                            "type": "string",
                            "enum": ["Базовый", "Продвинутый", "Экспертный"]
                        }
                    },
                    "required": ["category", "skills"]
                },
                "minItems": 2
            },
            "corporate_competencies": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "Инновационность и развитие",
                        "Ориентация на результат", 
                        "Стратегическое видение и принятие решений",
                        "Клиентоориентированность",
                        "Эффективная коммуникация",
                        "Работа в команде",
                        "Лидерство"
                    ]
                },
                "minItems": 3,
                "maxItems": 5
            },
            "personal_qualities": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "Внимательность", "Ответственность", "Коммуникабельность",
                        "Стрессоустойчивость", "Настойчивость", "Исполнительность",
                        "Системность мышления", "Инициативность", "Проактивность",
                        "Критическое мышление", "Лидерство", "Аналитический склад ума",
                        "Многозадачность", "Решительность"
                    ]
                },
                "minItems": 5,
                "maxItems": 8
            },
            "education": {
                "type": "object",
                "properties": {
                    "education_level": {
                        "type": "string",
                        "enum": [
                            "Среднее общее образование",
                            "Среднее профессиональное образование", 
                            "Высшее образование",
                            "Высшее/неоконченное высшее образование"
                        ]
                    },
                    "specialties": {"type": "string"},
                    "total_experience": {"type": "string"},
                    "additional_education": {"type": "string"}
                }
            },
            "career_path": {
                "type": "object",
                "properties": {
                    "donor_positions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "target_positions": {
                        "type": "array", 
                        "items": {"type": "string"}
                    }
                }
            },
            "technical_requirements": {
                "type": "object",
                "properties": {
                    "software": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "equipment": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "required": [
            "position_title", "department_broad", "department_specific", 
            "category", "primary_activity", "responsibility_areas",
            "professional_skills", "corporate_competencies", "personal_qualities"
        ],
        "additionalProperties": False
    }
    
    # Конфигурация промпта для Langfuse
    prompt_config = {
        "model": "google/gemini-2.5-flash",
        "temperature": 0.1,
        "max_tokens": 4000,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "job_profile",
                "strict": True,
                "schema": job_profile_schema
            }
        }
    }
    
    # Создаем промпт с системным и пользовательским сообщением
    try:
        print("🚀 Creating prompt in Langfuse...")
        
        # Удаляем старый промпт если существует (опционально)
        # langfuse.delete_prompt("a101-hr-profile-generation")
        
        result = langfuse.create_prompt(
            name="a101-hr-profile-gemini-v2",
            prompt=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": "Создай профиль должности \"{{position}}\" для департамента \"{{department}}\" сотрудника \"{{employee_name}}\".\n\nИспользуй контекст:\n- Организационная структура: {{org_structure}}\n- KPI данные: {{kpi_data}}\n- IT системы: {{it_systems}}\n\nВерни ТОЛЬКО валидный JSON в соответствии со схемой."
                }
            ],
            labels=["production", "v2.0", "structured-output"],
            tags=["a101", "hr", "profile-generation", "gemini-2.5-flash"],
            type="chat",
            config=prompt_config,
            commit_message="A101 HR Profile Generator v2.0 with structured output for Gemini 2.5 Flash"
        )
        
        print("✅ Prompt successfully created in Langfuse!")
        print(f"  Name: a101-hr-profile-gemini-v2")
        print(f"  Model: {prompt_config['model']}")
        print(f"  Temperature: {prompt_config['temperature']}")
        print(f"  Structured output: ✅")
        print(f"  Schema properties: {len(job_profile_schema['properties'])}")
        print(f"  Required fields: {len(job_profile_schema['required'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create prompt: {e}")
        
        # Если промпт уже существует, попробуем обновить
        if "already exists" in str(e).lower():
            print("ℹ️  Prompt already exists, this is normal")
            return True
        
        return False

def test_prompt_retrieval():
    """Тест получения созданного промпта"""
    
    print(f"\n🔍 Testing prompt retrieval...")
    
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY')
    
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host="https://cloud.langfuse.com"
    )
    
    try:
        prompt = langfuse.get_prompt("a101-hr-profile-gemini-v2")
        
        print("✅ Prompt retrieved successfully!")
        print(f"  Type: {type(prompt)}")
        
        if hasattr(prompt, 'prompt'):
            messages = prompt.prompt
            print(f"  Messages: {len(messages) if isinstance(messages, list) else 'Not a list'}")
        
        if hasattr(prompt, 'config'):
            config = prompt.config
            print(f"  Config model: {config.get('model', 'N/A')}")
            print(f"  Config temperature: {config.get('temperature', 'N/A')}")
            print(f"  Response format: {'JSON Schema' if config.get('response_format') else 'Text'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to retrieve prompt: {e}")
        return False

if __name__ == "__main__":
    print("🏗️ A101 HR Profile Generator - Langfuse Prompt Setup")
    print("=" * 60)
    
    success1 = create_langfuse_prompt()
    success2 = test_prompt_retrieval()
    
    if success1 and success2:
        print(f"\n🎉 SUCCESS: Prompt setup completed!")
        print(f"📊 Next steps:")
        print(f"  1. Update LLMClient to use langfuse.openai")
        print(f"  2. Modify ProfileGenerator to use Langfuse prompts")
        print(f"  3. Test complete pipeline")
        print(f"\n🌐 Check prompt in Langfuse: https://cloud.langfuse.com")
    else:
        print(f"\n❌ FAILED: Prompt setup incomplete")
    
    exit(0 if success1 and success2 else 1)
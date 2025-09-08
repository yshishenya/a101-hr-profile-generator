#!/usr/bin/env python3
"""
🔍 Full Trace Pipeline Test - полный трейс пайплайна с детальным логированием
Включает весь ответ LLM и детальную трассировку
"""

import os
import sys
import asyncio
import logging
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

# Добавляем путь к проекту
sys.path.insert(0, '/home/yan/A101/HR')

# Настраиваем детальное логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_pipeline_trace.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Устанавливаем DEBUG для всех наших модулей
logging.getLogger('backend.core.llm_client').setLevel(logging.DEBUG)
logging.getLogger('backend.core.profile_generator').setLevel(logging.DEBUG)
logging.getLogger('backend.core.data_loader').setLevel(logging.DEBUG)
logging.getLogger('langfuse').setLevel(logging.DEBUG)

from backend.core.profile_generator import ProfileGenerator

logger = logging.getLogger(__name__)

async def test_full_trace_pipeline():
    """Полный трейс пайплайна с детальным логированием"""
    
    logger.info("=" * 80)
    logger.info("🔍 A101 HR Profile Generator - FULL TRACE PIPELINE TEST")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # 1. Инициализация
        logger.info("🚀 STEP 1: Initializing ProfileGenerator")
        logger.debug("Environment variables loaded from .env")
        
        generator = ProfileGenerator()
        
        logger.info("✅ ProfileGenerator initialized successfully")
        logger.info(f"   - Langfuse enabled: {generator.langfuse_enabled}")
        logger.info(f"   - Base data path: {generator.base_data_path}")
        logger.info(f"   - LLM client available: {generator.llm_client is not None}")
        
        # 2. Валидация системы
        logger.info("\n🔧 STEP 2: System Validation")
        validation = await generator.validate_system()
        
        logger.info("📊 System validation results:")
        logger.info(f"   - System ready: {validation['system_ready']}")
        
        for component, status in validation["components"].items():
            if isinstance(status, dict):
                logger.info(f"   - {component}: {status}")
            else:
                logger.info(f"   - {component}: {status}")
        
        if validation["errors"]:
            logger.warning("⚠️ Validation errors:")
            for error in validation["errors"]:
                logger.warning(f"     - {error}")
        
        if not validation["system_ready"]:
            logger.error("❌ System not ready, aborting")
            return False
        
        # 3. Детальная генерация профиля с полным трейсингом
        logger.info("\n🤖 STEP 3: Profile Generation with Full Tracing")
        
        test_params = {
            "department": "ДИТ",
            "position": "Senior ML Engineer",
            "employee_name": "Full Trace Test User",
            "temperature": 0.1,
            "save_result": False
        }
        
        logger.info("📋 Generation parameters:")
        for key, value in test_params.items():
            logger.info(f"   - {key}: {value}")
        
        logger.info("\n🔄 Starting profile generation...")
        
        # Кастомизируем LLMClient для более детального логирования
        original_generate = generator.llm_client.generate_profile_from_langfuse
        
        def enhanced_generate(*args, **kwargs):
            logger.info("🔍 DETAILED LLM TRACE:")
            logger.info(f"   - Method: generate_profile_from_langfuse")
            logger.info(f"   - Prompt name: {args[0] if args else 'N/A'}")
            logger.info(f"   - Variables keys: {list(args[1].keys()) if len(args) > 1 else 'N/A'}")
            
            result = original_generate(*args, **kwargs)
            
            logger.info("📤 LLM RESPONSE RECEIVED:")
            logger.info(f"   - Success: {result['metadata']['success']}")
            logger.info(f"   - Generation time: {result['metadata']['generation_time']:.2f}s")
            
            # Выводим RAW ответ LLM
            raw_response = result.get('raw_response', '')
            if raw_response:
                logger.info("\n🤖 RAW LLM RESPONSE:")
                logger.info("=" * 80)
                logger.info(raw_response)
                logger.info("=" * 80)
            
            # Выводим распарсенный JSON профиль
            profile = result.get('profile', {})
            if profile and isinstance(profile, dict):
                logger.info("\n📋 PARSED JSON PROFILE:")
                logger.info("=" * 80)
                logger.info(json.dumps(profile, indent=2, ensure_ascii=False))
                logger.info("=" * 80)
            
            return result
        
        # Временно заменяем метод для детального логирования
        generator.llm_client.generate_profile_from_langfuse = enhanced_generate
        
        # Выполняем генерацию
        result = await generator.generate_profile(**test_params)
        
        # Восстанавливаем оригинальный метод
        generator.llm_client.generate_profile_from_langfuse = original_generate
        
        logger.info("\n📊 STEP 4: Generation Results Analysis")
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        logger.info("🎯 FINAL RESULTS:")
        logger.info(f"   - Success: {'✅' if result['success'] else '❌'}")
        logger.info(f"   - Total execution time: {generation_time:.2f}s")
        
        if result["success"]:
            profile = result.get("profile", {})
            metadata = result.get("metadata", {})
            
            logger.info("📋 GENERATED PROFILE STRUCTURE:")
            if isinstance(profile, dict):
                for key, value in profile.items():
                    if isinstance(value, list):
                        logger.info(f"   - {key}: array with {len(value)} items")
                    elif isinstance(value, dict):
                        logger.info(f"   - {key}: object with {len(value)} fields")
                    else:
                        logger.info(f"   - {key}: {type(value).__name__}")
            
            logger.info("\n✅ Profile generated successfully (see RAW LLM RESPONSE above)")
            
            # LLM метрики
            llm_meta = metadata.get("llm", {})
            if llm_meta:
                logger.info("\n📈 LLM PERFORMANCE METRICS:")
                logger.info(f"   - Model: {llm_meta.get('model', 'N/A')}")
                logger.info(f"   - Generation time: {llm_meta.get('generation_time', 0):.2f}s")
                
                tokens = llm_meta.get('tokens', {})
                if tokens:
                    logger.info(f"   - Input tokens: {tokens.get('input', 0)}")
                    logger.info(f"   - Output tokens: {tokens.get('output', 0)}")
                    logger.info(f"   - Total tokens: {tokens.get('total', 0)}")
                
                logger.info(f"   - Temperature: {llm_meta.get('temperature', 'N/A')}")
                logger.info(f"   - Success: {llm_meta.get('success', False)}")
                
                # Langfuse трейсинг
                trace_id = llm_meta.get('langfuse_trace_id')
                if trace_id:
                    logger.info(f"   - 🔗 Langfuse trace ID: {trace_id}")
                    logger.info(f"   - 🌐 View trace: https://cloud.langfuse.com")
                
                # Raw response already shown above during LLM call
            
            # Валидация профиля
            generation_meta = metadata.get("generation", {})
            if generation_meta:
                logger.info("\n✅ GENERATION METADATA:")
                logger.info(f"   - Department: {generation_meta.get('department', 'N/A')}")
                logger.info(f"   - Position: {generation_meta.get('position', 'N/A')}")
                logger.info(f"   - Duration: {generation_meta.get('duration', 0):.2f}s")
                logger.info(f"   - Timestamp: {generation_meta.get('timestamp', 'N/A')}")
        
        else:
            logger.error("❌ GENERATION FAILED:")
            errors = result.get("errors", [])
            for error in errors:
                logger.error(f"     - {error}")
            
            # Выводим метаданные даже при неудаче
            metadata = result.get("metadata", {})
            if metadata:
                logger.info("📊 Error metadata:")
                logger.info(json.dumps(metadata, indent=2, ensure_ascii=False))
        
        logger.info(f"\n🏁 PIPELINE TRACE COMPLETED!")
        logger.info(f"📄 Full log saved to: full_pipeline_trace.log")
        logger.info("=" * 80)
        
        return result["success"]
        
    except Exception as e:
        logger.error(f"\n💥 PIPELINE EXCEPTION:")
        logger.error(f"   - Error: {e}")
        logger.error(f"   - Type: {type(e).__name__}")
        
        import traceback
        logger.error("📍 Full traceback:")
        logger.error(traceback.format_exc())
        
        return False


async def main():
    """Главная функция теста"""
    logger.info("Starting Full Trace Pipeline Test")
    success = await test_full_trace_pipeline()
    
    if success:
        logger.info("🎉 FULL TRACE PIPELINE TEST: SUCCESS!")
    else:
        logger.error("💥 FULL TRACE PIPELINE TEST: FAILED!")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
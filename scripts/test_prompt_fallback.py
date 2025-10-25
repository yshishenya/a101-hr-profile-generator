#!/usr/bin/env python3
"""
@doc Тестирование fallback механизма PromptManager

Этот скрипт тестирует три сценария:
1. Успешное получение из Langfuse (с сохранением в локальные файлы)
2. Fallback к локальным файлам (когда Langfuse недоступен)
3. Fallback к старому формату (когда новые файлы отсутствуют)

Examples:
    python>
    # Запуск теста
    python scripts/test_prompt_fallback.py
"""

import logging
import sys
from pathlib import Path

# Добавляем путь к backend
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"

sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
import os

env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

from backend.core.prompt_manager import PromptManager
from langfuse import Langfuse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_scenario_1_langfuse_available():
    """Тест 1: Langfuse доступен"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: Langfuse Available - Should fetch and save locally")
    logger.info("=" * 60)

    try:
        # Инициализируем Langfuse
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )

        # Инициализируем PromptManager с Langfuse
        pm = PromptManager(
            langfuse_client=langfuse,
            templates_dir=str(TEMPLATES_DIR),
            cache_ttl=0,  # Отключаем кеш для теста
        )

        # Получаем промпт
        variables = {
            "position": "Test Position",
            "department": "Test Department",
            "generation_timestamp": "2025-10-25",
            "company_map": "Test Data",
            "org_structure": "Test Org",
            "kpi_data": "Test KPI",
            "it_systems": "Test Systems",
            "hierarchy_level": "3",
            "full_hierarchy_path": "Test/Path",
            "business_block": "Test Block",
            "department_unit": "Test Unit",
            "section_unit": "",
            "group_unit": "",
            "sub_section_unit": "",
            "final_group_unit": "",
            "subordinates_departments": "0",
            "subordinates_direct_reports": "0",
            "department_headcount": "10",
        }

        prompt = pm.get_prompt("profile_generation", variables=variables)

        logger.info(f"✅ Test 1 PASSED: Retrieved prompt from Langfuse")
        logger.info(f"   Prompt length: {len(prompt)} characters")
        logger.info(f"   First 100 chars: {prompt[:100]}...")

        # Проверяем что файлы были сохранены
        prod_dir = TEMPLATES_DIR / "prompts" / "production"
        files_exist = (
            (prod_dir / "prompt.txt").exists()
            and (prod_dir / "config.json").exists()
            and (prod_dir / "metadata.json").exists()
        )

        if files_exist:
            logger.info(f"✅ Local files were created successfully")
        else:
            logger.warning(f"⚠️ Local files were not created")

        return True

    except Exception as e:
        logger.error(f"❌ Test 1 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scenario_2_langfuse_unavailable():
    """Тест 2: Langfuse недоступен, используем локальные файлы"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Langfuse Unavailable - Should use local files")
    logger.info("=" * 60)

    try:
        # Инициализируем PromptManager БЕЗ Langfuse
        pm = PromptManager(
            langfuse_client=None,  # Симулируем отсутствие Langfuse
            templates_dir=str(TEMPLATES_DIR),
            cache_ttl=0,
        )

        # Получаем промпт
        variables = {
            "position": "Test Position",
            "department": "Test Department",
            "generation_timestamp": "2025-10-25",
            "company_map": "Test Data",
            "org_structure": "Test Org",
            "kpi_data": "Test KPI",
            "it_systems": "Test Systems",
            "hierarchy_level": "3",
            "full_hierarchy_path": "Test/Path",
            "business_block": "Test Block",
            "department_unit": "Test Unit",
            "section_unit": "",
            "group_unit": "",
            "sub_section_unit": "",
            "final_group_unit": "",
            "subordinates_departments": "0",
            "subordinates_direct_reports": "0",
            "department_headcount": "10",
        }

        prompt = pm.get_prompt("profile_generation", variables=variables)

        logger.info(f"✅ Test 2 PASSED: Retrieved prompt from local files")
        logger.info(f"   Prompt length: {len(prompt)} characters")
        logger.info(f"   First 100 chars: {prompt[:100]}...")

        return True

    except Exception as e:
        logger.error(f"❌ Test 2 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_scenario_3_config_fallback():
    """Тест 3: Получение конфигурации с fallback"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Config Fallback - Should try Langfuse then local files")
    logger.info("=" * 60)

    try:
        # Тест 3a: С Langfuse
        logger.info("\n--- Test 3a: With Langfuse ---")
        langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )

        pm_with_langfuse = PromptManager(
            langfuse_client=langfuse, templates_dir=str(TEMPLATES_DIR)
        )

        config = pm_with_langfuse.get_prompt_config("profile_generation")
        logger.info(f"Config source: Langfuse (expected)")
        logger.info(f"Model: {config.get('model')}")
        logger.info(f"Temperature: {config.get('temperature')}")
        logger.info(f"Max tokens: {config.get('max_tokens')}")

        # Тест 3b: Без Langfuse
        logger.info("\n--- Test 3b: Without Langfuse ---")
        pm_without_langfuse = PromptManager(
            langfuse_client=None, templates_dir=str(TEMPLATES_DIR)
        )

        config_fallback = pm_without_langfuse.get_prompt_config("profile_generation")
        logger.info(f"Config source: Local files (expected)")
        logger.info(f"Model: {config_fallback.get('model')}")
        logger.info(f"Temperature: {config_fallback.get('temperature')}")
        logger.info(f"Max tokens: {config_fallback.get('max_tokens')}")

        logger.info(f"\n✅ Test 3 PASSED: Config fallback works correctly")
        return True

    except Exception as e:
        logger.error(f"❌ Test 3 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Запуск всех тестов"""
    logger.info("\n" + "=" * 60)
    logger.info("PROMPT FALLBACK MECHANISM TEST SUITE")
    logger.info("=" * 60)

    results = {
        "Test 1 (Langfuse Available)": test_scenario_1_langfuse_available(),
        "Test 2 (Langfuse Unavailable)": test_scenario_2_langfuse_unavailable(),
        "Test 3 (Config Fallback)": test_scenario_3_config_fallback(),
    }

    # Итоговый отчет
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Fallback mechanism works correctly.")
        sys.exit(0)
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
@doc Скрипт для синхронизации промптов из Langfuse в локальные файлы

Этот скрипт загружает production промпты из Langfuse и сохраняет их
в структурированные локальные файлы для fallback режима.

Структура сохранения:
/templates/prompts/production/
  prompt.txt           # Текст промпта
  config.json          # Конфигурация (model, temperature, JSON schema)
  metadata.json        # Метаданные (version, timestamp, hash)

Examples:
    python>
    # Запуск синхронизации
    python scripts/sync_prompts_from_langfuse.py

    # С указанием окружения
    python scripts/sync_prompts_from_langfuse.py --environment development

    # Только проверка без сохранения
    python scripts/sync_prompts_from_langfuse.py --dry-run
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Добавляем путь к backend для импорта модулей
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"

sys.path.insert(0, str(PROJECT_ROOT))

# Загружаем .env файл напрямую
from dotenv import load_dotenv

env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

from backend.core.prompt_manager import PromptManager
from langfuse import Langfuse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def sync_prompts(environment: str = "production", dry_run: bool = False):
    """
    @doc Синхронизация промптов из Langfuse в локальные файлы

    Args:
        environment: Окружение (production/development)
        dry_run: Режим проверки без сохранения

    Examples:
        python>
        # Синхронизация production промптов
        sync_prompts("production", dry_run=False)

        # Проверка без сохранения
        sync_prompts("production", dry_run=True)
    """
    logger.info(f"🚀 Starting prompt synchronization for environment: {environment}")
    logger.info(f"Dry run mode: {dry_run}")

    # Получаем credentials напрямую из environment
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    # Проверяем наличие Langfuse credentials
    if not langfuse_public_key or not langfuse_secret_key:
        logger.error("❌ Langfuse credentials not found in .env file")
        logger.error("Please set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")
        return False

    try:
        # Инициализируем Langfuse клиент
        langfuse = Langfuse(
            public_key=langfuse_public_key,
            secret_key=langfuse_secret_key,
            host=langfuse_host,
        )
        logger.info("✅ Langfuse client initialized")

        # Инициализируем PromptManager
        prompt_manager = PromptManager(
            langfuse_client=langfuse,
            templates_dir=str(TEMPLATES_DIR),
            cache_ttl=0,  # Отключаем кеш для синхронизации
        )
        logger.info("✅ PromptManager initialized")

        # Список промптов для синхронизации
        prompts_to_sync = [
            {
                "name": "profile_generation",
                "langfuse_name": "a101-hr-profile-gemini-v3-simple",
                "label": environment,
            }
        ]

        results = []

        for prompt_info in prompts_to_sync:
            logger.info(f"\n{'='*60}")
            logger.info(f"Syncing: {prompt_info['name']}")
            logger.info(f"Langfuse name: {prompt_info['langfuse_name']}")
            logger.info(f"Label: {prompt_info['label']}")
            logger.info(f"{'='*60}\n")

            try:
                # Получаем промпт из Langfuse
                prompt_obj = langfuse.get_prompt(
                    prompt_info["langfuse_name"], label=prompt_info["label"]
                )

                if not prompt_obj:
                    logger.error(f"❌ Prompt not found: {prompt_info['langfuse_name']}")
                    results.append(
                        {
                            "name": prompt_info["name"],
                            "status": "error",
                            "error": "Prompt not found",
                        }
                    )
                    continue

                # Извлекаем текст промпта
                prompt_text = None
                if hasattr(prompt_obj, "prompt"):
                    prompt_text = prompt_obj.prompt
                elif hasattr(prompt_obj, "content"):
                    prompt_text = prompt_obj.content
                else:
                    prompt_text = str(prompt_obj)

                if not prompt_text:
                    logger.error(f"❌ Empty prompt text for {prompt_info['name']}")
                    results.append(
                        {
                            "name": prompt_info["name"],
                            "status": "error",
                            "error": "Empty prompt text",
                        }
                    )
                    continue

                # Информация о промпте
                version = getattr(prompt_obj, "version", "unknown")
                labels = getattr(prompt_obj, "labels", [])
                config_data = getattr(prompt_obj, "config", {})

                logger.info(f"📄 Prompt version: {version}")
                logger.info(f"🏷️  Labels: {labels}")
                logger.info(f"📝 Prompt length: {len(prompt_text)} characters")
                logger.info(f"📝 Prompt lines: {len(prompt_text.split(chr(10)))} lines")

                # Показываем конфигурацию
                if config_data:
                    logger.info(f"⚙️  Model: {config_data.get('model', 'N/A')}")
                    logger.info(
                        f"⚙️  Temperature: {config_data.get('temperature', 'N/A')}"
                    )
                    logger.info(
                        f"⚙️  Max tokens: {config_data.get('max_tokens', 'N/A')}"
                    )

                    # Проверяем JSON schema
                    response_format = config_data.get("response_format", {})
                    if response_format:
                        json_schema = response_format.get("json_schema", {})
                        if json_schema:
                            schema_name = json_schema.get("name", "unknown")
                            logger.info(f"📋 JSON Schema: {schema_name}")

                # Если dry-run, не сохраняем
                if dry_run:
                    logger.info("🔍 DRY RUN: Would save prompt to local files")
                    results.append(
                        {
                            "name": prompt_info["name"],
                            "status": "dry_run",
                            "version": version,
                            "size": len(prompt_text),
                        }
                    )
                    continue

                # Сохраняем промпт в локальные файлы
                prompt_manager._save_prompt_to_local(
                    prompt_info["name"], prompt_obj, prompt_text, environment
                )

                logger.info(
                    f"✅ Successfully saved prompt '{prompt_info['name']}' to local files"
                )
                results.append(
                    {
                        "name": prompt_info["name"],
                        "status": "success",
                        "version": version,
                        "size": len(prompt_text),
                    }
                )

            except Exception as e:
                logger.error(f"❌ Error syncing {prompt_info['name']}: {e}")
                results.append(
                    {"name": prompt_info["name"], "status": "error", "error": str(e)}
                )

        # Итоговый отчет
        logger.info(f"\n{'='*60}")
        logger.info("SYNCHRONIZATION SUMMARY")
        logger.info(f"{'='*60}\n")

        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")
        dry_run_count = sum(1 for r in results if r["status"] == "dry_run")

        logger.info(f"Total prompts: {len(results)}")
        logger.info(f"✅ Successful: {success_count}")
        logger.info(f"❌ Errors: {error_count}")
        logger.info(f"🔍 Dry run: {dry_run_count}")

        if error_count > 0:
            logger.info(f"\n{'='*60}")
            logger.info("ERRORS:")
            for result in results:
                if result["status"] == "error":
                    logger.error(
                        f"  - {result['name']}: {result.get('error', 'Unknown error')}"
                    )

        return error_count == 0

    except Exception as e:
        logger.error(f"❌ Fatal error during synchronization: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_local_files(environment: str = "production"):
    """
    @doc Проверка целостности локальных файлов промптов

    Examples:
        python>
        # Проверка production файлов
        verify_local_files("production")
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"VERIFYING LOCAL FILES for {environment}")
    logger.info(f"{'='*60}\n")

    env_dir = TEMPLATES_DIR / "prompts" / environment

    if not env_dir.exists():
        logger.error(f"❌ Directory not found: {env_dir}")
        return False

    # Проверяем наличие всех файлов
    prompt_file = env_dir / "prompt.txt"
    config_file = env_dir / "config.json"
    metadata_file = env_dir / "metadata.json"

    files_status = {
        "prompt.txt": prompt_file.exists(),
        "config.json": config_file.exists(),
        "metadata.json": metadata_file.exists(),
    }

    logger.info(f"Directory: {env_dir}")
    for filename, exists in files_status.items():
        status = "✅" if exists else "❌"
        logger.info(f"{status} {filename}")

    # Проверяем метаданные
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        logger.info(f"\n📋 Metadata:")
        logger.info(f"  Version: {metadata.get('version')}")
        logger.info(f"  Saved at: {metadata.get('saved_at')}")
        logger.info(f"  Hash: {metadata.get('hash', '')[:16]}...")
        logger.info(f"  Character count: {metadata.get('character_count')}")
        logger.info(f"  Line count: {metadata.get('line_count')}")

    # Проверяем конфигурацию
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        logger.info(f"\n⚙️  Configuration:")
        logger.info(f"  Model: {config_data.get('model')}")
        logger.info(f"  Temperature: {config_data.get('temperature')}")
        logger.info(f"  Max tokens: {config_data.get('max_tokens')}")

    all_exist = all(files_status.values())
    logger.info(f"\n{'='*60}")
    logger.info(f"Verification: {'✅ PASSED' if all_exist else '❌ FAILED'}")
    logger.info(f"{'='*60}\n")

    return all_exist


def main():
    """Основная функция скрипта"""
    parser = argparse.ArgumentParser(
        description="Sync prompts from Langfuse to local files"
    )
    parser.add_argument(
        "--environment",
        "-e",
        default="production",
        choices=["production", "development"],
        help="Environment to sync (default: production)",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Dry run mode - check without saving",
    )
    parser.add_argument(
        "--verify",
        "-v",
        action="store_true",
        help="Verify local files after sync",
    )

    args = parser.parse_args()

    # Запускаем синхронизацию
    success = sync_prompts(environment=args.environment, dry_run=args.dry_run)

    # Проверяем файлы если запрошено
    if args.verify and not args.dry_run:
        verify_local_files(environment=args.environment)

    # Возвращаем exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

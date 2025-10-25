#!/usr/bin/env python3
"""
@doc Универсальный скрипт для загрузки/обновления промптов в Langfuse

Поддерживает:
- Загрузку prompt.txt
- Загрузку config.json (включая JSON schema)
- Создание новых версий
- Обновление существующих промптов

Examples:
    python>
    # Загрузить из локальной структуры
    python scripts/upload_prompt_to_langfuse.py --environment production

    # Только config (быстрое исправление)
    python scripts/upload_prompt_to_langfuse.py --config-only

    # С кастомной версией
    python scripts/upload_prompt_to_langfuse.py --version 47
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Добавляем путь к backend
sys.path.insert(0, str(Path(__file__).parent.parent))

# Загружаем .env файл напрямую
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from langfuse import Langfuse


def load_local_prompt_files(environment="production"):
    """
    Загрузка промпта и конфига из локальных файлов

    Args:
        environment: Окружение (production/development)

    Returns:
        Tuple[str, dict, dict]: (prompt_text, config, metadata)
    """
    base_dir = Path(__file__).parent.parent / "templates" / "prompts" / environment

    prompt_file = base_dir / "prompt.txt"
    config_file = base_dir / "config.json"
    metadata_file = base_dir / "metadata.json"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # Читаем файлы
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return prompt_text, config, metadata


def upload_to_langfuse(
    prompt_text,
    config,
    metadata,
    prompt_name="a101-hr-profile-gemini-v3-simple",
    version=None,
    labels=None,
    dry_run=False,
):
    """
    Загрузка промпта в Langfuse

    Args:
        prompt_text: Текст промпта
        config: Конфигурация (model, temperature, response_format)
        metadata: Метаданные из локального файла
        prompt_name: Имя промпта в Langfuse
        version: Версия (если None, будет взята из metadata)
        labels: Список лейблов (если None, будет ['production'])
        dry_run: Режим проверки без фактической загрузки

    Returns:
        bool: Success status
    """
    print(f"\n{'='*70}")
    print(f"📤 UPLOADING PROMPT TO LANGFUSE")
    print(f"{'='*70}")

    # Получаем credentials
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        print("❌ Langfuse credentials not found in .env")
        return False

    # Подготавливаем данные
    version = version or metadata.get("version", "unknown")
    labels = labels or ["production", f"v{version}"]

    print(f"\n📋 Prompt Details:")
    print(f"   Name: {prompt_name}")
    print(f"   Version: {version}")
    print(f"   Labels: {labels}")
    print(f"   Prompt size: {len(prompt_text)} chars (~{len(prompt_text)//4} tokens)")
    print(f"   Config keys: {list(config.keys())}")

    # Показываем важные изменения из metadata
    if "config_note" in metadata:
        print(f"   📝 Config note: {metadata['config_note']}")

    # Проверяем JSON schema
    response_format = config.get("response_format", {})
    if response_format:
        json_schema = response_format.get("json_schema", {})
        if json_schema:
            schema_name = json_schema.get("name", "unknown")
            schema = json_schema.get("schema", {})
            properties_count = len(schema.get("properties", {}))
            required_count = len(schema.get("required", []))

            print(f"\n📋 JSON Schema:")
            print(f"   Schema name: {schema_name}")
            print(f"   Strict mode: {json_schema.get('strict', False)}")
            print(f"   Properties: {properties_count}")
            print(f"   Required fields: {required_count}")

            # Проверяем согласованность
            properties_keys = set(schema.get("properties", {}).keys())
            required_keys = set(schema.get("required", []))

            if properties_keys != required_keys:
                print(f"\n   ⚠️  WARNING: Properties and required mismatch!")
                missing = properties_keys - required_keys
                extra = required_keys - properties_keys
                if missing:
                    print(f"      Missing in required: {missing}")
                if extra:
                    print(f"      Extra in required: {extra}")
            else:
                print(f"   ✅ Schema validation: All {properties_count} fields consistent")

    if dry_run:
        print(f"\n🔍 DRY RUN: Would upload to Langfuse")
        return True

    # Инициализируем Langfuse
    try:
        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
        print(f"\n✅ Langfuse client initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize Langfuse: {e}")
        return False

    # Загружаем промпт
    try:
        print(f"\n🚀 Creating/updating prompt in Langfuse...")

        # Подготавливаем config для Langfuse
        langfuse_config = {
            **config,  # Включаем весь config (model, temperature, response_format)
            "metadata": {
                "version": version,
                "uploaded_at": datetime.now().isoformat(),
                "source": "local_files",
                "local_metadata": metadata,
            },
        }

        result = langfuse.create_prompt(
            name=prompt_name,
            prompt=prompt_text,
            labels=labels,
            tags=["a101", "hr", "profile-generation", f"v{version}"],
            type="text",
            config=langfuse_config,
            commit_message=metadata.get(
                "config_note",
                f"Updated prompt v{version} from local files at {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ),
        )

        print(f"\n✅ Prompt uploaded successfully!")
        print(f"   Result type: {type(result)}")

        return True

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Upload failed: {e}")

        # Если промпт существует, пробуем обновить
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
            print(f"\n⚠️  Prompt '{prompt_name}' already exists")
            print(f"   Langfuse will auto-increment version")
            print(f"   Retrying upload...")

            try:
                # Повторная попытка - Langfuse автоматически создаст новую версию
                result = langfuse.create_prompt(
                    name=prompt_name,
                    prompt=prompt_text,
                    labels=labels,
                    tags=["a101", "hr", f"v{version}-update"],
                    type="text",
                    config=langfuse_config,
                    commit_message=f"Update: {metadata.get('config_note', 'Updated prompt')}",
                )

                print(f"✅ New version created successfully!")
                return True

            except Exception as e2:
                print(f"❌ Retry failed: {e2}")
                import traceback

                traceback.print_exc()
                return False

        import traceback

        traceback.print_exc()
        return False


def verify_upload(prompt_name="a101-hr-profile-gemini-v3-simple", label="production"):
    """Проверка загруженного промпта"""
    print(f"\n{'='*70}")
    print(f"🔍 VERIFYING UPLOADED PROMPT")
    print(f"{'='*70}")

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    try:
        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)

        # Получаем промпт
        prompt = langfuse.get_prompt(prompt_name, label=label)

        print(f"\n✅ Prompt retrieved successfully!")
        print(f"   Name: {prompt_name}")

        if hasattr(prompt, "version"):
            print(f"   Version: {prompt.version}")

        if hasattr(prompt, "labels"):
            print(f"   Labels: {prompt.labels}")

        if hasattr(prompt, "prompt"):
            print(f"   Prompt length: {len(prompt.prompt)} chars")

        if hasattr(prompt, "config") and prompt.config:
            config = prompt.config
            print(f"\n⚙️  Config:")
            print(f"   Model: {config.get('model', 'N/A')}")
            print(f"   Temperature: {config.get('temperature', 'N/A')}")
            print(f"   Max tokens: {config.get('max_tokens', 'N/A')}")

            # Проверяем response_format
            response_format = config.get("response_format", {})
            if response_format:
                json_schema = response_format.get("json_schema", {})
                if json_schema:
                    schema = json_schema.get("schema", {})
                    properties_count = len(schema.get("properties", {}))
                    required_count = len(schema.get("required", []))

                    print(f"\n📋 JSON Schema:")
                    print(f"   Schema name: {json_schema.get('name')}")
                    print(f"   Properties: {properties_count}")
                    print(f"   Required: {required_count}")

                    # Проверяем согласованность
                    properties_keys = set(schema.get("properties", {}).keys())
                    required_keys = set(schema.get("required", []))

                    if properties_keys == required_keys:
                        print(f"   ✅ Schema valid: All fields consistent")
                    else:
                        print(f"   ⚠️  Schema issues detected!")
                        missing = properties_keys - required_keys
                        if missing:
                            print(f"      Missing in required: {missing}")

        return True

    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="Upload prompt to Langfuse from local files"
    )
    parser.add_argument(
        "--environment",
        "-e",
        default="production",
        choices=["production", "development"],
        help="Environment to upload from (default: production)",
    )
    parser.add_argument(
        "--version", "-v", type=str, help="Version number (default: from metadata)"
    )
    parser.add_argument(
        "--prompt-name",
        "-n",
        default="a101-hr-profile-gemini-v3-simple",
        help="Prompt name in Langfuse",
    )
    parser.add_argument(
        "--labels", "-l", nargs="+", help="Labels to add (default: ['production'])"
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true", help="Dry run - check without upload"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify upload by retrieving from Langfuse",
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Only update config (faster for schema fixes)",
    )

    args = parser.parse_args()

    print(f"\n🏗️  A101 HR Profile Generator - Langfuse Upload")
    print(f"{'='*70}")

    try:
        # Загружаем локальные файлы
        prompt_text, config, metadata = load_local_prompt_files(args.environment)

        print(f"\n✅ Loaded local files from {args.environment}")
        print(f"   Prompt: {len(prompt_text)} chars")
        print(f"   Config keys: {list(config.keys())}")
        print(f"   Metadata: {metadata.get('version', 'unknown')} ({metadata.get('saved_at', 'unknown')})")

        if "config_note" in metadata:
            print(f"   📝 Note: {metadata['config_note']}")

        # Загружаем в Langfuse
        success = upload_to_langfuse(
            prompt_text=prompt_text,
            config=config,
            metadata=metadata,
            prompt_name=args.prompt_name,
            version=args.version,
            labels=args.labels,
            dry_run=args.dry_run,
        )

        # Проверяем загрузку
        if success and args.verify and not args.dry_run:
            verify_success = verify_upload(
                prompt_name=args.prompt_name, label=args.labels[0] if args.labels else "production"
            )

            if not verify_success:
                print(f"\n⚠️  Upload succeeded but verification failed")
                print(f"   Check Langfuse UI manually")

        # Итоговый статус
        if success:
            print(f"\n{'='*70}")
            print(f"🎉 SUCCESS!")
            print(f"{'='*70}")
            print(f"\n📊 Next Steps:")
            print(f"  1. Check prompt in Langfuse UI:")
            print(f"     https://cloud.langfuse.com/project/prompts/{args.prompt_name}")
            print(f"  2. Test generation with updated prompt")
            print(f"  3. Verify JSON schema validation works")
            print(f"\n💡 To sync back to local files:")
            print(f"  python scripts/sync_prompts_from_langfuse.py --verify")
            sys.exit(0)
        else:
            print(f"\n{'='*70}")
            print(f"❌ FAILED")
            print(f"{'='*70}")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Скрипт для тестирования генерации профиля должности.

Использование:
    python scripts/test_generate_profile.py "Главный бухгалтер" "Финансовый департамент"
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.config import config
from backend.core.profile_generator import ProfileGenerator
from backend.core.data_loader import DataLoader
from backend.core.llm_client import LLMClient
from backend.models.database import initialize_db_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def generate_profile(position_title: str, department: str) -> Dict[str, Any]:
    """
    Генерирует профиль должности.

    Args:
        position_title: Название должности
        department: Название департамента

    Returns:
        Информация о сгенерированном профиле
    """
    start_time = time.time()

    logger.info(f"🚀 Начинаем генерацию профиля: {position_title} / {department}")

    # Инициализация компонентов
    logger.info("📦 Инициализация компонентов...")

    # Инициализируем БД для сохранения результатов
    db_manager = initialize_db_manager(config.database_path)
    db_manager.create_schema()

    # ProfileGenerator инициализируется без параметров - получает все из config
    generator = ProfileGenerator()

    logger.info("✅ Компоненты инициализированы")

    # Генерация профиля
    logger.info(f"🔄 Генерация профиля для: {position_title}")

    try:
        result = await generator.generate_profile(
            department=department,
            position=position_title
        )

        generation_time = time.time() - start_time

        logger.info(f"✅ Профиль успешно сгенерирован за {generation_time:.2f} сек")

        return {
            "status": "success",
            "position_title": position_title,
            "department": department,
            "file_path": result.get("file_path", ""),
            "profile_id": result.get("profile_id", ""),
            "generation_time": generation_time,
            "result": result
        }

    except Exception as e:
        logger.error(f"❌ Ошибка генерации профиля: {e}", exc_info=True)
        return {
            "status": "error",
            "position_title": position_title,
            "department": department,
            "error": str(e),
            "generation_time": time.time() - start_time
        }


def analyze_profile_file(file_path: str) -> Dict[str, Any]:
    """
    Анализирует сгенерированный JSON файл профиля.

    Args:
        file_path: Путь к файлу профиля

    Returns:
        Статистика по профилю
    """
    logger.info(f"📊 Анализ файла: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        # Подсчет статистики
        skills_categories = profile.get("skills", [])
        total_skills = sum(len(cat.get("items", [])) for cat in skills_categories)
        category_names = [cat.get("category", "Без названия") for cat in skills_categories]

        responsibilities = profile.get("responsibilities", [])
        total_responsibilities = len(responsibilities)

        # Размер файла
        file_size = Path(file_path).stat().st_size

        return {
            "categories_count": len(skills_categories),
            "total_skills": total_skills,
            "category_names": category_names,
            "responsibilities_count": total_responsibilities,
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 2)
        }

    except Exception as e:
        logger.error(f"❌ Ошибка анализа файла: {e}")
        return {
            "error": str(e)
        }


def print_report(generation_result: Dict[str, Any], stats: Dict[str, Any]) -> None:
    """
    Печатает отчет о генерации профиля.

    Args:
        generation_result: Результат генерации
        stats: Статистика по профилю
    """
    print("\n" + "="*80)
    print(f"ПРОФИЛЬ: {generation_result['position_title']}")
    print(f"ДЕПАРТАМЕНТ: {generation_result['department']}")
    print(f"ПУТЬ: {generation_result.get('file_path', 'N/A')}")

    if generation_result['status'] == 'success':
        print(f"СТАТУС: ✅ Успешно")
    else:
        print(f"СТАТУС: ❌ Ошибка - {generation_result.get('error', 'Unknown')}")
        print("="*80 + "\n")
        return

    print(f"\nСТАТИСТИКА:")
    print(f"- Категорий навыков: {stats.get('categories_count', 0)}")
    print(f"- Навыков всего: {stats.get('total_skills', 0)}")
    print(f"- Областей ответственности: {stats.get('responsibilities_count', 0)}")

    print(f"\nКАТЕГОРИИ НАВЫКОВ:")
    for i, category in enumerate(stats.get('category_names', []), 1):
        print(f"{i}. {category}")

    print(f"\nРАЗМЕР ФАЙЛА: {stats.get('file_size_kb', 0)} KB")
    print(f"ВРЕМЯ ГЕНЕРАЦИИ: {generation_result['generation_time']:.2f} секунд")
    print("="*80 + "\n")


async def main():
    """Основная функция скрипта."""
    if len(sys.argv) < 3:
        print("Использование: python scripts/test_generate_profile.py <должность> <департамент>")
        print('Пример: python scripts/test_generate_profile.py "Главный бухгалтер" "Финансовый департамент"')
        sys.exit(1)

    position_title = sys.argv[1]
    department = sys.argv[2]

    # Генерация профиля
    result = await generate_profile(position_title, department)

    # Анализ файла
    stats = {}
    if result['status'] == 'success' and result.get('file_path'):
        stats = analyze_profile_file(result['file_path'])

    # Печать отчета
    print_report(result, stats)

    # Возврат кода выхода
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == "__main__":
    asyncio.run(main())

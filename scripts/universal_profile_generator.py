#!/usr/bin/env python3
"""
🚀 УНИВЕРСАЛЬНЫЙ ГЕНЕРАТОР ПРОФИЛЕЙ А101 - ULTRATHINK MODE

Интерактивный скрипт для генерации профилей ЛЮБОГО бизнес-юнита в организационной структуре:
- ✅ Выбор из 567 бизнес-единиц (любой уровень: блок → департамент → управление → отдел → группа)
- ✅ Автоматический подсчет всех позиций в выбранном юните + всех дочерних подразделений
- ✅ Интеллектуальная обработка: от 1 позиции (конкретная должность) до 500+ (целый блок)
- ✅ Сохранение иерархической структуры папок в архиве
- ✅ Resume/restart функциональность для больших объемов
- ✅ Полная интеграция с production API pipeline

Архитектурные принципы ULTRATHINK:
1. УНИВЕРСАЛЬНОСТЬ - любой юнит любого уровня
2. ИНТЕЛЛЕКТУАЛЬНОСТЬ - автоматический анализ и подсчет
3. ЭФФЕКТИВНОСТЬ - пакетная обработка с оптимизацией
4. НАДЕЖНОСТЬ - полное восстановление после сбоев
5. ЮЗАБИЛИТИ - интуитивный интерфейс выбора

Usage:
    python scripts/universal_profile_generator.py [--dry-run] [--batch-size N] [--unit-path "Путь/К/Юниту"]
"""

import asyncio
import json
import logging
import os
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import aiohttp
import click
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Добавляем путь к backend модулям
sys.path.append(os.path.abspath('.'))

# Импорты из нашей системы
from backend.core.organization_cache import organization_cache

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/universal_generator.log')
    ]
)
logger = logging.getLogger(__name__)

# Константы
PROGRESS_FILE = "scripts/.universal_generator_progress.json"
API_BASE_URL = "http://localhost:8022"
DEFAULT_BATCH_SIZE = 10
MAX_CONCURRENT = 10
REQUEST_TIMEOUT = 300
POLL_INTERVAL = 5


class BusinessUnitSelector:
    """
    Интеллектуальный селектор бизнес-юнитов с поддержкой всех 567 единиц

    Функции:
    - Интерактивный выбор из полного списка
    - Поиск по названию с auto-complete
    - Отображение иерархии и количества позиций
    - Валидация выбранного юнита
    """

    def __init__(self):
        self.organization_cache = organization_cache
        self.all_units = {}
        self.searchable_items = []

    def load_organization_data(self) -> bool:
        """Загрузка организационных данных"""
        try:
            # Загружаем все бизнес-юниты через path-based индекс
            self.all_units = self.organization_cache.get_all_business_units_with_paths()

            # Получаем searchable items для отображения напрямую из organization_cache
            self.searchable_items = self.organization_cache.get_searchable_items()

            logger.info(f"✅ Loaded {len(self.all_units)} business units for selection")
            return True

        except Exception as e:
            logger.error(f"❌ Error loading organization data: {e}")
            return False

    def display_selection_interface(self) -> Optional[str]:
        """
        Интерактивный интерфейс выбора бизнес-юнита

        Returns:
            Полный путь к выбранному юниту или None
        """
        print("\n🏢 ВЫБОР БИЗНЕС-ЮНИТА ДЛЯ ГЕНЕРАЦИИ ПРОФИЛЕЙ")
        print("=" * 60)
        print(f"📊 Доступно: {len(self.searchable_items)} бизнес-единиц")
        print(f"🎯 Поддержка: от отдельных групп до целых блоков")

        # Группируем по уровням для удобства навигации
        by_levels = self._group_by_levels()

        print("\n📋 ВЫБЕРИТЕ УРОВЕНЬ:")
        print("1. 🏢 Блоки (весь блок целиком)")
        print("2. 🏬 Департаменты")
        print("3. 📋 Управления")
        print("4. 📂 Отделы")
        print("5. 📁 Под-отделы")
        print("6. 👥 Группы")
        print("7. 🔍 Поиск по названию")
        print("0. ❌ Отмена")

        choice = click.prompt("Выберите опцию", type=int, default=7)

        if choice == 0:
            return None
        elif choice == 7:
            return self._search_units()
        elif 1 <= choice <= 6:
            level = choice - 1
            return self._select_from_level(level, by_levels.get(level, []))
        else:
            print("❌ Некорректный выбор")
            return self.display_selection_interface()

    def _group_by_levels(self) -> Dict[int, List[Dict]]:
        """Группировка юнитов по уровням"""
        by_levels = {}

        for item in self.searchable_items:
            level = item["level"]
            if level not in by_levels:
                by_levels[level] = []
            by_levels[level].append(item)

        # Сортируем в каждом уровне
        for level in by_levels:
            by_levels[level].sort(key=lambda x: x["name"])

        return by_levels

    def _select_from_level(self, level: int, units: List[Dict]) -> Optional[str]:
        """Выбор из конкретного уровня"""
        if not units:
            print(f"❌ Нет юнитов на уровне {level + 1}")
            return self.display_selection_interface()

        level_names = ["Блок", "Департамент", "Управление", "Отдел", "Под-отдел", "Группа"]
        level_name = level_names[level] if level < len(level_names) else f"Уровень {level + 1}"

        print(f"\n📋 {level_name.upper()} ({len(units)} доступно):")
        print("-" * 50)

        for i, unit in enumerate(units[:20], 1):  # Показываем первые 20
            positions_text = f"({unit['positions_count']} поз.)" if unit['positions_count'] > 0 else "(нет поз.)"
            headcount_text = f"[{unit.get('headcount', 0)} чел.]" if unit.get('headcount') else ""

            print(f"{i:2d}. {unit['name']} {positions_text} {headcount_text}")
            if unit.get('hierarchy'):
                print(f"     └── {unit['hierarchy']}")

        if len(units) > 20:
            print(f"... и еще {len(units) - 20} юнитов")
            print("Для полного списка используйте поиск (опция 7)")

        print("\n0. ← Вернуться к выбору уровня")

        choice = click.prompt("Выберите номер", type=int, default=0)

        if choice == 0:
            return self.display_selection_interface()
        elif 1 <= choice <= min(20, len(units)):
            selected_unit = units[choice - 1]
            return self._confirm_selection(selected_unit)
        else:
            print("❌ Некорректный номер")
            return self._select_from_level(level, units)

    def _search_units(self) -> Optional[str]:
        """Поиск юнитов по названию"""
        print("\n🔍 ПОИСК БИЗНЕС-ЮНИТОВ")
        print("-" * 30)

        search_term = click.prompt("Введите часть названия для поиска", type=str, default="").strip()

        if not search_term:
            return self.display_selection_interface()

        # Поиск по всем полям
        matches = []
        search_lower = search_term.lower()

        for unit in self.searchable_items:
            if (search_lower in unit['name'].lower() or
                search_lower in unit.get('hierarchy', '').lower() or
                search_lower in unit['display_name'].lower()):
                matches.append(unit)

        if not matches:
            print(f"❌ Ничего не найдено по запросу '{search_term}'")
            return self._search_units()

        print(f"\n📋 РЕЗУЛЬТАТЫ ПОИСКА '{search_term}' ({len(matches)} найдено):")
        print("-" * 50)

        for i, unit in enumerate(matches[:15], 1):  # Показываем первые 15
            positions_text = f"({unit['positions_count']} поз.)" if unit['positions_count'] > 0 else "(нет поз.)"
            level_names = ["Блок", "Департ", "Управл", "Отдел", "П-отд", "Группа"]
            level_text = level_names[unit['level']] if unit['level'] < len(level_names) else f"Ур{unit['level']}"

            print(f"{i:2d}. [{level_text}] {unit['display_name']} {positions_text}")
            print(f"     └── {unit['hierarchy']}")

        if len(matches) > 15:
            print(f"... и еще {len(matches) - 15} результатов")

        print("\n0. ← Новый поиск")

        choice = click.prompt("Выберите номер", type=int, default=0)

        if choice == 0:
            return self._search_units()
        elif 1 <= choice <= min(15, len(matches)):
            selected_unit = matches[choice - 1]
            return self._confirm_selection(selected_unit)
        else:
            print("❌ Некорректный номер")
            return self._search_units()

    def _confirm_selection(self, unit: Dict) -> Optional[str]:
        """Подтверждение выбора юнита"""
        print("\n✅ ВЫБРАННЫЙ БИЗНЕС-ЮНИТ:")
        print("=" * 40)
        print(f"📍 Название: {unit['name']}")
        print(f"🏗️ Полный путь: {unit['full_path']}")
        print(f"📊 Уровень: {unit['level'] + 1} из 6")
        print(f"👥 Позиций в юните: {unit['positions_count']}")

        if unit.get('headcount'):
            print(f"🧑‍💼 Численность: {unit['headcount']} человек")

        # Показываем иерархию
        print(f"🌳 Иерархия: {unit['hierarchy']}")

        # Расчет общего количества позиций с дочерними
        total_positions = self._calculate_total_positions(unit['full_path'])

        if total_positions > unit['positions_count']:
            child_positions = total_positions - unit['positions_count']
            print(f"📈 Всего позиций (с дочерними): {total_positions}")
            print(f"   ├── В выбранном юните: {unit['positions_count']}")
            print(f"   └── В дочерних юнитах: {child_positions}")

        print(f"\n🎯 БУДЕТ СГЕНЕРИРОВАНО: {total_positions} профилей")

        if click.confirm("\nПодтвердить выбор этого бизнес-юнита?"):
            return unit['full_path']
        else:
            return self.display_selection_interface()

    def _calculate_total_positions(self, unit_path: str) -> int:
        """Подсчет общего количества позиций в юните и всех дочерних"""
        total = 0

        # Считаем позиции в самом юните
        unit_data = self.all_units.get(unit_path)
        if unit_data:
            total += len(unit_data.get('positions', []))

        # Рекурсивно считаем позиции в дочерних юнитах
        for path, data in self.all_units.items():
            if path.startswith(unit_path + "/"):  # Это дочерний юнит
                total += len(data.get('positions', []))

        return total


class UniversalPositionsExtractor:
    """
    Универсальный экстрактор позиций из любого бизнес-юнита

    Поддерживает:
    - Извлечение из конкретного юнита
    - Рекурсивное извлечение из всех дочерних
    - Сохранение полных путей департаментов
    - Группировку по подразделениям
    """

    def __init__(self):
        self.organization_cache = organization_cache
        self.all_units = {}

    def load_organization_data(self):
        """Загрузка организационных данных"""
        self.all_units = self.organization_cache.get_all_business_units_with_paths()

    def extract_positions_from_unit(self, unit_path: str, include_children: bool = True) -> List[Tuple[str, str]]:
        """
        Извлечение всех позиций из указанного бизнес-юнита

        Args:
            unit_path: Полный путь к бизнес-юниту
            include_children: Включать ли дочерние подразделения

        Returns:
            List[(department_path, position_name)]
        """
        positions = []

        # Позиции в самом юните
        unit_data = self.all_units.get(unit_path)
        if unit_data:
            for position in unit_data.get('positions', []):
                if position.strip():
                    positions.append((unit_path, position))

        # Позиции в дочерних юнитах (если включено)
        if include_children:
            for path, data in self.all_units.items():
                if path.startswith(unit_path + "/"):  # Это дочерний юнит
                    for position in data.get('positions', []):
                        if position.strip():
                            positions.append((path, position))

        logger.info(f"✅ Извлечено {len(positions)} позиций из {unit_path}" +
                   (f" (с дочерними)" if include_children else ""))

        return positions

    def get_unit_hierarchy_info(self, unit_path: str) -> Dict[str, Any]:
        """Получение детальной информации о юните"""
        unit_data = self.all_units.get(unit_path)
        if not unit_data:
            return {}

        # Считаем дочерние юниты
        children_count = sum(1 for path in self.all_units.keys()
                           if path.startswith(unit_path + "/"))

        return {
            "name": unit_data.get("name"),
            "path": unit_path,
            "level": unit_data.get("level"),
            "positions_count": len(unit_data.get("positions", [])),
            "children_count": children_count,
            "headcount": unit_data.get("headcount"),
        }


class UniversalProgressManager:
    """
    Расширенный менеджер прогресса для любых бизнес-юнитов

    Отличия от оригинала:
    - Хранит информацию о выбранном юните
    - Поддерживает любое количество позиций (от 1 до 1000+)
    - Интеллектуальное восстановление для разных юнитов
    """

    def __init__(self, progress_file: str = PROGRESS_FILE):
        self.progress_file = Path(progress_file)
        self.progress = {
            "selected_unit": None,
            "total_positions": 0,
            "completed_positions": [],
            "failed_positions": [],
            "in_progress": [],
            "started_at": None,
            "last_updated": None,
            "session_id": None,
            "unit_info": {}  # Дополнительная информация о юните
        }

    def set_selected_unit(self, unit_path: str, unit_info: Dict[str, Any]):
        """Установка выбранного бизнес-юнита"""
        self.progress["selected_unit"] = unit_path
        self.progress["unit_info"] = unit_info

    def reset_progress_for_unit(self, unit_path: str, total_positions: int, unit_info: Dict[str, Any]):
        """Сброс прогресса для нового юнита"""
        self.progress = {
            "selected_unit": unit_path,
            "total_positions": total_positions,
            "completed_positions": [],
            "failed_positions": [],
            "in_progress": [],
            "started_at": datetime.now().isoformat(),
            "last_updated": None,
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "unit_info": unit_info
        }
        self.save_progress()

    def print_progress_summary(self):
        """Расширенная сводка прогресса"""
        total = self.progress["total_positions"]
        completed = len(self.progress["completed_positions"])
        failed = len(self.progress["failed_positions"])
        remaining = total - completed - failed

        print(f"\n📊 ПРОГРЕСС ГЕНЕРАЦИИ:")

        if self.progress.get("selected_unit"):
            unit_name = self.progress["unit_info"].get("name", "Unknown")
            print(f"🎯 Выбранный юнит: {unit_name}")
            print(f"📍 Полный путь: {self.progress['selected_unit']}")

        print(f"📈 Всего позиций: {total}")
        print(f"✅ Завершено: {completed}")
        print(f"❌ Ошибки: {failed}")
        print(f"⏳ Осталось: {remaining}")

        if completed > 0 and total > 0:
            percentage = (completed / total) * 100
            print(f"📊 Прогресс: {percentage:.1f}%")

        # Другие методы остаются аналогичными оригиналу...

    def load_progress(self) -> Dict[str, Any]:
        """Загружает прогресс из файла"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    self.progress = json.load(f)
                logger.info(f"📂 Загружен прогресс из {self.progress_file}")
                return self.progress
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки прогресса: {e}")
        return self.progress

    def save_progress(self):
        """Сохраняет текущий прогресс"""
        try:
            self.progress_file.parent.mkdir(exist_ok=True)
            self.progress["last_updated"] = datetime.now().isoformat()

            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)

            logger.debug(f"💾 Прогресс сохранен в {self.progress_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения прогресса: {e}")

    def get_remaining_positions(self, all_positions: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Возвращает позиции которые еще нужно обработать"""
        completed_keys = {
            f"{pos['department']}::{pos['position']}"
            for pos in self.progress["completed_positions"]
        }
        failed_keys = {
            f"{pos['department']}::{pos['position']}"
            for pos in self.progress["failed_positions"]
        }

        remaining = [
            (dept, pos) for dept, pos in all_positions
            if f"{dept}::{pos}" not in completed_keys and f"{dept}::{pos}" not in failed_keys
        ]

        return remaining


class UniversalAPIClient:
    """
    Универсальный HTTP клиент для работы с API generation endpoints

    Адаптирован для работы с любыми путями департаментов из path-based индексации
    """

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None

    async def __aenter__(self):
        # Настраиваем таймауты для разных этапов запроса
        # Используем None для sock_read чтобы не прерывать длительные LLM запросы
        timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT,      # Общий таймаут (300s)
            connect=30,                 # Таймаут на установку соединения
            sock_connect=10,            # Таймаут на сокет
            sock_read=None              # Без таймаута на чтение (для долгих LLM генераций)
        )

        # Настраиваем connector для управления пулом соединений
        connector = aiohttp.TCPConnector(
            limit=100,                  # Максимум одновременных соединений
            limit_per_host=30,          # Максимум соединений на хост
            ttl_dns_cache=300,          # Кэш DNS на 5 минут
            force_close=False,          # Переиспользуем соединения
            enable_cleanup_closed=True  # Очистка закрытых соединений
        )

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            raise_for_status=False      # Обрабатываем статусы вручную
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """Получает JWT токен для аутентификации"""
        try:
            # Получаем учетные данные из .env
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

            # Пробуем аутентификацию через API
            auth_data = {
                "username": admin_username,
                "password": admin_password
            }

            async with self.session.post(f"{self.base_url}/api/auth/login", json=auth_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.auth_token = result.get('access_token')
                    logger.info("🔑 Получен JWT токен через аутентификацию")
                    return True
                else:
                    logger.error(f"❌ Ошибка аутентификации: HTTP {resp.status}")
                    return False

        except Exception as e:
            logger.error(f"❌ Ошибка получения токена: {e}")
            return False

    async def start_generation(self, department_path: str, position: str, max_retries: int = 3) -> Optional[str]:
        """
        Запускает генерацию профиля через API (поддерживает любые пути департаментов)

        Args:
            department_path: Полный путь департамента (может быть любого уровня)
            position: Название должности
            max_retries: Максимальное количество попыток при ошибках

        Returns:
            task_id или None в случае ошибки
        """
        if not self.auth_token:
            logger.error("❌ Нет токена аутентификации")
            return None

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "department": department_path,  # Поддерживаем полные пути
            "position": position,
            "employee_name": f"Сотрудник {position}",
            "temperature": 0.1,
            "save_result": True
        }

        # Retry logic для обработки транзиентных ошибок сети
        for attempt in range(max_retries):
            try:
                async with self.session.post(
                    f"{self.base_url}/api/generation/start",
                    json=payload,
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        task_id = result.get('task_id')
                        logger.info(f"🚀 Запущена генерация: {position} в {department_path} (task: {task_id[:8]}...)")
                        return task_id
                    else:
                        error_text = await resp.text()
                        logger.error(f"❌ Ошибка запуска генерации {position}: HTTP {resp.status} - {error_text}")
                        return None

            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
                # Транзиентные ошибки - повторяем попытку
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"⚠️ Транзиентная ошибка для {position} (попытка {attempt + 1}/{max_retries}): {type(e).__name__}: {e}. "
                        f"Повтор через {wait_time}с..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ Исчерпаны попытки для {position}: {type(e).__name__}: {e}")
                    return None

            except Exception as e:
                # Непредвиденные ошибки - не повторяем
                logger.error(f"❌ Исключение при запуске генерации {position}: {type(e).__name__}: {e}")
                return None

        return None

    async def get_task_status(self, task_id: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Получает статус задачи генерации с retry logic

        Args:
            task_id: ID задачи
            max_retries: Максимальное количество попыток

        Returns:
            Словарь с данными статуса или ошибкой
        """
        if not self.auth_token:
            return {"status": "error", "error": "No auth token"}

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Retry logic для обработки транзиентных ошибок
        for attempt in range(max_retries):
            try:
                async with self.session.get(
                    f"{self.base_url}/api/generation/{task_id}/status",
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        return {"status": "error", "error": f"HTTP {resp.status}: {error_text}"}

            except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
                # Транзиентные ошибки - повторяем попытку
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"⚠️ Ошибка получения статуса задачи {task_id[:8]} (попытка {attempt + 1}/{max_retries}): {type(e).__name__}. "
                        f"Повтор через {wait_time}с..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return {"status": "error", "error": f"Network error after {max_retries} attempts: {str(e)}"}

            except Exception as e:
                return {"status": "error", "error": str(e)}

        return {"status": "error", "error": "Max retries exceeded"}


class UniversalBatchProcessor:
    """
    Универсальный обработчик пакетов для любого объема позиций

    Поддерживает:
    - От 1 до 1000+ позиций
    - Позиции из разных уровней иерархии
    - Интеллектуальное управление нагрузкой
    """

    def __init__(self, api_client: UniversalAPIClient, progress_manager: UniversalProgressManager):
        self.api_client = api_client
        self.progress_manager = progress_manager

    async def process_batch(self, positions_batch: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Обрабатывает пакет позиций из разных департаментов

        Args:
            positions_batch: Список (department_path, position_name)

        Returns:
            {"successful": int, "failed": int, "results": List[Dict]}
        """
        batch_start = time.time()
        logger.info(f"📦 Начинаю обработку пакета из {len(positions_batch)} позиций")

        # Группируем позиции по департаментам для статистики
        departments_in_batch = set()
        for dept_path, pos in positions_batch:
            departments_in_batch.add(dept_path.split('/')[-1])  # Последний компонент пути

        logger.info(f"🏢 Пакет охватывает {len(departments_in_batch)} различных подразделений")

        # 1. Запускаем все задачи параллельно
        logger.info(f"🚀 Запуск {len(positions_batch)} задач параллельно...")

        # Создаем корутины для параллельного запуска
        start_tasks = [
            self.api_client.start_generation(dept_path, pos)
            for dept_path, pos in positions_batch
        ]

        # Запускаем все задачи параллельно
        task_ids = await asyncio.gather(*start_tasks, return_exceptions=True)

        # Формируем список задач с результатами
        tasks = []
        for (dept_path, pos), task_id in zip(positions_batch, task_ids):
            if isinstance(task_id, Exception):
                tasks.append({
                    "task_id": None,
                    "department": dept_path,
                    "position": pos,
                    "status": "failed",
                    "error": f"Failed to start generation: {str(task_id)}"
                })
                logger.error(f"❌ Ошибка запуска: {pos} - {task_id}")
            elif task_id:
                tasks.append({
                    "task_id": task_id,
                    "department": dept_path,
                    "position": pos,
                    "status": "processing",
                    "started_at": time.time()
                })
                logger.info(f"🚀 Запущена генерация: {pos} в {dept_path.split('/')[-1]} (task: {task_id[:8]}...)")
            else:
                tasks.append({
                    "task_id": None,
                    "department": dept_path,
                    "position": pos,
                    "status": "failed",
                    "error": "Failed to start generation"
                })
                logger.error(f"❌ Не удалось запустить: {pos}")

        # 2. Ждем завершения всех задач
        completed_tasks = await self._wait_for_completion(tasks)

        # 3. Обрабатываем результаты
        successful = sum(1 for task in completed_tasks if task["status"] == "completed")
        failed = len(completed_tasks) - successful

        # 4. Обновляем прогресс
        for task in completed_tasks:
            if task["status"] == "completed":
                self.progress_manager.progress["completed_positions"].append({
                    "department": task["department"],
                    "position": task["position"],
                    "task_id": task["task_id"],
                    "completed_at": datetime.now().isoformat()
                })
            else:
                self.progress_manager.progress["failed_positions"].append({
                    "department": task["department"],
                    "position": task["position"],
                    "task_id": task.get("task_id"),
                    "error": task.get("error", "Unknown error"),
                    "failed_at": datetime.now().isoformat()
                })

        self.progress_manager.save_progress()

        batch_time = time.time() - batch_start
        logger.info(f"📦 Пакет завершен за {batch_time:.1f}с: ✅{successful} ❌{failed}")

        return {
            "successful": successful,
            "failed": failed,
            "duration": batch_time,
            "results": completed_tasks,
            "departments_processed": len(departments_in_batch)
        }

    async def _wait_for_completion(self, tasks: List[Dict]) -> List[Dict]:
        """Ждет завершения всех задач в пакете"""
        pending_tasks = [task for task in tasks if task["task_id"] is not None]
        max_wait_time = 600  # 10 минут на задачу максимум

        while pending_tasks:
            # Проверяем статус каждой задачи
            for task in pending_tasks[:]:  # создаем копию для безопасного удаления
                if task["task_id"] is None:
                    continue

                # Проверяем timeout
                if time.time() - task["started_at"] > max_wait_time:
                    task["status"] = "failed"
                    task["error"] = f"Timeout after {max_wait_time}s"
                    pending_tasks.remove(task)
                    continue

                # Получаем статус задачи
                status_result = await self.api_client.get_task_status(task["task_id"])

                if "task" in status_result:
                    api_status = status_result["task"]["status"]
                    task["api_status"] = api_status

                    if api_status == "completed":
                        task["status"] = "completed"
                        pending_tasks.remove(task)
                        logger.info(f"✅ Завершено: {task['position']} ({task['department'].split('/')[-1]})")
                    elif api_status in ["failed", "cancelled"]:
                        task["status"] = "failed"
                        task["error"] = status_result["task"].get("error_message", "API reported failure")
                        pending_tasks.remove(task)
                        logger.error(f"❌ Ошибка: {task['position']} - {task['error']}")
                else:
                    # Ошибка получения статуса, но не критичная
                    logger.debug(f"⚠️ Не удалось получить статус для {task['position']}")

            if pending_tasks:
                logger.info(f"⏳ Ожидание завершения {len(pending_tasks)} задач...")
                await asyncio.sleep(POLL_INTERVAL)

        return tasks


class UniversalArchiveBuilder:
    """
    Интеллектуальный архив билдер для любого выбранного бизнес-юнита

    Особенности:
    - Сохраняет иерархическую структуру выбранного юнита
    - Поддерживает архивы от 1 файла до тысяч
    - Интеллектуальное именование архивов
    """

    @staticmethod
    def create_unit_archive(unit_path: str, unit_name: str) -> bool:
        """
        Создание архива для конкретного бизнес-юнита

        Args:
            unit_path: Полный путь выбранного юнита
            unit_name: Название юнита для архива

        Returns:
            True если архив создан успешно
        """
        try:
            # Создаем имя архива на основе юнита
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_unit_name = unit_name.replace(" ", "_").replace("/", "_")[:50]
            archive_name = f"{safe_unit_name}_Profiles_{timestamp}.zip"

            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)
            archive_path = archive_dir / archive_name

            generated_dir = Path("generated_profiles")
            if not generated_dir.exists():
                logger.error("❌ Директория generated_profiles не найдена")
                return False

            # Находим все файлы, связанные с выбранным юнитом
            unit_files = []
            for root, _, files in os.walk(generated_dir):
                root_path = Path(root)

                # Проверяем что путь содержит компоненты выбранного юнита
                root_str = str(root_path).replace("\\", "/")
                unit_components = [comp.replace(" ", "_") for comp in unit_path.split("/")]

                # Если хотя бы один компонент есть в пути файла
                if any(comp in root_str for comp in unit_components):
                    for file in files:
                        file_path = root_path / file
                        if file_path.suffix.lower() in ['.json', '.md', '.docx']:
                            if file_path.exists() and os.access(file_path, os.R_OK):
                                unit_files.append(file_path)

            if not unit_files:
                logger.warning(f"⚠️ Не найдено файлов для юнита {unit_name}")
                return False

            logger.info(f"📁 Найдено {len(unit_files)} файлов для архива {unit_name}")

            # Создаем архив
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in unit_files:
                    try:
                        # Сохраняем структуру относительно generated_profiles
                        arcname = file_path.relative_to(generated_dir)
                        zipf.write(file_path, arcname)
                        logger.debug(f"📄 Добавлен: {arcname}")
                    except Exception as file_error:
                        logger.error(f"❌ Ошибка добавления файла {file_path}: {file_error}")
                        continue

            # Проверяем результат
            if archive_path.exists():
                archive_size = archive_path.stat().st_size
                size_mb = archive_size / 1024 / 1024

                logger.info(f"✅ Архив создан: {archive_path} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("❌ Архив не был создан")
                return False

        except Exception as e:
            logger.error(f"❌ Ошибка создания архива для {unit_name}: {e}")
            return False


# ОСНОВНЫЕ ФУНКЦИИ СКРИПТА

@click.command()
@click.option('--dry-run', is_flag=True, help='Тестовый запуск без генерации')
@click.option('--batch-size', default=DEFAULT_BATCH_SIZE, help='Размер пакета')
@click.option('--api-url', default=API_BASE_URL, help='URL API сервера')
@click.option('--unit-path', default=None, help='Прямое указание пути к юниту (без интерактивного выбора)')
def main(dry_run: bool, batch_size: int, api_url: str, unit_path: Optional[str]):
    """🚀 Главная функция универсального генератора профилей"""
    return asyncio.run(_main_async(dry_run, batch_size, api_url, unit_path))


async def _main_async(dry_run: bool, batch_size: int, api_url: str, unit_path: Optional[str]):
    """🚀 Асинхронная главная функция универсального генератора"""

    global API_BASE_URL, DEFAULT_BATCH_SIZE
    API_BASE_URL = api_url
    DEFAULT_BATCH_SIZE = batch_size

    # Инициализация компонентов
    selector = BusinessUnitSelector()
    extractor = UniversalPositionsExtractor()
    progress_manager = UniversalProgressManager()

    try:
        print("🚀 УНИВЕРСАЛЬНЫЙ ГЕНЕРАТОР ПРОФИЛЕЙ А101")
        print("=" * 55)
        print("🎯 Возможности: генерация профилей для ЛЮБОГО бизнес-юнита")
        print("📊 Поддержка: от 1 позиции до 1000+ профилей")
        print("🌳 Уровни: блок → департамент → управление → отдел → под-отдел → группа")

        if dry_run:
            print("🧪 РЕЖИМ ТЕСТОВОГО ЗАПУСКА")

        # 1. Загружаем организационные данные
        print("\n📋 Загрузка организационной структуры...")
        if not selector.load_organization_data():
            print("❌ Не удалось загрузить организационные данные")
            return 1

        extractor.load_organization_data()

        # 2. Выбираем бизнес-юнит (интерактивно или через параметр)
        if unit_path:
            selected_unit_path = unit_path
            print(f"📍 Используется указанный путь: {unit_path}")
        else:
            selected_unit_path = selector.display_selection_interface()

        if not selected_unit_path:
            print("❌ Генерация отменена")
            return 0

        # 3. Получаем информацию о выбранном юните
        unit_info = extractor.get_unit_hierarchy_info(selected_unit_path)
        if not unit_info:
            print(f"❌ Не удалось найти информацию о юните: {selected_unit_path}")
            return 1

        # 4. Извлекаем все позиции из юнита
        print(f"\n📋 Извлечение позиций из '{unit_info['name']}'...")
        all_positions = extractor.extract_positions_from_unit(selected_unit_path, include_children=True)

        if not all_positions:
            print(f"❌ В выбранном юните '{unit_info['name']}' нет позиций для генерации")
            return 1

        print(f"✅ Найдено {len(all_positions)} позиций для генерации")

        # 5. Управление прогрессом
        progress_manager.load_progress()
        progress_manager.set_selected_unit(selected_unit_path, unit_info)

        # Проверяем, тот ли юнит в прогрессе
        has_progress = bool(progress_manager.progress.get("completed_positions") or
                          progress_manager.progress.get("failed_positions"))

        same_unit = (progress_manager.progress.get("selected_unit") == selected_unit_path)

        if has_progress and same_unit:
            progress_manager.print_progress_summary()
            if not dry_run:
                restart = click.confirm("Начать генерацию заново? (Нет = продолжить)")
            else:
                restart = True
                print("🧪 Тестовый режим: используется свежий прогресс")
        else:
            restart = True

        if restart:
            progress_manager.reset_progress_for_unit(selected_unit_path, len(all_positions), unit_info)

        # 6. Определяем оставшиеся позиции
        remaining_positions = progress_manager.get_remaining_positions(all_positions)

        if not remaining_positions:
            print("🎉 Все профили уже сгенерированы!")
            if click.confirm("Создать архив?"):
                if UniversalArchiveBuilder.create_unit_archive(selected_unit_path, unit_info['name']):
                    print("✅ Архив успешно создан")
            return 0

        # 7. Интерактивный выбор количества для генерации
        if dry_run:
            profiles_to_generate = min(3, len(remaining_positions))
            print(f"🧪 Тестовый режим: будет обработано {profiles_to_generate} позиций")
        else:
            print(f"\n📝 Доступно для генерации: {len(remaining_positions)} профилей")
            profiles_to_generate = click.prompt(
                f"Сколько профилей сгенерировать сейчас? (максимум {len(remaining_positions)})",
                type=int,
                default=min(batch_size, len(remaining_positions))
            )
            profiles_to_generate = min(max(profiles_to_generate, 1), len(remaining_positions))

        selected_positions = remaining_positions[:profiles_to_generate]

        # 8. Подтверждение генерации
        batches = (len(selected_positions) + batch_size - 1) // batch_size

        print(f"\n🎯 ПЛАН ГЕНЕРАЦИИ:")
        print(f"   🏢 Бизнес-юнит: {unit_info['name']}")
        print(f"   📊 Профилей: {len(selected_positions)}")
        print(f"   📦 Пакетов: {batches} (по {batch_size})")
        print(f"   ⏱️ Примерное время: {len(selected_positions) * 0.75:.0f} мин")

        if dry_run:
            print(f"\n🧪 ТЕСТОВЫЙ РЕЖИМ - СПИСОК ПОЗИЦИЙ:")
            for i, (dept, pos) in enumerate(selected_positions[:10], 1):
                print(f"   {i}. {pos}")
                print(f"      └── в {dept}")
            if len(selected_positions) > 10:
                print(f"   ... и еще {len(selected_positions) - 10} позиций")

            print(f"\n✅ Скрипт готов к генерации {len(selected_positions)} профилей")
            return 0

        if not click.confirm("\nНачать генерацию?"):
            print("❌ Генерация отменена")
            return 0

        # 9. РЕАЛЬНАЯ ГЕНЕРАЦИЯ через универсальную API интеграцию
        async with UniversalAPIClient(api_url) as api_client:
            # Аутентификация
            print("\n🔑 Аутентификация в системе...")
            if not await api_client.authenticate():
                print("❌ Не удалось аутентифицироваться")
                return 1

            print("✅ Аутентификация успешна")

            # Обработка пакетами
            batch_processor = UniversalBatchProcessor(api_client, progress_manager)

            total_successful = 0
            total_failed = 0
            total_departments_processed = set()
            start_time = time.time()

            for i in range(0, len(selected_positions), batch_size):
                batch = selected_positions[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(selected_positions) + batch_size - 1) // batch_size

                print(f"\n📦 ПАКЕТ {batch_num}/{total_batches} ({len(batch)} позиций)")
                print("-" * 50)

                # Показываем какие департаменты в пакете
                batch_departments = set()
                for dept_path, pos in batch:
                    dept_name = dept_path.split('/')[-1]
                    batch_departments.add(dept_name)

                print(f"🏢 Подразделения в пакете: {', '.join(sorted(batch_departments))}")

                batch_result = await batch_processor.process_batch(batch)

                total_successful += batch_result["successful"]
                total_failed += batch_result["failed"]
                total_departments_processed.update(batch_departments)

                print(f"   ✅ Успешно: {batch_result['successful']}")
                print(f"   ❌ Ошибки: {batch_result['failed']}")
                print(f"   🏢 Департаментов: {batch_result.get('departments_processed', 0)}")
                print(f"   ⏱️ Время: {batch_result['duration']:.1f}с")

                # Пауза между пакетами
                if i + batch_size < len(selected_positions):
                    print("⏸️ Пауза между пакетами...")
                    await asyncio.sleep(3)

        # Финальная сводка
        total_time = time.time() - start_time
        print(f"\n🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print(f"   🎯 Бизнес-юнит: {unit_info['name']}")
        print(f"   ✅ Успешно: {total_successful}")
        print(f"   ❌ Ошибок: {total_failed}")
        print(f"   🏢 Обработано департаментов: {len(total_departments_processed)}")
        print(f"   ⏱️ Общее время: {total_time/60:.1f} мин")

        # Показываем обновленный прогресс
        progress_manager.print_progress_summary()

        # Предлагаем создать архив
        if total_successful > 0 and click.confirm("\n📦 Создать ZIP архив?"):
            if UniversalArchiveBuilder.create_unit_archive(selected_unit_path, unit_info['name']):
                print(f"✅ Архив создан для {unit_info['name']}")
            else:
                print("❌ Ошибка создания архива")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Генерация прервана пользователем")
        progress_manager.save_progress()
        return 1
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    # Проверяем зависимости
    try:
        import aiohttp
        import click
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите: pip install aiohttp click")
        sys.exit(1)

    # Запускаем через click
    sys.exit(main())
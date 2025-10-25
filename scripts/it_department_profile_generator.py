#!/usr/bin/env python3
"""
🚀 ГЕНЕРАТОР ПРОФИЛЕЙ ИТ-ДЕПАРТАМЕНТА А101 - ULTRATHINK MODE

Интерактивный скрипт для массовой генерации профилей всех 95 должностей
Департамента информационных технологий с полной интеграцией в production pipeline.

Особенности:
- ✅ Работает с реальными API endpoints
- ✅ 95 уникальных должностей в контексте подразделений
- ✅ Пакетная обработка по 10 с параллелизмом
- ✅ Resume/restart функциональность
- ✅ Создание ZIP архива с сохранением структуры
- ✅ JWT аутентификация
- ✅ Полный pipeline: JSON + MD + DOCX + база данных

Usage:
    python scripts/it_department_profile_generator.py [--dry-run] [--batch-size N]
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
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
import click
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scripts/it_generator.log')
    ]
)
logger = logging.getLogger(__name__)

# Константы
PROGRESS_FILE = "scripts/.it_dept_generator_progress.json"  # Файл для сохранения прогресса генерации
API_BASE_URL = "http://localhost:8022"  # Базовый URL API сервера
STRUCTURE_FILE = "data/structure.json"  # Путь к файлу организационной структуры
IT_DEPT_NAME = "Департамент информационных технологий"  # Название целевого департамента

# Параметры производительности
BATCH_SIZE = 10  # Оптимальный размер пакета для параллельной обработки без перегрузки API
MAX_CONCURRENT = 10  # Максимальное количество одновременных запросов для предотвращения rate limiting
REQUEST_TIMEOUT = 300  # Таймаут запроса в секундах (5 минут для LLM генерации)
POLL_INTERVAL = 5  # Интервал опроса статуса задач в секундах


class ITPositionsExtractor:
    """Извлечение всех позиций ИТ-департамента из structure.json"""

    def __init__(self, structure_file: str = STRUCTURE_FILE):
        self.structure_file = Path(structure_file)
        self.positions = []

    def extract_positions(self) -> List[Tuple[str, str]]:
        """
        Извлекает все позиции с полными путями департаментов

        Returns:
            List[(department_path, position_name)]
        """
        try:
            with open(self.structure_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Находим ИТ-департамент
            it_dept = data['organization']['Блок операционного директора']['children'][IT_DEPT_NAME]

            positions = []

            def extract_recursive(node: Dict, path: str = ""):
                """Рекурсивно извлекает позиции с путями"""
                if 'positions' in node and node['positions']:
                    for position in node['positions']:
                        if position.strip():
                            positions.append((path, position))

                if 'children' in node:
                    for child_name, child_node in node['children'].items():
                        child_path = f"{path}/{child_name}" if path else child_name
                        extract_recursive(child_node, child_path)

            # Начинаем с корня ИТ-департамента
            extract_recursive(it_dept, IT_DEPT_NAME)

            logger.info(f"✅ Извлечено {len(positions)} позиций из {IT_DEPT_NAME}")
            return positions

        except Exception as e:
            logger.error(f"❌ Ошибка извлечения позиций: {e}")
            raise


class ProgressManager:
    """Управление состоянием генерации - resume/restart"""

    def __init__(self, progress_file: str = PROGRESS_FILE):
        self.progress_file = Path(progress_file)
        self.progress = {
            "total_positions": 0,
            "completed_positions": [],
            "failed_positions": [],
            "in_progress": [],
            "started_at": None,
            "last_updated": None,
            "session_id": None
        }

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

    def reset_progress(self, total_positions: int):
        """Сброс прогресса для нового запуска"""
        self.progress = {
            "total_positions": total_positions,
            "completed_positions": [],
            "failed_positions": [],
            "in_progress": [],
            "started_at": datetime.now().isoformat(),
            "last_updated": None,
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        self.save_progress()

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

    def print_progress_summary(self):
        """Выводит сводку по текущему прогрессу"""
        total = self.progress["total_positions"]
        completed = len(self.progress["completed_positions"])
        failed = len(self.progress["failed_positions"])
        in_progress = len(self.progress["in_progress"])
        remaining = total - completed - failed

        print(f"\n📊 ПРОГРЕСС ГЕНЕРАЦИИ ИТ-ДЕПАРТАМЕНТА:")
        print(f"   📈 Всего должностей: {total}")
        print(f"   ✅ Завершено: {completed}")
        print(f"   ❌ Ошибки: {failed}")
        print(f"   🔄 В процессе: {in_progress}")
        print(f"   ⏳ Осталось: {remaining}")

        if self.progress["started_at"]:
            print(f"   🕐 Начато: {self.progress['started_at']}")
        if self.progress["session_id"]:
            print(f"   🔖 Сессия: {self.progress['session_id']}")


class APIClient:
    """HTTP клиент для работы с API endpoints системы"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
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

    async def start_generation(self, department: str, position: str) -> Optional[str]:
        """
        Запускает генерацию профиля через API

        Returns:
            task_id или None в случае ошибки
        """
        if not self.auth_token:
            logger.error("❌ Нет токена аутентификации")
            return None

        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "department": department,
            "position": position,
            "employee_name": f"Сотрудник {position}",
            "temperature": 0.1,
            "save_result": True
        }

        try:
            async with self.session.post(
                f"{self.base_url}/api/generation/start",
                json=payload,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    task_id = result.get('task_id')
                    logger.info(f"🚀 Запущена генерация: {position} в {department} (task: {task_id[:8]}...)")
                    return task_id
                else:
                    error_text = await resp.text()
                    logger.error(f"❌ Ошибка запуска генерации {position}: HTTP {resp.status} - {error_text}")
                    return None

        except Exception as e:
            logger.error(f"❌ Исключение при запуске генерации {position}: {e}")
            return None

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Получает статус задачи генерации"""
        if not self.auth_token:
            return {"status": "error", "error": "No auth token"}

        headers = {"Authorization": f"Bearer {self.auth_token}"}

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

        except Exception as e:
            return {"status": "error", "error": str(e)}


class BatchProcessor:
    """Обработчик пакетов по 10 позиций с параллелизмом"""

    def __init__(self, api_client: APIClient, progress_manager: ProgressManager):
        self.api_client = api_client
        self.progress_manager = progress_manager

    async def process_batch(self, positions_batch: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Обрабатывает пакет позиций

        Returns:
            {"successful": int, "failed": int, "results": List[Dict]}
        """
        batch_start = time.time()
        logger.info(f"📦 Начинаю обработку пакета из {len(positions_batch)} позиций")

        # 1. Запускаем все задачи параллельно
        tasks = []
        for dept, pos in positions_batch:
            task_id = await self.api_client.start_generation(dept, pos)
            if task_id:
                tasks.append({
                    "task_id": task_id,
                    "department": dept,
                    "position": pos,
                    "status": "processing",
                    "started_at": time.time()
                })
            else:
                tasks.append({
                    "task_id": None,
                    "department": dept,
                    "position": pos,
                    "status": "failed",
                    "error": "Failed to start generation"
                })

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
            "results": completed_tasks
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
                        logger.info(f"✅ Завершено: {task['position']}")
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


class ArchiveBuilder:
    """Создание ZIP архива с сохранением структуры папок"""

    @staticmethod
    def create_archive(archive_path: str) -> bool:
        """
        Создает ZIP архив всех профилей ИТ-департамента

        Args:
            archive_path: Путь к создаваемому архиву

        Returns:
            True если архив создан успешно
        """
        try:
            # Используем локальную папку archive для архива
            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)

            # Создаем полный путь к архиву в локальной директории
            safe_archive_path = archive_dir / Path(archive_path).name

            generated_dir = Path("generated_profiles")
            if not generated_dir.exists():
                logger.error("❌ Директория generated_profiles не найдена")
                return False

            # Находим все файлы ИТ-департамента
            it_files = []
            for root, _, files in os.walk(generated_dir):
                root_path = Path(root)

                # Проверяем что это файлы ИТ-департамента
                if IT_DEPT_NAME.replace(" ", "_") in str(root_path):
                    for file in files:
                        file_path = root_path / file
                        if file_path.suffix.lower() in ['.json', '.md', '.docx']:
                            # Проверяем доступность файла перед добавлением
                            try:
                                if file_path.exists() and os.access(file_path, os.R_OK):
                                    it_files.append(file_path)
                                else:
                                    logger.warning(f"⚠️ Файл недоступен для чтения: {file_path}")
                            except (FileNotFoundError, PermissionError) as e:
                                logger.warning(f"⚠️ Ошибка доступа к файлу {file_path}: {e}")
                            except OSError as e:
                                logger.warning(f"⚠️ OS ошибка при проверке файла {file_path}: {e}")
                            except Exception as e:
                                logger.exception(f"⚠️ Неожиданная ошибка при проверке файла {file_path}: {e}")

            if not it_files:
                logger.warning("⚠️ Не найдено доступных файлов ИТ-департамента для архивирования")
                return False

            logger.info(f"📁 Найдено {len(it_files)} файлов для архива")

            # Создаем архив с сохранением структуры в безопасной директории
            with zipfile.ZipFile(safe_archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in it_files:
                    try:
                        # Сохраняем относительную структуру от generated_profiles
                        arcname = file_path.relative_to(generated_dir)
                        zipf.write(file_path, arcname)
                        logger.debug(f"📄 Добавлен: {arcname}")
                    except Exception as file_error:
                        logger.error(f"❌ Ошибка добавления файла {file_path}: {file_error}")
                        continue

            # Проверяем размер архива
            if safe_archive_path.exists():
                archive_size = safe_archive_path.stat().st_size
                size_mb = archive_size / 1024 / 1024

                logger.info(f"✅ Архив создан: {safe_archive_path} ({size_mb:.2f} MB)")
                return True
            else:
                logger.error("❌ Архив не был создан")
                return False

        except PermissionError as perm_error:
            logger.error(f"❌ Ошибка прав доступа при создании архива: {perm_error}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка создания архива: {e}")
            return False


class InteractiveInterface:
    """CLI интерфейс для интерактивной работы"""

    @staticmethod
    def print_header():
        """Выводит заголовок программы"""
        print("🚀 ГЕНЕРАТОР ПРОФИЛЕЙ ИТ-ДЕПАРТАМЕНТА А101")
        print("=" * 55)
        print(f"📊 Цель: генерация всех позиций департамента '{IT_DEPT_NAME}'")
        print(f"🔧 API: {API_BASE_URL}")
        print(f"📦 Пакеты по: {BATCH_SIZE} позиций")
        print()

    @staticmethod
    def ask_restart_choice(has_previous_progress: bool) -> bool:
        """
        Спрашивает пользователя о restart/resume

        Returns:
            True если нужно начать с начала, False - продолжить
        """
        if not has_previous_progress:
            return True

        print("🔍 Найден предыдущий прогресс генерации.")
        choice = click.confirm("Начать с самого начала? (Нет = продолжить с места остановки)")

        if choice:
            print("🔄 Прогресс будет сброшен. Начинаем с начала.")
        else:
            print("▶️ Продолжаем с места остановки.")

        return choice

    @staticmethod
    def ask_batch_size(max_available: int, default_size: int = BATCH_SIZE) -> int:
        """
        Спрашивает сколько профилей сгенерировать сейчас

        Returns:
            Количество профилей для генерации
        """
        print(f"\n📝 Доступно для генерации: {max_available} профилей")

        profiles_count = click.prompt(
            f"Сколько профилей сгенерировать сейчас? (максимум {max_available})",
            type=int,
            default=min(default_size, max_available)
        )

        return min(max(profiles_count, 1), max_available)

    @staticmethod
    def confirm_generation(count: int, batch_size: int) -> bool:
        """Подтверждение начала генерации"""
        batches = (count + batch_size - 1) // batch_size
        print(f"\n🎯 План генерации:")
        print(f"   📊 Профилей: {count}")
        print(f"   📦 Пакетов: {batches} (по {batch_size})")
        print(f"   ⏱️ Примерное время: {count * 0.75:.0f} мин")

        return click.confirm("Начать генерацию?")


@click.command()
@click.option('--dry-run', is_flag=True, help='Тестовый запуск без реальной генерации')
@click.option('--batch-size', default=BATCH_SIZE, help='Размер пакета')
@click.option('--api-url', default=API_BASE_URL, help='URL API сервера')
def main(dry_run: bool, batch_size: int, api_url: str):
    """🚀 Главная функция генератора профилей ИТ-департамента"""
    return asyncio.run(_main_async(dry_run, batch_size, api_url))


async def _main_async(dry_run: bool, batch_size: int, api_url: str):
    """
    🚀 Главная функция генератора профилей ИТ-департамента
    """
    # Обновляем глобальные константы
    global API_BASE_URL, BATCH_SIZE
    API_BASE_URL = api_url
    BATCH_SIZE = batch_size

    # Инициализация компонентов
    positions_extractor = ITPositionsExtractor()
    progress_manager = ProgressManager()
    interface = InteractiveInterface()

    try:
        # Показываем заголовок
        interface.print_header()

        if dry_run:
            print("🧪 РЕЖИМ ТЕСТОВОГО ЗАПУСКА")
            print()

        # Извлекаем все позиции ИТ-департамента
        print("📋 Извлекаю позиции из организационной структуры...")
        all_positions = positions_extractor.extract_positions()

        if not all_positions:
            print("❌ Не удалось извлечь позиции ИТ-департамента")
            return 1

        print(f"✅ Найдено {len(all_positions)} уникальных позиций")

        # Загружаем прогресс
        progress_manager.load_progress()
        progress_manager.progress["total_positions"] = len(all_positions)

        # Показываем текущий прогресс
        progress_manager.print_progress_summary()

        # Интерактивные вопросы
        has_progress = bool(progress_manager.progress["completed_positions"] or
                          progress_manager.progress["failed_positions"])

        if dry_run:
            restart = True  # В dry-run всегда начинаем с чистого листа
            print("🧪 Тестовый режим: используется свежий прогресс")
        else:
            restart = interface.ask_restart_choice(has_progress)

        if restart:
            progress_manager.reset_progress(len(all_positions))

        # Определяем оставшиеся позиции
        remaining_positions = progress_manager.get_remaining_positions(all_positions)

        if not remaining_positions:
            print("🎉 Все профили уже сгенерированы!")
            if click.confirm("Создать архив?"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = f"IT_Department_Profiles_{timestamp}.zip"
                if ArchiveBuilder.create_archive(archive_path):
                    safe_path = Path("archive") / archive_path
                    print(f"✅ Архив создан: {safe_path}")
            return 0

        # Спрашиваем сколько генерировать (в dry-run используем минимум)
        if dry_run:
            profiles_to_generate = min(5, len(remaining_positions))
            print(f"🧪 Тестовый режим: будет обработано {profiles_to_generate} позиций")
        else:
            profiles_to_generate = interface.ask_batch_size(len(remaining_positions), batch_size)

        selected_positions = remaining_positions[:profiles_to_generate]

        # Подтверждение (в dry-run автоматически yes)
        if not dry_run and not interface.confirm_generation(len(selected_positions), batch_size):
            print("❌ Генерация отменена")
            return 0

        if dry_run:
            print(f"\n🧪 ТЕСТОВЫЙ РЕЖИМ - ПРОВЕРКА ПОЗИЦИЙ:")
            print(f"   📊 Позиций к обработке: {len(selected_positions)}")
            for i, (dept, pos) in enumerate(selected_positions, 1):
                print(f"   {i}. {pos}")
                print(f"      └── в {dept}")
            print(f"\n✅ Скрипт готов к реальной генерации {len(selected_positions)} позиций")
            return 0

        # Реальная генерация
        async with APIClient(api_url) as api_client:
            # Аутентификация
            print("\n🔑 Аутентификация в системе...")
            if not await api_client.authenticate():
                print("❌ Не удалось аутентифицироваться")
                return 1

            print("✅ Аутентификация успешна")

            # Обработка пакетами
            batch_processor = BatchProcessor(api_client, progress_manager)

            total_successful = 0
            total_failed = 0
            start_time = time.time()

            for i in range(0, len(selected_positions), batch_size):
                batch = selected_positions[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(selected_positions) + batch_size - 1) // batch_size

                print(f"\n📦 ПАКЕТ {batch_num}/{total_batches} ({len(batch)} позиций)")
                print("-" * 50)

                batch_result = await batch_processor.process_batch(batch)

                total_successful += batch_result["successful"]
                total_failed += batch_result["failed"]

                print(f"   ✅ Успешно: {batch_result['successful']}")
                print(f"   ❌ Ошибки: {batch_result['failed']}")
                print(f"   ⏱️ Время: {batch_result['duration']:.1f}с")

                # Пауза между пакетами
                if i + batch_size < len(selected_positions):
                    print("⏸️ Пауза между пакетами...")
                    await asyncio.sleep(3)

        # Финальная сводка
        total_time = time.time() - start_time
        print(f"\n🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print(f"   ✅ Успешно: {total_successful}")
        print(f"   ❌ Ошибок: {total_failed}")
        print(f"   ⏱️ Общее время: {total_time/60:.1f} мин")

        progress_manager.print_progress_summary()

        # Предлагаем создать архив
        if total_successful > 0 and click.confirm("\n📦 Создать ZIP архив?"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = f"IT_Department_Profiles_{timestamp}.zip"
            if ArchiveBuilder.create_archive(archive_path):
                safe_path = Path("archive") / archive_path
                print(f"✅ Архив создан: {safe_path}")
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
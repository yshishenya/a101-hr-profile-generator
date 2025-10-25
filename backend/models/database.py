"""
SQLite модели базы данных для системы генерации профилей А101.

Структура базы данных:
- profiles: Сгенерированные профили должностей
- generation_tasks: Асинхронные задачи генерации
- generation_history: История всех генераций
- organization_cache: Кеш организационной структуры
- users: Пользователи системы (простая аутентификация)
- user_sessions: Активные сессии пользователей

Thread Safety:
- Uses threading.local() for per-thread connections
- Each thread gets its own SQLite connection
- Prevents "SQLite objects created in a thread can only be used in that same thread" errors
"""

import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import logging
import uuid

# Импорт будет после определения класса DatabaseManager, чтобы избежать циклических импортов
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    @doc Менеджер базы данных SQLite с thread-safe connection pooling.

    Uses threading.local() to maintain separate connections per thread.
    This prevents "SQLite objects created in a thread can only be used in that same thread" errors.

    Examples:
        python>
        # Usage in multi-threaded environment
        db = DatabaseManager("data/profiles.db")
        conn = db.get_connection()  # Each thread gets its own connection
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")

    Thread Safety:
        - Each thread gets its own SQLite connection
        - No check_same_thread=False needed
        - Connections are properly isolated
        - Thread-local storage prevents race conditions
    """

    def __init__(self, db_path: str):
        """
        Инициализация DatabaseManager с dependency injection конфигурации.

        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Use threading.local() for per-thread connections
        self._local = threading.local()

    def get_connection(self) -> sqlite3.Connection:
        """
        @doc Получение соединения с базой данных (thread-safe).

        Each thread gets its own connection stored in threading.local().
        This ensures thread safety without check_same_thread=False.

        Examples:
            python>
            # Thread 1
            conn1 = db.get_connection()  # Gets connection for thread 1

            # Thread 2
            conn2 = db.get_connection()  # Gets different connection for thread 2

            # conn1 != conn2, thread-safe!

        Returns:
            sqlite3.Connection for current thread
        """
        # Check if this thread already has a connection
        if not hasattr(self._local, "connection") or self._is_connection_closed():
            logger.debug(
                f"Creating new database connection for thread {threading.current_thread().name}"
            )

            # Close old connection if exists
            if hasattr(self._local, "connection") and self._local.connection:
                try:
                    self._local.connection.close()
                except:
                    pass  # Ignore errors when closing dead connection

            # Create new connection for this thread
            # NOTE: check_same_thread=True (default) is now safe because each thread has its own connection
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=True,  # FIXED: Now using True for thread safety
                timeout=30.0,
            )
            self._local.connection.row_factory = sqlite3.Row  # Для dict-like доступа
            self._local.connection.execute(
                "PRAGMA foreign_keys = ON"
            )  # Включаем foreign keys
            logger.debug(
                f"Database connection created for thread {threading.current_thread().name}"
            )

        return self._local.connection

    def _is_connection_closed(self) -> bool:
        """Проверка, закрыто ли соединение с базой данных для текущего потока"""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            return True
        try:
            # Простой запрос для проверки соединения
            self._local.connection.execute("SELECT 1").fetchone()
            return False
        except sqlite3.Error:
            logger.warning(
                f"Database connection is closed or invalid for thread {threading.current_thread().name}"
            )
            return True

    def close_connection(self):
        """Закрытие соединения с базой данных для текущего потока"""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            logger.debug(
                f"Closed database connection for thread {threading.current_thread().name}"
            )

    def close_all_connections(self):
        """
        @doc Закрытие всех thread-local соединений.

        WARNING: This should only be called during application shutdown.
        Cannot iterate over threading.local() objects directly.

        Examples:
            python>
            # During application shutdown
            db.close_all_connections()
        """
        # Note: Cannot iterate over threading.local() objects
        # Each thread must close its own connection
        logger.info("Application shutdown - threads will close their own connections")
        if hasattr(self._local, "connection") and self._local.connection:
            try:
                self._local.connection.close()
                logger.debug("Closed main thread database connection")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

    def create_schema(self):
        """Создание полной схемы базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Таблица пользователей (простая аутентификация)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            """
            )

            # 2. Таблица сессий пользователей
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,  -- UUID4 session ID
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    user_agent TEXT,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """
            )

            # 3. Таблица сгенерированных профилей
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,  -- UUID4
                    department TEXT NOT NULL,
                    position TEXT NOT NULL,
                    employee_name TEXT,

                    -- JSON данные профиля
                    profile_data TEXT NOT NULL,  -- JSON профиля
                    metadata_json TEXT NOT NULL,  -- Метаданные генерации

                    -- Метрики генерации
                    generation_time_seconds REAL NOT NULL,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,

                    -- Качество профиля
                    validation_score REAL DEFAULT 0.0,  -- 0.0 - 1.0
                    completeness_score REAL DEFAULT 0.0,  -- 0.0 - 1.0

                    -- Системные поля
                    created_by INTEGER,  -- User ID
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    -- Статус
                    status TEXT DEFAULT 'completed',  -- completed, failed, processing

                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """
            )

            # 4. Таблица асинхронных задач генерации
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS generation_tasks (
                    id TEXT PRIMARY KEY,  -- UUID4 task ID

                    -- Параметры генерации
                    department TEXT NOT NULL,
                    position TEXT NOT NULL,
                    employee_name TEXT,
                    generation_params TEXT,  -- JSON с дополнительными параметрами

                    -- Статус задачи
                    status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed, cancelled
                    progress INTEGER DEFAULT 0,  -- 0-100
                    current_step TEXT,  -- Текущий шаг выполнения

                    -- Результат
                    result_profile_id TEXT,  -- Ссылка на profiles.id при успехе
                    error_message TEXT,

                    -- Временные метки
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME,
                    completed_at DATETIME,

                    -- Пользователь
                    created_by INTEGER,

                    FOREIGN KEY (created_by) REFERENCES users (id),
                    FOREIGN KEY (result_profile_id) REFERENCES profiles (id)
                )
            """
            )

            # 5. История всех генераций (для аналитики)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS generation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    -- Что генерировали
                    department TEXT NOT NULL,
                    position TEXT NOT NULL,
                    employee_name TEXT,

                    -- Как генерировали
                    generation_type TEXT NOT NULL,  -- sync, async
                    status TEXT NOT NULL,  -- success, failed, cancelled

                    -- Метрики
                    generation_time_seconds REAL,
                    tokens_used INTEGER DEFAULT 0,

                    -- Результат
                    profile_id TEXT,  -- Ссылка на profiles.id если успешно
                    error_type TEXT,  -- Тип ошибки если неуспешно

                    -- Системные поля
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (created_by) REFERENCES users (id),
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            """
            )

            # 6. Кеш организационной структуры (для оптимизации)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS organization_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT NOT NULL UNIQUE,  -- department_name или другой ключ
                    cache_type TEXT NOT NULL,  -- department_structure, kpi_mapping, positions

                    -- Данные
                    data_json TEXT NOT NULL,

                    -- Кеш метаданные
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    access_count INTEGER DEFAULT 0,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Создание индексов для оптимизации запросов
            self._create_indexes(cursor)

            # Создание представлений для удобного доступа
            self._create_views(cursor)

            conn.commit()
            logger.info("✅ Схема базы данных создана успешно")

        except Exception as e:
            logger.error(f"❌ Ошибка создания схемы БД: {e}")
            conn.rollback()
            raise

    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Создание индексов для оптимизации производительности"""
        indexes = [
            # Индексы для profiles
            "CREATE INDEX IF NOT EXISTS idx_profiles_department ON profiles (department)",
            "CREATE INDEX IF NOT EXISTS idx_profiles_position ON profiles (position)",
            "CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_profiles_status ON profiles (status)",
            "CREATE INDEX IF NOT EXISTS idx_profiles_created_by ON profiles (created_by)",
            # Индексы для generation_tasks
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON generation_tasks (status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON generation_tasks (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON generation_tasks (created_by)",
            # Индексы для generation_history
            "CREATE INDEX IF NOT EXISTS idx_history_department ON generation_history (department)",
            "CREATE INDEX IF NOT EXISTS idx_history_created_at ON generation_history (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_history_status ON generation_history (status)",
            # Индексы для user_sessions
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions (expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON user_sessions (is_active)",
            # Индексы для organization_cache
            "CREATE INDEX IF NOT EXISTS idx_cache_key ON organization_cache (cache_key)",
            "CREATE INDEX IF NOT EXISTS idx_cache_type ON organization_cache (cache_type)",
            "CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON organization_cache (expires_at)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

    def _create_views(self, cursor: sqlite3.Cursor):
        """Создание представлений для удобного доступа к данным"""

        # Представление для полной информации о профилях с пользователем
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS profile_details AS
            SELECT
                p.*,
                u.username as created_by_username,
                u.full_name as created_by_full_name
            FROM profiles p
            LEFT JOIN users u ON p.created_by = u.id
        """
        )

        # Представление для статистики генераций
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS generation_stats AS
            SELECT
                DATE(created_at) as date,
                department,
                COUNT(*) as total_generations,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_generations,
                AVG(CASE WHEN status = 'completed' THEN generation_time_seconds END) as avg_generation_time,
                SUM(total_tokens) as total_tokens_used
            FROM profiles
            GROUP BY DATE(created_at), department
            ORDER BY date DESC, department
        """
        )

    def seed_initial_data(
        self,
        admin_username: str = None,
        admin_password: str = None,
        admin_full_name: str = "System Administrator",
        hr_username: str = None,
        hr_password: str = None,
        hr_full_name: str = "HR Manager",
    ):
        """
        Создание начальных данных для системы с dependency injection параметров.

        Args:
            admin_username: Имя пользователя администратора
            admin_password: Пароль администратора
            admin_full_name: Полное имя администратора
            hr_username: Имя пользователя HR
            hr_password: Пароль HR
            hr_full_name: Полное имя HR пользователя
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Проверяем, есть ли уже пользователи
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            if user_count == 0:
                # Создаем пользователей только если их нет
                import hashlib
                from passlib.context import CryptContext

                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

                # Use double hashing (SHA256 + bcrypt) to avoid 72-byte truncation
                # This matches AuthService._prehash_password() implementation
                admin_password_plain = admin_password if admin_password else "admin123"
                hr_password_plain = hr_password if hr_password else "hr123"

                # Pre-hash with SHA256 (same as AuthService)
                admin_password_prehashed = hashlib.sha256(
                    admin_password_plain.encode("utf-8")
                ).hexdigest()
                hr_password_prehashed = hashlib.sha256(
                    hr_password_plain.encode("utf-8")
                ).hexdigest()

                # Hash with bcrypt
                admin_password_hash = pwd_context.hash(admin_password_prehashed)
                hr_password_hash = pwd_context.hash(hr_password_prehashed)

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, full_name, is_active)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        admin_username,
                        admin_password_hash,
                        admin_full_name,
                        True,
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, full_name, is_active)
                    VALUES (?, ?, ?, ?)
                """,
                    (hr_username, hr_password_hash, hr_full_name, True),
                )

                conn.commit()
                logger.info(
                    f"✅ Начальные данные созданы ({admin_username}, {hr_username})"
                )
            else:
                logger.info("ℹ️ Пользователи уже существуют, пропускаем создание")

        except Exception as e:
            logger.error(f"❌ Ошибка создания начальных данных: {e}")
            conn.rollback()
            raise


# Глобальный экземпляр менеджера БД (инициализируется в main.py)
db_manager: Optional[DatabaseManager] = None


def initialize_db_manager(database_path: str) -> DatabaseManager:
    """
    Инициализация глобального экземпляра DatabaseManager.

    Вызывается из main.py для dependency injection конфигурации.

    Args:
        database_path: Путь к файлу базы данных

    Returns:
        Инициализированный экземпляр DatabaseManager
    """
    global db_manager
    db_manager = DatabaseManager(database_path)
    return db_manager


def get_db_manager() -> DatabaseManager:
    """
    Получение глобального экземпляра DatabaseManager.

    Returns:
        Глобальный экземпляр DatabaseManager

    Raises:
        RuntimeError: Если db_manager не был инициализирован
    """
    if db_manager is None:
        raise RuntimeError(
            "DatabaseManager not initialized. Call initialize_db_manager() first."
        )
    return db_manager


if __name__ == "__main__":
    # Тестирование создания схемы
    logging.basicConfig(level=logging.INFO)

    print("🗄️ Создание схемы базы данных...")
    db_manager.create_schema()

    print("🌱 Создание начальных данных...")
    db_manager.seed_initial_data()

    print("✅ База данных готова к использованию!")
    print(f"📍 Путь к БД: {db_manager.db_path}")

    # Проверим созданные таблицы
    conn = db_manager.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print("📋 Созданные таблицы:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} записей")

    db_manager.close_connection()

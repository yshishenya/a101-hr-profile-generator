"""
SQLite модели базы данных для системы генерации профилей А101.

Структура базы данных:
- profiles: Сгенерированные профили должностей
- generation_tasks: Асинхронные задачи генерации
- generation_history: История всех генераций
- organization_cache: Кеш организационной структуры
- users: Пользователи системы (простая аутентификация)
- user_sessions: Активные сессии пользователей
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import logging
import uuid

# Импорт будет после определения класса DatabaseManager, чтобы избежать циклических импортов
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер базы данных SQLite с методами для создания схемы и управления соединениями"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Импорт здесь, чтобы избежать циклических импортов
            from ..core.config import config

            db_path = config.database_path

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None

    def get_connection(self) -> sqlite3.Connection:
        """Получение соединения с базой данных"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path), check_same_thread=False, timeout=30.0
            )
            self._connection.row_factory = sqlite3.Row  # Для dict-like доступа
            self._connection.execute(
                "PRAGMA foreign_keys = ON"
            )  # Включаем foreign keys

        return self._connection

    def close_connection(self):
        """Закрытие соединения с базой данных"""
        if self._connection:
            self._connection.close()
            self._connection = None

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

    def seed_initial_data(self):
        """Создание начальных данных для системы"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Проверяем, есть ли уже пользователи
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

            if user_count == 0:
                # Создаем пользователей только если их нет
                from passlib.context import CryptContext
                from ..core.config import config

                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

                admin_password_hash = pwd_context.hash(config.ADMIN_PASSWORD)
                hr_password_hash = pwd_context.hash(config.HR_PASSWORD)

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, full_name, is_active)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        config.ADMIN_USERNAME,
                        admin_password_hash,
                        config.ADMIN_FULL_NAME,
                        True,
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, full_name, is_active)
                    VALUES (?, ?, ?, ?)
                """,
                    (config.HR_USERNAME, hr_password_hash, config.HR_FULL_NAME, True),
                )

                conn.commit()
                logger.info(
                    f"✅ Начальные данные созданы ({config.ADMIN_USERNAME}, {config.HR_USERNAME})"
                )
            else:
                logger.info("ℹ️ Пользователи уже существуют, пропускаем создание")

        except Exception as e:
            logger.error(f"❌ Ошибка создания начальных данных: {e}")
            conn.rollback()
            raise


# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()


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

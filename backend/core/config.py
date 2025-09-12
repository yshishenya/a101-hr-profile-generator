"""
Конфигурация приложения A101 HR Profile Generator.

Централизованное управление всеми настройками через environment variables.
Все настройки загружаются из .env файла или переменных окружения.
"""

import os
from typing import Optional
from pathlib import Path

# # Загружаем переменные из .env файла
# try:
#     from dotenv import load_dotenv

#     # Ищем .env файл в корне проекта
#     env_path = Path(__file__).parent.parent.parent / ".env"
#     if env_path.exists():
#         load_dotenv(env_path)
#         print(f"✅ Loaded environment from: {env_path}")
#     else:
#         print(f"⚠️  .env file not found at: {env_path}")

# except ImportError:
#     print("📦 python-dotenv not installed, using system environment variables only")


class Config:
    """Конфигурация приложения A101 HR."""

    # =============================================================================
    # Основные настройки приложения
    # =============================================================================

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = ENVIRONMENT == "development"

    # =============================================================================
    # Пути приложения
    # =============================================================================

    BASE_DATA_PATH: str = os.getenv("BASE_DATA_PATH", "/app")

    # =============================================================================
    # База данных
    # =============================================================================

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/profiles.db")

    # Извлекаем путь для SQLite
    @property
    def database_path(self) -> str:
        """Путь к файлу базы данных SQLite."""
        if self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL.replace("sqlite:///", "")
        return "data/profiles.db"  # fallback

    # =============================================================================
    # JWT Authentication
    # =============================================================================

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "a101-hr-profile-generator-secret-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )  # 24 hours

    # =============================================================================
    # Default User Credentials (для инициализации БД)
    # =============================================================================

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_FULL_NAME: str = os.getenv("ADMIN_FULL_NAME", "Администратор системы")

    HR_USERNAME: str = os.getenv("HR_USERNAME", "hr")
    HR_PASSWORD: str = os.getenv("HR_PASSWORD", "hr123")
    HR_FULL_NAME: str = os.getenv("HR_FULL_NAME", "HR специалист")

    # =============================================================================
    # OpenRouter API (LLM)
    # =============================================================================

    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = os.getenv(
        "OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free"
    )
    OPENROUTER_BASE_URL: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )

    @property
    def openrouter_configured(self) -> bool:
        """Проверка, настроен ли OpenRouter API."""
        return bool(self.OPENROUTER_API_KEY)

    # =============================================================================
    # Langfuse (мониторинг)
    # =============================================================================

    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    @property
    def langfuse_configured(self) -> bool:
        """Проверка, настроен ли Langfuse."""
        return bool(self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY)

    # =============================================================================
    # FastAPI настройки
    # =============================================================================

    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8022"))

    # CORS origins
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:8033,http://127.0.0.1:8033"
    ).split(",")

    # Trusted hosts для middleware
    TRUSTED_HOSTS: list = os.getenv(
        "TRUSTED_HOSTS", "localhost,127.0.0.1,0.0.0.0,49.12.122.181"
    ).split(",")

    # =============================================================================
    # Пути к данным
    # =============================================================================

    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    TEMPLATES_DIR: str = os.getenv("TEMPLATES_DIR", "templates")
    GENERATED_PROFILES_DIR: str = os.getenv(
        "GENERATED_PROFILES_DIR", "generated_profiles"
    )
    LOGS_DIR: str = os.getenv("LOGS_DIR", "logs")
    STATIC_DIR: str = os.getenv("STATIC_DIR", "backend/static")

    # =============================================================================
    # Валидация конфигурации
    # =============================================================================

    def validate(self) -> bool:
        """Валидация критически важных настроек."""
        issues = []
        critical_issues = []

        # Критическая проверка: JWT секрет
        if len(self.JWT_SECRET_KEY) < 32:
            critical_issues.append(
                "❌ КРИТИЧНО: JWT_SECRET_KEY должен быть минимум 32 символа!"
            )

        if (
            self.JWT_SECRET_KEY
            == "a101-hr-profile-generator-secret-key-change-in-production"
        ):
            if self.ENVIRONMENT == "production":
                critical_issues.append(
                    "❌ КРИТИЧНО: JWT_SECRET_KEY должен быть изменен в production!"
                )
            else:
                issues.append(
                    "⚠️  JWT_SECRET_KEY использует default значение (измените для production)"
                )

        # Критическая проверка: OpenRouter API
        if not self.OPENROUTER_API_KEY:
            critical_issues.append("❌ КРИТИЧНО: OPENROUTER_API_KEY не настроен!")
        elif not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            critical_issues.append(
                "❌ КРИТИЧНО: Неверный формат OPENROUTER_API_KEY (должен начинаться с 'sk-or-')"
            )

        # Проверяем пароли по умолчанию
        if self.ENVIRONMENT == "production":
            if self.ADMIN_PASSWORD == "admin123":
                critical_issues.append(
                    "❌ КРИТИЧНО: ADMIN_PASSWORD должен быть изменен в production!"
                )
            if self.HR_PASSWORD == "hr123":
                critical_issues.append(
                    "❌ КРИТИЧНО: HR_PASSWORD должен быть изменен в production!"
                )
        else:
            if self.ADMIN_PASSWORD == "admin123":
                issues.append("⚠️  ADMIN_PASSWORD использует default значение")
            if self.HR_PASSWORD == "hr123":
                issues.append("⚠️  HR_PASSWORD использует default значение")

        # Проверка базы данных
        if not self.DATABASE_URL:
            critical_issues.append("❌ КРИТИЧНО: DATABASE_URL не настроен!")

        # Проверка CORS origins в production
        if self.ENVIRONMENT == "production":
            if "localhost" in str(self.CORS_ORIGINS) or "127.0.0.1" in str(
                self.CORS_ORIGINS
            ):
                issues.append("⚠️  CORS_ORIGINS содержит localhost в production")

        # Выводим критические ошибки
        if critical_issues:
            print("🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ КОНФИГУРАЦИИ:")
            for issue in critical_issues:
                print(f"  {issue}")
            print("🛑 Система не может работать с такими настройками!")

        # Выводим предупреждения
        if issues:
            print("⚠️  ПРЕДУПРЕЖДЕНИЯ КОНФИГУРАЦИИ:")
            for issue in issues:
                print(f"  {issue}")

        # Возвращаем True только если нет критических проблем
        if len(critical_issues) == 0:
            print("✅ Конфигурация валидна")
            return True

        return False

    def print_summary(self):
        """Печать сводки конфигурации (без секретов)."""
        print(
            f"""
🔧 A101 HR Configuration Summary:
   Environment: {self.ENVIRONMENT}
   Debug: {self.DEBUG}
   Database: {self.database_path}
   API: {self.API_HOST}:{self.API_PORT}
   OpenRouter: {'✅ Configured' if self.openrouter_configured else '❌ Not configured'}
   Langfuse: {'✅ Configured' if self.langfuse_configured else '❌ Not configured'}
   CORS Origins: {len(self.CORS_ORIGINS)} origins
   Data Directory: {self.DATA_DIR}
        """
        )


# Глобальный экземпляр конфигурации
config = Config()

# Автоматическая валидация при импорте
if not config.validate():
    import sys

    print("🛑 Система остановлена из-за критических проблем конфигурации!")
    print("📋 Исправьте проблемы выше и перезапустите систему.")
    if config.ENVIRONMENT == "production":
        sys.exit(1)  # Останавливаем в production
    else:
        print("⚠️  Разработческий режим: продолжаем работу с предупреждениями")


if __name__ == "__main__":
    # Тестирование конфигурации
    print("🧪 Testing A101 HR Configuration...")
    config.print_summary()
    config.validate()

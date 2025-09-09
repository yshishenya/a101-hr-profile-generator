"""
Основное FastAPI приложение для системы генерации профилей должностей А101.

Интеграция с существующими backend/core модулями:
- ProfileGenerator, DataLoader, LLMClient
- NiceGUI frontend на порту 8033
- Langfuse мониторинг (опционально)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Импорты для аутентификации, каталога, генерации и управления профилями
from .api.auth import auth_router
from .api.catalog import catalog_router
from .api.generation import router as generation_router, initialize_generation_system
from .api.profiles import router as profiles_router
from .utils.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from .utils.exception_handlers import setup_exception_handlers
from .core.config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Глобальные переменные для компонентов системы
app_components = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для инициализации и очистки компонентов"""
    logger.info("🚀 Starting  HR Profile Generator API...")

    # Startup: Инициализация компонентов системы
    try:
        # Проверяем наличие необходимых environment variables через конфигурацию
        if not config.openrouter_configured:
            logger.warning("⚠️ OpenRouter API не настроен - LLM генерация недоступна")

        if not config.langfuse_configured:
            logger.info("ℹ️ Langfuse мониторинг не настроен - работаем без трекинга")
        else:
            logger.info("✅ Langfuse мониторинг настроен")

        # Инициализируем компоненты (lazy loading при первом запросе)
        app_components["initialized"] = True
        app_components["startup_time"] = datetime.now()

        logger.info("✅ Система инициализирована успешно")

        # Инициализируем систему генерации профилей
        initialize_generation_system()

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации системы: {e}")
        raise

    yield

    # Shutdown: Очистка ресурсов
    logger.info("🛑 Shutting down HR Profile Generator API...")
    app_components.clear()


# Создание FastAPI приложения
app = FastAPI(
    title="HR Profile Generator API",
    description="""
    🏢 **Система автоматической генерации профилей должностей для компании А101**

    Использует детерминированную логику для маппинга данных компании и
    Gemini 2.5 Flash для создания детальных профилей должностей.

    ## Основные возможности:
    - 🎯 Генерация профилей должностей с использованием AI
    - 📊 Детерминированное извлечение данных организационной структуры
    - 🔍 Автоматический поиск релевантных KPI для департаментов
    - 📈 Интеграция с Langfuse для мониторинга качества
    - 🚀 Асинхронная генерация для сложных профилей
    - 📄 Экспорт в различных форматах (JSON, Markdown, Excel)

    ## Технологический стек:
    - **Backend:** FastAPI + Python 3.9+
    - **LLM:** Gemini 2.5 Flash через OpenRouter API
    - **Database:** SQLite
    - **Frontend:** NiceGUI (Material Design)
    - **Monitoring:** Langfuse (опционально)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware для интеграции с NiceGUI frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host middleware для безопасности
app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.TRUSTED_HOSTS)


# Добавление custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Настройка глобальных обработчиков исключений
setup_exception_handlers(app)


# Health check endpoint
@app.get("/health", tags=["System Health"])
async def health_check() -> Dict[str, Any]:
    """
    Базовая проверка состояния системы.

    Возвращает информацию о состоянии API и основных компонентов.
    """
    try:
        uptime = datetime.now() - app_components.get("startup_time", datetime.now())

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "version": "1.0.0",
            "environment": config.ENVIRONMENT,
            "components": {
                "api": "operational",
                "core_modules": (
                    "initialized" if app_components.get("initialized") else "pending"
                ),
            },
            "external_services": {
                "openrouter_configured": config.openrouter_configured,
                "langfuse_configured": config.langfuse_configured,
            },
        }

        logger.info("💚 Health check successful")
        return health_status

    except Exception as e:
        logger.error(f"💔 Health check failed: {e}")

        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            },
        )


# Root endpoint с информацией о API
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Корневой endpoint с основной информацией о системе.
    """
    return {
        "service": "HR Profile Generator API",
        "version": "1.0.0",
        "description": "Система автоматической генерации профилей должностей А101",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat(),
        "message": "🏢 Добро пожаловать в систему генерации профилей должностей А101!",
    }


# Статические файлы
from fastapi.staticfiles import StaticFiles
import os

# Создаем папку static если не существует
static_dir = "backend/static"
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Подключение API роутеров
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(generation_router)
app.include_router(profiles_router)


if __name__ == "__main__":
    # Запуск сервера для разработки
    uvicorn.run("main:app", host="0.0.0.0", port=8022, reload=True, log_level="info")

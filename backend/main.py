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
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

# Импорты для аутентификации
from .api.auth import auth_router
from .utils.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Глобальные переменные для компонентов системы
app_components = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для инициализации и очистки компонентов"""
    logger.info("🚀 Starting A101 HR Profile Generator API...")
    
    # Startup: Инициализация компонентов системы
    try:
        # Проверяем наличие необходимых environment variables
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            logger.warning("⚠️ OPENROUTER_API_KEY не установлен - LLM генерация недоступна")
        
        langfuse_public = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret = os.getenv("LANGFUSE_SECRET_KEY")
        
        # Инициализируем компоненты (lazy loading при первом запросе)
        app_components["initialized"] = True
        app_components["startup_time"] = datetime.now()
        
        logger.info("✅ Система инициализирована успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации системы: {e}")
        raise
    
    yield
    
    # Shutdown: Очистка ресурсов
    logger.info("🛑 Shutting down A101 HR Profile Generator API...")
    app_components.clear()


# Создание FastAPI приложения
app = FastAPI(
    title="A101 HR Profile Generator API",
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
    lifespan=lifespan
)

# CORS middleware для интеграции с NiceGUI frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8033",  # NiceGUI frontend
        "http://127.0.0.1:8033",
        "http://0.0.0.0:8033",
        # В production добавить реальный домен
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host middleware для безопасности
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1", 
        "0.0.0.0",
        # В production добавить реальный домен
    ]
)


# Добавление custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# Глобальный exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Обработка всех неперехваченных исключений"""
    logger.error(f"💥 Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Произошла внутренняя ошибка сервера",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )


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
            "environment": os.getenv("ENVIRONMENT", "development"),
            "components": {
                "api": "operational",
                "core_modules": "initialized" if app_components.get("initialized") else "pending",
            },
            "external_services": {
                "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
                "langfuse_configured": bool(
                    os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
                ),
            }
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
                "error": str(e)
            }
        )


# Root endpoint с информацией о API
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Корневой endpoint с основной информацией о системе.
    """
    return {
        "service": "A101 HR Profile Generator API",
        "version": "1.0.0",
        "description": "Система автоматической генерации профилей должностей А101",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat(),
        "message": "🏢 Добро пожаловать в систему генерации профилей должностей А101!"
    }


# Статические файлы
from fastapi.staticfiles import StaticFiles
import os

# Создаем папку static если не существует
static_dir = "/home/yan/A101/HR/backend/static"
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Подключение API роутеров
app.include_router(auth_router)


if __name__ == "__main__":
    # Запуск сервера для разработки
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8022,
        reload=True,
        log_level="info"
    )
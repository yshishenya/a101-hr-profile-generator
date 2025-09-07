FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование требований и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY backend/ ./backend/
COPY data/ ./data/
COPY templates/ ./templates/
COPY docs/ ./docs/

# Создание необходимых директорий
RUN mkdir -p backend/static \
    && mkdir -p generated_profiles \
    && mkdir -p logs

# Настройки окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8022

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8022/health || exit 1

# Команда запуска для разработки с auto-reload
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8022", "--reload"]
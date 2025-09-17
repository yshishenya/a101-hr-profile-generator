#!/bin/bash
# Docker entrypoint для A101 HR Backend
# Создает необходимые директории и запускает приложение

set -e

echo "🚀 Инициализация A101 HR Backend от $(whoami)..."

# Проверяем и создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p /app/generated_profiles
mkdir -p /app/logs
mkdir -p /app/backend/static

# Простая проверка прав записи
echo "✅ Проверка прав записи..."
if touch /app/generated_profiles/test_write 2>/dev/null; then
    rm -f /app/generated_profiles/test_write
    echo "✅ generated_profiles доступен для записи"
else
    echo "⚠️ generated_profiles недоступен для записи, но продолжаем..."
fi


echo "🎯 Запуск приложения..."

# Запускаем переданную команду
exec "$@"
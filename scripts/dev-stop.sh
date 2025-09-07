#!/bin/bash
# Скрипт для остановки среды разработки A101 HR

echo "🛑 Остановка A101 HR Profile Generator"

# Остановка и удаление контейнеров
echo "📦 Остановка контейнеров..."
docker-compose down

# Показать статус
echo "🔍 Статус после остановки:"
docker-compose ps

# Очистка (опционально)
read -p "🗑️  Очистить Docker образы и volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Очистка Docker ресурсов..."
    docker-compose down -v --rmi local
    docker system prune -f
fi

echo "✅ Среда разработки остановлена!"
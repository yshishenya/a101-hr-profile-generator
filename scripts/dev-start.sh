#!/bin/bash
# Скрипт для запуска среды разработки A101 HR

echo "🚀 Запуск A101 HR Profile Generator (Development Mode)"

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден. Создаем из .env.example..."
    cp .env.example .env
    echo "📝 Отредактируйте .env файл с вашими API ключами"
fi

# Создание необходимых директорий
echo "📁 Создание необходимых директорий..."
mkdir -p generated_profiles logs backend/static

# Сборка и запуск контейнеров
echo "🔨 Сборка и запуск контейнеров..."
docker-compose build --no-cache
docker-compose up -d

# Ожидание запуска приложения
echo "⏳ Ожидание запуска приложения..."
sleep 10

# Проверка состояния
echo "🔍 Проверка состояния контейнеров..."
docker-compose ps

# Проверка health check
echo "🏥 Проверка работоспособности API..."
curl -f http://localhost:8022/health || echo "❌ API не отвечает"

echo ""
echo "✅ Среда разработки запущена!"
echo "📡 API: http://localhost:8022"
echo "📖 Swagger UI: http://localhost:8022/docs"
echo "📊 Health Check: http://localhost:8022/health"
echo ""
echo "🛠️  Команды для работы:"
echo "  - Логи: docker-compose logs -f app"
echo "  - Остановка: docker-compose down"
echo "  - Перезапуск: docker-compose restart app"
#!/bin/bash
# Fix DOCX file permissions for ZIP archive creation
# This script fixes permission issues with DOCX files created by Docker running as root

echo "🔧 Исправление прав доступа к DOCX файлам..."

# Check if Docker container is running
if ! docker ps | grep -q "a101hr_app"; then
    echo "❌ Контейнер a101hr_app не запущен"
    exit 1
fi

echo "📋 Поиск DOCX файлов с проблемными правами..."

# Find and fix permissions on DOCX files
docx_count=$(docker exec a101hr_app find /app/generated_profiles -name "*.docx" -user root | wc -l)

if [ "$docx_count" -eq 0 ]; then
    echo "✅ Все DOCX файлы уже имеют правильные права доступа"
    exit 0
fi

echo "📁 Найдено $docx_count DOCX файлов с проблемными правами"

# Fix permissions (644 = readable by everyone)
echo "🔧 Исправление прав доступа (chmod 644)..."
docker exec a101hr_app find /app/generated_profiles -name "*.docx" -exec chmod 644 {} \;

# Fix ownership (1000:1000 = yan:yan)
echo "👤 Исправление владельца (chown 1000:1000)..."
docker exec a101hr_app find /app/generated_profiles -name "*.docx" -exec chown 1000:1000 {} \;

echo "✅ Права доступа исправлены!"
echo "📦 Теперь можно создавать ZIP архивы без предупреждений"

# Test one file to verify
sample_file=$(find generated_profiles -name "*.docx" | head -1)
if [ -n "$sample_file" ]; then
    echo "🧪 Проверка исправления:"
    ls -la "$sample_file" | head -1
fi
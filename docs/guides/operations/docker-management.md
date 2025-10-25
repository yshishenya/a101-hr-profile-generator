# Docker Management Commands

## Управление данными в Docker volumes

### Просмотр сгенерированных профилей
```bash
# Показать все сгенерированные профили
docker exec a101hr_app find /app/generated_profiles -type f -name "*.json" -o -name "*.md"

# Подсчет файлов
docker exec a101hr_app find /app/generated_profiles -type f | wc -l
```

### Очистка данных
```bash
# Очистить все сгенерированные профили (внутри контейнера)
docker exec a101hr_app rm -rf /app/generated_profiles/*

# Очистить базу данных
docker exec a101hr_app python -c "
import sqlite3
conn = sqlite3.connect('/app/data/profiles.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM profiles')
cursor.execute('DELETE FROM generation_tasks')  
cursor.execute('DELETE FROM generation_history')
cursor.execute('DELETE FROM organization_cache')
cursor.execute('DELETE FROM sqlite_sequence WHERE name=\"profiles\"')
conn.commit()
conn.close()
print('✅ Database cleared')
"
```

### Резервное копирование данных
```bash
# Создать бэкап базы данных
docker exec a101hr_app cp /app/data/profiles.db /app/data/profiles_backup_$(date +%Y%m%d_%H%M%S).db

# Экспорт volume в tar архив
docker run --rm -v a101hr_generated_profiles:/backup -v $(pwd):/host alpine tar czf /host/profiles_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /backup .
```

### Docker Volumes
```bash
# Просмотр всех volumes
docker volume ls | grep a101hr

# Подробная информация о volume
docker volume inspect a101hr_generated_profiles

# Удаление всех данных (ОПАСНО!)
docker compose down
docker volume rm a101hr_database a101hr_generated_profiles a101hr_logs a101hr_frontend_static
```

## Статус системы

✅ **Конфигурация:** Docker volumes настроены корректно  
✅ **Данные:** Сохраняются в контейнере (`/app/data`, `/app/generated_profiles`)  
✅ **Изоляция:** Хост-система остается чистой  
✅ **Персистентность:** Данные сохраняются между перезапусками контейнеров  
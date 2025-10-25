# Docker Bind Mounts Configuration

## 📁 Структура файлов

Система настроена с bind mounts для доступа к данным как из контейнера, так и с хоста:

### Host System Paths:
```
/home/yan/A101/HR/
├── data/                           # База данных (видна на хосте)
│   └── profiles.db
├── generated_profiles/             # Сгенерированные профили (видны на хосте)
│   └── Блок_операционного_директора/
│       └── Департамент_информационных_технологий/
│           └── Директор_по_информационным_технологиям/
├── logs/                          # Логи системы (видны на хосте)
└── frontend_static/               # Статические файлы фронтенда
```

### Container Paths:
```
/app/
├── data/                          # Маппится к ./data
├── generated_profiles/            # Маппится к ./generated_profiles
├── logs/                          # Маппится к ./logs
└── frontend/static/               # Маппится к ./frontend_static
```

## 🐳 Docker Compose Configuration

```yaml
volumes:
  # Код для разработки с hot-reload
  - ./backend:/app/backend
  - ./templates:/app/templates
  - ./docs:/app/docs
  
  # Персистентные данные с доступом с хоста (bind mounts)
  - ./data:/app/data                      # База данных
  - ./generated_profiles:/app/generated_profiles  # Профили
  - ./logs:/app/logs                      # Логи
```

## ✅ Преимущества текущей конфигурации:

1. **👁️ Visibility:** Все файлы видны на хосте для анализа и редактирования
2. **💾 Persistence:** Данные сохраняются между перезапусками контейнеров
3. **🔄 Development:** Удобно для разработки и отладки
4. **📊 Monitoring:** Легкий доступ к логам и результатам
5. **🗂️ Management:** Простое управление файлами через хост-систему

## 🧪 Тестирование

Проверено:
- ✅ Генерация профилей работает
- ✅ Файлы .json и .md создаются в контейнере
- ✅ Файлы видны на хосте в `./generated_profiles/`
- ✅ База данных доступна на хосте в `./data/profiles.db`
- ✅ MD файлы читаются корректно с хоста

## 📋 Команды управления

```bash
# Просмотр сгенерированных файлов на хосте
find ./generated_profiles -name "*.json" -o -name "*.md"

# Очистка профилей на хосте
rm -rf ./generated_profiles/*

# Просмотр логов
tail -f ./logs/app.log

# Проверка базы данных
sqlite3 ./data/profiles.db "SELECT COUNT(*) FROM profiles;"
```

Система готова к работе с полным доступом к файлам! 🎉
# 🐳 **Docker Deployment Guide - A101 HR Profile Generator**

## 🚀 **Quick Start**

### Полная система (Backend + Frontend):
```bash
docker compose up --build
```

### Только Frontend (для development):
```bash
# Запустить backend локально
python -m backend.main

# Запустить frontend в контейнере
docker compose -f docker-compose.frontend.yml up --build
```

### Использование скриптов:
```bash
# Различные режимы запуска
./scripts/start-frontend.sh local       # Локально
./scripts/start-frontend.sh docker     # Frontend в Docker
./scripts/start-frontend.sh compose    # Полная система
```

## 📋 **Доступные URL**

- **Frontend:** http://localhost:8033
- **Backend API:** http://localhost:8022
- **API Docs:** http://localhost:8022/docs
- **Health Check:** http://localhost:8022/health

## 🔧 **Конфигурация Docker**

### Environment Variables (.env файл):

```bash
# =============================================================================
# Docker & Frontend Settings
# =============================================================================
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8033
BACKEND_HOST=localhost  # Изменяется на 'app' в контейнерах
BACKEND_PORT=8022

# =============================================================================
# Security
# =============================================================================
STORAGE_SECRET=a101hr-frontend-storage-secret-key
JWT_SECRET_KEY=dev-secret-key-change-in-production

# =============================================================================
# UI Settings
# =============================================================================
FRONTEND_TITLE=A101 HR Profile Generator
THEME=auto
PRIMARY_COLOR=blue
```

## 📁 **Структура Docker Files**

### Dockerfile.frontend
- **Base Image:** `python:3.11-slim`
- **User:** Непривилегированный пользователь `frontend`
- **Port:** 8033
- **Health Check:** NiceGUI status endpoint

### docker-compose.yml
- **app:** Backend FastAPI контейнер (порт 8022)
- **frontend:** NiceGUI frontend контейнер (порт 8033)
- **Networking:** Внутренняя сеть `a101hr_network`
- **Dependencies:** Frontend зависит от backend
- **Health Checks:** Автоматические проверки состояния

### docker-compose.frontend.yml
- Только frontend для development
- Подключается к backend через `host.docker.internal`

## 🔀 **Service Discovery**

В Docker Compose контейнеры используют service names для связи:

```yaml
# Frontend подключается к backend через service name
BACKEND_HOST=app  # Вместо localhost
BACKEND_PORT=8022
```

## 📊 **Мониторинг**

### Проверка состояния сервисов:
```bash
docker compose ps
docker compose logs frontend
docker compose logs app
```

### Health Checks:
```bash
# Backend
curl http://localhost:8022/health

# Frontend (через браузер)
curl http://localhost:8033/login
```

## 🔧 **Команды разработчика**

### Остановка сервисов:
```bash
docker compose down
```

### Пересборка с изменениями:
```bash
docker compose up --build
```

### Просмотр логов:
```bash
docker compose logs -f frontend  # Логи frontend
docker compose logs -f app       # Логи backend
```

### Выполнение команд в контейнере:
```bash
docker compose exec frontend bash
docker compose exec app python -c "from backend.core.config import config; print(config.ENVIRONMENT)"
```

## 🏭 **Production Deployment**

### Обязательные изменения для production:

1. **Secrets:**
```bash
JWT_SECRET_KEY=your-strong-production-secret
STORAGE_SECRET=your-frontend-storage-secret
ADMIN_PASSWORD=your-secure-admin-password
```

2. **Environment:**
```bash
ENVIRONMENT=production
DEBUG=false
```

3. **Reverse Proxy (Nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8033;  # Frontend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8022;  # Backend API
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **SSL/TLS Configuration:**
```bash
# Используйте Let's Encrypt или корпоративные сертификаты
certbot --nginx -d your-domain.com
```

## 🚨 **Troubleshooting**

### Frontend показывает 500 ошибку:
```bash
# Проверьте логи
docker compose logs frontend

# Наиболее частые причины:
# 1. Отсутствует STORAGE_SECRET
# 2. Backend недоступен
# 3. Неправильная конфигурация сети
```

### Backend недоступен:
```bash
# Проверьте health check
curl http://localhost:8022/health

# Проверьте переменные окружения
docker compose exec app env | grep OPENROUTER
```

### Контейнеры не стартуют:
```bash
# Проверьте docker-compose.yml
docker compose config

# Пересоберите образы
docker compose build --no-cache
```

## 📦 **Volumes & Persistence**

### Постоянные данные:
- `generated_profiles/` - Генерированные профили
- `logs/` - Логи приложения
- `data/` - База данных SQLite

### Очистка данных:
```bash
# Остановить и удалить volumes
docker compose down -v

# Удалить все данные
docker compose down -v --remove-orphans
```

## ✅ **Проверка успешного развертывания**

1. **Сервисы запущены:**
```bash
docker compose ps
# Оба сервиса должны быть в состоянии "Up"
```

2. **Health checks прошли:**
```bash
curl http://localhost:8022/health
# {"status":"healthy",...}
```

3. **Frontend доступен:**
```bash
curl -I http://localhost:8033/login
# HTTP/1.1 200 OK (или 405 для HEAD запросов)
```

4. **Авторизация работает:**
- Открыть http://localhost:8033/login
- Войти с `admin/admin123` или `hr/hr123`
- Перенаправление на главную страницу

---

## 🎯 **Готово к использованию!**

Система A101 HR Profile Generator полностью настроена для работы в Docker контейнерах:
- ✅ Отдельные контейнеры для backend и frontend
- ✅ Автоматическое service discovery
- ✅ Health checks и мониторинг
- ✅ Production-ready конфигурация
- ✅ Простые команды для развертывания

Captain, Docker Compose конфигурация готова к производственному использованию! 🐳
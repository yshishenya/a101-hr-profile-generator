# 🚀 Руководство по развертыванию A101 HR Profile Generator

## ⚡ Быстрый запуск (Development)

### Предварительные требования
- Python 3.9+
- pip для управления зависимостями

### 1. Установка зависимостей
```bash
# Установка зависимостей
pip install -r requirements.txt

# Проверка установки
python -c "import fastapi, uvicorn; print('✅ Dependencies installed')"
```

### 2. Настройка базы данных
```bash
# База данных создается автоматически при первом запуске
# Файл: data/profiles.db

# Принудительное создание схемы (опционально)
python -c "
from backend.models.database import db_manager
db_manager.create_schema()
print('✅ Database schema created')
"
```

### 3. Проверка данных
```bash
# Проверка наличия необходимых файлов
ls -la data/
# Должны быть: structure.json, anonymized_digitization_map.md, KPI/KPI_DIT.md

ls -la templates/
# Должны быть: job_profile_schema.json
```

### 4. Запуск сервера
```bash
# Development сервер с auto-reload
uvicorn backend.main:app --host 0.0.0.0 --port 8022 --reload

# Сервер запустится на http://localhost:8022
# Swagger UI: http://localhost:8022/docs
```

### 5. Тестирование
```bash
# Проверка здоровья системы
curl http://localhost:8022/health

# Аутентификация (admin/admin123 или hr/hr123)
curl -X POST "http://localhost:8022/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 🏭 Production развертывание

### Docker развертывание (Recommended)

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY backend/ ./backend/
COPY data/ ./data/
COPY templates/ ./templates/

# Создаем директории
RUN mkdir -p backend/static

# Настройки
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Порт
EXPOSE 8022

# Команда запуска
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8022", "--workers", "4"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8022:8022"
    environment:
      - ENVIRONMENT=production
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8022/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
```

#### Команды развертывания
```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f app

# Остановка
docker-compose down
```

### Обычное развертывание на сервере

#### 1. Подготовка сервера (Ubuntu/CentOS)
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python 3.9+
sudo apt install python3.9 python3.9-pip python3.9-venv -y

# Создание пользователя для приложения
sudo useradd -m -s /bin/bash a101hr
sudo su - a101hr
```

#### 2. Развертывание приложения
```bash
# Клонирование/копирование кода
git clone <repository> /home/a101hr/app
cd /home/a101hr/app

# Создание виртуального окружения
python3.9 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка дополнительных зависимостей для production
pip install gunicorn
```

#### 3. Настройка systemd сервиса
```bash
# /etc/systemd/system/a101hr.service
sudo cat > /etc/systemd/system/a101hr.service << EOF
[Unit]
Description=A101 HR Profile Generator
After=network.target

[Service]
User=a101hr
Group=a101hr
WorkingDirectory=/home/a101hr/app
Environment="PATH=/home/a101hr/app/venv/bin"
Environment="PYTHONPATH=/home/a101hr/app"
Environment="ENVIRONMENT=production"
ExecStart=/home/a101hr/app/venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8022
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Активация сервиса
sudo systemctl daemon-reload
sudo systemctl enable a101hr
sudo systemctl start a101hr

# Проверка статуса
sudo systemctl status a101hr
```

#### 4. Настройка Nginx
```bash
# /etc/nginx/sites-available/a101hr
sudo cat > /etc/nginx/sites-available/a101hr << EOF
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8022;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias /home/a101hr/app/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/a101hr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 Конфигурация

### Централизованная система конфигурации

A101 HR использует **модуль централизованной конфигурации** `backend/core/config.py` с автоматической загрузкой `.env` файлов.

### Environment Variables

**Полный список переменных окружения:**
```bash
# =============================================================================
# Application Settings
# =============================================================================
ENVIRONMENT=production
LOG_LEVEL=INFO

# =============================================================================
# Database Configuration
# =============================================================================
DATABASE_URL=sqlite:///data/profiles.db

# =============================================================================
# JWT Authentication (ВАЖНО: Изменить в production!)
# =============================================================================
JWT_SECRET_KEY=your-production-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# =============================================================================
# User Credentials (ВАЖНО: Изменить в production!)
# =============================================================================
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
ADMIN_FULL_NAME=Администратор системы

HR_USERNAME=hr
HR_PASSWORD=your-secure-hr-password
HR_FULL_NAME=HR специалист

# =============================================================================
# OpenRouter API (обязательно для LLM функций)
# =============================================================================
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# Langfuse Monitoring (опционально)
# =============================================================================
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# =============================================================================
# FastAPI Configuration
# =============================================================================
API_PREFIX=/api
API_HOST=0.0.0.0
API_PORT=8022
CORS_ORIGINS=https://your-domain.com

# =============================================================================
# Directory Paths
# =============================================================================
DATA_DIR=data
TEMPLATES_DIR=templates
GENERATED_PROFILES_DIR=generated_profiles
LOGS_DIR=logs
STATIC_DIR=backend/static
```

### Создание .env файла для production

```bash
# Создать .env из шаблона
cp .env.example .env

# Отредактировать критически важные настройки
nano .env
```

**ВАЖНО для production:**
```bash
# Обязательно изменить эти значения:
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ADMIN_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
HR_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
ENVIRONMENT=production
CORS_ORIGINS=https://your-production-domain.com
```

### Валидация конфигурации

```bash
# Проверка конфигурации перед деплоем
python3 -c "from backend.core.config import config; config.validate()"
```

### Настройка логирования
```python
# config/logging.conf
[loggers]
keys=root,uvicorn,backend

[handlers]
keys=console,file

[formatters] 
keys=default

[logger_root]
level=INFO
handlers=console,file

[logger_uvicorn]
level=INFO
handlers=console,file
qualname=uvicorn
propagate=0

[logger_backend]
level=INFO
handlers=console,file
qualname=backend
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=default
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=default
args=('logs/app.log', 'a', 10485760, 5)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

---

## 🔍 Мониторинг и диагностика

### Health Checks
```bash
# Проверка здоровья системы
curl -f http://localhost:8022/health || exit 1

# Проверка аутентификации
curl -X POST http://localhost:8022/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.success' | grep -q true || exit 1
```

### Логирование
```bash
# Просмотр логов приложения
sudo journalctl -u a101hr -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Логи приложения (если настроены в файл)
tail -f logs/app.log
```

### Метрики производительности
```bash
# Системные метрики
htop
df -h
free -h

# Метрики приложения
curl -s http://localhost:8022/health | jq '.uptime_seconds'

# Проверка подключений к БД
lsof -i :8022
```

---

## 🛡️ Безопасность

### Настройки безопасности
1. **Firewall конфигурация:**
```bash
# Открыть только необходимые порты
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw --force enable
```

2. **SSL/TLS сертификаты:**
```bash
# Использование Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

3. **Обновление секретных ключей:**
```python
# Генерация нового JWT секрета
import secrets
jwt_secret = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={jwt_secret}")
```

### Backup стратегия
```bash
# Backup базы данных
cp data/profiles.db backups/profiles_$(date +%Y%m%d_%H%M%S).db

# Backup конфигурации
tar -czf backups/config_$(date +%Y%m%d).tar.gz \
  /etc/nginx/sites-available/a101hr \
  /etc/systemd/system/a101hr.service \
  .env

# Автоматический backup (crontab)
# 0 2 * * * /home/a101hr/scripts/backup.sh
```

---

## 🔄 Обновление системы

### Процедура обновления
```bash
# 1. Остановка сервиса
sudo systemctl stop a101hr

# 2. Backup текущей версии
cp -r /home/a101hr/app /home/a101hr/app_backup_$(date +%Y%m%d)

# 3. Обновление кода
cd /home/a101hr/app
git pull origin main

# 4. Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# 5. Миграция БД (если необходимо)
python -c "
from backend.models.database import db_manager
db_manager.create_schema()  # Обновит схему
"

# 6. Запуск сервиса
sudo systemctl start a101hr
sudo systemctl status a101hr

# 7. Проверка работоспособности
curl -f http://localhost:8022/health
```

### Rollback процедура
```bash
# В случае проблем
sudo systemctl stop a101hr
rm -rf /home/a101hr/app
mv /home/a101hr/app_backup_YYYYMMDD /home/a101hr/app
sudo systemctl start a101hr
```

---

## 📊 Performance Tuning

### Gunicorn настройки для production
```python
# gunicorn.conf.py
bind = "0.0.0.0:8022"
workers = 4  # (CPU cores * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
preload_app = True
```

### Nginx оптимизация
```nginx
# worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
gzip_types text/plain application/json application/javascript text/css;

# Кеширование статических файлов
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Мониторинг ресурсов
```bash
# Автоматический мониторинг
watch -n 5 'curl -s http://localhost:8022/health | jq ".uptime_seconds, .components"'

# Мониторинг памяти
watch -n 5 'ps aux | grep -E "(gunicorn|uvicorn)" | grep -v grep'
```

---

## 🆘 Troubleshooting

### Частые проблемы

#### 1. Сервер не запускается
```bash
# Проверка порта
sudo netstat -tlnp | grep :8022

# Проверка логов
sudo journalctl -u a101hr --no-pager

# Проверка разрешений
sudo chown -R a101hr:a101hr /home/a101hr/app
```

#### 2. База данных недоступна
```bash
# Проверка файла БД
ls -la data/profiles.db

# Проверка разрешений
chmod 644 data/profiles.db

# Пересоздание схемы
python -c "
from backend.models.database import db_manager
db_manager.create_schema()
"
```

#### 3. 401 ошибки аутентификации
```bash
# Проверка создания пользователей
python -c "
from backend.services.auth_service import auth_service  
user = auth_service.get_user_by_username('admin')
print('Admin user exists:', bool(user))
"

# Пересоздание пользователей
python -c "
from backend.models.database import db_manager
db_manager.seed_initial_data()
"
```

#### 4. Высокое потребление памяти
```bash
# Уменьшение количества workers
sudo systemctl edit a101hr
# Добавить: ExecStart=/home/a101hr/app/venv/bin/gunicorn ... -w 2

# Перезапуск
sudo systemctl daemon-reload
sudo systemctl restart a101hr
```

---

## 📞 Поддержка

### Команды для диагностики
```bash
# Полная проверка системы
curl -s http://localhost:8022/health | jq '.'

# Проверка всех endpoints
curl -s http://localhost:8022/ | jq '.'

# Тест аутентификации
curl -X POST http://localhost:8022/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq '.'
```

### Контактная информация
- **Документация:** http://localhost:8022/docs
- **Статус системы:** http://localhost:8022/health
- **Версия:** 1.0.0

**Deployment Guide актуален на:** 2025-09-07